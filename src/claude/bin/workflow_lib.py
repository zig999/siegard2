"""Append-only workflow events, the state derived from them, and the guards between.

This module is the append-only persistence candidate under test for open question 1 in
the build plan. It holds three things and no rules of its own beyond them:

- TRANSITIONS, the lookup table that makes a transition a table read rather than an
  interpretation of prose. Its phase vocabulary is R2's default path,
  complete: R2 permits escalation to insert phases and forbids removing one.
- derive(), which reads a log back into workflow state. State is never stored; it is
  replayed, so it cannot drift from the record that produced it
  (the workflow state definition).
- guard(), which decides whether one candidate event may be appended. Every condition is
  decidable from the log and the candidate alone — no clock, no filesystem, no judgment
  (the transition guard definition).

Ordering comes from `seq`, never from file order or from `occurred_at`: a clock can repeat
or move backwards, and replay has to be deterministic. Callers supply
`event_id` and `occurred_at` for the same reason concept-author refuses to invent its own
timestamp — a framework that minted them would make a replay irreproducible.

Rejection is total: guard() returns reasons and append() refuses. Nothing here repairs a
malformed event.

Declared dependencies: jsonschema. Required; this module raises a named error rather than
degrading silently if it is missing.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = REPO_ROOT / "schemas"
EVENT_SCHEMA_PATH = SCHEMA_DIR / "workflow-event.json"

try:
    from jsonschema import Draft202012Validator
except ImportError as exc: # pragma: no cover - environment failure, not logic
    raise ImportError("cannot run: jsonschema is not installed (pip install jsonschema)") from exc

# The phase a workflow opens in. no phase runs without a change request.
OPENING_PHASE = "change-request"

# Terminal statuses. A workflow reaching one accepts no further event.
ACCEPTED = "accepted"
FAILED = "failed"
BLOCKED = "blocked"
OPEN = "open"
TERMINAL = (ACCEPTED, FAILED, BLOCKED)

# (phase, outcome) -> next phase, or a terminal status. The table is the whole of the
# control flow: a pair absent from it is not a transition, and the guard says so rather
# than guessing an intent. Each entry cites the requirement that puts it here.
TRANSITIONS: dict[tuple[str, str], str] = {
    ("change-request", "recorded"): "impact-analysis",
    # R3: impact analysis runs for every request, including a `none` verdict. A `none`
    # verdict has no knowledge to author, so the path runs to acceptance, which still
    # evaluates closure over the observed diff.
    ("impact-analysis", "none"): "acceptance",
    ("impact-analysis", "update"): "context-resolution",
    ("impact-analysis", "create"): "context-resolution",
    # R13: resolution never blocks. Degradation continues to the next phase and becomes an
    # input to acceptance (R14) rather than a stop.
    ("context-resolution", "resolved"): "specification-delta",
    ("context-resolution", "degraded"): "specification-delta",
    ("specification-delta", "recorded"): "implementation",
    ("implementation", "authored"): "validation",
    ("implementation", "updated"): "validation",
    ("validation", "passed"): "acceptance",
    # R7: a validation failure returns the workflow to implementation under a stated
    # attempt limit; exhausting the limit is terminal and is never an acceptance.
    ("validation", "failed"): "implementation",
    ("validation", "exhausted"): FAILED,
    ("acceptance", "accepted"): ACCEPTED,
}

# `blocked` is legal from any phase, so it is held apart from the table rather than
# repeated seven times.
BLOCKING_OUTCOME = "blocked"

_validator: Draft202012Validator | None = None


def event_validator() -> Draft202012Validator:
    global _validator
    if _validator is None:
        if not EVENT_SCHEMA_PATH.is_file():
            raise FileNotFoundError(f"cannot run: schema {EVENT_SCHEMA_PATH} does not exist")
        _validator = Draft202012Validator(json.loads(EVENT_SCHEMA_PATH.read_text()))
    return _validator


def schema_problems(event: dict) -> list[str]:
    """Every way this event fails its contract, as messages naming the field."""
    problems = []
    for err in sorted(event_validator().iter_errors(event), key=lambda e: list(e.path)):
        where = ".".join(str(p) for p in err.path) or "(root)"
        schema_path = list(err.absolute_schema_path)
        message = err.message
        if schema_path and schema_path[0] == "dependentSchemas":
            message = f"{message} (required by the presence of '{schema_path[1]}')"
            where = str(schema_path[1])
        problems.append(f"{where}: {message}")
    return problems


def read_log(path: Path) -> list[dict]:
    """Parse a JSONL event log. A malformed line is an error, never a skipped entry.

    Silently dropping an unreadable line would make the derived state a function of what
    happened to parse, which is the opposite of reconstructible from records alone.
    """
    if not path.is_file():
        return []
    events = []
    for number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{number}: not valid JSON: {exc}") from exc
        if not isinstance(entry, dict):
            raise ValueError(f"{path}:{number}: entry is {type(entry).__name__}, expected an object")
        events.append(entry)
    return events


def derive(events: list[dict], workflow_id: str) -> dict:
    """Replay one workflow's events into its current state.

    Ordering is by `seq`, so the caller's file order cannot change the result. The returned
    mapping is the whole of the state: nothing about a workflow is known that this does not
    say, and nothing here is stored anywhere.
    """
    own = sorted(
        (e for e in events if e.get("workflow_id") == workflow_id),
        key=lambda e: e["seq"],
    )
    state = {
        "workflow_id": workflow_id,
        "phase": OPENING_PHASE,
        "status": OPEN,
        "seq": 0,
        "attempt_limit": None,
        "attempts": 0,
        "degradations": [],
        "history": [],
    }
    for event in own:
        phase, outcome = event["phase"], event["outcome"]
        state["seq"] = event["seq"]
        state["history"].append({"seq": event["seq"], "phase": phase, "outcome": outcome})
        if event["seq"] == 1 and "attempt_limit" in event:
            state["attempt_limit"] = event["attempt_limit"]
        if phase == "implementation" and outcome in ("authored", "updated"):
            state["attempts"] += 1
        if outcome == "degraded":
            state["degradations"].append({"seq": event["seq"], "detail": event.get("degradation")})
        target = BLOCKED if outcome == BLOCKING_OUTCOME else TRANSITIONS.get((phase, outcome))
        if target in TERMINAL:
            state["status"] = target
            state["phase"] = phase
        elif target is not None:
            state["phase"] = target
    return state


def guard(state: dict, event: dict) -> list[str]:
    """Every reason this event may not be appended to a workflow in `state`.

    An empty list is the only permission. Each condition below is decidable from the
    derived state and the candidate event, which is what makes it a guard rather than a
    suggestion (the transition guard definition).
    """
    reasons = []
    phase, outcome = event.get("phase"), event.get("outcome")

    if state["status"] in TERMINAL:
        reasons.append(
            f"workflow {state['workflow_id']} is {state['status']}, a terminal status; "
            f"a terminal workflow accepts no further event"
        )
        return reasons

    expected_seq = state["seq"] + 1
    if event.get("seq") != expected_seq:
        reasons.append(
            f"seq is {event.get('seq')}, expected {expected_seq} — seq increases by exactly 1, "
            f"so a gap or a repeat is a lost or duplicated record rather than a new fact"
        )

    if phase != state["phase"]:
        reasons.append(
            f"event reports phase '{phase}' but the workflow is in '{state['phase']}' — "
            f"a phase is entered by a transition, never by an event asserting it"
        )
        return reasons

    if outcome != BLOCKING_OUTCOME and (phase, outcome) not in TRANSITIONS:
        legal = sorted(o for p, o in TRANSITIONS if p == phase) + [BLOCKING_OUTCOME]
        reasons.append(
            f"'{outcome}' is not an outcome of phase '{phase}' — legal outcomes are {legal}"
        )
        return reasons

    # R7's attempt limit, read from the workflow's own opening record.
    limit = state["attempt_limit"]
    if phase == "validation" and outcome == "failed" and limit is not None:
        if state["attempts"] >= limit:
            reasons.append(
                f"attempt {state['attempts']} of {limit} has been used, so a return to "
                f"implementation is not available; the legal outcome is 'exhausted' "
                f"(exhaustion terminal and never an acceptance)"
            )
    if phase == "validation" and outcome == "exhausted" and limit is not None:
        if state["attempts"] < limit:
            reasons.append(
                f"attempt {state['attempts']} of {limit} has been used, so the limit is not "
                f"exhausted; the legal outcome is 'failed', which returns to implementation"
            )

    # The evidence a validation event carries must agree with the outcome it asserts.
    # The schema can require evidence but cannot compare it to the verdict.
    if phase == "validation" and outcome in ("passed", "failed"):
        results = [item.get("result") for item in event.get("evidence") or []]
        if outcome == "passed" and "fail" in results:
            reasons.append("outcome is 'passed' but evidence records a failing check")
        if outcome == "failed" and "fail" not in results:
            reasons.append("outcome is 'failed' but no evidence item records a failing check")

    return reasons


def append(path: Path, event: dict, events: list[dict] | None = None) -> dict:
    """Validate an event at the boundary, guard it, then append it. Never repair it.

    Returns the state derived after the append. Raises ValueError naming every reason when
    the event fails its contract or its guard: rejected, never repaired.
    """
    problems = schema_problems(event)
    if problems:
        raise ValueError(
            "event fails contract workflow-event/1:\n" + "\n".join(f" {p}" for p in problems)
        )
    if events is None:
        events = read_log(path)
    state = derive(events, event["workflow_id"])
    reasons = guard(state, event)
    if reasons:
        raise ValueError(
            "event rejected by the transition guard:\n" + "\n".join(f" {r}" for r in reasons)
        )
    if any(e.get("event_id") == event["event_id"] for e in events):
        raise ValueError(f"event_id {event['event_id']} already exists in {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")
    return derive(events + [event], event["workflow_id"])
