"""`plan.py` — one walk, three parties: the gate a plan node passes, the checks that need the
whole plan and the specification, and the derived plan.json held to the files."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

import plan

PLAN_PY = Path(plan.__file__)


def run(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(PLAN_PY), *map(str, args)],
                          capture_output=True, text=True)


def problems_in(work, root) -> list[str]:
    validator = plan.contract()
    nodes, problems = plan.collect(work, validator)
    spec_nodes, spec_problems = plan.load_base(root)
    assert spec_problems == [], f"the fixture specification does not hold together: {spec_problems}"
    return sorted(set(problems + plan.cross_problems(nodes, spec_nodes)))


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


def test_task_entries_carry_epic_and_edges(work, root, sound_plan):
    assert run(work, root).returncode == 0
    derived = json.loads((work / "plan.json").read_text())
    task = next(n for n in derived["nodes"] if n["id"] == "task/checkout/bill-order")
    assert task["kind"] == "task"
    assert task["file"] == "task/checkout/bill-order.md"
    assert task["epic"] == "checkout"
    assert "implements" not in task, \
        "the index carries no field for it; implements is edges, the same as covers"
    kinds = {e["kind"] for e in derived["edges"]}
    assert kinds == {"depends_on", "implements", "covers"}
    dep = next(e for e in derived["edges"] if e["kind"] == "depends_on")
    assert dep == {"from": "task/checkout/bill-order", "to": "task/checkout/record-order",
                   "kind": "depends_on", "at": "depends_on[0]"}
    impl = next(e for e in derived["edges"] if e["kind"] == "implements"
                and e["from"] == "task/checkout/bill-order")
    assert impl == {"from": "task/checkout/bill-order", "to": "domain/sales/invoice",
                    "kind": "implements", "at": "implements[0]"}


def test_the_derivation_summary_counts_kinds_and_implements(work, root, sound_plan):
    done = run(work, root)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "1 inventory, 1 epic, 2 task" in done.stdout
    assert "2 specification node reference(s) implemented (2 unique)" in done.stdout


def test_two_tasks_implementing_one_node_counts_once_as_unique(work, root, sound_plan):
    sound_plan("task/checkout/refuse-unbilled-order", {
        "title": "Refuse unbilled order", "summary": "Refuse shipping an unbilled order.",
        "objective": "An order without an invoice is refused at shipping.",
        "criteria": ["Shipping an order with no invoice returns the stated domain error."],
        "implements": ["domain/sales/invoice"],
    })
    done = run(work, root)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "3 specification node reference(s) implemented (2 unique)" in done.stdout


def test_two_epics_may_cover_the_same_specification_node(work, root, sound_plan):
    sound_plan("epic/billing", {
        "title": "Billing", "summary": "Everything invoicing needs, cut as its own claim.",
        "covers": ["domain/sales/invoice"],
    })
    sound_plan("task/billing/raise-invoice", {
        "title": "Raise invoice", "summary": "Produce the invoice billing answers for.",
        "objective": "A recorded order reaches billing as exactly one raised invoice.",
        "criteria": ["A recorded order is billable exactly once."],
        "implements": ["domain/sales/invoice"],
    })
    done = run(work, root)
    assert done.returncode == 0, done.stdout + done.stderr


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
        "implements": ["domain/sales/order"]})
    done = run("--check", work, root)
    assert done.returncode == 1
    assert "STALE" in done.stdout


# ---------------------------------------------------------------- the closed plan

def test_a_closed_plan_derives_without_the_specification(work, root, sound_plan):
    (work / "closure.md").write_text("The initiative shipped; see intake/.\n", encoding="utf-8")
    done = run(work)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "; closed" in done.stdout
    assert (work / "plan.json").is_file()


def test_a_closed_plan_ignores_a_broken_specification_path(work, root, sound_plan, tmp_path):
    (work / "closure.md").write_text("Closed.\n", encoding="utf-8")
    done = run(work, tmp_path / "no-such-specification")
    assert done.returncode == 0, done.stdout + done.stderr


def test_a_live_plan_requires_the_specification_root(work, root, sound_plan):
    done = run(work)
    assert done.returncode == 2
    assert "a live plan validates against its specification" in done.stderr


def test_a_closed_plan_still_refuses_broken_structure(work, root, sound_plan):
    sound_plan("task/checkout/rogue", {
        "title": "Rogue", "summary": "Implements outside the epic's claim.",
        "objective": "An unclaimed reference is refused even in history.",
        "criteria": ["The validator refuses this task."],
        "implements": ["domain/sales/order", "domain/sales/_context"],
    })
    (work / "closure.md").write_text("Closed.\n", encoding="utf-8")
    done = run(work)
    assert done.returncode == 1
    assert "does not cover" in done.stdout


def test_the_closure_marker_is_not_a_node(work, root, sound_plan):
    (work / "closure.md").write_text("Closed.\n", encoding="utf-8")
    done = run("--node", "closure.md", work)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "marks the plan closed" in done.stdout


# ---------------------------------------------------------------- coverage

def test_a_covered_node_no_task_implements_is_refused(work, root, sound_plan):
    sound_plan("epic/checkout", {
        "title": "Checkout", "summary": "Everything order placement needs.",
        "covers": ["domain/sales/order", "domain/sales/invoice",
                   "rules/sales/invoice-immutable"]})
    reported = problems_in(work, root)
    assert any("covers names rules/sales/invoice-immutable" in p and "never neither" in p
               for p in reported)
    assert any("implement it in a task under this epic, or declare it in `uncovered` with a why"
               in p for p in reported)


def test_uncovered_settles_a_coverage_hole(work, root, sound_plan):
    sound_plan("epic/checkout", {
        "title": "Checkout", "summary": "Everything order placement needs.",
        "covers": ["domain/sales/order", "domain/sales/invoice",
                   "rules/sales/invoice-immutable"],
        "uncovered": [{"node": "rules/sales/invoice-immutable",
                       "why": "This plan reads the rule; it does not enforce it in code."}]})
    assert problems_in(work, root) == []


def test_uncovered_contradicting_an_implementation_is_refused(work, root, sound_plan):
    sound_plan("epic/checkout", {
        "title": "Checkout", "summary": "Everything order placement needs.",
        "covers": ["domain/sales/order", "domain/sales/invoice"],
        "uncovered": [{"node": "domain/sales/invoice",
                       "why": "Left for the follow-up scope."}]})
    assert any("which a task under this epic implements" in p for p in problems_in(work, root))


def test_a_reference_outside_the_epics_covers_is_refused(work, root, sound_plan):
    sound_plan("task/checkout/record-order", {
        "title": "Record order", "summary": "Persist a placed order.",
        "objective": "A valid order is persisted.",
        "criteria": ["A valid order is retrievable."],
        "implements": ["domain/sales/order", "domain/sales/_context"]})
    problems = problems_in(work, root)
    assert any("implements[1] names domain/sales/_context, which epic/checkout does not cover"
               in p and "grow `covers`, or move the task" in p for p in problems)


def test_uncovered_outside_covers_is_refused(work, root, sound_plan):
    sound_plan("epic/checkout", {
        "title": "Checkout", "summary": "Everything order placement needs.",
        "covers": ["domain/sales/order", "domain/sales/invoice"],
        "uncovered": [{"node": "domain/sales/_context", "why": "Never claimed to begin with."}]})
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
    sound_plan("task/checkout/record-order",
               {**RECORD_ORDER, "implements": ["domain/sales/order"]},
               body=noted("From the specification — the recount is governed by "
                          "domain/sales/_context, which sits outside this epic's claim."))
    problems = problems_in(work, root)
    assert any("## Notes names domain/sales/_context, which the epic's covers do not claim" in p
               and "`Decision, beyond the covers —` line names it" in p
               and "never travels alone" in p for p in problems)


def test_a_decision_line_beside_the_note_settles_it(work, root, sound_plan):
    sound_plan("task/checkout/record-order",
               {**RECORD_ORDER, "implements": ["domain/sales/order"]},
               body=noted("From the specification — the recount is governed by "
                          "domain/sales/_context, which sits outside this epic's claim.",
                          "Decision, beyond the covers — stand: domain/sales/_context carries "
                          "no work here; the recount belongs to the follow-up initiative."))
    assert problems_in(work, root) == []


def test_a_note_naming_a_covered_node_demands_nothing(work, root, sound_plan):
    sound_plan("task/checkout/record-order",
               {**RECORD_ORDER, "implements": ["domain/sales/order"]},
               body=noted("From the specification — domain/sales/invoice answers the billing "
                          "seam this task stops at."))
    assert problems_in(work, root) == []


def test_a_name_matches_whole_never_inside_a_longer_one(work, root, sound_plan):
    sound_plan("task/checkout/record-order",
               {**RECORD_ORDER, "implements": ["domain/sales/order"]},
               body=noted("From the specification — the recount lives in "
                          "domain/sales/order-history today."))
    assert problems_in(work, root) == []


def test_a_decision_line_alone_demands_nothing(work, root, sound_plan):
    sound_plan("task/checkout/record-order",
               {**RECORD_ORDER, "implements": ["domain/sales/order"]},
               body=noted("Decision, beyond the covers — stand: domain/sales/_context stays "
                          "the neighbouring claim this plan reads and never touches."))
    assert problems_in(work, root) == []


def test_an_epics_notes_are_not_a_tasks(work, root, sound_plan):
    sound_plan("epic/checkout", {
        "title": "Checkout", "summary": "Everything order placement needs.",
        "covers": ["domain/sales/order", "domain/sales/invoice"]},
        body="## What it is\nEverything order placement needs.\n\n## Notes\n"
             "The recount is governed by domain/sales/_context, outside this claim.\n")
    assert problems_in(work, root) == []


def test_a_closed_plan_never_demands_a_decision(work, root, sound_plan):
    sound_plan("task/checkout/record-order",
               {**RECORD_ORDER, "implements": ["domain/sales/order"]},
               body=noted("From the specification — the recount is governed by "
                          "domain/sales/_context, which sits outside this epic's claim."))
    assert run(work, root).returncode == 1
    (work / "closure.md").write_text("The initiative ended; the why lives in intake.\n",
                                     encoding="utf-8")
    assert run(work).returncode == 0


# ---------------------------------------------------------------- broken references

def test_a_reference_to_a_node_the_specification_does_not_hold_is_refused(work, root,
                                                                          sound_plan):
    sound_plan("task/checkout/record-order", {
        "title": "Record order", "summary": "Persist a placed order.",
        "objective": "A valid order is persisted.",
        "criteria": ["A valid order is retrievable."],
        "implements": ["domain/sales/nothing"]})
    done = run(work, root)
    assert done.returncode == 1
    assert "domain/sales/nothing" in done.stdout
    assert not (work / "plan.json").is_file()


def test_an_orphan_dependency_is_refused(work, root, sound_plan):
    sound_plan("task/checkout/record-order", {
        "title": "Record order", "summary": "Persist a placed order.",
        "objective": "A valid order is persisted.",
        "criteria": ["A valid order is retrievable."],
        "implements": ["domain/sales/order"],
        "depends_on": ["task/checkout/nothing"]})
    assert any("task/checkout/nothing, which the plan does not hold" in p
               for p in problems_in(work, root))


def test_a_dependency_cycle_is_refused(work, root, sound_plan):
    sound_plan("task/checkout/record-order", {
        "title": "Record order", "summary": "Persist a placed order.",
        "objective": "A valid order is persisted.",
        "criteria": ["A valid order is retrievable."],
        "implements": ["domain/sales/order"],
        "depends_on": ["task/checkout/bill-order"]})
    problems = problems_in(work, root)
    assert any("closes a cycle" in p and "no startable task" in p for p in problems)


def test_a_self_dependency_is_refused(work, root, sound_plan):
    sound_plan("task/checkout/record-order", {
        "title": "Record order", "summary": "Persist a placed order.",
        "objective": "A valid order is persisted.",
        "criteria": ["A valid order is retrievable."],
        "implements": ["domain/sales/order"],
        "depends_on": ["task/checkout/record-order"]})
    assert any("names itself" in p for p in problems_in(work, root))


def test_a_task_under_no_epic_is_refused(work, root, sound_plan):
    sound_plan("task/ghost/record-order", {
        "title": "Record order", "summary": "Persist a placed order.",
        "objective": "A valid order is persisted.",
        "criteria": ["A valid order is retrievable."],
        "implements": ["domain/sales/order"]})
    assert any("epic/ghost does not exist" in p for p in problems_in(work, root))


# ---------------------------------------------------------------- the schema at the gate

def test_a_status_field_is_refused(work, root, sound_plan):
    sound_plan("task/checkout/record-order", {
        "title": "Record order", "summary": "Persist a placed order.",
        "objective": "A valid order is persisted.",
        "criteria": ["A valid order is retrievable."],
        "implements": ["domain/sales/order"],
        "status": "done"})
    assert any("status" in p for p in problems_in(work, root))


def test_a_task_implementing_nothing_needs_a_rationale(work, root, sound_plan):
    task = {
        "title": "Wire the toolchain", "summary": "Scaffolding before any bound task.",
        "objective": "The repository builds and tests run.",
        "criteria": ["The test runner exits zero on an empty suite."]}
    sound_plan("task/checkout/scaffold", task)
    assert any("'rationale' is a required property" in p for p in problems_in(work, root))
    sound_plan("task/checkout/scaffold", {
        **task, "rationale": "No specification node governs scaffolding; the toolchain is the "
                             "plan's own."})
    assert problems_in(work, root) == []


def test_a_string_where_a_list_belongs_reports_once_not_per_character(work, root, sound_plan,
                                                                      write_plan):
    write_plan("epic/checkout", {
        "title": "Checkout", "summary": "Covers written as a string, not a list.",
        "covers": "domain/sales/order"})
    problems = problems_in(work, root)
    assert any("is not of type 'array'" in p for p in problems)
    assert not any("covers names" in p for p in problems), \
        "a wrong shape is the schema's report alone; its characters are not references"


def test_duplicate_references_are_refused(work, root, sound_plan):
    sound_plan("task/checkout/record-order", {
        "title": "Record order", "summary": "Persist a placed order.",
        "objective": "A valid order is persisted.",
        "criteria": ["A valid order is retrievable."],
        "implements": ["domain/sales/order", "domain/sales/order"]})
    assert any("non-unique" in p and "implements" in p for p in problems_in(work, root))
    sound_plan("task/checkout/record-order", {
        "title": "Record order", "summary": "Persist a placed order.",
        "objective": "A valid order is persisted.",
        "criteria": ["A valid order is retrievable."],
        "implements": ["domain/sales/order"],
        "depends_on": ["task/checkout/bill-order", "task/checkout/bill-order"]})
    problems = problems_in(work, root)
    assert any("non-unique" in p and "depends_on" in p for p in problems)


def test_a_stray_file_is_reported(work, root, sound_plan):
    (work / "notes.md").write_text("scratch\n")
    assert any("notes.md" in p for p in problems_in(work, root))


def test_wrong_body_headings_are_refused(work, root, sound_plan, write_plan):
    write_plan("epic/checkout",
               {"title": "Checkout", "summary": "Order placement.",
                "covers": ["domain/sales/order", "domain/sales/invoice"]},
               body="## What it is\nProse.\n\n## Rules\nNone.\n")
    assert any("headings" in p for p in problems_in(work, root))


# ---------------------------------------------------------------- the specification at the gate

def test_a_specification_that_does_not_hold_together_cannot_be_planned_over(work, root,
                                                                            sound_plan,
                                                                            sound_base):
    sound_base("domain/sales/broken", {"type": "value-object"})  # attributes is required
    done = run(work, root)
    assert done.returncode == 2
    assert "does not hold together" in done.stderr
    assert "fix it with spec.py" in done.stderr


def test_usage_errors_cannot_run(work, root, sound_plan):
    assert run(work).returncode == 2
    assert run(work, root, "extra").returncode == 2
    assert run("--node", work, root).returncode == 2
    missing = run(work, root / "nowhere")
    assert missing.returncode == 2
    assert "not a directory" in missing.stderr


# ---------------------------------------------------------------- --node

def test_single_node_mode_ignores_cross_node_references(work, root, sound_plan, write_plan):
    path = write_plan("task/checkout/later", {
        "title": "Later", "summary": "Implements a node not yet in the specification.",
        "objective": "Something demonstrable.",
        "criteria": ["Something falsifiable."],
        "implements": ["domain/sales/not-yet-written"]})
    done = run("--node", path, work, root)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "Cross-node checks and specification checks did not run" in done.stdout


def test_single_node_mode_still_refuses_bad_form(work, root, sound_plan, write_plan):
    path = write_plan("task/checkout/broken", {
        "title": "Broken", "summary": "Malformed.", "objective": "X.",
        "criteria": ["Y."],
        "implements": "domain/sales/order"})
    done = run("--node", path, work, root)
    assert done.returncode == 1
    assert "is not of type 'array'" in done.stdout


# ------------------------------------ what the project's own standard presupposes

def registry(tmp_path: Path, *paths: str) -> Path:
    """A registry presupposing one artifact per path given, written where a plan can be held
    against it."""
    import yaml
    from conftest import STANDARD
    path = tmp_path / "registry.yaml"
    path.write_text(yaml.safe_dump({**STANDARD, "presupposes": [
        {"path": p, "provides": "the `lint` step PRH-01 is decided by.", "rules": ["PRH-01"]}
        for p in paths]}, sort_keys=False), encoding="utf-8")
    return path


def test_an_absent_artifact_no_task_produces_is_refused(work, root, sound_plan, tmp_path):
    """The plan-side half of the refusal. A delivery already stops before writing source over the
    absence, so a plan that leaves it unplanned is a plan whose every task stops — and this is
    where that is visible while it can still be cut."""
    tree = tmp_path / "tree"
    tree.mkdir()
    found = plan.substrate_problems(
        plan.collect(work, plan.contract())[0], str(registry(tmp_path, "package.json")), tree)
    assert len(found) == 1
    assert "which " + str(tree) + " does not hold and no task produces" in found[0]
    assert "PRH-01 cannot be applied" in found[0]
    assert "declares package.json in `produces`" in found[0]


def test_an_artifact_the_tree_already_holds_is_not_the_plan_s_business(work, root, sound_plan,
                                                                      tmp_path):
    tree = tmp_path / "tree"
    tree.mkdir()
    (tree / "package.json").write_text("{}", encoding="utf-8")
    assert plan.substrate_problems(
        plan.collect(work, plan.contract())[0],
        str(registry(tmp_path, "package.json")), tree) == []


def test_a_task_that_produces_the_artifact_answers_for_it(work, root, sound_plan, write_plan,
                                                          tmp_path):
    tree = tmp_path / "tree"
    tree.mkdir()
    import re

    import yaml
    text = (work / "task/checkout/record-order.md").read_text(encoding="utf-8")
    front = yaml.safe_load(re.match(r"^---\n(.*?)\n---\n", text, re.S).group(1))
    front["produces"] = ["package.json"]
    write_plan("task/checkout/record-order", front)
    assert plan.substrate_problems(
        plan.collect(work, plan.contract())[0],
        str(registry(tmp_path, "package.json")), tree) == []
    assert problems_in(work, root) == [], "producing an artifact breaks no other check"


def test_a_registry_that_does_not_hold_reconciles_nothing(work, root, sound_plan, tmp_path):
    """A broken registry presupposes nothing anybody can check, and saying so beats reporting a
    plan as sound against rules that never parsed."""
    import yaml
    from conftest import STANDARD
    path = tmp_path / "broken.yaml"
    one = STANDARD["rules"][0]
    path.write_text(yaml.safe_dump({**STANDARD, "rules": [one, dict(one)]}), encoding="utf-8")
    found = plan.substrate_problems(plan.collect(work, plan.contract())[0], str(path),
                                    tmp_path)
    assert any("the plan is not reconciled against" in p for p in found)


def test_the_two_flags_travel_together(work, root, sound_plan, tmp_path):
    done = run("--standard", registry(tmp_path, "package.json"), work, root)
    assert done.returncode == 2
    assert "travel together" in done.stderr
    done = run("--against", tmp_path, work, root)
    assert done.returncode == 2
    assert "travel together" in done.stderr


def test_the_reconciliation_refuses_the_run_and_derives_nothing(work, root, sound_plan, tmp_path):
    """It is a problem like any other: plan.json is not derived over a plan that does not hold
    together, and a substrate nothing will build is exactly that."""
    tree = tmp_path / "tree"
    tree.mkdir()
    done = run("--standard", registry(tmp_path, "package.json"), "--against", tree, work, root)
    assert done.returncode == 1, done.stdout + done.stderr
    assert "no task produces" in done.stdout
    assert not (work / "plan.json").exists()


def test_a_node_check_is_not_where_a_plan_wide_fact_is_decided(work, root, sound_plan, tmp_path):
    done = run("--node", work / "task/checkout/record-order.md",
               "--standard", registry(tmp_path, "package.json"), "--against", tmp_path, work, root)
    assert done.returncode == 2
    assert "a fact about the whole plan" in done.stderr


def test_a_closed_plan_is_not_reconciled_against_a_standard(work, root, sound_plan, tmp_path):
    """History answers to the tree it planned over, not today's. A closed plan refused because
    somebody never built an artifact would be history that cannot validate for a reason nobody
    can act on — the initiative is over, and there is no task left to cut."""
    (work / "closure.md").write_text("# Closed\nThe initiative shipped.\n", encoding="utf-8")
    done = run("--standard", registry(tmp_path, "package.json"), "--against", tmp_path, work, root)
    assert done.returncode == 2
    assert "is closed, and what a standard presupposes" in done.stderr
    assert run("--check", work).returncode in (0, 1), \
        "history still validates without the flags; only the reconciliation is refused"


# ------------------------------------------------ the classified note openings, read by script


def test_the_classified_openings_are_read_by_script_not_by_eye():
    """The two note classes something downstream collects — the stop /implement-task quotes and
    the entries the test author is handed — read by the literal opening the plan writes, and by
    nothing else: a paraphrase is invisible on purpose, because the opening is the contract."""
    notes = (
        "BLOCKING, from the specification — the criterion asserts a refund exceeding the cap "
        "rules/billing/refund-cap states.\n"
        "  UNDERDETERMINED, from the specification — an empty bill satisfies every criterion.\n"
        "Decision, beyond the covers — stand: the epic keeps its claim.\n"
        "A blocking note mentioned in passing is not one.\n"
        "\n"
        "UNDERDETERMINED, from the specification — a duplicate submission is silently merged.\n")
    assert plan.blocking_notes_of(notes) == [
        "BLOCKING, from the specification — the criterion asserts a refund exceeding the cap "
        "rules/billing/refund-cap states."]
    assert plan.underdetermined_notes_of(notes) == [
        "UNDERDETERMINED, from the specification — an empty bill satisfies every criterion.",
        "UNDERDETERMINED, from the specification — a duplicate submission is silently merged."]
    assert plan.blocking_notes_of("") == [] and plan.underdetermined_notes_of("") == []


def test_a_persisted_unstated_entry_is_refused():
    """The unstated class is transient by contract: the fact is decided into the specification
    and disclosed in its decision log during planning, so a task file still carrying the opening
    is a plan that skipped the route — and without this refusal it would read exactly like one
    that ran it."""
    notes = ("UNSTATED, from the specification — no node states where a requester "
             "identity originates.\n")
    problems = plan.unstated_notes_problems("task/billing/refund", notes)
    assert len(problems) == 1
    assert "never persists" in problems[0]
    assert "task/billing/refund" in problems[0]
    assert plan.unstated_notes_problems("task/billing/refund", "") == []
    assert plan.unstated_notes_problems(
        "task/billing/refund",
        "An unstated fact mentioned in passing is not an entry.\n") == []


def test_a_plan_holding_a_persisted_unstated_entry_derives_nothing(work, root, sound_plan,
                                                                   write_plan):
    """The whole pipeline refuses, not just the helper: a task file carrying the opening fails
    the run and plan.json is not derived — the refusal a consumer actually meets."""
    write_plan("task/checkout/record-order", {
        "title": "Record order", "summary": "Persist a placed order.",
        "objective": "A valid order is persisted and retrievable by its order_number.",
        "criteria": ["Submitting a valid order returns its order_number."],
        "implements": ["domain/sales/order"],
    }, body=("## What it is\nOne sentence.\n\n## Notes\n"
             "UNSTATED, from the specification — no node states where a requester "
             "identity originates.\n"))
    done = run(work, root)
    assert done.returncode == 1, done.stdout + done.stderr
    assert "never persists" in done.stdout
    assert not (work / "plan.json").is_file()


# --------------------------------------------------- what a task is written to look like


def test_a_task_may_name_the_references_it_is_written_against(work, root, sound_plan, write_plan):
    """The field carries what a criterion cannot. A criterion is falsifiable on its own, and
    "matches the mockup" is not, so before this the layout reached the survey, the decomposition
    and the binding and then stopped at the step that writes the code."""
    write_plan("task/checkout/record-order", {
        "title": "Record order", "summary": "Persist a placed order.",
        "objective": "A valid order is persisted and retrievable by its order_number.",
        "criteria": ["Submitting a valid order returns its order_number."],
        "implements": ["domain/sales/order"],
        "reference": ["intake/layout/order-form.html"],
    })
    assert problems_in(work, root) == []


def test_the_validator_never_opens_a_reference(work, root, sound_plan, write_plan):
    """The same as `sources`, and for the same reason: what a task was written from is not a claim
    anything here can check. An absent path is the executor's stop, where the reading happens."""
    write_plan("task/checkout/record-order", {
        "title": "Record order", "summary": "Persist a placed order.",
        "objective": "A valid order is persisted and retrievable by its order_number.",
        "criteria": ["Submitting a valid order returns its order_number."],
        "implements": ["domain/sales/order"],
        "reference": ["intake/layout/nothing-was-ever-written-here.html"],
    })
    assert problems_in(work, root) == []


def test_a_reference_is_never_an_edge_of_the_plan(work, root, sound_plan, write_plan):
    """A reference points outside every root the graph describes — not at a task, not at a
    specification node. Deriving an edge for it would put a fourth kind in an index every
    committed plan.json is held to, and stale every one of them."""
    write_plan("task/checkout/record-order", {
        "title": "Record order", "summary": "Persist a placed order.",
        "objective": "A valid order is persisted and retrievable by its order_number.",
        "criteria": ["Submitting a valid order returns its order_number."],
        "implements": ["domain/sales/order"],
        "reference": ["intake/layout/order-form.html"],
    })
    assert run(work, root).returncode == 0
    graph = json.loads((work / "plan.json").read_text(encoding="utf-8"))
    assert {edge["kind"] for edge in graph["edges"]} <= {"depends_on", "implements", "covers"}
    assert not any("layout" in edge["to"] for edge in graph["edges"])


def test_an_epic_cannot_name_a_reference(work, root, sound_plan, write_plan):
    """An epic is a claim over the specification, not an input to writing anything."""
    write_plan("epic/checkout", {
        "title": "Checkout", "summary": "Everything order placement needs.",
        "covers": ["domain/sales/order", "domain/sales/invoice"],
        "reference": ["intake/layout/order-form.html"],
    })
    assert any("reference" in problem for problem in problems_in(work, root))


# ------------------------------------------------------------- --contract (branch extraction)

def test_a_defs_branch_is_sliced_self_contained():
    schema = json.loads(
        (Path(__file__).resolve().parent.parent / "src/claude/schemas/plan-node.json").read_text())
    sliced = plan.contract_branch(schema, "specNodeRef")
    assert "type" in sliced


def test_a_kind_branch_carries_only_what_that_kind_admits():
    schema = json.loads(
        (Path(__file__).resolve().parent.parent / "src/claude/schemas/plan-node.json").read_text())
    sliced = plan.contract_branch(schema, "task")
    assert sliced["kind"] == "task"
    assert "objective" in sliced["properties"] and "criteria" in sliced["properties"]
    assert "area" not in sliced["properties"], "area belongs to the inventory kind, not task"


def test_an_unknown_branch_names_every_branch_that_exists():
    schema = json.loads(
        (Path(__file__).resolve().parent.parent / "src/claude/schemas/plan-node.json").read_text())
    assert plan.contract_branch(schema, "no-such-branch") is None
    branches = plan.contract_branches(schema)
    assert "inventory" in branches and "task" in branches


def test_contract_cli_prints_a_branch_and_refuses_an_unknown_one():
    result = run("--contract", "inventory")
    assert result.returncode == 0, result.stderr
    printed = json.loads(result.stdout)
    assert printed["kind"] == "inventory"

    refused = run("--contract", "no-such-branch")
    assert refused.returncode == 2
    assert "no-such-branch is not a branch of plan-node.json" in refused.stderr


def test_contract_stands_alone():
    combined = run("--contract", "task", "--check")
    assert combined.returncode == 2
    assert "--contract stands alone" in combined.stderr
