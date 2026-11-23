"""Holds a session's stop to what `bin/handoff.py --check` decides and to the render its turn
owes, where no armed goal answers the stop.

`hooks/goal_stop.py` is the one `Stop` hook, and it hands a stop here where no armed goal
answers it — none is armed, or the armed goal is bound to another session — and where the armed
goal has just ended on it, in state A, state B or paused: control returns to the person on that
stop, and its message is the report that closes the goal. A `not yet` is the armed goal's alone,
and one script answering each stop is what keeps two answers from ever meeting on the same stop.
«Where no armed goal answers the stop in a project that declares `siegard.json`, the plugin's
`Stop` hook reads the event's `last_assistant_message` and the session's turn record»
(SPEC-008 R15), and appends one line to `siegard/handoff-checks.jsonl` where the message hands a
decision or the turn ran a skill whose run ends on a render.

The turn record is `hooks/turn.py`'s: the instant of the last `Skill` call to a skill whose run
ends on `bin/handoff.py --render` — the line's `route` — and, read here, whether a record
`--render` keeps is newer than that instant — the line's `rendered`. The message's reading is
`handoff.py`'s own `reading` and `violations`, the functions `--check` runs; what leaves is the
message's length and the lines `--check` prints, never its words.

The mode is the environment variable `SIEGARD_HANDOFF_STOP`, which a project sets in the harness's
own settings, `env`:

- `measure`, the default and the reading of any value but `enforce` — the line is appended and
  the stop is always allowed.
- `enforce` — «a stop whose turn ran such a skill and printed no render is blocked once»
  (SPEC-008 R15), the reason asking for the render; the next stop of the same session is allowed
  whatever it holds and recorded `released`. «The violations of a message's form are recorded and
  never block.» (SPEC-008 R15)

A stop while the session still has background work in flight is not read: the session is waiting
to be woken, and control has not returned to a person. Every failure — no validator, no git, a
log that cannot be written — allows the stop and says nothing: a measurement that could hold a
session on its own failure would cost the session the work it measures.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

HOOKS = Path(__file__).resolve().parent
BIN = HOOKS.parent / "bin"
CHECKS_FILE = "handoff-checks.jsonl"
MODE_VARIABLE = "SIEGARD_HANDOFF_STOP"
MEASURE, ENFORCE = "measure", "enforce"
KINDS = ("opening", "length", "decision")
REASON = ("This turn ran a Siegard skill whose run ends on a handoff, and no handoff was rendered "
          "since. Render it with `bin/handoff.py --render` from a record: run `--prepare`, write "
          "the report with `--save-report`, then `--render`, and hand the person what `--render` "
          "prints. Do not rewrite it as free text. Recommend the door, never the answer. The next "
          "stop of this session is allowed whatever it holds.")


def checks_path(siegard_dir: Path) -> Path:
    """The measuring log, beside the armed goal's record in the repository's git directory."""
    return siegard_dir / CHECKS_FILE


def mode_of(environment: dict) -> str:
    return ENFORCE if (environment.get(MODE_VARIABLE) or "").strip().lower() == ENFORCE \
        else MEASURE


def kind_of(problem: str) -> str:
    head = problem.split(":", 1)[0]
    return head if head in KINDS else "other"


def last_of_session(path: Path, session: str) -> dict | None:
    """The newest line this session left in the log, or None."""
    last = None
    try:
        with path.open(encoding="utf-8") as log:
            for line in log:
                try:
                    entry = json.loads(line)
                except ValueError:
                    continue
                if isinstance(entry, dict) and entry.get("session_id") == session:
                    last = entry
    except OSError:
        return None
    return last


def append(path: Path, entry: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as log:
        log.write(json.dumps(entry) + "\n")


def answer(record: dict, siegard_dir: Path, environment: dict | None = None) -> dict | None:
    """What the stop is answered with — `{"decision": "block", ...}` or None, the stop allowed —
    after the line it owes is appended. Raises on nothing: every failure is None."""
    try:
        return _answer(record, siegard_dir, os.environ if environment is None else environment)
    except (Exception, SystemExit):
        return None


def _answer(record: dict, siegard_dir: Path, environment: dict) -> dict | None:
    waiting = record.get("background_tasks")
    if isinstance(waiting, list) and waiting:
        return None
    message = record.get("last_assistant_message")
    session = record.get("session_id")
    if not isinstance(message, str) or not isinstance(session, str) or not session:
        return None
    mode = mode_of(environment)
    path = checks_path(siegard_dir)
    released = mode == ENFORCE and bool((last_of_session(path, session) or {}).get("blocked"))
    sys.path.insert(0, str(BIN))
    sys.path.insert(0, str(HOOKS))
    with contextlib.redirect_stderr(io.StringIO()):
        import handoff
        import turn
    route_at = turn.read(siegard_dir, session)["route_at"]
    route = route_at is not None
    rendered = turn.rendered(siegard_dir, route_at)
    contract = handoff.load_contract()
    read = handoff.reading(message, contract)
    if not read["hands_decision"] and not route and not released:
        return None
    problems = handoff.violations(read, contract) if read["hands_decision"] else []
    blocked = mode == ENFORCE and not released and route and not rendered
    append(path, {"at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                  "session_id": session, "characters": read["characters"],
                  "hands_decision": read["hands_decision"], "route": route, "rendered": rendered,
                  "mode": mode, "violations": problems,
                  "kinds": sorted({kind_of(p) for p in problems}),
                  "blocked": blocked, "released": released})
    if not blocked:
        return None
    return {"decision": "block", "reason": REASON}
