#!/usr/bin/env python3
"""The thin-path orchestrator: validate an agent's result, then look up the transition.

This is the consumer that schemas/concept-authoring-result.v1.json names, and the reason
that contract's boundary check stopped being a declared gap. It does three things and
deliberately nothing else:

1. validates a producer's result against the contract the artifact itself declares, at the
   boundary, before anything reads it (.claude/rules/contracts.md, specs/0001 R6);
2. reads the transition from CONSUMED — a table keyed by contract version and the closed
   `state` field. It never reads prose, and there is no branch here that inspects the
   artifact's narrative content (specs/0001 R5);
3. appends one event and reports the state derived from the log.

It holds no orchestration prose and no model judgment. That is the point:
.claude/rules/claude-code-authoring.md requires durable orchestration and state logic in
tested scripts, and docs/bootstrap.md stage 2 sets the abandonment criterion — if this had
to interpret prose to choose a transition, the artifact design would be wrong.

Acceptance is not available here. specs/0001 R21 forbids a workflow accepting its own
output, so an acceptance event carries `decided_by` and arrives through `record` from a
maintainer's decision, never from this script's own reasoning.

Declared dependencies: jsonschema, via scripts/workflow_lib.py.

Usage:
  orchestrate.py consume --log P --workflow ID --result P --event-id ID --at TS
  orchestrate.py record  --log P --event P
  orchestrate.py state   --log P --workflow ID
Exit: 0 appended or reported, 1 rejected at the boundary or by the guard, 2 cannot run
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from workflow_lib import SCHEMA_DIR, append, derive, read_log

try:
    from jsonschema import Draft202012Validator
except ImportError:
    sys.exit("cannot run: jsonschema is not installed (pip install jsonschema)")

# Which phase a producer's result drives, and how its closed `state` maps to an event
# outcome. A contract absent from this table is refused rather than guessed: an orchestrator
# that accepted an unknown artifact would be choosing a transition by inference.
#
# Adding a producer is adding a row. That is the extension point, and it is data.
CONSUMED: dict[str, dict] = {
    "concept-authoring-result/1": {
        "phase": "implementation",
        "field": "state",
        "producer": "concept-author",
        # In a knowledge-only change the authored knowledge *is* the implementation, so a
        # concept-authoring result drives the implementation phase of specs/0001 R2.
        "outcomes": {"authored": "authored", "updated": "updated", "blocked": "blocked"},
    },
    "impact-analysis/1": {
        "phase": "impact-analysis",
        "field": "verdict",
        # No `producer` key: specs/0001 R4 requires the artifact, not a particular producer
        # of it, so this contract is not owned by one named agent the way the other is.
        "outcomes": {"none": "none", "update": "update", "create": "create"},
    },
}


def schema_for(contract_version: str) -> Path:
    """Path of the contract a declared version names, by rule rather than by registry.

    `concept-authoring-result/1` -> schemas/concept-authoring-result.v1.json. Deriving the
    path means a new contract needs no mapping to keep in step; a registry would be a second
    place for the same fact to live.
    """
    if contract_version.count("/") != 1:
        raise ValueError(f"contract_version '{contract_version}' is not '<name>/<version>'")
    name, version = contract_version.split("/")
    if not name or not version.isdigit():
        raise ValueError(f"contract_version '{contract_version}' is not '<name>/<version>'")
    return SCHEMA_DIR / f"{name}.v{version}.json"


def validate_at_boundary(path: Path) -> dict:
    """Load a result and validate it against its own declared contract, or raise.

    The artifact declares its version and the consumer rejects what it was not built to
    read; nothing infers a version from shape.
    """
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{path}: result is {type(data).__name__}, expected an object")
    declared = data.get("contract_version")
    if not isinstance(declared, str):
        raise ValueError(f"{path}: no contract_version — a consumer cannot validate what does not say what it is")
    if declared not in CONSUMED:
        raise ValueError(
            f"{path}: contract '{declared}' has no entry in CONSUMED, so this orchestrator "
            f"was not built to read it; known: {sorted(CONSUMED)}"
        )
    schema_path = schema_for(declared)
    if not schema_path.is_file():
        raise ValueError(f"{path}: contract '{declared}' names {schema_path}, which does not exist")
    validator = Draft202012Validator(json.loads(schema_path.read_text()))
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    if errors:
        lines = []
        for err in errors:
            where = ".".join(str(p) for p in err.path) or "(root)"
            lines.append(f"  {where}: {err.message}")
        raise ValueError(
            f"{path}: fails contract {declared} at the boundary — rejected, not repaired:\n"
            + "\n".join(lines)
        )
    return data


def consume_result(
    log_path: Path,
    workflow_id: str,
    result_path: Path,
    event_id: str,
    at: str,
    subject_path: str | None = None,
) -> dict:
    """Validate a result at the boundary, look up its transition, append one event.

    `subject_path` is what gets recorded, defaulting to `result_path` as given. It is a
    separate argument because the recorded path must be stable: deriving it from however the
    caller happened to spell the path — absolute here, relative there — would make two runs
    of the same workflow produce different logs.
    """
    data = validate_at_boundary(result_path)
    entry = CONSUMED[data["contract_version"]]

    expected_producer = entry.get("producer")
    if expected_producer is not None and data.get("producer") != expected_producer:
        raise ValueError(
            f"{result_path}: producer '{data.get('producer')}' is not the '{expected_producer}' "
            f"this contract belongs to"
        )

    field = entry["field"]
    verdict = data[field]
    outcome = entry["outcomes"].get(verdict)
    if outcome is None:
        raise ValueError(
            f"{result_path}: {field} '{verdict}' has no transition under contract "
            f"{data['contract_version']}; known: {sorted(entry['outcomes'])}"
        )

    events = read_log(log_path)
    event = {
        "contract_version": "workflow-event/1",
        "event_id": event_id,
        "workflow_id": workflow_id,
        "seq": derive(events, workflow_id)["seq"] + 1,
        "occurred_at": at,
        "producer": "orchestrate",
        "phase": entry["phase"],
        "outcome": outcome,
    }
    if outcome == "blocked":
        event["blocking_reason"] = data.get("blocking_reason", "producer reported blocked with no reason")
    else:
        event["subject"] = {
            "path": subject_path if subject_path is not None else str(result_path),
            "contract_version": data["contract_version"],
        }
    return append(log_path, event, events)


def consume(args: argparse.Namespace) -> int:
    state = consume_result(
        Path(args.log),
        args.workflow,
        Path(args.result),
        args.event_id,
        args.at,
        args.subject_path,
    )
    print(json.dumps(state, indent=2, sort_keys=True))
    return 0


def record(args: argparse.Namespace) -> int:
    """Append a caller-authored event: a phase with no agent producer, or a decision.

    The guard applies identically. This is how a maintainer's acceptance enters the log
    (specs/0001 R21) and how the phases that no agent yet produces are recorded.
    """
    event = json.loads(Path(args.event).read_text())
    state = append(Path(args.log), event)
    print(json.dumps(state, indent=2, sort_keys=True))
    return 0


def report(args: argparse.Namespace) -> int:
    state = derive(read_log(Path(args.log)), args.workflow)
    print(json.dumps(state, indent=2, sort_keys=True))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    c = sub.add_parser("consume", help="validate a producer's result and append its transition")
    c.add_argument("--log", required=True)
    c.add_argument("--workflow", required=True)
    c.add_argument("--result", required=True)
    c.add_argument("--event-id", required=True, help="caller-supplied; the framework never mints one")
    c.add_argument("--at", required=True, help="caller-supplied UTC instant, YYYY-MM-DDTHH:MM:SSZ")
    c.add_argument(
        "--subject-path",
        default=None,
        help="path to record for the consumed artifact; defaults to --result as given. "
        "State it when the log must be reproducible from a stable path.",
    )
    c.set_defaults(func=consume)

    r = sub.add_parser("record", help="append a caller-authored event, guard applied")
    r.add_argument("--log", required=True)
    r.add_argument("--event", required=True, help="path to a JSON file holding one event")
    r.set_defaults(func=record)

    s = sub.add_parser("state", help="derive and print workflow state from the log")
    s.add_argument("--log", required=True)
    s.add_argument("--workflow", required=True)
    s.set_defaults(func=report)

    args = parser.parse_args()
    try:
        return args.func(args)
    except (ValueError, FileNotFoundError) as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
