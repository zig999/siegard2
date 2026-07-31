"""Projections are reproducible from the graph, and the committed ones are not stale.

Validation item 5 of foundation/0003 requires the glossary and context-map projections to be
generated from the fixture, with a test asserting regeneration is byte-identical (R51).
Byte identity is asserted three ways, because each catches a different failure:

- two runs over one knowledge base agree, which catches ordering that depends on a set's
  iteration or on a filesystem walk;
- the committed files match what the graph produces, which catches a projection that rotted
  after the knowledge changed;
- a change in knowledge changes the projection, which catches the opposite failure — a
  generator whose output is stable because it reads nothing.

The third is the one a byte-identity test usually forgets. A generator emitting a constant
passes the first two.
"""

from __future__ import annotations

import json

from jsonschema import Draft202012Validator
from knowledge_graph_lib import load
from project_knowledge import GRAPH_SCHEMA_PATH, outputs, run
from tests.support import FIXTURE, KnowledgeCase

PROPOSAL = "definition/sales/proposal.md"
GENERATED = ("graph.json", "index.md", "glossary.md", "context-map.md")


class ProjectionsAreReproducible(KnowledgeCase):
    def test_two_runs_agree_byte_for_byte(self):
        first = outputs(load(self.root))
        second = outputs(load(self.root))
        self.assertEqual(sorted(first), sorted(GENERATED))
        for name in GENERATED:
            self.assertEqual(first[name], second[name], f"{name} is not reproducible")

    def test_committed_projections_match_the_graph(self):
        code, differences = run(FIXTURE, check=True)
        self.assertEqual(differences, [])
        self.assertEqual(code, 0)

    def test_writing_then_checking_agrees(self):
        write_code, _ = run(self.root, check=False)
        self.assertEqual(write_code, 0)
        check_code, differences = run(self.root, check=True)
        self.assertEqual(differences, [])
        self.assertEqual(check_code, 0)

    def test_a_change_in_knowledge_changes_the_projection(self):
        before = outputs(load(self.root))
        self.edit(PROPOSAL, lambda d: d.update(title="Quotation"))
        after = outputs(load(self.root))
        self.assertNotEqual(before["glossary.md"], after["glossary.md"])
        self.assertNotEqual(before["graph.json"], after["graph.json"])
        self.assertIn("Quotation", after["glossary.md"])

    def test_check_reports_a_stale_projection_rather_than_repairing_it(self):
        run(self.root, check=False)
        (self.root / "glossary.md").write_text("stale\n")
        code, differences = run(self.root, check=True)
        self.assertEqual(code, 1)
        self.assertTrue(any("glossary.md" in d for d in differences), differences)
        self.assertEqual((self.root / "glossary.md").read_text(), "stale\n", "check must not repair")


class GraphConformsToItsContract(KnowledgeCase):
    def test_materialized_graph_validates_against_its_schema(self):
        generated = json.loads(outputs(load(self.root))["graph.json"])
        Draft202012Validator(json.loads(GRAPH_SCHEMA_PATH.read_text())).validate(generated)
        self.assertEqual(generated["contract_version"], "knowledge-graph/1")

    def test_graph_declares_the_traversal_policy_a_consumer_needs(self):
        """R19 requires every edge to declare whether expansion traverses it, and to what depth.

        The materialized artifact carries the policy so expansion reads the graph rather than
        importing the materializer.
        """
        generated = json.loads(outputs(load(self.root))["graph.json"])
        for name, kind in generated["edge_kinds"].items():
            self.assertIn("traversed", kind, name)
            self.assertIn("depth", kind, name)
            if kind["traversed"]:
                self.assertIsNotNone(kind["depth"], f"{name} is traversed with no declared depth")


class MeasurementIsRecorded(KnowledgeCase):
    """Validation item 6 — the R52 measurement runs and the record is not stale."""

    def test_recorded_measurement_matches_the_fixture(self):
        from measure_ontology import run as measure

        code, problems = measure(FIXTURE, check=True)
        self.assertEqual(problems, [])
        self.assertEqual(code, 0)

    def test_measurement_finds_no_removal_candidate_after_the_repair(self):
        """The R52 candidates the first measurement found were removed from the specification."""
        from measure_ontology import render

        recorded = render(load(FIXTURE))
        self.assertIn("Every declared edge is traversed and has at least one instance.", recorded)
        self.assertNotIn("Edges meeting the removal condition", recorded)
        self.assertIn("No type meets both removal conditions", recorded)

    def test_measurement_still_reports_supersession(self):
        """Moving `superseded_by` out of the edge table must not move it out of view."""
        from measure_ontology import render

        recorded = render(load(FIXTURE))
        self.assertIn("`superseded_by` is counted apart: 1 reference(s)", recorded)
