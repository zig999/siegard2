"""Capability lifecycle and shipped thresholds — the two rules that were maintained by reading.

`foundation/0006` R17 requires a capability's status to be derived from checkable facts "and not from a
label maintained by hand", and `foundation/0008` R12 puts that status in the one record a consumer is
told to trust. `foundation/0006` R19 refuses a shipped numeric threshold with no evidence behind it, and
R20 names the failure it prevents: a value chosen once to get a first run moving becoming a default
nobody decided to ship.

Both were prose until `scripts/check_capabilities.py`.
"""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

import check_capabilities as cc
import generate_dist

REPO_ROOT = Path(__file__).resolve().parent.parent
DIST = REPO_ROOT / "dist" / ".claude"


class DerivedStatus(unittest.TestCase):
    """foundation/0006 R17."""

    def test_the_installed_statuses_agree_with_what_the_facts_derive(self) -> None:
        self.assertEqual([], cc.check_statuses(DIST))

    def test_every_installed_capability_is_active_or_deprecated(self) -> None:
        """R14: `proposed` ships nothing and `retired` is absent, so an installation holds neither.

        This required `active` of everything, and was true for as long as `deprecated` had no
        mechanism — the generator wrote the label and the label was always the same one. It fails
        the moment a real deprecation lands, which is what it is for.
        """
        for name, status in cc.installed_statuses(DIST).items():
            with self.subTest(capability=name):
                self.assertIn(status, ("active", "deprecated"))

    def test_a_hand_edited_status_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as holder:
            copy = Path(holder) / "dist"
            shutil.copytree(DIST, copy)
            manifest_path = copy / generate_dist.MANIFEST_NAME
            manifest = json.loads(manifest_path.read_text())
            manifest["capabilities"][0]["status"] = "deprecated"
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
            problems = cc.check_statuses(copy)
        self.assertTrue(any("the facts derive" in p for p in problems), problems)

    def test_a_status_no_fact_supports_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as holder:
            copy = Path(holder) / "dist"
            shutil.copytree(DIST, copy)
            manifest_path = copy / generate_dist.MANIFEST_NAME
            manifest = json.loads(manifest_path.read_text())
            manifest["capabilities"].append(
                {"name": "invented", "class": "skill", "status": "active", "path": "skills/x/SKILL.md"}
            )
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
            problems = cc.check_statuses(copy)
        self.assertTrue(any("derivable from nothing" in p for p in problems), problems)

    def test_a_retired_capability_may_not_appear_in_an_installation(self) -> None:
        with tempfile.TemporaryDirectory() as holder:
            copy = Path(holder) / "dist"
            shutil.copytree(DIST, copy)
            manifest_path = copy / generate_dist.MANIFEST_NAME
            manifest = json.loads(manifest_path.read_text())
            manifest["capabilities"][0]["status"] = "retired"
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
            problems = cc.check_statuses(copy)
        self.assertTrue(any("retired" in p and "R14" in p for p in problems), problems)

    def test_which_capability_classes_are_occupied(self) -> None:
        """Which of the six classes the distribution fills, recorded so a change is noticed.

        This required at least four, citing a condition in a specification that no longer exists —
        and the fixture each was to be evidenced by went with
        This repository keeps no fixture. Three are filled today, `script` having joined when the expansion step shipped — and this test is what noticed. Hook, script,
        template, and target pack are open and empty; `foundation/0005` R2 removes a class rather
        than keeping it open, and these stay because the *class* is occupied elsewhere in the
        model — what is empty is this distribution's share of it.
        """
        manifest = json.loads((DIST / generate_dist.MANIFEST_NAME).read_text())
        self.assertEqual({"skill", "specialized-agent", "script"},
                         {c["class"] for c in manifest["capabilities"]})


class DeprecationIsDerived(unittest.TestCase):
    """`foundation/0005` R17: a status comes from checkable facts, never from a label.

    Two facts, and the generator reads both: whether the distribution installs the capability, and
    whether its declaration documents it as going away. Nothing writes `deprecated` anywhere — what
    a person writes is the replacement and the reason, and the status follows from their presence.

    This fails against the old behavior in the way the compatibility rule asks for: before the
    declaration could carry a deprecation, every installed capability derived `active`, and R15's
    move through `deprecated` had no mechanism at all.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads((DIST / generate_dist.MANIFEST_NAME).read_text())
        cls.declarations = {
            entry["identifier"]: entry
            for entry in json.loads(
                (REPO_ROOT / "src" / "claude" / "capabilities.declaration.json").read_text()
            )["declarations"]
        }

    def statuses(self) -> dict[str, str]:
        return {c["name"]: c["status"] for c in self.manifest["capabilities"]}

    def test_a_capability_with_a_declared_deprecation_derives_deprecated(self) -> None:
        for name, entry in self.declarations.items():
            if entry.get("deprecation"):
                with self.subTest(capability=name):
                    self.assertEqual("deprecated", self.statuses().get(name))

    def test_a_capability_without_one_derives_active(self) -> None:
        for name, status in self.statuses().items():
            if not self.declarations.get(name, {}).get("deprecation"):
                with self.subTest(capability=name):
                    self.assertEqual("active", status)

    def test_the_word_deprecated_is_written_nowhere_in_the_source(self) -> None:
        """The label is derived. A file carrying it would be the hand-maintained status R17 forbids."""
        source = REPO_ROOT / "src" / "claude" / "capabilities.declaration.json"
        self.assertNotIn("deprecated", source.read_text())

    def test_a_deprecation_names_its_replacement(self) -> None:
        """R15: a consumer told a capability is going away and not what replaces it has half a migration."""
        for name, entry in self.declarations.items():
            deprecation = entry.get("deprecation")
            if deprecation:
                with self.subTest(capability=name):
                    self.assertTrue(deprecation["replacement"])
                    self.assertTrue(deprecation["reason"])

    def test_a_deprecated_capability_is_still_installed(self) -> None:
        """R14: `deprecated` is installed and going away; absent is `retired`, which is a later move."""
        installed = {c["name"] for c in self.manifest["capabilities"]}
        for name, entry in self.declarations.items():
            if entry.get("deprecation"):
                with self.subTest(capability=name):
                    self.assertIn(name, installed)

    def test_the_replacement_it_names_is_itself_installed(self) -> None:
        """A replacement nothing installs is a migration path with no destination."""
        installed = {c["name"] for c in self.manifest["capabilities"]}
        for name, entry in self.declarations.items():
            deprecation = entry.get("deprecation")
            if deprecation and deprecation["replacement"] in self.declarations:
                with self.subTest(capability=name):
                    self.assertIn(deprecation["replacement"], installed)


class Thresholds(unittest.TestCase):
    """foundation/0006 R21 and R20."""

    def test_the_distribution_ships_no_uncalibrated_threshold(self) -> None:
        self.assertEqual([], cc.check_thresholds(DIST))

    def test_a_bare_threshold_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as holder:
            copy = Path(holder) / "dist"
            shutil.copytree(DIST, copy)
            (copy / "schemas" / "eager.py").write_text("RETRY_COUNT = 3\n")
            problems = cc.check_thresholds(copy)
        self.assertTrue(any("eager.py" in p for p in problems), problems)

    def test_an_underscore_separated_number_is_not_missed(self) -> None:
        """`10_000` read as `10` was a real near-miss in this check's first draft."""
        with tempfile.TemporaryDirectory() as holder:
            copy = Path(holder) / "dist"
            shutil.copytree(DIST, copy)
            (copy / "schemas" / "eager.py").write_text("BUDGET = 12_000\n")
            problems = cc.check_thresholds(copy)
        self.assertTrue(any("12_000" in p for p in problems), problems)

    def test_every_exemption_carries_its_evidence(self) -> None:
        """R19 admits a shipped value only with the evidence that calibrated it.

        Two shapes of evidence, and the second was reached the hard way. A value this framework
        chose cites the requirement that fixed it. A value the *harness* imposes cites the harness's
        own documentation — which is the source `CLAUDE.md` demands for any dependency on Claude
        Code behaviour, and which one threshold reached only through a decision record that cited it
        for us. The record went; the documentation is where the number was all along.
        """
        for field, reason in cc.CALIBRATED.items():
            self.assertTrue(reason.strip(), field)
            self.assertTrue(
                "foundation/" in reason or reason.startswith("https://"),
                f"{field}: {reason!r} cites neither a requirement nor a documentation page",
            )

    def test_a_caller_supplied_value_is_not_a_framework_threshold(self) -> None:
        """R20's other route: a value the caller states is not a threshold the framework ships.

        Read off the declaration of `ingest-domain`, whose `system_defaults` is the clearest live
        instance: the body-line ceiling and the three attribute defaults are facts about a
        repository, and the declared behaviour on their absence is to stop rather than to choose
        one. A framework that picked a value here would be shipping the uncalibrated threshold R19
        refuses.
        """
        declarations = json.loads(
            (REPO_ROOT / "src" / "claude" / "capabilities.declaration.json").read_text()
        )["declarations"]
        entry = next(d for d in declarations if d["identifier"] == "ingest-domain")
        defaults = next(i for i in entry["inputs"] if i["name"] == "system_defaults")
        self.assertFalse(defaults["required"])
        self.assertIn("stops rather than choosing", defaults["default"])


class ShippedSkills(unittest.TestCase):
    """`skills/upgrade/` stood here and does not ship; what it was checked for still applies.

    Two of its three tests asserted that one named skill exists and declares itself
    non-model-invocable. The third asked the same of every skill that ships, which is the
    assertion that survives a skill being removed — and it is the one kept.
    """

    def test_every_shipped_skill_with_outside_effects_says_so(self) -> None:
        from frontmatter_lib import split_frontmatter

        for path in sorted((DIST / "skills").glob("*/SKILL.md")):
            data, _ = split_frontmatter(path.read_text())
            self.assertTrue(data.get("disable-model-invocation"), path.parent.name)


if __name__ == "__main__":
    unittest.main()


class Retirement(unittest.TestCase):
    """`foundation/0005` R14 through R16, exercised against constructed sequences.

    Nothing in the framework has needed to be retired yet, and retiring something to demonstrate
    retirement would manufacture the evidence rather than produce it. What is asserted is the
    mechanism: an invalid sequence is reported, and the migration below fails against the old
    behavior — the clause R16 states, which no amount of recorded history would satisfy on its own.

    Three tests here read `fixtures/lifecycle-retirement/releases.json` and went with it when
    `fixtures/` was removed. Each asserted that a recorded sequence was well-formed, which the
    constructed cases below already cover from both directions; what the recording added was a
    claim that some release had happened, and none had.
    """

    def test_skipping_deprecated_is_reported(self) -> None:
        problems = cc.check_release_sequence(
            [{"version": "0.1.0", "status": "active"},
             {"version": "0.2.0", "status": "retired", "migration": "x"}]
        )
        self.assertTrue(any("R15" in p for p in problems), problems)

    def test_a_deprecation_naming_no_replacement_is_reported(self) -> None:
        problems = cc.check_release_sequence([{"version": "0.2.0", "status": "deprecated"}])
        self.assertTrue(any("replacement" in p for p in problems), problems)

    def test_a_retirement_with_no_migration_is_reported(self) -> None:
        problems = cc.check_release_sequence(
            [{"version": "0.2.0", "status": "deprecated", "replacement": "report"},
             {"version": "0.3.0", "status": "retired", "replacement": "report"}]
        )
        self.assertTrue(any("R16" in p for p in problems), problems)

    def test_the_lifecycle_does_not_run_backwards(self) -> None:
        problems = cc.check_release_sequence(
            [{"version": "0.2.0", "status": "deprecated", "replacement": "report"},
             {"version": "0.3.0", "status": "active"}]
        )
        self.assertTrue(any("backwards" in p for p in problems), problems)

    def test_the_migration_fails_against_the_old_behavior(self) -> None:
        """R16's own clause, and the reason this is a test rather than a recorded claim.

        The retired capability answered with a bare string; its replacement answers with the
        structured result the rest of the framework consumes. A migration that returned its input
        unchanged would pass a test asserting only that the new shape works — so the assertion
        that matters is that the *old* behavior no longer satisfies the new consumer.
        """

        def old_behavior(request: str) -> str:
            return f"report for {request}"

        def migrate(legacy: str) -> dict:
            return {"contract_version": "report/1", "summary": legacy}

        def new_consumer(result) -> str:
            if not isinstance(result, dict) or result.get("contract_version") != "report/1":
                raise TypeError("report/1 expected")
            return result["summary"]

        legacy = old_behavior("invoices")
        with self.assertRaises(TypeError):
            new_consumer(legacy)
        self.assertEqual(legacy, new_consumer(migrate(legacy)))
