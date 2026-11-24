"""The bounds hook refuses what no armed run may do to the repository, and a hand write of a
file a script owns.

«A push, a branch or a history rewrite is never a skill's, a goal's or a grant's.» (SPEC-010 R8)
«A file a script derives or captures is written by that script alone.» (SPEC-010 R9) These tests
are Validation items 6 and 7 of SPEC-010, over fixture repositories: what is refused and in which
state, what always goes ahead, what is never read as a command, and that the hook never fails a
session.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
HOOKS = REPO / "src/claude/hooks"
HOOK = HOOKS / "bounds.py"
SLUG = "run-one"
DECLARED = {"specification_root": "specification", "targets": {"app": "target"},
            "work_root": "plans", "delivery_root": "deliveries", "telemetry_root": "telemetry",
            "standard": None}

sys.path.insert(0, str(REPO / "src/claude/bin"))
import goal  # noqa: E402

REFUSED_UNDER_AN_ARMED_RUN = [
    "git push",
    "git push -u origin main 2>&1 | tail -5",
    "git push origin --delete master",
    "git checkout -b feature",
    "git checkout -B feature",
    "git switch -c feature",
    "git switch --create feature",
    "git worktree add -b batch/one ../wt-one main",
    "git branch feature",
    "git branch -D old",
    "git branch -m master main",
    "git rebase origin/main",
    "git rebase --continue",
    "git commit -q --amend --no-edit",
    "git reset --hard HEAD~1",
    "git filter-branch --tree-filter true HEAD",
    "git filter-repo --path secret --invert-paths",
    "git stash",
    "git stash -q",
    "git stash push -u -m wip -- backend",
    "git stash pop",
    "git add -A",
    "git add --all",
    "git add -u",
    "git add .",
    "git add -A -- .",
    "git commit -am 'everything'",
    "git commit -a -m everything",
    "git commit --all -m everything",
    "git status && git push",
    "git add -- a.txt; git commit -m one -- a.txt; git push",
    "GIT_TERMINAL_PROMPT=0 timeout 120 git push -u origin main",
    "git -C . push",
    "bash -c 'git push'",
    "sh -c \"git stash && git stash pop\"",
    "echo $(git push)",
]

ALWAYS_GO_AHEAD = [
    "git status --porcelain",
    "git log --oneline -5",
    "git diff -- a.txt",
    "git add -- a.txt",
    "git add -A -- src",
    "git add -A siegard/specification",
    "git commit -q -m 'plan-work run-one: plan' -- plans",
    "git commit -m 'mentions -a and --amend in the message' -- a.txt",
    "git branch --show-current",
    "git branch -a",
    "git branch --contains HEAD",
    "git stash list",
    "git stash show",
    "git checkout -- a.txt",
    "git switch main",
    "git worktree list",
    "git reset HEAD a.txt",
    "echo 'git push'",
    "echo git push",
    "grep -rn 'git push' docs",
    "printf 'run git push later\\n' > note.txt",
    "cat > note.md <<'EOF'\nThe person may git push once the run ends.\ngit rebase origin/main\nEOF",
    "python3 -c \"print('git push')\"",
]


def git(home: Path, *args: str) -> str:
    done = subprocess.run(["git", "-C", str(home), "-c", "user.name=t", "-c", "user.email=t@t",
                           *args], capture_output=True, text=True, check=True)
    return done.stdout


@pytest.fixture
def home(tmp_path: Path) -> Path:
    home = tmp_path / "consumer"
    for root in ("target", "specification", f"plans/{SLUG}", f"deliveries/{SLUG}", "telemetry"):
        (home / root).mkdir(parents=True)
    git(home.parent, "init", "-q", str(home))
    (home / "siegard.json").write_text(json.dumps(DECLARED), encoding="utf-8")
    (home / "a.txt").write_text("a\n", encoding="utf-8")
    git(home, "add", "-A")
    git(home, "commit", "-q", "-m", "init")
    return home


@pytest.fixture
def foreign(tmp_path: Path) -> Path:
    """A repository that declares no siegard.json, carrying an armed goal's record all the same."""
    home = tmp_path / "foreign"
    home.mkdir()
    git(home.parent, "init", "-q", str(home))
    arm(home, "goal")
    return home


def arm(home: Path, which: str) -> Path:
    """An armed goal or grant is read from its record's presence, exactly where goal.py and
    grant.py write it."""
    path = goal.armed_path(home)
    if which == "grant":
        path = path.with_name("grant.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"armed": which}), encoding="utf-8")
    return path


def hook(event: dict | str) -> subprocess.CompletedProcess:
    stdin = event if isinstance(event, str) else json.dumps(event)
    return subprocess.run([sys.executable, "-B", str(HOOK)], input=stdin, capture_output=True,
                          text=True, timeout=60)


def shell(command: str, cwd: Path) -> dict:
    return {"hook_event_name": "PreToolUse", "tool_name": "Bash", "cwd": str(cwd),
            "tool_input": {"command": command}}


def write(path: str | Path, cwd: Path, tool: str = "Write") -> dict:
    tool_input = {"file_path": str(path)}
    tool_input.update({"content": "x"} if tool == "Write" else
                      {"old_string": "a", "new_string": "b"} if tool == "Edit" else
                      {"edits": [{"old_string": "a", "new_string": "b"}]})
    return {"hook_event_name": "PreToolUse", "tool_name": tool, "cwd": str(cwd),
            "tool_input": tool_input}


def denied(done: subprocess.CompletedProcess) -> str | None:
    assert done.returncode == 0, done.stderr
    if not done.stdout:
        return None
    out = json.loads(done.stdout)["hookSpecificOutput"]
    assert out["hookEventName"] == "PreToolUse" and out["permissionDecision"] == "deny"
    return out["permissionDecisionReason"]


# ------------------------------------------------------------------ the shell bound (R8)


@pytest.mark.parametrize("which", ["goal", "grant"])
@pytest.mark.parametrize("command", REFUSED_UNDER_AN_ARMED_RUN)
def test_an_act_r8_names_is_refused_while_a_goal_or_a_grant_is_armed(home, which, command):
    arm(home, which)
    reason = denied(hook(shell(command, home)))
    assert reason is not None, f"{command!r} ran while {which} was armed"
    assert f"a {which} is armed" in reason, reason
    assert "never a skill's, a goal's or a grant's" in reason, reason


@pytest.mark.parametrize("command", REFUSED_UNDER_AN_ARMED_RUN)
def test_the_same_act_runs_where_neither_is_armed(home, command):
    """Outside an armed run the person's own words decide, and nothing here reads them."""
    assert denied(hook(shell(command, home))) is None, command


@pytest.mark.parametrize("command", ALWAYS_GO_AHEAD)
def test_what_r8_does_not_name_runs_while_a_goal_and_a_grant_are_armed(home, command):
    arm(home, "goal")
    arm(home, "grant")
    assert denied(hook(shell(command, home))) is None, \
        f"{command!r} was refused; a scoped stage, a commit naming paths, a read and a `git` word " \
        f"that is no command are never an act R8 names"


def test_the_reason_names_every_state_armed_and_each_act_once(home):
    arm(home, "goal")
    arm(home, "grant")
    reason = denied(hook(shell("git push; git push origin main; git stash", home)))
    assert "a goal and a grant is armed" in reason
    assert reason.count("`git push`") == 1 and "`git stash`" in reason


def test_a_cd_into_an_armed_project_is_followed(home, tmp_path):
    arm(home, "goal")
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    assert denied(hook(shell(f"cd {home} && git push", elsewhere))) is not None
    assert denied(hook(shell(f"git -C {home} push", elsewhere))) is not None
    assert denied(hook(shell("git push", elsewhere))) is None, \
        "a directory no Siegard project holds is not this hook's"


def test_a_session_below_the_toplevel_is_read_at_the_toplevel(home):
    arm(home, "grant")
    assert denied(hook(shell("git push", home / "target"))) is not None


def test_a_project_without_siegard_json_is_never_refused(foreign):
    assert denied(hook(shell("git push --force", foreign))) is None


def test_an_ended_goal_refuses_nothing(home):
    record = arm(home, "goal")
    record.unlink()
    assert denied(hook(shell("git push", home))) is None


@pytest.mark.parametrize("stdin", [
    "", "not json", "[]", json.dumps({"hook_event_name": "Stop"}),
    json.dumps({"hook_event_name": "PreToolUse", "tool_name": "Bash"}),
    json.dumps({"hook_event_name": "PreToolUse", "tool_name": "Bash",
                "tool_input": {"command": 7}}),
    json.dumps({"hook_event_name": "PreToolUse", "tool_name": "Bash", "cwd": "/no/such/dir",
                "tool_input": {"command": "git push"}}),
    json.dumps({"hook_event_name": "PreToolUse", "tool_name": "Bash",
                "tool_input": {"command": "git push 'unterminated"}}),
])
def test_input_it_cannot_read_never_fails_a_session(stdin):
    done = hook(stdin)
    assert done.returncode == 0 and done.stdout == "", (done.stdout, done.stderr)


def test_a_command_shlex_cannot_split_is_still_read(home):
    arm(home, "goal")
    assert denied(hook(shell("git push 'unterminated", home))) is not None


# ------------------------------------------------------------------ the write bound (R9)


OWNED = {
    "siegard-trace.json": "bin/trace.py",
    f"plans/{SLUG}/plan.json": "bin/plan.py",
    f"deliveries/{SLUG}/delivery.json": "bin/deliver.py",
    f"deliveries/{SLUG}/run/{SLUG}-build/run.json": "bin/run.py",
    f"deliveries/{SLUG}/run/{SLUG}-build/build.log": "bin/run.py",
    "target/siegard-trace.json": "bin/trace.py",
}

FREE = [
    "siegard.json",
    "plans/plan.json",
    f"plans/{SLUG}/task/epic/one.md",
    "target/plan.json",
    "target/run/notes.json",
    f"deliveries/{SLUG}/implementation/epic/one.md",
    f"deliveries/{SLUG}/orchestration.md",
    "target/src/delivery.json",
]


@pytest.mark.parametrize("tool", ["Write", "Edit", "MultiEdit"])
@pytest.mark.parametrize("relative", sorted(OWNED))
def test_a_file_a_script_owns_is_refused_to_every_writing_tool(home, tool, relative):
    reason = denied(hook(write(home / relative, home, tool)))
    assert reason is not None, f"{tool} of {relative} went ahead"
    assert OWNED[relative] in reason, reason


@pytest.mark.parametrize("relative", sorted(OWNED))
def test_the_write_bound_holds_whether_or_not_a_run_is_armed(home, relative):
    arm(home, "goal")
    assert denied(hook(write(home / relative, home))) is not None


@pytest.mark.parametrize("relative", FREE)
def test_every_other_file_of_the_project_is_written_freely(home, relative):
    assert denied(hook(write(home / relative, home))) is None, \
        f"{relative} was refused; siegard.json is /siegard-config's, and a file outside an " \
        f"initiative's roots is no file a script owns"


def test_a_relative_path_is_read_from_the_working_directory(home):
    assert denied(hook(write(f"plans/{SLUG}/plan.json", home))) is not None
    assert denied(hook(write(f"{SLUG}/plan.json", home / "plans"))) is not None


def test_a_path_spelled_with_dot_segments_is_read_as_the_file_it_names(home):
    spelled = home / "target" / ".." / "deliveries" / SLUG / "delivery.json"
    assert denied(hook(write(spelled, home))) is not None


def test_a_project_without_siegard_json_writes_every_file(foreign):
    (foreign / "plans" / SLUG).mkdir(parents=True)
    assert denied(hook(write(foreign / "siegard-trace.json", foreign))) is None
    assert denied(hook(write(foreign / "plans" / SLUG / "plan.json", foreign))) is None


@pytest.mark.parametrize("stdin", [
    json.dumps({"hook_event_name": "PreToolUse", "tool_name": "Write"}),
    json.dumps({"hook_event_name": "PreToolUse", "tool_name": "Write",
                "tool_input": {"file_path": ""}}),
    json.dumps({"hook_event_name": "PreToolUse", "tool_name": "Edit",
                "tool_input": {"file_path": ["x"]}}),
    json.dumps({"hook_event_name": "PreToolUse", "tool_name": "Read",
                "tool_input": {"file_path": "/x/siegard-trace.json"}}),
])
def test_a_write_event_it_cannot_read_never_fails_a_session(stdin):
    done = hook(stdin)
    assert done.returncode == 0 and done.stdout == ""


# ------------------------------------------------------------------ the declaration


def test_the_hook_is_declared_for_the_shell_and_for_every_writing_tool():
    declared = json.loads((HOOKS / "hooks.json").read_text(encoding="utf-8"))["hooks"]
    groups = {group["matcher"]: [h["command"] for h in group["hooks"]]
              for group in declared["PreToolUse"]}
    command = 'python3 "${CLAUDE_PLUGIN_ROOT}/hooks/bounds.py"'
    assert command in groups["Bash"]
    assert groups["Write|Edit|MultiEdit"] == [command]


def test_the_session_rules_state_the_bound_the_hook_holds():
    rules = " ".join((HOOKS / "rules.md").read_text(encoding="utf-8").split())
    assert ("a push, a branch, a stash or a rewrite only on the person's own words in this "
            "session, never while a goal or grant is armed.") in rules
    assert "never `git add -A`, a branch, a push" not in rules
