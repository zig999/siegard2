"""A shipped scaffold exercised the way a consumer actually uses one.

`tests/test_scaffolds.py` covers the generator's path: `scaffold.py` expands a template and refuses a
missing value. This suite covers the consumer's, which is different in kind — an agent reads the shipped
scaffold, substitutes, and writes, and no expander stands between it and the file.

Whether an expander *could* stand there is not what decides this. Four paths go around one, and none of
them needs bad faith: not running it, running it and editing the output afterwards, writing the object by
hand, and passing a placeholder as a value. The last is not hypothetical — `scaffold.py` accepts
`--set title='"{{title}}"'` and prints a conforming artifact, because `expand` checks that every
placeholder received a value and never that the value is itself one. The generator's own refusal has the
hole this check exists to close.

So the guarantee goes where a producer's work is checked rather than where it is intended, which is the
rule `foundation/0005` R5 states and the reason the boundary validator runs *after* an authoring agent
rather than inside it. These tests exercise it there: a scaffold substituted the way an agent substitutes
one, written into a knowledge base, and validated by the validator that ships beside it. Nothing in them
depends on which tools the producer was granted, which is the point.

The asymmetry that makes the check necessary is asserted directly. A bare `{{name}}` in frontmatter
already fails — YAML reads `{{...}}` as a flow mapping — but by accident, and the message says
`unhashable key`. Quoted or in the body it passes everything, because `"{{title}}"` is a non-empty string
and no schema can tell it from a title. It would then reach the graph, the projections, and generation,
all of which read the same objects.
"""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from validate_knowledge import validate

from tests.support import REPO_ROOT

SHIPPED_TEMPLATES = REPO_ROOT / "src" / "claude" / "templates"
FIXTURE = REPO_ROOT / "fixtures" / "knowledge-two-context" / "knowledge"

# Every value the boundary scaffold asks for. A consumer's agent supplies these from the request; here
# they stand in for it, and one is left out per test to model the substitution it forgot.
VALUES = {
    "context": "sales",
    "slug": "order",
    "title": "Order",
    "description": "The consistency boundary an order and its lines share.",
    "ddd": "aggregate",
    "subdomain_type": "core",
    "out_of_scope": "pricing, which the pricing boundary holds",
    "responsibility": "keep an order consistent with the lines it holds",
    "owns": "the order and its lines",
    "generated_by": "claude-opus-5",
    "generated_at": "2026-08-01T10:00:00Z",
}


def substitute(text: str, values: dict[str, str]) -> str:
    """What an agent with Write and no shell does: read, replace, write."""
    for name, value in values.items():
        text = text.replace(f"{{{{{name}}}}}", value)
    return text


class ScaffoldInUse(unittest.TestCase):
    def setUp(self) -> None:
        holder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, holder, True)
        self.root = Path(holder) / "knowledge"
        self.root.mkdir(parents=True)
        # A base that already holds what a new boundary needs to sit beside.
        shutil.copy(FIXTURE / "system.md", self.root / "system.md")

    def author(self, relative: str, kind: str, values: dict[str, str]) -> Path:
        template = (SHIPPED_TEMPLATES / f"{kind}.md").read_text()
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(substitute(template, values))
        return path

    def placeholder_problems(self) -> list[str]:
        return [p for p in validate(self.root) if "placeholder" in p]

    def test_a_fully_substituted_scaffold_carries_no_placeholder(self) -> None:
        """The positive case, without which every rejection below could be rejecting everything."""
        self.author("boundary/sales.order.md", "knowledge-object-boundary", VALUES)
        self.assertEqual([], self.placeholder_problems())

    def test_a_placeholder_left_in_a_quoted_field_is_caught(self) -> None:
        """`"{{title}}"` is a valid non-empty string, and no schema can refuse it."""
        values = dict(VALUES, title='"{{title}}"')
        self.author("boundary/sales.order.md", "knowledge-object-boundary", values)
        problems = self.placeholder_problems()
        self.assertTrue(problems)
        self.assertTrue(any("`{{title}}`" in p for p in problems))

    def test_a_placeholder_left_in_the_body_is_caught(self) -> None:
        """The body is prose; nothing else in the framework reads it for shape."""
        values = {k: v for k, v in VALUES.items() if k != "owns"}
        self.author("boundary/sales.order.md", "knowledge-object-boundary", values)
        self.assertTrue(any("`{{owns}}`" in p for p in self.placeholder_problems()))

    def test_each_missing_value_is_reported_once(self) -> None:
        """A placeholder repeated through a template is one decision, not four findings.

        Quoted, because the boundary scaffold uses `title` in four places and a bare one would not
        reach this check at all — see the test below.
        """
        values = dict(VALUES, title='"{{title}}"')
        self.author("boundary/sales.order.md", "knowledge-object-boundary", values)
        named = [p for p in self.placeholder_problems() if "`{{title}}`" in p]
        self.assertEqual(1, len(named), f"expected one finding for `title`; got {named}")

    def test_a_bare_placeholder_in_frontmatter_never_reaches_this_check(self) -> None:
        """It fails earlier, as a YAML error, and the message does not say what is wrong.

        `{{title}}` unquoted is a flow mapping, so the frontmatter does not parse and the file never
        becomes a node. The rejection is real and it is accidental: a reader is told `found unhashable
        key` and has to work out that a substitution was forgotten. Recorded here rather than repaired,
        because the file is refused either way and the case that mattered — a placeholder that parses —
        is what the check was added for.
        """
        values = {k: v for k, v in VALUES.items() if k != "title"}
        self.author("boundary/sales.order.md", "knowledge-object-boundary", values)
        problems = validate(self.root)
        self.assertTrue(problems, "a bare placeholder must not be accepted")
        self.assertEqual([], self.placeholder_problems())
        self.assertTrue(any("unhashable" in p or "not valid YAML" in p for p in problems))

    def test_the_finding_names_the_line(self) -> None:
        """A placeholder in a body of prose is not findable without one."""
        values = {k: v for k, v in VALUES.items() if k != "owns"}
        self.author("boundary/sales.order.md", "knowledge-object-boundary", values)
        self.assertTrue(any("line " in p for p in self.placeholder_problems()))


class AnExpanderCannotCarryThisGuarantee(unittest.TestCase):
    """Why the check is at the boundary and not in a tool, asserted rather than argued.

    The tempting design is to ship the expander and let it refuse. It cannot: `expand` verifies that
    every placeholder received a value, and a placeholder is a value. This test pins that hole open, so
    the reasoning does not quietly become wrong if someone later decides the expander is the guard.
    """

    def test_the_generators_expander_accepts_a_placeholder_as_a_value(self) -> None:
        import scaffold

        values = dict(VALUES, title='"{{title}}"')
        supplied = {k: v for k, v in values.items() if k in scaffold.placeholders(
            (SHIPPED_TEMPLATES / "knowledge-object-boundary.md").read_text()
        )}
        text, problems = scaffold.expand("knowledge-object-boundary", supplied)
        self.assertEqual([], problems, "expand refuses a missing value and not a placeholder value")
        self.assertIn('"{{title}}"', text)
        self.assertEqual([], scaffold.conforms("knowledge-object-boundary", text))

    def test_the_boundary_check_catches_what_the_expander_passed(self) -> None:
        """The same artifact, refused where it is read instead of where it was made."""
        import scaffold

        holder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, holder, True)
        root = Path(holder) / "knowledge"
        (root / "boundary").mkdir(parents=True)
        shutil.copy(FIXTURE / "system.md", root / "system.md")

        values = dict(VALUES, title='"{{title}}"')
        supplied = {k: v for k, v in values.items() if k in scaffold.placeholders(
            (SHIPPED_TEMPLATES / "knowledge-object-boundary.md").read_text()
        )}
        text, _ = scaffold.expand("knowledge-object-boundary", supplied)
        (root / "boundary" / "sales.order.md").write_text(text)

        self.assertTrue(any("placeholder" in p for p in validate(root)))


class EveryShippedScaffoldSurvivesTheCheck(unittest.TestCase):
    """A scaffold whose own placeholder syntax the check cannot see would be unguarded.

    The check reads `{{name}}` with a lowercase identifier. A scaffold using any other spelling would
    pass through it silently, so the shipped set is held to the one shape the check knows.
    """

    def test_every_placeholder_uses_the_shape_the_check_reads(self) -> None:
        import re

        recognised = re.compile(r"\{\{[a-z0-9_]+\}\}")
        any_braces = re.compile(r"\{\{[^}]*\}\}")
        for template in sorted(SHIPPED_TEMPLATES.glob("*.md")):
            with self.subTest(scaffold=template.name):
                for found in any_braces.findall(template.read_text()):
                    self.assertRegex(found, recognised, f"{template.name} uses an unreadable placeholder")

    def test_the_shipped_set_is_not_empty(self) -> None:
        """Otherwise the loop above passes by iterating over nothing."""
        self.assertGreater(len(list(SHIPPED_TEMPLATES.glob("*.md"))), 10)
