"""`plan.py` — one walk, three parties: the gate a plan node passes, the checks that need the
whole plan and the base, and the derived plan.json held to the files."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

import plan

from conftest import bind

PLAN_PY = Path(plan.__file__)


def run(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(PLAN_PY), *map(str, args)],
                          capture_output=True, text=True)


def problems_in(work, root) -> list[str]:
    validator, allowed = plan.contract()
    nodes, problems = plan.collect(work, validator, allowed)
    base_nodes, base_problems = plan.load_base(root)
    assert base_problems == [], f"the fixture base does not hold together: {base_problems}"
    return sorted(set(problems + plan.cross_problems(nodes, base_nodes)))


# ---------------------------------------------------------------- the sound path

def test_a_sound_plan_derives_and_checks_clean(work, root, sound_plan):
    done = run(work, root)
    assert done.returncode == 0, done.stdout + done.stderr
    assert (work / "plan.json").is_file()
    assert run("--check", work, root).returncode == 0


def test_derivation_is_deterministic(work, root, sound_plan):
    assert run(work, root).returncode == 0
    first = (work / "plan.json").read_bytes()
    assert run(work, root).returncode == 0
    assert (work / "plan.json").read_bytes() == first


def test_the_derived_plan_satisfies_its_own_contract(repo, work, root, sound_plan):
    from jsonschema import Draft202012Validator
    assert run(work, root).returncode == 0
    contract = json.loads((repo / "src/claude/schemas/plan.json").read_text())
    derived = json.loads((work / "plan.json").read_text())
    assert list(Draft202012Validator(contract).iter_errors(derived)) == []


def test_task_entries_carry_epic_unresolved_and_edges(work, root, sound_plan):
    assert run(work, root).returncode == 0
    derived = json.loads((work / "plan.json").read_text())
    task = next(n for n in derived["nodes"] if n["id"] == "task/checkout/bill-order")
    assert task["kind"] == "task"
    assert task["file"] == "task/checkout/bill-order.md"
    assert task["epic"] == "checkout"
    assert "base" not in task, \
        "the index carries no aggregate pin; a binding is pinned per node, in the node file"
    assert task["unresolved"] == ["definition/sales/invoice#attributes"]
    assert "questions" not in task
    kinds = {e["kind"] for e in derived["edges"]}
    assert kinds == {"depends_on", "binds", "covers"}
    dep = next(e for e in derived["edges"] if e["kind"] == "depends_on")
    assert dep == {"from": "task/checkout/bill-order", "to": "task/checkout/record-order",
                   "kind": "depends_on", "at": "depends_on[0]"}


def test_the_derivation_summary_counts_kinds_and_triage(work, root, sound_plan):
    done = run(work, root)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "1 inventory, 1 epic, 2 task" in done.stdout
    assert "1 unresolved gap citation(s) (1 unique)" in done.stdout
    assert "0 open question(s)" in done.stdout
    assert "0 waived" in done.stdout


def test_a_gap_cited_by_two_tasks_counts_once_as_unique(work, root, sound_plan):
    sound_plan("task/checkout/refuse-unbilled-order", {
        "title": "Refuse unbilled order", "summary": "Refuse shipping an unbilled order.",
        "objective": "An order without an invoice is refused at shipping.",
        "criteria": ["Shipping an order with no invoice returns the stated domain error."],
        "nodes": bind(root, "definition/sales/invoice"),
        "unresolved": [{"gap": "definition/sales/invoice#attributes"}],
    })
    done = run(work, root)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "2 unresolved gap citation(s) (1 unique)" in done.stdout


def test_two_epics_may_cover_the_same_base_node(work, root, sound_plan):
    sound_plan("epic/billing", {
        "title": "Billing", "summary": "Everything invoicing needs, cut as its own claim.",
        "covers": ["definition/sales/invoice"],
    })
    sound_plan("task/billing/raise-invoice", {
        "title": "Raise invoice", "summary": "Produce the invoice billing answers for.",
        "objective": "A recorded order reaches billing as exactly one raised invoice.",
        "criteria": ["A recorded order is billable exactly once."],
        "nodes": bind(root, "definition/sales/invoice"),
        "unresolved": [{"gap": "definition/sales/invoice#attributes"}],
    })
    done = run(work, root)
    assert done.returncode == 0, done.stdout + done.stderr


def test_a_question_is_counted_and_indexed(work, root, sound_plan):
    sound_plan("task/checkout/bill-order", {
        "title": "Bill order", "summary": "Raise the bill.",
        "objective": "A recorded order produces exactly one invoice.",
        "criteria": ["Recording an order twice produces one invoice."],
        "nodes": bind(root, "definition/sales/invoice"),
        "unresolved": [{"gap": "definition/sales/invoice#attributes"},
                       {"question": "Nobody said what currency the bill is raised in."}],
    })
    assert run(work, root).returncode == 0
    derived = json.loads((work / "plan.json").read_text())
    task = next(n for n in derived["nodes"] if n["id"] == "task/checkout/bill-order")
    assert task["questions"] == 1


def test_a_plan_with_only_an_inventory_is_a_plan(work, root, sound_base, write_plan):
    write_plan("inventory/greenfield", {
        "title": "Greenfield", "summary": "The target holds nothing; the survey found nothing.",
        "area": ["."],
    })
    done = run(work, root)
    assert done.returncode == 0, done.stdout + done.stderr


def test_intake_holds_material_and_is_never_validated(work, root, sound_plan):
    (work / "intake").mkdir()
    (work / "intake" / "scope.md").write_text("The scope, as supplied.\n", encoding="utf-8")
    done = run(work, root)
    assert done.returncode == 0, done.stdout + done.stderr
    derived = json.loads((work / "plan.json").read_text())
    assert all(not n["id"].startswith("intake") for n in derived["nodes"])
    single = run("--node", work / "intake" / "scope.md", work, root)
    assert single.returncode == 0
    assert "never validated" in single.stdout


# ---------------------------------------------------------------- --unresolved

def test_the_unresolved_report_names_gaps_and_questions(work, root, sound_plan):
    sound_plan("task/checkout/bill-order", {
        "title": "Bill order", "summary": "Raise the bill.",
        "objective": "A recorded order produces exactly one invoice.",
        "criteria": ["Recording an order twice produces one invoice."],
        "nodes": bind(root, "definition/sales/invoice"),
        "unresolved": [{"gap": "definition/sales/invoice#attributes"},
                       {"question": "Nobody said what currency the bill is raised in."}],
    })
    done = run("--unresolved", work, root)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "task/checkout/bill-order:" in done.stdout
    assert "  gap definition/sales/invoice#attributes" in done.stdout
    assert "  question Nobody said what currency the bill is raised in." in done.stdout
    assert "task/checkout/record-order" not in done.stdout
    assert not (work / "plan.json").is_file()


def test_the_unresolved_report_over_a_settled_plan_says_so(work, root, gapped_base, write_plan):
    write_plan("epic/checkout", {
        "title": "Checkout", "summary": "Order placement.",
        "covers": ["definition/sales/order"]})
    write_plan("task/checkout/record-order", {
        "title": "Record order", "summary": "Persist a placed order.",
        "objective": "A valid order is persisted.",
        "criteria": ["A valid order is retrievable."],
        "nodes": bind(root, "definition/sales/order")})
    done = run("--unresolved", work, root)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "no unresolved entries" in done.stdout


def test_the_unresolved_report_is_refused_over_a_broken_plan(work, root, sound_plan,
                                                             write_plan):
    write_plan("task/checkout/orphan", {
        "title": "Orphan", "summary": "Depends on nothing that exists.",
        "objective": "Something demonstrable.",
        "criteria": ["Something falsifiable."],
        "nodes": bind(root, "definition/sales/order"),
        "depends_on": ["task/checkout/nothing"]})
    done = run("--unresolved", work, root)
    assert done.returncode == 1
    assert "the unresolved report is not derived" in done.stdout


def test_unresolved_stands_alone(work, root, sound_plan):
    done = run("--unresolved", "--check", work, root)
    assert done.returncode == 2
    assert "stands alone" in done.stderr


# ---------------------------------------------------------------- staleness

def test_check_before_any_derivation_is_stale(work, root, sound_plan):
    done = run("--check", work, root)
    assert done.returncode == 1
    assert "STALE" in done.stdout


def test_check_after_an_edit_is_stale(work, root, sound_plan):
    assert run(work, root).returncode == 0
    sound_plan("task/checkout/record-order", {
        "title": "Record order", "summary": "Persist a placed order, renamed.",
        "objective": "A valid order is persisted and retrievable by its order_number.",
        "criteria": ["Submitting a valid order returns its order_number."],
        "nodes": bind(root, "definition/sales/order")})
    done = run("--check", work, root)
    assert done.returncode == 1
    assert "STALE" in done.stdout


def test_a_moved_bound_node_stales_the_task_that_binds_it(work, root, sound_plan, gapped_base):
    """The node `record-order` binds is rewritten under it. What moved is named, and the task that
    binds a different node is not — an aggregate over the whole base could do neither."""
    assert run(work, root).returncode == 0
    gapped_base("definition/sales/order", {
        "title": "Order", "summary": "A customer's order.",
        "ddd": "aggregate-root", "aggregate": "orders",
        "identity": ["order_number"],
        "attributes": [{"name": "order_number", "type": "string", "max_length": 8}]})
    done = run("--check", work, root)
    assert done.returncode == 1
    assert "task/checkout/record-order: definition/sales/order is pinned at" in done.stdout
    assert "task/checkout/bill-order" not in done.stdout, \
        "a task binding a node nothing touched was staled by another task's node moving"


def test_a_base_that_grew_elsewhere_stales_nothing(work, root, sound_plan, gapped_base):
    """A node nobody binds is added. Under the aggregate pin this staled every task in the plan,
    which is the noise that made a real stale easy to wave through."""
    assert run(work, root).returncode == 0
    gapped_base("definition/sales/customer", {
        "title": "Customer", "summary": "Who buys.", "ddd": "value-object",
        "attributes": [{"name": "name", "type": "string", "max_length": 80}]})
    assert run(work, root).returncode == 0


# ---------------------------------------------------------------- the closed plan

def test_a_closed_plan_derives_without_the_base(work, root, sound_plan):
    (work / "closure.md").write_text("The initiative shipped; see intake/.\n", encoding="utf-8")
    done = run(work)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "; closed" in done.stdout
    assert (work / "plan.json").is_file()


def test_a_closed_plan_ignores_a_broken_base_path(work, root, sound_plan, tmp_path):
    (work / "closure.md").write_text("Closed.\n", encoding="utf-8")
    done = run(work, tmp_path / "no-such-base")
    assert done.returncode == 0, done.stdout + done.stderr


def test_a_live_plan_requires_the_knowledge_root(work, root, sound_plan):
    done = run(work)
    assert done.returncode == 2
    assert "a live plan validates against its base" in done.stderr


def test_a_moved_base_does_not_stale_a_closed_plan(work, root, sound_plan, gapped_base):
    assert run(work, root).returncode == 0
    gapped_base("definition/sales/order", {
        "title": "Order", "summary": "A customer's order.",
        "ddd": "aggregate-root", "aggregate": "orders",
        "identity": ["order_number"],
        "attributes": [{"name": "order_number", "type": "string", "max_length": 8}]})
    (work / "closure.md").write_text("Closed after the base moved on.\n", encoding="utf-8")
    assert run("--check", work, root).returncode == 0
    assert run("--check", work).returncode == 0


def test_a_closed_plan_still_refuses_broken_structure(work, root, sound_plan):
    sound_plan("task/checkout/rogue", {
        "title": "Rogue", "summary": "Binds outside the epic's claim.",
        "objective": "An unclaimed binding is refused even in history.",
        "criteria": ["The validator refuses this task."],
        "nodes": bind(root, "definition/sales/order", "context/sales"),
    })
    (work / "closure.md").write_text("Closed.\n", encoding="utf-8")
    done = run(work)
    assert done.returncode == 1
    assert "does not cover" in done.stdout


def test_the_unresolved_report_works_on_a_closed_plan(work, root, sound_plan):
    (work / "closure.md").write_text("Closed.\n", encoding="utf-8")
    done = run("--unresolved", work)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "definition/sales/invoice#attributes" in done.stdout


def test_the_closure_marker_is_not_a_node(work, root, sound_plan):
    (work / "closure.md").write_text("Closed.\n", encoding="utf-8")
    done = run("--node", "closure.md", work)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "marks the plan closed" in done.stdout


# ---------------------------------------------------------------- the triage discipline

def test_an_untriaged_gap_on_a_bound_node_is_refused(work, root, sound_plan):
    sound_plan("task/checkout/bill-order", {
        "title": "Bill order", "summary": "Raise the bill.",
        "objective": "A recorded order produces exactly one invoice.",
        "criteria": ["Recording an order twice produces one invoice."],
        "nodes": bind(root, "definition/sales/invoice")})
    problems = problems_in(work, root)
    assert any("open gap on `attributes`" in p and "ignored in silence" in p for p in problems)


def test_a_waiver_settles_an_untriaged_gap(work, root, sound_plan):
    sound_plan("task/checkout/bill-order", {
        "title": "Bill order", "summary": "Raise the bill.",
        "objective": "A recorded order produces exactly one invoice.",
        "criteria": ["Recording an order twice produces one invoice."],
        "nodes": bind(root, "definition/sales/invoice"),
        "waived": [{"gap": "definition/sales/invoice#attributes",
                    "why": "Billing reads the invoice as opaque; its fields are not on this path."}]})
    assert problems_in(work, root) == []


def test_a_triage_entry_on_a_closed_gap_is_refused(work, root, sound_plan):
    sound_plan("task/checkout/record-order", {
        "title": "Record order", "summary": "Persist a placed order.",
        "objective": "A valid order is persisted.",
        "criteria": ["A valid order is retrievable."],
        "nodes": bind(root, "definition/sales/order"),
        "unresolved": [{"gap": "definition/sales/order#attributes"}]})
    assert any("declares no open gap on `attributes`" in p for p in problems_in(work, root))


def test_a_triage_entry_on_an_unbound_node_is_refused(work, root, sound_plan):
    sound_plan("task/checkout/record-order", {
        "title": "Record order", "summary": "Persist a placed order.",
        "objective": "A valid order is persisted.",
        "criteria": ["A valid order is retrievable."],
        "nodes": bind(root, "definition/sales/order"),
        "waived": [{"gap": "definition/sales/invoice#attributes",
                    "why": "Not this task's node at all."}]})
    reported = problems_in(work, root)
    assert any("`nodes` does not bind" in p for p in reported)
    # Which of the two repairs this wants depends on whether the node governs the task, so the
    # message offers both instead of implying the triage was the mistake.
    assert any("bind definition/sales/invoice if it governs this task, or drop the entry" in p
               for p in reported)


def test_a_gap_both_unresolved_and_waived_is_refused(work, root, sound_plan):
    sound_plan("task/checkout/bill-order", {
        "title": "Bill order", "summary": "Raise the bill.",
        "objective": "A recorded order produces exactly one invoice.",
        "criteria": ["Recording an order twice produces one invoice."],
        "nodes": bind(root, "definition/sales/invoice"),
        "unresolved": [{"gap": "definition/sales/invoice#attributes"}],
        "waived": [{"gap": "definition/sales/invoice#attributes", "why": "Also not needed."}]})
    assert any("both unresolved and waived" in p for p in problems_in(work, root))


def test_a_stale_digest_is_refused_with_its_own_message(work, root, sound_plan):
    sound_plan("task/checkout/record-order", {
        "title": "Record order", "summary": "Persist a placed order.",
        "objective": "A valid order is persisted.",
        "criteria": ["A valid order is retrievable."],
        "nodes": [{"node": "definition/sales/order", "digest": "sha256:" + "0" * 64}]})
    problems = problems_in(work, root)
    assert any("definition/sales/order is pinned at" in p and "re-bind the task" in p
               for p in problems), \
        "the refusal must name the node that moved; naming only the task is what it replaced"


# ---------------------------------------------------------------- coverage

def test_a_covered_node_no_task_binds_is_refused(work, root, sound_plan):
    sound_plan("epic/checkout", {
        "title": "Checkout", "summary": "Everything order placement needs.",
        "covers": ["definition/sales/order", "definition/sales/invoice", "context/sales"]})
    reported = problems_in(work, root)
    assert any("covers names context/sales" in p and "never neither" in p for p in reported)
    # Both repairs named, because they live in different files and the message is where the reader
    # finds out which one this hole wants.
    assert any("bind it in a task under this epic, or declare it in `uncovered` with a why" in p
               for p in reported)


def test_uncovered_settles_a_coverage_hole(work, root, sound_plan):
    sound_plan("epic/checkout", {
        "title": "Checkout", "summary": "Everything order placement needs.",
        "covers": ["definition/sales/order", "definition/sales/invoice", "context/sales"],
        "uncovered": [{"node": "context/sales",
                       "why": "The context itself carries no work; it scopes the epic."}]})
    assert problems_in(work, root) == []


def test_uncovered_contradicting_a_binding_is_refused(work, root, sound_plan):
    sound_plan("epic/checkout", {
        "title": "Checkout", "summary": "Everything order placement needs.",
        "covers": ["definition/sales/order", "definition/sales/invoice"],
        "uncovered": [{"node": "definition/sales/invoice",
                       "why": "Left for the follow-up scope."}]})
    assert any("which a task under this epic binds" in p for p in problems_in(work, root))


def test_a_binding_outside_the_epics_covers_is_refused(work, root, sound_plan):
    sound_plan("task/checkout/record-order", {
        "title": "Record order", "summary": "Persist a placed order.",
        "objective": "A valid order is persisted.",
        "criteria": ["A valid order is retrievable."],
        "nodes": bind(root, "definition/sales/order", "context/sales")})
    problems = problems_in(work, root)
    assert any("binds context/sales, which epic/checkout does not cover" in p
               and "grow `covers`, or move the task" in p for p in problems)


def test_uncovered_outside_covers_is_refused(work, root, sound_plan):
    sound_plan("epic/checkout", {
        "title": "Checkout", "summary": "Everything order placement needs.",
        "covers": ["definition/sales/order", "definition/sales/invoice"],
        "uncovered": [{"node": "context/sales", "why": "Never claimed to begin with."}]})
    assert any("which `covers` does not claim" in p for p in problems_in(work, root))


# ---------------------------------------------------------------- beyond the covers

RECORD_ORDER = {
    "title": "Record order", "summary": "Persist a placed order.",
    "objective": "A valid order is persisted and retrievable by its order_number.",
    "criteria": ["Submitting a valid order returns its order_number."],
}


def noted(*lines: str) -> str:
    return "## What it is\nPersist a placed order.\n\n## Notes\n" + "".join(
        f"{line}\n" for line in lines)


def test_a_note_naming_a_node_beyond_covers_without_a_decision_is_refused(work, root,
                                                                          sound_plan):
    sound_plan("task/checkout/record-order", {**RECORD_ORDER, "nodes": bind(root, "definition/sales/order")},
               body=noted("From the binding — the recount is governed by context/sales, "
                          "which sits outside this epic's claim."))
    problems = problems_in(work, root)
    assert any("## Notes names context/sales, which the epic's covers do not claim" in p
               and "`Decision, beyond the covers —` line names it" in p
               and "never travels alone" in p for p in problems)


def test_a_decision_line_beside_the_note_settles_it(work, root, sound_plan):
    sound_plan("task/checkout/record-order", {**RECORD_ORDER, "nodes": bind(root, "definition/sales/order")},
               body=noted("From the binding — the recount is governed by context/sales, "
                          "which sits outside this epic's claim.",
                          "Decision, beyond the covers — stand: context/sales carries no "
                          "work here; the recount belongs to the follow-up initiative."))
    assert problems_in(work, root) == []


def test_a_note_naming_a_covered_node_demands_nothing(work, root, sound_plan):
    sound_plan("task/checkout/record-order", {**RECORD_ORDER, "nodes": bind(root, "definition/sales/order")},
               body=noted("From the binding — definition/sales/invoice answers the billing "
                          "seam this task stops at."))
    assert problems_in(work, root) == []


def test_a_name_matches_whole_never_inside_a_longer_one(work, root, sound_plan):
    sound_plan("task/checkout/record-order", {**RECORD_ORDER, "nodes": bind(root, "definition/sales/order")},
               body=noted("From the binding — the recount lives in "
                          "aggregate/sales/orders-archive today."))
    assert problems_in(work, root) == []


def test_a_decision_line_alone_demands_nothing(work, root, sound_plan):
    sound_plan("task/checkout/record-order", {**RECORD_ORDER, "nodes": bind(root, "definition/sales/order")},
               body=noted("Decision, beyond the covers — stand: context/sales stays the "
                          "neighbouring claim this plan reads and never touches."))
    assert problems_in(work, root) == []


def test_an_epics_notes_are_not_a_tasks(work, root, sound_plan):
    sound_plan("epic/checkout", {
        "title": "Checkout", "summary": "Everything order placement needs.",
        "covers": ["definition/sales/order", "definition/sales/invoice"]},
        body="## What it is\nEverything order placement needs.\n\n## Notes\n"
             "The recount is governed by context/sales, outside this claim.\n")
    assert problems_in(work, root) == []


def test_a_closed_plan_never_demands_a_decision(work, root, sound_plan):
    sound_plan("task/checkout/record-order", {**RECORD_ORDER, "nodes": bind(root, "definition/sales/order")},
               body=noted("From the binding — the recount is governed by context/sales, "
                          "which sits outside this epic's claim."))
    assert run(work, root).returncode == 1
    (work / "closure.md").write_text("The initiative ended; the why lives in intake.\n",
                                     encoding="utf-8")
    assert run(work).returncode == 0


# ---------------------------------------------------------------- broken references

def test_a_binding_to_a_node_the_base_does_not_hold_is_refused(work, root, sound_plan):
    sound_plan("task/checkout/record-order", {
        "title": "Record order", "summary": "Persist a placed order.",
        "objective": "A valid order is persisted.",
        "criteria": ["A valid order is retrievable."],
        "nodes": [{"node": "definition/sales/nothing",
                   "digest": "sha256:" + "0" * 64}]})
    done = run(work, root)
    assert done.returncode == 1
    assert "definition/sales/nothing" in done.stdout
    assert not (work / "plan.json").is_file()


def test_an_orphan_dependency_is_refused(work, root, sound_plan):
    sound_plan("task/checkout/record-order", {
        "title": "Record order", "summary": "Persist a placed order.",
        "objective": "A valid order is persisted.",
        "criteria": ["A valid order is retrievable."],
        "nodes": bind(root, "definition/sales/order"),
        "depends_on": ["task/checkout/nothing"]})
    assert any("task/checkout/nothing, which the plan does not hold" in p
               for p in problems_in(work, root))


def test_a_dependency_cycle_is_refused(work, root, sound_plan):
    sound_plan("task/checkout/record-order", {
        "title": "Record order", "summary": "Persist a placed order.",
        "objective": "A valid order is persisted.",
        "criteria": ["A valid order is retrievable."],
        "nodes": bind(root, "definition/sales/order"),
        "depends_on": ["task/checkout/bill-order"]})
    problems = problems_in(work, root)
    assert any("closes a cycle" in p and "no startable task" in p for p in problems)


def test_a_self_dependency_is_refused(work, root, sound_plan):
    sound_plan("task/checkout/record-order", {
        "title": "Record order", "summary": "Persist a placed order.",
        "objective": "A valid order is persisted.",
        "criteria": ["A valid order is retrievable."],
        "nodes": bind(root, "definition/sales/order"),
        "depends_on": ["task/checkout/record-order"]})
    assert any("names itself" in p for p in problems_in(work, root))


def test_a_task_under_no_epic_is_refused(work, root, sound_plan):
    sound_plan("task/ghost/record-order", {
        "title": "Record order", "summary": "Persist a placed order.",
        "objective": "A valid order is persisted.",
        "criteria": ["A valid order is retrievable."],
        "nodes": bind(root, "definition/sales/order")})
    assert any("epic/ghost does not exist" in p for p in problems_in(work, root))


# ---------------------------------------------------------------- the schema at the gate

def test_a_status_field_is_refused(work, root, sound_plan):
    sound_plan("task/checkout/record-order", {
        "title": "Record order", "summary": "Persist a placed order.",
        "objective": "A valid order is persisted.",
        "criteria": ["A valid order is retrievable."],
        "nodes": bind(root, "definition/sales/order"),
        "status": "done"})
    assert any("status" in p for p in problems_in(work, root))


def test_a_task_binding_nothing_needs_a_rationale(work, root, sound_plan):
    task = {
        "title": "Wire the toolchain", "summary": "Scaffolding before any bound task.",
        "objective": "The repository builds and tests run.",
        "criteria": ["The test runner exits zero on an empty suite."]}
    sound_plan("task/checkout/scaffold", task)
    assert any("'rationale' is a required property" in p for p in problems_in(work, root))
    sound_plan("task/checkout/scaffold", {
        **task, "rationale": "No base node governs scaffolding; the toolchain is the plan's own."})
    assert problems_in(work, root) == []


def test_a_string_where_a_list_belongs_reports_once_not_per_character(work, root, sound_plan,
                                                                      write_plan):
    write_plan("epic/checkout", {
        "title": "Checkout", "summary": "Covers written as a string, not a list.",
        "covers": "definition/sales/order"})
    problems = problems_in(work, root)
    assert any("is not of type 'array'" in p for p in problems)
    assert not any("covers names" in p for p in problems), \
        "a wrong shape is the schema's report alone; its characters are not references"


def test_duplicate_references_are_refused(work, root, sound_plan):
    sound_plan("task/checkout/record-order", {
        "title": "Record order", "summary": "Persist a placed order.",
        "objective": "A valid order is persisted.",
        "criteria": ["A valid order is retrievable."],
        "nodes": bind(root, "definition/sales/order", "definition/sales/order")})
    assert any("non-unique" in p and "nodes" in p for p in problems_in(work, root))
    sound_plan("task/checkout/record-order", {
        "title": "Record order", "summary": "Persist a placed order.",
        "objective": "A valid order is persisted.",
        "criteria": ["A valid order is retrievable."],
        "nodes": bind(root, "definition/sales/order"),
        "depends_on": ["task/checkout/bill-order", "task/checkout/bill-order"]})
    problems = problems_in(work, root)
    assert any("non-unique" in p and "depends_on" in p for p in problems)


def test_a_stray_file_is_reported(work, root, sound_plan):
    (work / "notes.md").write_text("scratch\n")
    assert any("notes.md" in p for p in problems_in(work, root))


def test_wrong_body_headings_are_refused(work, root, sound_plan, write_plan):
    write_plan("epic/checkout",
               {"title": "Checkout", "summary": "Order placement.",
                "covers": ["definition/sales/order", "definition/sales/invoice"]},
               body="## What it is\nProse.\n\n## Rules\nNone.\n")
    assert any("headings" in p for p in problems_in(work, root))


# ---------------------------------------------------------------- the base at the gate

def test_a_base_that_does_not_hold_together_cannot_be_planned_over(work, root, sound_plan,
                                                                    gapped_base):
    gapped_base("definition/sales/broken", {
        "title": "Broken", "summary": "Malformed on purpose.", "ddd": "value-object"})
    done = run(work, root)
    assert done.returncode == 2
    assert "does not hold together" in done.stderr
    assert "fix it with graph.py" in done.stderr


def test_usage_errors_cannot_run(work, root, sound_plan):
    assert run(work).returncode == 2
    assert run(work, root, "extra").returncode == 2
    assert run("--node", work, root).returncode == 2
    missing = run(work, root / "nowhere")
    assert missing.returncode == 2
    assert "not a directory" in missing.stderr


# ---------------------------------------------------------------- --node

def test_single_node_mode_ignores_unresolved_references(work, root, sound_plan, write_plan):
    path = write_plan("task/checkout/later", {
        "title": "Later", "summary": "Binds a node not yet in the base.",
        "objective": "Something demonstrable.",
        "criteria": ["Something falsifiable."],
        "nodes": [{"node": "definition/sales/not-yet-written",
                   "digest": "sha256:" + "0" * 64}]})
    done = run("--node", path, work, root)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "Cross-node checks and base checks did not run" in done.stdout


def test_single_node_mode_still_refuses_bad_form(work, root, sound_plan, write_plan):
    path = write_plan("task/checkout/broken", {
        "title": "Broken", "summary": "Malformed.", "objective": "X.",
        "criteria": ["Y."],
        "nodes": [{"node": "definition/sales/order", "digest": "not-a-pin"}]})
    done = run("--node", path, work, root)
    assert done.returncode == 1
    assert "not-a-pin" in done.stdout
