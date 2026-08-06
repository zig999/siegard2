"""Every skill stays bound to its contract: it cites what exists, and restates nothing.

The last test is the unusual one. Every closed-vocabulary value the shipped contracts declare must
be absent from every skill's text — a value listed in a prompt is a second home the moment the
schema changes, and the prompt is the copy nothing validates. The subject is the union of all of
them rather than each skill's own, for two reasons: a skill has no more business restating another
root's vocabulary than its own, and two of the contracts happen to declare no hyphenated value at
all, which would leave a per-skill guard with nothing to check. Only hyphenated values are checked:
they are distinctive tokens, where bare words like `core`, `task`, `covered` or `standard` occur in
ordinary prose.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
CITATION = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([\w./-]+)")
FENCE = re.compile(r"^---\n(.*?)\n---\n", re.S)

NODE_CONTRACTS = ("schemas/node.json", "schemas/plan-node.json", "schemas/delivery-node.json",
                  "schemas/standard.json")

SKILLS = {
    "analyse-domain": {"contract": "schemas/node.json", "validator": "bin/graph.py",
                       "delegates": []},
    "plan-work": {"contract": "schemas/plan-node.json", "validator": "bin/plan.py",
                  "delegates": ["codebase-surveyor", "backlog-decomposer",
                                "execution-contract-binder"]},
    "implement-task": {"contract": "schemas/delivery-node.json", "validator": "bin/deliver.py",
                       "delegates": ["task-implementer", "test-author"]},
    "review-change": {"contract": "schemas/delivery-node.json", "validator": "bin/deliver.py",
                      "delegates": ["coverage-auditor", "base-conformance-reviewer",
                                    "standard-conformance-reviewer", "failure-diagnostician"]},
}


@pytest.fixture(params=sorted(SKILLS), scope="module")
def case(request) -> dict:
    name = request.param
    pairing = SKILLS[name]
    text = (REPO / "src/claude/skills" / name / "SKILL.md").read_text(encoding="utf-8")
    schema = json.loads((REPO / "src/claude" / pairing["contract"]).read_text(encoding="utf-8"))
    return {"name": name, "text": text, "schema": schema, **pairing}


def test_the_frontmatter_parses_and_names_the_skill(case):
    """A description holding an unquoted `: ` is not a description — it is a mapping the loader
    refuses, and the skill never loads at all. Cheap to write and cheap to break."""
    import yaml
    match = FENCE.match(case["text"])
    assert match, f"{case['name']} carries no frontmatter fence"
    front = yaml.safe_load(match.group(1))
    assert isinstance(front, dict), f"{case['name']}: frontmatter is not a mapping"
    assert front.get("name") == case["name"], \
        "a skill whose name is not its directory's breaks path-based traceability"
    assert isinstance(front.get("description"), str) and front["description"], \
        f"{case['name']}: the description is the trigger, and it must be a non-empty string"


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


def test_every_delegate_is_cited_and_exists(repo, case):
    for name in case["delegates"]:
        assert f"agents/{name}.md" in case["text"], \
            f"{case['name']} delegates to {name} and never cites its file"
        assert (repo / "src/claude/agents" / f"{name}.md").is_file(), \
            f"{case['name']} delegates to {name}, which src/claude/agents does not hold"


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


def shipped_vocabulary() -> list[str]:
    """Every distinctive value the node contracts declare, across all three roots."""
    values: set[str] = set()
    for relative in NODE_CONTRACTS:
        schema = json.loads((REPO / "src/claude" / relative).read_text(encoding="utf-8"))
        values |= {v for v in enum_values(schema) if "-" in v}
    return sorted(values)


def test_the_skill_restates_no_vocabulary(case):
    distinctive = shipped_vocabulary()
    assert distinctive, "the contracts declare no hyphenated vocabulary; the guard lost its subject"
    restated = [v for v in distinctive if v in case["text"]]
    assert restated == [], \
        f"{case['name']} restates {restated}; a vocabulary listed in a prompt is a second home"


INPUT_TERM = re.compile(r"^\d+\. \*\*the ([a-z ]+)\*\*", re.M)


def handoff_blocks(text: str, invocation: str) -> list[str]:
    """Paragraph-shaped chunks holding a handoff, whitespace collapsed so prose may wrap."""
    marker = f"`{invocation}` invocation ready to paste"
    chunks = (re.sub(r"\s+", " ", chunk) for chunk in text.split("\n\n"))
    return [chunk for chunk in chunks if marker in chunk]


def test_the_seam_hands_off_every_input_the_other_skill_requires():
    """The analyse report ends with a /plan-work invocation ready to paste, and the plan report
    and the closure hand open questions back the same way. A handoff that omits an input the
    receiving skill requires reintroduces the stop it exists to spare, so the seam is held
    mechanically: change what one side requires or hands off and this test forces the other
    file into the same change."""
    plan = (REPO / "src/claude/skills/plan-work/SKILL.md").read_text(encoding="utf-8")
    analyse = (REPO / "src/claude/skills/analyse-domain/SKILL.md").read_text(encoding="utf-8")

    plan_inputs = INPUT_TERM.findall(plan)
    assert plan_inputs, "plan-work numbers no required inputs; the seam guard lost its subject"
    outgoing = handoff_blocks(analyse, "/plan-work")
    assert len(outgoing) == 1, "the analyse report ends with exactly one /plan-work handoff"
    for term in plan_inputs:
        assert term in outgoing[0], \
            f"the analyse handoff never names '{term}'; the stop it exists to spare returns"

    analyse_inputs = INPUT_TERM.findall(analyse)
    assert analyse_inputs, "analyse-domain numbers no required inputs; the seam guard lost its subject"
    returning = handoff_blocks(plan, "/analyse-domain")
    assert len(returning) == 2, \
        "the plan report and the closure each hand the open questions back as an invocation"
    for block in returning:
        for term in analyse_inputs:
            assert term in block, \
                f"a questions handoff never names '{term}'; the stop it exists to spare returns"
