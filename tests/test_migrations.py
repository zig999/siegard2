"""Contract versioning and migration, over `.claude/rules/compatibility.md`.

That rule states four things a breaking change owes and, until this suite, held none of them
to a mechanism.

No contract in this repository carries a second version, so no migration is registered. What
remains under test is the machinery that will meet the first real bump: the refusals a migration owes, and the coverage check that fails a bump
registering no path. `foundation/0013` R11 asks for a migration tested against the old behavior;
with no migration in the registry, R11 is unexercised rather than satisfied, and that is
stated here rather than implied by a green suite.

The contract-version checks are the same argument applied to the schemas
themselves: a constraint change with no version bump must be detected, and an edit to a
description must not be, because the rule calls one breaking and not the other.
"""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from jsonschema import Draft202012Validator

import check_contract_versions as cv
from migrate_contracts import MIGRATIONS, MigrationError, migrate  # noqa: F401

REPO_ROOT = Path(__file__).resolve().parent.parent
SHIPPED_SCHEMAS = REPO_ROOT / "src" / "claude" / "schemas"
GENERATOR_SCHEMAS = REPO_ROOT / "schemas"
SCHEMAS = SHIPPED_SCHEMAS


def validator(name: str) -> Draft202012Validator:
    return Draft202012Validator(json.loads((SCHEMAS / name).read_text()))


class MigrationRefusals(unittest.TestCase):
    """A migration does not guess. Each refusal is the rejection direction of one rule."""

    def test_refuses_an_instance_declaring_another_version(self) -> None:
        with self.assertRaises(MigrationError) as caught:
            migrate({"contract_version": "adr/2"}, "adr/1", "adr/2")
        self.assertIn("does not guess", str(caught.exception))

    def test_refuses_a_downgrade(self) -> None:
        with self.assertRaises(MigrationError):
            migrate({"contract_version": "adr/2"}, "adr/2", "adr/1")

    def test_refuses_crossing_contracts(self) -> None:
        with self.assertRaises(MigrationError):
            migrate({"contract_version": "adr/1"}, "adr/1", "concept/1")

    def test_refuses_an_unregistered_hop(self) -> None:
        with self.assertRaises(MigrationError) as caught:
            migrate({"contract_version": "concept/1"}, "concept/1", "concept/2")
        self.assertIn("no migration registered", str(caught.exception))



class ConstraintDigest(unittest.TestCase):
    """What counts as a change, and what does not — the rule's own distinction."""

    def test_annotation_keywords_are_stripped(self) -> None:
        plain = {"type": "object", "properties": {"a": {"type": "string"}}}
        annotated = {
            "type": "object",
            "description": "some prose",
            "properties": {"a": {"type": "string", "description": "more prose"}},
        }
        self.assertEqual(cv.constraint_digest(plain), cv.constraint_digest(annotated))

    def test_a_property_named_description_survives(self) -> None:
        """`properties.description` is a field name, not an annotation — the concept contract has one."""
        schema = {"type": "object", "properties": {"description": {"type": "string"}}}
        stripped = cv.strip_annotations(schema)
        self.assertIn("description", stripped["properties"])

    def test_a_constraint_change_changes_the_digest(self) -> None:
        before = {"type": "object", "properties": {"a": {"type": "string"}}}
        after = {"type": "object", "properties": {"a": {"type": "string", "maxLength": 3}}}
        self.assertNotEqual(cv.constraint_digest(before), cv.constraint_digest(after))

    def test_key_order_does_not_change_the_digest(self) -> None:
        self.assertEqual(
            cv.constraint_digest({"type": "object", "required": ["a"]}),
            cv.constraint_digest({"required": ["a"], "type": "object"}),
        )


class Declaration(unittest.TestCase):
    """A filename and a self-declared version are two records of one fact."""

    def entry(self, file: str, name: str, schema: dict) -> dict:
        return {"file": file, "name": name, "schema": schema}

    def test_agreement_passes(self) -> None:
        schema = {
            "required": ["contract_version"],
            "properties": {"contract_version": {"const": "widget/1"}},
        }
        self.assertEqual([], cv.check_declaration("widget/1", self.entry("widget.json", "widget", schema)))

    def test_a_const_naming_another_file_is_reported(self) -> None:
        """The filename carries identity, the document carries the version, and they must agree."""
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        directory = Path(holder.name)
        (directory / "widget.json").write_text(json.dumps({
            "required": ["contract_version"],
            "properties": {"contract_version": {"const": "gadget/1"}},
        }))
        with mock.patch.object(cv, "SCHEMA_DIRS", (directory,)):
            _found, problems = cv.contracts()
        self.assertEqual(1, len(problems))
        self.assertIn("does not name this file", problems[0])

    def test_declared_but_not_required_is_reported(self) -> None:
        schema = {"properties": {"contract_version": {"const": "widget/1"}}}
        problems = cv.check_declaration("widget/1", self.entry("widget.json", "widget", schema))
        self.assertIn("does not require it", problems[0])

    def test_a_missing_declaration_is_reported(self) -> None:
        problems = cv.check_declaration("widget/1", self.entry("widget.json", "widget", {}))
        self.assertIn("infer", problems[0])

    def test_harness_owned_contracts_are_exempt(self) -> None:
        schema = {"additionalProperties": False, "properties": {"name": {"type": "string"}}}
        self.assertEqual([], cv.check_declaration("skill/1", self.entry("skill.json", "skill", schema)))

    def test_the_exemption_requires_a_closed_object(self) -> None:
        """The stated reason has to hold, or the exemption is a hole with a comment on it."""
        schema = {"properties": {"name": {"type": "string"}}}
        problems = cv.check_declaration("skill/1", self.entry("skill.json", "skill", schema))
        self.assertIn("additionalProperties", problems[0])


class LockIntegrity(unittest.TestCase):
    """The committed lock against a disposable copy of both contract trees.

    Contracts sit on two sides now — what the framework ships under `src/claude/schemas/`,
    and what governs this repository under `schemas/` — and one lock covers both, because a
    constraint that moves is a break whichever side it sits on. The copy flattens them, which
    is what the checker sees anyway: it keys on contract version, and a name colliding across
    the two trees would be the defect this arrangement should surface rather than hide.
    """

    def setUp(self) -> None:
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        self.dir = Path(holder.name) / "schemas"
        shutil.copytree(GENERATOR_SCHEMAS, self.dir)
        for source in SHIPPED_SCHEMAS.glob("*.json"):
            shutil.copy(source, self.dir / source.name)
        patches = [
            mock.patch.object(cv, "SCHEMA_DIRS", (self.dir,)),
            mock.patch.object(cv, "SCHEMA_DIR", self.dir),
            mock.patch.object(cv, "LOCK_PATH", self.dir / "contract-versions.json"),
        ]
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)

    def edit(self, name: str, mutate) -> None:
        path = self.dir / name
        schema = json.loads(path.read_text())
        mutate(schema)
        path.write_text(json.dumps(schema, indent=2) + "\n")

    def test_the_committed_lock_matches_the_committed_schemas(self) -> None:
        count, problems = cv.check(update=False)
        self.assertEqual([], problems)
        self.assertEqual(0, count)

    def test_a_constraint_change_without_a_bump_is_reported(self) -> None:
        self.edit("concept.json", lambda s: s["properties"]["tags"].update(maxItems=3))
        _count, problems = cv.check(update=False)
        self.assertTrue(
            any("concept.json" in p and "constraints changed" in p for p in problems),
            f"expected a constraint-drift report naming the file; got {problems}",
        )

    def test_an_annotation_change_is_not_reported(self) -> None:
        self.edit(
            "concept.json",
            lambda s: s["properties"]["title"].update(description="Display name, reworded."),
        )
        _count, problems = cv.check(update=False)
        self.assertEqual([], problems)

    def test_a_removed_contract_is_reported(self) -> None:
        (self.dir / "impact-analysis.json").unlink()
        _count, problems = cv.check(update=False)
        self.assertTrue(
            any("impact-analysis/1" in p and "no schema file" in p for p in problems),
            f"expected a removal report; got {problems}",
        )

    def test_an_unrecorded_contract_is_reported(self) -> None:
        shutil.copy(self.dir / "concept.json", self.dir / "widget.json")
        self.edit("widget.json", lambda s: s["properties"]["contract_version"].update(const="widget/1"))
        _count, problems = cv.check(update=False)
        self.assertTrue(
            any("widget.json" in p and "not recorded" in p for p in problems),
            f"expected an unrecorded-contract report; got {problems}",
        )

    def test_a_malformed_filename_is_reported(self) -> None:
        shutil.copy(self.dir / "concept.json", self.dir / "no-version.json")
        _count, problems = cv.check(update=False)
        self.assertTrue(
            any("no-version.json" in p for p in problems),
            f"expected a filename report; got {problems}",
        )

    def test_update_rewrites_the_lock_so_the_check_passes_again(self) -> None:
        self.edit("concept.json", lambda s: s["properties"]["tags"].update(maxItems=3))
        cv.check(update=True)
        _count, problems = cv.check(update=False)
        self.assertEqual([], problems)



if __name__ == "__main__":
    unittest.main()
