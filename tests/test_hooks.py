"""The plugin's hooks are what place the session rules.

`hooks/rules.md` reaches a context only through `hooks/hooks.json`: a `SessionStart` reaches the
session and never the agents it spawns, a `SubagentStart` reaches that agent alone, and both run
`hooks/rules.py` over the one file. A hook declared for one event and not the other is rules half
the contexts never hold; a script that fails is every session of every project stopped at start.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "src/claude"
HOOKS = SRC / "hooks"
RULES = HOOKS / "rules.md"
SCRIPT = HOOKS / "rules.py"
EVENTS = ("SessionStart", "SubagentStart")


def declared() -> dict:
    return json.loads((HOOKS / "hooks.json").read_text(encoding="utf-8"))["hooks"]


def commands(event: str) -> list[str]:
    return [h["command"] for group in declared()[event] for h in group["hooks"]]


def run(stdin: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT)], input=stdin,
                          capture_output=True, text=True)


def test_both_starts_are_declared_and_neither_is_narrowed():
    hooks = declared()
    assert sorted(hooks) == sorted(EVENTS), \
        f"hooks.json declares {sorted(hooks)}; the rules must reach the session and every agent"
    for event in EVENTS:
        for group in hooks[event]:
            assert "matcher" not in group, \
                f"{event} carries a matcher; the rules hold for every {event}, not a subset"


def test_both_starts_run_the_one_script_over_the_one_file():
    for event in EVENTS:
        assert len(commands(event)) == 1, f"{event} runs {len(commands(event))} commands; one places the rules"
        command = commands(event)[0]
        assert "${CLAUDE_PLUGIN_ROOT}/hooks/rules.py" in command, \
            f"{event} runs {command!r}; the plugin root is the only path a hook may rely on"
        resolved = Path(command.split('"')[1].replace("${CLAUDE_PLUGIN_ROOT}", str(SRC)))
        assert resolved == SCRIPT and resolved.is_file()
    assert commands(EVENTS[0]) == commands(EVENTS[1])
    assert os.access(SCRIPT, os.X_OK), f"{SCRIPT} is not executable"


@pytest.mark.parametrize("event", EVENTS)
def test_the_script_places_the_rules_verbatim_for_the_event_it_was_run_for(event):
    done = run(json.dumps({"hook_event_name": event, "session_id": "x"}))
    assert done.returncode == 0, done.stderr
    out = json.loads(done.stdout)["hookSpecificOutput"]
    assert out["hookEventName"] == event
    assert out["additionalContext"] == RULES.read_text(encoding="utf-8")


def test_an_unreadable_or_foreign_event_record_still_places_the_rules():
    for stdin in ("", "not json", json.dumps({"hook_event_name": "PreToolUse"})):
        done = run(stdin)
        assert done.returncode == 0, done.stderr
        out = json.loads(done.stdout)["hookSpecificOutput"]
        assert out["hookEventName"] == EVENTS[0]
        assert out["additionalContext"] == RULES.read_text(encoding="utf-8")


def test_the_script_never_fails_a_session_over_a_missing_file(tmp_path):
    """A hook that exits non-zero stops the session; a missing rules file is the distribution's
    defect, reported by the distribution suite, never by stopping every consumer."""
    copy = tmp_path / "rules.py"
    copy.write_bytes(SCRIPT.read_bytes())
    done = subprocess.run([sys.executable, str(copy)], input="{}", capture_output=True, text=True)
    assert done.returncode == 0 and done.stdout == ""
