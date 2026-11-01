#!/usr/bin/env python3
"""Answers a session's stop from the state of the goal the person armed, in a Siegard project.

The harness runs this on `Stop`, as `hooks/hooks.json` declares. Where the project holds a goal
armed by `bin/goal.py --arm`, the stop is answered by the same computation `goal.py --state`
runs, over the record's own pins — never by a model reading the transcript: «A goal the person
arms through the framework ends on the state script's answer at the session's stop, never on a
model's reading: `state A` or `state B` ends the goal and lets the session stop, `not yet` blocks
the stop with the checks that failed, and a fourth consecutive `not yet` whose whole answer
repeats the last ends the goal paused.» (SPEC-008 R14)

- `state A` or `state B` — the record is ended, the stop is allowed, and one line,
  `systemMessage`, tells the person the state and, under state B, the stop line it was read from.
- `not yet` — the stop is blocked, `{"decision": "block", "reason": ...}`: the state's first line,
  then every failing check with its output verbatim, then the condition the person armed,
  repeated as the harness repeats its own goal's.
- the same `not yet`, whole, after three consecutive blocks — the session answered each with
  nothing a check could see, so the stop is allowed, the record is ended `paused`, and the line
  says so.

Where the project holds no armed goal, the stop is handed to `hooks/handoff_stop.py`, which holds
the message the session stopped on to what `bin/handoff.py --check` decides. This is the one
`Stop` hook so that an armed goal and that check never both answer the same stop: the armed goal
answers its stops, and the check reads only the stops of a project where none is armed.

The goal binds to the first session whose stop reaches it; another session's stop is left alone.
A stop while the session still has background work in flight is left alone too, uncounted: the
session is waiting to be woken, and blocking it would ask for work it is already waiting on.

It never fails a session and never traps one. Every path out exits 0. Silent in a project that
declares no `siegard.json`; in one that holds no armed goal, silent but for the check above.
Where the state cannot be computed — a validator missing, a project file that no longer resolves
— the stop is allowed and the goal left armed, said in one line: a hook that blocked on its own failure would hold the session on a
reason the session cannot repair.
"""
from __future__ import annotations

import contextlib
import io
import json
import sys
from pathlib import Path

HOOKS = Path(__file__).resolve().parent
EVENT = "Stop"
GIT_TIMEOUT_SECONDS = 10


def said(line: str) -> int:
    print(json.dumps({"systemMessage": line}))
    return 0


def handed_on(record: dict, siegard_dir: Path) -> int:
    """The stop of a project with no armed goal, answered by the handoff check."""
    sys.path.insert(0, str(HOOKS))
    import handoff_stop
    answer = handoff_stop.answer(record, siegard_dir)
    if answer is not None:
        print(json.dumps(answer))
    return 0


def main() -> int:
    try:
        record = json.loads(sys.stdin.read() or "{}")
    except (ValueError, OSError):
        record = {}
    if not isinstance(record, dict):
        record = {}
    if record.get("hook_event_name") not in (EVENT, None):
        return 0
    where = record.get("cwd")
    try:
        start = Path(where) if isinstance(where, str) and where else Path.cwd()
        if not start.is_dir():
            return 0
        sys.path.insert(0, str(HOOKS.parent / "bin"))
        from project import PROJECT_FILE, toplevel_of
        home = toplevel_of(start, timeout=GIT_TIMEOUT_SECONDS)
        if not (home / PROJECT_FILE).is_file():
            return 0
        with contextlib.redirect_stderr(io.StringIO()):
            import goal
        path = goal.armed_path(home)
        if not path.exists():
            return handed_on(record, path.parent)
        armed = goal.read_armed(path)
    except (Exception, SystemExit):
        return 0
    if armed is None:
        return said(f"Siegard could not read the armed goal at {path}; the stop is allowed. "
                    f"`goal.py --disarm` ends it.")
    session = record.get("session_id")
    if isinstance(session, str) and session:
        bound = armed.get("session_id")
        if bound and bound != session:
            return 0
        if not bound:
            armed["session_id"] = session
    waiting = record.get("background_tasks")
    if isinstance(waiting, list) and waiting:
        try:
            goal.write_armed(path, armed)
        except OSError:
            pass
        return 0
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            answer, text = goal.answer_stop(armed, path)
    except (Exception, SystemExit) as broken:
        reason = str(broken).splitlines()[0] if str(broken) else type(broken).__name__
        return said(f"Siegard could not read the state of the armed goal "
                    f"{armed.get('slug', '')}: {reason}; the stop is allowed and the goal stays "
                    f"armed.")
    if answer == "block":
        print(json.dumps({"decision": "block", "reason": text}))
        return 0
    return said(text)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException:
        raise SystemExit(0)
