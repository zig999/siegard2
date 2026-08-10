"""The parallel-frontier procedure the consumer rules describe, held by CI instead of by prose.

A consumer delivers several frontier tasks concurrently by giving each one its own git worktree,
running a plain `/implement-task` in each, and integrating by merge. The framework ships no
orchestrator for this — every guarantee holds per worktree because each delivery is the ordinary
path, unvaried — so what there is to hold is the integration surface itself. The load-bearing
assertion is one fact: **the merge surface of two parallel deliveries is exactly the two derived
files**, `delivery.json` and `siegard-trace.json`, and the reconciliation is mechanical — take
either side, rederive with deliver.py, rebind each record with trace.py --bind-record — and ends
green under every validator.

That fact is not a property of git; it is a property this framework has to keep. Source and
record files merge clean because the path is the identity and nothing in a record is minted from
a clock or a session. A future change that widens the surface — a timestamp in a node, a run
named non-deterministically, a new shared file written per delivery — breaks a consumer's merge
in the field, and this module is where it breaks first.

What this deliberately does not cover: the content of a delivery (records here are composed the
way the whole suite composes them, not written by agents), and the numbers only a real consumer
run produces — frontier width, retry rate, merge-conflict rate.
"""
from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

import deliver

REPO = Path(__file__).resolve().parent.parent
BIN = REPO / "src" / "claude" / "bin"
FIXTURE = REPO / "tests" / "fixtures" / "spec-model"

PLAN_BODY = "## What it is\nProse for a reader.\n\n## Notes\nNone.\n"

TASKS = {
    "record-case": ("domain/troubleshooting/case", "A case round-trips.", "a.ts"),
    "hold-evidence": ("domain/troubleshooting/evidence", "Evidence round-trips.", "b.ts"),
}


def invoke(script: str, *args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(BIN / script), *map(str, args)],
                          capture_output=True, text=True)


def git(cwd: Path, *args) -> subprocess.CompletedProcess:
    done = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True)
    assert done.returncode == 0, f"git {' '.join(args)}: {done.stdout}{done.stderr}"
    return done


def write_node(root: Path, nid: str, front: dict) -> Path:
    path = root / f"{nid}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{yaml.safe_dump(front, sort_keys=False)}---\n{PLAN_BODY}",
                    encoding="utf-8")
    return path


@pytest.fixture
def consumer(tmp_path: Path) -> Path:
    """A consumer repository at its base commit: the project file, a sound specification, and a
    plan of one epic and two independent tasks — a frontier of width two, which is the smallest
    plan the parallel route exists for. Committed, because a worktree sees commits, never trees."""
    base = tmp_path / "base"
    base.mkdir()
    subprocess.run(["git", "init", "-q", str(base)], check=True, capture_output=True)
    git(base, "config", "user.email", "suite@test")
    git(base, "config", "user.name", "suite")
    (base / "siegard.json").write_text(
        '{\n  "specification_root": "specs",\n  "targets": {"backend": "backend"},\n'
        '  "work_root": "work",\n  "delivery_root": "delivery"\n}\n', encoding="utf-8")
    keep = base / "backend" / ".gitkeep"  # git carries no empty directory, and a consumer's
    keep.parent.mkdir()                   # target root exists before any delivery lands in it
    keep.write_text("", encoding="utf-8")
    shutil.copytree(FIXTURE, base / "specs")
    shutil.rmtree(base / "specs" / "projections", ignore_errors=True)
    work = base / "work" / "m1"
    write_node(work, "epic/checkout", {
        "title": "Checkout", "summary": "Both facts the two tasks land.",
        "covers": [node for node, _, _ in TASKS.values()]})
    for slug, (node, criterion, _) in TASKS.items():
        write_node(work, f"task/checkout/{slug}", {
            "title": slug, "summary": f"Deliver {slug}.",
            "objective": f"The fact behind {slug} is persisted.",
            "criteria": [criterion], "implements": [node]})
    derived = invoke("plan.py", work, base / "specs")
    assert derived.returncode == 0, derived.stdout + derived.stderr
    git(base, "add", "-A")
    git(base, "commit", "-qm", "base")
    return base


def worktree_for(base: Path, slug: str) -> Path:
    where = base.parent / f"wt-{slug}"
    git(base, "worktree", "add", "-q", "-b", f"batch/{slug}", str(where), "HEAD")
    return where


def deliver_in(worktree: Path, slug: str) -> None:
    """One ordinary delivery, exactly as `/implement-task` leaves it: the source, the record
    pair, the derived index, the trace bound from the record — then committed by the
    orchestrator, which is the one git act the skill never performs."""
    node, criterion, fname = TASKS[slug]
    source = worktree / "backend" / "src" / fname
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text("export {}\n", encoding="utf-8")

    root = worktree / "delivery" / "m1"
    write_node(root, f"implementation/checkout/{slug}", {
        "title": slug, "summary": f"What {slug} wrote.",
        "task": deliver.task_pin(worktree / "work" / "m1", f"task/checkout/{slug}"),
        "files": [{"path": f"src/{fname}", "effect": "holds the fact"}],
        "criteria": [{"criterion": criterion, "met": True, "how": "the source answers it"}],
        "nodes": [{"node": node, "encoded_at": [f"src/{fname}"], "how": "encoded there"}]})
    record = root / f"implementation/checkout/{slug}.md"
    write_node(root, f"proof/checkout/{slug}", {
        "title": f"Proof for {slug}", "summary": "What proves it.",
        "implementation": "sha256:" + hashlib.sha256(record.read_bytes()).hexdigest(),
        "tests": [{"file": f"tests/{slug}.spec.ts", "name": "holds", "proves": criterion,
                   "fails_when": "the fact stops holding"}]})

    derived = invoke("deliver.py", root, worktree / "work" / "m1", worktree / "backend",
                     worktree / "specs")
    assert derived.returncode == 0, derived.stdout + derived.stderr
    bound = invoke("trace.py", "--bind-record", worktree / "backend", worktree / "specs", record)
    assert bound.returncode == 0, bound.stdout + bound.stderr
    git(worktree, "add", "-A")
    git(worktree, "commit", "-qm", f"deliver {slug}")


def test_the_procedure_end_to_end(consumer):
    """The eight steps of the consumer rules' parallel route, asserted where each could break."""
    trees = {slug: worktree_for(consumer, slug) for slug in TASKS}

    # The project file resolves inside the worktree — every root a delivery reads is the
    # worktree's own, so nothing an invocation does can reach a sibling's tree.
    resolved = invoke("project.py", trees["record-case"])
    assert resolved.returncode == 0, resolved.stderr
    for line in resolved.stdout.strip().splitlines():
        assert str(trees["record-case"]) in line, \
            f"{line!r} resolves outside the worktree; two invocations would share a root"

    # Each worktree starts clean: the clean-tree stop is satisfied by construction, which is
    # the whole reason the route parallelizes what the shared tree serialized.
    for tree in trees.values():
        assert git(tree, "status", "--porcelain").stdout == ""

    for slug in TASKS:
        deliver_in(trees[slug], slug)

    # First merge clean; second conflicts on exactly the two derived files. This is the
    # load-bearing assertion: source and records merge clean because the path is the identity
    # and nothing in a record is minted from a clock. Anything that widens this set breaks a
    # consumer's merge in the field.
    git(consumer, "merge", "-q", "--no-edit", "batch/record-case")
    second = subprocess.run(["git", "-C", str(consumer), "merge", "--no-edit",
                             "batch/hold-evidence"], capture_output=True, text=True)
    assert second.returncode != 0, "the two derived files should have collided"
    unmerged = sorted(git(consumer, "diff", "--name-only",
                          "--diff-filter=U").stdout.split())
    assert unmerged == ["delivery/m1/delivery.json", "siegard-trace.json"], \
        f"the merge surface is {unmerged}; the procedure promises exactly the two derived files"

    # Resolution is mechanical because both files are derived, and derived extends to conflict
    # resolution: take either side — the content is disposable — and the completion of the
    # resolution is the rederivation, never a hand-merge.
    git(consumer, "checkout", "--ours", "delivery/m1/delivery.json", "siegard-trace.json")
    git(consumer, "add", "-A")
    git(consumer, "commit", "-q", "--no-edit")

    rederived = invoke("deliver.py", consumer / "delivery/m1", consumer / "work/m1",
                       consumer / "backend", consumer / "specs")
    assert rederived.returncode == 0, rederived.stdout + rederived.stderr
    for slug in TASKS:
        rebound = invoke("trace.py", "--bind-record", consumer / "backend", consumer / "specs",
                         consumer / f"delivery/m1/implementation/checkout/{slug}.md")
        assert rebound.returncode == 0, rebound.stdout + rebound.stderr

    # Everything green over the union, including the digests: "no drift" is what says the
    # merged files are byte-for-byte what each worktree bound, so the trace survived the merge.
    checked_plan = invoke("plan.py", "--check", consumer / "work/m1", consumer / "specs")
    assert checked_plan.returncode == 0, checked_plan.stdout
    checked = invoke("deliver.py", "--check", consumer / "delivery/m1", consumer / "work/m1",
                     consumer / "backend", consumer / "specs")
    assert checked.returncode == 0, checked.stdout
    drift = invoke("trace.py", "--check", consumer / "backend")
    assert drift.returncode == 0, drift.stdout
    assert "no drift: 2 binding(s)" in drift.stdout
    outstanding = invoke("deliver.py", "--outstanding", consumer / "delivery/m1",
                         consumer / "work/m1", consumer / "backend", consumer / "specs")
    assert "every task has a record, and every record its proof" in outstanding.stdout

    git(consumer, "add", "-A")
    git(consumer, "commit", "-qm", "reconcile the batch")
    assert git(consumer, "status", "--porcelain").stdout == "", \
        "the reconciliation left pending state; the procedure ends committed"


def test_a_failed_worktree_is_discarded_without_cleanup(consumer):
    """Recovery is free by design: a task without a record is pending, `--outstanding` derives
    that from the files, and a worktree that failed is a branch thrown away — nothing in the
    base repository has to be undone, because nothing in it was touched."""
    tree = worktree_for(consumer, "record-case")
    half = tree / "backend" / "src" / "half.ts"
    half.parent.mkdir(parents=True, exist_ok=True)
    half.write_text("export {}\n", encoding="utf-8")

    git(consumer, "worktree", "remove", "--force", str(tree))
    git(consumer, "branch", "-D", "batch/record-case")

    assert git(consumer, "status", "--porcelain").stdout == "", \
        "discarding a worktree must leave the base tree exactly as it was"
    (consumer / "delivery" / "m1").mkdir(parents=True)
    outstanding = invoke("deliver.py", "--outstanding", consumer / "delivery/m1",
                         consumer / "work/m1", consumer / "backend", consumer / "specs")
    assert outstanding.returncode == 0, outstanding.stdout + outstanding.stderr
    for slug in TASKS:
        assert f"task/checkout/{slug}: no record" in outstanding.stdout, \
            "the abandoned task reads as pending, not as anything needing repair"
