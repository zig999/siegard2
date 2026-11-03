"""`bin/archive.py` decides which closed initiatives may leave the working tree and removes exactly
those: closed, committed, valid as history, and taken as a whole pair. What carries understanding
— the specification, the trace, the reconciliation records — never leaves, and no git command that
writes is ever run: the tag and the commit are printed for the person.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import derive_plan

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "src/claude/bin/archive.py"
DELIVER = REPO / "src/claude/bin/deliver.py"


def git(where: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(where), "-c", "user.email=t@t", "-c", "user.name=t",
                           *args], capture_output=True, text=True, check=True)


def archive(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(SCRIPT), *map(str, args)],
                          capture_output=True, text=True)


def derive_delivery(delivery: Path, work: Path, target: Path) -> None:
    done = subprocess.run([sys.executable, "-B", str(DELIVER), str(delivery), str(work),
                           str(target)], capture_output=True, text=True)
    assert done.returncode == 0, done.stdout + done.stderr


@pytest.fixture
def project(tmp_path, root, work, delivery, target, sound_delivery):
    """A project holding one closed initiative, `checkout`, whose plan and delivery validate, plus
    what carries understanding beside them, all committed."""
    plans, deliveries = tmp_path / "plans", tmp_path / "deliveries"
    plans.mkdir()
    deliveries.mkdir()
    shutil.move(str(work), plans / "checkout")
    shutil.move(str(delivery), deliveries / "checkout")
    closed = plans / "checkout"
    (closed / "closure.md").write_text("Closed: delivered.\n", encoding="utf-8")
    derive_plan(closed)
    derive_delivery(deliveries / "checkout", closed, target)
    (tmp_path / "siegard.json").write_text(json.dumps({
        "specification_root": "specification", "targets": {"app": "target"},
        "work_root": "plans", "delivery_root": "deliveries"}), encoding="utf-8")
    (tmp_path / "siegard-trace.json").write_text("{}\n", encoding="utf-8")
    (tmp_path / "siegard-reconcile").mkdir()
    (tmp_path / "siegard-reconcile/checkout.md").write_text("a record\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, capture_output=True)
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-qm", "the closed initiative")
    return tmp_path


def test_a_closed_committed_valid_pair_is_eligible_and_check_changes_nothing(project):
    done = archive("--check", project, "--all")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "eligible checkout:" in done.stdout
    assert "1 eligible, 0 skipped, of 1 in scope" in done.stdout
    assert (project / "plans/checkout").is_dir() and (project / "deliveries/checkout").is_dir()


def test_remove_takes_the_pair_whole_and_leaves_understanding_and_git_alone(project):
    head = git(project, "rev-parse", "HEAD").stdout.strip()
    done = archive("--remove", project, "checkout")
    assert done.returncode == 0, done.stdout + done.stderr
    assert not (project / "plans/checkout").exists()
    assert not (project / "deliveries/checkout").exists()
    for kept in ("siegard-trace.json", "siegard-reconcile/checkout.md", "specification",
                 "siegard.json"):
        assert (project / kept).exists(), f"{kept} carries understanding and must stay"
    assert git(project, "rev-parse", "HEAD").stdout.strip() == head, "archive.py committed"
    assert git(project, "tag", "-l").stdout == "", "archive.py tagged"
    assert f"tag -a archive/" in done.stdout and head in done.stdout, \
        "the tag must name the commit the removal starts from"
    assert "add -A -- plans/checkout deliveries/checkout" in done.stdout
    assert "commit -m \"siegard-archive: checkout\"" in done.stdout
    assert "brings any of it back" in done.stdout
    assert "no remote" in done.stdout
    assert "spec.py" in done.stdout and "trace.py --check" in done.stdout


def test_a_live_initiative_is_never_eligible(project):
    shutil.copytree(project / "plans/checkout", project / "plans/open")
    (project / "plans/open/closure.md").unlink()
    git(project, "add", "-A")
    git(project, "commit", "-qm", "a live initiative")
    named = archive("--check", project, "open")
    assert named.returncode == 1
    assert "skipped open: criterion 1 closed" in named.stdout
    every = archive("--remove", project, "--all")
    assert "live, left as they are: open" in every.stdout
    assert (project / "plans/open").is_dir()


@pytest.mark.parametrize("how", ["changed", "untracked", "ignored"])
def test_a_pair_git_does_not_hold_as_it_stands_is_skipped_and_stays(project, how):
    record = project / "deliveries/checkout/run-note.log"
    if how == "changed":
        (project / "plans/checkout/closure.md").write_text("Closed again.\n", encoding="utf-8")
    elif how == "untracked":
        record.write_text("a log nobody committed\n", encoding="utf-8")
    else:
        (project / ".gitignore").write_text("*.log\n", encoding="utf-8")
        git(project, "add", ".gitignore")
        git(project, "commit", "-qm", "ignore logs")
        record.write_text("a log git ignores\n", encoding="utf-8")
    done = archive("--remove", project, "checkout")
    assert done.returncode == 1
    assert "skipped checkout: criterion 2 committed" in done.stdout
    assert (project / "plans/checkout").is_dir() and (project / "deliveries/checkout").is_dir()


def test_a_delivery_never_derived_names_the_derivation_that_answers_it(project):
    (project / "deliveries/checkout/delivery.json").unlink()
    git(project, "add", "-A")
    git(project, "commit", "-qm", "an index nobody derived")
    done = archive("--check", project, "checkout")
    assert done.returncode == 1
    assert "criterion 3 valid history: deliver.py --check against app" in done.stdout
    assert "answers it: python3 -B" in done.stdout and "deliver.py" in done.stdout
    assert "then commit what it wrote and check again" in done.stdout


def test_a_target_no_record_names_is_asked_where_the_project_declares_two(project):
    bare = project / "deliveries/bare"
    shutil.copytree(project / "plans/checkout", project / "plans/bare")
    bare.mkdir()
    (bare / "orchestration.md").write_text("# bare\n", encoding="utf-8")
    derive_delivery(bare, project / "plans/bare", project / "target")
    (project / "web").mkdir()
    (project / "web/.keep").write_text("", encoding="utf-8")
    (project / "siegard.json").write_text(json.dumps({
        "specification_root": "specification", "targets": {"app": "target", "web": "web"},
        "work_root": "plans", "delivery_root": "deliveries"}), encoding="utf-8")
    git(project, "add", "-A")
    git(project, "commit", "-qm", "a second target and a delivery naming none")
    asked = archive("--check", project, "bare")
    assert asked.returncode == 1
    assert "no record names a target" in asked.stdout and "--target <key>" in asked.stdout
    named = archive("--check", project, "bare", "--target", "app")
    assert named.returncode == 0, named.stdout + named.stderr
    records = archive("--check", project, "checkout")
    assert records.returncode == 0, "a delivery whose records name a target needs no --target"


def test_remove_takes_only_what_passed(project):
    shutil.copytree(project / "plans/checkout", project / "plans/open")
    (project / "plans/open/closure.md").unlink()
    git(project, "add", "-A")
    git(project, "commit", "-qm", "a live initiative")
    done = archive("--remove", project, "checkout", "open")
    assert done.returncode == 1
    assert not (project / "plans/checkout").exists()
    assert (project / "plans/open").is_dir()
    assert "removed from the tree: checkout" in done.stdout


@pytest.mark.parametrize("args", [
    ("--check",),
    ("--check", "{p}"),
    ("--check", "{p}", "--all", "checkout"),
    ("--check", "{p}", "--remove", "{p}", "--all"),
    ("--check", "{p}", "--all", "--target", "nowhere"),
])
def test_an_unstated_or_contradictory_invocation_cannot_run(project, args):
    done = archive(*[a.format(p=project) for a in args])
    assert done.returncode == 2, done.stdout + done.stderr
    assert done.stderr.startswith("cannot run:")
    assert (project / "plans/checkout").is_dir()
