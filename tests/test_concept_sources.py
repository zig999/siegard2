"""A concept's declared sources must still exist, and the live bundle must satisfy that.

The check exists because of the failure ADR-0010 records: docs/concepts/projection.md was
sourced from docs/adr/0001-event-sourced-workflow-state.md, that ADR was deleted, the
dangling source was replaced rather than reported, and the definition then drifted from
what cited it while every file still validated on its own.

Both outcomes are covered here for the reason tests/support.py states about the knowledge
fixture: a rejection test alone cannot tell a working check from one that rejects
everything, so the live bundle is asserted clean beside every rejection.
"""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from validate_concepts import validate

from tests.support import REPO_ROOT, render

BUNDLE = REPO_ROOT / "docs" / "concepts"

BASE = {
    "id": "concept.example-term",
    "type": "term",
    "title": "example term",
    "description": "A term that exists only inside this test.",
    "status": "proposed",
    "contract_version": "concept/1",
    "generated": {"by": "test", "at": "2026-07-30T00:00:00Z"},
}


class SourcesMustResolve(unittest.TestCase):
    def bundle_with(self, sources) -> Path:
        """A one-file bundle whose only concept declares `sources`, or none when None."""
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        root = Path(holder.name) / "concepts"
        root.mkdir(parents=True)
        data = dict(BASE)
        if sources is not None:
            data["sources"] = sources
        (root / "example-term.md").write_text(render(data, "# example term\n"))
        return root

    def problems_for(self, sources) -> list[str]:
        return validate(self.bundle_with(sources))

    def assertOneProblem(self, problems: list[str], *needles: str) -> None:
        if not any(all(needle in problem for needle in needles) for problem in problems):
            listing = "\n".join(f"    {p}" for p in problems) or "    (nothing reported)"
            self.fail(f"no single problem holds all of {needles}. Reported:\n{listing}")

    # --- the live bundle ----------------------------------------------------------

    def test_the_committed_bundle_validates_cleanly(self):
        self.assertEqual(validate(BUNDLE), [], "the committed concept bundle must validate")

    # --- rejections ---------------------------------------------------------------

    def test_a_source_that_resolves_to_no_file_is_rejected(self):
        problems = self.problems_for([{"resource": "docs/adr/0001-event-sourced-workflow-state.md"}])
        self.assertOneProblem(
            problems, "sources.0.resource", "0001-event-sourced-workflow-state.md", "no file"
        )

    def test_the_second_source_is_reported_by_its_own_index(self):
        problems = self.problems_for(
            [{"resource": "CLAUDE.md"}, {"resource": "specs/9999-does-not-exist.md"}]
        )
        self.assertOneProblem(problems, "sources.1.resource", "no file")

    def test_an_absolute_filesystem_path_is_rejected(self):
        problems = self.problems_for([{"resource": "/etc/hostname"}])
        self.assertOneProblem(problems, "sources.0.resource", "repo-relative")

    def test_a_path_escaping_the_repository_is_rejected(self):
        problems = self.problems_for([{"resource": "../outside/CLAUDE.md"}])
        self.assertOneProblem(problems, "sources.0.resource", "repo-relative")

    def test_a_directory_is_not_a_source(self):
        problems = self.problems_for([{"resource": "docs/adr"}])
        self.assertOneProblem(problems, "sources.0.resource", "no file")

    # --- acceptances --------------------------------------------------------------

    def test_a_source_that_resolves_is_accepted(self):
        self.assertEqual(self.problems_for([{"resource": "CLAUDE.md"}]), [])

    def test_an_absolute_uri_is_accepted_without_touching_the_filesystem(self):
        self.assertEqual(
            self.problems_for([{"resource": "https://json-schema.org/draft/2020-12/schema"}]), []
        )

    def test_a_concept_with_no_sources_field_is_accepted(self):
        self.assertEqual(self.problems_for(None), [])

    def test_an_empty_sources_list_is_accepted(self):
        self.assertEqual(self.problems_for([]), [])

    # --- the check does not displace the ones already there -----------------------

    def test_id_and_filename_disagreement_is_still_reported(self):
        root = self.bundle_with([{"resource": "CLAUDE.md"}])
        shutil.move(root / "example-term.md", root / "other-name.md")
        self.assertOneProblem(validate(root), "filename must be", "example-term.md")


if __name__ == "__main__":
    unittest.main()
