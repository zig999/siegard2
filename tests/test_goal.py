"""A goal ends on a script's answer: state A, state B, or not yet (SPEC-008).

Each test builds a consumer repository under git — the fixture specification, plan and delivery
moved under the roots a `siegard.json` declares — commits it the way `/deliver-scope` would, and
asks `goal.py` as a consumer runs it. One test per condition of R2 makes that condition fail
alone, so a check that stopped being run would leave its test red rather than every test green.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from conftest import derive_plan

REPO = Path(__file__).resolve().parent.parent
BIN = REPO / "src/claude/bin"
SLUG = "s"
TASK = "task/checkout/record-order"
VERSION = json.loads((REPO / "src/claude/.claude-plugin/plugin.json").read_text())["version"]


def git(home: Path, *args: str) -> str:
    done = subprocess.run(["git", "-C", str(home), "-c", "user.name=t", "-c", "user.email=t@t",
                           *args], capture_output=True, text=True, check=True)
    return done.stdout.strip()


def commit(home: Path, message: str, *paths: str) -> str:
    git(home, "add", "--", *(paths or ["."]))
    git(home, "commit", "-q", "-m", message)
    return git(home, "rev-parse", "HEAD")


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(BIN / "goal.py"), *args],
                          capture_output=True, text=True)


def derive_delivery(home: Path) -> None:
    done = subprocess.run([sys.executable, "-B", str(BIN / "deliver.py"),
                           str(home / "deliveries" / SLUG), str(home / "plans" / SLUG),
                           str(home / "target"), str(home / "specification")],
                          capture_output=True, text=True)
    assert done.returncode == 0, done.stdout + done.stderr


REVIEW = {
    "target": "app",
    "title": "Checkout, first review",
    "summary": "What the passes found.",
    "reviewed": ["src/orders/place.ts", "tests/place.spec.ts"],
    "tasks": [TASK],
    "passes": [
        {"pass": "coverage"},
        {"pass": "conformance"},
        {"pass": "standard", "missing": "this project has authored no standard"},
        {"pass": "failures", "missing": "no run was captured"},
    ],
    "coverage": [{"criterion": "Submitting a valid order returns its order_number.",
                  "state": "covered",
                  "tests": [{"file": "tests/place.spec.ts",
                             "name": "returns the order_number for a valid submission"}]}],
    "unpaired": [],
}


@pytest.fixture
def project(tmp_path, root, work, delivery, target, sound_delivery):
    """The fixture roots under one git repository, with the plan committed before the goal began
    and the delivery held back, so each test commits it as the run would."""
    home = tmp_path
    (home / "plans").mkdir()
    shutil.move(str(work), str(home / "plans" / SLUG))
    held = home.parent / f"{home.name}-held-delivery"
    shutil.move(str(delivery), str(held))
    (target / "siegard.json").unlink()
    (home / "siegard.json").write_text(json.dumps({
        "specification_root": "specification", "targets": {"app": "target"},
        "work_root": "plans", "delivery_root": "deliveries", "telemetry_root": "telemetry",
    }), encoding="utf-8")
    derive_plan(home / "plans" / SLUG, root)
    git(home, "init", "-q")
    since = commit(home, "the project before the goal")
    return {"home": home, "since": since, "held": held}


def deliver(project: dict) -> None:
    home = project["home"]
    (home / "deliveries").mkdir(exist_ok=True)
    shutil.move(str(project["held"]), str(home / "deliveries" / SLUG))
    derive_delivery(home)
    commit(home, f"deliver-scope {SLUG}: deliver record-order", "deliveries")


def review(project: dict) -> None:
    home = project["home"]
    path = home / "deliveries" / SLUG / "review" / "first.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("---\n" + yaml.safe_dump(REVIEW, sort_keys=False) + "---\n## What it is\nProse for a reader.\n\n## Notes\nNone.\n",
                    encoding="utf-8")
    derive_delivery(home)
    commit(home, f"deliver-scope {SLUG}: review", "deliveries")


def log(project: dict, *lines: str) -> None:
    path = project["home"] / "deliveries" / SLUG / "orchestration.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write("".join(f"{line}\n" for line in lines))


def measure(project: dict) -> None:
    home = project["home"]
    (home / "telemetry").mkdir(exist_ok=True)
    (home / "telemetry" / "report.json").write_text("{}\n", encoding="utf-8")
    commit(home, f"deliver-scope {SLUG}: measure", "telemetry",
           *(["deliveries"] if (home / "deliveries").is_dir() else []))


def state(project: dict, *extra: str, version: str = VERSION) -> subprocess.CompletedProcess:
    return run("--state", str(project["home"]), "--slug", SLUG, "--scope", TASK,
               "--since", project["since"], "--version", version, *extra)


def first(result: subprocess.CompletedProcess) -> str:
    assert result.returncode in (0, 1), result.stderr
    return result.stdout.splitlines()[0]


def failing(result: subprocess.CompletedProcess) -> set[str]:
    return set(re.findall(r"^check (\S+): FAIL$", result.stdout, re.M))


# ------------------------------------------------------------------------------- state A (R2)


def test_a_scope_delivered_reviewed_and_measured_is_state_a(project):
    deliver(project)
    review(project)
    log(project, f"- /review-change over {TASK}: recorded.")
    measure(project)
    result = state(project)
    assert first(result).startswith("state A"), result.stdout
    assert result.returncode == 0
    assert failing(result) == set()



def substrate_alone(project: dict) -> None:
    """The scope's one task re-planned, before the goal began, as the one that builds the
    substrate, and its delivery held back as such: the implementation writes the artifact the
    task produces and nothing a rule reaches, and no proof is written beside it."""
    import hashlib
    home = project["home"]
    task = home / "plans" / SLUG / "task" / "checkout" / "record-order.md"
    _, front, body = task.read_text(encoding="utf-8").split("---\n", 2)
    data = yaml.safe_load(front)
    data["produces"] = ["package.json"]
    task.write_text("---\n" + yaml.safe_dump(data, sort_keys=False) + "---\n" + body,
                    encoding="utf-8")
    derive_plan(home / "plans" / SLUG, home / "specification")
    (home / "target" / "package.json").write_text("{}\n", encoding="utf-8")
    project["since"] = commit(home, "the project before the goal, its substrate task planned")
    record = project["held"] / "implementation" / "checkout" / "record-order.md"
    _, front, body = record.read_text(encoding="utf-8").split("---\n", 2)
    data = yaml.safe_load(front)
    data["task"] = "sha256:" + hashlib.sha256(task.read_bytes()).hexdigest()
    data["files"] = [{"path": "package.json", "effect": "declares the build and the suite"}]
    record.write_text("---\n" + yaml.safe_dump(data, sort_keys=False) + "---\n" + body,
                      encoding="utf-8")
    (project["held"] / "proof" / "checkout" / "record-order.md").unlink()


def test_a_scope_whose_task_is_the_substrate_alone_reaches_state_a_without_a_proof(project):
    """«State A holds when every task of the scope holds an implementation record and a proof
    record, or an implementation record of the substrate alone, which owes no proof» (SPEC-008
    R2). A plan whose first task builds the substrate would otherwise end every goal in state B."""
    substrate_alone(project)
    deliver(project)
    review(project)
    measure(project)
    result = state(project)
    assert first(result).startswith("state A"), result.stdout
    assert "implemented as the substrate alone, which owes no proof" in result.stdout

def test_records_no_review_names_after_them_are_not_yet(project):
    deliver(project)
    measure(project)
    result = state(project)
    assert first(result).startswith("not yet")
    assert result.returncode == 1
    assert failing(result) == {"review"}


def test_a_measure_older_than_the_review_is_not_yet(project):
    deliver(project)
    measure(project)
    review(project)
    result = state(project)
    assert failing(result) == {"measure"}


def test_a_change_left_in_the_tree_is_not_yet_unless_the_condition_declared_it(project):
    deliver(project)
    review(project)
    measure(project)
    (project["home"] / "notes.txt").write_text("somebody's work in progress\n")
    assert failing(state(project)) == {"tree"}
    assert first(state(project, "--untouched", "notes.txt")).startswith("state A")


def test_a_commit_naming_no_skill_and_the_slug_is_state_b_on_its_own(project):
    deliver(project)
    review(project)
    (project["home"] / "notes.txt").write_text("x\n")
    foreign = commit(project["home"], "tidy up", "notes.txt")
    measure(project)
    result = state(project)
    assert failing(result) == {"commits"}
    assert first(result) == ("state B — a commit since the goal began names no skill and the "
                             "slug, which the route never rewrites")
    assert result.returncode == 0
    assert f"  {foreign} tidy up" in result.stdout


def test_a_foreign_commit_ends_the_goal_before_the_route_has_delivered(project):
    (project["home"] / "notes.txt").write_text("x\n")
    commit(project["home"], "the person's own edit", "notes.txt")
    result = state(project)
    assert first(result).startswith("state B — a commit since the goal began names no skill")
    assert "records" in failing(result)


def unmet(project: dict) -> None:
    """The held implementation record says its criterion is unmet, and the proof is re-pinned to
    it, so the delivery still checks against its sources."""
    import hashlib
    held = project["held"]
    record = held / "implementation/checkout/record-order.md"
    before = "sha256:" + hashlib.sha256(record.read_bytes()).hexdigest()
    text = record.read_text(encoding="utf-8")
    assert "met: true" in text
    record.write_text(text.replace("met: true", "met: false", 1), encoding="utf-8")
    after = "sha256:" + hashlib.sha256(record.read_bytes()).hexdigest()
    proof = held / "proof/checkout/record-order.md"
    proof.write_text(proof.read_text(encoding="utf-8").replace(before, after), encoding="utf-8")


def test_a_criterion_recorded_unmet_is_state_b_with_the_criterion_named(project):
    unmet(project)
    deliver(project)
    review(project)
    measure(project)
    result = state(project)
    assert failing(result) == {"criteria"}, result.stdout
    assert first(result) == (f"state B — {SLUG}: the scope is delivered, reviewed and measured, "
                             f"and its records name criteria unmet")
    assert result.returncode == 0
    assert (f"    {TASK}: Submitting a valid order returns its order_number."
            in result.stdout.splitlines())


def test_a_criterion_recorded_unmet_with_work_left_is_not_yet(project):
    unmet(project)
    deliver(project)
    measure(project)
    result = state(project)
    assert first(result).startswith("not yet")
    assert failing(result) == {"review", "criteria"}


def test_a_criterion_a_review_left_uncovered_is_named_and_fails_nothing(project):
    deliver(project)
    home = project["home"]
    path = home / "deliveries" / SLUG / "review" / "first.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    left = {**REVIEW, "coverage": [{"criterion": "Submitting a valid order returns its "
                                                 "order_number.",
                                    "state": "partial",
                                    "why": "no test submits an order the store refuses"}]}
    path.write_text("---\n" + yaml.safe_dump(left, sort_keys=False) + "---\n## What it is\n"
                    "Prose for a reader.\n\n## Notes\nNone.\n", encoding="utf-8")
    derive_delivery(home)
    commit(home, f"deliver-scope {SLUG}: review", "deliveries")
    measure(project)
    result = state(project)
    assert first(result).startswith("state A"), result.stdout
    lines = result.stdout.splitlines()
    assert f"  deliveries/{SLUG}/review/first.md left 1 criterion(s) other than covered:" in lines
    assert "    partial: Submitting a valid order returns its order_number." in lines


def test_a_commit_already_on_a_remote_is_not_yet(project, tmp_path_factory):
    deliver(project)
    review(project)
    measure(project)
    remote = tmp_path_factory.mktemp("remote")
    git(remote, "init", "-q", "--bare")
    git(project["home"], "remote", "add", "origin", str(remote))
    git(project["home"], "push", "-q", "origin", "HEAD:refs/heads/main")
    git(project["home"], "fetch", "-q", "origin")
    assert failing(state(project)) == {"remote"}


def test_a_task_of_the_scope_without_records_is_not_yet(project):
    measure(project)
    result = state(project)
    assert "records" in failing(result)


# ------------------------------------------------------------------------------- state B (R3)


def test_a_stop_line_closing_the_log_with_the_measure_committed_is_state_b(project):
    log(project, "- /implement-task over task/checkout/record-order: the delivery gave up.",
        "stop: gave-up — the build stayed red after three attempts")
    commit(project["home"], f"deliver-scope {SLUG}: log the stop", "deliveries")
    measure(project)
    result = state(project)
    assert first(result) == "state B — stop: gave-up — the build stayed red after three attempts"
    assert result.returncode == 0


def test_a_stop_that_left_files_is_state_b_and_lists_them_for_the_person(project):
    log(project, "stop: producers — the diagnosis reads the test and the code apart")
    commit(project["home"], f"deliver-scope {SLUG}: log the stop", "deliveries")
    measure(project)
    (project["home"] / "target" / "half-written.ts").write_text("export {}\n")
    result = state(project)
    assert first(result) == ("state B — stop: producers — the diagnosis reads the test and the "
                             "code apart; the uncommitted files below are left for the person")
    assert "target/half-written.ts" in result.stdout


def test_a_reconciliation_touching_only_the_trace_and_its_record_is_on_the_route(project):
    deliver(project)
    review(project)
    home = project["home"]
    (home / "siegard-trace.json").write_text("{}\n")
    (home / "siegard-reconcile").mkdir()
    (home / "siegard-reconcile" / "drift.md").write_text("record\n")
    commit(home, "reconcile drift: rebind the reader", "siegard-trace.json", "siegard-reconcile")
    measure(project)
    assert "commits" not in failing(state(project))
    (home / "notes.txt").write_text("x\n")
    commit(home, "reconcile drift: and a note", "notes.txt")
    assert "commits" in failing(state(project))


def test_a_stop_line_whose_class_is_none_of_the_list_is_not_state_b(project):
    log(project, "stop: tired — nothing left to say")
    commit(project["home"], f"deliver-scope {SLUG}: log the stop", "deliveries")
    measure(project)
    assert first(state(project)).startswith("not yet")


def test_a_stop_line_before_the_measure_is_not_yet(project):
    log(project, "stop: rebind — domain/sales/order moved since the plan was derived")
    commit(project["home"], f"deliver-scope {SLUG}: log the stop", "deliveries")
    result = state(project)
    assert first(result).startswith("not yet")
    assert "measure" in failing(result)


def test_a_plugin_whose_version_changed_is_state_b_on_its_own(project):
    assert first(state(project, version="0.0.0")).startswith(
        "state B — the plugin's version changed")


def test_a_commit_touching_the_project_file_is_state_b_on_its_own(project):
    home = project["home"]
    declared = json.loads((home / "siegard.json").read_text())
    (home / "siegard.json").write_text(json.dumps({**declared, "edits_freely": ["app"]}))
    commit(home, f"deliver-scope {SLUG}: widen the surface route", "siegard.json")
    assert first(state(project)).startswith("state B — a commit since the goal began touched "
                                            "siegard.json")


# ---------------------------------------------------------------------- the condition (R6)


def compose(project: dict, *extra: str) -> subprocess.CompletedProcess:
    return run("--compose", str(project["home"]), "--slug", SLUG, *extra)


def test_a_composed_condition_names_the_route_the_scope_and_the_state_command(project):
    (project["home"] / "notes.txt").write_text("pending elsewhere\n")
    result = compose(project, "--scope", "epic/checkout")
    assert result.returncode == 0, result.stdout + result.stderr
    condition = result.stdout.split("paste after /goal:\n\n", 1)[1]
    assert "/siegard:deliver-scope" in condition
    assert "Scope: epic/checkout" in condition
    assert "Leave untouched — never edit, commit or discard: notes.txt." in condition
    command = condition.strip().splitlines()[-1]
    assert "goal.py --state" in command and f"--version {VERSION}" in command
    assert "--untouched notes.txt" in command and "--scope epic/checkout" in command
    assert len(condition) <= 4000


def test_a_budget_and_a_findings_policy_are_stated_in_the_condition(project):
    result = compose(project, "--scope", TASK, "--budget", "2", "--correct", "contradicts")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Budget: 2 judged door(s), each taken only as the door decider returns it." \
        in result.stdout
    assert "Findings: correct contradicts by a corrective increment, once" in result.stdout
    plain = compose(project, "--scope", TASK).stdout
    assert "Budget: no judged door; a choice a fact does not decide ends the run." in plain
    assert "Findings: report them all; correct none." in plain


def test_a_findings_policy_naming_a_kind_no_route_corrects_is_refused(project):
    result = compose(project, "--scope", TASK, "--correct", "restates")
    assert result.returncode == 2
    assert "no route corrects it" in result.stderr


def test_a_cited_objective_is_copied_whole_from_its_file(project, tmp_path):
    cited = tmp_path / "cited.md"
    cited.write_text("Parte 2: testes que faltam.\n\n  - item: com dois pontos\n",
                     encoding="utf-8")
    result = compose(project, "--objective-file", str(cited))
    assert result.returncode == 0, result.stdout + result.stderr
    (written,) = (project["home"] / "telemetry").glob(f"goal-*-{SLUG}.md")
    assert written.read_bytes() == cited.read_bytes()
    both = compose(project, "--objective-file", str(cited), "--objective", "x")
    assert both.returncode == 2


def test_to_specify_is_the_persons_and_only_over_an_objective(project):
    result = compose(project, "--objective", "An order is billed once.", "--specify")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Specify: run /analyse once over the objective, before the plan" in result.stdout
    assert "Specify:" not in compose(project, "--objective", "An order is billed once.").stdout
    assert compose(project, "--scope", TASK, "--specify").returncode == 2


def test_composing_over_a_pending_change_under_the_roots_is_refused(project):
    task = project["home"] / "plans" / SLUG / f"{TASK}.md"
    task.write_text(task.read_text() + "\n")
    result = compose(project, "--scope", TASK)
    assert result.returncode == 1
    assert "changes are pending under the specification, work, delivery or target root" \
        in result.stdout


def test_composing_over_a_pending_trace_or_reconciliation_record_is_refused(project):
    home = project["home"]
    (home / "siegard-trace.json").write_text("{}\n", encoding="utf-8")
    result = compose(project, "--scope", TASK)
    assert result.returncode == 1
    assert "the trace or siegard-reconcile/ holds a change pending" in result.stdout
    assert "siegard-trace.json" in result.stdout
    commit(home, "reconcile drift: bind", "siegard-trace.json")
    record = home / "siegard-reconcile" / "drift.md"
    record.parent.mkdir()
    record.write_text("---\n---\n", encoding="utf-8")
    result = compose(project, "--scope", TASK)
    assert result.returncode == 1
    assert "siegard-reconcile/drift.md" in result.stdout
    record.unlink()
    assert compose(project, "--scope", TASK).returncode == 0


def test_a_specification_root_not_yet_created_is_refused_naming_both_ways_to_create_it(project):
    settings = project["home"] / "siegard.json"
    fields = json.loads(settings.read_text(encoding="utf-8"))
    fields["specification_root"] = "not-yet"
    settings.write_text(json.dumps(fields), encoding="utf-8")
    commit(project["home"], "point the specification root at a directory not created yet")
    result = compose(project, "--objective", "Orders are billed once.")
    assert result.returncode == 1
    assert "the specification root not-yet does not exist yet" in result.stdout
    assert "/analyse over that material" in result.stdout and "--specify" in result.stdout
    assert "not sound" not in result.stdout


def test_composing_over_an_id_the_plan_does_not_hold_is_refused(project):
    result = compose(project, "--scope", "epic/nothing")
    assert result.returncode == 1
    assert "epic/nothing is no epic of this plan" in result.stdout


def test_composing_over_a_closed_slug_is_refused(project):
    (project["home"] / "plans" / SLUG / "closure.md").write_text("Closed.\n")
    commit(project["home"], f"plan-work {SLUG}: close")
    result = compose(project, "--objective", "Orders are billed once.")
    assert result.returncode == 1
    assert "holds closure.md" in result.stdout


def test_an_objective_travels_by_file_and_the_condition_stays_one_line_each(project):
    objective = "An order is billed once.\n" * 200
    result = compose(project, "--objective", objective)
    assert result.returncode == 0, result.stdout + result.stderr
    condition = result.stdout.split("paste after /goal:\n\n", 1)[1].strip()
    assert len(condition) < 1500 and "An order is billed once." not in condition
    assert "\n" not in condition, "a condition is one line the person pastes whole"
    (written,) = (project["home"] / "telemetry").glob(f"goal-*-{SLUG}.md")
    assert written.read_text() == objective
    assert f"Scope: the objective in telemetry/{written.name} (sha256 " in condition


# ------------------------------------------------------------------- the stop classes (R3, R4)


def stop_classes_of_the_skill() -> list[str]:
    text = (REPO / "src/claude/skills/deliver-scope/SKILL.md").read_text(encoding="utf-8")
    section = text.split("## What ends the run", 1)[1].split("\nThe log then closes", 1)[0]
    bullets = re.split(r"\n- ", section)[1:]
    return [re.findall(r"`([a-z-]+)`[;.]?\s*$", bullet.strip())[-1] for bullet in bullets]


def test_every_stop_of_deliver_scope_carries_one_class_of_the_list():
    import goal
    classes = stop_classes_of_the_skill()
    assert sorted(classes) == sorted(goal.STOP_CLASSES), \
        "a stop /deliver-scope names and goal.py cannot read as state B leaves a goal unending"
    requirement = (REPO / "specs/goal.md").read_text(encoding="utf-8")
    listed = re.search(r"\*\*R3\*\* — (.*?)\n", requirement).group(1)
    assert sorted(re.findall(r"`([a-z-]+)`", listed)) == sorted(goal.STOP_CLASSES)


# ------------------------------------------------------------------ the restricted scope (R5)


def outstanding(project: dict, *scope: str) -> subprocess.CompletedProcess:
    home = project["home"]
    return subprocess.run([sys.executable, "-B", str(BIN / "deliver.py"), "--outstanding",
                           str(project["held"]), str(home / "plans" / SLUG),
                           str(home / "target"), str(home / "specification"), *scope],
                          capture_output=True, text=True)


def test_a_task_scope_carries_what_it_depends_on(project):
    result = outstanding(project, "--scope", "task/checkout/bill-order")
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines()[0] == (
        "scope: task/checkout/bill-order — 1 task(s), and 1 it depends on: "
        "task/checkout/record-order")
    assert "task/checkout/bill-order: no record" in result.stdout


def test_a_scope_whose_tasks_hold_their_records_says_so(project):
    result = outstanding(project, "--scope", TASK)
    assert "every task in the scope has a record, and every record its proof" in result.stdout
    assert "bill-order" not in result.stdout


def test_an_epic_scope_carries_its_tasks(project):
    result = outstanding(project, "--scope", "epic/checkout")
    assert result.stdout.splitlines()[0] == "scope: epic/checkout — 2 task(s)"


def test_a_scope_id_the_plan_does_not_hold_is_refused(project):
    result = outstanding(project, "--scope", "task/checkout/nothing")
    assert result.returncode == 2
    assert "task/checkout/nothing is no task of this plan" in result.stderr


def test_a_scope_outside_the_outstanding_report_is_refused(project):
    home = project["home"]
    result = subprocess.run([sys.executable, "-B", str(BIN / "deliver.py"), "--check",
                             str(project["held"]), str(home / "plans" / SLUG),
                             str(home / "target"), str(home / "specification"),
                             "--scope", TASK], capture_output=True, text=True)
    assert result.returncode == 2
    assert "only --outstanding prints one" in result.stderr
