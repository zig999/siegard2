"""C01, C02, C03 — and proof that each one fails.

The committed tree is asserted clean beside every rejection, for the reason `tests/support.py` records
about the knowledge fixture: a rejection test alone cannot tell a working check from one that rejects
everything, and a passing check alone cannot tell a working check from one that can never fire. Both
matter more than usual here, because every finding these rules exist for was found by hand first — and
a rule that silently stops firing returns the repository to finding them by hand.

Each mutation is made on a disposable copy of the real tree, so the assertions run against the real
components rather than against a fixture that could drift from them.
"""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

import check_component_prose as cp

from tests.support import REPO_ROOT

SOURCE = REPO_ROOT / "src" / "claude"


class Case(unittest.TestCase):
    def setUp(self) -> None:
        holder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, holder, True)
        self.root = Path(holder) / "claude"
        shutil.copytree(SOURCE, self.root, ignore=shutil.ignore_patterns("__pycache__"))

    def findings(self) -> list[str]:
        findings: list[str] = []
        entries = {e["identifier"]: e for e in cp.load(self.root / cp.DECLARATION)["declarations"]}
        for path in sorted((self.root / "agents").glob("*.md")):
            entry = entries.get(path.stem)
            if entry is not None:
                cp.check_fields(self.root, entry, path, findings)
        cp.check_reachability(self.root, findings)
        return findings

    def rules(self) -> set[str]:
        return {f.split(None, 1)[0] for f in self.findings()}

    def rewrite(self, relative: str, old: str, new: str) -> None:
        path = self.root / relative
        text = path.read_text()
        self.assertIn(old, text, f"{relative} no longer holds the text this test mutates")
        path.write_text(text.replace(old, new, 1))


class TheRealTree(Case):
    def test_it_is_clean(self) -> None:
        self.assertEqual([], self.findings())

    def test_every_agent_with_an_output_contract_is_checked(self) -> None:
        """A rule that skipped an agent would pass by not looking."""
        entries = {e["identifier"]: e for e in cp.load(self.root / cp.DECLARATION)["declarations"]}
        with_output = {
            name for name, e in entries.items()
            if e["class"] == "specialized-agent" and e.get("outputs")
        }
        on_disk = {p.stem for p in (self.root / "agents").glob("*.md")}
        self.assertEqual(with_output, with_output & on_disk)
        self.assertEqual(7, len(with_output & on_disk))


class C01(Case):
    """A field the prose names must exist in a contract the component declares."""

    def test_the_original_defect_is_caught(self) -> None:
        """`impact-analyst` told its producer to record an ambiguity in a field the contract lacks."""
        self.rewrite(
            "agents/impact-analyst.md",
            "resolve toward the verdict whose implicated set is the",
            "record the reading you did not take in `notes`, and resolve toward the verdict whose is the",
        )
        self.assertIn("C01", self.rules())

    def test_an_enum_value_is_not_reported(self) -> None:
        """Prose legitimately names a state or a verdict; the first form of C01 flagged every one."""
        self.rewrite(
            "agents/domain-modeler.md",
            "You model a domain.",
            "You model a domain. A `blocked` result models nothing, and `stated` is not `modeled`.",
        )
        self.assertNotIn("C01", self.rules())

    def test_citing_a_schema_admits_its_vocabulary(self) -> None:
        """How `domain-analyst` legitimately speaks in ontology field names."""
        self.rewrite(
            "agents/domain-modeler.md",
            "You model a domain.",
            "You model a domain. See `schemas/knowledge-object.json` for `out_of_scope`.",
        )
        self.assertNotIn("C01", self.rules())

    def test_a_field_of_an_undeclared_contract_is_reported(self) -> None:
        """Neither declared nor cited: the check cannot tell an invention from a missing declaration."""
        self.rewrite(
            "agents/domain-modeler.md",
            "You model a domain.",
            "You model a domain. Record it under `superseded_by`.",
        )
        self.assertIn("C01", self.rules())


class C02(Case):
    """A component carries one worked example, and it conforms to its output contract."""

    def test_a_missing_example_is_caught(self) -> None:
        path = self.root / "agents" / "domain-modeler.md"
        body = path.read_text()
        start = body.index("```json")
        end = body.index("```", start + 7) + 3
        path.write_text(body[:start] + body[end:])
        self.assertIn("C02", self.rules())

    def test_a_second_example_is_caught(self) -> None:
        """Two examples are two shapes to imitate."""
        self.rewrite(
            "agents/concept-author.md",
            "## Result",
            '## Result\n\n```json\n{"contract_version": "concept-authoring-result/1"}\n```\n',
        )
        self.assertIn("C02", self.rules())

    def test_an_example_that_does_not_conform_is_caught(self) -> None:
        self.rewrite("agents/domain-modeler.md", '"state": "modeled"', '"state": "partially-modeled"')
        self.assertIn("C02", self.rules())

    def test_an_example_that_is_not_json_is_caught(self) -> None:
        self.rewrite("agents/concept-author.md", '"state": "authored"', '"state": authored')
        self.assertIn("C02", self.rules())


class C03(Case):
    """An agent no skill names is unreachable."""

    def test_an_unrecorded_unreachable_agent_is_caught(self) -> None:
        """`domain-modeler` is reached by `model-domain`; cut the link and it must be reported."""
        self.rewrite("skills/model-domain/SKILL.md", "domain-modeler", "the modelling agent")
        findings = self.findings()
        self.assertIn("C03", {f.split(None, 1)[0] for f in findings})
        self.assertTrue(any("domain-modeler" in f for f in findings))

    def test_a_recorded_debt_passes_and_is_returned_for_printing(self) -> None:
        """Four agents are unreachable today. A recorded debt is not a pass in silence."""
        findings: list[str] = []
        recorded = cp.check_reachability(self.root, findings)
        self.assertEqual([], findings)
        self.assertEqual(len(cp.UNREACHABLE), len(recorded))

    def test_every_recorded_entry_carries_a_reason(self) -> None:
        for agent, reason in cp.UNREACHABLE.items():
            with self.subTest(agent=agent):
                self.assertTrue(reason.strip(), agent)
                self.assertGreater(len(reason), 40, "a reason short enough to be a label is not one")

    def test_no_recorded_entry_is_stale(self) -> None:
        """An agent that gained a caller must leave the table, or the debt outlives the defect."""
        skills = list((self.root / "skills").glob("*/SKILL.md"))
        for agent in cp.UNREACHABLE:
            with self.subTest(agent=agent):
                self.assertFalse(
                    any(agent in s.read_text() for s in skills),
                    f"{agent} is now invoked by a skill and must leave UNREACHABLE",
                )

    def test_every_recorded_entry_names_an_agent_that_exists(self) -> None:
        on_disk = {p.stem for p in (self.root / "agents").glob("*.md")}
        self.assertEqual(set(), set(cp.UNREACHABLE) - on_disk)
