#!/usr/bin/env python3
"""Places the framework's session rules into the context that is starting.

The harness runs this on `SessionStart` and on `SubagentStart`, as `hooks/hooks.json` declares.
Each start reaches a different context: a session's start reaches the session and never the
agents it later spawns, and an agent's start reaches that agent alone. Both run the same script
over the same file, `hooks/rules.md` beside it, so the session and every agent hold one text.

Reads the harness's event record on stdin for the event name and prints one JSON object whose
`additionalContext` is the rules file verbatim. Where the file is missing, prints nothing and
exits 0: a hook that fails would stop every session of every project holding the plugin, and the
rules' absence is the skills' to notice, not this script's to enforce.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RULES = Path(__file__).resolve().parent / "rules.md"
EVENTS = ("SessionStart", "SubagentStart")


def main() -> int:
    try:
        event = json.loads(sys.stdin.read() or "{}").get("hook_event_name")
    except json.JSONDecodeError:
        event = None
    if event not in EVENTS:
        event = EVENTS[0]
    try:
        rules = RULES.read_text(encoding="utf-8")
    except OSError:
        return 0
    print(json.dumps({"hookSpecificOutput": {"hookEventName": event,
                                             "additionalContext": rules}}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
