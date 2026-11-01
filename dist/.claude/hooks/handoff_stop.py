"""Holds the message a session stops on to what `bin/handoff.py --check` decides, where no goal is armed.

`hooks/goal_stop.py` is the one `Stop` hook, and it hands a stop here only where the project
holds no armed goal: an armed goal answers its own stops, and one script answering each stop is
what keeps two answers from ever meeting on the same stop. «Where no goal is armed in a project
that declares `siegard.json`, the plugin's `Stop` hook reads the event's `last_assistant_message`
and, where `bin/handoff.py`'s own reading says it hands a decision, appends one line to
`siegard/handoff-checks.jsonl` under the repository's git directory — never in the tree the state
reads — holding `at`, `session_id`, `characters`, `hands_decision`, `mode`, `violations` as
`handoff.py --check` prints them, `kinds`, `blocked` and `released`.» (SPEC-008 R15)

The reading is `handoff.py`'s own `reading` and `violations`, the functions `--check` runs, so a
stop is held by the same definition a handoff is measured by and by nothing else. What leaves is
the message's length and the lines `--check` prints, never its words.

The mode is the environment variable `SIEGARD_HANDOFF_STOP`, which a project sets in the harness's
own settings, `env`:

- `measure`, the default and the reading of any value but `enforce` — the line is appended and
  the stop is always allowed.
- `enforce` — a stop whose message violates is blocked once, `{"decision": "block", "reason":
  ...}`, the violations as the reason; the next stop of the same session is allowed whatever it
  holds and recorded `released`, so a block never holds a session twice over one message.

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

BIN = Path(__file__).resolve().parent.parent / "bin"
CHECKS_FILE = "handoff-checks.jsonl"
MODE_VARIABLE = "SIEGARD_HANDOFF_STOP"
MEASURE, ENFORCE = "measure", "enforce"
KINDS = ("opening", "length", "decision")


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
    with contextlib.redirect_stderr(io.StringIO()):
        import handoff
    contract = handoff.load_contract()
    read = handoff.reading(message, contract)
    if not read["hands_decision"] and not released:
        return None
    problems = handoff.violations(read, contract) if read["hands_decision"] else []
    blocked = mode == ENFORCE and not released and bool(problems)
    append(path, {"at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                  "session_id": session, "characters": read["characters"],
                  "hands_decision": read["hands_decision"], "mode": mode,
                  "violations": problems, "kinds": sorted({kind_of(p) for p in problems}),
                  "blocked": blocked, "released": released})
    if not blocked:
        return None
    return {"decision": "block",
            "reason": "The message this session stopped on hands the person a decision and does "
                      "not hold what `bin/handoff.py --check` decides:\n"
                      + "\n".join(f"- {p}" for p in problems)
                      + "\nRender it with `bin/handoff.py --render` from a record, or rewrite it "
                        "to hold; the next stop of this session is allowed whatever it holds."}
