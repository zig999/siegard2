"""The skill stays bound to the contract: it cites what exists, and restates nothing.

The third test is the unusual one. Every closed-vocabulary value the schema declares must be
absent from the skill text — a value listed in the prompt is a second home the moment the schema
changes, and the prompt is the copy nothing validates. Only hyphenated values are checked:
they are distinctive tokens, where bare words like `core` or `saga` occur in ordinary prose.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

SKILL = Path(__file__).resolve().parent.parent / "src/claude/skills/analyse-domain/SKILL.md"
CITATION = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([\w./-]+)")


@pytest.fixture(scope="module")
def text() -> str:
    return SKILL.read_text(encoding="utf-8")


def test_every_cited_path_exists(repo, text):
    cited = CITATION.findall(text)
    assert cited, "the skill cites nothing under the plugin root; it must cite the contract"
    for relative in cited:
        assert (repo / "src/claude" / relative).is_file(), \
            f"the skill cites {relative}, which src/claude does not hold"


def test_the_contract_and_the_validator_are_both_cited(text):
    cited = set(CITATION.findall(text))
    assert "schemas/node.json" in cited
    assert "bin/graph.py" in cited


def enum_values(node):
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "enum" and isinstance(value, list):
                yield from (v for v in value if isinstance(v, str))
            else:
                yield from enum_values(value)
    elif isinstance(node, list):
        for value in node:
            yield from enum_values(value)


def test_the_skill_restates_no_vocabulary(schema, text):
    distinctive = sorted({v for v in enum_values(schema) if "-" in v})
    assert distinctive, "the schema declares no hyphenated vocabulary; the guard lost its subject"
    restated = [v for v in distinctive if v in text]
    assert restated == [], \
        f"the skill restates {restated}; a vocabulary listed in a prompt is a second home"
