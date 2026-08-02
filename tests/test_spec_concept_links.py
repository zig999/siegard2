"""A concept link in a specification must resolve, and must name what it resolves to.

The check exists because of a defect the review of `foundation/0009-context-assembly.md`
found: its **Definitions** section labelled a link `knowledge object` while pointing at
`docs/concepts/knowledge-base.md`. Both files exist, so the resolution check passed it.
A mislabelled link to an existing file was invisible to `make validate` across every
specification, and the reader who follows it is told the wrong term is the authority.

Both outcomes are covered for the reason tests/support.py states about the knowledge
fixture: a rejection test alone cannot tell a working check from one that rejects
everything, so the committed specifications are asserted clean beside every rejection.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from validate_specs import check_concept_links, label_names

from tests.support import REPO_ROOT

SPECS = REPO_ROOT / "foundation"
# Only the parent directory is read, to resolve a link the way a real specification
# would. The file itself is never opened, so it does not need to exist.
AS_IF_IN_SPECS = SPECS / "0000-a-specification-under-test.md"


def problems(body: str) -> list[str]:
    return check_concept_links(AS_IF_IN_SPECS, body)


class ConceptLinksInCommittedSpecifications(unittest.TestCase):
    def test_every_committed_specification_links_cleanly(self):
        for path in sorted(SPECS.glob("*.md")):
            with self.subTest(specification=path.name):
                self.assertEqual(
                    check_concept_links(path, path.read_text()),
                    [],
                    f"{path.name} must link the concept bundle cleanly",
                )


class AMislabelledLinkIsRejected(unittest.TestCase):
    def assertOneProblem(self, found: list[str], *needles: str) -> None:
        if not any(all(needle in problem for needle in needles) for problem in found):
            listing = "\n".join(f"    {p}" for p in found) or "    (nothing reported)"
            self.fail(f"no single problem holds all of {needles}. Reported:\n{listing}")

    def test_the_defect_this_check_was_written_for(self):
        """The `foundation/0009` case: a label naming one concept, a target holding another."""
        found = problems("[knowledge object](../docs/concepts/knowledge-base.md)")
        self.assertOneProblem(found, "knowledge object", "knowledge base")

    def test_the_two_records_cannot_be_swapped(self):
        """`foundation/0008` R15 forbids one manifest wearing the other's name in prose.

        A link is where that confusion would survive review, because the target's title
        is not on the page the reader is looking at.
        """
        found = problems("[generation manifest](../docs/concepts/distribution-manifest.md)")
        self.assertOneProblem(found, "generation manifest", "distribution manifest")

    def test_a_leading_fragment_is_rejected(self):
        found = problems("[knowledge](../docs/concepts/knowledge-base.md)")
        self.assertOneProblem(found, "knowledge", "knowledge base")

    def test_a_link_that_resolves_to_no_file_is_still_reported(self):
        found = problems("[nothing](../docs/concepts/does-not-exist.md)")
        self.assertOneProblem(found, "resolves to no file")


class ALinkThatNamesItsConceptIsAccepted(unittest.TestCase):
    def accepts(self, body: str) -> None:
        self.assertEqual(problems(body), [], f"{body} names its concept")

    def test_the_exact_title(self):
        self.accepts("[knowledge base](../docs/concepts/knowledge-base.md)")

    def test_the_file_slug_as_a_label(self):
        self.accepts("[knowledge-base](../docs/concepts/knowledge-base.md)")

    def test_a_plural(self):
        self.accepts("[artifact classes](../docs/concepts/artifact-class.md)")
        self.accepts("[contract versions](../docs/concepts/contract-version.md)")
        self.accepts("[capabilities](../docs/concepts/capability.md)")

    def test_a_shortened_label_that_keeps_the_head_noun(self):
        self.accepts("[pack](../docs/concepts/target-pack.md)")
        self.accepts("[knowledge](../docs/concepts/domain-knowledge.md)")

    def test_a_link_outside_the_concept_bundle_is_not_this_check_s_business(self):
        self.accepts("[compatibility](../.claude/rules/compatibility.md)")
        self.accepts("[the plugin contract](../schemas/plugin.json)")


class TheMatchingRule(unittest.TestCase):
    """`label_names` decides the whole check, so its edges are tested directly."""

    def test_inflection_is_matched_in_both_directions(self):
        self.assertTrue(label_names("artifact classes", "artifact class"))
        self.assertTrue(label_names("artifact class", "artifact classes"))

    def test_a_double_s_is_not_a_plural(self):
        self.assertTrue(label_names("process", "process"))

    def test_a_different_head_noun_never_matches(self):
        self.assertFalse(label_names("knowledge object", "knowledge base"))
        self.assertFalse(label_names("generation manifest", "distribution manifest"))

    def test_an_empty_label_never_matches(self):
        self.assertFalse(label_names("", "capability"))
        self.assertFalse(label_names("**", "capability"))


if __name__ == "__main__":
    unittest.main()
