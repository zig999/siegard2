#!/usr/bin/env python3
"""Places the framework's session rules into the context that is starting, in a Siegard project.

The harness runs this on `SessionStart` and on `SubagentStart`, as `hooks/hooks.json` declares.
Each start reaches a different context: a session's start reaches the session and never the
agents it later spawns, and an agent's start reaches that agent alone. Both run the same script
over the same file, `hooks/rules.md` beside it, so the session and every agent hold one text.

The rules govern a project that declares `siegard.json`, and nothing else. A plugin enabled for
every project a person opens would otherwise hand those rules — no comments in source, no domain
fact outside the specification, commits bounded to one skill's roots — to repositories that never
adopted the framework, and to every agent spawned there. So the context's working directory,
read from the event record, is resolved to the place the project file sits through
`bin/project.py`'s `toplevel_of`, the one answer to that question; where no `siegard.json` sits
there, this prints nothing. Every agent of a Siegard project still receives the rules, whatever
its type: the project is the scope, never the agent.

Reads the harness's event record on stdin for the event name and the working directory, and prints
one JSON object whose `additionalContext` is the rules file verbatim. It never fails a session:
every path out exits 0. Where the rules file is missing it prints nothing — the rules' absence is
the distribution suite's to report. Where the project cannot be resolved at all — git not
answering in time, a working directory that is gone — it places the rules: placing them where
they were not needed costs context, while withholding them from a project that declares
`siegard.json` loses every rule silently.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HOOKS = Path(__file__).resolve().parent
RULES = HOOKS / "rules.md"
EVENTS = ("SessionStart", "SubagentStart")
GIT_TIMEOUT_SECONDS = 10


def is_a_siegard_project(record: dict) -> bool:
    """Whether the context starts inside a project that declares `siegard.json`."""
    where = record.get("cwd")
    try:
        start = Path(where) if isinstance(where, str) and where else Path.cwd()
        sys.path.insert(0, str(HOOKS.parent / "bin"))
        from project import PROJECT_FILE, toplevel_of
        if not start.is_dir():
            return True
        return (toplevel_of(start, timeout=GIT_TIMEOUT_SECONDS) / PROJECT_FILE).is_file()
    except (Exception, SystemExit):
        return True


def main() -> int:
    try:
        record = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        record = {}
    if not isinstance(record, dict):
        record = {}
    event = record.get("hook_event_name")
    if event not in EVENTS:
        event = EVENTS[0]
    if not is_a_siegard_project(record):
        return 0
    try:
        rules = RULES.read_text(encoding="utf-8")
    except OSError:
        return 0
    print(json.dumps({"hookSpecificOutput": {"hookEventName": event,
                                             "additionalContext": rules}}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
