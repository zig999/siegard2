#!/usr/bin/env python3
"""Keeps what an armed grant answered at a stop as the session's obligation until it is carried
out, in a Siegard project.

The harness runs this on `PostToolUse` over `Bash`, `Skill` and `Agent`, as `hooks/hooks.json`
declares. Where the project declares `siegard.json` and holds a grant armed by `bin/grant.py
--arm` under this plugin's version, `bin/grant.py`'s `after_tool` reads the call: a command that
printed a grant's answer — `bin/handoff.py --render` or `bin/grant.py --decide` — records each
`take:` and `judge:` decision as an obligation of the session, under the repository's git
directory; a `Skill` invocation of the door a `take:` named, or an `Agent` spawn of
`siegard:door-decider` over a `judge:`, carries it out. The stop is answered from those
obligations by `hooks/goal_stop.py`, the one `Stop` hook: «A stop of a session whose obligation
is not carried out is blocked once by the plugin's `Stop` hook, its reason the grant's line and
what carries it out, and the session's next stop is allowed whatever it holds.» (SPEC-011 R12)

It reads only what the harness hands a hook — the call's input and its response — and never the
session's transcript. It never fails a session and prints nothing: every path out exits 0, and
every failure leaves the obligations as they were.
"""
from __future__ import annotations

import contextlib
import io
import json
import sys
from pathlib import Path

HOOKS = Path(__file__).resolve().parent
EVENT = "PostToolUse"
TOOLS = ("Bash", "Skill", "Agent", "Task")
GIT_TIMEOUT_SECONDS = 10


def output_of(response) -> str:
    """The text a call answered with: a command's standard output and error, whatever shape the
    harness hands them in."""
    if isinstance(response, dict):
        parts = [response.get(key) for key in ("stdout", "stderr", "output", "content")]
        text = "\n".join(p for p in parts if isinstance(p, str))
        return text or json.dumps(response)
    if isinstance(response, list):
        return "\n".join(item.get("text", "") if isinstance(item, dict) else str(item)
                         for item in response)
    return response if isinstance(response, str) else ""


def main() -> int:
    try:
        record = json.loads(sys.stdin.read() or "{}")
    except (ValueError, OSError):
        return 0
    if not isinstance(record, dict) or record.get("hook_event_name") not in (EVENT, None):
        return 0
    tool, session = record.get("tool_name"), record.get("session_id")
    if tool not in TOOLS or not isinstance(session, str) or not session:
        return 0
    given = record.get("tool_input")
    if not isinstance(given, dict):
        return 0
    if tool == "Bash" and "grant.py" not in str(given.get("command")) \
            and "handoff.py" not in str(given.get("command")):
        return 0
    try:
        where = record.get("cwd")
        start = Path(where) if isinstance(where, str) and where else Path.cwd()
        sys.path.insert(0, str(HOOKS.parent / "bin"))
        from project import PROJECT_FILE, toplevel_of
        home = toplevel_of(start, timeout=GIT_TIMEOUT_SECONDS)
        if not (home / PROJECT_FILE).is_file():
            return 0
        with contextlib.redirect_stderr(io.StringIO()):
            import goal
            import grant
        siegard_dir = goal.armed_path(home).parent
        if grant.live_grant(siegard_dir) is None:
            return 0
        grant.after_tool(siegard_dir, session, tool, given, output_of(record.get("tool_response")))
    except (Exception, SystemExit):
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
