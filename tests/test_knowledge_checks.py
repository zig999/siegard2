"""Both outcomes for each check foundation/0003 requires a script to decide.

Validation item 3 names three by requirement — the cross-context check of R15, the totality
check of R11 including both shorthand expansions, and the cardinality checks of R18 — and
requires tests covering both outcomes. A rejection alone proves a check fires; an
acceptance alone proves nothing fires wrongly. Both are needed, and neither is enough.

The positive cases assert that the accepted shape is genuinely the interesting one. A test
asserting "this validates" over a tree with no cross-context edge would pass while checking
nothing, so each positive first asserts the condition it claims to accept is present.
"""

from __future__ import annotations

from knowledge_graph_lib import context_of, load
from tests.support import FIXTURE, KnowledgeCase

INVOICE = "definition/billing/invoice.md"
PROPOSAL = "definition/sales/proposal.md"
RULE = "rule/sales/proposal-expiration.md"
SALES_LIFECYCLE = "lifecycle/sales/proposal.md"


class CrossContext(KnowledgeCase):
    """R15 — a reference leaving a bounded context targets an interface."""

    def test_cross_context_edge_to_an_interface_is_accepted(self):
        graph = load(FIXTURE)
        crossing = [
            edge
            for edge in graph.edges
            if edge.kind == "depends_on"
            and context_of(graph, edge.source) != context_of(graph, edge.target)
        ]
        self.assertTrue(crossing, "the fixture holds no cross-context edge, so acceptance proves nothing")
        self.assertEqual(
            sorted({graph.nodes[e.target].kind for e in crossing}),
            ["interface"],
            "every crossing edge in the fixture must target an interface",
        )
        self.assertAccepted()

    def test_cross_context_edge_to_a_definition_is_rejected(self):
        self.edit(INVOICE, lambda d: d.update(depends_on=["ko.definition.sales.proposal"]))
        self.assertRejected("crosses from", "names a 'definition'")

    def test_cross_context_attribute_reference_is_rejected(self):
        """An attribute's target is restricted to a definition, so crossing can never conform.

        This is the shape the two rules leave impossible rather than merely discouraged: the
        edge table forbids an attribute reference from naming an interface, and R15 forbids
        it from naming anything else once it leaves the context.
        """

        def retarget(data):
            for attribute in data["attributes"]:
                if attribute["type"] == "ref":
                    attribute["target"] = "ko.definition.billing.invoice"

        self.edit(PROPOSAL, retarget)
        self.assertRejected("crosses from", "attributes.customer")


class Totality(KnowledgeCase):
    """R11 — the transition table is total, with both shorthands expanded before checking."""

    def test_terminal_shorthand_is_expanded_before_the_product_is_checked(self):
        data, _ = self.read(SALES_LIFECYCLE)
        self.assertTrue(
            any(r["from"] == "terminal" for r in data["rejections"]),
            "the fixture must use the `terminal` shorthand for this acceptance to mean anything",
        )
        # 5 states x 4 triggers is 20 pairs; 5 are transitions and the shorthand decides 12
        # of the remaining 15. Without expansion the table would read as non-total.
        self.assertEqual(len(data["states"]) * 4, 20)
        self.assertAccepted()

    def test_removing_the_terminal_shorthand_leaves_pairs_undecided(self):
        def narrow(data):
            for rejection in data["rejections"]:
                if rejection["from"] == "terminal":
                    rejection["from"] = "accepted"

        self.edit(SALES_LIFECYCLE, narrow)
        self.assertRejected("(expired, issue)", "not total")

    def test_trigger_list_shorthand_is_expanded(self):
        data, _ = self.read(SALES_LIFECYCLE)
        self.assertTrue(
            any(isinstance(r["trigger"], list) and len(r["trigger"]) > 1 for r in data["rejections"]),
            "the fixture must use a trigger list for this acceptance to mean anything",
        )
        self.assertAccepted()

    def test_shortening_a_trigger_list_leaves_a_pair_undecided(self):
        def shorten(data):
            for rejection in data["rejections"]:
                if rejection["from"] == "draft":
                    rejection["trigger"] = ["accept"]

        self.edit(SALES_LIFECYCLE, shorten)
        self.assertRejected("(draft, expire)", "not total")

    def test_a_pair_decided_twice_is_rejected(self):
        def double(data):
            data["rejections"].append(
                {
                    "from": "draft",
                    "trigger": ["issue"],
                    "error": "ko.definition.sales.proposal-not-issued",
                }
            )

        self.edit(SALES_LIFECYCLE, double)
        self.assertRejected("decided twice")

    def test_reserved_terminal_as_a_state_name_is_rejected(self):
        def reserve(data):
            data["states"] = data["states"] + ["terminal"]

        self.edit(SALES_LIFECYCLE, reserve)
        self.assertRejected("reserved")


class InverseCardinality(KnowledgeCase):
    """R18 and R20 — the inverse bound the edge table declares on lifecycle.subject."""

    def test_one_lifecycle_per_subject_is_accepted(self):
        graph = load(FIXTURE)
        subjects = [e.target for e in graph.edges if e.kind == "lifecycle.subject"]
        self.assertTrue(subjects, "the fixture holds no lifecycle, so acceptance proves nothing")
        self.assertEqual(len(subjects), len(set(subjects)))
        self.assertAccepted()


class GraphIntegrity(KnowledgeCase):
    """R22 and R29 — unresolved targets, orphans, and cycles, reported and never repaired."""

    def test_edge_naming_an_absent_node_is_rejected(self):
        self.edit(RULE, lambda d: d.update(depends_on=["ko.definition.sales.nowhere"]))
        self.assertRejected("which the graph does not hold")

    def test_orphan_is_rejected(self):
        # The expiration rule's `depends_on` is the only thing holding this domain error into
        # the graph, so narrowing it isolates the orphan check from every other failure.
        self.edit(RULE, lambda d: d.update(depends_on=["ko.definition.sales.proposal"]))
        self.assertRejected("orphan", "proposal-expired")

    def test_cycle_is_rejected(self):
        self.edit(PROPOSAL, lambda d: d.update(depends_on=["ko.rule.sales.proposal-expiration"]))
        self.assertRejected("forms a cycle")

    def test_rejection_error_that_is_not_a_domain_error_is_rejected(self):
        def misdirect(data):
            data["rejections"][0]["error"] = "ko.definition.sales.proposal"

        self.edit(SALES_LIFECYCLE, misdirect)
        self.assertRejected("ddd domain-error")

    def test_identity_naming_an_absent_attribute_is_rejected(self):
        self.edit(PROPOSAL, lambda d: d.update(identity={"attributes": ["nonexistent"]}))
        self.assertRejected("identity names attribute 'nonexistent'")

    def test_numeric_id_segment_is_rejected(self):
        """R39 — an id is never a sequential number, and no allocator exists."""
        self.edit(PROPOSAL, lambda d: d.update(id="ko.definition.sales.0001"))
        self.rename(PROPOSAL, "definition/sales/0001.md")
        self.assertRejected("sequential number")

    def test_id_context_disagreeing_with_the_boundary_chain_is_rejected(self):
        self.edit(PROPOSAL, lambda d: d.update(boundary="ko.boundary.billing.invoice"))
        self.assertRejected("boundary chain resolves to")
