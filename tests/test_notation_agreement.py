"""The envelope every knowledge profile writes in, held to one declaration.

A profile decides which kinds exist and what each demands of its own content. The envelope — `id`,
`title`, `origin`, `gaps`, `sources` and the rest — is not its to decide, and while three profiles
shipped they carried it three times.

The measurement that made this worth a check: stripped of annotations, two of those three differed in
exactly four places, and every one carried completeness rather than vocabulary. Everything else was the
same assertions written down more than once, with nothing holding the copies together. Two have since
been retired with the vocabulary they spelled, and the envelope did not go with them — which is what a
declaration separate from the files is for.

What is asserted here is the check itself, not the schemas: that it passes over the tree as it
stands, and that each way a profile could drift is a way it reports. A check nobody can make fail is
a check that proves nothing about the day it stops looking.
"""

from __future__ import annotations

import contextlib
import io
import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import check_notation_agreement as agreement  # noqa: E402

NOTATION = REPO_ROOT / "schemas" / "knowledge-notation.json"
SHIPPED_SCHEMAS = REPO_ROOT / "src" / "claude" / "schemas"


def envelope() -> dict:
    return json.loads(NOTATION.read_text())["envelope"]


def profile(name: str) -> dict:
    return json.loads((SHIPPED_SCHEMAS / name).read_text())


class TheDeclaration(unittest.TestCase):
    def test_it_is_not_a_contract_and_says_so(self) -> None:
        """Nothing declares `knowledge-notation/N`, so nothing may look for one."""
        document = json.loads(NOTATION.read_text())
        self.assertNotIn("properties", document, "a top-level `properties` would read as a schema")
        self.assertIn("$comment", document)
        self.assertIn("NOT a contract", document["$comment"])

    def test_the_contract_check_exempts_it(self) -> None:
        import check_contract_versions as versions

        self.assertIn("knowledge-notation.json", versions.NOT_A_CONTRACT)

    def test_it_does_not_ship(self) -> None:
        """It is the generator's bookkeeping. `src/claude/` is the only tree that reaches anyone."""
        self.assertFalse((SHIPPED_SCHEMAS / "knowledge-notation.json").exists())

    def test_the_envelope_names_what_a_profile_still_defines(self) -> None:
        self.assertEqual(["type", "contract_version"], envelope()["required_keys"])


class ItPasses(unittest.TestCase):
    def test_every_shipped_profile_agrees(self) -> None:
        for name in agreement.PROFILES:
            with self.subTest(profile=name):
                self.assertEqual([], agreement.disagreements(profile(name), envelope(), name))

    def test_the_envelope_outlived_the_profiles_that_carried_it(self) -> None:
        """What the declaration bought, asserted rather than remembered.

        Three profiles carried this envelope when it was written down; two were retired with the
        vocabulary they spelled. The envelope survived because it was stated somewhere other than in
        the files that went — which is the whole of what a separate declaration is for.
        """
        self.assertEqual(("domain-object.json",), agreement.PROFILES)
        for gone in ("knowledge-object.json", "staged-knowledge-object.json"):
            with self.subTest(retired=gone):
                self.assertFalse((SHIPPED_SCHEMAS / gone).exists())
        self.assertGreaterEqual(len(envelope()["properties"]), 18)


class ItFails(unittest.TestCase):
    """Each way a profile can drift, and the report it produces."""

    def setUp(self) -> None:
        self.envelope = envelope()
        self.profile = profile("domain-object.json")

    def report(self) -> str:
        return " ".join(agreement.disagreements(self.profile, self.envelope, "profile.json"))

    def test_a_dropped_envelope_field_is_reported(self) -> None:
        del self.profile["properties"]["sources"]
        self.assertIn("`sources` is absent", self.report())

    def test_a_changed_assertion_is_reported(self) -> None:
        self.profile["properties"]["out_of_scope"]["minItems"] = 0
        self.assertIn("asserts something the notation does not", self.report())

    def test_a_reworded_description_is_not_reported(self) -> None:
        """A profile words a field for its own readers; only the assertions have to agree."""
        self.profile["properties"]["sources"]["description"] = "Where this came from."
        self.assertEqual([], agreement.disagreements(self.profile, self.envelope, "profile.json"))

    def test_a_missing_profile_key_is_reported(self) -> None:
        del self.profile["properties"]["contract_version"]
        self.assertIn("`contract_version` is absent", self.report())

    def test_a_changed_shared_def_is_reported(self) -> None:
        self.profile["$defs"]["gap"]["required"] = []
        self.assertIn("`$defs.gap` asserts something", self.report())

    def test_closing_the_object_is_reported(self) -> None:
        """R30 requires an unknown field to be preserved, which is why the envelope is open."""
        self.profile["additionalProperties"] = False
        self.assertIn("`additionalProperties`", self.report())

    def test_a_profile_named_and_absent_is_reported(self) -> None:
        """A check that quietly stops checking is what this file exists to prevent."""
        original = agreement.PROFILES
        agreement.PROFILES = ("does-not-exist.json",)
        spoken = io.StringIO()
        try:
            with contextlib.redirect_stdout(spoken):
                code = agreement.main()
        finally:
            agreement.PROFILES = original
        self.assertEqual(1, code)
        self.assertIn("does-not-exist.json", spoken.getvalue())
