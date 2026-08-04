"""The runner does what it says, and refuses before it creates anything.

This is the only shipped component that executes something, so it is the only one whose contract
can be exercised rather than argued about. Two of these tests are about refusal rather than
running: a bad input must not leave a directory behind, because that would burn the name the next
run wanted, and an existing run must never be overwritten, because a run's output is the evidence
somebody else will disagree over.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

REPO = Path(__file__).resolve().parent.parent
RUNNER = REPO / "src/claude/bin/run.py"


@pytest.fixture(scope="module")
def run_contract() -> Draft202012Validator:
    schema = json.loads((REPO / "src/claude/schemas/run.json").read_text(encoding="utf-8"))
    return Draft202012Validator(schema)


@pytest.fixture
def delivery(tmp_path: Path) -> Path:
    base = tmp_path / "delivery"
    base.mkdir()
    return base


def invoke(delivery: Path, *args: str, timeout: int = 30) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(RUNNER), str(delivery), *args],
                          capture_output=True, text=True, timeout=timeout)


def record_of(delivery: Path, slug: str) -> dict:
    return json.loads((delivery / "run" / slug / "run.json").read_text(encoding="utf-8"))


# ---------------------------------------------------------------------- what it runs


def test_a_run_where_everything_passes(delivery, run_contract):
    done = invoke(delivery, "--run", "green", "--timeout-seconds", "20",
                  "--step", "one=python3 -c 'pass'", "--step", "two=python3 -c 'pass'")
    assert done.returncode == 0, done.stderr
    record = record_of(delivery, "green")
    assert [e.message for e in run_contract.iter_errors(record)] == []
    assert record["outcome"] == "passed"
    assert record["failed_step"] is None
    assert [s["outcome"] for s in record["steps"]] == ["passed", "passed"]
    assert record["timeout_seconds"] == 20, "the bound is recorded with the run it bounded"


def test_a_failed_step_stops_the_run(delivery, run_contract):
    done = invoke(delivery, "--run", "red", "--timeout-seconds", "20",
                  "--step", "build=python3 -c 'raise SystemExit(3)'",
                  "--step", "suite=python3 -c 'pass'")
    assert done.returncode == 1
    record = record_of(delivery, "red")
    assert [e.message for e in run_contract.iter_errors(record)] == []
    assert record["outcome"] == "failed"
    assert record["failed_step"] == "build"
    assert record["steps"][0]["exit_code"] == 3
    assert record["steps"][1]["outcome"] == "not_run", \
        "a suite run over a tree that did not build reports failures about a binary nobody built"
    assert record["steps"][1]["output"] is None


def test_what_a_command_printed_lands_verbatim(delivery):
    invoke(delivery, "--run", "loud", "--timeout-seconds", "20",
           "--step", 'say=python3 -c \'print("expected 409, got 500")\'')
    log = (delivery / "run/loud/say.log").read_text(encoding="utf-8")
    assert log == "expected 409, got 500\n", "a diagnosis reads what the command wrote, not a summary"
    combined = (delivery / "run/loud/run.log").read_text(encoding="utf-8")
    assert "===== say ::" in combined and "expected 409, got 500" in combined


def test_a_command_that_does_not_exist(delivery, run_contract):
    done = invoke(delivery, "--run", "absent", "--timeout-seconds", "20",
                  "--step", "suite=siegard-no-such-command")
    assert done.returncode == 1
    record = record_of(delivery, "absent")
    assert [e.message for e in run_contract.iter_errors(record)] == []
    assert record["outcome"] == "not_found"
    assert record["steps"][0]["exit_code"] is None
    assert "command not found" in (delivery / "run/absent/suite.log").read_text(encoding="utf-8")


def test_a_step_that_outlives_its_bound(delivery, run_contract):
    done = invoke(delivery, "--run", "slow", "--timeout-seconds", "1",
                  "--step", "hang=python3 -c 'import time; time.sleep(30)'")
    assert done.returncode == 1
    record = record_of(delivery, "slow")
    assert [e.message for e in run_contract.iter_errors(record)] == []
    assert record["outcome"] == "timed_out"
    assert "terminated after 1s" in (delivery / "run/slow/hang.log").read_text(encoding="utf-8")


def test_no_shell_sees_the_command(delivery):
    """`&&` reaches the command as an argument, never as an operator — nothing a command prints
    or is passed can start another one."""
    invoke(delivery, "--run", "literal", "--timeout-seconds", "20",
           "--step", 'echo=python3 -c \'import sys; print(sys.argv[1:])\' && rm -rf /')
    record = record_of(delivery, "literal")
    assert record["outcome"] == "passed"
    assert "'&&'" in (delivery / "run/literal/echo.log").read_text(encoding="utf-8")


# ------------------------------------------------------------------ what it refuses


@pytest.mark.parametrize("args, fragment", [
    (("--run", "Green", "--timeout-seconds", "20", "--step", "a=python3 -c 'pass'"),
     "the path is the identity"),
    (("--run", "green", "--timeout-seconds", "0", "--step", "a=python3 -c 'pass'"),
     "positive whole number"),
    (("--run", "green", "--timeout-seconds", "20", "--step", "no-equals-sign"),
     "is not NAME=COMMAND"),
    (("--run", "green", "--timeout-seconds", "20", "--step", "Bad=python3 -c 'pass'"),
     "lowercase words joined by hyphens"),
    (("--run", "green", "--timeout-seconds", "20",
      "--step", "a=python3 -c 'pass'", "--step", "a=python3 -c 'pass'"),
     "is named twice"),
    (("--run", "green", "--timeout-seconds", "20", "--step", "a="),
     "has an empty command"),
])
def test_it_refuses_what_it_cannot_run(delivery, args, fragment):
    done = invoke(delivery, *args)
    assert done.returncode == 2, done.stdout
    assert fragment in done.stderr, done.stderr


def test_a_refusal_leaves_no_directory_behind(delivery):
    """The name a refused run was given must still be available. A refusal that had already made
    the directory would burn it for a run that never happened."""
    invoke(delivery, "--run", "green", "--timeout-seconds", "20", "--step", "Bad=python3 -c 'pass'")
    assert not (delivery / "run" / "green").exists()
    done = invoke(delivery, "--run", "green", "--timeout-seconds", "20",
                  "--step", "ok=python3 -c 'pass'")
    assert done.returncode == 0, done.stderr


def test_it_never_overwrites_a_run(delivery):
    assert invoke(delivery, "--run", "once", "--timeout-seconds", "20",
                  "--step", "a=python3 -c 'pass'").returncode == 0
    again = invoke(delivery, "--run", "once", "--timeout-seconds", "20",
                   "--step", "a=python3 -c 'pass'")
    assert again.returncode == 2
    assert "would overwrite" in again.stderr


def test_it_refuses_a_delivery_root_that_is_not_there(tmp_path):
    done = invoke(tmp_path / "nowhere", "--run", "green", "--timeout-seconds", "20",
                  "--step", "a=python3 -c 'pass'")
    assert done.returncode == 2
    assert "is not a directory" in done.stderr


def test_it_counts_nothing(delivery):
    """The record says what each command exited with and what it printed. How many tests failed
    is read out of the output by whoever diagnoses it, because counting means parsing a
    reporter's format and nothing here holds knowledge of a stack."""
    invoke(delivery, "--run", "counted", "--timeout-seconds", "20",
           "--step", 'a=python3 -c \'print("2 failed, 5 passed")\'')
    record = record_of(delivery, "counted")
    flat = json.dumps(record)
    for word in ("failures", "passed_count", "failed_count", "total"):
        assert f'"{word}"' not in flat, f"the record offers a {word}; it must offer none"
