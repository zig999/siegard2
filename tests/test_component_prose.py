"""C01 through C04 — and proof that each one fails.

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
        cp.check_selectability(self.root, findings)
        cp.check_named_scripts(self.root, findings)
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
        self.assertEqual(5, len(with_output & on_disk))


class C01(Case):
    """A field the prose names must exist in a contract the component declares."""

    def test_the_original_defect_is_caught(self) -> None:
        """`impact-analyst` told its producer to record an ambiguity in a field the contract lacks.

        The field it originally named was `notes`, and that stopped being unknown: the agent
        declares `domain-model/2` as an input and the model carries a top-level `notes`, so the
        vocabulary C01 builds legitimately holds it. The token here is one no contract this agent
        declares or cites has — which is what the rule is about, not which word was used.
        """
        self.rewrite(
            "agents/impact-analyst.md",
            "resolve toward the verdict whose implicated set is the",
            "record the reading you did not take in `superseded_by`, and resolve toward the verdict whose is the",
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
            "agents/knowledge-author.md",
            "## Result",
            '## Result\n\n```json\n{"contract_version": "knowledge-authoring-result/1"}\n```\n',
        )
        self.assertIn("C02", self.rules())

    def test_an_example_that_does_not_conform_is_caught(self) -> None:
        self.rewrite("agents/domain-modeler.md", '"state": "modeled"', '"state": "partially-modeled"')
        self.assertIn("C02", self.rules())

    def test_an_example_that_is_not_json_is_caught(self) -> None:
        self.rewrite("agents/knowledge-author.md", '"state": "authored"', '"state": authored')
        self.assertIn("C02", self.rules())


class C03(Case):
    """An agent's description states a prerequisite a selector can evaluate.

    A first form of this rule asked whether any skill named the agent, and that was the wrong criterion
    in both directions. `foundation/0005` R3 puts selection with the model; every shipped skill declares
    `disable-model-invocation` because each writes outside the session; so agents are the only layer a
    selector reaches, and what decides selectability is the description — the declaration does not reach
    the distribution.
    """

    CLAUSE = "Delegate when a request describes a problem or a solution and no domain model exists yet."

    def test_a_phase_routed_delegation_is_caught(self) -> None:
        """The shape four agents carried until the phase order became guidance."""
        self.rewrite(
            "agents/domain-modeler.md",
            self.CLAUSE,
            "Delegate at the modelling phase of a knowledge change workflow.",
        )
        findings = self.findings()
        self.assertIn("C03", {f.split(None, 1)[0] for f in findings})
        self.assertTrue(any("a moment rather" in f for f in findings))

    def test_a_workflow_routed_delegation_is_caught(self) -> None:
        self.rewrite(
            "agents/domain-modeler.md", self.CLAUSE, "Delegate when a workflow needs a domain modelled."
        )
        self.assertIn("C03", self.rules())

    def test_an_artifact_routed_delegation_passes(self) -> None:
        """Otherwise the two above could be passing because every clause is rejected."""
        self.rewrite(
            "agents/domain-modeler.md",
            self.CLAUSE,
            "Delegate once a change request exists and no domain model has been produced for it.",
        )
        self.assertNotIn("C03", self.rules())

    def test_a_description_with_no_delegation_clause_is_caught(self) -> None:
        """A selector told what an agent does and never when to choose it cannot choose it."""
        self.rewrite("agents/domain-modeler.md", self.CLAUSE, "It is the modelling agent.")
        self.assertTrue(any("states no `Delegate" in f for f in self.findings()))

    def test_every_committed_agent_says_when_to_choose_it(self) -> None:
        self.assertNotIn("C03", self.rules())


class C04(Case):
    """A component that tells its executor to run a shipped script names the script."""

    def test_an_unnamed_script_is_caught(self) -> None:
        """The original defect: `Run the knowledge validator` names no file a consumer can resolve.

        Planted rather than mutated. The instruction it was found in — a skill telling its executor
        to run `bin/validate_knowledge.py` — went with the shipped executables, so there is nothing
        left in the tree to break. The rule itself is unchanged and fires the same way.
        """
        path = self.root / "skills" / "ingest-domain" / "SKILL.md"
        path.write_text(path.read_text() + "\nRun the knowledge validator over the base.\n")
        findings = self.findings()
        self.assertIn("C04", {f.split(None, 1)[0] for f in findings})
        self.assertTrue(any("names no shipped script" in f for f in findings))

    def test_naming_the_script_passes(self) -> None:
        self.assertNotIn("C04", self.rules())

    def test_every_exempt_name_is_a_file_that_ships(self) -> None:
        """The exempt set must name real files, or the exemption drifts into covering nothing.

        It held four library modules while the generation path shipped them, and emptied when they
        went. The expansion step is a *runnable* script rather than a library, so it is not exempt
        and the set stays empty — but the assertion is now about the set matching the tree rather
        than about the tree being empty, which is what survives the next module either way.
        """
        on_disk = {p.name for p in (self.root / "bin").glob("*.py")}
        self.assertEqual(set(), cp.LIBRARIES - on_disk)
