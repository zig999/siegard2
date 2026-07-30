"""Shared plumbing for the framework test suite.

Every knowledge test follows one shape: copy the fixture, break exactly one thing, assert
the validator names it. The pristine copy is asserted to report nothing in
tests/test_knowledge_fixture.py, which is the other half of "both outcomes covered" — a
rejection test alone cannot tell a working check from one that rejects everything.

The suite runs on unittest from the standard library rather than on pytest. Every script
in this repository declares its dependencies and exits with a named error when one is
missing; a test suite that added a third dependency to run at all would make `make test`
fail for a reason unrelated to the framework.
"""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

# tests/__init__.py has already put scripts/ on the import path. Importing these here rather
# than inside each test keeps one place where the framework under test is named.
from frontmatter_lib import split_frontmatter
from validate_knowledge import validate

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_ROOT = REPO_ROOT / "fixtures" / "knowledge-two-context"
FIXTURE = FIXTURE_ROOT / "knowledge"


def render(data: dict, body: str) -> str:
    return "---\n" + yaml.safe_dump(data, sort_keys=False, allow_unicode=True) + "---\n" + body


class KnowledgeCase(unittest.TestCase):
    """A disposable copy of the two-context fixture, and the mutations a test applies."""

    def setUp(self) -> None:
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        self.root = Path(holder.name) / "knowledge"
        shutil.copytree(FIXTURE, self.root)

    # --- mutations ---------------------------------------------------------------

    def read(self, rel: str) -> tuple[dict, str]:
        return split_frontmatter((self.root / rel).read_text())

    def edit(self, rel: str, mutate) -> None:
        """Apply `mutate` to one file's frontmatter mapping and write it back."""
        data, body = self.read(rel)
        mutate(data)
        (self.root / rel).write_text(render(data, body))

    def replace_body(self, rel: str, body: str) -> None:
        data, _ = self.read(rel)
        (self.root / rel).write_text(render(data, body))

    def rename(self, rel: str, new_rel: str) -> None:
        target = self.root / new_rel
        target.parent.mkdir(parents=True, exist_ok=True)
        (self.root / rel).rename(target)

    def duplicate(self, rel: str, new_rel: str, new_id: str) -> None:
        data, body = self.read(rel)
        data["id"] = new_id
        target = self.root / new_rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render(data, body))

    # --- assertions --------------------------------------------------------------

    def problems(self) -> list[str]:
        return validate(self.root)

    def problems_after(self, rel: str, mutate) -> list[str]:
        """Validate a fresh copy carrying one mutation, leaving `self.root` untouched.

        For a test that must compare two verdicts: applying both mutations to one tree would
        report both failures together, which cannot show that each fires on its own.
        """
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        root = Path(holder.name) / "knowledge"
        shutil.copytree(FIXTURE, root)
        data, body = split_frontmatter((root / rel).read_text())
        mutate(data)
        (root / rel).write_text(render(data, body))
        return validate(root)

    def assertRejected(self, *needles: str) -> list[str]:
        """One reported problem must hold every needle.

        All needles in one problem rather than across the set: a mutation that provokes
        several unrelated failures would otherwise let a test pass on the wrong one.
        """
        found = self.problems()
        if not any(all(needle in problem for needle in needles) for problem in found):
            listing = "\n".join(f"    {p}" for p in found) or "    (nothing reported)"
            self.fail(f"no single problem holds all of {needles}. Reported:\n{listing}")
        return found

    def assertAccepted(self) -> None:
        found = self.problems()
        self.assertEqual(found, [], "the tree was expected to validate cleanly")
