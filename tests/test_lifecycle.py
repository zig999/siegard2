"""Capability lifecycle and shipped thresholds — the two rules that were maintained by reading.

`specs/0006` R17 requires a capability's status to be derived from checkable facts "and not from a
label maintained by hand", and `specs/0008` R12 puts that status in the one record a consumer is
told to trust. `specs/0007` R19 refuses a shipped numeric threshold with no evidence behind it, and
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
    """specs/0006 R17."""

    def test_the_installed_statuses_agree_with_what_the_facts_derive(self) -> None:
        self.assertEqual([], cc.check_statuses(DIST))

    def test_every_installed_capability_is_active(self) -> None:
        """R14: proposed ships nothing and retired is absent from the distribution."""
        for name, status in cc.installed_statuses(DIST).items():
            self.assertEqual("active", status, name)

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

    def test_four_capability_classes_are_occupied(self) -> None:
        """specs/0006 condition 1: at least four classes, each with a fixture."""
        manifest = json.loads((DIST / generate_dist.MANIFEST_NAME).read_text())
        self.assertGreaterEqual(len({c["class"] for c in manifest["capabilities"]}), 4)


class Thresholds(unittest.TestCase):
    """specs/0007 R19 and R20."""

    def test_the_distribution_ships_no_uncalibrated_threshold(self) -> None:
        self.assertEqual([], cc.check_thresholds(DIST))

    def test_a_bare_threshold_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as holder:
            copy = Path(holder) / "dist"
            shutil.copytree(DIST, copy)
            (copy / "bin" / "eager.py").write_text("RETRY_COUNT = 3\n")
            problems = cc.check_thresholds(copy)
        self.assertTrue(any("eager.py" in p for p in problems), problems)

    def test_an_underscore_separated_number_is_not_missed(self) -> None:
        """`10_000` read as `10` was a real near-miss in this check's first draft."""
        with tempfile.TemporaryDirectory() as holder:
            copy = Path(holder) / "dist"
            shutil.copytree(DIST, copy)
            (copy / "bin" / "eager.py").write_text("BUDGET = 12_000\n")
            problems = cc.check_thresholds(copy)
        self.assertTrue(any("12_000" in p for p in problems), problems)

    def test_every_exemption_carries_its_evidence(self) -> None:
        """R19 admits a shipped value only with the evidence that calibrated it."""
        for field, reason in cc.CALIBRATED.items():
            self.assertTrue(reason.strip(), field)
            self.assertTrue(
                "specs/" in reason or "ADR-" in reason,
                f"{field}: {reason!r} cites no requirement",
            )

    def test_a_caller_supplied_value_is_not_a_framework_threshold(self) -> None:
        """R20's other route: the attempt limit comes from the workflow's opening event."""
        log = REPO_ROOT / "fixtures" / "knowledge-change-loop" / "inputs" / "events" / "01-change-request.json"
        self.assertIn("attempt_limit", json.loads(log.read_text()))


class UpgradeSkill(unittest.TestCase):
    def test_it_ships(self) -> None:
        self.assertTrue((DIST / "skills" / "upgrade" / "SKILL.md").is_file())

    def test_it_is_not_model_invocable(self) -> None:
        """specs/0006 R4: a skill whose effects reach outside the session says so."""
        from frontmatter_lib import split_frontmatter

        data, _ = split_frontmatter((DIST / "skills" / "upgrade" / "SKILL.md").read_text())
        self.assertTrue(data.get("disable-model-invocation"))

    def test_every_shipped_skill_with_outside_effects_says_so(self) -> None:
        from frontmatter_lib import split_frontmatter

        for path in sorted((DIST / "skills").glob("*/SKILL.md")):
            data, _ = split_frontmatter(path.read_text())
            self.assertTrue(data.get("disable-model-invocation"), path.parent.name)


if __name__ == "__main__":
    unittest.main()


class RecordedUpgradeOutcomes(unittest.TestCase):
    """`fixtures/upgrade-run/`: three outcomes, reproduced rather than remembered.

    The skill drives `scripts/install_dist.py`, so what a fixture can hold is the outcome each
    situation must produce. Recording them as data rather than as prose is also what admits the
    skill: `specs/0006` R11 makes a fixture the thing that turns an intention into a capability,
    and R14 keeps an unexercised one out of the distribution entirely.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.recipe = json.loads((REPO_ROOT / "fixtures" / "upgrade-run" / "run.json").read_text())

    def setUp(self) -> None:
        import install_dist

        self.install_dist = install_dist
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        self.project = Path(holder.name) / "consumer"
        self.plugin = self.project / ".claude" / "plugins" / "siegard"
        self.project.mkdir(parents=True)
        self.install_dist.write(DIST, self.plugin)

    def case(self, name: str) -> dict:
        return next(c for c in self.recipe["cases"] if c["name"] == name)

    def test_same_version_is_a_no_op(self) -> None:
        case = self.case("same-version")
        before = self.install_dist.tree(self.plugin)
        self.assertEqual([], self.install_dist.divergences(self.plugin))
        self.assertEqual(before, self.install_dist.tree(self.plugin))
        self.assertEqual("no-op", case["expected_outcome"])

    def test_local_divergence_is_detected_and_named(self) -> None:
        case = self.case("local-divergence")
        target = self.plugin / case["diverge"]
        target.write_text(target.read_text() + "\n<!-- the repository's own note -->\n")
        found = self.install_dist.divergences(self.plugin)
        self.assertTrue(any(case["expected_marker"] in note for note in found), found)
        self.assertTrue(any(case["diverge"] in note for note in found), found)

    def test_a_shadowed_agent_is_reported(self) -> None:
        case = self.case("shadowed-agent")
        agents = self.project / ".claude" / "agents"
        agents.mkdir(parents=True, exist_ok=True)
        (agents / f"{case['shadow']}.md").write_text(
            f"---\nname: {case['shadow']}\ndescription: The repository's own.\ntools: Read\n---\n\nLocal.\n"
        )
        found = self.install_dist.shadowed(self.plugin, self.project)
        self.assertTrue(any(case["expected_marker"] in note for note in found), found)

    def test_every_recorded_case_cites_a_requirement(self) -> None:
        for case in self.recipe["cases"]:
            self.assertRegex(case["requirement"], r"^specs/\d{4} R\d+$")

    def test_every_recorded_case_has_a_test(self) -> None:
        """A case in the fixture with nothing reproducing it is a claim, not evidence."""
        covered = {"same-version", "local-divergence", "shadowed-agent"}
        self.assertEqual(covered, {case["name"] for case in self.recipe["cases"]})
