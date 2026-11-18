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
    """Every invocation states its working directory: the runner refuses to choose one."""
    cwd = [] if "--cwd" in args else ["--cwd", str(REPO)]
    return subprocess.run([sys.executable, "-B", str(RUNNER), str(delivery), *cwd, *args],
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
    for step in record["steps"]:
        assert step["started_at"] <= step["ended_at"], \
            "an attempted step says when it ran; the difference is its duration"
    assert record["steps"][0]["ended_at"] <= record["steps"][1]["started_at"], \
        "steps run in order, and their clocks say so"


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
    assert record["steps"][1]["started_at"] is None and record["steps"][1]["ended_at"] is None, \
        "a step never attempted carries no clock reading; one would claim something happened"


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


# --------------------------------------------------------------- what it excerpts


def test_no_excerpt_unless_it_is_asked_for(delivery):
    done = invoke(delivery, "--run", "quiet", "--timeout-seconds", "20",
                  "--step", "build=python3 -c 'print(\"boom\"); raise SystemExit(1)'")
    assert done.returncode == 1
    assert json.loads(done.stdout)["failed_step"] == "build", \
        "without the flag stdout is the record alone, and parses as one"


def test_the_excerpt_is_the_tail_of_the_step_that_failed(delivery):
    lines = "; ".join(f'print({n})' for n in range(1, 31))
    done = invoke(delivery, "--run", "loud", "--timeout-seconds", "20", "--excerpt", "3",
                  "--step", f"build=python3 -c '{lines}; raise SystemExit(1)'")
    assert done.returncode == 1
    head, _, record = done.stdout.partition("{")
    assert "===== build :: last 3 line(s) of build.log" in head
    assert "run/loud/build.log" in head, "the excerpt says where the whole of it is"
    assert head.rstrip().endswith("28\n29\n30"), head
    assert "27" not in head, "the bound is the bound"
    assert json.loads("{" + record)["failed_step"] == "build", \
        "the record prints last, so a caller piping through tail keeps it"


def test_the_excerpt_bounds_a_single_enormous_line(delivery):
    done = invoke(delivery, "--run", "wide", "--timeout-seconds", "20", "--excerpt", "5",
                  "--step", "build=python3 -c 'print(\"x\" * 4000); raise SystemExit(1)'")
    assert done.returncode == 1
    head = done.stdout.partition("{")[0]
    assert "[+3500 characters]" in head, \
        "a line count alone bounds nothing when one line holds a whole trace"
    assert len(head) < 1200, head[:200]


def test_a_run_that_passed_carries_no_excerpt(delivery):
    done = invoke(delivery, "--run", "green", "--timeout-seconds", "20", "--excerpt", "40",
                  "--step", "build=python3 -c 'print(\"fine\")'")
    assert done.returncode == 0
    assert json.loads(done.stdout)["outcome"] == "passed", \
        "there is no failure to excerpt, so stdout is the record alone"


def test_the_excerpt_never_reaches_the_record_on_disk(delivery, run_contract):
    done = invoke(delivery, "--run", "red", "--timeout-seconds", "20", "--excerpt", "40",
                  "--step", "build=python3 -c 'print(chr(66) * 3); raise SystemExit(1)'")
    assert "BBB" in done.stdout.partition("{")[0], "the excerpt carried what the step printed"
    record = record_of(delivery, "red")
    assert [e.message for e in run_contract.iter_errors(record)] == [], \
        "the excerpt is a convenience for the caller and never evidence; siegard-run/2 is unmoved"
    assert "BBB" not in json.dumps(record), \
        "what the command printed lives in the log the record names, in one place"
    assert "excerpt" not in json.dumps(record) and "last 40" not in json.dumps(record), \
        "no trace of the flag reaches the evidence, so two runs of one command still compare"


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
    # The identity check is what keeps a run inside the delivery root, and until these rows
    # existed nothing exercised the spellings it exists for.
    (("--run", "a/b", "--timeout-seconds", "20", "--step", "a=python3 -c 'pass'"),
     "the path is the identity"),
    (("--run", "../up", "--timeout-seconds", "20", "--step", "a=python3 -c 'pass'"),
     "the path is the identity"),
    (("--run", "", "--timeout-seconds", "20", "--step", "a=python3 -c 'pass'"),
     "the path is the identity"),
    (("--run", "green\n", "--timeout-seconds", "20", "--step", "a=python3 -c 'pass'"),
     "the path is the identity"),
    # `run.log` is the combined log of every step; a step writing it destroys its own output.
    (("--run", "green", "--timeout-seconds", "20", "--step", "run=python3 -c 'pass'"),
     "combined log of every step"),
    (("--run", "green", "--timeout-seconds", "20", "--step", "a=python3 -c 'pass'",
      "--excerpt", "0"),
     "a bound of none is the flag left off"),
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


def test_it_refuses_to_choose_a_working_directory(delivery):
    """The commands only mean anything where the project sits; a directory chosen in silence would
    produce a run whose every step failed for a reason the record could not show. Invoked past the
    helper, so nothing supplies the flag on the caller's behalf."""
    done = subprocess.run([sys.executable, "-B", str(RUNNER), str(delivery),
                           "--run", "green", "--timeout-seconds", "20",
                           "--step", "a=python3 -c 'pass'"],
                          capture_output=True, text=True)
    assert done.returncode == 2
    assert "--cwd" in done.stderr, done.stderr
    assert not (delivery / "run").exists(), "a refused run leaves nothing behind"


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


def test_it_refuses_a_slug_whose_directory_is_a_dangling_symlink(delivery, tmp_path):
    """`exists()` is advisory — it follows the link and answers False for a dangling one. What
    actually refuses is `mkdir` without `exist_ok`, and its `FileExistsError` carries the same
    message as the check above it. Without this test the two paths could diverge and only the
    unreachable one would be covered."""
    (delivery / "run").mkdir(parents=True, exist_ok=True)
    (delivery / "run/green").symlink_to(tmp_path / "nowhere")
    done = invoke(delivery, "--run", "green", "--timeout-seconds", "20",
                  "--step", "a=python3 -c 'pass'")
    assert done.returncode == 2, done.stdout
    assert "already exists" in done.stderr, done.stderr


def landed(result: subprocess.CompletedProcess) -> str:
    return json.loads(result.stdout[result.stdout.index("{"):])["run"]


def test_next_takes_the_base_where_nothing_holds_it(delivery: Path) -> None:
    result = invoke(delivery, "--run", "e-t-setup", "--next", "--timeout-seconds", "30",
                    "--step", "ok=true")
    assert result.returncode == 0, result.stderr
    assert landed(result) == "run/e-t-setup"


def test_next_takes_two_after_the_base(delivery: Path) -> None:
    (delivery / "run/e-t-setup").mkdir(parents=True)
    result = invoke(delivery, "--run", "e-t-setup", "--next", "--timeout-seconds", "30",
                    "--step", "ok=true")
    assert landed(result) == "run/e-t-setup-2"


@pytest.mark.parametrize("held, expected", [
    (["e-t-setup", "e-t-setup-1", "e-t-setup-2", "e-t-setup-9"], "run/e-t-setup-10"),
    (["e-t-setup", "e-t-setup-1"], "run/e-t-setup-2"),
    (["e-t-setup-3"], "run/e-t-setup-4"),
    (["e-t-setup", "e-t-setup-2", "e-t-setup-build-7", "e-t-setup-x-4"], "run/e-t-setup-3"),
])
def test_next_takes_one_past_the_greatest_number_the_base_holds(
        delivery: Path, held: list[str], expected: str) -> None:
    for name in held:
        (delivery / "run" / name).mkdir(parents=True)
    result = invoke(delivery, "--run", "e-t-setup", "--next", "--timeout-seconds", "30",
                    "--step", "ok=true")
    assert landed(result) == expected


def test_a_refused_name_hands_the_flag_that_names_it(delivery: Path) -> None:
    (delivery / "run/e-t-setup").mkdir(parents=True)
    result = invoke(delivery, "--run", "e-t-setup", "--timeout-seconds", "30", "--step", "ok=true")
    assert result.returncode == 2
    assert "run again with --next" in result.stderr


# ---------------------------------------------------------------------- the tree it ran over


def git_in(home: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(home), "-c", "user.name=t", "-c", "user.email=t@t",
                           *args], check=True, capture_output=True, text=True).stdout


def test_a_run_records_the_tree_it_left(tmp_path, run_contract):
    """«A captured run records the tree it ran over.» (SPEC-004 R31)"""
    import hashlib
    home = tmp_path / "consumer"
    (home / "src").mkdir(parents=True)
    git_in(home, "init", "-q")
    (home / "src" / "kept.txt").write_text("kept\n", encoding="utf-8")
    (home / "src" / "gone.txt").write_text("gone\n", encoding="utf-8")
    git_in(home, "add", "-A")
    git_in(home, "commit", "-qm", "init")
    (home / "src" / "gone.txt").unlink()
    (home / "src" / "new.txt").write_text("new\n", encoding="utf-8")
    delivery = home / "delivery" / "one"
    delivery.mkdir(parents=True)
    (delivery / "run" / "earlier").mkdir(parents=True)
    (delivery / "run" / "earlier" / "run.json").write_text("{}", encoding="utf-8")
    done = invoke(delivery, "--run", "tree", "--cwd", str(home / "src"), "--timeout-seconds", "20",
                  "--step", "write=python3 -c \"open('late.txt','w').write('late')\"")
    assert done.returncode == 0, done.stderr
    record = record_of(delivery, "tree")
    assert [e.message for e in run_contract.iter_errors(record)] == []
    assert record["contract_version"] == "siegard-run/3"
    tree = record["tree"]
    assert tree["root"] == str(home.resolve())
    assert tree["head"] == git_in(home, "rev-parse", "HEAD").strip()
    digest = "sha256:" + hashlib.sha256(b"new\n").hexdigest()
    assert tree["changed"]["src/new.txt"] == digest
    assert tree["changed"]["src/gone.txt"] is None, "a deleted path is recorded as null"
    assert "src/late.txt" in tree["changed"], \
        "the tree is taken after the last step, so what a step wrote is what the run left"
    assert "src/kept.txt" not in tree["changed"], "an unchanged path is the bytes HEAD holds"
    assert not [name for name in tree["changed"] if "/run/" in f"/{name}"], \
        "the delivery root's runs — this one's logs and every earlier one — are never recorded"


def test_a_run_no_repository_holds_records_a_null_tree(tmp_path, run_contract):
    outside = tmp_path / "plain"
    outside.mkdir()
    delivery = tmp_path / "delivery"
    delivery.mkdir()
    probe = subprocess.run(["git", "-C", str(outside), "rev-parse", "--show-toplevel"],
                           capture_output=True)
    if probe.returncode == 0:
        pytest.skip("the temporary directory sits inside a git repository on this machine")
    done = invoke(delivery, "--run", "plain", "--cwd", str(outside), "--timeout-seconds", "20",
                  "--step", "one=python3 -c pass")
    assert done.returncode == 0, done.stderr
    record = record_of(delivery, "plain")
    assert record["tree"] is None
    assert [e.message for e in run_contract.iter_errors(record)] == []


# ---------------------------------------------------------------------- a run that already stands


@pytest.fixture
def standing(tmp_path: Path) -> dict:
    """A consumer whose delivery holds one passed run of a step that writes a marker; the tree is
    committed whole, so the run's tree is `HEAD` plus what the step wrote outside the records."""
    home = tmp_path / "consumer"
    for sub in ("backend/src", "siegard/specification", "siegard/work/one",
                "siegard/delivery/one", "siegard/telemetry"):
        (home / sub).mkdir(parents=True)
    (home / "siegard.json").write_text(json.dumps(
        {"specification_root": "siegard/specification", "delivery_root": "siegard/delivery",
         "work_root": "siegard/work", "telemetry_root": "siegard/telemetry",
         "targets": {"backend": "backend"}}), encoding="utf-8")
    (home / "backend" / "src" / "a.ts").write_text("a\n", encoding="utf-8")
    (home / "siegard" / "specification" / "node.md").write_text("fact\n", encoding="utf-8")
    (home / ".gitignore").write_text("marks/\n", encoding="utf-8")
    git_in(home, "init", "-q")
    git_in(home, "add", "-A")
    git_in(home, "commit", "-qm", "init")
    delivery = home / "siegard" / "delivery" / "one"
    marks = home / "marks"
    marks.mkdir()
    step = f"mark=python3 -c \"import uuid,pathlib; pathlib.Path(r'{marks}', uuid.uuid4().hex).touch()\""
    first = invoke(delivery, "--run", "task-suite", "--cwd", str(home / "backend"),
                   "--timeout-seconds", "20", "--step", step)
    assert first.returncode == 0, first.stderr
    return {"home": home, "delivery": delivery, "step": step, "marks": marks}


def reuse(s: dict, *extra: str, step: str | None = None, cwd: str = "backend"):
    return invoke(s["delivery"], "--run", "review", "--reuse", "--cwd", str(s["home"] / cwd),
                  "--timeout-seconds", "20", "--step", step or s["step"], *extra)


def ran(s: dict) -> int:
    return len(list(s["marks"].iterdir()))


def test_a_review_capture_reuses_a_passed_run_over_the_same_tree(standing):
    """«A run of the delivery that passed the steps the review would run, in the working directory
    it would run them in, over a tree whose every path outside the framework's records holds the
    bytes the tree holds now, is the review's capture, and `bin/run.py --reuse` names it and
    executes nothing.» (SPEC-004 R33)"""
    s = standing
    home = s["home"]
    (s["delivery"] / "implementation.md").write_text("record\n", encoding="utf-8")
    (home / "siegard" / "work" / "one" / "plan.md").write_text("plan\n", encoding="utf-8")
    (home / "siegard" / "telemetry" / "goal.md").write_text("goal\n", encoding="utf-8")
    (home / "siegard-trace.json").write_text("{}\n", encoding="utf-8")
    (home / "siegard-reconcile").mkdir()
    (home / "siegard-reconcile" / "review.md").write_text("judged\n", encoding="utf-8")
    git_in(home, "add", "-A")
    git_in(home, "commit", "-qm", "records")
    done = reuse(s)
    assert done.returncode == 0, done.stderr
    assert done.stdout.startswith("standing: run/task-suite"), done.stdout
    assert ran(s) == 1, "a run that stands is named, and nothing executes"
    assert not (s["delivery"] / "run" / "review").exists(), "nothing is written under --run"
    printed = json.loads(done.stdout.split("\n", 1)[1])
    assert printed["run"] == "run/task-suite"


@pytest.mark.parametrize("change", ["source", "specification", "untracked"])
def test_a_review_capture_runs_where_a_path_outside_the_records_changed(standing, change):
    s = standing
    home = s["home"]
    if change == "source":
        (home / "backend" / "src" / "a.ts").write_text("b\n", encoding="utf-8")
    elif change == "specification":
        (home / "siegard" / "specification" / "node.md").write_text("moved\n", encoding="utf-8")
        git_in(home, "commit", "-qam", "spec")
    else:
        (home / "backend" / "src" / "new.ts").write_text("new\n", encoding="utf-8")
    done = reuse(s)
    assert done.returncode == 0, done.stderr
    assert not done.stdout.startswith("standing:")
    assert ran(s) == 2
    assert record_of(s["delivery"], "review")["outcome"] == "passed"


def test_a_review_capture_runs_where_the_steps_or_directory_differ(standing):
    s = standing
    other = s["step"].replace("mark=", "suite=")
    assert not reuse(s, step=other).stdout.startswith("standing:")
    assert ran(s) == 2
    elsewhere = invoke(s["delivery"], "--run", "review-two", "--reuse", "--cwd",
                       str(s["home"] / "backend" / "src"), "--timeout-seconds", "20",
                       "--step", s["step"])
    assert not elsewhere.stdout.startswith("standing:")
    assert ran(s) == 3


def test_a_review_capture_never_reuses_a_run_that_did_not_pass(standing):
    s = standing
    failing = "mark=python3 -c \"raise SystemExit(1)\""
    first = invoke(s["delivery"], "--run", "red", "--cwd", str(s["home"] / "backend"),
                   "--timeout-seconds", "20", "--step", failing)
    assert first.returncode == 1
    again = invoke(s["delivery"], "--run", "review", "--reuse", "--cwd", str(s["home"] / "backend"),
                   "--timeout-seconds", "20", "--step", failing)
    assert again.returncode == 1
    assert not again.stdout.startswith("standing:")
    assert record_of(s["delivery"], "review")["outcome"] == "failed"
