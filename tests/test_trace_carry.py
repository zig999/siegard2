"""`trace.py --carry`: a pair whose node changed in form alone is restamped without a judgment.

«A pair whose node changed in form alone is carried to the node as it stands without a judgment»
(SPEC-005 R13), form being what SPEC-003 R7 sets aside — key order, quoting, wrapping. Every
test below is one of the proofs SPEC-005's validation item 11 names: what is carried, what is
left and why, what a carry never touches, and that a second carry changes nothing.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

import spec
import trace

REPO = Path(__file__).resolve().parent.parent
TRACE_PY = Path(trace.__file__)
FIXTURE = REPO / "tests" / "fixtures" / "spec-model"
NODE = "domain/troubleshooting/case"
OTHER = "domain/troubleshooting/evidence"
FILE = "src/orders/place.ts"
SECOND = "src/orders/bill.ts"
STORED = f"backend/{FILE}"
STORED_SECOND = f"backend/{SECOND}"


def run(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(TRACE_PY), *map(str, args)],
                          capture_output=True, text=True)


def git(home: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(home), "-c", "user.name=t", "-c", "user.email=t@t", *args],
                   check=True, capture_output=True)


def node_path(home: Path, node: str = NODE) -> Path:
    return home / "specs" / f"{node}.md"


def reform(home: Path, node: str = NODE) -> None:
    """Rewrite a node with the same reading: its frontmatter re-serialised with keys sorted and
    every scalar re-quoted as the dumper chooses, its body untouched."""
    path = node_path(home, node)
    front, body, problem = spec.parse_node(path)
    assert problem is None
    dumped = yaml.safe_dump(front, sort_keys=True, default_flow_style=False, width=40)
    path.write_text(f"---\n{dumped}---\n{body}", encoding="utf-8")
    assert spec.reading_of(path.read_bytes()) is not None


def binding(home: Path, node: str = NODE) -> dict:
    return next(e for e in json.loads((home / "siegard-trace.json").read_text(
        encoding="utf-8"))["bindings"] if e["node"] == node)


def stamped(entry: dict, stored: str) -> str:
    held = next(f for f in entry["files"] if f["path"] == stored)
    return trace.stamped_against(entry, held)


def moved_lines(home: Path) -> list[str]:
    done = run("--check", home / "backend", "--all")
    return [line for line in done.stdout.splitlines() if "moved since" in line
            or "was stamped against" in line]


@pytest.fixture
def bound(tmp_path: Path) -> Path:
    """A consumer whose specification and bindings are committed: NODE bound to both files,
    OTHER to the first."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, capture_output=True)
    shutil.copytree(FIXTURE, tmp_path / "specs")
    shutil.rmtree(tmp_path / "specs" / "projections", ignore_errors=True)
    target = tmp_path / "backend"
    (target / "src/orders").mkdir(parents=True)
    (target / FILE).write_text("export function place() {}\n", encoding="utf-8")
    (target / SECOND).write_text("export function bill() {}\n", encoding="utf-8")
    (tmp_path / "siegard.json").write_text(json.dumps(
        {"specification_root": "specs", "targets": {"backend": "backend"},
         "work_root": "work"}) + "\n", encoding="utf-8")
    assert run("--bind", target, tmp_path / "specs", NODE, FILE, SECOND).returncode == 0
    assert run("--bind", target, tmp_path / "specs", OTHER, FILE).returncode == 0
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-qm", "bound")
    return tmp_path


def test_a_node_changed_in_form_alone_is_carried_without_a_judge(bound):
    reform(bound)
    git(bound, "commit", "-qam", "reform")
    assert moved_lines(bound), "a reformatted node moves its digest, so its pairs report moved"
    done = run("--carry", bound / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert f"carried {NODE}: 2 pair(s)" in done.stdout
    assert "same reading, no judgment" in done.stdout
    assert not moved_lines(bound)
    current = spec.digest_of(node_path(bound))
    entry = binding(bound)
    assert entry["digest"] == current
    assert stamped(entry, STORED) == stamped(entry, STORED_SECOND) == current


def test_a_changed_frontmatter_value_is_left_as_it_stood(bound):
    path = node_path(bound)
    front, body, _ = spec.parse_node(path)
    front["operations"] = list(reversed(front["operations"]))
    path.write_text(f"---\n{yaml.safe_dump(front, sort_keys=False)}---\n{body}", encoding="utf-8")
    git(bound, "commit", "-qam", "reorder operations")
    before = binding(bound)
    done = run("--carry", bound / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert f"left {NODE} {STORED}: the node's reading changed, not its form alone" in done.stdout
    assert binding(bound) == before, "a list's order is a value, and a value that moved is read"


def test_a_changed_body_is_left_as_it_stood(bound):
    path = node_path(bound)
    path.write_text(path.read_text(encoding="utf-8").replace(
        "A customer problem", "A customer's problem"), encoding="utf-8")
    git(bound, "commit", "-qam", "reword")
    done = run("--carry", bound / "backend")
    assert "the node's reading changed, not its form alone" in done.stdout
    assert "0 pair(s) carried" in done.stdout


def test_a_stamped_text_git_does_not_hold_carries_nothing(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, capture_output=True)
    shutil.copytree(FIXTURE, tmp_path / "specs")
    shutil.rmtree(tmp_path / "specs" / "projections", ignore_errors=True)
    target = tmp_path / "backend"
    (target / "src/orders").mkdir(parents=True)
    (target / FILE).write_text("export function place() {}\n", encoding="utf-8")
    (tmp_path / "siegard.json").write_text(json.dumps(
        {"specification_root": "specs", "targets": {"backend": "backend"}}) + "\n",
        encoding="utf-8")
    assert run("--bind", target, tmp_path / "specs", NODE, FILE).returncode == 0
    reform(tmp_path)
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-qm", "only the reformed text was ever committed")
    done = run("--carry", target)
    assert done.returncode == 0, done.stdout + done.stderr
    assert (f"left {NODE} {STORED}: git holds no text of the node at the digest this file was "
            f"stamped against") in done.stdout


def test_a_pair_an_open_finding_stands_against_is_left(bound, monkeypatch, capsys):
    reform(bound)
    git(bound, "commit", "-qam", "reform")
    monkeypatch.setattr(trace, "open_owed", lambda home: {(NODE, STORED)})
    assert trace.carry(bound / "backend", []) == 0
    said = capsys.readouterr().out
    assert f"left {NODE} {STORED}: an open finding stands against this pair" in said
    assert f"carried {NODE}: 1 pair(s)" in said
    entry = binding(bound)
    current = spec.digest_of(node_path(bound))
    assert stamped(entry, STORED_SECOND) == current
    assert stamped(entry, STORED) != current
    assert entry["digest"] != current, \
        "a binding one of whose files still reads the earlier text is not restamped whole"


def test_a_node_a_live_plan_pins_is_left_and_a_closed_plan_pins_nothing(bound):
    pinned = spec.digest_of(node_path(bound))
    initiative = bound / "work" / "round"
    initiative.mkdir(parents=True)
    (initiative / "plan.json").write_text(json.dumps({"contract_version": "plan/1", "nodes": [],
        "edges": [{"from": "task/e/t", "to": NODE, "kind": "implements", "at": "implements[0]",
                   "digest": pinned}]}), encoding="utf-8")
    reform(bound)
    git(bound, "add", "-A")
    git(bound, "commit", "-qm", "reform under a live plan")
    done = run("--carry", bound / "backend")
    assert (f"left {NODE} {STORED}: a live plan pins the node at the text this file was stamped "
            f"against") in done.stdout
    (initiative / "closure.md").write_text("closed\n", encoding="utf-8")
    done = run("--carry", bound / "backend")
    assert f"carried {NODE}: 2 pair(s)" in done.stdout, done.stdout


def test_a_carry_keeps_the_file_digest_judged_decided_by_and_proof(bound):
    trace_file = bound / "siegard-trace.json"
    declared = json.loads(trace_file.read_text(encoding="utf-8"))
    entry = next(e for e in declared["bindings"] if e["node"] == NODE)
    first = next(f for f in entry["files"] if f["path"] == STORED)
    first["judged"] = True
    entry["decided_by"] = "test"
    entry["step"] = "test"
    entry["proof"] = [{"path": STORED_SECOND, "digest": "sha256:" + "0" * 64}]
    trace_file.write_text(json.dumps(declared, indent=2) + "\n", encoding="utf-8")
    git(bound, "commit", "-qam", "certified by hand")
    kept = {k: v for k, v in entry.items() if k not in ("digest", "files")}
    file_digests = {f["path"]: (f["digest"], f.get("judged")) for f in entry["files"]}
    reform(bound)
    git(bound, "commit", "-qam", "reform")
    done = run("--carry", bound / "backend")
    assert f"carried {NODE}: 2 pair(s)" in done.stdout, done.stdout + done.stderr
    after = binding(bound)
    assert {k: v for k, v in after.items() if k not in ("digest", "files")} == kept
    assert {f["path"]: (f["digest"], f.get("judged")) for f in after["files"]} == file_digests


def test_an_earlier_equivalent_text_is_carried_and_a_non_equivalent_one_is_not(bound):
    path = node_path(bound)
    path.write_text(path.read_text(encoding="utf-8").replace(
        "A customer problem", "A customer's problem"), encoding="utf-8")
    git(bound, "commit", "-qam", "reword")
    assert run("--bind", bound / "backend", bound / "specs", NODE, FILE).returncode == 0
    git(bound, "commit", "-qam", "rebind the first file")
    reform(bound)
    git(bound, "commit", "-qam", "reform")
    done = run("--carry", bound / "backend")
    assert f"carried {NODE}: 1 pair(s)" in done.stdout, done.stdout
    assert f"left {NODE} {STORED_SECOND}: the node's reading changed" in done.stdout
    entry = binding(bound)
    current = spec.digest_of(path)
    assert stamped(entry, STORED) == current
    assert stamped(entry, STORED_SECOND) != current


def test_a_second_carry_changes_nothing(bound):
    reform(bound)
    git(bound, "commit", "-qam", "reform")
    assert run("--carry", bound / "backend").returncode == 0
    written = (bound / "siegard-trace.json").read_bytes()
    done = run("--carry", bound / "backend")
    assert done.returncode == 0
    assert "0 pair(s) carried over 0 node(s)" in done.stdout
    assert (bound / "siegard-trace.json").read_bytes() == written


def test_a_named_node_no_binding_names_is_refused(bound):
    done = run("--carry", bound / "backend", "--node", "domain/troubleshooting/hypothesis")
    assert done.returncode == 1
    assert "no binding names it" in done.stdout


def test_node_scopes_the_carry(bound):
    reform(bound)
    reform(bound, OTHER)
    git(bound, "commit", "-qam", "reform both")
    done = run("--carry", bound / "backend", "--node", OTHER)
    assert f"carried {OTHER}: 1 pair(s)" in done.stdout
    assert NODE not in done.stdout.split("\n\n")[0]


def test_a_target_with_no_trace_has_nothing_to_carry_and_is_no_refusal(tmp_path):
    """A first adoption runs `/reconcile` over a target nothing has been bound in yet, and its
    step 2 runs `--carry` before `--check`: with no trace there is nothing that moved, which is an
    ordinary state, answered the way `--check` answers it — never a refusal that stops the route."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, capture_output=True)
    (tmp_path / "backend").mkdir()
    shutil.copytree(FIXTURE, tmp_path / "specs")
    (tmp_path / "siegard.json").write_text(json.dumps(
        {"specification_root": "specs", "targets": {"backend": "backend"}}) + "\n",
        encoding="utf-8")
    done = run("--carry", tmp_path / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "no trace file" in done.stdout and "nothing is carried" in done.stdout
    assert not (tmp_path / "siegard-trace.json").exists()
