"""The fixture validates, and exercises what specs/0003 requires a fixture to exercise.

This module is the positive half of every rejection test elsewhere in the suite. A
validator proven only to reject cannot be distinguished from one that rejects everything,
so the tree each of those tests mutates is asserted here to be clean before mutation.

It also holds the coverage assertions of the specification's own validation item 4: a
two-context bundle exercising all six node types and every traversed edge. Coverage is
asserted rather than described, because a fixture that quietly stops covering an edge is
the failure the item exists to prevent.
"""

from __future__ import annotations

from collections import Counter

from knowledge_graph_lib import EDGE_KINDS, load
from tests.support import FIXTURE, KnowledgeCase


class FixtureValidates(KnowledgeCase):
    def test_pristine_fixture_reports_nothing(self):
        self.assertAccepted()

    def test_committed_fixture_reports_nothing(self):
        # The copy under test is a copy. This asserts the committed tree itself, so a
        # fixture that rots in place is caught rather than only its temporary clone.
        from validate_knowledge import validate

        self.assertEqual(validate(FIXTURE), [])


class FixtureCoverage(KnowledgeCase):
    def setUp(self):
        super().setUp()
        self.graph = load(FIXTURE)

    def test_holds_two_bounded_contexts(self):
        contexts = sorted(
            node.id
            for node in self.graph.nodes.values()
            if node.kind == "boundary" and node.data.get("ddd") == "bounded-context"
        )
        self.assertEqual(contexts, ["ko.boundary.billing", "ko.boundary.sales"])

    def test_holds_every_node_type(self):
        present = Counter(node.kind for node in self.graph.nodes.values())
        for kind in ("definition", "rule", "lifecycle", "interface", "boundary", "process"):
            self.assertGreater(present[kind], 0, f"no '{kind}' in the fixture")
        self.assertGreater(present["adr"], 0, "no ADR node in the fixture")

    def test_exercises_every_traversed_edge(self):
        seen = Counter(edge.kind for edge in self.graph.edges)
        missing = [
            name for name, kind in EDGE_KINDS.items() if kind.traversed and not seen[name]
        ]
        self.assertEqual(missing, [], f"traversed edges with no instance: {missing}")

    def test_every_declared_edge_has_at_least_one_instance(self):
        """R52's removal condition, asserted rather than left for a reader to notice.

        The first measurement over this fixture found three edges no resolution read, and the
        specification was repaired: `references` and `supersedes` were removed and
        `superseded_by` became a resolvable reference. Nothing declared should now be idle, so
        an edge that falls to zero instances is a finding the next reader should not have to
        rediscover.
        """
        seen = Counter(edge.kind for edge in self.graph.edges)
        idle = sorted(name for name in EDGE_KINDS if not seen[name])
        self.assertEqual(idle, [], f"declared edges with no instance: {idle}")

    def test_supersession_is_held_outside_the_edge_list(self):
        """R22 forbids expansion from following `superseded_by`, in either direction.

        Keeping the references out of `edges` enforces that structurally: a traversal cannot
        filter out what it never receives. The fixture holds one so the path is exercised.
        """
        self.assertEqual(len(self.graph.supersessions), 1)
        self.assertNotIn("superseded_by", {edge.kind for edge in self.graph.edges})
        reference = self.graph.supersessions[0]
        self.assertEqual(reference.source, "ko.rule.sales.proposal-validity")
        self.assertEqual(reference.target, "ko.rule.sales.proposal-expiration")
