"""The plan contract's own examples pass the gate that will judge real files.

Validated through `plan.node_problems` — the real gate — rather than the raw schema, so the
examples are held to exactly what a plan file is held to. The last test pins the triage
mechanic: unresolved and waived are the record that keeps a plan honest about what the base
leaves open, and a contract that never demonstrates them teaches silence.
"""
from __future__ import annotations

import json

import pytest

import plan


@pytest.fixture(scope="module")
def plan_schema(repo) -> dict:
    return json.loads((repo / "src/claude/schemas/plan-node.json").read_text(encoding="utf-8"))


def branches(schema):
    for branch in schema["allOf"]:
        kind = branch["if"]["properties"]["kind"]["const"]
        yield kind, branch["then"]


def test_every_kind_carries_exactly_one_example(plan_schema):
    kinds = {kind: then.get("examples", []) for kind, then in branches(plan_schema)}
    assert sorted(kinds) == sorted(["inventory", "epic", "task"])
    for kind, examples in kinds.items():
        assert len(examples) == 1, f"{kind} carries {len(examples)} examples; the contract is one"


def test_examples_pass_the_gate(plan_schema):
    validator, allowed = plan.contract()
    for kind, then in branches(plan_schema):
        for example in then["examples"]:
            assert "kind" not in example, f"{kind}: examples omit kind, exactly as a file does"
            problems = plan.node_problems(example, kind, validator, allowed)
            assert problems == [], f"{kind} example: {problems}"


def test_examples_are_yaml_writable_frontmatter(plan_schema):
    import yaml
    for kind, then in branches(plan_schema):
        for example in then["examples"]:
            assert yaml.safe_load(yaml.safe_dump(example)) == example


def test_the_triage_mechanic_is_demonstrated_somewhere(plan_schema):
    examples = [example for _, then in branches(plan_schema) for example in then["examples"]]
    assert any("unresolved" in example for example in examples), \
        "no example demonstrates unresolved, and unresolved is how a plan carries what the " \
        "base leaves open"
    assert any("waived" in example for example in examples), \
        "no example demonstrates a waiver, and the waiver is what keeps the totality " \
        "check honest"
    assert any(isinstance(entry, dict) and "question" in entry
               for example in examples for entry in example.get("unresolved", [])), \
        "no example demonstrates a question — the fact no base node holds"
