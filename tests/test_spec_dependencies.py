"""The acceptance order the specification set declares about itself must hold.

`specs/README.md` states the rule in prose — "No framework specification is accepted
before the method specification it depends on" — and nothing checked it. The edges are
derived from the acceptance conditions the documents already write, so the check adds no
authored field that could disagree with the text.

Both outcomes are covered for the reason tests/support.py states about the knowledge
fixture: a rejection test alone cannot tell a working check from one that rejects
everything, so the committed set is asserted clean beside every rejection.

The "clean" half is asserted over the committed set and the "rejected" half over
synthetic input, deliberately. How many edges the committed set holds is a function of
which documents are proposed at the time — every specification was accepted on
2026-07-31, which took the count to zero — so a test demanding the live corpus produce
an edge would fail on a change that is not a defect. The derivation itself is proven
instead, on input this file controls.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from frontmatter_lib import split_frontmatter
from validate_specs import (
    RESERVED,
    acceptance_prerequisites,
    check_acceptance_order,
    check_spec_references,
    find_cycle,
)

from tests.support import REPO_ROOT

SPECS = REPO_ROOT / "specs"


def committed() -> dict[str, tuple[str, str, str]]:
    """Every committed specification as id -> (filename, status, body)."""
    found: dict[str, tuple[str, str, str]] = {}
    for path in sorted(SPECS.glob("*.md")):
        if path.name in RESERVED:
            continue
        data, body = split_frontmatter(path.read_text())
        found[data["id"]] = (path.name, data["status"], body)
    return found


class TheCommittedSetIsClean(unittest.TestCase):
    def setUp(self) -> None:
        self.specs = committed()
        self.filenames = {sid: name for sid, (name, _, _) in self.specs.items()}
        self.statuses = {sid: status for sid, (_, status, _) in self.specs.items()}
        self.paths = {sid: f"specs/{name}" for sid, (name, _, _) in self.specs.items()}

    def test_every_cross_reference_resolves(self):
        for sid, (name, _, body) in self.specs.items():
            with self.subTest(specification=name):
                self.assertEqual(check_spec_references(body, self.filenames), [])

    def test_the_acceptance_order_holds(self):
        prerequisites = {sid: acceptance_prerequisites(body) for sid, (_, _, body) in self.specs.items()}
        self.assertEqual(check_acceptance_order(prerequisites, self.statuses, self.paths), [])


class ReferencesAreResolved(unittest.TestCase):
    FILENAMES = {"0001": "0001-first.md", "0004": "0004-fourth.md"}

    def problems(self, body: str) -> list[str]:
        return check_spec_references(body, self.FILENAMES)

    def test_an_unknown_id_is_reported(self):
        found = self.problems("as `specs/0099` requires")
        self.assertEqual(len(found), 1)
        self.assertIn("specs/0099", found[0])

    def test_a_filename_that_disagrees_with_the_id_is_reported(self):
        found = self.problems("see `specs/0004-renamed-yesterday.md` R3")
        self.assertEqual(len(found), 1)
        self.assertIn("0004-fourth.md", found[0])

    def test_the_two_accepted_forms_pass(self):
        self.assertEqual(self.problems("`specs/0001` and `specs/0004-fourth.md`"), [])

    def test_one_bad_reference_is_reported_once_however_often_it_appears(self):
        self.assertEqual(len(self.problems("`specs/0099` … `specs/0099` … `specs/0099`")), 1)


class PrerequisitesAreDerivedFromTheAcceptanceSection(unittest.TestCase):
    def test_a_prerequisite_outside_the_section_is_not_an_edge(self):
        body = (
            "## Scope\n\nThis rests on `specs/0004`, which is accepted nowhere yet.\n\n"
            "## Validation required before acceptance\n\n1. A maintainer accepts this.\n"
        )
        self.assertEqual(acceptance_prerequisites(body), [])

    def test_a_condition_naming_a_specification_without_the_phrase_is_not_an_edge(self):
        body = (
            "## Validation required before acceptance\n\n"
            "1. A fixture exercises `specs/0003` R38 in both directions.\n"
        )
        self.assertEqual(acceptance_prerequisites(body), [])

    def test_an_unmet_and_a_met_condition_are_distinguished(self):
        body = (
            "## Validation required before acceptance\n\n"
            "1. `specs/0004` is accepted. It is the authority for artifact classes.\n"
            "2. ~~`specs/0001` is accepted.~~ **Met** on 2026-07-31.\n"
        )
        self.assertEqual(acceptance_prerequisites(body), [("0004", False), ("0001", True)])

    def test_a_document_with_no_acceptance_section_declares_nothing(self):
        self.assertEqual(acceptance_prerequisites("## Scope\n\nAccepted already.\n"), [])


class TheAcceptanceOrderIsEnforced(unittest.TestCase):
    PATHS = {"0001": "specs/0001-a.md", "0004": "specs/0004-b.md", "0011": "specs/0011-c.md"}

    def order(self, prerequisites: dict, statuses: dict) -> list[str]:
        return check_acceptance_order(prerequisites, statuses, self.PATHS)

    def test_a_met_claim_against_a_proposed_target_is_rejected(self):
        found = self.order(
            {"0011": [("0004", True)]},
            {"0011": "proposed", "0004": "proposed"},
        )
        self.assertEqual(len(found), 1)
        self.assertIn("**Met**", found[0])

    def test_a_met_claim_against_an_accepted_target_passes(self):
        self.assertEqual(
            self.order({"0011": [("0004", True)]}, {"0011": "proposed", "0004": "accepted"}),
            [],
        )

    def test_an_accepted_specification_with_an_unmet_prerequisite_is_rejected(self):
        found = self.order(
            {"0011": [("0004", False)]},
            {"0011": "accepted", "0004": "proposed"},
        )
        self.assertEqual(len(found), 1)
        self.assertIn("still carries an unmet acceptance condition", found[0])

    def test_a_proposed_specification_with_an_unmet_prerequisite_passes(self):
        """That is the normal state of the set, not a defect."""
        self.assertEqual(
            self.order({"0011": [("0004", False)]}, {"0011": "proposed", "0004": "proposed"}),
            [],
        )

    def test_a_specification_requiring_itself_is_rejected(self):
        found = self.order({"0004": [("0004", False)]}, {"0004": "proposed"})
        self.assertEqual(len(found), 1)
        self.assertIn("itself", found[0])

    def test_a_cycle_is_reported(self):
        found = self.order(
            {"0004": [("0011", False)], "0011": [("0004", False)]},
            {"0004": "proposed", "0011": "proposed"},
        )
        self.assertTrue(any("cycle" in problem for problem in found), found)

    def test_a_prerequisite_on_a_missing_specification_is_left_to_the_reference_check(self):
        """Reporting it twice in two vocabularies would name one defect as two."""
        self.assertEqual(self.order({"0011": [("0099", False)]}, {"0011": "proposed"}), [])


class TheCycleFinder(unittest.TestCase):
    def test_a_chain_is_not_a_cycle(self):
        self.assertIsNone(find_cycle({"a": {"b"}, "b": {"c"}}))

    def test_a_diamond_is_not_a_cycle(self):
        self.assertIsNone(find_cycle({"a": {"b", "c"}, "b": {"d"}, "c": {"d"}}))

    def test_the_cycle_is_returned_as_the_path_that_closes_it(self):
        found = find_cycle({"a": {"b"}, "b": {"c"}, "c": {"a"}})
        self.assertIsNotNone(found)
        self.assertEqual(found[0], found[-1])

    def test_a_cycle_is_found_even_when_it_is_not_reachable_from_the_first_node(self):
        self.assertIsNotNone(find_cycle({"a": {"b"}, "y": {"z"}, "z": {"y"}}))


if __name__ == "__main__":
    unittest.main()
