"""The prose that explains the framework is held to the framework.

`docs/how-siegard-works.md` names every skill, every script and every flag, and it was held by
nothing at all — which is where three drifts were found: a hardcoded skill count two behind the
tree, a hardcoded line count of a script's output, and a documented flag list missing a form the
same page's own table cites.

`src/consumer/CLAUDE.md` already gets this treatment, for the reason stated there: a file that
explains the tree cannot report its own gaps. This is the same guard for the page that explains
it to a person rather than to a session.

What is deliberately not checked is prose accuracy. A sentence can be wrong in ways no test
reaches; what a test can hold is that every name it uses exists and every count it states is
computed rather than remembered.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
DOC = REPO / "docs/how-siegard-works.md"
SRC = REPO / "src/claude"

NUMBER = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
          "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
          "fourteen": 14, "fifteen": 15}


@pytest.fixture(scope="module")
def text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_every_shipped_skill_is_named(text):
    for path in sorted((SRC / "skills").iterdir()):
        assert f"/{path.name}" in text, \
            f"the page never names /{path.name}; a skill the page omits is a skill nobody reading " \
            f"this learns exists"


def test_every_shipped_agent_is_named(text):
    for path in sorted((SRC / "agents").glob("*.md")):
        assert path.stem in text, f"the page never names the {path.stem} agent"


def test_it_names_no_skill_or_agent_that_is_not_shipped(text):
    """Two namespaces share the slash: the framework's skills, which this repository ships and
    this test holds the page to, and the harness's own commands, which the install section names
    because they are how a consumer receives updates. The second set is enumerated, not inferred —
    a typo'd skill name must keep failing here rather than pass as a presumed harness command."""
    harness = {"plugin", "reload-plugins"}
    shipped = {p.name for p in (SRC / "skills").iterdir()}
    for named in set(re.findall(r"`/([a-z][a-z-]+)`", text)) - harness:
        assert named in shipped, \
            f"the page names /{named}, which src/claude/skills does not hold"


@pytest.mark.parametrize("script", sorted(p.name for p in (SRC / "bin").glob("*.py")))
def test_every_flag_the_page_attributes_to_a_script_exists_in_it(script, text):
    """The page documents each script's forms. A flag it names and the script does not parse is a
    reader running an invocation that refuses."""
    source = (SRC / "bin" / script).read_text(encoding="utf-8")
    for block in re.findall(rf"^\s*(?:python3 -B \S*)?{re.escape(script)} ([^\n`]*)$", text, re.M):
        for flag in re.findall(r"--[a-z][a-z-]+", block):
            assert flag in source, \
                f"the page shows `{script} {flag}`, which {script} does not parse"


def test_the_counts_it_states_are_the_counts_that_ship(text):
    """A number written into prose is a number nobody recomputes. These two were both wrong when
    this test was written — the page said eight skills beside a table listing ten."""
    for word, kind in (("skills", "skills"), ("agents", "agents")):
        actual = len(list((SRC / kind).iterdir()))
        for stated in re.findall(rf"the ([a-z]+) {word}\b", text):
            assert NUMBER.get(stated) == actual, \
                f"the page says '{stated} {word}' and {actual} ship"


def test_it_quotes_no_line_count_of_a_scripts_own_output(text):
    """`terms.py`'s output was quoted as '211 lines' and stood at 219. A count of something that
    changes every time a definition is added belongs in the reader's terminal, not in prose."""
    assert not re.search(r"\b\d{2,}\s+lines\b", text), \
        "the page states a line count; run the script instead of remembering its size"
