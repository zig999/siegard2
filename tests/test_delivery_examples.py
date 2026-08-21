"""The delivery contract's own examples pass the gate that will judge real files.

Validated through `deliver.node_problems` — the real gate — rather than the raw schema, so the
examples are held to exactly what a delivery file is held to. The last tests pin the mechanics a
contract that never demonstrated them would teach nothing about: that a record accounts for every
bound node including the ones it only honored, that an inference is written down rather than
hidden, and that a pass which did not run says which input was missing.
"""
from __future__ import annotations

import json

import pytest

import deliver


@pytest.fixture(scope="module")
def delivery_schema(repo) -> dict:
    return json.loads(
        (repo / "src/claude/schemas/delivery-node.json").read_text(encoding="utf-8"))


def branches(schema):
    for branch in schema["allOf"]:
        kind = branch["if"]["properties"]["kind"]["const"]
        yield kind, branch["then"]


def examples_of(schema) -> list[dict]:
    return [example for _, then in branches(schema) for example in then["examples"]]


def test_every_kind_carries_exactly_one_example(delivery_schema):
    kinds = {kind: then.get("examples", []) for kind, then in branches(delivery_schema)}
    assert sorted(kinds) == sorted(["implementation", "proof", "review"])
    for kind, examples in kinds.items():
        assert len(examples) == 1, f"{kind} carries {len(examples)} examples; the contract is one"


def test_examples_pass_the_gate(delivery_schema):
    validator = deliver.contract()
    names = deliver.pass_names()
    for kind, then in branches(delivery_schema):
        for example in then["examples"]:
            assert "kind" not in example, f"{kind}: examples omit kind, exactly as a file does"
            problems = deliver.node_problems(example, kind, validator, names)
            assert problems == [], f"{kind} example: {problems}"


def test_examples_are_yaml_writable_frontmatter(delivery_schema):
    import yaml
    for _, then in branches(delivery_schema):
        for example in then["examples"]:
            assert yaml.safe_load(yaml.safe_dump(example)) == example


def test_the_node_accounting_is_demonstrated_both_ways(delivery_schema):
    entries = [entry for example in examples_of(delivery_schema)
               for entry in example.get("nodes", [])]
    assert entries, "no example demonstrates how a record answers to the nodes its task bound"
    assert any("encoded_at" in entry for entry in entries), \
        "no example shows a fact of the base reaching the source, which is the traceability " \
        "the whole field exists for"


def test_an_inference_is_demonstrated(delivery_schema):
    assert any("inferences" in example for example in examples_of(delivery_schema)), \
        "no example records an inference, and an inference nobody records is a decision that " \
        "reads like one the business made"


def test_a_pass_that_did_not_run_is_demonstrated(delivery_schema):
    entries = [entry for example in examples_of(delivery_schema)
               for entry in example.get("passes", [])]
    assert entries, "no example demonstrates the passes a review answers for"
    assert any("missing" in entry for entry in entries), \
        "no example shows a pass that did not run naming what was absent — a contract that " \
        "never demonstrates it teaches a review to read as clean when it was only narrow"


def test_no_example_offers_a_figure_or_a_verdict(delivery_schema):
    forbidden = ("status", "verdict", "approved", "ready", "severity", "score", "percentage")
    for example in examples_of(delivery_schema):
        present = sorted(k for k in example if k in forbidden)
        assert present == [], \
            f"an example carries {present}; a number that must rise becomes a target, and a " \
            f"verdict in a record is the reviewer becoming the gate"
