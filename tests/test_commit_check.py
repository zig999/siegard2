"""The commit hook holds every door line a commit adds to an orchestration log to its form.

«A `git commit` a session runs in a project that declares `siegard.json` is refused by the
plugin's `PreToolUse` hook where a line it adds to an orchestration log opens with `decided:` or
`recommended:` and is not of the form R5 and R7 state with a criterion R2 names, or opens with
`decided:` over a judged criterion while no goal armed through the framework names that log's
initiative.» (SPEC-006 R12) These tests are Validation item 8 of SPEC-006, over fixture
repositories: what refuses, what goes ahead, what is never read, and that the hook never fails a
session.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
HOOK = REPO / "src/claude/hooks/commit_check.py"
SLUG = "run-one"
LOG = f"deliveries/{SLUG}/orchestration.md"
DECLARED = {"specification_root": "specification", "targets": {"app": "target"},
            "work_root": "plans", "delivery_root": "deliveries", "telemetry_root": "telemetry",
            "standard": None}
MALFORMED = "- decided: skip the task for now (delegated decision 1 of 5) — cost"
JUDGED = "- decided: /plan-work over run-one — costs less — twenty re-deliveries"
DERIVED = "- decided: /plan-work over run-one — already done — the task holds a record"
RECOMMENDED = "- recommended: /review-change over run-one — keeps the route — every task delivered"


def git(home: Path, *args: str) -> str:
    done = subprocess.run(["git", "-C", str(home), "-c", "user.name=t", "-c", "user.email=t@t",
                           *args], capture_output=True, text=True, check=True)
    return done.stdout


@pytest.fixture
def home(tmp_path: Path) -> Path:
    home = tmp_path / "consumer"
    (home / "deliveries" / SLUG).mkdir(parents=True)
    for root in ("target", "specification", "plans"):
        (home / root).mkdir()
    git(home.parent, "init", "-q", str(home))
    (home / "siegard.json").write_text(json.dumps(DECLARED), encoding="utf-8")
    (home / LOG).write_text("- plan: /plan-work over run-one — commit abc1234\n", encoding="utf-8")
    git(home, "add", "-A")
    git(home, "commit", "-q", "-m", "init")
    return home


def append(home: Path, line: str, log: str = LOG) -> None:
    path = home / log
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as out:
        out.write(line + "\n")


def arm(home: Path, slug: str) -> None:
    (home / ".git" / "siegard").mkdir(exist_ok=True)
    (home / ".git" / "siegard" / "goal.json").write_text(json.dumps({"slug": slug}),
                                                          encoding="utf-8")


def grant(home: Path, slug: str) -> None:
    (home / ".git" / "siegard").mkdir(exist_ok=True)
    (home / ".git" / "siegard" / "grant.json").write_text(json.dumps({"slug": slug}),
                                                           encoding="utf-8")


def hook(home: Path, command: str, **changed) -> subprocess.CompletedProcess:
    event = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "cwd": str(home),
             "tool_input": {"command": command}, **changed}
    return subprocess.run([sys.executable, "-B", str(HOOK)], input=json.dumps(event),
                          capture_output=True, text=True)


def refused(done: subprocess.CompletedProcess) -> str:
    assert done.returncode == 0, done.stderr
    out = json.loads(done.stdout)["hookSpecificOutput"]
    assert out["hookEventName"] == "PreToolUse" and out["permissionDecision"] == "deny"
    return out["permissionDecisionReason"]


def allowed(done: subprocess.CompletedProcess) -> None:
    assert done.returncode == 0 and done.stdout == "" and done.stderr == "", done


def test_the_hook_is_declared_for_bash_and_is_executable():
    declared = json.loads((HOOK.parent / "hooks.json").read_text(encoding="utf-8"))["hooks"]
    assert declared["PreToolUse"] == [{"matcher": "Bash", "hooks": [
        {"type": "command", "command": 'python3 "${CLAUDE_PLUGIN_ROOT}/hooks/commit_check.py"'}]}]
    assert os.access(HOOK, os.X_OK)


@pytest.mark.parametrize("command", [f"git add {LOG} && git commit -m x",
                                     f"git commit -m x -- deliveries/{SLUG}",
                                     "git commit -am 'deliver-scope run-one: x'",
                                     "git add -A && git commit -m x",
                                     f"cd sub && git -C .. commit -m x -- {LOG}"])
def test_a_line_out_of_form_is_refused_with_the_line_named(home, command):
    (home / "sub").mkdir()
    append(home, MALFORMED)
    reason = refused(hook(home, command))
    assert "decided: skip the task for now (delegated decision 1 of 5) — cost" in reason
    assert "costs less" in reason and str(home / LOG) in reason


def test_a_line_already_staged_is_read_without_a_path_named(home):
    append(home, MALFORMED)
    git(home, "add", LOG)
    assert "delegated decision" in refused(hook(home, "git commit -m 'deliver-scope run-one: x'"))


def test_a_recommendation_out_of_form_is_refused(home):
    append(home, "- recommended: rerun the suite — infrastructure failing twice — two timeouts")
    assert "recommended: rerun the suite" in refused(hook(home, "git commit -am x"))


def test_a_judged_door_with_no_goal_and_no_grant_armed_is_refused(home):
    append(home, JUDGED)
    reason = refused(hook(home, "git commit -am x"))
    assert "a judged door, and neither a goal nor a grant is armed" in reason
    assert "/siegard-goal --arm" in reason and "/siegard-grant" in reason


def test_a_judged_door_under_a_goal_armed_for_another_initiative_is_refused(home):
    arm(home, "another-run")
    append(home, JUDGED)
    assert "what is armed names another-run, not run-one" in refused(hook(home, "git commit -am x"))


def test_a_judged_door_under_a_grant_armed_for_its_initiative_goes_ahead(home):
    """«a line over a rung of the ladder is taken where a goal or a grant names the initiative»
    (SPEC-011 R6)"""
    grant(home, SLUG)
    append(home, JUDGED)
    allowed(hook(home, "git commit -am x"))


def test_a_judged_door_under_a_grant_armed_for_another_initiative_is_refused(home):
    grant(home, "another-run")
    append(home, JUDGED)
    assert "what is armed names another-run, not run-one" in refused(hook(home, "git commit -am x"))


def test_a_judged_door_under_the_goal_armed_for_its_initiative_goes_ahead(home):
    arm(home, SLUG)
    append(home, JUDGED)
    allowed(hook(home, "git commit -am x"))


@pytest.mark.parametrize("line", [DERIVED, RECOMMENDED, "- deliver task/a: implemented and proved",
                                  "- Slug derived from the ask: run-one; target decided: app",
                                  "`decided: /implement-task over a — precondition unmet — gone`"])
def test_a_derived_door_or_a_line_that_is_no_door_line_goes_ahead(home, line):
    append(home, line)
    allowed(hook(home, "git commit -am x"))


def test_a_line_already_at_head_is_never_read(home):
    append(home, MALFORMED)
    git(home, "add", "-A")
    git(home, "commit", "-q", "-m", "history")
    append(home, DERIVED)
    allowed(hook(home, "git commit -am x"))


def test_a_log_head_does_not_hold_is_read_whole(home):
    append(home, MALFORMED, log="deliveries/new-run/orchestration.md")
    assert "delegated decision" in refused(hook(home, "git add deliveries && git commit -m x"))


def test_an_adoption_log_is_read(home):
    append(home, MALFORMED, log="siegard-survey/adopted/orchestration.md")
    assert "siegard-survey" in refused(hook(home, "git add siegard-survey && git commit -m x"))


@pytest.mark.parametrize("command", ["git commit -m x -- siegard.json",
                                     "git add siegard.json && git commit -m x"])
def test_a_log_the_commit_does_not_reach_is_never_read(home, command):
    append(home, MALFORMED)
    allowed(hook(home, command))


@pytest.mark.parametrize("command", ["git log --grep commit", "git status", "ls deliveries",
                                     "git diff HEAD -- deliveries"])
def test_a_command_that_is_no_commit_is_allowed(home, command):
    append(home, MALFORMED)
    git(home, "add", LOG)
    allowed(hook(home, command))


def test_a_tool_other_than_bash_is_allowed(home):
    append(home, MALFORMED)
    allowed(hook(home, "git commit -am x", tool_name="Write"))


def test_a_project_without_siegard_json_is_allowed(home):
    (home / "siegard.json").unlink()
    git(home, "commit", "-qam", "drop")
    append(home, MALFORMED)
    allowed(hook(home, "git commit -am x"))


@pytest.mark.parametrize("stdin", ["", "not json", "[1, 2]",
                                   json.dumps({"hook_event_name": "PreToolUse", "tool_name": "Bash"}),
                                   json.dumps({"hook_event_name": "PreToolUse", "tool_name": "Bash",
                                               "cwd": "/gone/away",
                                               "tool_input": {"command": "git commit -am x"}}),
                                   json.dumps({"hook_event_name": "Stop", "tool_name": "Bash",
                                               "tool_input": {"command": "git commit -am x"}})])
def test_an_event_record_that_does_not_parse_is_allowed_in_silence(home, stdin):
    append(home, MALFORMED)
    done = subprocess.run([sys.executable, "-B", str(HOOK)], input=stdin, cwd=home,
                          capture_output=True, text=True)
    allowed(done)


def test_a_project_file_that_does_not_resolve_is_allowed(home):
    (home / "siegard.json").write_text("{not json", encoding="utf-8")
    append(home, MALFORMED)
    allowed(hook(home, "git commit -am x"))
