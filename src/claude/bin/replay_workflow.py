#!/usr/bin/env python3
"""Replay a workflow fixture's declared steps, and write or check what they produce.

A workflow fixture is any directory under the named root holding inputs/run.json. Replaying it
drives the real orchestrator over the real guard: every event is validated against
workflow-event/1 and accepted by the transition guard, or the replay fails. So a fixture
that replays is evidence that its recorded history is a legal one, not merely well-formed
JSON.

Two derived artifacts per fixture, neither ever hand-edited:

- event-log.jsonl — the append-only log the steps produce;
- derived-state.json — the workflow state replayed from that log.

--check compares both against a fresh replay in a temporary directory and mutates nothing,
which is what lets `make validate` run it on a dirty tree. Regeneration is this script with
no flag. A check that rewrote what it was meant to detect would report success on a defect.

Committing the derived state is deliberate: a change in control flow then shows up as a diff
in a reviewable file rather than only inside a test's expectations.

There is no Makefile target for regeneration. CLAUDE.md **Commands** fixes the canonical
entry points and only the maintainer changes that file, so `--check` is wired into
`make validate` and regeneration is this script run directly.

Declared dependencies: jsonschema, via bin/workflow_lib.py.

Usage: bin/replay_workflow.py [fixtures_root] [--check]
Exit: 0 written, or check passed; 1 check failed or a replay was rejected; 2 cannot run
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

from orchestrate import consume_result
from cli import cannot_run
from workflow_lib import REPO_ROOT, append, derive, read_log

LOG_NAME = "event-log.jsonl"
STATE_NAME = "derived-state.json"


def find_fixtures(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    return sorted(p.parent.parent for p in root.glob("*/inputs/run.json"))


def replay(fixture: Path, log_path: Path) -> dict:
    """Run every declared step into `log_path`, returning the derived state.

    Raises ValueError, from the guard or a boundary check, on the first step the framework
    refuses. Nothing here catches that: a fixture whose history the framework rejects is a
    failure to report, not a state to record.
    """
    run = json.loads((fixture / "inputs" / "run.json").read_text())
    workflow_id = run["workflow_id"]
    state = derive([], workflow_id)
    for index, step in enumerate(run["steps"], start=1):
        kind = step["kind"]
        try:
            if kind == "record":
                event = json.loads((fixture / "inputs" / step["event"]).read_text())
                state = append(log_path, event)
            elif kind == "consume":
                relative = f"inputs/{step['result']}"
                state = consume_result(
                    log_path,
                    workflow_id,
                    fixture / "inputs" / step["result"],
                    step["event_id"],
                    step["at"],
                    subject_path=relative,
                )
            else:
                raise ValueError(f"step kind '{kind}' is neither 'record' nor 'consume'")
        except ValueError as exc:
            raise ValueError(f"{fixture.name}: step {index} ({kind}) rejected: {exc}") from exc
    return state


def render_state(state: dict) -> str:
    return json.dumps(state, indent=2, sort_keys=True) + "\n"


def process(fixture: Path, check: bool, problems: list[str]) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        fresh_log = Path(tmp) / LOG_NAME
        state = replay(fixture, fresh_log)
        produced_log = fresh_log.read_text()
        produced_state = render_state(state)

    log_path = fixture / LOG_NAME
    state_path = fixture / STATE_NAME

    if not check:
        log_path.write_text(produced_log)
        state_path.write_text(produced_state)
        print(f"{fixture.name}: replayed {len(read_log(log_path))} event(s) -> {LOG_NAME}, {STATE_NAME}")
        return

    for path, produced in ((log_path, produced_log), (state_path, produced_state)):
        name = path.name
        if not path.is_file():
            problems.append(f"{fixture.name}/{name} does not exist; run bin/replay_workflow.py")
        elif path.read_text() != produced:
            problems.append(
                f"{fixture.name}/{name} does not match a fresh replay — it was hand-edited, or the "
                f"inputs changed without regenerating; run bin/replay_workflow.py"
            )
    print(f"{fixture.name}: checked {LOG_NAME}, {STATE_NAME} against a fresh replay")


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--check"]
    check = "--check" in sys.argv[1:]
    if not args:
        cannot_run("cannot run: name the root holding the workflow runs; there is no default")
    root = Path(args[0])

    if not root.is_dir():
        cannot_run(f"cannot run: fixture root {root} does not exist")

    fixtures = find_fixtures(root)
    if not fixtures:
        # A green run that replayed nothing is worse than a named gap — the Makefile states
        # that rule for its own targets, and this is the script it most easily hides behind:
        # a verification run would report success over a tree somebody renamed.
        cannot_run(f"cannot run: no inputs/run.json under {root}, so nothing was replayed")

    problems: list[str] = []
    for fixture in fixtures:
        try:
            process(fixture, check, problems)
        except (ValueError, KeyError, FileNotFoundError) as exc:
            problems.append(f"{fixture.name}: {exc}")

    print(f"workflow fixtures: {len(fixtures)} contract: schemas/workflow-event.json")
    if problems:
        print(f"FAILED: {len(problems)} problem(s)\n")
        for problem in problems:
            print(f" {problem}")
        return 1
    print("all workflow fixtures replay to their recorded log and state")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
