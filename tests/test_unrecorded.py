"""`deliver.py --unrecorded`: a delivery's tree held to the records it names (SPEC-004 R16).

Each consumer here is a git repository with one committed baseline, so what the working tree
changed since `HEAD` is exactly what the test did afterwards — the state the delivering
invocation's clean-tree stop guarantees before it writes.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent
DELIVER = REPO / "src" / "claude" / "bin" / "deliver.py"


def git(home: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(home), "-c", "user.email=t@t", "-c", "user.name=t", *args],
                   check=True, capture_output=True)


def put(path: Path, text: str = "x\n") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def record(home: Path, kind: str, **front) -> Path:
    path = home / "delivery" / "slug" / kind / "epic" / "task.md"
    body = yaml.safe_dump(dict(target="backend", **front), sort_keys=False)
    return put(path, f"---\n{body}---\n## What was done\nProse.\n\n## Notes\nNone.\n")


def run(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(DELIVER), "--unrecorded", *map(str, args)],
                          capture_output=True, text=True)


@pytest.fixture
def consumer(tmp_path: Path) -> Path:
    home = tmp_path / "consumer"
    put(home / "siegard.json", json.dumps({
        "specification_root": "knowledge", "work_root": "work", "delivery_root": "delivery",
        "telemetry_root": "telemetry", "targets": {"backend": "src"}}))
    put(home / "src" / "orders" / "place.ts")
    put(home / "src" / "orders" / "place.spec.ts")
    put(home / "src" / "orders" / "legacy.ts")
    put(home / "knowledge" / "domain" / "orders" / "_context.md")
    git(home, "init", "-q")
    git(home, "add", "-A")
    git(home, "commit", "-qm", "base")
    return home


def test_a_tree_every_record_names_is_sound(consumer):
    put(consumer / "src" / "orders" / "place.ts", "changed\n")
    put(consumer / "src" / "orders" / "place.spec.ts", "changed\n")
    impl = record(consumer, "implementation",
                  files=[{"path": "orders/place.ts", "effect": "places"}])
    proof = record(consumer, "proof", tests=[{"file": "orders/place.spec.ts", "name": "n",
                                              "proves": "p", "fails_when": "f"}])
    done = run(consumer / "src", impl, proof)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "is named by the 2 record(s) given" in done.stdout


def test_an_adjusted_test_no_record_names_is_refused(consumer):
    """The shape the measurement found: a test an earlier task wrote, changed by this delivery,
    and left out of both records — so the review handed the records' file set never reads it."""
    put(consumer / "src" / "orders" / "place.ts", "changed\n")
    put(consumer / "src" / "orders" / "place.spec.ts", "weakened\n")
    impl = record(consumer, "implementation",
                  files=[{"path": "orders/place.ts", "effect": "places"}])
    done = run(consumer / "src", impl)
    assert done.returncode == 1
    assert "unrecorded: orders/place.spec.ts" in done.stdout
    assert "unrecorded: orders/place.ts" not in done.stdout


def test_an_untracked_file_counts_as_changed(consumer):
    put(consumer / "src" / "orders" / "new-helper.ts")
    impl = record(consumer, "implementation", files=[])
    done = run(consumer / "src", impl)
    assert done.returncode == 1
    assert "unrecorded: orders/new-helper.ts" in done.stdout


def test_a_helper_the_proof_names_in_files_is_admitted(consumer):
    put(consumer / "src" / "orders" / "place.test-support.ts")
    proof = record(consumer, "proof",
                   files=[{"path": "orders/place.test-support.ts", "effect": "builds an order"}])
    done = run(consumer / "src", proof)
    assert done.returncode == 0, done.stdout + done.stderr


def test_a_deleted_path_a_record_names_is_admitted(consumer):
    (consumer / "src" / "orders" / "legacy.ts").unlink()
    impl = record(consumer, "implementation",
                  files=[{"path": "orders/legacy.ts", "effect": "removed"}])
    assert run(consumer / "src", impl).returncode == 0


def test_a_deleted_path_no_record_names_is_refused(consumer):
    (consumer / "src" / "orders" / "legacy.ts").unlink()
    impl = record(consumer, "implementation", files=[])
    done = run(consumer / "src", impl)
    assert done.returncode == 1
    assert "unrecorded: orders/legacy.ts" in done.stdout


def test_a_change_outside_the_target_is_not_this_delivery_s(consumer):
    put(consumer / "README.md")
    impl = record(consumer, "implementation", files=[])
    assert run(consumer / "src", impl).returncode == 0


def test_the_framework_s_own_roots_are_never_the_change(tmp_path):
    """A target that is the whole tree holds the delivery root, the specification and the trace
    under it; the records and the runs are written there, and none of it is source."""
    home = tmp_path / "whole"
    put(home / "siegard.json", json.dumps({
        "specification_root": "knowledge", "work_root": "work", "delivery_root": "delivery",
        "telemetry_root": "telemetry", "targets": {"backend": "."}}))
    put(home / "app.ts")
    git(home, "init", "-q")
    git(home, "add", "-A")
    git(home, "commit", "-qm", "base")
    put(home / "app.ts", "changed\n")
    put(home / "siegard-trace.json", "{}\n")
    put(home / "knowledge" / "rules" / "a.md")
    put(home / "work" / "slug" / "plan.json", "{}\n")
    put(home / "telemetry" / "r.json", "{}\n")
    put(home / "siegard-reconcile" / "r.json", "{}\n")
    put(home / "delivery" / "slug" / "run" / "x" / "run.log")
    impl = record(home, "implementation", files=[{"path": "app.ts", "effect": "runs"}])
    done = run(home, impl)
    assert done.returncode == 0, done.stdout + done.stderr


def test_a_record_over_an_undeclared_target_cannot_run(consumer):
    path = record(consumer, "implementation", files=[])
    path.write_text(path.read_text(encoding="utf-8").replace("target: backend", "target: nowhere"),
                    encoding="utf-8")
    done = run(consumer / "src", path)
    assert done.returncode == 2
    assert "does not declare" in done.stderr


def test_no_record_named_cannot_run(consumer):
    done = run(consumer / "src")
    assert done.returncode == 2


def test_a_tree_with_no_commit_cannot_run(tmp_path):
    home = tmp_path / "fresh"
    put(home / "siegard.json", json.dumps({"targets": {"backend": "src"}}))
    put(home / "src" / "a.ts")
    git(home, "init", "-q")
    impl = record(home, "implementation", files=[])
    done = run(home / "src", impl)
    assert done.returncode == 2
    assert "no commit" in done.stderr


def committed_record(home: Path, **front) -> Path:
    """An implementation record an earlier delivery wrote and committed — the record a
    re-delivery replaces."""
    path = record(home, "implementation", **front)
    git(home, "add", "-A")
    git(home, "commit", "-qm", "first delivery")
    return path


def test_a_re_delivery_carries_the_files_its_task_already_wrote(consumer):
    """«A re-delivery names a file the tree did not change only where the record it replaces
    named it» (SPEC-004 R21): the task's own files, unchanged, answer the task as it stands."""
    committed_record(consumer, files=[{"path": "orders/place.ts", "effect": "places"}])
    impl = record(consumer, "implementation",
                  files=[{"path": "orders/place.ts", "effect": "places, and answers the node "
                                                        "the re-bind added"}])
    done = run(consumer / "src", impl)
    assert done.returncode == 0, done.stdout + done.stderr


def test_a_re_delivery_naming_an_unchanged_file_its_task_never_wrote_is_refused(consumer):
    """An unchanged file the replaced record did not name is source the task never wrote; the
    fact standing there is R20's stop, not this re-delivery's to claim."""
    committed_record(consumer, files=[{"path": "orders/place.ts", "effect": "places"}])
    impl = record(consumer, "implementation",
                  files=[{"path": "orders/place.ts", "effect": "places"},
                         {"path": "orders/legacy.ts", "effect": "already answers the node"}])
    done = run(consumer / "src", impl)
    assert done.returncode == 1
    assert ("uncarried: " in done.stdout
            and "names orders/legacy.ts, which the tree did not change and the record it "
                "replaces did not name" in done.stdout), done.stdout
    assert "orders/place.ts, which the tree did not change" not in done.stdout


def test_a_re_delivery_naming_a_file_it_changed_is_held_as_any_delivery(consumer):
    committed_record(consumer, files=[{"path": "orders/place.ts", "effect": "places"}])
    put(consumer / "src" / "orders" / "legacy.ts", "rewritten\n")
    impl = record(consumer, "implementation",
                  files=[{"path": "orders/place.ts", "effect": "places"},
                         {"path": "orders/legacy.ts", "effect": "rewritten for the node"}])
    assert run(consumer / "src", impl).returncode == 0


def test_a_first_delivery_is_not_held_to_a_record_it_replaces(consumer):
    """No record at `HEAD` is a first delivery: the check is a re-delivery's alone, and a first
    delivery stays held to R16 and nothing more here."""
    impl = record(consumer, "implementation",
                  files=[{"path": "orders/legacy.ts", "effect": "named, unchanged"}])
    assert run(consumer / "src", impl).returncode == 0
