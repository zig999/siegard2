"""Context resolution: determinism, stopping, degradation, and whether it earns its place.

`specs/0009` leaves the expansion order free and pins it to a contract version (R17). That is
the whole of what makes R13's `claim-recorded` persistence real: `specs/0004` R48 requires a
discarded body to recompute to the recorded content hash, and a package truncated by a budget
recomputes to a different set the moment the traversal reorders.

The measurement class is the one that could end this machinery. `specs/0009` R11 retains
resolution only while it selects better than including the whole bundle, and R10 asks for the
record rather than the figure — so these assert that the record exists and that the numbers in
the specifications record are the ones the code actually produces.
"""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

import resolve_context as rc
from knowledge_graph_lib import load

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE = REPO_ROOT / "fixtures" / "knowledge-two-context" / "knowledge"
SCHEMA = REPO_ROOT / "src" / "claude" / "schemas" / "context-package.json"

RULE = "ko.rule.sales.proposal-validity"
CLAIM = "the change alters when a proposal may still be accepted"


def build(root: Path = FIXTURE, roots=None, budget=10_000, unit="objects", depth=None) -> dict:
    graph = load(root)
    return rc.package(
        graph, "cp_00000001", "cr_00000001", roots or [(RULE, CLAIM)], budget, unit, depth
    )


class Conformance(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = Draft202012Validator(json.loads(SCHEMA.read_text()))

    def test_a_produced_package_conforms(self) -> None:
        self.assertEqual([], list(self.validator.iter_errors(build())))

    def test_a_truncated_package_conforms(self) -> None:
        self.assertEqual([], list(self.validator.iter_errors(build(budget=3))))

    def test_a_truncated_package_must_carry_a_degradation(self) -> None:
        """specs/0009 R16: a package saying the closure was cut short and nothing was lost."""
        document = build(budget=3)
        document["degradations"] = []
        self.assertTrue(list(self.validator.iter_errors(document)))

    def test_a_root_without_a_claim_is_rejected(self) -> None:
        """specs/0009 R4."""
        document = build()
        document["roots"] = [{"id": RULE}]
        self.assertTrue(list(self.validator.iter_errors(document)))


class Determinism(unittest.TestCase):
    """specs/0001 R12, made checkable by specs/0009 R17."""

    def test_the_same_inputs_produce_a_byte_identical_package(self) -> None:
        first = json.dumps(build(), indent=2, sort_keys=True)
        second = json.dumps(build(), indent=2, sort_keys=True)
        self.assertEqual(first, second)

    def test_it_holds_under_truncation(self) -> None:
        """The case R17 exists for: a truncated closure reorders and recomputes differently."""
        self.assertEqual(
            json.dumps(build(budget=5), indent=2, sort_keys=True),
            json.dumps(build(budget=5), indent=2, sort_keys=True),
        )

    def test_root_order_is_the_caller_s_and_is_preserved(self) -> None:
        """Reordering roots would silently rank one justification above another."""
        pair = [(RULE, CLAIM), ("ko.rule.billing.invoice-amount", "billing is implicated too")]
        self.assertEqual([r["id"] for r in build(roots=pair)["roots"]], [p[0] for p in pair])

    def test_a_change_to_a_member_changes_the_package(self) -> None:
        with tempfile.TemporaryDirectory() as holder:
            copy = Path(holder) / "knowledge"
            shutil.copytree(FIXTURE, copy)
            before = build(root=copy)
            target = copy / "rule" / "sales" / "proposal-validity.md"
            target.write_text(target.read_text() + "\nAn added line.\n")
            after = build(root=copy)
        self.assertNotEqual(before["entries"], after["entries"])

    def test_the_expansion_contract_version_is_recorded(self) -> None:
        self.assertEqual(rc.EXPANSION_CONTRACT, build()["expansion_contract_version"])


class Stopping(unittest.TestCase):
    """Every stop reason of specs/0009 R8, produced at least once."""

    def test_closure_complete(self) -> None:
        self.assertEqual("closure_complete", build()["stop_reason"])

    def test_budget_exhausted(self) -> None:
        document = build(budget=4)
        self.assertEqual("budget_exhausted", document["stop_reason"])
        self.assertLessEqual(document["budget"]["consumed"], 4)

    def test_depth_limit(self) -> None:
        document = build(depth=1)
        self.assertEqual("depth_limit", document["stop_reason"])
        self.assertTrue(all(e["depth"] <= 1 for e in document["entries"]))

    def test_unresolved_relationship(self) -> None:
        with tempfile.TemporaryDirectory() as holder:
            copy = Path(holder) / "knowledge"
            shutil.copytree(FIXTURE, copy)
            target = copy / "rule" / "sales" / "proposal-validity.md"
            target.write_text(
                target.read_text().replace(
                    "depends_on: [", "depends_on: [ko.definition.sales.nothing-here, ", 1
                )
            )
            document = build(root=copy)
        self.assertEqual("unresolved_relationship", document["stop_reason"])

    def test_every_stop_reason_is_reachable(self) -> None:
        """A closed set with an unreachable member is a set with a member nobody tested."""
        declared = set(
            json.loads(SCHEMA.read_text())["properties"]["stop_reason"]["enum"]
        )
        self.assertEqual(
            declared, {rc.CLOSURE_COMPLETE, rc.BUDGET_EXHAUSTED, rc.DEPTH_LIMIT, rc.UNRESOLVED}
        )

    def test_a_budget_the_first_root_exceeds_stops_immediately(self) -> None:
        document = build(budget=1, unit="bytes")
        self.assertEqual("budget_exhausted", document["stop_reason"])
        self.assertEqual([], document["entries"])


class Degradation(unittest.TestCase):
    """specs/0009 R15: recorded separately from the single stop reason."""

    def test_a_complete_closure_degrades_in_no_way(self) -> None:
        self.assertEqual([], build()["degradations"])

    def test_truncation_records_both_the_stop_and_the_degradation(self) -> None:
        document = build(budget=4)
        self.assertEqual("budget_exhausted", document["stop_reason"])
        self.assertIn("budget_exhausted", [d["code"] for d in document["degradations"]])

    def test_an_unresolved_root_degrades_without_stopping_the_run(self) -> None:
        """specs/0001 R13 requires resolution to continue past it; R16 makes it never a stop reason."""
        document = build(roots=[("ko.definition.sales.not-a-thing", "absent"), (RULE, CLAIM)])
        self.assertIn("unresolved_root", [d["code"] for d in document["degradations"]])
        self.assertNotEqual("unresolved_root", document["stop_reason"])
        self.assertTrue(document["entries"], "the run should have continued past the bad root")

    def test_every_degradation_names_a_subject_and_evidence(self) -> None:
        for document in (build(budget=4), build(depth=1)):
            for entry in document["degradations"]:
                self.assertTrue(entry["subject"])
                self.assertTrue(entry["evidence"])


class Traversal(unittest.TestCase):
    def test_only_declared_edge_kinds_are_followed(self) -> None:
        """specs/0009 R9: a relationship the ontology does not hold is not traversed."""
        from knowledge_graph_lib import EDGE_KINDS

        graph = load(FIXTURE)
        for node_id in graph.nodes:
            for kind, _target in rc.outgoing(graph, node_id):
                self.assertTrue(EDGE_KINDS[kind].traversed, kind)

    def test_a_supersession_is_never_followed(self) -> None:
        """knowledge_graph_lib keeps supersessions out of `edges`, so this holds structurally."""
        graph = load(FIXTURE)
        kinds = {kind for node in graph.nodes for kind, _ in rc.outgoing(graph, node)}
        self.assertNotIn("superseded_by", kinds)

    def test_a_root_is_at_depth_zero_and_carries_no_via(self) -> None:
        first = build()["entries"][0]
        self.assertEqual(0, first["depth"])
        self.assertNotIn("via", first)

    def test_every_non_root_entry_names_the_edge_that_reached_it(self) -> None:
        for entry in build()["entries"][1:]:
            self.assertIn("via", entry)

    def test_no_entry_appears_twice(self) -> None:
        entries = [e["id"] for e in build()["entries"]]
        self.assertEqual(len(entries), len(set(entries)))


class EarnsItsPlace(unittest.TestCase):
    """specs/0009 R10 and R11 — the measurement, and the decision it forces."""

    def setUp(self) -> None:
        self.graph = load(FIXTURE)
        self.total = len(self.graph.nodes)

    def excluded(self, root: str) -> float:
        document = rc.package(
            self.graph, "cp_00000001", "cr_00000001", [(root, "measured")], 10_000, "objects", None
        )
        return 100 * (self.total - len(document["entries"])) / self.total

    def test_resolution_selects_rather_than_including_everything(self) -> None:
        """R11's condition, on this repository's bundle: it selects better than the whole bundle."""
        measured = [
            self.excluded(root)
            for root in (
                "ko.rule.billing.invoice-amount",
                "ko.rule.sales.proposal-validity",
                "ko.definition.billing.invoice",
                "ko.lifecycle.sales.proposal",
                "ko.boundary.billing",
            )
        ]
        self.assertGreater(sum(measured) / len(measured), 0, "nothing was excluded anywhere")
        self.assertGreater(min(measured), 0, "some root pulled in the entire bundle")

    def test_the_recorded_measurement_matches_what_the_code_produces(self) -> None:
        """A figure in prose that nothing derives is the drift this repository has already had twice."""
        recorded = (REPO_ROOT / "specs" / "0009-context-assembly.md").read_text()
        self.assertIn(f"{self.total} knowledge objects", recorded)

    def test_expanding_from_a_boundary_reaches_almost_nothing(self) -> None:
        """A property of the ontology, recorded because it makes one selection strategy wrong.

        `boundary` edges run member → boundary, and a boundary never enumerates its members
        (specs/0003). Expansion follows declared direction, so a boundary chosen as a root brings
        in almost nothing — which is a fact the root selector has to know, not a bug to route
        around by adding an undeclared reverse edge.
        """
        self.assertGreater(self.excluded("ko.boundary.billing"), 90)


if __name__ == "__main__":
    unittest.main()


class CommittedFixture(unittest.TestCase):
    """The package in `fixtures/consumer-knowledge/`, recomputed from what it records.

    `specs/0009` R13 makes a package `claim-recorded`: not committed for its own sake, but
    recomputable from the recorded roots, the graph, the budget, and the expansion contract
    version. This fixture commits one anyway, because a fixture is evidence a reader inspects —
    and that is only safe while the committed copy is asserted to equal what the recorded inputs
    produce. Otherwise it is a second authority for a scope the graph already determines.
    """

    def setUp(self) -> None:
        self.path = REPO_ROOT / "fixtures" / "consumer-knowledge" / "context-package.json"
        self.document = json.loads(self.path.read_text())

    def test_it_recomputes_from_its_own_recorded_inputs(self) -> None:
        graph = load(FIXTURE)
        roots = [(r["id"], r["claim"]) for r in self.document["roots"]]
        budget = self.document["budget"]
        fresh = rc.package(
            graph,
            self.document["package_id"],
            self.document["request_id"],
            roots,
            budget["limit"],
            budget["unit"],
            budget.get("depth_limit"),
        )
        self.assertEqual(fresh, self.document)

    def test_it_conforms(self) -> None:
        validator = Draft202012Validator(json.loads(SCHEMA.read_text()))
        self.assertEqual([], list(validator.iter_errors(self.document)))

    def test_it_is_a_truncated_package_and_says_so(self) -> None:
        """The fixture exercises the degraded path, which the other workflow fixture does not."""
        self.assertEqual("budget_exhausted", self.document["stop_reason"])
        self.assertTrue(self.document["degradations"])

    def test_the_workflow_event_agrees_with_the_package(self) -> None:
        """specs/0001 R14 makes the degradation an input to acceptance, so the two must not diverge."""
        log = REPO_ROOT / "fixtures" / "consumer-knowledge" / "event-log.jsonl"
        events = [json.loads(line) for line in log.read_text().splitlines() if line.strip()]
        resolution = next(e for e in events if e["phase"] == "context-resolution")
        self.assertEqual("degraded", resolution["outcome"])
        self.assertIn(self.document["package_id"], resolution["degradation"])
        self.assertIn(self.document["stop_reason"], resolution["degradation"])
