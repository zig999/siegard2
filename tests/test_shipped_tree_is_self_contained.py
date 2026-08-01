"""A shipped component names no path the consumer does not have, and its prose stays whole.

`src/claude/` is copied into the distribution whole, so a citation inside it travels to a
repository where `foundation/`, `scripts/`, `tests/`, `fixtures/`, and `docs/` do not exist. Those
are the generator's own trees, and a component pointing at one hands its reader a path that
resolves to nothing — the failure is silent, because prose does not fail like an import does.

`CLAUDE.md` and `.claude/` are covered for the same reason and were missed for longer. Both are the
generator's own development environment: `CLAUDE.md` is the maintainer's file and `.claude/`
configures the agent that develops the generator. Neither is installed, so a shipped file citing one
is the same dangling pointer as a citation of `foundation/`. Ten such references shipped while this
suite watched only the five directories above.

The second test exists because removing a citation is how the first one gets satisfied, and a
careless removal takes the sentence with it. Stripping the generator's paths out of this tree left
44 sentences beheaded — `You run generation. `this the entry point` — with the opening backtick
of the deleted span still in place. Every validator passed: prose has no syntax to fail. Unbalanced
inline-code spans are the mechanical trace that damage leaves, so they are what this asserts on.

Its granularity is the paragraph, and the limit is worth stating rather than discovering. Two
orphaned backticks in one paragraph restore even parity and pass — that is how four of the 44 sites
would have survived this check. What closes the gap is not a cleverer regex but the first test: the
damage only ever arose from stripping a citation, and a citation that never ships is never stripped.

That no generator-only directory reaches the assembled distribution is a separate guarantee, held by
`scripts/verify_dist.py`.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from . import SHIPPED_ROOT

# Each names something that exists only in the generator's repository.
GENERATOR_ONLY_TREES = ("foundation", "scripts", "tests", "fixtures", "docs")
CITATION = re.compile(
    rf"\b({'|'.join(GENERATOR_ONLY_TREES)})/"
    r"|\bCLAUDE\.md"
    r"|(?<!dist/)\.claude/"
)

# A fence is three backticks and pairs with its closer; counting it would report every fenced
# block as unbalanced.
FENCE = re.compile(r"^\s*```")


def shipped_files() -> list[Path]:
    return [
        p
        for p in sorted(SHIPPED_ROOT.rglob("*"))
        if p.is_file() and "__pycache__" not in str(p)
    ]


def unbalanced_paragraphs(text: str) -> list[int]:
    """The first line of every paragraph holding an odd number of backticks.

    Paragraph rather than line, because an inline span may legitimately wrap across two lines;
    paragraph rather than file, because a whole file is coarse enough to cancel two defects out.
    """
    starts: list[int] = []
    paragraph: list[str] = []
    first = 1
    for number, line in enumerate(text.splitlines() + [""], 1):
        if line.strip() == "":
            if paragraph and sum(l.count("`") for l in paragraph) % 2 == 1:
                starts.append(first)
            paragraph, first = [], number + 1
        else:
            if not paragraph:
                first = number
            paragraph.append(line)
    return starts


class ShippedTree(unittest.TestCase):
    def test_no_shipped_file_cites_a_generator_only_path(self) -> None:
        offenders: list[str] = []
        for path in shipped_files():
            for number, line in enumerate(path.read_text(errors="ignore").splitlines(), 1):
                if CITATION.search(line):
                    rel = path.relative_to(SHIPPED_ROOT).as_posix()
                    offenders.append(f"{rel}:{number}: {line.strip()[:90]}")
        self.assertEqual([], offenders, "\n".join(["", *offenders]))

    def test_no_shipped_file_leaves_an_inline_span_unclosed(self) -> None:
        offenders: list[str] = []
        for path in shipped_files():
            body = "\n".join(
                line for line in path.read_text(errors="ignore").splitlines()
                if not FENCE.match(line)
            )
            for start in unbalanced_paragraphs(body):
                offenders.append(f"{path.relative_to(SHIPPED_ROOT).as_posix()}: paragraph at line {start}")
        self.assertEqual([], offenders, "\n".join(["", *offenders]))

    def test_the_citation_check_can_fail(self) -> None:
        """Otherwise a rename of the generator's trees would make the assertion vacuous."""
        self.assertTrue(CITATION.search("see scripts/orchestrate.py for the transition table"))
        self.assertTrue(CITATION.search("CLAUDE.md **Commands** fixes the entry points"))
        self.assertTrue(CITATION.search("stated in .claude/rules/contracts.md"))

    def test_the_citation_check_admits_the_two_trees_that_do_ship(self) -> None:
        """`src/claude/` is this tree's own name and `dist/.claude/` is where it lands."""
        self.assertIsNone(CITATION.search("everything under src/claude/ ships"))
        self.assertIsNone(CITATION.search("assembled into dist/.claude/ by the generator"))

    def test_the_span_check_can_fail(self) -> None:
        """The exact shape the citation stripping left behind."""
        self.assertEqual([1], unbalanced_paragraphs("You run generation. `this the entry point"))
        self.assertEqual([], unbalanced_paragraphs("a `span` that closes"))
        self.assertEqual([], unbalanced_paragraphs("a `span wrapping\nacross` two lines"))
