"""Every scaffold in `templates/`, expanded and validated against the contract it names.

`CLAUDE.md` gives `templates/` the role "artifact generators that conform to schemas".
`docs/concepts/scaffold.md` records what that is and what it is not — a scaffold is not a
template in the sense of `foundation/0011`, which expands domain knowledge into an artifact class
from the closed vocabulary of `foundation/0004` R8 and holds byte identity.

What the two share is enforced here: output validates before it is written, and nothing is
minted. Every placeholder is required, so a scaffold cannot quietly supply a timestamp, an
identifier, or a version — the values a caller owns and `foundation/0011` R5 forbids a generator
from inventing.

Each kind gets a full expansion with plausible values and an assertion that the result passes
its real contract. A scaffold that produced a skeleton failing validation would put the author
in the worst position: a file that looks finished and fails later, with no way to tell which
part was the scaffold's fault.
"""

from __future__ import annotations

import ast
import json
import tempfile
import unittest
from pathlib import Path

import scaffold

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_SHIPPED = REPO_ROOT / "src" / "claude" / "templates"
TEMPLATES_GENERATOR = REPO_ROOT / "templates"

STAMP = {"generated_by": "claude-opus-5", "generated_at": "2026-07-31T10:00:00Z"}
# `domain-object/1` requires `origin`, so every domain-object case supplies one.
# `modeled` rather than `stated`: these are invented examples, and a case claiming the
# business stated it would be the false claim the field exists to prevent.
ORIGIN = {"origin": "modeled"}

# One plausible value per placeholder, per kind. Deliberately verbose rather than generated:
# a value that happened to satisfy a pattern by accident would make a green test meaningless.
CASES: dict[str, dict[str, str]] = {
    "knowledge-system": {
        "timezone": "America/Sao_Paulo",
        "currency": "BRL",
        "identity_strategy": "surrogate",
        # The ceiling's *value* is still deferred to measurement; that it is supplied rather than
        # defaulted is the part under test here.
        "body_lines": "24",
    },
    "specification": {
        "id": "0099",
        "title": "Decide one thing, and make the deciding checkable",
        "short_title": "A worked example",
        "scope": "what a scaffolded specification looks like before anyone has written one",
        "decides": "nothing; it is a skeleton",
        "decided_elsewhere": "`CLAUDE.md` **Where authority lives** fixes precedence and this does not restate it.",
        "concept_title": "specification",
        "concept_slug": "specification",
        "requirement_group": "The example",
        "requirement": "A scaffolded specification MUST be filled in before it is proposed.",
        "acceptance_condition": "Someone replaced every placeholder with a decision.",
    },
    "concept": {
        "slug": "worked-example",
        "title": "worked example",
        "description": "A filled-in skeleton used to prove a scaffold produces a conforming artifact.",
        "tag": "tooling",
        "source_resource": "CLAUDE.md",
        "source_title": "Repository layout",
        "body": "It exists to be validated, and for nothing else.",
        **STAMP,
    },
    "skill": {
        "name": "worked-example",
        "description": "Does one thing, for the purpose of proving a scaffold expands into a valid component. Use when testing the scaffold. Not for real work.",
        "purpose": "You demonstrate that the skill scaffold produces a conforming component.",
        "required_input": "the thing to demonstrate with",
        "first_step": "Read the contract before writing anything.",
        "result": "A statement that the demonstration ran.",
    },
    "agent": {
        "name": "worked-example",
        "description": "Produces one artifact, for the purpose of proving a scaffold expands into a valid component. Delegate when testing the scaffold. Not for real work.",
        "tools": "Read, Grep",
        "purpose": "You demonstrate that the agent scaffold produces a conforming component.",
        "required_input": "the thing to demonstrate with",
        "first_step": "Read the contract before writing anything.",
        "result": "One JSON object conforming to the contract named above.",
    },
    "validation-evidence": {
        "producer": "worked-example",
        "verdict": "passed",
        "request_id": "rq_7a2e4d10",
        "command": "make validate",
        "result": "pass",
        "detail": "all knowledge bases valid",
    },
    "domain-object-subdomain": {
        'slug': 'sales',
        'title': 'Sales',
        'subdomain_type': 'core',
        'description': 'Where this business wins the work it does.',
        'question': 'What is the sales subdomain?',
        'responsibility': 'how work is won, priced and committed to',
        'generated_by': 'domain-modeler',
        'generated_at': '2026-08-02T10:00:00Z',
        'origin': 'stated',
        'out_of_scope': 'How any of this is stored.',
    },
    "domain-object-context": {
        'slug': 'sales',
        'title': 'Sales',
        'subdomain_slug': 'sales',
        'description': 'The context that issues priced offers.',
        'question': 'What is the sales context?',
        'responsibility': 'issuing and tracking proposals',
        'generated_by': 'domain-modeler',
        'generated_at': '2026-08-02T10:00:00Z',
        'origin': 'stated',
        'out_of_scope': 'How any of this is stored.',
    },
    "domain-object-aggregate": {
        'context': 'sales',
        'slug': 'proposal',
        'title': 'Proposal',
        'root_slug': 'proposal',
        'description': 'The consistency boundary around a priced offer.',
        'question': 'What must stay consistent with a proposal?',
        'invariant': 'keep its total equal to the sum of its items',
        'generated_by': 'domain-modeler',
        'generated_at': '2026-08-02T10:00:00Z',
        'origin': 'stated',
        'out_of_scope': 'How any of this is stored.',
    },
    "domain-object-definition": {
        'context': 'sales',
        'slug': 'proposal',
        'title': 'Proposal',
        'boundary_slug': 'proposal',
        'ddd': 'aggregate-root',
        'attribute_name': 'number',
        'attribute_type': 'string',
        'attribute_max_length': '30',
        'description': 'A priced offer issued to a customer.',
        'question': 'What is a proposal?',
        'invariant': 'carry the number that identifies it',
        'generated_by': 'domain-modeler',
        'generated_at': '2026-08-02T10:00:00Z',
        'origin': 'stated',
        'out_of_scope': 'How any of this is stored.',
    },
    "domain-object-rule": {
        'context': 'sales',
        'slug': 'proposal-expiration',
        'title': 'Proposal expiration',
        'ddd': 'invariant',
        'statement': 'A proposal MUST NOT be accepted after its validity period has passed.',
        'expression': 'proposal.accepted_at <= proposal.valid_until',
        'description': 'When a proposal stops being acceptable.',
        'question': 'May a proposal be accepted after it expires?',
        'condition': 'An acceptance dated after the validity period is refused',
        'generated_by': 'domain-modeler',
        'generated_at': '2026-08-02T10:00:00Z',
        'origin': 'stated',
        'out_of_scope': 'How any of this is stored.',
    },
    "domain-object-lifecycle": {
        'context': 'sales',
        'slug': 'proposal',
        'title': 'Proposal lifecycle',
        'initial_state': 'draft',
        'next_state': 'issued',
        'trigger': 'issue',
        'error_slug': 'proposal-already-issued',
        'description': 'The states a proposal holds and how it moves.',
        'question': 'Which states may a proposal hold?',
        'state_meaning': 'has not reached a customer',
        'generated_by': 'domain-modeler',
        'generated_at': '2026-08-02T10:00:00Z',
        'origin': 'stated',
        'out_of_scope': 'How any of this is stored.',
    },
    "domain-object-interface": {
        'context': 'sales',
        'slug': 'proposal-accepted',
        'title': 'Proposal accepted',
        'ddd': 'domain-event',
        'version': '1',
        'schema': 'events/proposal-accepted.json',
        'ownership': 'published',
        'description': 'Announced when a customer accepts a proposal.',
        'question': 'What is published when a proposal is accepted?',
        'payload_meaning': 'the proposal number and the instant it was accepted',
        'generated_by': 'domain-modeler',
        'generated_at': '2026-08-02T10:00:00Z',
        'origin': 'stated',
        'out_of_scope': 'How any of this is stored.',
    },
    "domain-object-process": {
        'context': 'sales',
        'slug': 'issue-proposal',
        'title': 'Issue proposal',
        'ddd': 'use-case',
        'first_step_slug': 'proposal',
        'description': 'How a proposal reaches a customer.',
        'question': 'How is a proposal issued?',
        'outcome': 'a proposal a customer can accept',
        'generated_by': 'domain-modeler',
        'generated_at': '2026-08-02T10:00:00Z',
        'origin': 'stated',
        'out_of_scope': 'How any of this is stored.',
    },
    "knowledge-decision": {
        "id": "0099",
        "title": "Settle one domain question, and say what it cost",
        "context": "A consumer's decision record needs a worked example to be testable.",
        "decision": "Ship this skeleton and require it to be filled in.",
        "consequences": "An unfilled decision is visibly unfilled rather than plausibly complete.",
    },
}


class Coverage(unittest.TestCase):
    def test_every_kind_has_a_template(self) -> None:
        for kind in scaffold.SCHEMA_BY_KIND:
            self.assertTrue(scaffold.template_path(kind).is_file(), kind)

    def test_every_template_has_a_kind(self) -> None:
        """A template nothing maps to a schema would produce an unvalidated artifact."""
        present = {p.stem for p in list(TEMPLATES_SHIPPED.glob("*.md")) + list(TEMPLATES_GENERATOR.glob("*.md"))}
        self.assertEqual(present, set(scaffold.SCHEMA_BY_KIND))

    def test_every_kind_has_a_case(self) -> None:
        self.assertEqual(set(scaffold.SCHEMA_BY_KIND), set(CASES))

    def test_every_scaffold_sits_in_the_tree_its_audience_reads(self) -> None:
        """A scaffold ships exactly when the artifact it skeletons is a consumer's to author.

        This is the third form of the same check. It was a count of fourteen, which could not
        tell the two audiences apart; then a classification table in the generator, which was a
        second place for a fact the filesystem already held. The location is now the whole of
        the decision, so what is left to assert is that the two directories partition the kinds
        `scaffold.py` knows — a scaffold in neither tree, or in both, is the defect.
        """
        shipped = {p.stem for p in TEMPLATES_SHIPPED.glob("*.md")}
        generator = {p.stem for p in TEMPLATES_GENERATOR.glob("*.md")}
        self.assertEqual(set(), shipped & generator, "a scaffold sits in both trees")
        self.assertEqual(set(scaffold.SCHEMA_BY_KIND), shipped | generator)

    def test_every_json_kind_expands_to_valid_json(self) -> None:
        for kind in sorted(scaffold.JSON_KINDS):
            with self.subTest(kind=kind):
                text, problems = scaffold.expand(kind, CASES[kind])
                self.assertEqual([], problems)
                json.loads(text)

    def test_a_json_kind_carries_no_frontmatter(self) -> None:
        """The artifact's own form decides how it is parsed; a delta is an object, not a file."""
        for kind in sorted(scaffold.JSON_KINDS):
            self.assertFalse(scaffold.template_path(kind).read_text().startswith("---"), kind)


class SystemDefaults(unittest.TestCase):
    """The one kind that names no schema, checked against the validator that owns it instead.

    `conforms` returns nothing for `knowledge-system`, so the generic expansion test passes it
    vacuously. That is exactly the case where a suite can look green and assert nothing, so the
    real contract is exercised here: the knowledge materializer reads this file before any object
    loads, and the body check reads the ceiling out of it. Both are asserted rather than assumed.
    """

    def expanded(self) -> Path:
        text, problems = scaffold.expand("knowledge-system", CASES["knowledge-system"])
        self.assertEqual([], problems)
        root = Path(tempfile.mkdtemp()) / "knowledge"
        root.mkdir(parents=True)
        (root / "system.md").write_text(text)
        return root

    def test_the_expansion_names_all_three_defaults_and_the_ceiling(self) -> None:
        """The four facts `foundation/0003` R32 requires the base to declare, asserted in the output.

        This read them back through the knowledge materializer until that library went with the
        generation path. What the materializer proved — that a reader finds all four — is asserted
        against the expanded text instead, because the scaffold is what this module is about and a
        test that needs an absent consumer to run asserts nothing at all.
        """
        text = (self.expanded() / "system.md").read_text()
        for key in ("timezone", "currency", "identity_strategy", "body_lines"):
            self.assertIn(key, text, f"the scaffolded system.md declares no {key}")

    def test_it_names_a_schema_now_that_nothing_else_checks_it(self) -> None:
        """The inverse of what stood here, and the reason is that the other checker left.

        It asserted `None`, because a schema would have been a second home for four facts the
        knowledge validator already checked by name. That validator went with the generation path,
        so the facts went from checked in one place to checked in none — and a scaffold that fills
        in no default cannot catch a value somebody edited to nonsense afterwards.
        """
        self.assertEqual("knowledge-system.json", scaffold.SCHEMA_BY_KIND["knowledge-system"])

    def test_the_ceiling_is_supplied_and_never_defaulted(self) -> None:
        values = {k: v for k, v in CASES["knowledge-system"].items() if k != "body_lines"}
        _text, problems = scaffold.expand("knowledge-system", values)
        self.assertNotEqual([], problems, "a ceiling nobody supplied is a hidden default")


class Expansion(unittest.TestCase):
    def test_each_scaffold_produces_a_conforming_artifact(self) -> None:
        for kind, values in CASES.items():
            with self.subTest(kind=kind):
                text, problems = scaffold.expand(kind, values)
                self.assertEqual([], problems, kind)
                self.assertEqual([], scaffold.conforms(kind, text), kind)

    def test_no_placeholder_survives_expansion(self) -> None:
        for kind, values in CASES.items():
            with self.subTest(kind=kind):
                text, _ = scaffold.expand(kind, values)
                self.assertEqual([], scaffold.PLACEHOLDER.findall(text), kind)

    def test_a_missing_value_is_refused(self) -> None:
        """No default is filled in: a value nobody supplied is a decision nobody made."""
        values = dict(CASES["concept"])
        values.pop("generated_at")
        _text, problems = scaffold.expand("concept", values)
        self.assertTrue(any("generated_at" in p for p in problems), problems)

    def test_an_unknown_value_is_refused(self) -> None:
        values = dict(CASES["concept"], nonsense="x")
        _text, problems = scaffold.expand("concept", values)
        self.assertTrue(any("nonsense" in p for p in problems), problems)

    def test_nothing_is_minted(self) -> None:
        """Every stamp-shaped field is a placeholder, never a value the scaffold supplies."""
        for kind in ("concept", "domain-object-definition"):
            text = scaffold.template_path(kind).read_text()
            names = scaffold.placeholders(text)
            self.assertIn("generated_at", names, kind)
            self.assertIn("generated_by", names, kind)


class Rejection(unittest.TestCase):
    """The direction that proves validation is real."""

    def test_a_non_conforming_expansion_is_reported(self) -> None:
        values = dict(CASES["concept"], slug="Not A Valid Slug")
        text, problems = scaffold.expand("concept", values)
        self.assertEqual([], problems)
        self.assertTrue(scaffold.conforms("concept", text), "the schema accepted an invalid id")

    def test_a_domain_object_missing_its_kind_fields_is_reported(self) -> None:
        """Each kind has its own required fields; one skeleton for eight would fit none."""
        text, _ = scaffold.expand("domain-object-definition", CASES["domain-object-definition"])
        broken = text.replace("type: definition", "type: lifecycle")
        self.assertTrue(scaffold.conforms("domain-object-lifecycle", broken))


class CommandLine(unittest.TestCase):
    def test_it_writes_and_refuses_to_overwrite(self) -> None:
        import subprocess
        import sys

        args = [f"--set={k}={v}" for k, v in CASES["concept"].items()]
        with tempfile.TemporaryDirectory() as holder:
            out = Path(holder) / "worked-example.md"
            first = subprocess.run(
                [sys.executable, "-B", str(REPO_ROOT / "scripts" / "scaffold.py"),
                 "--kind", "concept", "--out", str(out), *args],
                capture_output=True, text=True,
            )
            self.assertEqual(0, first.returncode, first.stderr)
            self.assertTrue(out.is_file())
            second = subprocess.run(
                [sys.executable, "-B", str(REPO_ROOT / "scripts" / "scaffold.py"),
                 "--kind", "concept", "--out", str(out), *args],
                capture_output=True, text=True,
            )
            self.assertEqual(1, second.returncode)
            self.assertIn("already exists", second.stderr)


if __name__ == "__main__":
    unittest.main()
