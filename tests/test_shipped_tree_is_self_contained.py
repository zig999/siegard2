"""A shipped component names no path the consumer does not have.

`src/claude/` is copied into the distribution whole, so a citation inside it travels to a
repository where `scripts/`, `tests/`, `fixtures/`, and `docs/` do not exist. Those are the
generator's own trees, and a component pointing at one hands its reader a path that resolves
to nothing — the failure is silent, because prose does not fail like an import does.

The four trees below were clean when this was written and this keeps them clean. `specs/` is
deliberately absent: a shipped artifact still cites the requirement it implements, and whether
those citations should survive in a consumer's hands is a decision this suite does not make.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from . import SHIPPED_ROOT

# Each is a directory that exists only in the generator's repository.
GENERATOR_ONLY = ("specs", "scripts", "tests", "fixtures", "docs")
CITATION = re.compile(rf"\b({'|'.join(GENERATOR_ONLY)})/")


class ShippedTree(unittest.TestCase):
    def test_no_shipped_file_cites_a_generator_only_path(self) -> None:
        offenders: list[str] = []
        for path in sorted(SHIPPED_ROOT.rglob("*")):
            if not path.is_file() or "__pycache__" in str(path):
                continue
            for number, line in enumerate(path.read_text(errors="ignore").splitlines(), 1):
                if CITATION.search(line):
                    rel = path.relative_to(SHIPPED_ROOT).as_posix()
                    offenders.append(f"{rel}:{number}: {line.strip()[:90]}")
        self.assertEqual([], offenders, "\n".join(["", *offenders]))

    def test_the_check_can_fail(self) -> None:
        """Otherwise a rename of the generator's trees would make the assertion vacuous."""
        self.assertTrue(CITATION.search("see scripts/orchestrate.py for the transition table"))
