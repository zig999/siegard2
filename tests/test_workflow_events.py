"""The event log, the state derived from it, and the guard between them.

Each guard condition is tested in both directions. A rejection test alone cannot tell a
working guard from one that rejects everything, which is the same standard
tests/support.py records for the knowledge validators.

The fixture under fixtures/knowledge-change-loop is the end-to-end case: a full pass of the
seven-phase default path with one validation failure and one recovery.
"""

from __future__ import annotations

import json
import random
import re
import tempfile
import unittest
from pathlib import Path

from orchestrate import CONSUMED, consume_result, validate_at_boundary
from workflow_lib import (
    OPENING_PHASE,
    TRANSITIONS,
    append,
    derive,
    guard,
    read_log,
    schema_problems,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE = REPO_ROOT / "fixtures" / "knowledge-change-loop"
LOG = FIXTURE / "event-log.jsonl"
WORKFLOW = "wf_dunning-term"

# The phases foundation/0001 R2 fixes, read from the contract that encodes them rather than
# restated here. Restating would put the same list in a third place — the specification, the
# schema, and this file — and a test that carries its own copy of a rule stops being able to
# disagree with the schema.
R2_PHASES = set(
    json.loads((REPO_ROOT / "src" / "claude" / "schemas" / "workflow-event.json").read_text())["properties"]["phase"][
        "enum"
    ]
)


def event(seq: int, phase: str, outcome: str, **extra) -> dict:
    base = {
        "contract_version": "workflow-event/1",
        "event_id": f"ev_{seq:012x}",
        "workflow_id": WORKFLOW,
        "seq": seq,
        "occurred_at": "2026-07-30T12:00:00Z",
        "producer": "test",
        "phase": phase,
        "outcome": outcome,
    }
    base.update(extra)
    return base


PASSING_EVIDENCE = [{"check": "validators", "result": "pass"}]
FAILING_EVIDENCE = [{"check": "validators", "result": "fail"}]


def opening(limit: int = 2) -> dict:
    return event(1, "change-request", "recorded", attempt_limit=limit)


def subject(path: str = "inputs/x.json", contract: str = "concept-authoring-result/1") -> dict:
    return {"path": path, "contract_version": contract}


class Derivation(unittest.TestCase):
    """Workflow state is replayed from the log and cannot drift from it."""

    def setUp(self) -> None:
        self.events = read_log(LOG)

    def test_committed_state_matches_a_fresh_derivation(self) -> None:
        recorded = json.loads((FIXTURE / "derived-state.json").read_text())
        self.assertEqual(derive(self.events, WORKFLOW), recorded)

    def test_file_order_does_not_change_the_result(self) -> None:
        """Ordering is by seq, so any read order yields the same state (foundation/0001 R8)."""
        expected = derive(self.events, WORKFLOW)
        shuffled = list(self.events)
        random.Random(20260730).shuffle(shuffled)
        self.assertEqual(derive(shuffled, WORKFLOW), expected)
        self.assertEqual(derive(list(reversed(self.events)), WORKFLOW), expected)

    def test_replay_is_repeatable(self) -> None:
        self.assertEqual(derive(self.events, WORKFLOW), derive(self.events, WORKFLOW))

    def test_incremental_derivation_equals_wholesale(self) -> None:
        """Deriving after each append agrees with deriving the finished log once."""
        for count in range(1, len(self.events) + 1):
            prefix = self.events[:count]
            self.assertEqual(derive(prefix, WORKFLOW)["seq"], count)
        self.assertEqual(derive(self.events, WORKFLOW)["status"], "accepted")

    def test_an_empty_log_opens_at_the_change_request(self) -> None:
        state = derive([], WORKFLOW)
        self.assertEqual(state["phase"], OPENING_PHASE)
        self.assertEqual(state["status"], "open")
        self.assertEqual(state["seq"], 0)

    def test_another_workflow_in_the_same_log_is_ignored(self) -> None:
        other = dict(self.events[0], workflow_id="wf_other", event_id="ev_ffffffffffff")
        self.assertEqual(derive(self.events + [other], WORKFLOW), derive(self.events, WORKFLOW))


class Guard(unittest.TestCase):
    """Every condition, in both directions."""

    def state_after(self, *events: dict) -> dict:
        return derive(list(events), WORKFLOW)

    def test_the_opening_event_is_accepted(self) -> None:
        self.assertEqual(guard(derive([], WORKFLOW), opening()), [])

    def test_an_event_for_another_phase_is_rejected(self) -> None:
        reasons = guard(derive([], WORKFLOW), event(1, "validation", "passed"))
        self.assertTrue(any("is in 'change-request'" in r for r in reasons), reasons)

    def test_a_seq_gap_is_rejected_and_the_right_seq_accepted(self) -> None:
        state = self.state_after(opening())
        self.assertTrue(any("expected 2" in r for r in guard(state, event(3, "impact-analysis", "create", subject=subject()))))
        self.assertEqual(guard(state, event(2, "impact-analysis", "create", subject=subject())), [])

    def test_a_repeated_seq_is_rejected(self) -> None:
        state = self.state_after(opening())
        self.assertTrue(guard(state, event(1, "impact-analysis", "create", subject=subject())))

    def test_an_outcome_outside_the_phase_is_rejected(self) -> None:
        state = self.state_after(opening())
        reasons = guard(state, event(2, "impact-analysis", "passed"))
        self.assertTrue(any("not an outcome of phase" in r for r in reasons), reasons)

    def test_blocked_is_accepted_from_any_phase(self) -> None:
        state = self.state_after(opening())
        self.assertEqual(
            guard(state, event(2, "impact-analysis", "blocked", blocking_reason="no graph")), []
        )

    def test_a_terminal_workflow_accepts_nothing_further(self) -> None:
        blocked = event(2, "impact-analysis", "blocked", blocking_reason="no graph")
        state = self.state_after(opening(), blocked)
        self.assertEqual(state["status"], "blocked")
        reasons = guard(state, event(3, "impact-analysis", "create", subject=subject()))
        self.assertTrue(any("terminal status" in r for r in reasons), reasons)

    # --- foundation/0001 R7, the attempt limit ------------------------------------------

    def reached_validation(self, limit: int, attempts: int) -> list[dict]:
        """A log standing in validation, having used `attempts` implementation attempts."""
        log = [
            opening(limit),
            event(2, "impact-analysis", "create", subject=subject()),
            event(3, "context-resolution", "resolved"),
            event(4, "specification-delta", "recorded"),
            event(5, "implementation", "authored", subject=subject()),
        ]
        seq = 6
        for _ in range(attempts - 1):
            log.append(event(seq, "validation", "failed", evidence=FAILING_EVIDENCE))
            log.append(event(seq + 1, "implementation", "updated", subject=subject()))
            seq += 2
        return log

    def test_failure_returns_to_implementation_while_attempts_remain(self) -> None:
        log = self.reached_validation(limit=2, attempts=1)
        state = derive(log, WORKFLOW)
        self.assertEqual(state["attempts"], 1)
        self.assertEqual(guard(state, event(6, "validation", "failed", evidence=FAILING_EVIDENCE)), [])

    def test_failure_is_rejected_once_the_limit_is_used(self) -> None:
        log = self.reached_validation(limit=2, attempts=2)
        state = derive(log, WORKFLOW)
        self.assertEqual(state["attempts"], 2)
        reasons = guard(state, event(8, "validation", "failed", evidence=FAILING_EVIDENCE))
        self.assertTrue(any("legal outcome is 'exhausted'" in r for r in reasons), reasons)

    def test_exhausted_is_rejected_while_attempts_remain(self) -> None:
        log = self.reached_validation(limit=2, attempts=1)
        reasons = guard(derive(log, WORKFLOW), event(6, "validation", "exhausted"))
        self.assertTrue(any("legal outcome is 'failed'" in r for r in reasons), reasons)

    def test_exhausted_is_accepted_and_terminal_once_the_limit_is_used(self) -> None:
        log = self.reached_validation(limit=2, attempts=2)
        exhausted = event(8, "validation", "exhausted")
        self.assertEqual(guard(derive(log, WORKFLOW), exhausted), [])
        self.assertEqual(derive(log + [exhausted], WORKFLOW)["status"], "failed")

    def test_exhaustion_is_never_an_acceptance(self) -> None:
        """foundation/0001 R7. The terminal status of an exhausted limit is failure."""
        self.assertEqual(TRANSITIONS[("validation", "exhausted")], "failed")

    # --- foundation/0001 R22, evidence that agrees with the verdict ---------------------

    def test_passed_with_a_failing_check_is_rejected(self) -> None:
        log = self.reached_validation(limit=2, attempts=1)
        reasons = guard(derive(log, WORKFLOW), event(6, "validation", "passed", evidence=FAILING_EVIDENCE))
        self.assertTrue(any("evidence records a failing check" in r for r in reasons), reasons)

    def test_failed_without_a_failing_check_is_rejected(self) -> None:
        log = self.reached_validation(limit=2, attempts=1)
        reasons = guard(derive(log, WORKFLOW), event(6, "validation", "failed", evidence=PASSING_EVIDENCE))
        self.assertTrue(any("no evidence item records a failing check" in r for r in reasons), reasons)

    def test_agreeing_evidence_is_accepted(self) -> None:
        log = self.reached_validation(limit=2, attempts=1)
        self.assertEqual(
            guard(derive(log, WORKFLOW), event(6, "validation", "passed", evidence=PASSING_EVIDENCE)), []
        )


class SpecificationAgreement(unittest.TestCase):
    """The schema's phase vocabulary against the specification that fixes it.

    foundation/0001 R2 is the authority and the schema is derived from it, so the two can drift.
    This asserts they have not, the same way tests/test_edge_table_agreement.py holds spec
    0003's edge table against the knowledge contract.
    """

    def test_the_phase_enum_is_r2s_default_path_in_order(self) -> None:
        spec = (REPO_ROOT / "foundation" / "0001-knowledge-object-driven-development.md").read_text()
        match = re.search(r"\*\*R2\*\* — The default path is exactly: (.+?), in that order", spec, re.S)
        self.assertIsNotNone(match, "R2 no longer states the default path in the expected form")
        prose = [part.strip().replace(" ", "-") for part in match.group(1).replace("\n", " ").split(",")]
        schema = json.loads((REPO_ROOT / "src" / "claude" / "schemas" / "workflow-event.json").read_text())
        self.assertEqual(
            prose,
            schema["properties"]["phase"]["enum"],
            "the phase enum and R2's default path disagree — R2 is the authority",
        )

    def test_no_phase_is_missing_from_the_transition_table(self) -> None:
        """A phase with no outcome would be a dead end the guard could never leave."""
        self.assertEqual({phase for phase, _ in TRANSITIONS}, R2_PHASES)


class Contract(unittest.TestCase):
    """The conditionals in schemas/workflow-event.json, in both directions."""

    def test_a_conforming_event_has_no_problems(self) -> None:
        self.assertEqual(schema_problems(opening()), [])

    def test_the_opening_event_must_state_the_attempt_limit(self) -> None:
        bare = event(1, "change-request", "recorded")
        self.assertTrue(any("attempt_limit" in p for p in schema_problems(bare)), schema_problems(bare))

    def test_acceptance_requires_a_deciding_authority(self) -> None:
        """foundation/0001 R21: no workflow accepts its own output."""
        without = event(9, "acceptance", "accepted")
        self.assertTrue(any("decided_by" in p for p in schema_problems(without)))
        self.assertEqual(schema_problems(event(9, "acceptance", "accepted", decided_by="maintainer")), [])

    def test_a_deciding_authority_outside_acceptance_is_rejected(self) -> None:
        bad = event(6, "validation", "passed", evidence=PASSING_EVIDENCE, decided_by="maintainer")
        self.assertTrue(schema_problems(bad))

    def test_validation_requires_evidence(self) -> None:
        """foundation/0001 R22."""
        self.assertTrue(any("evidence" in p for p in schema_problems(event(6, "validation", "passed"))))

    def test_exhaustion_needs_no_evidence(self) -> None:
        """It reports a control-flow fact about prior attempts, not a check that ran."""
        self.assertEqual(schema_problems(event(6, "validation", "exhausted")), [])

    def test_a_verdict_read_from_an_artifact_must_name_it(self) -> None:
        """foundation/0001 R5: the transition is a lookup on a validated artifact's field."""
        self.assertTrue(any("subject" in p for p in schema_problems(event(5, "implementation", "authored"))))
        self.assertEqual(schema_problems(event(5, "implementation", "authored", subject=subject())), [])

    def test_blocked_requires_a_reason(self) -> None:
        self.assertTrue(any("blocking_reason" in p for p in schema_problems(event(2, "impact-analysis", "blocked"))))

    def test_a_blocking_reason_on_a_successful_outcome_is_rejected(self) -> None:
        bad = event(3, "context-resolution", "resolved", blocking_reason="none")
        self.assertTrue(schema_problems(bad))

    def test_degradation_belongs_only_to_context_resolution(self) -> None:
        """foundation/0001 R13."""
        ok = event(3, "context-resolution", "degraded", degradation="budget exhausted")
        self.assertEqual(schema_problems(ok), [])
        self.assertTrue(schema_problems(event(4, "specification-delta", "recorded", degradation="x")))

    def test_degraded_must_say_what_degraded(self) -> None:
        self.assertTrue(schema_problems(event(3, "context-resolution", "degraded")))

    def test_an_unknown_field_is_rejected(self) -> None:
        self.assertTrue(schema_problems(dict(opening(), note="extra")))

    def test_a_wrong_contract_version_is_rejected(self) -> None:
        self.assertTrue(schema_problems(dict(opening(), contract_version="workflow-event/2")))


class Boundary(unittest.TestCase):
    """A producer's result is validated before consumption, and rejected rather than repaired."""

    def setUp(self) -> None:
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        self.tmp = Path(holder.name)
        self.log = self.tmp / "event-log.jsonl"
        append(self.log, opening())
        append(self.log, event(2, "impact-analysis", "create", subject=subject()))
        append(self.log, event(3, "context-resolution", "resolved"))
        append(self.log, event(4, "specification-delta", "recorded"))

    def write(self, name: str, data: dict) -> Path:
        path = self.tmp / name
        path.write_text(json.dumps(data))
        return path

    def valid_result(self, **extra) -> dict:
        base = {
            "contract_version": "concept-authoring-result/1",
            "producer": "concept-author",
            "state": "authored",
            "term": "dunning",
            "concept_id": "concept.dunning",
            "concept_path": "knowledge/concepts/dunning.md",
            "files_changed": ["knowledge/concepts/dunning.md"],
        }
        base.update(extra)
        return base

    def consume(self, path: Path) -> dict:
        return consume_result(self.log, WORKFLOW, path, "ev_00000000000f", "2026-07-30T12:20:00Z")

    def test_a_conforming_result_transitions_the_workflow(self) -> None:
        state = self.consume(self.write("r.json", self.valid_result()))
        self.assertEqual(state["phase"], "validation")
        self.assertEqual(state["attempts"], 1)

    def test_the_recorded_outcome_comes_from_the_closed_state_field(self) -> None:
        self.consume(self.write("r.json", self.valid_result(state="updated")))
        self.assertEqual(read_log(self.log)[-1]["outcome"], "updated")

    def test_a_blocked_result_blocks_the_workflow_with_its_reason(self) -> None:
        blocked = {
            "contract_version": "concept-authoring-result/1",
            "producer": "concept-author",
            "state": "blocked",
            "term": "dunning",
            "blocking_reason": "concept.collections already covers these semantics",
        }
        state = self.consume(self.write("b.json", blocked))
        self.assertEqual(state["status"], "blocked")
        self.assertIn("collections", read_log(self.log)[-1]["blocking_reason"])

    def test_a_result_missing_a_required_field_is_rejected(self) -> None:
        broken = self.valid_result()
        del broken["concept_id"]
        with self.assertRaises(ValueError) as caught:
            self.consume(self.write("r.json", broken))
        self.assertIn("rejected, not repaired", str(caught.exception))
        self.assertEqual(len(read_log(self.log)), 4, "a rejected result must append nothing")

    def test_a_contradictory_result_is_rejected(self) -> None:
        """A blocking reason on a successful state is a contradiction the contract catches."""
        with self.assertRaises(ValueError):
            self.consume(self.write("r.json", self.valid_result(blocking_reason="why")))

    def test_an_unknown_contract_is_refused(self) -> None:
        with self.assertRaises(ValueError) as caught:
            self.consume(self.write("r.json", self.valid_result(contract_version="review-verdict/1")))
        self.assertIn("not built to read it", str(caught.exception))

    def test_a_result_with_no_contract_version_is_refused(self) -> None:
        with self.assertRaises(ValueError) as caught:
            self.consume(self.write("r.json", {"state": "authored"}))
        self.assertIn("no contract_version", str(caught.exception))

    def test_a_result_claiming_another_producer_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            self.consume(self.write("r.json", self.valid_result(producer="impostor")))

    def test_malformed_json_is_refused(self) -> None:
        path = self.tmp / "r.json"
        path.write_text("{not json")
        with self.assertRaises(ValueError) as caught:
            self.consume(path)
        self.assertIn("not valid JSON", str(caught.exception))

    def test_the_impact_analysis_contract_drives_its_own_phase(self) -> None:
        """The second producer row exercises the extension point, on a different field."""
        self.assertEqual(CONSUMED["impact-analysis/1"]["field"], "verdict")
        analysis = validate_at_boundary(FIXTURE / "inputs" / "impact-analysis.json")
        self.assertEqual(analysis["verdict"], "create")

    def test_a_create_verdict_naming_nothing_is_rejected(self) -> None:
        empty = {
            "contract_version": "impact-analysis/1",
            "analysis_id": "ia_1a2b3c4d",
            "request_id": "cr_0f1e2d3c",
            "producer": "impact-analysis",
            "verdict": "create",
            "implicated": [],
        }
        with self.assertRaises(ValueError):
            validate_at_boundary(self.write("ia.json", empty))

    def test_a_none_verdict_may_name_nothing(self) -> None:
        empty = {
            "contract_version": "impact-analysis/1",
            "analysis_id": "ia_1a2b3c4d",
            "request_id": "cr_0f1e2d3c",
            "producer": "impact-analysis",
            "verdict": "none",
            "implicated": [],
        }
        self.assertEqual(validate_at_boundary(self.write("ia.json", empty))["verdict"], "none")


class Appending(unittest.TestCase):
    """append() refuses rather than repairs, and never half-writes."""

    def setUp(self) -> None:
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        self.log = Path(holder.name) / "event-log.jsonl"

    def test_a_rejected_event_is_not_written(self) -> None:
        append(self.log, opening())
        with self.assertRaises(ValueError):
            append(self.log, event(5, "validation", "passed", evidence=PASSING_EVIDENCE))
        self.assertEqual(len(read_log(self.log)), 1)

    def test_a_malformed_event_names_its_contract(self) -> None:
        with self.assertRaises(ValueError) as caught:
            append(self.log, event(1, "change-request", "recorded"))
        self.assertIn("workflow-event/1", str(caught.exception))

    def test_a_duplicate_event_id_is_rejected(self) -> None:
        append(self.log, opening())
        duplicate = event(2, "impact-analysis", "create", subject=subject())
        duplicate["event_id"] = opening()["event_id"]
        with self.assertRaises(ValueError) as caught:
            append(self.log, duplicate)
        self.assertIn("already exists", str(caught.exception))

    def test_an_unreadable_line_is_an_error_not_a_skip(self) -> None:
        append(self.log, opening())
        with self.log.open("a") as handle:
            handle.write("{truncated\n")
        with self.assertRaises(ValueError):
            read_log(self.log)


class Fixture(unittest.TestCase):
    """The end-to-end case: what the committed history proves."""

    def setUp(self) -> None:
        self.events = read_log(LOG)
        self.state = derive(self.events, WORKFLOW)

    def test_the_workflow_reached_acceptance(self) -> None:
        self.assertEqual(self.state["status"], "accepted")

    def test_every_phase_of_the_default_path_is_recorded(self) -> None:
        """foundation/0001 R2: escalation inserts phases and never removes one."""
        self.assertEqual({e["phase"] for e in self.events}, R2_PHASES)

    def test_the_recorded_path_follows_the_transition_table(self) -> None:
        """Every consecutive pair is the table's own edge — the log encodes no other route."""
        phase = OPENING_PHASE
        for entry in sorted(self.events, key=lambda e: e["seq"]):
            self.assertEqual(entry["phase"], phase, f"seq {entry['seq']} entered the wrong phase")
            target = TRANSITIONS[(entry["phase"], entry["outcome"])]
            phase = target if target not in ("accepted", "failed", "blocked") else phase

    def test_it_exercises_a_validation_failure_and_a_recovery(self) -> None:
        outcomes = [(e["phase"], e["outcome"]) for e in sorted(self.events, key=lambda e: e["seq"])]
        self.assertIn(("validation", "failed"), outcomes)
        self.assertIn(("implementation", "updated"), outcomes)
        self.assertEqual(self.state["attempts"], 2)

    def test_acceptance_names_who_decided_it(self) -> None:
        accepted = [e for e in self.events if e["phase"] == "acceptance"][0]
        self.assertTrue(accepted["decided_by"], "foundation/0001 R21 requires a deciding authority")

    def test_every_consumable_contract_is_exercised_by_some_fixture(self) -> None:
        """Derived rather than counted: a new row in CONSUMED needs a fixture, not an edit here.

        This assertion read `== set(CONSUMED)` over one fixture until `knowledge-authoring-result/1`
        arrived. That was correct when one fixture consumed everything and became wrong the moment a
        second one carried part of the load — the property worth holding is that no consumable
        contract goes unexercised, across the whole fixture set.
        """
        exercised: set[str] = set()
        for log in sorted((REPO_ROOT / "fixtures").glob("*/event-log.jsonl")):
            for line in log.read_text().splitlines():
                if line.strip():
                    event = json.loads(line)
                    if "subject" in event:
                        exercised.add(event["subject"]["contract_version"])
        self.assertEqual(set(CONSUMED), exercised)

    def test_every_recorded_event_still_passes_its_contract(self) -> None:
        for entry in self.events:
            self.assertEqual(schema_problems(entry), [], f"seq {entry['seq']} no longer conforms")


if __name__ == "__main__":
    unittest.main()
