"""Every skill stays bound to its contract: it cites what exists, and restates nothing.

The third test is the unusual one. Every closed-vocabulary value the paired schema declares
must be absent from the skill text — a value listed in the prompt is a second home the moment
the schema changes, and the prompt is the copy nothing validates. Only hyphenated values are
checked: they are distinctive tokens, where bare words like `core` or `task` occur in ordinary
prose.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
CITATION = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([\w./-]+)")

SKILLS = {
    "analyse-domain": {"contract": "schemas/node.json", "validator": "bin/graph.py"},
    "plan-work": {"contract": "schemas/plan-node.json", "validator": "bin/plan.py"},
}


@pytest.fixture(params=sorted(SKILLS), scope="module")
def case(request) -> dict:
    name = request.param
    pairing = SKILLS[name]
    text = (REPO / "src/claude/skills" / name / "SKILL.md").read_text(encoding="utf-8")
    schema = json.loads((REPO / "src/claude" / pairing["contract"]).read_text(encoding="utf-8"))
    return {"name": name, "text": text, "schema": schema, **pairing}


def test_every_cited_path_exists(repo, case):
    cited = CITATION.findall(case["text"])
    assert cited, f"{case['name']} cites nothing under the plugin root; it must cite the contract"
    for relative in cited:
        assert (repo / "src/claude" / relative).is_file(), \
            f"{case['name']} cites {relative}, which src/claude does not hold"


def test_the_contract_and_the_validator_are_both_cited(case):
    cited = set(CITATION.findall(case["text"]))
    assert case["contract"] in cited
    assert case["validator"] in cited


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


def test_the_skill_restates_no_vocabulary(case):
    distinctive = sorted({v for v in enum_values(case["schema"]) if "-" in v})
    assert distinctive, "the schema declares no hyphenated vocabulary; the guard lost its subject"
    restated = [v for v in distinctive if v in case["text"]]
    assert restated == [], \
        f"{case['name']} restates {restated}; a vocabulary listed in a prompt is a second home"
