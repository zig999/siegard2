"""A shipped component names no path the consumer does not have.

`src/claude/` is copied into the distribution whole, so a citation inside it travels to a
repository where `foundation/`, `scripts/`, `tests/`, `fixtures/`, and `docs/` do not exist. Those
are the generator's own trees, and a component pointing at one hands its reader a path that
resolves to nothing — the failure is silent, because prose does not fail like an import does.

All five trees below are covered, `foundation/` included. An earlier version of this docstring
described four and called `foundation/` deliberately absent, on the grounds that a shipped artifact
still cites the requirement it implements and whether such a citation should survive in a
consumer's hands was a decision this suite did not make. That decision was made: every such
citation was removed when the shipped tree was cut loose from the generator's documents, and the
tuple has covered `foundation/` since. The docstring is what lagged, which is the failure mode a
comment has and an assertion does not.

This checks citations *inside* shipped files. That no such directory reaches the assembled
distribution is a separate guarantee, held by `scripts/verify_dist.py`.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from . import SHIPPED_ROOT

# Each is a directory that exists only in the generator's repository.
GENERATOR_ONLY = ("foundation", "scripts", "tests", "fixtures", "docs")
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
