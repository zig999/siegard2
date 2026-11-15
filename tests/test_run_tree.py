"""A record binds only the bytes a run of its task saw.

«`bin/trace.py --bind-record` refuses a record whose file it would bind where the file's bytes are
not what a run that the task's implementation or proof record points at saw; a run recorded
without a tree is named in a receipt and refuses nothing.» (SPEC-004 R31) These tests are the
`--bind-record` half of SPEC-004's validation item 17, over fixture repositories whose runs are
captured by `bin/run.py` itself.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent
BIN = REPO / "src/claude/bin"
FIXTURE = REPO / "tests" / "fixtures" / "spec-model"
NODE = "domain/troubleshooting/case"
FILE = "src/orders/place.ts"
STORED = f"backend/{FILE}"


def git(home: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(home), "-c", "user.name=t", "-c", "user.email=t@t",
                           *args], check=True, capture_output=True, text=True).stdout


def script(name: str, *args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(BIN / name), *map(str, args)],
                          capture_output=True, text=True, timeout=120)


@pytest.fixture
def consumer(tmp_path: Path) -> Path:
    """A repository with a specification, a target under `backend/` and one initiative's delivery
    root, everything committed."""
    home = tmp_path / "consumer"
    home.mkdir()
    git(home, "init", "-q")
    shutil.copytree(FIXTURE, home / "specs")
    shutil.rmtree(home / "specs" / "projections", ignore_errors=True)
    (home / "backend/src/orders").mkdir(parents=True)
    (home / "backend" / FILE).write_text("export function place() {}\n", encoding="utf-8")
    (home / "delivery").mkdir()
    git(home, "add", "-A")
    git(home, "commit", "-qm", "init")
    return home


def capture(home: Path, name: str) -> str:
    done = script("run.py", home / "delivery", "--run", name, "--cwd", home / "backend",
                  "--timeout-seconds", "30", "--step", "build=python3 -c pass")
    assert done.returncode == 0, done.stdout + done.stderr
    return f"run/{name}"


def record(home: Path, kind: str, run: str | None) -> Path:
    path = home / "delivery" / kind / "checkout" / "place.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    front = {"title": "Record a placed order", "summary": "What this delivery wrote.",
             "task": "sha256:" + "0" * 64,
             "files": [{"path": FILE, "effect": "persists the order"}],
             "criteria": [{"criterion": "It works.", "met": True, "how": "it does"}],
             "nodes": [{"node": NODE, "encoded_at": [FILE], "how": "place() persists the case"}]}
    if run is not None:
        front["run"] = run
    path.write_text(f"---\n{yaml.safe_dump(front, sort_keys=False)}---\n## What it is\nProse.\n\n"
                    f"## Notes\nNone.\n", encoding="utf-8")
    return path


def bind(home: Path, implementation: Path) -> subprocess.CompletedProcess:
    return script("trace.py", "--bind-record", home / "backend", home / "specs", implementation)


def edit(home: Path, text: str = "export function place() { return 1 }\n") -> None:
    (home / "backend" / FILE).write_text(text, encoding="utf-8")


def bound(home: Path) -> bool:
    trace = home / "siegard-trace.json"
    if not trace.is_file():
        return False
    held = json.loads(trace.read_text(encoding="utf-8"))
    return any(f["path"] == STORED for e in held["bindings"] for f in e["files"])


def test_a_file_the_implementation_run_saw_unchanged_from_head_is_bound(consumer):
    implementation = record(consumer, "implementation", capture(consumer, "place-build"))
    done = bind(consumer, implementation)
    assert done.returncode == 0, done.stdout + done.stderr
    assert bound(consumer)
    assert "recorded no tree" not in done.stdout


def test_a_file_the_run_saw_uncommitted_is_bound_by_its_digest(consumer):
    edit(consumer)
    run = capture(consumer, "place-build")
    tree = json.loads((consumer / "delivery" / run / "run.json").read_text())["tree"]
    assert STORED in tree["changed"]
    done = bind(consumer, record(consumer, "implementation", run))
    assert done.returncode == 0, done.stdout + done.stderr
    assert bound(consumer)


def test_a_file_changed_after_the_only_run_is_refused_and_nothing_is_bound(consumer):
    implementation = record(consumer, "implementation", capture(consumer, "place-build"))
    edit(consumer)
    done = bind(consumer, implementation)
    assert done.returncode == 1, done.stdout + done.stderr
    assert f"cannot bind: {STORED}: its bytes are not what run/place-build saw" in done.stdout
    assert "bin/run.py --next" in done.stdout
    assert not bound(consumer), "a record's bindings are one act; none is written"


def test_the_proofs_later_run_answers_for_a_source_the_implementer_fixed(consumer):
    """A red suite answered `code` sends the implementer back after the implementation record was
    written; the suite run that follows saw the source the bind pins."""
    implementation = record(consumer, "implementation", capture(consumer, "place-build"))
    edit(consumer)
    record(consumer, "proof", capture(consumer, "place-suite"))
    done = bind(consumer, implementation)
    assert done.returncode == 0, done.stdout + done.stderr
    assert bound(consumer)


def test_a_file_changed_after_both_runs_is_refused_naming_both(consumer):
    implementation = record(consumer, "implementation", capture(consumer, "place-build"))
    record(consumer, "proof", capture(consumer, "place-suite"))
    edit(consumer)
    done = bind(consumer, implementation)
    assert done.returncode == 1
    assert "not what run/place-build, run/place-suite saw" in done.stdout


def test_a_file_committed_again_after_the_run_is_refused(consumer):
    """A path the run did not see changed is held to the blob its `HEAD` held, not today's."""
    implementation = record(consumer, "implementation", capture(consumer, "place-build"))
    edit(consumer)
    git(consumer, "commit", "-qam", "change after the run")
    done = bind(consumer, implementation)
    assert done.returncode == 1, done.stdout
    assert "its bytes are not what run/place-build saw" in done.stdout


def test_a_run_captured_without_a_tree_binds_with_a_receipt(consumer):
    run = capture(consumer, "place-build")
    held = consumer / "delivery" / run / "run.json"
    captured = json.loads(held.read_text())
    captured.pop("tree")
    captured["contract_version"] = "siegard-run/2"
    held.write_text(json.dumps(captured), encoding="utf-8")
    edit(consumer)
    done = bind(consumer, record(consumer, "implementation", run))
    assert done.returncode == 0, done.stdout + done.stderr
    assert bound(consumer)
    assert f"{run} recorded no tree, so the files bound from place.md were not held" in done.stdout


def test_a_run_captured_in_a_worktree_is_read_by_the_paths_and_the_commit(consumer):
    """A run in a worktree of this repository spells its paths from its own toplevel and names a
    commit the repository holds; the batch flow binds over it after the merge."""
    run = capture(consumer, "place-build")
    held = consumer / "delivery" / run / "run.json"
    captured = json.loads(held.read_text())
    captured["tree"]["root"] = str(consumer.parent / "wt-place")
    held.write_text(json.dumps(captured), encoding="utf-8")
    done = bind(consumer, record(consumer, "implementation", run))
    assert done.returncode == 0, done.stdout + done.stderr


def test_a_record_outside_an_implementation_or_proof_root_is_never_held(consumer):
    """A reconciliation record names no run of a task; the bind reads none."""
    run = capture(consumer, "place-build")
    elsewhere = record(consumer, "implementation", run)
    moved = consumer / "siegard-reconcile" / "place.md"
    moved.parent.mkdir()
    shutil.move(elsewhere, moved)
    edit(consumer)
    done = bind(consumer, moved)
    assert "its bytes are not what" not in done.stdout
