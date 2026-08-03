"""`graph.py` — one walk, two modes: the gate a node passes, the checks that need the whole
base, and the derived graph held to the files."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

import graph

GRAPH_PY = Path(graph.__file__)


def run(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(GRAPH_PY), *map(str, args)],
                          capture_output=True, text=True)


def problems_in(root) -> list[str]:
    validator, allowed, obligations = graph.contract()
    nodes, problems = graph.collect(root, validator, allowed, obligations)
    return sorted(set(problems + graph.cross_problems(nodes)))


# ---------------------------------------------------------------- the sound path

def test_a_sound_base_derives_and_checks_clean(root, sound_base):
    done = run(root)
    assert done.returncode == 0, done.stdout + done.stderr
    assert (root / "graph.json").is_file()
    assert run("--check", root).returncode == 0


def test_derivation_is_deterministic(root, sound_base):
    assert run(root).returncode == 0
    first = (root / "graph.json").read_bytes()
    assert run(root).returncode == 0
    assert (root / "graph.json").read_bytes() == first


def test_the_derived_graph_satisfies_its_own_contract(repo, root, sound_base):
    from jsonschema import Draft202012Validator
    assert run(root).returncode == 0
    contract = json.loads((repo / "src/claude/schemas/graph.json").read_text())
    derived = json.loads((root / "graph.json").read_text())
    assert list(Draft202012Validator(contract).iter_errors(derived)) == []


def test_node_entries_carry_the_index_and_edges_the_locator(root, sound_base):
    assert run(root).returncode == 0
    derived = json.loads((root / "graph.json").read_text())
    order = next(n for n in derived["nodes"] if n["id"] == "definition/sales/order")
    assert order["kind"] == "definition"
    assert order["file"] == "definition/sales/order.md"
    assert order["context"] == "sales"
    assert order["aggregate"] == "orders"
    assert order["ddd"] == "aggregate-root"
    assert "gaps" not in order
    edge = next(e for e in derived["edges"] if e["kind"] == "aggregate")
    assert edge == {"from": "definition/sales/order", "to": "aggregate/sales/orders",
                    "kind": "aggregate", "at": "aggregate"}


def test_the_derivation_summary_counts_kinds_gaps_and_rationale(root, sound_base):
    sound_base("definition/sales/customer", {
        "title": "Customer", "summary": "Who buys.", "ddd": "value-object",
        "rationale": "The analysis decided this shape.",
        "attributes": [{"name": "name", "type": "string"}],
        "gaps": [{"field": "aggregate", "why": "Nobody said where it sits."}]})
    done = run(root)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "1 context, 1 aggregate, 2 definition" in done.stdout
    assert "1 gap(s)" in done.stdout
    assert "1 node(s) with rationale" in done.stdout


# ---------------------------------------------------------------- staleness

def test_check_before_any_derivation_is_stale(root, sound_base):
    done = run("--check", root)
    assert done.returncode == 1
    assert "STALE" in done.stdout


def test_check_after_an_edit_is_stale(root, sound_base):
    assert run(root).returncode == 0
    sound_base("definition/sales/customer", {
        "title": "Customer", "summary": "Who buys.", "ddd": "value-object",
        "attributes": [{"name": "name", "type": "string", "max_length": 80}]})
    done = run("--check", root)
    assert done.returncode == 1
    assert "STALE" in done.stdout


# ---------------------------------------------------------------- refusals

def test_a_broken_reference_refuses_the_derivation(root, sound_base):
    sound_base("rule/sales/positive-total", {
        "title": "Positive total", "summary": "Totals are positive.",
        "ddd": "invariant", "aggregate": "orders",
        "statement": "A total MUST be positive.",
        "constrains": ["definition/sales/nothing"]})
    done = run(root)
    assert done.returncode == 1
    assert "definition/sales/nothing" in done.stdout
    assert not (root / "graph.json").is_file()


def test_a_stray_file_is_reported(root, sound_base):
    (root / "notes.md").write_text("scratch\n")
    assert any("notes.md" in p for p in problems_in(root))


def test_an_unknown_field_is_refused(root, sound_base):
    sound_base("context/billing", {"title": "Billing", "summary": "Invoices.",
                                   "strategic": "supporting", "status": "draft"})
    assert any("status" in p for p in problems_in(root))


def test_a_field_of_another_kind_is_refused(root, sound_base):
    sound_base("context/billing", {"title": "Billing", "summary": "Invoices.",
                                   "strategic": "supporting",
                                   "steps": [{"node": "context/sales"}]})
    assert any("steps" in p and "context/billing" in p for p in problems_in(root))


def test_wrong_body_headings_are_refused(root, sound_base):
    sound_base("context/billing",
               {"title": "Billing", "summary": "Invoices.", "strategic": "supporting"},
               body="## Answer\nX.\n\n## Rules\nNone.\n")
    assert any("headings" in p for p in problems_in(root))


# ---------------------------------------------------------------- the gap discipline

def test_a_gap_excuses_the_field_it_names(root, sound_base):
    sound_base("definition/sales/invoice", {
        "title": "Invoice", "summary": "The bill.", "ddd": "value-object",
        "gaps": [{"field": "attributes", "why": "the material lists no fields"}]})
    assert problems_in(root) == []


def test_an_absence_no_gap_names_is_refused(root, sound_base):
    sound_base("definition/sales/invoice",
               {"title": "Invoice", "summary": "The bill.", "ddd": "value-object"})
    assert any("attributes" in p for p in problems_in(root))


def test_a_gap_never_excuses_a_field_it_does_not_name(root, sound_base):
    sound_base("definition/sales/invoice", {
        "title": "Invoice", "summary": "The bill.",
        "gaps": [{"field": "attributes", "why": "unstated"}]})
    assert any("'ddd' is a required property" in p for p in problems_in(root))


def test_a_gap_on_a_declared_field_is_refused(root, sound_base):
    sound_base("definition/sales/invoice", {
        "title": "Invoice", "summary": "The bill.", "ddd": "value-object",
        "attributes": [{"name": "number", "type": "string", "max_length": 10}],
        "gaps": [{"field": "attributes", "why": "but it is right there"}]})
    assert any("absent fact" in p for p in problems_in(root))


def test_a_gap_on_a_field_the_kind_never_declares_is_refused(root, sound_base):
    sound_base("definition/sales/invoice", {
        "title": "Invoice", "summary": "The bill.", "ddd": "value-object",
        "attributes": [{"name": "number", "type": "string", "max_length": 10}],
        "gaps": [{"field": "steps", "why": "wrong kind entirely"}]})
    assert any("not a field a definition declares" in p for p in problems_in(root))


def test_a_dotted_gap_needs_its_container_present(root, sound_base):
    sound_base("definition/sales/invoice", {
        "title": "Invoice", "summary": "The bill.", "ddd": "value-object",
        "attributes": [{"name": "number", "type": "string"}],
        "gaps": [{"field": "attributes.number.max_length", "why": "no bound stated"}]})
    assert problems_in(root) == []
    sound_base("definition/sales/receipt", {
        "title": "Receipt", "summary": "Proof.", "ddd": "value-object",
        "gaps": [{"field": "attributes", "why": "unstated"},
                 {"field": "identity.attributes", "why": "container is absent"}]})
    assert any("points inside `identity`" in p for p in problems_in(root))


# ---------------------------------------------------------------- cross-node rules

def test_two_lifecycles_cannot_claim_one_subject(root, sound_base):
    for slug in ("order", "order-again"):
        sound_base(f"lifecycle/sales/{slug}", {
            "title": "Order lifecycle", "summary": "States of an order.",
            "subject": "definition/sales/order",
            "states": ["draft", "done"], "initial": "draft", "terminal": ["done"],
            "transitions": [{"from": "draft", "trigger": "finish", "to": "done"}]})
    assert any("both claim definition/sales/order" in p for p in problems_in(root))


def test_an_aggregate_needs_exactly_one_root(root, write):
    write("context/sales", {"title": "Sales", "summary": "Ordering.", "strategic": "core"})
    write("aggregate/sales/orders", {"title": "Orders", "summary": "Together."})
    assert any("aggregate/sales/orders" in p and "root" in p for p in problems_in(root))
    for slug in ("order", "order-header"):
        write(f"definition/sales/{slug}", {
            "title": slug, "summary": "A root.", "ddd": "aggregate-root",
            "aggregate": "orders", "identity": ["number"],
            "attributes": [{"name": "number", "type": "string", "max_length": 9}]})
    assert any("2 definitions claim its root" in p for p in problems_in(root))


def test_a_consumed_interface_ends_at_a_published_one(root, sound_base):
    sound_base("interface/sales/order-feed", {
        "title": "Order feed", "summary": "Orders, streamed.",
        "ddd": "api", "ownership": "consumed", "upstream": "interface/sales/other-feed"})
    sound_base("interface/sales/other-feed", {
        "title": "Other feed", "summary": "Also consumed.",
        "ddd": "api", "ownership": "consumed", "upstream": "interface/sales/order-feed"})
    assert sum("ownership is not published" in p for p in problems_in(root)) == 2


def test_a_transition_emits_an_event_not_an_api(root, sound_base):
    sound_base("interface/sales/order-api", {
        "title": "Order API", "summary": "Operations on orders.",
        "ddd": "api", "ownership": "published"})
    sound_base("lifecycle/sales/order", {
        "title": "Order lifecycle", "summary": "States of an order.",
        "subject": "definition/sales/order",
        "states": ["draft", "done"], "initial": "draft", "terminal": ["done"],
        "transitions": [{"from": "draft", "trigger": "finish", "to": "done",
                         "emits": ["interface/sales/order-api"]}]})
    assert any("a state change raises an event" in p for p in problems_in(root))


def test_totality_covers_nonterminal_states_and_exempts_terminal_ones(root, sound_base):
    sound_base("lifecycle/sales/order", {
        "title": "Order lifecycle", "summary": "States of an order.",
        "subject": "definition/sales/order",
        "states": ["draft", "placed", "done"], "initial": "draft", "terminal": ["done"],
        "transitions": [{"from": "draft", "trigger": "place", "to": "placed"}]})
    problems = problems_in(root)
    assert any("state `placed` has no transition and no rejection for trigger `place`" in p
               for p in problems)
    assert not any("state `done`" in p for p in problems)


def test_a_rule_reaching_outside_its_aggregate_declares_consistency(root, sound_base):
    sound_base("aggregate/sales/shipments", {"title": "Shipments", "summary": "Together."})
    sound_base("definition/sales/shipment", {
        "title": "Shipment", "summary": "A shipment.", "ddd": "aggregate-root",
        "aggregate": "shipments", "identity": ["number"],
        "attributes": [{"name": "number", "type": "string", "max_length": 9}]})
    rule = {"title": "Ship only paid", "summary": "No unpaid order ships.",
            "ddd": "invariant", "aggregate": "orders",
            "statement": "An unpaid order MUST NOT ship.",
            "constrains": ["definition/sales/shipment"]}
    sound_base("rule/sales/ship-only-paid", rule)
    assert any("declares no consistency" in p for p in problems_in(root))
    sound_base("rule/sales/ship-only-paid", {**rule, "consistency": "eventual"})
    assert problems_in(root) == []


# ---------------------------------------------------------------- schema-level shapes

def test_a_directional_relationship_carries_a_role_and_a_symmetric_one_refuses_it(root, write):
    write("context/sales", {
        "title": "Sales", "summary": "Ordering.", "strategic": "core",
        "relationships": [{"with": "billing", "pattern": "conformist"}]})
    write("context/billing", {
        "title": "Billing", "summary": "Invoices.", "strategic": "supporting",
        "relationships": [{"with": "sales", "pattern": "partnership", "role": "upstream"}]})
    problems = problems_in(root)
    assert any("context/sales" in p and "role" in p for p in problems)
    assert any("context/billing" in p for p in problems)


def test_an_enum_attribute_takes_values_or_a_lifecycle_never_both(root, sound_base):
    sound_base("definition/sales/invoice", {
        "title": "Invoice", "summary": "The bill.", "ddd": "value-object",
        "attributes": [{"name": "state", "type": "enum",
                        "values": ["open"], "lifecycle": "lifecycle/sales/order"}]})
    assert any("attributes.0" in p for p in problems_in(root))


# ---------------------------------------------------------------- --node

def test_single_node_mode_ignores_unresolved_references(root, sound_base):
    path = sound_base("rule/sales/positive-total", {
        "title": "Positive total", "summary": "Totals are positive.",
        "ddd": "invariant", "statement": "A total MUST be positive.",
        "constrains": ["definition/sales/not-yet-written"]})
    done = run("--node", path, root)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "Cross-node checks did not run" in done.stdout


def test_single_node_mode_still_refuses_bad_form(root, sound_base):
    path = sound_base("rule/sales/broken", {
        "title": "Broken", "summary": "Malformed.", "ddd": "not-a-ddd",
        "statement": "X MUST Y."})
    done = run("--node", path, root)
    assert done.returncode == 1
    assert "not-a-ddd" in done.stdout
