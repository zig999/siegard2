"""The contract's own examples pass the gate that will judge real files.

Validated through `graph.node_problems` — the real gate — rather than the raw schema, because
the gap mechanic is validator behaviour: an example demonstrating a gap is schema-invalid on
purpose, and only the gate can say it is right.
"""
from __future__ import annotations

import graph


def tables(schema):
    validator, allowed, obligations = graph.contract()
    return validator, allowed, obligations


def branches(schema):
    for branch in schema["allOf"]:
        kind = branch["if"]["properties"]["kind"]["const"]
        yield kind, branch["then"]


def test_every_kind_carries_exactly_one_example(schema):
    kinds = {kind: then.get("examples", []) for kind, then in branches(schema)}
    assert sorted(kinds) == sorted(
        ["context", "aggregate", "definition", "rule", "lifecycle", "interface", "process"])
    for kind, examples in kinds.items():
        assert len(examples) == 1, f"{kind} carries {len(examples)} examples; the contract is one"


def test_examples_pass_the_gate(schema):
    validator, allowed, obligations = tables(schema)
    for kind, then in branches(schema):
        for example in then["examples"]:
            assert "kind" not in example, f"{kind}: examples omit kind, exactly as a file does"
            problems = graph.node_problems(example, kind, validator, allowed, obligations)
            assert problems == [], f"{kind} example: {problems}"


def test_examples_are_yaml_writable_frontmatter(schema):
    import yaml
    for kind, then in branches(schema):
        for example in then["examples"]:
            assert yaml.safe_load(yaml.safe_dump(example)) == example


def test_the_gap_mechanic_is_demonstrated_somewhere(schema):
    assert any("gaps" in example for _, then in branches(schema)
               for example in then["examples"]), \
        "no example demonstrates a gap, and the gap is the mechanic that keeps the base honest"
