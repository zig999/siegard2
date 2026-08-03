"""The body form rules of foundation/0003, each proven to reject and to accept.

R43 through R48 are where the specification pays a stated human cost for machine
consumption. A form rule nothing enforces is a style suggestion, so each rule that can be
decided mechanically is exercised here. Two clauses of R46 are deliberately absent, and
scripts/validate_knowledge.py names them: that a body carries no rationale or motivating
narrative, and that a body is not the only home of a machine-read fact. Both are judgments
about meaning rather than form.
"""

from __future__ import annotations

from tests.support import KnowledgeCase

PROPOSAL = "definition/sales/proposal.md"
SYSTEM = "system.md"

WELL_FORMED = """
# Proposal

## Answer

A proposal is a priced offer issued to one customer.

## Invariants

A proposal MUST hold at least one item.
"""


class BodyArity(KnowledgeCase):
    """R43 — exactly the two sections the type names, in order, none empty."""

    def test_well_formed_body_is_accepted(self):
        self.replace_body(PROPOSAL, WELL_FORMED)
        self.assertAccepted()

    def test_wrong_section_name_is_rejected(self):
        self.replace_body(PROPOSAL, WELL_FORMED.replace("## Invariants", "## Rationale"))
        self.assertRejected("carries sections")

    def test_reordered_sections_are_rejected(self):
        body = "\n# Proposal\n\n## Invariants\n\nA proposal MUST hold one item.\n\n## Answer\n\nA proposal is an offer.\n"
        self.replace_body(PROPOSAL, body)
        self.assertRejected("in that order")

    def test_extra_heading_is_rejected(self):
        self.replace_body(PROPOSAL, WELL_FORMED + "\n### Notes\n\nAnything.\n")
        self.assertRejected("extra heading")

    def test_empty_section_is_rejected(self):
        self.replace_body(PROPOSAL, "\n# Proposal\n\n## Answer\n\nA proposal is an offer.\n\n## Invariants\n\n")
        self.assertRejected("is empty")

    def test_none_satisfies_an_otherwise_empty_section(self):
        self.replace_body(PROPOSAL, "\n# Proposal\n\n## Answer\n\nA proposal is an offer.\n\n## Invariants\n\nNone.\n")
        self.assertAccepted()


class SentencePerLine(KnowledgeCase):
    """R44 — one sentence per line, so path:line is a citable anchor and a diff is one line."""

    def test_two_sentences_on_one_line_are_rejected(self):
        body = WELL_FORMED.replace(
            "A proposal is a priced offer issued to one customer.",
            "A proposal is an offer. A proposal is priced.",
        )
        self.replace_body(PROPOSAL, body)
        self.assertRejected("more than one sentence")


class NormativeForm(KnowledgeCase):
    """R45 — one RFC 2119 keyword and no pronoun in a normative statement."""

    def test_two_keywords_on_one_line_are_rejected(self):
        body = WELL_FORMED.replace(
            "A proposal MUST hold at least one item.",
            "A proposal MUST hold one item and MUST NOT hold zero.",
        )
        self.replace_body(PROPOSAL, body)
        self.assertRejected("RFC 2119 keywords")

    def test_must_not_counts_as_one_keyword(self):
        body = WELL_FORMED.replace(
            "A proposal MUST hold at least one item.", "A proposal MUST NOT hold zero items."
        )
        self.replace_body(PROPOSAL, body)
        self.assertAccepted()

    def test_pronoun_in_a_normative_statement_is_rejected(self):
        body = WELL_FORMED.replace(
            "A proposal MUST hold at least one item.", "A proposal MUST hold its item."
        )
        self.replace_body(PROPOSAL, body)
        self.assertRejected("pronoun")

    def test_pronoun_outside_a_normative_statement_is_not_rejected(self):
        """The rule binds a normative statement, and the check does not exceed the rule."""
        body = WELL_FORMED.replace(
            "A proposal is a priced offer issued to one customer.",
            "A proposal carries its price for a bounded period.",
        )
        self.replace_body(PROPOSAL, body)
        self.assertAccepted()


class LengthCeiling(KnowledgeCase):
    """R48 — a ceiling read from the knowledge base, never invented by the validator."""

    def test_body_over_the_declared_ceiling_is_rejected(self):
        self.edit(SYSTEM, lambda d: d.update(limits={"body_lines": 3}))
        self.assertRejected("against a ceiling of 3")

    def test_absent_ceiling_is_reported_rather_than_defaulted(self):
        self.edit(SYSTEM, lambda d: d.pop("limits"))
        self.assertRejected("cannot be enforced")


class Aliases(KnowledgeCase):
    """R35 — a synonym is declared in `aliases` and appears in no body."""

    def test_declared_synonym_used_in_a_body_is_rejected(self):
        body = WELL_FORMED.replace(
            "A proposal is a priced offer issued to one customer.",
            "A proposal is a priced offer issued to one client.",
        )
        self.replace_body(PROPOSAL, body)
        self.assertRejected("synonym")
