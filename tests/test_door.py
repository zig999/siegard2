"""A door is checked by what its own entry point refuses, read from disk and git (SPEC-006 R2).

Each test builds a consumer repository under git — the fixture specification, plan and delivery
moved under the roots a `siegard.json` declares, all committed — and asks `door.py --check` as a
session would before recommending a door. One test accepts per door; one test per refusal the
script decides makes that cause hold alone, so a check that stopped being run leaves its test red.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from conftest import STANDARD, derive_plan

REPO = Path(__file__).resolve().parent.parent
BIN = REPO / "src/claude/bin"
SLUG = "s"
RECORDED = "task/checkout/record-order"
READY = "task/checkout/bill-order"
DECLARED = {"specification_root": "specification", "targets": {"app": "target"},
            "work_root": "plans", "delivery_root": "deliveries", "telemetry_root": "telemetry",
            "standard": None}


def git(home: Path, *args: str) -> str:
    done = subprocess.run(["git", "-C", str(home), "-c", "user.name=t", "-c", "user.email=t@t",
                           *args], capture_output=True, text=True, check=True)
    return done.stdout.strip()


def commit(home: Path, message: str = "change") -> None:
    git(home, "add", "-A")
    git(home, "commit", "-q", "--allow-empty", "-m", message)


def derive_delivery(home: Path, slug: str = SLUG) -> None:
    done = subprocess.run([sys.executable, "-B", str(BIN / "deliver.py"),
                           str(home / "deliveries" / slug), str(home / "plans" / slug),
                           str(home / "target"), str(home / "specification")],
                          capture_output=True, text=True)
    assert done.returncode == 0, done.stdout + done.stderr


def declare(home: Path, **changed) -> None:
    fields = {**DECLARED, **changed}
    fields = {k: v for k, v in fields.items() if v is not ...}
    (home / "siegard.json").write_text(json.dumps(fields), encoding="utf-8")


def door(home: Path, skill: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(BIN / "door.py"), "--check", skill,
                           "--project", str(home), *args], capture_output=True, text=True)


def accepts(result: subprocess.CompletedProcess) -> None:
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.splitlines()[0] == "accepts"
    assert "refused:" not in result.stdout


def refuses(result: subprocess.CompletedProcess, *facts: str) -> str:
    assert result.returncode == 1, result.stdout + result.stderr
    lines = result.stdout.splitlines()
    assert lines[0] == "refuses"
    refusals = "\n".join(line for line in lines if line.startswith("refused: "))
    for fact in facts:
        assert fact in refusals, f"{fact!r} is not among the refusals:\n{result.stdout}"
    return result.stdout


@pytest.fixture
def project(tmp_path, root, work, delivery, target, sound_delivery):
    """The fixture roots under one committed git repository: a live plan whose first task is
    delivered and proven, and whose second is deliverable now."""
    home = tmp_path
    (home / "plans").mkdir()
    shutil.move(str(work), str(home / "plans" / SLUG))
    (home / "deliveries").mkdir()
    shutil.move(str(delivery), str(home / "deliveries" / SLUG))
    (target / "siegard.json").unlink()
    declare(home)
    git(home, "init", "-q")
    derive_plan(home / "plans" / SLUG, root)
    derive_delivery(home)
    commit(home, "the project")
    return home


def add_task(home: Path, name: str, front: dict, notes: str = "None.") -> None:
    path = home / "plans" / SLUG / "task" / "checkout" / f"{name}.md"
    front = {"title": name, "summary": "A task.", "objective": "It holds.",
             "criteria": [f"{name} holds."], "implements": ["domain/sales/order"], **front}
    path.write_text("---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n## What it is\n"
                    "Prose for a reader.\n\n## Notes\n" + notes + "\n", encoding="utf-8")


def rederive(home: Path) -> None:
    derive_plan(home / "plans" / SLUG, home / "specification")
    derive_delivery(home)
    commit(home)


def break_specification(home: Path) -> None:
    (home / "specification/domain/sales/broken.md").write_text(
        "---\ntype: no-such-type\n---\n## Description\nProse.\n", encoding="utf-8")
    commit(home)


# ---------------------------------------------------------------- the project file


def test_no_project_file_refuses_every_door(project):
    (project / "siegard.json").unlink()
    commit(project)
    refuses(door(project, "plan-work", "--slug", SLUG), "no siegard.json declares this project")


def test_a_root_the_door_needs_and_the_file_lacks_refuses(project):
    declare(project, delivery_root=...)
    commit(project)
    refuses(door(project, "implement-task"), "siegard.json declares no delivery_root")
    accepts(door(project, "plan-work", "--slug", SLUG))


def test_a_target_the_file_does_not_declare_refuses(project):
    refuses(door(project, "plan-work", "--slug", SLUG, "--target", "web"),
            "siegard.json declares no target web")


def test_two_targets_and_none_named_refuses(project):
    (project / "web").mkdir()
    (project / "web/.keep").write_text("", encoding="utf-8")
    declare(project, targets={"app": "target", "web": "web"}, standard={"app": None, "web": None})
    commit(project)
    refuses(door(project, "plan-work", "--slug", SLUG), "no target named")
    accepts(door(project, "plan-work", "--slug", SLUG, "--target", "app"))


def test_inputs_no_tree_decides_cannot_run(project):
    assert door(project, "no-such-skill").returncode == 2
    assert door(project, "plan-work").returncode == 2, "plan-work's slug is named, never inferred"
    assert door(project, "reconcile", "--slug", "r").returncode == 2, "a file set is named"
    assert door(project, "plan-work", "--slug", SLUG, "--task", READY).returncode == 2


# ---------------------------------------------------------------- implement-task


def test_implement_task_accepts_the_deliverable_task(project):
    result = door(project, "implement-task", "--task", READY)
    accepts(result)
    assert f"checked: deliver.py --outstanding" in result.stdout
    assert "not decided: " in result.stdout, "the prose-only refusals are listed, never guessed"


def test_implement_task_decides_the_one_deliverable_task(project):
    result = door(project, "implement-task")
    accepts(result)
    assert f"decided: task {READY} — the one task deliverable now" in result.stdout
    assert f"decided: slug {SLUG} — the one live initiative" in result.stdout


def test_implement_task_refuses_a_closed_plan(project):
    (project / "plans" / SLUG / "closure.md").write_text("Closed.\n", encoding="utf-8")
    commit(project)
    refuses(door(project, "implement-task", "--slug", SLUG, "--task", READY), "closure.md exists")


def test_implement_task_refuses_a_stale_plan(project):
    add_task(project, "refund-order", {})
    commit(project)
    refuses(door(project, "implement-task", "--task", READY), "plan.py --check")


def test_implement_task_refuses_a_pending_change_where_it_writes(project):
    (project / "target/src.ts").write_text("pending\n", encoding="utf-8")
    out = refuses(door(project, "implement-task", "--task", READY), "git status --porcelain")
    assert "src.ts" in out


def test_implement_task_refuses_a_task_the_plan_does_not_hold(project):
    refuses(door(project, "implement-task", "--task", "task/checkout/no-such-task"),
            "is not in the plan")


def test_implement_task_refuses_a_task_waiting_on_a_dependency(project):
    add_task(project, "refund-order", {"depends_on": [READY]})
    rederive(project)
    out = refuses(door(project, "implement-task", "--task", "task/checkout/refund-order"),
                  "task/checkout/refund-order waits")
    assert f"waits on {READY}" in out


def test_implement_task_refuses_a_standing_blocking_note(project):
    add_task(project, "refund-order", {}, notes="BLOCKING, from the specification — the scope "
             "refunds twice, and the specification refunds once.")
    rederive(project)
    out = refuses(door(project, "implement-task", "--task", "task/checkout/refund-order"),
                  "standing BLOCKING note")
    assert "the scope refunds twice" in out


def test_implement_task_refuses_a_blocking_note_over_a_delivered_task(project):
    task = project / "plans" / SLUG / f"{RECORDED}.md"
    task.write_text(task.read_text(encoding="utf-8").replace(
        "## Notes\nNone.", "## Notes\nBLOCKING, from the specification — the scope records "
        "twice."), encoding="utf-8")
    derive_plan(project / "plans" / SLUG, project / "specification")
    commit(project)
    refuses(door(project, "implement-task", "--task", RECORDED), "standing BLOCKING note")


def test_implement_task_refuses_no_task_over_several_deliverable(project):
    add_task(project, "refund-order", {})
    rederive(project)
    out = refuses(door(project, "implement-task"), "deliverable set does not hold exactly one")
    assert "deliverable now: " in out


def test_implement_task_refuses_a_delivery_that_does_not_hold(project):
    record = project / "deliveries" / SLUG / f"implementation/{RECORDED[5:]}.md"
    record.write_text("---\ntitle: broken\n---\n## What it is\nx\n\n## Notes\nNone.\n",
                      encoding="utf-8")
    commit(project)
    refuses(door(project, "implement-task", "--task", READY), "deliver.py --outstanding")


def test_implement_task_refuses_an_undeclared_standard(project):
    declare(project, standard=...)
    commit(project)
    refuses(door(project, "implement-task", "--task", READY),
            "siegard.json declares no standard for target app")


def test_implement_task_refuses_an_absent_substrate(project):
    registry = project / "target/standard.yaml"
    registry.write_text(yaml.safe_dump({**STANDARD, "presupposes": [{
        "path": "package.json", "provides": "the lint step PRH-01 is decided by.",
        "rules": ["PRH-01"]}]}, sort_keys=False), encoding="utf-8")
    declare(project, standard="target/standard.yaml")
    commit(project)
    out = refuses(door(project, "implement-task", "--task", READY), "deliver.py --standard")
    assert "--against" in out and "package.json" in out


# ---------------------------------------------------------------- plan-work


def test_plan_work_accepts_a_live_slug_and_a_new_one(project):
    accepts(door(project, "plan-work", "--slug", SLUG))
    accepts(door(project, "plan-work", "--slug", "refunds"))


def test_plan_work_refuses_a_closed_plan(project):
    (project / "plans" / SLUG / "closure.md").write_text("Closed.\n", encoding="utf-8")
    commit(project)
    refuses(door(project, "plan-work", "--slug", SLUG), "closure.md exists")


def test_plan_work_refuses_an_unsound_specification(project):
    break_specification(project)
    refuses(door(project, "plan-work", "--slug", SLUG), "spec.py")


def test_plan_work_refuses_a_pending_change_under_the_work_root(project):
    (project / "plans" / SLUG / "draft.md").write_text("draft\n", encoding="utf-8")
    refuses(door(project, "plan-work", "--slug", SLUG), "git status --porcelain")


def test_plan_work_refuses_an_undeclared_standard(project):
    declare(project, standard=...)
    commit(project)
    refuses(door(project, "plan-work", "--slug", SLUG), "declares no standard for target app")


def test_plan_work_refuses_a_standard_that_does_not_hold(project):
    (project / "target/standard.yaml").write_text("rules: not-a-list\n", encoding="utf-8")
    declare(project, standard="target/standard.yaml")
    commit(project)
    refuses(door(project, "plan-work", "--slug", SLUG), "deliver.py --standard")


# ---------------------------------------------------------------- review-change


def test_review_change_accepts_a_delivered_task(project):
    result = door(project, "review-change", "--task", RECORDED)
    accepts(result)
    assert f"the review's name {SLUG} is free" in result.stdout


def test_review_change_refuses_a_stale_plan(project):
    add_task(project, "refund-order", {})
    commit(project)
    refuses(door(project, "review-change", "--task", RECORDED), "plan.py --check")


def test_review_change_refuses_a_stale_delivery_index(project):
    (project / "deliveries" / SLUG / "delivery.json").unlink()
    commit(project)
    refuses(door(project, "review-change", "--task", RECORDED), "deliver.py --check")


def test_review_change_refuses_a_pending_change_under_the_delivery_root(project):
    (project / "deliveries" / SLUG / "run").mkdir()
    (project / "deliveries" / SLUG / "run/x.log").write_text("x\n", encoding="utf-8")
    refuses(door(project, "review-change", "--task", RECORDED), "git status --porcelain")


def test_review_change_refuses_a_task_nothing_delivered(project):
    refuses(door(project, "review-change", "--task", READY), "holds no implementation record")


def test_review_change_refuses_a_delivery_holding_no_record(project):
    for kind in ("implementation", "proof"):
        shutil.rmtree(project / "deliveries" / SLUG / kind)
    derive_delivery(project)
    commit(project)
    refuses(door(project, "review-change"), "holds no record — nothing is delivered")


def test_review_change_refuses_a_name_already_taken(project):
    (project / "siegard-reconcile").mkdir()
    (project / "siegard-reconcile" / f"{SLUG}.md").write_text("taken\n", encoding="utf-8")
    commit(project)
    refuses(door(project, "review-change", "--task", RECORDED), f"the review's name {SLUG} is taken")
    accepts(door(project, "review-change", "--task", RECORDED, "--name", f"{SLUG}-2"))


def test_review_change_refuses_an_undeclared_standard(project):
    declare(project, standard=...)
    commit(project)
    refuses(door(project, "review-change", "--task", RECORDED), "declares no standard")


# ---------------------------------------------------------------- deliver-scope


def test_deliver_scope_accepts_a_resume_a_new_slug_and_a_reach(project):
    result = door(project, "deliver-scope", "--slug", SLUG)
    accepts(result)
    assert "a resume from the deliverable set" in result.stdout
    accepts(door(project, "deliver-scope", "--slug", "refunds"))
    accepts(door(project, "deliver-scope", "--slug", SLUG, "--scope", "epic/checkout"))


def test_deliver_scope_refuses_an_absent_specification_root(project):
    shutil.rmtree(project / "specification")
    commit(project)
    refuses(door(project, "deliver-scope", "--slug", "refunds"), "does not exist")


def test_deliver_scope_refuses_an_unsound_specification(project):
    break_specification(project)
    refuses(door(project, "deliver-scope", "--slug", SLUG), "spec.py")


def test_deliver_scope_refuses_a_pending_change_under_a_root(project):
    (project / "plans" / SLUG / "draft.md").write_text("draft\n", encoding="utf-8")
    refuses(door(project, "deliver-scope", "--slug", SLUG), "git status --porcelain")


def test_deliver_scope_refuses_a_pending_trace(project):
    (project / "siegard-trace.json").write_text("{}\n", encoding="utf-8")
    out = refuses(door(project, "deliver-scope", "--slug", SLUG), "git status --porcelain")
    assert "siegard-trace.json" in out


def test_deliver_scope_refuses_a_closed_plan(project):
    (project / "plans" / SLUG / "closure.md").write_text("Closed.\n", encoding="utf-8")
    commit(project)
    refuses(door(project, "deliver-scope", "--slug", SLUG), "closure.md exists")


def test_deliver_scope_refuses_a_reach_the_plan_does_not_hold(project):
    refuses(door(project, "deliver-scope", "--slug", SLUG, "--scope", "epic/refunds"),
            "the scope does not name the live plan")


def test_deliver_scope_refuses_a_reach_over_no_plan(project):
    refuses(door(project, "deliver-scope", "--slug", "refunds", "--scope", "epic/checkout"),
            "holds no plan")


def test_deliver_scope_refuses_an_undeclared_telemetry_root(project):
    declare(project, telemetry_root=...)
    commit(project)
    refuses(door(project, "deliver-scope", "--slug", SLUG), "declares no telemetry_root")


def test_deliver_scope_refuses_an_undeclared_standard(project):
    declare(project, standard=...)
    commit(project)
    refuses(door(project, "deliver-scope", "--slug", SLUG), "declares no standard")


# ---------------------------------------------------------------- reconcile


@pytest.fixture
def bound(project):
    """The project with one source file bound in the trace, committed."""
    source = project / "target/src/orders/place.ts"
    source.parent.mkdir(parents=True)
    source.write_text("export const place = () => 1\n", encoding="utf-8")
    commit(project)
    done = subprocess.run([sys.executable, "-B", str(BIN / "trace.py"), "--bind",
                           str(project / "target"), str(project / "specification"),
                           "domain/sales/order", "src/orders/place.ts"],
                          capture_output=True, text=True)
    assert done.returncode == 0, done.stdout + done.stderr
    commit(project)
    return project


def reconcile(home: Path, *extra: str) -> subprocess.CompletedProcess:
    return door(home, "reconcile", "--slug", "r", "--file", "src/orders/place.ts", *extra)


def test_reconcile_accepts_a_committed_file_set(bound):
    accepts(reconcile(bound))


def test_reconcile_refuses_an_unsound_specification(bound):
    break_specification(bound)
    refuses(reconcile(bound), "spec.py")


def test_reconcile_refuses_a_target_never_bound(project):
    (project / "target/src").mkdir()
    (project / "target/src/orders.ts").write_text("x\n", encoding="utf-8")
    commit(project)
    refuses(door(project, "reconcile", "--slug", "r", "--file", "src/orders.ts"),
            "nothing has been bound in this target")


def test_reconcile_refuses_a_slug_already_taken(bound):
    (bound / "siegard-reconcile").mkdir()
    (bound / "siegard-reconcile/r.md").write_text("taken\n", encoding="utf-8")
    commit(bound)
    refuses(reconcile(bound), "siegard-reconcile/r.md exists")


def test_reconcile_refuses_a_named_file_left_uncommitted(bound):
    (bound / "target/src/orders/place.ts").write_text("export const place = () => 2\n",
                                                       encoding="utf-8")
    out = refuses(reconcile(bound), "git status --porcelain")
    assert "place.ts" in out


def test_reconcile_refuses_a_target_not_under_git(tmp_path, root, target):
    home = tmp_path
    (target / "siegard.json").unlink()
    declare(home)
    refuses(door(home, "reconcile", "--slug", "r", "--file", "src/x.ts"), "is not under git")
