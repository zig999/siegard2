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

NODE_CONTRACTS = ("schemas/plan-node.json", "schemas/delivery-node.json",
                  "schemas/standard.json", "schemas/spec/context.json",
                  "schemas/spec/element.json", "schemas/spec/rule.json",
                  "schemas/spec/scenario.json", "schemas/spec/contract.json",
                  "schemas/spec/constraint.json", "schemas/spec/decision-log.json")

SKILLS = {
    "analyse": {"contract": "schemas/spec/element.json", "validator": "bin/spec.py",
               "delegates": []},
    "siegard-config": {"contract": "schemas/project.json", "validator": "bin/project.py",
                       "delegates": []},
    "plan-work": {"contract": "schemas/plan-node.json", "validator": "bin/plan.py",
                  "delegates": ["codebase-surveyor", "backlog-decomposer",
                                "execution-contract-binder", "unstated-fact-decider"]},
    "implement-task": {"contract": "schemas/delivery-node.json", "validator": "bin/deliver.py",
                       "delegates": ["task-implementer", "test-author"]},
    "review-change": {"contract": "schemas/delivery-node.json", "validator": "bin/deliver.py",
                      "delegates": ["coverage-auditor", "specification-conformance-reviewer",
                                    "standard-conformance-reviewer", "failure-diagnostician"]},
    "reconcile": {"contract": "schemas/reconciliation.json", "validator": "bin/trace.py",
                  "delegates": ["specification-conformance-reviewer"]},
    "siegard-status": {"contract": "schemas/project.json", "validator": "bin/project.py",
                       "delegates": []},
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


@pytest.fixture(scope="module")
def skill_schema():
    from jsonschema import Draft202012Validator
    return Draft202012Validator(
        json.loads((REPO / "schemas/skill.json").read_text(encoding="utf-8")))


MODEL_MAY_REACH = {
    "analyse": True,
    "plan-work": True,
    "implement-task": True,
    "review-change": True,
    "reconcile": True,
    "siegard-config": False,
    # Read-only and input-free beyond the project root: nothing here is the human's to assert,
    # so a session may reach for it when asked how the work stands — that reachability is the
    # skill's point.
    "siegard-status": True,
}


def test_only_the_declared_skills_are_closed_to_the_model(case):
    """Which entry points a session may load by itself is a policy, and until this test existed it
    lived in three YAML values that no commit message, rule or schema ever explained — which is how
    a skill authored beside another inherited the flag by copying the file next to it.

    The criterion is who has the right to state the input, and never how much the skill writes:
    `/implement-task` writes source, installs packages and runs commands, and is reachable, while
    `/siegard-config` writes one JSON file every other entry point reads, and is not. The reachable
    ones are held by what is inside them — an input nobody named is a stop, a pending root is a
    stop, a judgment is delegated — and by the fact that a skill's description is the only
    instruction that reaches a plugin install at all. A new skill has to appear here to ship, which
    is the point: the decision gets made rather than inherited."""
    import yaml
    assert sorted(MODEL_MAY_REACH) == sorted(SKILLS), \
        "a skill was added or removed without deciding whether a session may reach for it"
    front = yaml.safe_load(FENCE.match(case["text"]).group(1))
    closed = front.get("disable-model-invocation", False)
    assert closed is not MODEL_MAY_REACH[case["name"]], \
        f"{case['name']}: the frontmatter and the policy disagree about who may invoke it"


def test_frontmatter_satisfies_the_skill_contract(case, skill_schema):
    """The agents have been held to `schemas/agent.json` since they shipped; the skills were held
    to nothing but a name-and-description spot check. The contract sets `additionalProperties:
    false` precisely because Claude Code ignores a frontmatter key it does not recognise — so a
    misspelled field, or a value outside a closed vocabulary like `effort`, ships as a silent
    no-op. Nothing else in this suite would notice."""
    import yaml
    front = yaml.safe_load(FENCE.match(case["text"]).group(1))
    problems = [e.message for e in skill_schema.iter_errors(front)]
    assert problems == [], f"{case['name']}: {problems}"


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


def skill_text(name: str) -> str:
    return (REPO / "src/claude/skills" / name / "SKILL.md").read_text(encoding="utf-8")


# analyse-domain -> plan-work stays absent for good: analyse-domain is retired, not renamed,
# and it authors the pre-redesign knowledge base plan-work no longer accepts. Its replacement is
# named below instead of appended beside it.
FORWARD_SEAMS = (
    ("analyse", "plan-work"),
    ("plan-work", "implement-task"),
    ("implement-task", "review-change"),
    ("reconcile", "analyse"),
    ("reconcile", "plan-work"),
)


@pytest.mark.parametrize("handing,receiving", FORWARD_SEAMS)
def test_the_seam_hands_off_every_input_the_other_skill_requires(handing, receiving):
    """Each report ends with the next skill's invocation ready to paste. A handoff that omits an
    input the receiving skill requires reintroduces the stop it exists to spare, so every seam is
    held mechanically: change what one side requires or hands off and this test forces the other
    file into the same change. Every forward seam is covered — a seam left out of this list is a
    seam where the two files can drift apart in silence, which is how the first two ended up being
    the only ones anybody checked."""
    required = INPUT_TERM.findall(skill_text(receiving))
    assert required, f"{receiving} numbers no required inputs; the seam guard lost its subject"
    outgoing = handoff_blocks(skill_text(handing), f"/{receiving}")
    assert len(outgoing) == 1, \
        f"the {handing} report ends with exactly one /{receiving} handoff"
    for term in required:
        assert term in outgoing[0], \
            f"the {handing} handoff never names '{term}'; the stop it exists to spare returns"


# test_the_plan_hands_open_questions_back_to_the_analysis retired with it: it held plan-work to
# a fixed two-block /analyse-domain handoff carrying gaps and questions, and neither exists any
# more — the specification never carries an open fact under decide-and-disclose, so there is
# nothing left to hand back in that shape. What replaces it is a blocking note, reported by
# plan-work and implement-task alike but pointed at no fixed invocation — a route named in prose
# ("through /analyse extending the specification"), never a filled slot the way a real handoff
# is. A seam test for it would be checking a sentence, not a contract, and stays unwritten for
# that reason rather than for want of a name.


def test_the_review_hands_nothing_forward_as_an_invocation():
    """The one skill that ends the chain, and deliberately: which route a finding deserves — or
    whether it deserves one — is the decision this pass does not make. A pasteable invocation here
    would be that decision, taken by the reviewer, so its absence is held rather than assumed."""
    text = skill_text("review-change")
    assert handoff_blocks(text, "/implement-task") == []
    assert handoff_blocks(text, "/plan-work") == []
    assert handoff_blocks(text, "/analyse") == []
