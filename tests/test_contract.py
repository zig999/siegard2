"""The composed contract, and the tree it is composed from.

Two things are held here. That `domain/` composes at all — the sibling `$ref`s resolve, the tables
splice, and the result is a schema — and that the committed `src/claude/schemas/domain-object.json`
is what that composition produces. The second is what stops the tree and the shipped file becoming
two homes for one set of facts.

The behaviour cases are run against a freshly composed document rather than the committed one, so a
failure says the tree is wrong rather than that somebody forgot to run the composer.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys

import pytest
import yaml
from jsonschema import Draft202012Validator

import compose_domain


@pytest.fixture(scope="module")
def composed() -> dict:
    document, _ = compose_domain.compose()
    return document


@pytest.fixture(scope="module")
def validator(composed) -> Draft202012Validator:
    Draft202012Validator.check_schema(composed)
    return Draft202012Validator(composed)


@pytest.fixture
def build(composed):
    """A frontmatter mapping stamped with whatever version the tree currently pins."""
    def make(node_id: str, kind: str, **extra) -> dict:
        return {"id": node_id, "type": kind, "title": "T",
                "contract_version": composed["properties"]["contract_version"]["const"],
                "generated": {"by": "test", "at": "2026-08-02T00:00:00Z"},
                "origin": "stated", "question": "q?", "description": "d", "out_of_scope": ["x"],
                **extra}
    return make


def definition(build, **extra):
    return build("dm.definition.sales.order", "definition",
                 **{"ddd": "value-object", "boundary": "dm.context.sales",
                    "attributes": [{"name": "total", "type": "money"}], **extra})


def accepts(validator, instance) -> bool:
    return not list(validator.iter_errors(instance))


# ---- the tree composes -----------------------------------------------------------------------

def test_the_composed_document_is_a_schema(composed):
    Draft202012Validator.check_schema(composed)


def test_it_carries_one_block_per_kind_and_one_per_cross_kind_rule(composed):
    kinds = len(compose_domain.KINDS)
    rules = len(compose_domain.load(compose_domain.DOMAIN / "tables" / "invariants.json")["x-cross-kind"])
    assert len(composed["allOf"]) == kinds + rules


def test_it_is_self_contained(composed):
    """A consumer's boundary validator loads it standalone, and a cross-file `$ref` would be
    resolved over the network."""
    external = [ref for ref in re.findall(r'"\$ref": "([^"]+)"', json.dumps(composed))
                if not ref.startswith("#/")]
    assert external == []


def test_it_holds_no_definition_nothing_references(composed):
    """Dead representation in a shipped file. The composer drops them and names what it dropped."""
    used = set(re.findall(r'"#/\$defs/(\w+)"', json.dumps(composed)))
    assert set(composed["$defs"]) - used == set()


def test_the_committed_contract_is_what_the_tree_composes_to(repo):
    """Otherwise the tree and the shipped file are two homes for one set of facts, and the shipped
    one wins by being the file anything reads."""
    done = subprocess.run([sys.executable, str(repo / "scripts/compose_domain.py"), "--check"],
                          capture_output=True, text=True)
    assert done.returncode == 0, done.stdout + done.stderr


# ---- what the contract accepts and refuses -------------------------------------------------------

def test_a_complete_definition(validator, build):
    assert accepts(validator, definition(build))


def test_a_gap_naming_the_missing_field_excuses_it(validator, build):
    node = definition(build, gaps=[{"kind": "domain", "field": "boundary", "why": "unstated"}])
    del node["boundary"]
    assert accepts(validator, node)


def test_a_gap_about_another_field_does_not(validator, build):
    """A single alternation per kind is satisfied by any gap over any field, so a gap about `owner`
    would excuse a missing `boundary` — and `boundary` is the parent pointer."""
    node = definition(build, gaps=[{"kind": "domain", "field": "owner", "why": "unstated"}])
    del node["boundary"]
    assert not accepts(validator, node)


@pytest.mark.parametrize("boundary, ok", [
    ("dm.context.sales", True),
    ("dm.aggregate.sales.order", True),
    ("dm.context.sales.orders", False),
    ("dm.aggregate.order", False),
])
def test_a_boundary_names_a_scope_this_profile_holds(validator, build, boundary, ok):
    assert accepts(validator, definition(build, boundary=boundary)) is ok


@pytest.mark.parametrize("ddd, needs_identity", [
    ("entity", True), ("aggregate-root", True), ("read-model", True),
    ("value-object", False), ("domain-error", False),
])
def test_which_definitions_declare_an_identity(validator, build, ddd, needs_identity):
    node = definition(build, ddd=ddd, attributes=[{"name": "reference", "type": "string",
                                                   "max_length": 40}])
    assert accepts(validator, node) is not needs_identity
    node["identity"] = {"attributes": ["reference"]}
    assert accepts(validator, node)


def test_a_scope_declares_no_boundary(validator, build):
    node = build("dm.subdomain.sales", "subdomain", subdomain_type="core")
    assert accepts(validator, node)
    assert not accepts(validator, dict(node, boundary="dm.context.sales"))


def test_a_kind_that_is_its_own_construct_declares_no_ddd(validator, build):
    node = build("dm.aggregate.sales.order", "aggregate", boundary="dm.context.sales",
                 root="dm.definition.sales.order")
    assert accepts(validator, node)
    assert not accepts(validator, dict(node, ddd="entity"))


def test_a_modeled_fact_carries_its_reason(validator, build):
    """A reviewer accepts a fact the material stated and disagrees with one the analysis reached,
    and can do the second only against a reason."""
    node = definition(build, origin="modeled")
    assert not accepts(validator, node)
    assert accepts(validator, dict(node, rationale="the material implies it"))


def test_status_is_rejected_rather_than_absent(validator, build):
    assert not accepts(validator, definition(build, status="draft"))


def test_only_a_context_relates_to_a_context(validator, build):
    node = definition(build, context_relationships=[{"with": "dm.context.billing",
                                                     "pattern": "shared-kernel"}])
    assert not accepts(validator, node)


@pytest.mark.parametrize("pattern, role, ok", [
    ("customer-supplier", "downstream", True),
    ("customer-supplier", None, False),
    ("shared-kernel", None, True),
    ("shared-kernel", "upstream", False),
    ("partnership", None, True),
])
def test_a_directional_relationship_names_its_side(validator, build, pattern, role, ok):
    entry = {"with": "dm.context.billing", "pattern": pattern}
    if role:
        entry["role"] = role
    node = build("dm.context.sales", "context", subdomain="dm.subdomain.commerce",
                 context_relationships=[entry])
    assert accepts(validator, node) is ok


@pytest.mark.parametrize("ddd, needs_payload", [
    ("domain-event", True), ("integration-event", True), ("published-language", True),
    ("command", True), ("api", False),
])
def test_which_interfaces_carry_a_payload(validator, build, ddd, needs_payload):
    node = build("dm.interface.sales.placed", "interface", boundary="dm.context.sales", ddd=ddd,
                 version="2", schema="c.json", ownership="published")
    assert accepts(validator, node) is not needs_payload
    assert accepts(validator, dict(node, payload="dm.definition.sales.placed"))


@pytest.mark.parametrize("ownership, upstream, ok", [
    ("consumed", "dm.interface.billing.placed", True),
    ("consumed", None, False),
    ("published", None, True),
    ("published", "dm.interface.billing.placed", False),
])
def test_only_a_consumed_interface_names_what_it_consumes(validator, build, ownership, upstream, ok):
    node = build("dm.interface.sales.placed", "interface", boundary="dm.context.sales",
                 ddd="domain-event", version="2", schema="c.json", ownership=ownership,
                 payload="dm.definition.sales.placed")
    if upstream:
        node["upstream"] = upstream
    assert accepts(validator, node) is ok


def test_an_authoring_gap_excuses_the_three_the_enrichment_owns(validator, build):
    node = build("dm.subdomain.sales", "subdomain", subdomain_type="core")
    for field in ("question", "description", "out_of_scope"):
        del node[field]
    assert not accepts(validator, node)
    assert accepts(validator, dict(node, gaps=[{"kind": "authoring", "field": "description"}]))


# ---- the scaffolds produce nodes the contract accepts ------------------------------------------------

FILL = {
    "context": "sales", "slug": "order", "subdomain_slug": "commerce", "root_slug": "order",
    "boundary_slug": "order", "error_slug": "already-paid", "first_step_slug": "order",
    "payload_slug": "order-placed-payload", "title": "Order",
    "description": "What a customer asked to buy.", "question": "What did the customer ask to buy?",
    "out_of_scope": "payment routing", "generated_by": "test",
    "generated_at": "2026-08-02T00:00:00Z", "origin": "stated", "subdomain_type": "core",
    "attribute_name": "reference", "attribute_max_length": "40", "version": "2",
    "schema": "contracts/order.v2.json", "ownership": "published",
    "statement": "An order carries at least one line.", "expression": "lines.count >= 1",
    "initial_state": "new", "next_state": "paid", "trigger": "pay",
    "invariant": "carry at least one line", "responsibility": "the order book",
    "outcome": "a placed order", "condition": "An order MUST carry at least one line",
    "state_meaning": "awaits payment", "payload_meaning": "the order that was placed",
}
DDD = {"definition": "entity", "rule": "invariant", "interface": "domain-event",
       "process": "use-case"}
KINDS = sorted(compose_domain.KINDS)


@pytest.fixture(scope="module")
def sections(repo) -> dict:
    return json.loads((repo / "domain/tables/body-sections.json").read_text())["x-sections"]


@pytest.fixture
def rendered(repo):
    def render(kind: str) -> tuple[dict, str]:
        text = (repo / f"src/claude/templates/domain-object-{kind}.md").read_text(encoding="utf-8")
        fill = dict(FILL, ddd=DDD.get(kind, ""))
        unknown = {m for m in re.findall(r"\{\{(\w+)\}\}", text) if m not in fill}
        assert not unknown, f"the scaffold names placeholders this test cannot fill: {unknown}"
        filled = re.sub(r"\{\{(\w+)\}\}", lambda m: fill[m.group(1)], text)
        match = re.match(r"^---\n(.*?)\n---\n", filled, re.S)
        assert match, "the scaffold carries no frontmatter fence"
        return yaml.safe_load(match.group(1)), filled[match.end():]
    return render


@pytest.mark.parametrize("kind", KINDS)
def test_a_scaffold_renders_to_a_node_the_contract_accepts(validator, rendered, kind):
    """A scaffold that produces a node the contract refuses is worse than no scaffold: the refusal
    arrives after the writing, and it names the contract rather than the template."""
    frontmatter, _ = rendered(kind)
    errors = sorted(validator.iter_errors(frontmatter), key=str)
    assert not errors, "; ".join(e.message for e in errors[:3])


@pytest.mark.parametrize("kind", KINDS)
def test_a_scaffold_pins_the_version_the_contract_pins(composed, rendered, kind):
    frontmatter, _ = rendered(kind)
    assert frontmatter["contract_version"] == composed["properties"]["contract_version"]["const"]


@pytest.mark.parametrize("kind", KINDS)
def test_a_scaffold_carries_the_two_headings_its_kind_names(sections, rendered, kind):
    _, body = rendered(kind)
    assert [line.strip() for line in body.splitlines() if line.startswith("## ")] == sections[kind]
