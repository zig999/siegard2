"""The rules no per-file schema can express, in `check_knowledge.cross_object`.

Each compares two objects, and a boundary validator is handed one. They are exercised against
frontmatter mappings directly rather than through files: what is under test is the rule, and going
through disk would put the file layer's own refusals in front of it.
"""
from __future__ import annotations

import pytest

import check_knowledge


def obj(identifier: str, kind: str, **fields) -> dict:
    return {"id": identifier, "type": kind, **fields}


def problems(*objects: dict) -> list[str]:
    held = {o["id"]: o for o in objects}
    where = {o["id"]: "/".join(o["id"].split(".")[1:]) + ".md" for o in objects}
    return check_knowledge.cross_object(held, where)


SUBDOMAIN = obj("dm.subdomain.commerce", "subdomain")
CONTEXT = obj("dm.context.sales", "context", subdomain="dm.subdomain.commerce")
BILLING = obj("dm.context.billing", "context", subdomain="dm.subdomain.commerce")


def test_a_coherent_base_reports_nothing():
    assert problems(
        SUBDOMAIN, CONTEXT,
        obj("dm.aggregate.sales.order", "aggregate", boundary="dm.context.sales",
            root="dm.definition.sales.order"),
        obj("dm.definition.sales.order", "definition", ddd="aggregate-root",
            boundary="dm.aggregate.sales.order"),
    ) == []


# ---- containment is acyclic --------------------------------------------------------------------

def test_an_aggregate_containing_itself():
    found = problems(SUBDOMAIN, CONTEXT,
                     obj("dm.aggregate.sales.order", "aggregate",
                         boundary="dm.aggregate.sales.order"))
    assert len(found) == 1 and "loop" in found[0]


def test_two_aggregates_containing_each_other():
    """Reported per node on the loop: each one's scope is undefined, and the walk that resolves it
    does not end."""
    found = problems(SUBDOMAIN, CONTEXT,
                     obj("dm.aggregate.sales.a", "aggregate", boundary="dm.aggregate.sales.b"),
                     obj("dm.aggregate.sales.b", "aggregate", boundary="dm.aggregate.sales.a"))
    assert len(found) == 2


# ---- the boundary agrees with the identifier ----------------------------------------------------

def test_a_boundary_in_another_context_than_the_identifier():
    """The parent is written twice — once fixing the path, once fixing membership — and a node
    whose two parents disagree sits in two trees."""
    found = problems(SUBDOMAIN, CONTEXT, BILLING,
                     obj("dm.definition.sales.invoice", "definition", ddd="entity",
                         boundary="dm.context.billing"))
    assert len(found) == 1 and "filed under context" in found[0]


# ---- an aggregate agrees with its root -----------------------------------------------------------

def test_a_root_whose_ddd_does_not_say_so():
    found = problems(SUBDOMAIN, CONTEXT,
                     obj("dm.aggregate.sales.order", "aggregate", boundary="dm.context.sales",
                         root="dm.definition.sales.order"),
                     obj("dm.definition.sales.order", "definition", ddd="entity",
                         boundary="dm.aggregate.sales.order"))
    assert len(found) == 1 and "ddd" in found[0]


def test_a_root_sitting_outside_the_aggregate_it_heads():
    found = problems(SUBDOMAIN, CONTEXT,
                     obj("dm.aggregate.sales.order", "aggregate", boundary="dm.context.sales",
                         root="dm.definition.sales.order"),
                     obj("dm.definition.sales.order", "definition", ddd="aggregate-root",
                         boundary="dm.context.sales"))
    assert len(found) == 1 and "entry point" in found[0]


# ---- every reference resolves ----------------------------------------------------------------------

def test_a_root_the_base_does_not_hold():
    found = problems(SUBDOMAIN, CONTEXT,
                     obj("dm.aggregate.sales.order", "aggregate", boundary="dm.context.sales",
                         root="dm.definition.sales.nowhere"))
    assert len(found) == 1 and "does not hold" in found[0]


def test_a_boundary_the_base_does_not_hold():
    """`boundary` is held apart from the content edges for the crossing rule, which must not see
    it — but resolution has no such exemption, and a missing parent is the worst case of it."""
    found = problems(SUBDOMAIN, CONTEXT,
                     obj("dm.definition.sales.order", "definition", ddd="entity",
                         boundary="dm.aggregate.sales.nowhere"))
    assert len(found) == 1 and "does not hold" in found[0]


def test_a_boundary_both_unresolved_and_in_another_context_reports_both():
    found = problems(SUBDOMAIN, CONTEXT,
                     obj("dm.definition.sales.order", "definition", ddd="entity",
                         boundary="dm.context.nowhere"))
    assert len(found) == 2


# ---- one lifecycle per subject, and what a transition may emit ---------------------------------------

def test_two_lifecycles_claiming_one_subject():
    found = problems(SUBDOMAIN, CONTEXT,
                     obj("dm.lifecycle.sales.order", "lifecycle", boundary="dm.context.sales",
                         subject="dm.definition.sales.order"),
                     obj("dm.lifecycle.sales.order-two", "lifecycle", boundary="dm.context.sales",
                         subject="dm.definition.sales.order"),
                     obj("dm.definition.sales.order", "definition", ddd="entity",
                         boundary="dm.context.sales"))
    assert len(found) == 1 and "lifecycles" in found[0]


@pytest.mark.parametrize("ddd, reported", [("api", True), ("command", True),
                                           ("domain-event", False), ("integration-event", False)])
def test_what_a_transition_may_emit(ddd, reported):
    """A state change raises something that happened. An api is called and a command is sent, and
    a transition raises neither."""
    found = problems(SUBDOMAIN, CONTEXT,
                     obj("dm.lifecycle.sales.order", "lifecycle", boundary="dm.context.sales",
                         subject="dm.definition.sales.order",
                         transitions=[{"from": "new", "trigger": "pay", "to": "paid",
                                       "emits": ["dm.interface.sales.event"]}]),
                     obj("dm.interface.sales.event", "interface", boundary="dm.context.sales",
                         ddd=ddd, ownership="published"),
                     obj("dm.definition.sales.order", "definition", ddd="entity",
                         boundary="dm.context.sales"))
    assert bool(found) is reported


# ---- a consumed interface names something published --------------------------------------------------

@pytest.mark.parametrize("ownership, reported", [("consumed", True), ("published", False)])
def test_upstream_ends_at_the_context_that_owes_compatibility(ownership, reported):
    found = problems(SUBDOMAIN, CONTEXT, BILLING,
                     obj("dm.interface.billing.placed", "interface", boundary="dm.context.billing",
                         ownership="consumed", upstream="dm.interface.sales.placed"),
                     obj("dm.interface.sales.placed", "interface", boundary="dm.context.sales",
                         ownership=ownership))
    assert bool(found) is reported


# ---- a rule that reaches outside its aggregate ---------------------------------------------------------

def rule_reaching(**extra):
    return problems(SUBDOMAIN, CONTEXT,
                    obj("dm.aggregate.sales.order", "aggregate", boundary="dm.context.sales"),
                    obj("dm.aggregate.sales.stock", "aggregate", boundary="dm.context.sales"),
                    obj("dm.rule.sales.enough-stock", "rule", boundary="dm.aggregate.sales.order",
                        depends_on=["dm.definition.sales.level"], **extra),
                    obj("dm.definition.sales.level", "definition", ddd="entity",
                        boundary="dm.aggregate.sales.stock"))


def test_a_rule_spanning_two_aggregates_owes_a_consistency():
    found = rule_reaching()
    assert len(found) == 1 and "consistency" in found[0]


@pytest.mark.parametrize("consistency", ["immediate", "eventual"])
def test_and_owes_nothing_once_it_declares_one(consistency):
    assert rule_reaching(consistency=consistency) == []


def test_a_rule_inside_one_aggregate_owes_nothing():
    assert problems(SUBDOMAIN, CONTEXT,
                    obj("dm.aggregate.sales.order", "aggregate", boundary="dm.context.sales"),
                    obj("dm.rule.sales.positive", "rule", boundary="dm.aggregate.sales.order",
                        depends_on=["dm.definition.sales.line"]),
                    obj("dm.definition.sales.line", "definition", ddd="value-object",
                        boundary="dm.aggregate.sales.order")) == []


# ---- what may cross a bounded context --------------------------------------------------------------------

def test_reaching_into_another_contexts_internals():
    found = problems(SUBDOMAIN, CONTEXT, BILLING,
                     obj("dm.definition.sales.order", "definition", ddd="entity",
                         boundary="dm.context.sales", depends_on=["dm.definition.billing.invoice"]),
                     obj("dm.definition.billing.invoice", "definition", ddd="entity",
                         boundary="dm.context.billing"))
    assert len(found) == 1 and "another" in found[0]


def test_crossing_to_an_interface_is_what_the_boundary_is_for():
    assert problems(SUBDOMAIN, CONTEXT, BILLING,
                    obj("dm.definition.sales.order", "definition", ddd="entity",
                        boundary="dm.context.sales", depends_on=["dm.interface.billing.invoiced"]),
                    obj("dm.interface.billing.invoiced", "interface", boundary="dm.context.billing",
                        ownership="published")) == []
