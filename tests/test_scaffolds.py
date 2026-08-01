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

# One plausible value per placeholder, per kind. Deliberately verbose rather than generated:
# a value that happened to satisfy a pattern by accident would make a green test meaningless.
CASES: dict[str, dict[str, str]] = {
    "change-request": {
        "request_id": "cr_7a2e4d10",
        "type": "ordinary",
        "requested_by": "the sales team lead",
        "requested_at": "2026-08-01T09:00:00Z",
        "statement": "Sales must issue priced proposals that expire after a bounded period.",
        "artifact": "intake/sales-request.md",
    },
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
    "adr": {
        "id": "0099",
        "title": "Record one decision, and say what it costs",
        "context": "A scaffold needs a worked example to be testable.",
        "decision": "Ship this skeleton and require it to be filled in.",
        "consequences": "An unfilled ADR is visibly unfilled rather than plausibly complete.",
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
    "knowledge-object-definition": {
        "context": "sales",
        "slug": "order-line",
        "title": "Order line",
        "description": "One priced line inside an order, with no identity outside the order.",
        "boundary_slug": "order",
        "ddd": "value-object",
        "attribute_name": "quantity",
        "attribute_type": "integer",
        "out_of_scope": "how a line price is calculated, which no knowledge object here holds",
        "invariant": "carry a quantity greater than zero",
        **STAMP,
    },
    "knowledge-object-rule": {
        "context": "sales",
        "slug": "cancelled-order-not-billable",
        "title": "A cancelled order is not billable",
        "description": "An order may be invoiced only while it has not been cancelled.",
        "question": "Which orders may be invoiced?",
        "boundary_slug": "order",
        "expression": "order.state != 'cancelled'",
        "given_field": "order.state",
        "allowed_value": "confirmed",
        "trigger": "invoice",
        "rejected_value": "cancelled",
        "out_of_scope": "who may cancel an order, which the order lifecycle holds",
        "condition": "the order has not reached its cancelled state",
        **STAMP,
    },
    "knowledge-object-lifecycle": {
        "context": "sales",
        "slug": "order",
        "title": "Order lifecycle",
        "description": "An order is placed and then either fulfilled or cancelled.",
        "subject_title": "Order",
        "boundary_slug": "order",
        "subject_slug": "order",
        "initial_state": "placed",
        "terminal_state": "cancelled",
        "trigger": "cancel",
        "error_slug": "order-already-cancelled",
        "out_of_scope": "how a cancellation is authorized, which no object here holds",
        "initial_meaning": "has been recorded and not yet resolved",
        "terminal_meaning": "will not be fulfilled and cannot be invoiced",
        **STAMP,
    },
    "knowledge-object-interface": {
        "context": "sales",
        "slug": "order-placed",
        "title": "Order placed",
        "description": "The event published when an order reaches its placed state.",
        "boundary_slug": "order",
        "ddd": "domain-event",
        "version": "1",
        "schema": "order-placed.v1",
        "ownership": "published",
        "out_of_scope": "who consumes the event, which is not a fact about the interface",
        "semantics": "Published once, when the order is first recorded.",
        **STAMP,
    },
    "knowledge-object-boundary": {
        "context": "sales",
        "slug": "sales",
        "title": "Sales",
        "description": "The scope that owns an order and everything whose identity depends on it.",
        "subdomain_type": "core",
        "out_of_scope": "invoicing, which the billing boundary owns",
        "owns": "the order, its lines, and its lifecycle",
        **STAMP,
    },
    "pack-declaration": {
        "pack": "worked-example",
        "version": "0.1.0",
        "framework_contract": "generation-plan/1",
        "artifact_class": "type",
        "track": "deterministic",
        "node_type": "definition",
    },
    "specification-delta": {
        "request_id": "cr_7a2e4d10",
        "artifact_id": "ko.definition.sales.order-line",
        "artifact_kind": "knowledge-object",
        "operation": "update",
        "reason": "the line gains a quantity, which the definition does not currently hold",
    },
    "validation-evidence": {
        "producer": "worked-example",
        "verdict": "passed",
        "request_id": "cr_7a2e4d10",
        "command": "make validate",
        "result": "pass",
        "detail": "all knowledge bases valid",
    },
    "knowledge-object-process": {
        "context": "sales",
        "slug": "order-to-cash",
        "title": "Order to cash",
        "description": "The path from a placed order to a settled invoice.",
        "boundary_slug": "order",
        "ddd": "saga",
        "first_step_slug": "order",
        "last_step_slug": "order-line",
        "out_of_scope": "payment reconciliation, which no object here holds",
        "outcome": "a settled invoice or a cancelled order",
        **STAMP,
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

    def test_the_materializer_resolves_all_three_defaults(self) -> None:
        from knowledge_graph_lib import load

        graph = load(self.expanded())
        self.assertEqual([], graph.problems, "the scaffolded file reports nothing missing")
        for key in ("timezone", "currency", "identity_strategy"):
            self.assertIn(key, graph.defaults)

    def test_the_body_ceiling_is_enforceable_from_it(self) -> None:
        """Absent the ceiling the check reports itself unenforceable, which is the failure to avoid."""
        from knowledge_graph_lib import load

        ceiling = load(self.expanded()).limits.get("body_lines")
        self.assertIsInstance(ceiling, int)
        self.assertGreater(ceiling, 0)

    def test_it_names_no_schema_on_purpose(self) -> None:
        """A schema here would be a second home for the four facts the validator already checks."""
        self.assertIsNone(scaffold.SCHEMA_BY_KIND["knowledge-system"])

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
        for kind in ("concept", "knowledge-object-definition"):
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

    def test_a_knowledge_object_missing_its_type_fields_is_reported(self) -> None:
        """Each node type has its own required fields; one skeleton for six would fit none."""
        text, _ = scaffold.expand("knowledge-object-definition", CASES["knowledge-object-definition"])
        broken = text.replace("type: definition", "type: lifecycle")
        self.assertTrue(scaffold.conforms("knowledge-object-lifecycle", broken))


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
