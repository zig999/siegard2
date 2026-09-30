"""Every distributable agent stays bound to its contracts: the frontmatter satisfies
`schemas/agent.json`, the grant is the minimum the role defends, and the body restates no
vocabulary a node contract owns — an enum listed in a prompt is a second home the moment the
schema changes, and the prompt is the copy nothing validates.

The grant table is the interesting part. Most of these agents return content and write nothing, so
their grant is read-only. Two of them write — the source, and the tests over it — and their grant
says so explicitly. **None of them holds Bash**, and that is the structural half of a guarantee no
prompt can make: an agent that could run a suite would be the only witness to what happened, so
running lives in `bin/run.py` and nowhere else.

This became load-bearing rather than decorative when the skills started to execute. `/implement-task`
now installs and builds, and `/review-change` runs the steps a registry declares — but they do it
through the runner, whose refusal to reuse a slug is what makes every attempt readable afterwards.
An agent that quietly gained Bash would run outside that capture, and what it saw would exist only
in a context nobody else can open. If the assertion below ever fails, the widening leaked.
"""
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

READS = {"Read", "Grep", "Glob"}
WRITES = READS | {"Write", "Edit"}

# Every shipped agent, and the grant its role defends. A grant wider than the role is a finding
# here, not a preference: the tools are the enforcement, and the prose is only the explanation.
GRANTS = {
    "backlog-decomposer": READS,
    "specification-conformance-reviewer": READS,
    "codebase-surveyor": READS,
    "domain-surveyor": READS,
    "coverage-auditor": READS,
    "execution-contract-binder": READS,
    "failure-diagnostician": READS,
    "standard-conformance-reviewer": READS,
    "task-implementer": WRITES,
    "test-author": WRITES,
    "unstated-fact-decider": READS,
}
AGENTS = tuple(sorted(GRANTS))


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


def granted(front: dict) -> set[str]:
    tools = front["tools"]
    return {t.strip() for t in (tools.split(",") if isinstance(tools, str) else tools)}


def test_the_directory_holds_exactly_the_named_agents():
    found = sorted(p.stem for p in AGENTS_DIR.glob("*.md"))
    assert found == sorted(AGENTS), \
        "an agent file nothing names, or a named agent without a file, breaks traceability"


def test_every_agent_is_some_skills_delegate():
    from test_skill_contract import SKILLS
    delegated = sorted({name for case in SKILLS.values() for name in case["delegates"]})
    assert delegated == sorted(AGENTS), \
        "an agent no skill delegates to is dead weight, and a delegate this suite does not " \
        "hold to the agent contract is untested — the two lists are one truth"


def test_frontmatter_satisfies_the_agent_contract(agent, agent_schema):
    problems = [e.message for e in agent_schema.iter_errors(agent["front"])]
    assert problems == [], f"{agent['stem']}: {problems}"


def test_the_filename_stem_is_the_name(agent):
    assert agent["front"]["name"] == agent["stem"], \
        "a file whose name is not the agent's name breaks path-based traceability"


def test_the_grant_is_the_minimum_the_role_defends(agent):
    assert granted(agent["front"]) == GRANTS[agent["stem"]], \
        f"{agent['stem']} grants {sorted(granted(agent['front']))}; its role defends exactly " \
        f"{sorted(GRANTS[agent['stem']])}"


def test_no_agent_can_run_anything(agent):
    forbidden = granted(agent["front"]) & {"Bash", "BashOutput", "KillShell"}
    assert forbidden == set(), \
        f"{agent['stem']} grants {sorted(forbidden)}; nothing that judges a run may perform " \
        f"one, and nothing that writes source may witness whether it passed — running is " \
        f"bin/run.py's and nothing else's"


def test_only_the_writers_write(agent):
    writes = granted(agent["front"]) & {"Write", "Edit"}
    if agent["stem"] in ("task-implementer", "test-author"):
        assert writes == {"Write", "Edit"}, \
            f"{agent['stem']} writes what the delivery is made of and needs both"
    else:
        assert writes == set(), \
            f"{agent['stem']} grants {sorted(writes)}; it returns content and the caller " \
            f"writes it, so a reviewer cannot edit what it flagged"


def test_the_agent_restates_no_node_vocabulary(agent):
    from test_skill_contract import shipped_vocabulary
    distinctive = shipped_vocabulary()
    assert distinctive, "the contracts declare no hyphenated vocabulary; the guard lost its subject"
    text = yaml.safe_dump(agent["front"]) + agent["body"]
    restated = [v for v in distinctive if v in text]
    assert restated == [], \
        f"{agent['stem']} restates {restated}; a vocabulary listed in a prompt is a second home"


# Fields the harness ignores when it loads an agent from a plugin, which is the only shape this
# framework is distributed in. The contract still admits them — an agent copied into a repository's
# own `.claude/agents/` would get them — so what has to be guarded is that nothing *shipped*
# declares one.
INERT_FOR_A_PLUGIN_SUBAGENT = ("hooks", "mcpServers", "permissionMode")


@pytest.mark.parametrize("field", INERT_FOR_A_PLUGIN_SUBAGENT)
def test_no_shipped_agent_declares_a_field_a_plugin_subagent_ignores(field, agent):
    """A field the harness ignores is worse here than a field that does not exist: it passes this
    contract, passes this suite, ships to every consumer, and takes no effect — and nothing inside
    this repository can tell. That is the same species as a check whose command was `true`.

    The cost is not hypothetical. `permissionMode`'s own description carried a deliberate,
    reasoned exclusion of `bypassPermissions` — a security decision recorded about a field that
    never took effect in the shape this framework ships."""
    assert field not in agent["front"], \
        f"{agent['stem']} declares `{field}`, which the harness ignores for a plugin subagent; " \
        f"it would read as a live constraint and enforce nothing"


@pytest.mark.parametrize("field", INERT_FOR_A_PLUGIN_SUBAGENT)
def test_the_contract_says_which_fields_a_plugin_subagent_ignores(field):
    """The guard above refuses the field; this one holds the contract to saying why, so a reader
    deciding whether to reach for it learns it is inert before writing it rather than after."""
    schema = json.loads((REPO / "schemas/agent.json").read_text(encoding="utf-8"))
    described = schema["properties"][field]["description"]
    assert "Inert" in described and "plugin" in described, \
        f"the contract admits `{field}` without saying a plugin subagent ignores it"
