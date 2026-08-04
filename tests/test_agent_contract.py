"""Every distributable agent stays bound to its contracts: the frontmatter satisfies
`schemas/agent.json`, the grant is the read-only minimum the role defends, and the body
restates no vocabulary the plan-node contract owns — an enum listed in a prompt is a second
home the moment the schema changes, and the prompt is the copy nothing validates."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator

REPO = Path(__file__).resolve().parent.parent
AGENTS_DIR = REPO / "src/claude/agents"
FENCE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)

AGENTS = ("backlog-decomposer", "codebase-surveyor", "execution-contract-binder")
READ_ONLY = {"Read", "Grep", "Glob"}


@pytest.fixture(scope="module")
def agent_schema() -> Draft202012Validator:
    schema = json.loads((REPO / "schemas/agent.json").read_text(encoding="utf-8"))
    return Draft202012Validator(schema)


@pytest.fixture(params=AGENTS, scope="module")
def agent(request) -> dict:
    path = AGENTS_DIR / f"{request.param}.md"
    match = FENCE.match(path.read_text(encoding="utf-8"))
    assert match, f"{path.name} carries no frontmatter fence"
    return {"stem": request.param,
            "front": yaml.safe_load(match.group(1)),
            "body": match.group(2)}


def test_the_directory_holds_exactly_the_named_agents():
    found = sorted(p.stem for p in AGENTS_DIR.glob("*.md"))
    assert found == sorted(AGENTS), \
        "an agent file nothing names, or a named agent without a file, breaks traceability"


def test_frontmatter_satisfies_the_agent_contract(agent, agent_schema):
    problems = [e.message for e in agent_schema.iter_errors(agent["front"])]
    assert problems == [], f"{agent['stem']}: {problems}"


def test_the_filename_stem_is_the_name(agent):
    assert agent["front"]["name"] == agent["stem"], \
        "a file whose name is not the agent's name breaks path-based traceability"


def test_the_grant_is_the_read_only_minimum(agent):
    tools = agent["front"]["tools"]
    granted = {t.strip() for t in (tools.split(",") if isinstance(tools, str) else tools)}
    assert granted == READ_ONLY, \
        f"{agent['stem']} grants {sorted(granted)}; these agents return content and write " \
        f"nothing, so the grant is exactly {sorted(READ_ONLY)}"


def test_the_agent_restates_no_plan_vocabulary(agent):
    schema = json.loads((REPO / "src/claude/schemas/plan-node.json").read_text(encoding="utf-8"))

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

    distinctive = sorted({v for v in enum_values(schema) if "-" in v})
    assert distinctive, "the schema declares no hyphenated vocabulary; the guard lost its subject"
    text = yaml.safe_dump(agent["front"]) + agent["body"]
    restated = [v for v in distinctive if v in text]
    assert restated == [], \
        f"{agent['stem']} restates {restated}; a vocabulary listed in a prompt is a second home"
