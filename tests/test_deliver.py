"""What the delivery validator refuses, and why each refusal exists.

Every test here is a rule somebody could otherwise satisfy by leaving something out. The
totality checks are the heart of it — a record answers every criterion its task states and every
specification node its task implements — because an omission is invisible in the record that
omits it and reads as work that went fine. The rest holds the seams: a record answers a task
that exists, a proof stands beside an implementation, nothing is delivered before what it builds
on, and no pin outlives the plan it read.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml

import deliver
from conftest import STANDARD, task_pin_of

REPO = Path(__file__).resolve().parent.parent


def problems_of(delivery: Path, work: Path, target: Path, root: Path) -> list[str]:
    """Everything the validator would report over this delivery, in one list."""
    validator = deliver.contract()
    names = deliver.pass_names()
    plan_nodes, plan_problems = deliver.load_plan(work, root)
    assert plan_problems == [], f"the fixture plan does not hold together: {plan_problems}"
    nodes, found = deliver.collect(delivery, validator, names)
    return found + deliver.cross_problems(nodes, plan_nodes, work, names, delivery, target)


def said(problems: list[str], fragment: str) -> None:
    assert any(fragment in p for p in problems), \
        f"nothing reported {fragment!r}; what was reported was {problems}"


# ------------------------------------------------------------------- the sound case


def test_the_sound_delivery_holds_together(delivery, work, root, target, sound_delivery):
    assert problems_of(delivery, work, target, root) == []


def test_it_derives_the_index_it_promises(delivery, work, root, sound_delivery):
    validator = deliver.contract()
    names = deliver.pass_names()
    nodes, _ = deliver.collect(delivery, validator, names)
    graph = deliver.derive(nodes, names)
    assert graph["contract_version"] == "siegard-delivery/2"
    assert [n["id"] for n in graph["nodes"]] == ["implementation/checkout/record-order",
                                                 "proof/checkout/record-order"]
    kinds = {(e["from"], e["kind"], e["to"]) for e in graph["edges"]}
    assert ("implementation/checkout/record-order", "implements",
            "task/checkout/record-order") in kinds, "the path is what names the task answered"
    assert ("implementation/checkout/record-order", "encodes",
            "domain/sales/order") in kinds, "a fact in the source traces to the specification node"
    assert ("proof/checkout/record-order", "proves",
            "implementation/checkout/record-order") in kinds


def test_the_derivation_is_byte_stable(delivery, work, root, sound_delivery):
    validator = deliver.contract()
    names = deliver.pass_names()
    nodes, _ = deliver.collect(delivery, validator, names)
    once = json.dumps(deliver.derive(nodes, names), indent=2, ensure_ascii=False)
    twice = json.dumps(deliver.derive(nodes, names), indent=2, ensure_ascii=False)
    assert once == twice, "identical input must be byte-identical output, or --check is noise"


def test_the_index_satisfies_its_own_contract(repo, delivery, work, root, sound_delivery):
    from jsonschema import Draft202012Validator
    validator = deliver.contract()
    names = deliver.pass_names()
    nodes, _ = deliver.collect(delivery, validator, names)
    schema = json.loads((repo / "src/claude/schemas/delivery.json").read_text(encoding="utf-8"))
    broken = [e.message for e in Draft202012Validator(schema).iter_errors(
        deliver.derive(nodes, names))]
    assert broken == [], f"the derived delivery does not satisfy its contract: {broken}"


# --------------------------------------------------------------- the files as files


def test_a_path_that_computes_to_no_identifier_is_refused(delivery, work, root, target, sound_delivery):
    (delivery / "notes.md").write_text("---\ntitle: x\n---\n", encoding="utf-8")
    said(problems_of(delivery, work, target, root), "the path is the identity and this one computes to none")


def test_run_holds_material_and_is_never_a_node(delivery, work, root, target, sound_delivery):
    (delivery / "run" / "first").mkdir(parents=True)
    (delivery / "run" / "first" / "notes.md").write_text("not a node\n", encoding="utf-8")
    assert problems_of(delivery, work, target, root) == [], \
        "run/ holds what the commands printed; validating it as a node would refuse a log"


def test_the_orchestration_log_is_a_marker_and_never_a_node(delivery, work, root, target,
                                                             sound_delivery):
    """/deliver-scope appends its run to orchestration.md at the delivery root and promises the
    validator keeps it the way plan.py keeps closure.md. A marker the validator refused would be
    dropped by the first run that met the refusal, and the run's own decisions with it."""
    (delivery / deliver.ORCHESTRATION_FILE).write_text(
        "plan-work checkout: commit abc1234 — planned.\n", encoding="utf-8")
    assert problems_of(delivery, work, target, root) == []
    (delivery / "implementation" / deliver.ORCHESTRATION_FILE).write_text("stray\n",
                                                                         encoding="utf-8")
    said(problems_of(delivery, work, target, root),
         f"implementation/{deliver.ORCHESTRATION_FILE}: not implementation/")


def test_the_body_carries_exactly_two_headings(delivery, work, root, target, sound_delivery,
                                               write_delivery):
    path = delivery / "proof/checkout/record-order.md"
    path.write_text(path.read_text(encoding="utf-8").replace("## Notes", "## Findings"),
                    encoding="utf-8")
    said(problems_of(delivery, work, target, root), "body headings are")


def test_a_status_field_does_not_exist(delivery, work, root, target, sound_delivery, write_delivery):
    front = {"title": "Proof", "summary": "What proves it.", "status": "done",
             "tests": [{"file": "t.spec.ts", "name": "n", "proves": "p", "fails_when": "f"}]}
    write_delivery("proof/checkout/record-order", front)
    said(problems_of(delivery, work, target, root),
         "Additional properties are not allowed ('status' was unexpected)")


# ------------------------------------------------------------------ against the plan


def test_a_record_for_a_task_the_plan_does_not_hold(delivery, work, root, target, sound_delivery,
                                                    write_delivery):
    write_delivery("implementation/checkout/ship-order", {
        "title": "Ship", "summary": "Ship it.", "task": "sha256:" + "0" * 64,
        "files": [{"path": "src/ship.ts", "effect": "ships"}],
        "criteria": [{"criterion": "c", "met": True, "how": "h"}],
        "nodes": [{"node": "domain/sales/order", "how": "read only"}],
    })
    said(problems_of(delivery, work, target, root), "which the plan does not hold as a task")


def test_a_criterion_the_record_leaves_unanswered(delivery, work, root, target, sound_delivery,
                                                  write_plan):
    task = work / "task/checkout/record-order.md"
    task.write_text(task.read_text(encoding="utf-8").replace(
        "- Submitting a valid order returns its order_number.",
        "- Submitting a valid order returns its order_number.\n"
        "- A non-positive total is refused."), encoding="utf-8")
    said(problems_of(delivery, work, target, root), "cannot be read as complete")


def test_a_criterion_the_task_does_not_state(delivery, work, root, target, sound_delivery,
                                            write_delivery):
    front = json_front(delivery, "implementation/checkout/record-order")
    front["criteria"].append({"criterion": "Something nobody wrote.", "met": True, "how": "h"})
    write_delivery("implementation/checkout/record-order", front)
    said(problems_of(delivery, work, target, root), "which the task does not state")


def test_an_implemented_node_the_record_passes_over(delivery, work, root, target, sound_delivery,
                                                     write_delivery):
    front = json_front(delivery, "implementation/checkout/record-order")
    front["nodes"] = []
    write_delivery("implementation/checkout/record-order", front)
    problems = problems_of(delivery, work, target, root)
    said(problems, "the specification going unanswered in code")
    # The corrective act, not only the cost: two repairs are legitimate here and they live in
    # different roots, so a message naming neither leaves the reader to guess which.
    said(problems, "answer it in `nodes`, or update the task's `implements` through /plan-work")


def test_a_node_the_task_never_implemented(delivery, work, root, target, sound_delivery, write_delivery):
    front = json_front(delivery, "implementation/checkout/record-order")
    front["nodes"].append({"node": "domain/sales/invoice", "how": "read only"})
    write_delivery("implementation/checkout/record-order", front)
    said(problems_of(delivery, work, target, root), "which the task does not implement")


def test_nothing_is_delivered_before_what_it_builds_on(delivery, work, root, target, sound_delivery,
                                                       write_delivery):
    """bill-order builds on record-order. Remove record-order's record and the dependency is
    what has to be delivered first — with no status field to ask, the records are how that is
    known."""
    (delivery / "implementation/checkout/record-order.md").unlink()
    (delivery / "proof/checkout/record-order.md").unlink()
    write_delivery("implementation/checkout/bill-order", {
        "title": "Bill", "summary": "Raise the bill.",
        "task": task_pin_of(work, "task/checkout/bill-order"),
        "files": [{"path": "src/bill.ts", "effect": "bills"}],
        "criteria": [{"criterion": "Recording an order twice produces one invoice.",
                      "met": True, "how": "idempotent on order_number"}],
        "nodes": [{"node": "domain/sales/invoice", "how": "the invoice shape"}],
    })
    found = problems_of(delivery, work, target, root)
    said(found, "the dependency is what has to be delivered first")


def test_a_pin_that_outlived_its_task(delivery, work, root, target, sound_delivery, write_plan):
    """The record answers one task, so only that task moving disturbs it."""
    task = work / "task/checkout/record-order.md"
    task.write_text(task.read_text(encoding="utf-8").replace(
        "summary: Persist a placed order.", "summary: Persist a placed order, once."),
        encoding="utf-8")
    said(problems_of(delivery, work, target, root), "as it stands")


def test_another_task_moving_leaves_a_record_alone(delivery, work, root, target, sound_delivery,
                                                   write_plan):
    """Pinning the plan's index made every record in the root stale the moment any unrelated task
    was added, and no entry point owns re-pinning records it was forbidden to read."""
    write_plan("epic/shipping", {"title": "Shipping", "summary": "Later.",
                                 "covers": ["domain/sales/order"]})
    write_plan("task/shipping/ship-order", {
        "title": "Ship order", "summary": "Ship it.",
        "objective": "A recorded order ships once.",
        "criteria": ["A recorded order ships once."],
        "implements": ["domain/sales/order"],
    })
    assert problems_of(delivery, work, target, root) == []


def test_a_proof_without_an_implementation(delivery, work, root, target, sound_delivery):
    (delivery / "implementation/checkout/record-order.md").unlink()
    said(problems_of(delivery, work, target, root), "what a proof holds up has to exist first")


def rewrite_proof(delivery: Path, write_delivery, **test_fields) -> None:
    """The sound proof again, with its one test carrying whatever the caller adds."""
    import hashlib
    written = delivery / "implementation/checkout/record-order.md"
    write_delivery("proof/checkout/record-order", {
        "title": "Proof for recording a placed order",
        "summary": "What proves the recorded order.",
        "implementation": "sha256:" + hashlib.sha256(written.read_bytes()).hexdigest(),
        "tests": [{"file": "tests/place.spec.ts",
                   "name": "returns the order_number for a valid submission",
                   "proves": "Submitting a valid order returns its order_number.",
                   "fails_when": "place() answers with anything but the stored order_number",
                   **test_fields}],
    })


def test_a_test_may_demonstrate_a_node_its_task_implements(delivery, work, root, target,
                                                           sound_delivery, write_delivery):
    """The claim a review certifies: this test would fail if the node's fact stopped holding."""
    rewrite_proof(delivery, write_delivery, demonstrates="domain/sales/order")
    assert problems_of(delivery, work, target, root) == []


def test_a_test_may_not_demonstrate_a_node_its_task_does_not_implement(delivery, work, root,
                                                                       target, sound_delivery,
                                                                       write_delivery):
    """A proof answers its own task, and a review would certify this claim into a binding the
    trace decides by running that test — so a node the plan never gave the task is ground the
    proof cannot claim."""
    rewrite_proof(delivery, write_delivery, demonstrates="rules/sales/invoice-immutable")
    said(problems_of(delivery, work, target, root), "which this task does not implement")


def test_a_demonstrates_must_be_a_node_identity(delivery, work, root, target, sound_delivery,
                                                write_delivery):
    rewrite_proof(delivery, write_delivery, demonstrates="not a node identity")
    said(problems_of(delivery, work, target, root), "demonstrates")


def test_a_proof_carrying_no_demonstrates_is_the_ordinary_case(delivery, work, root, target,
                                                               sound_delivery):
    """A proof with no `demonstrates` validates: a task may implement only nodes no finite test
    decides, and the claim is the author's to make, never the validator's to demand."""
    assert problems_of(delivery, work, target, root) == []


# ------------------------------------------------------------------------ the review


def review_front(work: Path, root: Path, **overrides) -> dict:
    front = {
        "title": "Checkout, first review",
        "summary": "What the passes found.",
        "reviewed": ["src/orders/place.ts", "tests/place.spec.ts"],
        "tasks": ["task/checkout/record-order"],
        "passes": [
            {"pass": "coverage"},
            {"pass": "conformance"},
            {"pass": "standard", "missing": "this project has authored no standard"},
            {"pass": "failures", "missing": "no run was captured"},
        ],
        "coverage": [{"criterion": "Submitting a valid order returns its order_number.",
                      "state": "covered",
                      "tests": [{"file": "tests/place.spec.ts",
                                 "name": "returns the order_number for a valid submission"}]}],
        "unpaired": [],
    }
    front.update(overrides)
    return front


def set_pass(front: dict, name: str, **fields) -> None:
    """Rewrite one pass entry, found by its name. Never by index: a pass inserted before it would
    silently rewrite the wrong entry, and the test would keep passing while asserting something
    else."""
    for entry in front["passes"]:
        if entry["pass"] == name:
            entry.clear()
            entry["pass"] = name
            entry.update(fields)
            return
    raise AssertionError(f"the fixture holds no {name} pass entry")


def test_a_review_that_answers_for_every_pass_holds(delivery, work, root, target, sound_delivery,
                                                    write_delivery):
    write_delivery("review/first", review_front(work, root))
    assert problems_of(delivery, work, target, root) == []


def test_a_pass_left_unanswered_is_refused(delivery, work, root, target, sound_delivery,
                                           write_delivery):
    front = review_front(work, root)
    front["passes"] = front["passes"][:2]
    write_delivery("review/first", front)
    said(problems_of(delivery, work, target, root), "passes names no entry for `failures`")


def test_a_finding_cannot_claim_a_pass_that_did_not_run(delivery, work, root, target, sound_delivery,
                                                        write_delivery):
    front = review_front(work, root)
    front["findings"] = [{"pass": "failures", "file": "src/orders/place.ts",
                          "where": "line 3", "cause": "code",
                          "evidence": "expected the stated refusal, got a generic error",
                          "cost": "the refusal is unproven"}]
    write_delivery("review/first", front)
    said(problems_of(delivery, work, target, root), "a pass that did not run found nothing")


def test_a_cause_belongs_to_the_failures_pass_and_nowhere_else(delivery, work, root, target,
                                                               sound_delivery, write_delivery):
    front = review_front(work, root)
    front["findings"] = [{"pass": "conformance", "file": "src/orders/place.ts",
                          "where": "line 3", "cause": "code",
                          "evidence": "return refuse('ORDER_TOTAL_INVALID')",
                          "cost": "the code became the home of the refusal code"}]
    write_delivery("review/first", front)
    said(problems_of(delivery, work, target, root), "states `cause` outside the failures pass")


def test_a_failure_finding_without_a_cause(delivery, work, root, target, sound_delivery, write_delivery,
                                           run_dir):
    front = review_front(work, root)
    set_pass(front, "failures")
    front["run"] = "run/first"
    front["failures_counted"] = 1
    front["findings"] = [{"pass": "failures", "file": "tests/place.spec.ts",
                          "where": "line 8",
                          "evidence": "expected 409, got 500",
                          "cost": "the refusal answers the wrong way"}]
    write_delivery("review/first", front)
    said(problems_of(delivery, work, target, root), "states no `cause`")


def test_a_count_that_disagrees_with_the_findings(delivery, work, root, target, sound_delivery,
                                                  write_delivery, run_dir):
    run_dir()
    front = review_front(work, root)
    set_pass(front, "failures")
    front["run"] = "run/first"
    front["failures_counted"] = 3
    front["findings"] = [{"pass": "failures", "file": "tests/place.spec.ts",
                          "where": "line 8", "cause": "code",
                          "evidence": "expected 409, got 500",
                          "cost": "the refusal answers the wrong way"}]
    write_delivery("review/first", front)
    problems = problems_of(delivery, work, target, root)
    said(problems, "how a failure goes unexamined while the record still looks complete")
    # The obvious repair here is the forbidden one, so the message names it as forbidden rather
    # than leaving the reader to reach for the count.
    said(problems, "never lower the count or drop a finding to make the two agree")


def test_a_pass_that_ran_and_recorded_nothing_of_what_it_read(delivery, work, root, target,
                                                              sound_delivery, write_delivery):
    front = review_front(work, root)
    del front["coverage"]
    write_delivery("review/first", front)
    said(problems_of(delivery, work, target, root), "the coverage pass ran and `coverage` is absent")


def test_a_review_written_before_unpaired_existed_is_receipted_and_never_refused(
        delivery, work, root, target, sound_delivery, write_delivery):
    """Every review written before the field existed records no `unpaired`, and a field that
    became required would refuse a consumer's whole delivery root the day the framework updates.
    So absence is a receipt: what such a review did not do is read its test set in the other
    direction, and the receipt says so once, where a reader can act on it."""
    front = review_front(work, root)
    del front["unpaired"]
    write_delivery("review/first", front)
    assert problems_of(delivery, work, target, root) == []
    nodes, _ = deliver.collect(delivery, deliver.contract(), deliver.pass_names())
    lines = deliver.unread_unpaired(nodes)
    assert len(lines) == 1 and "records no `unpaired` list" in lines[0], lines


def test_a_review_carrying_unpaired_earns_no_such_receipt(delivery, work, root, target,
                                                          sound_delivery, write_delivery):
    write_delivery("review/first", review_front(work, root))
    nodes, _ = deliver.collect(delivery, deliver.contract(), deliver.pass_names())
    assert deliver.unread_unpaired(nodes) == []


def test_an_empty_unpaired_list_is_an_answer_and_not_an_omission(delivery, work, root, target,
                                                                 sound_delivery, write_delivery):
    write_delivery("review/first", review_front(work, root, unpaired=[]))
    assert problems_of(delivery, work, target, root) == []


def test_a_test_bearing_on_no_criterion_is_recorded_with_what_it_asserts(delivery, work, root,
                                                                         target, sound_delivery,
                                                                         write_delivery):
    """Never a verdict on the test: it may prove a sibling task's criterion, and what says which
    is what it asserts."""
    front = review_front(work, root, unpaired=[
        {"test": {"file": "tests/place.spec.ts", "name": "emits order.placed on the bus"},
         "asserts": "that placing an order publishes an order.placed event, which no criterion "
                    "of the tasks under this review states"}])
    write_delivery("review/first", front)
    assert problems_of(delivery, work, target, root) == []


def test_an_unpaired_entry_naming_no_assertion_is_refused(delivery, work, root, target,
                                                          sound_delivery, write_delivery):
    """A bare path says a test went unpaired and leaves a reader no way to tell a proof of a
    sibling's criterion from a proof of a fact nobody stated."""
    front = review_front(work, root, unpaired=[
        {"test": {"file": "tests/place.spec.ts", "name": "emits order.placed on the bus"}}])
    write_delivery("review/first", front)
    assert problems_of(delivery, work, target, root) != []


def test_unpaired_outside_a_coverage_pass_is_refused(delivery, work, root, target,
                                                     sound_delivery, write_delivery):
    front = review_front(work, root)
    front["passes"] = [{"pass": "coverage", "missing": "no proof record named a test"}
                       if entry["pass"] == "coverage" else entry
                       for entry in front["passes"]]
    del front["coverage"]
    write_delivery("review/first", front)
    said(problems_of(delivery, work, target, root),
         "`unpaired` is present and the coverage pass did not run")


def test_a_criterion_the_coverage_pass_left_out(delivery, work, root, target, sound_delivery,
                                                write_delivery):
    front = review_front(work, root)
    front["coverage"] = [{"criterion": "Something nobody wrote.", "state": "covered"}]
    write_delivery("review/first", front)
    said(problems_of(delivery, work, target, root), "an omitted criterion reads as one that passed")


def test_a_review_of_a_task_nothing_delivered(delivery, work, root, target, sound_delivery,
                                              write_delivery):
    front = review_front(work, root)
    front["tasks"] = ["task/checkout/bill-order"]
    front["coverage"] = [{"criterion": "Recording an order twice produces one invoice.",
                          "state": "uncovered", "why": "nothing exercises it"}]
    write_delivery("review/first", front)
    said(problems_of(delivery, work, target, root), "a review of a task nothing delivered has no subject")


def test_a_run_the_delivery_root_does_not_hold(delivery, work, root, target, sound_delivery,
                                               write_delivery):
    front = review_front(work, root)
    set_pass(front, "failures")
    front["run"] = "run/nowhere"
    front["failures_counted"] = 0
    write_delivery("review/first", front)
    said(problems_of(delivery, work, target, root), "which the delivery root does not hold")


# ------------------------------------------------ what a review says about its run


def test_a_failure_may_land_in_a_file_the_change_never_touched(delivery, work, root, target,
                                                               sound_delivery, write_delivery,
                                                               run_dir):
    """The passes that scan a file set are held to it. The failures pass is not: its subject is a
    captured run, and a change breaks tests it never touched. Refusing to record that would refuse
    the most useful thing a run says."""
    run_dir()
    front = review_front(work, root)
    set_pass(front, "failures")
    front["run"] = "run/first"
    front["failures_counted"] = 1
    front["findings"] = [{"pass": "failures", "file": "src/cart/total.spec.ts", "where": "line 4",
                          "cause": "code", "evidence": "expected 1, got 0",
                          "cost": "an area the change never touched now fails"}]
    write_delivery("review/first", front)
    assert problems_of(delivery, work, target, root) == []


def test_a_failure_may_name_no_file_at_all(delivery, work, root, target, sound_delivery, write_delivery,
                                           run_dir):
    """A command that could not be found, or a step that was terminated, is located by the step's
    own name because no file is its subject."""
    run_dir("not_found")
    front = review_front(work, root)
    set_pass(front, "failures")
    front["run"] = "run/first"
    front["failures_counted"] = 1
    front["findings"] = [{"pass": "failures", "where": "the suite step", "cause": "setup",
                          "evidence": "command not found: pnpm",
                          "cost": "nothing was proved about this code at all"}]
    write_delivery("review/first", front)
    assert problems_of(delivery, work, target, root) == []


def test_a_scanning_pass_still_may_not_leave_the_file_set(delivery, work, root, target, sound_delivery,
                                                          write_delivery):
    front = review_front(work, root)
    front["findings"] = [{"pass": "conformance", "file": "src/cart/total.ts", "where": "line 4",
                          "evidence": "x", "cost": "y"}]
    write_delivery("review/first", front)
    said(problems_of(delivery, work, target, root), "which `reviewed` does not list")


def test_a_review_cannot_report_no_failures_over_a_run_that_failed(delivery, work, root, target,
                                                                   sound_delivery,
                                                                   write_delivery, run_dir):
    """The hole this closes: every fact a review states about a run used to be the reviewer's own,
    so a record could claim the pass ran and counted nothing over a run that failed."""
    run_dir()
    front = review_front(work, root)
    set_pass(front, "failures")
    front["run"] = "run/first"
    front["failures_counted"] = 0
    write_delivery("review/first", front)
    said(problems_of(delivery, work, target, root), "and this review counted no failures")


def test_the_failures_pass_does_not_read_a_run_that_passed(delivery, work, root, target, sound_delivery,
                                                           write_delivery, run_dir):
    run_dir("passed")
    front = review_front(work, root)
    set_pass(front, "failures")
    front["run"] = "run/first"
    front["failures_counted"] = 1
    front["findings"] = [{"pass": "failures", "file": "src/orders/place.ts", "where": "line 4",
                          "cause": "code", "evidence": "x", "cost": "y"}]
    write_delivery("review/first", front)
    said(problems_of(delivery, work, target, root), "a pass that should not have been asked for")


def test_a_run_directory_the_runner_did_not_write(delivery, work, root, target, sound_delivery,
                                                  write_delivery):
    (delivery / "run" / "first").mkdir(parents=True)
    front = review_front(work, root)
    set_pass(front, "failures")
    front["run"] = "run/first"
    front["failures_counted"] = 1
    front["findings"] = [{"pass": "failures", "file": "src/orders/place.ts", "where": "line 4",
                          "cause": "code", "evidence": "x", "cost": "y"}]
    write_delivery("review/first", front)
    said(problems_of(delivery, work, target, root), "holds no run.json")


def test_the_coverage_pass_cannot_run_without_a_task(delivery, work, root, target, sound_delivery,
                                                    write_delivery):
    front = review_front(work, root)
    del front["tasks"]
    write_delivery("review/first", front)
    said(problems_of(delivery, work, target, root), "pairing tests with criteria nobody wrote")


# ------------------------------- what an implementation discloses about the standard


def disclosed(delivery: Path, work: Path, ref: dict, **overrides) -> dict:
    """The sound implementation record, plus a standard and one disclosed departure from it."""
    front = json_front(delivery, "implementation/checkout/record-order")
    front["standard"] = ref
    front["divergences"] = [{"cites": "ARC-01", "file": "src/orders/place.ts",
                             "departure": "place() constructs the store rather than receiving it.",
                             "why": "no factory exists for this module yet, and adding one reaches "
                                    "past this task"}]
    front.update(overrides)
    return front


def repin_proof(delivery: Path, write_delivery) -> None:
    """The proof pins the implementation, so rewriting one rewrites the other."""
    import hashlib
    front = json_front(delivery, "proof/checkout/record-order")
    written = (delivery / "implementation/checkout/record-order.md").read_bytes()
    front["implementation"] = "sha256:" + hashlib.sha256(written).hexdigest()
    write_delivery("proof/checkout/record-order", front)


def test_a_disclosed_departure_from_a_standard_rule_holds(delivery, work, root, target, sound_delivery,
                                                          write_delivery, write_standard,
                                                          run_dir):
    run_dir("passed", "build")
    write_delivery("implementation/checkout/record-order",
                   disclosed(delivery, work, write_standard(), run="run/build"))
    repin_proof(delivery, write_delivery)
    assert problems_of(delivery, work, target, root) == []


def test_an_implementation_may_depart_from_a_rule_a_tool_decides(delivery, work, root, target,
                                                                 sound_delivery, write_delivery,
                                                                 write_standard, run_dir):
    """The asymmetry that matters: a review may not judge a rule a tool decides, and a record may
    depart from one — it obeys the whole standard, and the run will show the tool's own failure."""
    run_dir("passed", "build")
    front = disclosed(delivery, work, write_standard(), run="run/build")
    front["divergences"][0]["cites"] = "PRH-01"
    write_delivery("implementation/checkout/record-order", front)
    repin_proof(delivery, write_delivery)
    assert problems_of(delivery, work, target, root) == []


def test_a_disclosure_citing_a_rule_the_standard_does_not_declare(delivery, work, root, target,
                                                                  sound_delivery, write_delivery,
                                                                  write_standard):
    front = disclosed(delivery, work, write_standard())
    front["divergences"][0]["cites"] = "ZZZ-99"
    write_delivery("implementation/checkout/record-order", front)
    repin_proof(delivery, write_delivery)
    said(problems_of(delivery, work, target, root), "which standard.yaml does not declare")


def test_a_disclosure_hung_on_a_file_the_rule_does_not_reach(delivery, work, root, target, sound_delivery,
                                                             write_delivery, write_standard):
    """ARC-02's scope is src/routes/ and the departure sits under src/orders/."""
    front = disclosed(delivery, work, write_standard())
    front["divergences"][0]["cites"] = "ARC-02"
    write_delivery("implementation/checkout/record-order", front)
    repin_proof(delivery, write_delivery)
    said(problems_of(delivery, work, target, root), "which that rule's scope does not reach")


def test_a_disclosure_citing_a_rule_with_no_standard_named(delivery, work, root, target, sound_delivery,
                                                           write_delivery):
    front = disclosed(delivery, work, {"at": "x.yaml", "pin": "sha256:" + "0" * 64})
    del front["standard"]
    write_delivery("implementation/checkout/record-order", front)
    repin_proof(delivery, write_delivery)
    said(problems_of(delivery, work, target, root), "this record names no standard")


def test_a_disclosure_naming_a_file_the_record_did_not_write(delivery, work, root, target, sound_delivery,
                                                             write_delivery, write_standard):
    front = disclosed(delivery, work, write_standard())
    front["divergences"][0]["file"] = "src/elsewhere.ts"
    write_delivery("implementation/checkout/record-order", front)
    repin_proof(delivery, write_delivery)
    said(problems_of(delivery, work, target, root), "which `files` does not list")


@pytest.mark.parametrize("departure, fragment", [
    ({"departure": "d.", "why": "w."},
     "names neither"),
    ({"departure": "d.", "why": "w.", "from": "a convention", "cites": "ARC-01",
      "file": "src/orders/place.ts"},
     "names both"),
    ({"departure": "d.", "why": "w.", "cites": "ARC-01"},
     "names no `file`"),
    ({"departure": "d.", "why": "w.", "file": "src/orders/place.ts"},
     "cites no rule"),
])
def test_a_departure_departs_from_exactly_one_thing(delivery, work, root, target, sound_delivery,
                                                    write_delivery, write_standard,
                                                    departure, fragment):
    front = disclosed(delivery, work, write_standard(), divergences=[departure])
    write_delivery("implementation/checkout/record-order", front)
    repin_proof(delivery, write_delivery)
    said(problems_of(delivery, work, target, root), fragment)


def test_an_implementation_pin_is_never_reverified_against_the_live_standard(
        delivery, work, root, target, sound_delivery, write_delivery, write_standard, run_dir):
    """The pin is a citation of what was read when the record was written, not a standing
    guarantee — like a task's `implements`, it is never mechanically reverified against the file
    as it stands today. A project free to keep evolving its own registry cannot retroactively
    invalidate a record written against an earlier version of it."""
    run_dir("passed", "build")
    ref = write_standard()
    write_delivery("implementation/checkout/record-order",
                   disclosed(delivery, work, ref, run="run/build"))
    path = target / ref["at"]
    path.write_text(path.read_text(encoding="utf-8") + "\n# edited after the record\n",
                    encoding="utf-8")
    repin_proof(delivery, write_delivery)
    assert problems_of(delivery, work, target, root) == []


# ------------------------------------------- a task the plan leaves ungoverned


def test_a_task_that_binds_nothing_can_be_delivered(delivery, work, root, target, sound_plan,
                                                    write_plan, write_delivery):
    """plan-work cuts such a task deliberately — scaffolding is real work, and the plan says why in
    its own `rationale`. The record answers for no bound node because there is none to answer for,
    and before this the contract made that record impossible to write at all."""
    write_plan("task/checkout/scaffold", {
        "title": "Scaffold", "summary": "Set the toolchain up.",
        "objective": "The project builds and its suite runs.",
        "criteria": ["The suite runs and reports."],
        "rationale": "No base node governs the toolchain; the plan decided this cut itself."})
    write_delivery("implementation/checkout/scaffold", {
        "title": "Scaffold", "summary": "The toolchain this project builds with.",
        "task": task_pin_of(work, "task/checkout/scaffold"),
        "files": [{"path": "package.json", "effect": "declares the build and the suite"}],
        "criteria": [{"criterion": "The suite runs and reports.", "met": True,
                      "how": "the suite script runs the runner over the test tree"}]})
    assert problems_of(delivery, work, target, root) == []


# ---------------------------------------------------- the proof and its subject


def test_a_proof_left_behind_by_a_rewritten_implementation(delivery, work, root, target, sound_delivery,
                                                           write_delivery):
    """A re-delivery that rewrites the implementation and leaves the proof alone would otherwise
    validate clean, with tests claiming to prove criteria the source now satisfies another way."""
    front = json_front(delivery, "implementation/checkout/record-order")
    front["files"][0]["effect"] = "persists a submitted order through the new store"
    write_delivery("implementation/checkout/record-order", front)
    said(problems_of(delivery, work, target, root), "the proof has not")


def test_a_proof_rewritten_alone_over_a_standing_implementation_validates(delivery, work, root,
                                                                          target, sound_delivery,
                                                                          write_delivery):
    """The pin's asymmetry is one-way by design, and proof-only re-delivery stands on it: a proof
    rewritten whole while the implementation record did not move restamps the same pin and
    validates — the sanctioned route when a sibling task's legitimate delivery falsifies an
    assertion that claimed more than this task's criteria establish."""
    import hashlib
    written = delivery / "implementation/checkout/record-order.md"
    write_delivery("proof/checkout/record-order", {
        "title": "Proof for recording a placed order, re-proven",
        "summary": "The proof rewritten whole against the tree as it now stands.",
        "implementation": "sha256:" + hashlib.sha256(written.read_bytes()).hexdigest(),
        "tests": [{"file": "tests/place.spec.ts",
                   "name": "returns the order_number for a valid submission",
                   "proves": "Submitting a valid order returns its order_number.",
                   "fails_when": "the adapter this task ships stops implementing the store "
                                 "interface — scoped by interface, no longer by directory count"}],
    })
    assert problems_of(delivery, work, target, root) == []




# ------------------------------------------------------- the project's own standard


def standard_review(work: Path, root: Path, ref: dict, **overrides) -> dict:
    front = review_front(work, root)
    set_pass(front, "standard")
    front["standard"] = ref
    front.update(overrides)
    return front


def green_review(work: Path, root: Path, ref: dict, run_dir, **overrides) -> dict:
    """A review against the fixture standard — which declares commands — over the run those
    commands owe it, green: the run is recorded, and the failures pass did not run because there
    was no failure to read, which is what its entry says."""
    run_dir("passed", "first")
    front = standard_review(work, root, ref, run="run/first", **overrides)
    set_pass(front, "failures", missing="run/first passed; there was no failure to read")
    return front


def test_a_review_against_a_standard_holds(delivery, work, root, target, sound_delivery,
                                           write_delivery, write_standard, run_dir):
    front = green_review(work, root, write_standard(), run_dir)
    front["findings"] = [{"pass": "standard", "file": "src/orders/place.ts",
                          "where": "line 12, the constructor", "cites": "ARC-01",
                          "evidence": "constructor(private readonly store: PostgresStore)",
                          "cost": "the entry point cannot be exercised without a live store"}]
    write_delivery("review/first", front)
    assert problems_of(delivery, work, target, root) == []


def test_a_clean_standard_pass_says_what_it_was_clean_over(delivery, work, root, target,
                                                           sound_delivery, write_delivery,
                                                           write_standard, run_dir):
    """No findings at all is a real result: the copy and its pin are what the set of rules in
    scope derives from, so the record needs no list of them to be answerable."""
    write_delivery("review/first", green_review(work, root, write_standard(), run_dir))
    assert problems_of(delivery, work, target, root) == []


def test_the_standard_must_be_there_to_be_checked(delivery, work, root, target, sound_delivery,
                                                  write_delivery, write_standard):
    ref = write_standard()
    (target / ref["at"]).unlink()
    write_delivery("review/first", standard_review(work, root, ref))
    said(problems_of(delivery, work, target, root), "does not exist")


def test_a_standard_spelled_from_the_wrong_anchor_is_handed_its_spelling(
        delivery, work, root, target, sound_delivery, write_delivery, tmp_path):
    """Four records in one consumer window spelled the standard's path from the repository root,
    and the bare `does not exist` sent each into its own fix-and-rerun cycle. The refusal walks
    the target's ancestors and hands the corrected spelling, so the class ends in one cycle."""
    import hashlib
    from conftest import STANDARD
    outside = tmp_path / "standards" / "standard.yaml"
    outside.parent.mkdir()
    outside.write_text(yaml.safe_dump(STANDARD, sort_keys=False), encoding="utf-8")
    ref = {"at": "standards/standard.yaml",
           "pin": "sha256:" + hashlib.sha256(outside.read_bytes()).hexdigest()}
    write_delivery("review/first", standard_review(work, root, ref))
    problems = problems_of(delivery, work, target, root)
    said(problems, "does not resolve inside")
    said(problems, "never to the repository around it")
    said(problems, "`../standards/standard.yaml`")


def test_the_deliverable_line_names_the_worktree_route_and_its_counterfeit():
    """The parallel door is printed at the one moment a caller learns the set holds more than
    one — and beside it, why the tempting substitute (one general-purpose agent per task) is not
    that route: an agent cannot spawn the two producers, so implementation and proof land in one
    context. A consumer window measured exactly that pattern and paid every proof twice."""
    line = deliver.deliverable_line(["task/a/x", "task/a/y"], False)
    assert "one git worktree each" in line
    assert "general-purpose agent" in line
    assert "cannot spawn the two producers" in line
    single = deliver.deliverable_line(["task/a/x"], False)
    assert "worktree" not in single, "a set of one holds no parallel route to offer"


def test_a_standard_that_does_not_hold_together(delivery, work, root, target, sound_delivery,
                                                write_delivery, write_standard):
    from conftest import STANDARD
    broken = {**STANDARD, "rules": [{**STANDARD["rules"][0], "decided_by": "tool"}]}
    write_delivery("review/first", standard_review(work, root, write_standard(broken)))
    said(problems_of(delivery, work, target, root), "'tool' is a required property")


def test_a_review_pin_is_never_reverified_against_the_live_standard(
        delivery, work, root, target, sound_delivery, write_delivery, write_standard, run_dir):
    """Same discipline as an implementation's: the pin is a citation of what this review read
    when it was written, never mechanically reverified against the file as it stands today."""
    ref = write_standard()
    path = target / ref["at"]
    path.write_text(path.read_text(encoding="utf-8") + "\n# edited after the review\n",
                    encoding="utf-8")
    write_delivery("review/first", green_review(work, root, ref, run_dir))
    assert problems_of(delivery, work, target, root) == []



def test_a_finding_citing_a_rule_a_tool_decides(delivery, work, root, target, sound_delivery,
                                                write_delivery, write_standard):
    front = standard_review(work, root, write_standard())
    front["findings"] = [{"pass": "standard", "file": "src/orders/place.ts", "where": "line 3",
                          "cites": "PRH-01", "evidence": "console.log(order)", "cost": "y"}]
    write_delivery("review/first", front)
    said(problems_of(delivery, work, target, root), "says a tool decides")


def test_a_finding_citing_a_rule_the_standard_does_not_declare(delivery, work, root, target,
                                                               sound_delivery, write_delivery,
                                                               write_standard):
    front = standard_review(work, root, write_standard())
    front["findings"] = [{"pass": "standard", "file": "src/orders/place.ts", "where": "line 3",
                          "cites": "ZZZ-99", "evidence": "x", "cost": "y"}]
    write_delivery("review/first", front)
    said(problems_of(delivery, work, target, root), "which standard.yaml does not declare")



def test_a_finding_hung_on_a_rule_that_does_not_govern_the_file(delivery, work, root, target,
                                                                sound_delivery, write_delivery,
                                                                write_standard):
    """ARC-02's scope is src/routes/ and the finding names a file under src/orders/."""
    front = standard_review(work, root, write_standard())
    front["findings"] = [{"pass": "standard", "file": "src/orders/place.ts", "where": "line 12",
                          "cites": "ARC-02", "evidence": "x", "cost": "y"}]
    write_delivery("review/first", front)
    said(problems_of(delivery, work, target, root), "which that rule's scope does not reach")


def test_a_finding_against_a_file_the_rule_does_not_reach(delivery, work, root, target, sound_delivery,
                                                          write_delivery, write_standard):
    """ARC-01's scope is src/, and the finding names a test file that `reviewed` does list."""
    front = standard_review(work, root, write_standard())
    front["findings"] = [{"pass": "standard", "file": "tests/place.spec.ts", "where": "line 3",
                          "cites": "ARC-01", "evidence": "x", "cost": "y"}]
    write_delivery("review/first", front)
    said(problems_of(delivery, work, target, root), "which that rule's scope does not reach")


def test_the_standard_and_its_pass_agree(delivery, work, root, target, sound_delivery, write_delivery,
                                         write_standard):
    front = review_front(work, root)          # the standard pass records itself as not run
    front["standard"] = write_standard()
    write_delivery("review/first", front)
    said(problems_of(delivery, work, target, root), "`standard` is present and the standard pass did not run")


def test_a_finding_outside_the_file_set(delivery, work, root, target, sound_delivery, write_delivery,
                                        write_standard):
    front = standard_review(work, root, write_standard())
    front["findings"] = [{"pass": "standard", "file": "src/nowhere.ts", "where": "line 1",
                          "cites": "ARC-01", "evidence": "x", "cost": "y"}]
    write_delivery("review/first", front)
    said(problems_of(delivery, work, target, root), "which `reviewed` does not list")


def test_a_review_records_which_passes_ran_in_the_index(delivery, work, root, sound_delivery,
                                                        write_delivery, write_standard):
    """The derivation emits every pass the contract allows. Before a review reached a fixture,
    delivery.json's own enum held three names and this path exited as a defect in the script."""
    write_delivery("review/first", standard_review(work, root, write_standard()))
    validator = deliver.contract()
    names = deliver.pass_names()
    nodes, _ = deliver.collect(delivery, validator, names)
    graph = deliver.derive(nodes, names)
    entry = next(n for n in graph["nodes"] if n["kind"] == "review")
    assert entry["ran"] == ["coverage", "conformance", "standard"], \
        "the index names the passes that ran, in the order the contract declares them"
    from jsonschema import Draft202012Validator
    schema = json.loads((REPO / "src/claude/schemas/delivery.json").read_text(encoding="utf-8"))
    assert [e.message for e in Draft202012Validator(schema).iter_errors(graph)] == []


# ----------------------------------------------------------------- what remains open


def test_the_outstanding_report_derives_what_no_field_records(delivery, work, root, target,
                                                              sound_delivery):
    validator = deliver.contract()
    names = deliver.pass_names()
    nodes, _ = deliver.collect(delivery, validator, names)
    plan_nodes, _ = deliver.load_plan(work, root)
    report = deliver.outstanding_report(nodes, plan_nodes, target)
    assert "task/checkout/bill-order: no record" in report
    assert "task/checkout/record-order:" not in report, \
        "a task with a record and a proof is not outstanding"


def test_the_outstanding_report_names_the_set_a_caller_may_take_now(delivery, work, root, target,
                                                                   sound_delivery):
    """The subtraction the handoff used to describe in words. One task is delivered, the other
    declares it builds on it, so nothing is deliverable — and saying so is the answer, not a gap."""
    validator = deliver.contract()
    nodes, _ = deliver.collect(delivery, validator, deliver.pass_names())
    plan_nodes, _ = deliver.load_plan(work, root)
    report = deliver.outstanding_report(nodes, plan_nodes, target)
    assert "deliverable now: task/checkout/bill-order" in report, report

    (delivery / "implementation/checkout/record-order.md").unlink()
    (delivery / "proof/checkout/record-order.md").unlink()
    nodes, _ = deliver.collect(delivery, validator, deliver.pass_names())
    report = deliver.outstanding_report(nodes, plan_nodes, target)
    assert "deliverable now: task/checkout/record-order — no record, nothing they wait on" \
        in report, report
    assert "task/checkout/bill-order" not in report.splitlines()[-2], \
        "a task waiting on one with no record is not deliverable now"


def test_an_implementation_without_its_proof_is_reported(delivery, work, root, target,
                                                         sound_delivery):
    (delivery / "proof/checkout/record-order.md").unlink()
    validator = deliver.contract()
    names = deliver.pass_names()
    nodes, _ = deliver.collect(delivery, validator, names)
    plan_nodes, _ = deliver.load_plan(work, root)
    assert "no proof record holds it up" in deliver.outstanding_report(nodes, plan_nodes, target)


def test_a_standing_blocking_note_is_named_where_a_caller_chooses(delivery, work, root, target,
                                                                 sound_delivery, write_plan):
    """The one refusal the plan's index cannot hold, said where a caller picks a task rather than
    two commands later. It is named, never refused: this exits 0, and the stop stays the skill's."""
    write_plan("task/checkout/bill-order", {
        "title": "Bill order", "summary": "Raise the bill for a recorded order.",
        "objective": "A recorded order produces exactly one invoice.",
        "criteria": ["Recording an order twice produces one invoice."],
        "implements": ["domain/sales/invoice"],
    }, body="## What it is\nProse for a reader.\n\n## Notes\n"
            "BLOCKING, from the specification — the criterion asserts a refund exceeding the "
            "cap rules/sales/refund-cap states.\n")
    validator = deliver.contract()
    nodes, _ = deliver.collect(delivery, validator, deliver.pass_names())
    plan_nodes, _ = deliver.load_plan(work, root)
    report = deliver.outstanding_report(nodes, plan_nodes, target)
    assert "1 standing BLOCKING note(s), which only a person settles" in report, report
    assert "the criterion asserts a refund exceeding the cap" in report, \
        "the entry is quoted, so a caller learns what it concedes without opening the file"
    assert "deliverable now: none" in report, report


def test_an_underdetermined_note_is_quoted_and_bars_nothing(delivery, work, root, target,
                                                            sound_delivery, write_plan):
    """The entries /implement-task hands to the test author, read by a script instead of collected
    by eye — and they are not a stop: the task stays deliverable, because the note is the tests'
    to exclude, not a person's to settle."""
    write_plan("task/checkout/bill-order", {
        "title": "Bill order", "summary": "Raise the bill for a recorded order.",
        "objective": "A recorded order produces exactly one invoice.",
        "criteria": ["Recording an order twice produces one invoice."],
        "implements": ["domain/sales/invoice"],
    }, body="## What it is\nProse for a reader.\n\n## Notes\n"
            "UNDERDETERMINED, from the specification — a bill of zero lines satisfies every "
            "criterion and the invoice definition refuses it.\n")
    validator = deliver.contract()
    nodes, _ = deliver.collect(delivery, validator, deliver.pass_names())
    plan_nodes, _ = deliver.load_plan(work, root)
    report = deliver.outstanding_report(nodes, plan_nodes, target)
    assert "1 UNDERDETERMINED note(s) the proof must exclude" in report, report
    assert "a bill of zero lines satisfies every criterion" in report, report
    assert "deliverable now: task/checkout/bill-order" in report, \
        "an underdetermined note travels with the task and stops nothing"


# --------------------------------------------------------------- a closed plan, and the CLI


def test_a_closed_plan_is_delivered_against_without_the_base(delivery, work, root, target,
                                                             sound_delivery):
    """A closed plan is history, and it validates without opening today's base — the same rule
    plan.py applies, inherited here because the plan is read through it. The pin stops being a
    currency constraint and stands as the anchor naming what the binding read."""
    (work / "closure.md").write_text("The initiative is over.\n", encoding="utf-8")
    nodes, problems = deliver.load_plan(work, None)
    assert problems == [], problems
    assert "task/checkout/record-order" in nodes
    validator = deliver.contract()
    names = deliver.pass_names()
    found, _ = deliver.collect(delivery, validator, names)
    assert deliver.cross_problems(found, nodes, work, names, delivery, target) == []


def test_the_cli_derives_checks_and_reports(delivery, work, root, target, sound_delivery):
    import subprocess
    import sys
    script = REPO / "src/claude/bin/deliver.py"

    def invoke(*args):
        return subprocess.run([sys.executable, "-B", str(script), *args, str(delivery),
                               str(work), str(target), str(root)], capture_output=True, text=True)

    stale = invoke("--check")
    assert stale.returncode == 1 and "STALE" in stale.stdout, \
        "an index that has never been derived is stale, not sound"

    derived = invoke()
    assert derived.returncode == 0, derived.stderr
    assert "contract siegard-delivery/2" in derived.stdout
    assert (delivery / "delivery.json").is_file()

    assert invoke("--check").returncode == 0, "what was just derived must read as current"

    by_hand = json.loads((delivery / "delivery.json").read_text(encoding="utf-8"))
    assert by_hand["contract_version"] == "siegard-delivery/2"

    outstanding = invoke("--outstanding")
    assert outstanding.returncode == 0, outstanding.stderr
    assert "task/checkout/bill-order" in outstanding.stdout


def test_the_cli_refuses_a_plan_that_does_not_hold(delivery, work, root, target, sound_delivery):
    import subprocess
    import sys
    (work / "epic/checkout.md").unlink()
    done = subprocess.run([sys.executable, "-B", str(REPO / "src/claude/bin/deliver.py"),
                           str(delivery), str(work), str(target), str(root)],
                          capture_output=True, text=True)
    assert done.returncode == 2, done.stdout
    assert "fix it with plan.py before" in done.stderr


def test_the_cli_needs_the_specification_while_the_plan_is_live(delivery, work, root, target,
                                                                 sound_delivery):
    import subprocess
    import sys
    done = subprocess.run([sys.executable, "-B", str(REPO / "src/claude/bin/deliver.py"),
                           str(delivery), str(work), str(target)], capture_output=True, text=True)
    assert done.returncode == 2
    assert "name the specification root" in done.stderr


def test_a_captured_run_reaches_a_review(delivery, work, root, target, sound_delivery, write_delivery):
    """The whole chain the review skill describes: the runner writes evidence to disk, the review
    points at it by directory, and the validator holds the two together."""
    import subprocess
    import sys
    captured = subprocess.run(
        [sys.executable, "-B", str(REPO / "src/claude/bin/run.py"), str(delivery),
         "--run", "first", "--cwd", str(REPO), "--timeout-seconds", "20",
         "--step", "suite=python3 -c 'raise SystemExit(1)'"],
        capture_output=True, text=True)
    assert captured.returncode == 1, captured.stderr
    record = json.loads((delivery / "run/first/run.json").read_text(encoding="utf-8"))
    assert record["run"] == "run/first" and record["outcome"] == "failed"

    front = review_front(work, root)
    set_pass(front, "failures")
    front["run"] = record["run"]
    front["failures_counted"] = 1
    front["findings"] = [{"pass": "failures", "file": "tests/place.spec.ts",
                          "where": "line 8", "cause": "code",
                          "evidence": "expected the stated refusal, got a generic error",
                          "cost": "the refusal answers the wrong way",
                          "correction": "answer with the refusal the bound rule names"}]
    write_delivery("review/first", front)
    assert problems_of(delivery, work, target, root) == []


# ------------------------------------------------------------------------- fixtures


@pytest.fixture
def run_dir(delivery: Path, target: Path):
    """A captured run, as the runner writes one. The validator opens it, so a bare directory is
    not a run."""
    def put(outcome: str = "failed", slug: str = "first",
            steps: tuple[str, ...] = ("install", "lint", "test"),
            commands: dict[str, str] | None = None, cwd: Path | None = None,
            contract: str = "siegard-run/2") -> Path:
        # The step names and the commands are the registry's, because that is the join the whole
        # split hangs on: a rule names the step that decides it, the runner records the outcome
        # and the command under that name, and a record is held to having covered it under that
        # command, from the target. A fixture inventing a name, a command or a directory of its
        # own would be a run nothing could be checked against.
        declared = {c["step"]: c["command"] for c in STANDARD["commands"]}
        declared.update(commands or {})
        recorded, stopped = [], False
        for name in steps:
            if stopped:
                said = "not_run"
            elif name == steps[-1]:
                said = outcome
            else:
                said = "passed"
            attempted = said != "not_run"
            recorded.append({"name": name, "command": declared.get(name, "true"),
                             "outcome": said,
                             "exit_code": 0 if said == "passed" else 1,
                             "output": f"{name}.log" if attempted else None,
                             "started_at": "2026-01-01T00:00:00.000+00:00" if attempted else None,
                             "ended_at": "2026-01-01T00:00:01.000+00:00" if attempted else None})
            stopped = stopped or said not in ("passed",)
        where = delivery / "run" / slug
        where.mkdir(parents=True, exist_ok=True)
        (where / "run.json").write_text(json.dumps({
            "contract_version": contract, "run": f"run/{slug}", "cwd": str(cwd or target),
            "timeout_seconds": 20, "outcome": outcome,
            "failed_step": None if outcome == "passed" else steps[-1],
            "steps": recorded,
            "combined_output": "run.log"}, indent=2), encoding="utf-8")
        return where
    return put


def json_front(delivery: Path, did: str) -> dict:
    """One node's frontmatter, read back so a test can change exactly one field of it."""
    import re

    import yaml
    text = (delivery / f"{did}.md").read_text(encoding="utf-8")
    return yaml.safe_load(re.match(r"^---\n(.*?)\n---\n", text, re.S).group(1))



# ------------------------------------------- what a proof may disclose, and what it produces

def proof_disclosing(delivery: Path, ref: dict, **overrides) -> dict:
    """The sound proof, plus the standard it read and one disclosed departure from it. The rules
    about how a project writes its tests reach files no implementation ever lists, so until the
    proof carried these two fields a rule the tests could not satisfy had nowhere to be said."""
    front = json_front(delivery, "proof/checkout/record-order")
    front["standard"] = ref
    front["divergences"] = [{"cites": "TST-01", "file": "tests/place.spec.ts",
                             "departure": "the spec constructs the store rather than standing one "
                                          "in through the interface.",
                             "why": "no stand-in exists for it yet, and writing one reaches past "
                                    "what this task proves"}]
    front.update(overrides)
    return front


def test_a_proof_may_disclose_a_departure_from_a_standard_rule(delivery, work, root, target,
                                                               sound_delivery, write_delivery,
                                                               write_standard, run_dir):
    run_dir("passed", "suite")
    write_delivery("proof/checkout/record-order",
                   proof_disclosing(delivery, write_standard(), run="run/suite"))
    assert problems_of(delivery, work, target, root) == []


def test_a_proof_departure_sits_in_a_file_its_tests_list(delivery, work, root, target, sound_delivery,
                                                         write_delivery, write_standard):
    """The implementation's rule, applied to what a proof writes: a departure sits in a file this
    record says it wrote, and for a proof that is `tests` rather than `files`."""
    front = proof_disclosing(delivery, write_standard())
    front["divergences"][0]["file"] = "tests/elsewhere.spec.ts"
    write_delivery("proof/checkout/record-order", front)
    said(problems_of(delivery, work, target, root), "which `tests` does not list")


def test_a_proof_citing_a_rule_the_standard_does_not_declare(delivery, work, root, target, sound_delivery,
                                                             write_delivery, write_standard):
    front = proof_disclosing(delivery, write_standard())
    front["divergences"][0]["cites"] = "ZZZ-99"
    write_delivery("proof/checkout/record-order", front)
    said(problems_of(delivery, work, target, root), "which standard.yaml does not declare")


def test_a_proof_citing_a_rule_with_no_standard_named(delivery, work, root, target, sound_delivery,
                                                      write_delivery):
    front = proof_disclosing(delivery, {"at": "x.yaml", "pin": "sha256:" + "0" * 64})
    del front["standard"]
    write_delivery("proof/checkout/record-order", front)
    said(problems_of(delivery, work, target, root), "this record names no standard")


def produces(work: Path, delivery: Path, write_plan, write_delivery, paths: list[str]) -> None:
    """The fixture task, plus the artifacts it says its delivery must create — repinned, because
    a task rewritten under a record that pinned it is exactly what the pin exists to catch."""
    front = json_front(work, "task/checkout/record-order")
    front["produces"] = paths
    write_plan("task/checkout/record-order", front)
    record = json_front(delivery, "implementation/checkout/record-order")
    record["task"] = task_pin_of(work, "task/checkout/record-order")
    write_delivery("implementation/checkout/record-order", record)
    repin_proof(delivery, write_delivery)


def test_a_task_that_produces_an_artifact_is_held_to_writing_it(delivery, work, root, target,
                                                                sound_delivery, write_plan,
                                                                write_delivery):
    """The claim that ends the stop is held to what was written. Without this a substrate task
    could be delivered having created nothing, and every task after it would stop on an absence
    this one was cut to end — with a record saying it had been."""
    produces(work, delivery, write_plan, write_delivery, ["package.json"])
    said(problems_of(delivery, work, target, root), "the task says it produces package.json")


def test_a_task_that_produces_what_the_record_wrote_holds(delivery, work, root, target, sound_delivery,
                                                          write_plan, write_delivery):
    (target / "src" / "orders").mkdir(parents=True)
    (target / "src" / "orders" / "place.ts").write_text("export {};\n", encoding="utf-8")
    produces(work, delivery, write_plan, write_delivery, ["src/orders/place.ts"])
    assert problems_of(delivery, work, target, root) == []


def test_what_a_task_produces_stands_in_the_target(delivery, work, root, target, sound_delivery,
                                                   write_plan, write_delivery):
    """`files` listing the artifact is the record's claim; the tree is what the next delivery
    refuses on. A record claiming an artifact the target does not hold is the claim outliving
    the thing, and every later task stops on an absence this record says was ended."""
    produces(work, delivery, write_plan, write_delivery, ["src/orders/place.ts"])
    said(problems_of(delivery, work, target, root),
         "the task says it produces src/orders/place.ts, `files` lists it, and")
    said(problems_of(delivery, work, target, root), "does not hold it")


def test_the_substrate_barrier_is_named_because_no_edge_can_carry_it(delivery, work, root, target,
                                                                    sound_delivery, write_plan):
    """The one thing `waits on` cannot say. The task producing what every rule needs takes no
    dependency edge — an edge from every other task to it would be a fact somebody kept true by
    hand — so nothing in the graph shows that every other delivery stops before it writes."""
    front = json_front(work, "task/checkout/record-order")
    front["produces"] = ["package.json", "tsconfig.json"]
    write_plan("task/checkout/record-order", front)
    write_plan("task/checkout/tidy-logs", {
        "title": "Tidy logs", "summary": "Scaffolding the specification does not govern.",
        "objective": "The service logs through one configured logger.",
        "criteria": ["Every module logs through the configured logger."],
        "rationale": "The scope asked for it and no node holds it.",
    })
    (delivery / "implementation/checkout/record-order.md").unlink()
    (delivery / "proof/checkout/record-order.md").unlink()
    (target / "tsconfig.json").write_text("{}\n", encoding="utf-8")

    validator = deliver.contract()
    nodes, _ = deliver.collect(delivery, validator, deliver.pass_names())
    plan_nodes, _ = deliver.load_plan(work, root)
    report = deliver.outstanding_report(nodes, plan_nodes, target)
    assert "produces the substrate every other delivery waits on" in report, report
    assert "  package.json: ABSENT" in report, report
    assert "  tsconfig.json: stands" in report, \
        "existence is the whole of the question, and the half that stands is said too"
    assert "deliverable now: task/checkout/record-order —" in report, report
    assert "the task(s) building what the tree does not hold" in report, report
    assert "task/checkout/tidy-logs: no record" in report, \
        "the task is still outstanding and the report still says so"
    assert "deliverable now: task/checkout/record-order, task/checkout/tidy-logs" not in report, \
        "a task that waits on nothing still stops on an absent substrate, and the set says so"


def test_a_substrate_the_tree_already_holds_bars_nothing(delivery, work, root, target,
                                                         sound_delivery, write_plan):
    """`produces` is not a standing barrier: once the artifacts stand, the task is one task."""
    front = json_front(work, "task/checkout/record-order")
    front["produces"] = ["package.json"]
    write_plan("task/checkout/record-order", front)
    (delivery / "implementation/checkout/record-order.md").unlink()
    (delivery / "proof/checkout/record-order.md").unlink()
    (target / "package.json").write_text("{}\n", encoding="utf-8")

    validator = deliver.contract()
    nodes, _ = deliver.collect(delivery, validator, deliver.pass_names())
    plan_nodes, _ = deliver.load_plan(work, root)
    report = deliver.outstanding_report(nodes, plan_nodes, target)
    assert "produces the substrate" not in report, report
    assert "no record, nothing they wait on" in report, report


def test_the_outstanding_report_names_the_standard_this_root_remembers(delivery, work, root,
                                                                       target, sound_delivery,
                                                                       write_delivery,
                                                                       write_standard):
    """A delivery written against no rules and one written against rules nobody handed over
    produce the same clean output, and only the root can tell them apart."""
    write_delivery("implementation/checkout/record-order",
                   disclosed(delivery, work, write_standard()))
    repin_proof(delivery, write_delivery)
    validator = deliver.contract()
    nodes, _ = deliver.collect(delivery, validator, deliver.pass_names())
    plan_nodes, _ = deliver.load_plan(work, root)
    report = deliver.outstanding_report(nodes, plan_nodes, target)
    assert "standard.yaml (target app): pinned by 1 record(s)" in report
    assert "an invocation naming no standard now writes source" in report


# ------------------------------- what a record captured, and what it was allowed to install

def test_a_record_over_a_run_that_did_not_pass(delivery, work, root, target, sound_delivery,
                                               write_delivery, write_standard, run_dir):
    """The mirror of the review's rule, and the reason both exist. A review's run that passed is
    refused — there was no failure to diagnose. A delivery's run that failed is refused — the
    record claims what the run denied. Neither erases anything: the failed run keeps its directory,
    and the runner refuses to let a later one take its name."""
    run_dir("failed", "build")
    write_delivery("implementation/checkout/record-order",
                   disclosed(delivery, work, write_standard(), run="run/build"))
    repin_proof(delivery, write_delivery)
    said(problems_of(delivery, work, target, root), "run again under a name of its own")


def test_a_record_naming_a_run_the_runner_never_wrote(delivery, work, root, target, sound_delivery,
                                                      write_delivery, write_standard):
    (delivery / "run" / "build").mkdir(parents=True)
    write_delivery("implementation/checkout/record-order",
                   disclosed(delivery, work, write_standard(), run="run/build"))
    repin_proof(delivery, write_delivery)
    said(problems_of(delivery, work, target, root), "is not a run this framework captured")


def test_a_package_the_standard_does_not_authorize(delivery, work, root, target, sound_delivery,
                                                   write_delivery, write_standard, run_dir):
    """The allowlist is where a human's approval of a package lives — the only place it survives
    the session it was given in. A delivery that could install past it would make it decorative."""
    run_dir("passed", "build")
    write_delivery("implementation/checkout/record-order",
                   disclosed(delivery, work, write_standard(), run="run/build",
                             installed=["left-pad"]))
    repin_proof(delivery, write_delivery)
    said(problems_of(delivery, work, target, root), "which standard.yaml does not "
                                            "authorize")


def test_a_package_the_standard_authorizes(delivery, work, root, target, sound_delivery, write_delivery,
                                           write_standard, run_dir):
    run_dir("passed", "build")
    write_delivery("implementation/checkout/record-order",
                   disclosed(delivery, work, write_standard(), run="run/build",
                             installed=["pino"]))
    repin_proof(delivery, write_delivery)
    assert problems_of(delivery, work, target, root) == []


def test_packages_installed_against_no_standard_at_all(delivery, work, root, target, sound_delivery,
                                                       write_delivery):
    front = json_front(delivery, "implementation/checkout/record-order")
    front["installed"] = ["pino"]
    write_delivery("implementation/checkout/record-order", front)
    repin_proof(delivery, write_delivery)
    said(problems_of(delivery, work, target, root), "the names resolve against nothing")


def test_a_standard_that_declares_commands_is_owed_a_run(delivery, work, root, target, sound_delivery,
                                                         write_delivery, write_standard):
    """Source handed over having never been executed is the state this arrangement exists to end.
    A registry saying how the project is installed and checked is one whose delivery could be run,
    and a delivery that could be and was not is refused rather than reported."""
    front = json_front(delivery, "implementation/checkout/record-order")
    front["standard"] = write_standard()
    write_delivery("implementation/checkout/record-order", front)
    repin_proof(delivery, write_delivery)
    said(problems_of(delivery, work, target, root), "captured no run")


def test_what_each_kind_owes_differs_by_when_it_is_written(delivery, work, root, target, sound_delivery,
                                                           write_delivery, write_standard,
                                                           run_dir):
    """An implementation is written before any test exists, so it owes the checks that do not need
    one; a proof is written after, so it owes them all. A registry whose only command is the suite
    therefore owes the implementation nothing and the proof a run."""
    from conftest import STANDARD
    suite_only = {k: v for k, v in STANDARD.items() if k != "dependencies"}
    suite_only["rules"] = [r for r in STANDARD["rules"] if r["decided_by"] == "reading"]
    suite_only["commands"] = [{"step": "test", "command": "true", "timeout_seconds": 60,
                                "role": "suite"}]
    ref = write_standard(suite_only, name="suite-only.yaml")

    front = json_front(delivery, "implementation/checkout/record-order")
    front["standard"] = ref
    write_delivery("implementation/checkout/record-order", front)
    repin_proof(delivery, write_delivery)
    assert problems_of(delivery, work, target, root) == [], "the implementation owes no run here"

    proof = json_front(delivery, "proof/checkout/record-order")
    proof["standard"] = ref
    write_delivery("proof/checkout/record-order", proof)
    said(problems_of(delivery, work, target, root), "proof/checkout/record-order")

    run_dir("passed", "suite")
    proof["run"] = "run/suite"
    write_delivery("proof/checkout/record-order", proof)
    assert problems_of(delivery, work, target, root) == []


# ------------------------------------------------- every path has one anchor


def test_no_path_field_admits_an_absolute_path():
    """`produces`, `files[].path` and `reviewed[]` are compared to each other and to the
    registry's scopes by spelling, so all of them are stated against one anchor — the target
    source root — and an absolute path is refused at the contract, not discovered as a
    comparison that never matches."""
    from jsonschema import Draft202012Validator
    delivery = json.loads((REPO / "src/claude/schemas/delivery-node.json").read_text())
    plan_node = json.loads((REPO / "src/claude/schemas/plan-node.json").read_text())
    cases = {
        "files[].path": delivery["$defs"]["writtenFile"]["properties"]["path"],
        "reviewed[]": delivery["properties"]["reviewed"]["items"],
        "produces[]": plan_node["properties"]["produces"]["items"],
    }
    for name, schema in cases.items():
        judge = Draft202012Validator(schema)
        assert judge.is_valid("src/routes/case.ts"), f"{name} refuses an ordinary relative path"
        assert not judge.is_valid("/etc/passwd"), f"{name} admits an absolute path"


def test_the_written_file_path_states_its_anchor():
    """The anchor is load-bearing prose: three fields compare by spelling, and the contract is
    where the spelling's root is stated once."""
    delivery = json.loads((REPO / "src/claude/schemas/delivery-node.json").read_text())
    stated = delivery["$defs"]["writtenFile"]["properties"]["path"]["description"]
    assert "relative to the target source root" in stated.lower()


def test_a_record_answering_one_node_twice_is_refused(delivery, work, root, target,
                                                      sound_delivery, write_delivery):
    """The guard was here and nothing exercised it. It matters beyond the contradiction it names:
    `trace.py --bind-record --replace` folds a record's answers in order, so a record answering one
    node twice would have the second fold drop the first's files inside a single invocation. What
    keeps that from reaching the trace is this refusal, one script earlier."""
    front = yaml.safe_load(
        re.match(r"^---\n(.*?)\n---\n",
                 (delivery / "implementation/checkout/record-order.md").read_text(
                     encoding="utf-8"), re.S).group(1))
    front["nodes"] = front["nodes"] + [{
        "node": "domain/sales/order",
        "encoded_at": ["src/orders/place.ts"],
        "how": "said a second time, with a different reason"}]
    write_delivery("implementation/checkout/record-order", front)
    said(problems_of(delivery, work, target, root),
         "nodes answers for `domain/sales/order` 2 times")


# ------------------------------------------------------------- --contract (branch extraction)

def test_a_defs_branch_is_sliced_self_contained():
    """A `$defs` entry comes back as its own object, with an internal `$ref` inlined rather than
    left dangling — a slice that still pointed into the file it was sliced from would not be a
    slice."""
    schema = json.loads((REPO / "src/claude/schemas/delivery-node.json").read_text())
    sliced = deliver.contract_branch(schema, "finding")
    assert sliced["required"] == ["pass", "where", "evidence", "cost"]
    assert "$ref" not in json.dumps(sliced["properties"]["pass"])
    assert sliced["properties"]["pass"]["enum"] == ["coverage", "conformance", "failures",
                                                    "standard"]


def test_a_kind_branch_carries_only_what_that_kind_admits():
    """An `implementation` slice names the fields that kind's `propertyNames` enum allows, and no
    others — a reviewer handed this instead of the whole file cannot mistake a `proof`-only field
    for one of its own."""
    schema = json.loads((REPO / "src/claude/schemas/delivery-node.json").read_text())
    sliced = deliver.contract_branch(schema, "implementation")
    assert sliced["kind"] == "implementation"
    assert "task" in sliced["properties"] and "files" in sliced["properties"]
    assert "reviewed" not in sliced["properties"], \
        "reviewed belongs to the review kind, not implementation"


def test_an_unknown_branch_names_every_branch_that_exists():
    schema = json.loads((REPO / "src/claude/schemas/delivery-node.json").read_text())
    assert deliver.contract_branch(schema, "no-such-branch") is None
    branches = deliver.contract_branches(schema)
    assert "finding" in branches and "implementation" in branches


def test_contract_cli_prints_a_branch_and_refuses_an_unknown_one():
    import subprocess
    import sys
    script = REPO / "src/claude/bin/deliver.py"
    result = subprocess.run([sys.executable, "-B", str(script), "--contract", "coverageEntry"],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    printed = json.loads(result.stdout)
    assert printed["properties"]["state"]["enum"] == \
        ["covered", "partial", "uncovered", "unauditable"]

    refused = subprocess.run([sys.executable, "-B", str(script), "--contract", "no-such-branch"],
                             capture_output=True, text=True)
    assert refused.returncode == 2
    assert "no-such-branch is not a branch of any contract this script slices" in refused.stderr
    assert "delivery-node.json:" in refused.stderr


def contract(*args: str) -> subprocess.CompletedProcess:
    import subprocess as _sp
    import sys as _sys
    return _sp.run([_sys.executable, "-B", str(REPO / "src/claude/bin/deliver.py"),
                    "--contract", *args], capture_output=True, text=True)


def test_contract_slices_the_registry_as_well_as_the_delivery_node():
    """A registry is the artifact a human authors by hand, and until this printed it the only
    home of what `commands[]` or a rule may declare was a file under the plugin's own schemas,
    which a person with the question had to know was there."""
    for branch, marker in (("command", "timeout_seconds"), ("rule", "decided_by"),
                           ("presupposition", "path"), ("dependency", "")):
        out = contract(branch)
        assert out.returncode == 0, f"--contract {branch}: {out.stderr}"
        assert out.stdout.strip().startswith("{"), f"--contract {branch} printed nothing"
        assert marker in out.stdout, f"--contract {branch} is not the registry's branch"
    proof = contract("proof")
    assert proof.returncode == 0 and "implementation" in proof.stdout


def test_contract_with_no_branch_lists_every_one_it_answers_for():
    """A caller who knows the flag and not the names is the ordinary case, and a refusal is a
    poor way to learn them."""
    out = contract()
    assert out.returncode == 0, out.stderr
    for name in ("delivery-node.json", "standard.json", "proof", "command"):
        assert name in out.stdout
    assert "spec.py --contract" in out.stdout and "plan.py --contract" in out.stdout, \
        "the index names where the other contracts are printed, or it is a dead end"


def test_an_unknown_branch_is_refused_naming_every_contract_sliced():
    out = contract("nosuchbranch")
    assert out.returncode == 2
    assert "delivery-node.json:" in out.stderr and "standard.json:" in out.stderr


def test_a_branch_carries_no_pointer_into_a_file_its_reader_was_not_given():
    """A slice is pasted whole into a delegation's prompt, so a `$ref` surviving in it points at
    a file that reader does not have — the exact problem `--contract` exists to remove. Draft
    2020-12 admits keywords beside a `$ref`, and a field written that way must inline all the
    same, with the siblings winning: they are the more specific statement."""
    import subprocess
    import sys
    script = REPO / "src/claude/bin/deliver.py"
    for branch in ("proof", "finding", "implementation", "review", "coverageEntry"):
        out = subprocess.run([sys.executable, "-B", str(script), "--contract", branch],
                             capture_output=True, text=True)
        assert out.returncode == 0, out.stderr
        assert "$ref" not in out.stdout, f"--contract {branch} leaves a dangling pointer"
    proof = subprocess.run([sys.executable, "-B", str(script), "--contract", "proof"],
                           capture_output=True, text=True).stdout
    assert "domain|rules|scenarios|contracts" in proof, \
        "`demonstrates` shares specNodeRef's shape; the slice has to carry it"
    assert "offered as the proof of" in proof, "the sibling description must survive the inline"


def test_contract_stands_alone():
    import subprocess
    import sys
    script = REPO / "src/claude/bin/deliver.py"
    combined = subprocess.run(
        [sys.executable, "-B", str(script), "--contract", "finding", "--check"],
        capture_output=True, text=True)
    assert combined.returncode == 2
    assert "--contract stands alone" in combined.stderr


# ------------------------------------------------------------- --standard --reading (item 2)

def test_reading_excludes_every_tool_decided_rule(target, write_standard):
    ref = write_standard()
    path = target / ref["at"]
    import subprocess
    import sys
    script = REPO / "src/claude/bin/deliver.py"
    result = subprocess.run(
        [sys.executable, "-B", str(script), "--standard", str(path), "--reading"],
        capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    printed = json.loads(result.stdout)
    ids = {r["id"] for r in printed}
    assert ids == {"ARC-01", "ARC-02", "TST-01"}, ids
    assert "PRH-01" not in ids, "a tool-decided rule reached a reading judgment"


def test_for_narrows_to_rules_whose_scope_the_named_paths_reach(target, write_standard):
    ref = write_standard()
    path = target / ref["at"]
    import subprocess
    import sys
    script = REPO / "src/claude/bin/deliver.py"
    result = subprocess.run(
        [sys.executable, "-B", str(script), "--standard", str(path), "--reading",
         "--for", "src/orders/place.ts"],
        capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    ids = {r["id"] for r in json.loads(result.stdout)}
    assert ids == {"ARC-01"}, \
        f"src/orders/place.ts is not under src/routes, so ARC-02 should not reach it: {ids}"


def test_for_over_several_paths_unions_what_each_reaches(target, write_standard):
    ref = write_standard()
    path = target / ref["at"]
    import subprocess
    import sys
    script = REPO / "src/claude/bin/deliver.py"
    result = subprocess.run(
        [sys.executable, "-B", str(script), "--standard", str(path), "--reading",
         "--for", "src/orders/place.ts", "--for", "src/routes/order.ts"],
        capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    ids = {r["id"] for r in json.loads(result.stdout)}
    assert ids == {"ARC-01", "ARC-02"}, ids


def test_for_without_reading_has_no_effect_and_is_refused():
    import subprocess
    import sys
    script = REPO / "src/claude/bin/deliver.py"
    result = subprocess.run(
        [sys.executable, "-B", str(script), "--standard", "whatever.yaml", "--for", "a.ts"],
        capture_output=True, text=True)
    assert result.returncode == 2
    assert "--for narrows --reading" in result.stderr


def test_reading_refuses_alongside_against():
    import subprocess
    import sys
    script = REPO / "src/claude/bin/deliver.py"
    result = subprocess.run(
        [sys.executable, "-B", str(script), "--standard", "whatever.yaml", "--reading",
         "--against", "."],
        capture_output=True, text=True)
    assert result.returncode == 2
    assert "--reading stands with --standard and --for at most" in result.stderr


# ------------------------------------------------ a review and its reconciliation record


def traced(target: Path) -> None:
    (target / "siegard-trace.json").write_text(json.dumps(
        {"specification": "specs", "bindings": []}) + "\n", encoding="utf-8")


def reconciliation_record(target: Path, name: str, files: list[str]) -> str:
    folder = target / "siegard-reconcile"
    folder.mkdir(exist_ok=True)
    front = {"contract_version": "siegard-reconcile/3", "title": name, "summary": "a review's",
             "target": "backend",
             "files": [{"path": p, "change": "written by the delivery"} for p in files],
             "nodes": []}
    (folder / f"{name}.md").write_text(
        "---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n\n## What it is\n\nA review's fold.\n",
        encoding="utf-8")
    return f"siegard-reconcile/{name}.md"


def test_a_review_over_a_traced_target_naming_no_record_validates_and_is_receipted(
        delivery, work, root, target, sound_delivery, write_delivery):
    """Every review written before the field existed names none, and a field that became
    required would refuse a consumer's whole delivery root the day the framework updates. So the
    absence is said, never refused: the review judged the plan's nodes alone."""
    traced(target)
    write_delivery("review/first", review_front(work, root))
    assert problems_of(delivery, work, target, root) == []
    nodes, _ = deliver.collect(delivery, deliver.contract(), deliver.pass_names())
    receipt = deliver.unreconciled_reviews(nodes, target)
    assert len(receipt) == 1 and receipt[0].startswith("review/first: ")
    assert "judged the plan's nodes alone" in receipt[0]


def test_a_review_naming_its_record_draws_no_receipt(delivery, work, root, target, sound_delivery,
                                                     write_delivery):
    traced(target)
    front = review_front(work, root)
    front["reconciliation"] = reconciliation_record(target, "first", front["reviewed"])
    write_delivery("review/first", front)
    nodes, _ = deliver.collect(delivery, deliver.contract(), deliver.pass_names())
    assert deliver.unreconciled_reviews(nodes, target) == []


def test_a_review_over_an_untraced_target_owes_no_record(delivery, work, root, target,
                                                         sound_delivery, write_delivery):
    write_delivery("review/first", review_front(work, root))
    assert problems_of(delivery, work, target, root) == []
    nodes, _ = deliver.collect(delivery, deliver.contract(), deliver.pass_names())
    assert deliver.unreconciled_reviews(nodes, target) == [], \
        "nothing has been bound in this target, so there was no collateral to judge"


def test_the_named_record_holds_and_covers_the_reviewed_set(delivery, work, root, target,
                                                            sound_delivery, write_delivery):
    traced(target)
    front = review_front(work, root)
    front["reconciliation"] = reconciliation_record(target, "first", front["reviewed"])
    write_delivery("review/first", front)
    assert problems_of(delivery, work, target, root) == []


def test_a_record_over_a_different_file_set_judged_a_different_change(delivery, work, root, target,
                                                                      sound_delivery,
                                                                      write_delivery):
    traced(target)
    front = review_front(work, root)
    front["reconciliation"] = reconciliation_record(target, "first",
                                                    ["src/orders/place.ts", "src/orders/x.ts"])
    write_delivery("review/first", front)
    problems = problems_of(delivery, work, target, root)
    said(problems, "accounts for none of tests/place.spec.ts")
    said(problems, "accounts for src/orders/x.ts, which `reviewed` does not list")


def test_a_record_that_does_not_exist_is_refused(delivery, work, root, target, sound_delivery,
                                                 write_delivery):
    traced(target)
    front = review_front(work, root)
    front["reconciliation"] = "siegard-reconcile/first.md"
    write_delivery("review/first", front)
    said(problems_of(delivery, work, target, root), "does not exist")


def test_a_record_named_over_a_conformance_pass_that_did_not_run(delivery, work, root, target,
                                                                sound_delivery, write_delivery):
    front = review_front(work, root)
    set_pass(front, "conformance", missing="the specification root was not supplied")
    front["reconciliation"] = reconciliation_record(target, "first", front["reviewed"])
    write_delivery("review/first", front)
    said(problems_of(delivery, work, target, root),
         "`reconciliation` is present and the conformance pass did not run")


# ------------------------------------------------------------ the record's own target


def declare_targets(target: Path, **more: str) -> None:
    """Rewrite the target's project file to declare `app` (the fixture's root) plus the given
    keys, each a directory created under it — the shape of a project delivering into several
    target source roots from one delivery root."""
    import json
    import subprocess
    for path in more.values():
        (target / path).mkdir(parents=True, exist_ok=True)
    (target / "siegard.json").write_text(
        json.dumps({"targets": {"app": ".", **more}}), encoding="utf-8")
    # The project file is read at the target's git toplevel, the way trace.py reads it; a
    # consumer's targets all sit under one repository, and so do this fixture's.
    subprocess.run(["git", "init", "-q", str(target)], check=True, capture_output=True)


def second_target_record(home: Path, work: Path, write_delivery, **overrides) -> None:
    """The fixture plan's other task, delivered into a second target root `web` — its files, its
    standard and its key all spelled from that root."""
    import hashlib
    registry = home / "web" / "standard.yaml"
    # Only the suite step: an implementation record owes a run for every other step, and this
    # record's question is where its standard resolves, not whether it ran.
    registry.write_text(yaml.safe_dump({
        **{k: v for k, v in STANDARD.items() if k != "dependencies"},
        "commands": [STANDARD["commands"][2]],
        "rules": [r for r in STANDARD["rules"] if r["decided_by"] == "reading"]},
        sort_keys=False), encoding="utf-8")
    pin = "sha256:" + hashlib.sha256(registry.read_bytes()).hexdigest()
    write_delivery("implementation/checkout/bill-order", {
        "target": "web",
        "title": "Bill a recorded order",
        "summary": "The invoice raised once per recorded order.",
        "task": task_pin_of(work, "task/checkout/bill-order"),
        "standard": {"at": "standard.yaml", "pin": pin},
        "files": [{"path": "src/billing/bill.ts", "effect": "raises exactly one invoice"}],
        "criteria": [{"criterion": "Recording an order twice produces one invoice.",
                      "met": True, "how": "bill() is idempotent over the order_number"}],
        "nodes": [{"node": "domain/sales/invoice", "encoded_at": ["src/billing/bill.ts"],
                   "how": "the invoice's shape is what bill() persists"}],
        **overrides,
    })


def test_a_delivery_reaching_two_targets_validates_whole_under_either(
        delivery, work, root, target, sound_delivery, write_delivery):
    declare_targets(target, web="web")
    second_target_record(target, work, write_delivery)
    assert problems_of(delivery, work, target, root) == []
    assert problems_of(delivery, work, target / "web", root) == []


def test_a_record_is_resolved_at_its_own_target_and_never_the_invocations(
        delivery, work, root, target, sound_delivery, write_delivery):
    """The second record's standard exists only under `web`; spelled from there it resolves, and
    the invocation naming `app` changes nothing about that."""
    declare_targets(target, web="web")
    second_target_record(target, work, write_delivery)
    assert not (target / "standard.yaml").is_file()
    assert problems_of(delivery, work, target, root) == []


def test_a_target_the_project_does_not_declare(delivery, work, root, target, sound_delivery,
                                              write_delivery):
    declare_targets(target, web="web")
    second_target_record(target, work, write_delivery, target="mobile")
    problems = problems_of(delivery, work, target, root)
    said(problems, "implementation/checkout/bill-order: names target mobile, which siegard.json's "
                   "`targets` does not declare (declared: app, web)")


def test_a_record_without_a_target_is_refused_by_the_contract(
        delivery, work, root, target, sound_delivery, write_delivery):
    front = yaml.safe_load(
        (delivery / "implementation/checkout/record-order.md").read_text(encoding="utf-8")
        .split("---\n")[1])
    del front["target"]
    path = delivery / "implementation/checkout/record-order.md"
    path.write_text(f"---\n{yaml.safe_dump(front, sort_keys=False)}---\n"
                    + path.read_text(encoding="utf-8").split("---\n", 2)[2], encoding="utf-8")
    said(problems_of(delivery, work, target, root), "'target' is a required property")


def test_a_project_file_nobody_wrote_resolves_no_target(delivery, work, root, target,
                                                        sound_delivery):
    (target / "siegard.json").unlink()
    problems = problems_of(delivery, work, target, root)
    said(problems, f"no project file at {target / 'siegard.json'}")
    said(problems, "names target app, which siegard.json's `targets` does not declare "
                   "(declared: none)")


def test_a_standard_spelled_from_the_wrong_root_is_corrected_against_the_records_own_target(
        delivery, work, root, target, sound_delivery, write_delivery):
    """A record under `web` that spelled its registry from the repository around it — `web/…` —
    is told the spelling from its own root, not from the root the invocation named."""
    declare_targets(target, web="web")
    second_target_record(target, work, write_delivery)
    path = delivery / "implementation/checkout/bill-order.md"
    path.write_text(path.read_text(encoding="utf-8")
                    .replace("at: standard.yaml", "at: web/standard.yaml"), encoding="utf-8")
    (target / "web/web").mkdir()
    (target / "web/web/standard.yaml").write_bytes(b"")  # exists, so the ancestor walk is what
    (target / "web/web/standard.yaml").unlink()          # finds it — not a file under web/web
    problems = problems_of(delivery, work, target, root)
    said(problems, f"web/standard.yaml: does not resolve inside {target / 'web'}")
    said(problems, "from the target that is spelled `standard.yaml`")


def test_the_standards_receipt_says_which_target_pins_each(
        delivery, work, root, target, sound_delivery, write_delivery, write_standard):
    """Two roots may hold a registry under the same relative path; the receipt keeps them apart."""
    declare_targets(target, web="web")
    second_target_record(target, work, write_delivery)
    ref = write_standard()
    path = delivery / "implementation/checkout/record-order.md"
    front = yaml.safe_load(path.read_text(encoding="utf-8").split("---\n")[1])
    front["standard"] = ref
    body = path.read_text(encoding="utf-8").split("---\n", 2)[2]
    path.write_text(f"---\n{yaml.safe_dump(front, sort_keys=False)}---\n{body}", encoding="utf-8")
    validator = deliver.contract()
    nodes, found = deliver.collect(delivery, validator, deliver.pass_names())
    assert found == []
    receipt = deliver.standards_held(nodes)
    assert "standard.yaml (target app): pinned by 1 record(s)" in "\n".join(receipt)
    assert "standard.yaml (target web): pinned by 1 record(s)" in "\n".join(receipt)


# ------------------------------- a run is held to its commands and its directory, not its names


def test_a_step_run_under_another_command_than_the_registrys(delivery, work, root, target,
                                                             sound_delivery, write_delivery,
                                                             write_standard, run_dir):
    """A run whose `lint` passed says a step called lint exited 0; the rule `lint` decides needs
    the registry's lint to have — and the only thing tying the two is the command string the
    runner wrote beside the outcome. `--step lint="echo X"` validating is the name standing in
    for the command."""
    run_dir("passed", "build", commands={"lint": "echo X"})
    write_delivery("implementation/checkout/record-order",
                   disclosed(delivery, work, write_standard(), run="run/build"))
    repin_proof(delivery, write_delivery)
    said(problems_of(delivery, work, target, root),
         "run run/build step lint ran `echo X` where the registry declares `true`")


def test_a_command_is_compared_by_what_the_shell_reads(delivery, work, root, target,
                                                       sound_delivery, write_delivery,
                                                       write_standard, run_dir):
    """The runner records `shlex.join` of what it split; the registry spells the command by
    hand. A quoting difference is not a different command."""
    run_dir("passed", "build", commands={"lint": "'true'"})
    write_delivery("implementation/checkout/record-order",
                   disclosed(delivery, work, write_standard(), run="run/build"))
    repin_proof(delivery, write_delivery)
    assert problems_of(delivery, work, target, root) == []


def test_a_run_from_outside_the_target_is_refused(delivery, work, root, target, sound_delivery,
                                                  write_delivery, write_standard, run_dir,
                                                  tmp_path):
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    run_dir("passed", "build", cwd=elsewhere)
    write_delivery("implementation/checkout/record-order",
                   disclosed(delivery, work, write_standard(), run="run/build"))
    repin_proof(delivery, write_delivery)
    said(problems_of(delivery, work, target, root),
         f"run run/build ran in {elsewhere}, not the target")


def test_a_run_from_the_same_path_under_another_checkout_is_the_target(
        delivery, work, root, target, sound_delivery, write_delivery, run_dir, tmp_path):
    """A git worktree carries the whole tree at another toplevel, and the parallel route the
    module docstring describes captures every run there. The target is held by its path within
    the project, so a run from `<other checkout>/web` is a run in the target `web`."""
    import hashlib
    declare_targets(target, web="web")
    second_target_record(target, work, write_delivery)
    registry = target / "web" / "standard.yaml"
    front = json_front(delivery, "implementation/checkout/bill-order")
    data = yaml.safe_load(registry.read_text(encoding="utf-8"))
    data["commands"] = [{"step": "lint", "command": "true", "timeout_seconds": 60}]
    registry.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    front["standard"] = {"at": "standard.yaml",
                         "pin": "sha256:" + hashlib.sha256(registry.read_bytes()).hexdigest()}
    front["run"] = "run/web-build"
    write_delivery("implementation/checkout/bill-order", front)
    worktree = tmp_path / "wt-bill-order" / "web"
    worktree.mkdir(parents=True)
    run_dir("passed", "web-build", steps=("lint",), cwd=worktree)
    assert problems_of(delivery, work, target, root) == []
    run_dir("passed", "web-build", steps=("lint",), cwd=tmp_path / "wt-bill-order")
    said(problems_of(delivery, work, target, root), "not the target")


def test_a_step_the_caller_added_beyond_the_registry_stands(delivery, work, root, target,
                                                            sound_delivery, write_delivery,
                                                            write_standard, run_dir):
    """The registry says what must run, not what may: a caller's own step under a name the
    registry does not declare is held to nothing."""
    run_dir("passed", "build", steps=("install", "lint", "smoke", "test"),
            commands={"smoke": "echo smoke"})
    write_delivery("implementation/checkout/record-order",
                   disclosed(delivery, work, write_standard(), run="run/build"))
    repin_proof(delivery, write_delivery)
    assert problems_of(delivery, work, target, root) == []


# ------------------------------------------------- a review over a registry declaring commands


def test_a_review_over_a_registry_declaring_commands_owes_a_run(delivery, work, root, target,
                                                                sound_delivery, write_delivery,
                                                                write_standard):
    """The review is the one run over the whole change. Over a registry that declares how the
    project is checked, a review naming no run read the change and never built it."""
    write_delivery("review/first", standard_review(work, root, write_standard()))
    said(problems_of(delivery, work, target, root),
         "declares the step(s) install, lint, test and this review captured no run")


def test_a_review_records_its_green_run_and_the_failures_pass_says_it_passed(
        delivery, work, root, target, sound_delivery, write_delivery, write_standard, run_dir):
    """A run in which everything passed is the one case where the failures pass does not run,
    and the run is still recorded: the entry says the run passed, which is what was missing."""
    write_delivery("review/first", green_review(work, root, write_standard(), run_dir))
    assert problems_of(delivery, work, target, root) == []


def test_a_review_recording_a_red_run_it_did_not_read(delivery, work, root, target,
                                                      sound_delivery, write_delivery,
                                                      write_standard, run_dir):
    """A run that did not pass reported something, and the failures pass is what reads it."""
    run_dir("failed", "first")
    front = standard_review(work, root, write_standard(), run="run/first")
    set_pass(front, "failures", missing="no run was captured")
    write_delivery("review/first", front)
    said(problems_of(delivery, work, target, root),
         "run/first ended `failed` and the failures pass did not run")


def test_a_reviews_green_run_that_skipped_a_registry_step(delivery, work, root, target,
                                                          sound_delivery, write_delivery,
                                                          write_standard, run_dir):
    run_dir("passed", "first", steps=("install", "test"))
    front = standard_review(work, root, write_standard(), run="run/first")
    set_pass(front, "failures", missing="run/first passed; there was no failure to read")
    write_delivery("review/first", front)
    said(problems_of(delivery, work, target, root),
         "run/first passed having run only install, test; nothing decided the rules lint own")


def test_a_reviews_run_is_held_to_the_registrys_commands(delivery, work, root, target,
                                                         sound_delivery, write_delivery,
                                                         write_standard, run_dir):
    run_dir("passed", "first", commands={"test": "echo X"})
    front = standard_review(work, root, write_standard(), run="run/first")
    set_pass(front, "failures", missing="run/first passed; there was no failure to read")
    write_delivery("review/first", front)
    said(problems_of(delivery, work, target, root),
         "review/first: run run/first step test ran `echo X` where the registry declares `true`")


# ----------------------------------------------------- four prose stops, now refusals


def blocked_task(work: Path, delivery: Path, write_plan, write_delivery) -> None:
    """The fixture task with a standing blocking note, and its record repinned to it."""
    front = json_front(work, "task/checkout/record-order")
    write_plan("task/checkout/record-order", front,
               body="## What it is\nProse for a reader.\n\n## Notes\n"
                    "BLOCKING, from the specification — the criterion asserts an order with no "
                    "lines, which domain/sales/order refuses.\n")
    record = json_front(delivery, "implementation/checkout/record-order")
    record["task"] = task_pin_of(work, "task/checkout/record-order")
    write_delivery("implementation/checkout/record-order", record)
    repin_proof(delivery, write_delivery)


def test_a_record_over_a_blocked_task_is_refused(delivery, work, root, target, sound_delivery,
                                                 write_plan, write_delivery):
    """Writing source past a blocking note encodes the contradiction as though the business had
    decided it. The record is refused quoting the entry and naming both doors, the way the stale
    pin refusal hands its three ways out."""
    blocked_task(work, delivery, write_plan, write_delivery)
    found = problems_of(delivery, work, target, root)
    said(found, "whose ## Notes carries `BLOCKING, from the specification — the criterion "
                "asserts an order with no lines")
    said(found, "`/plan-work`, re-cutting the scope")
    said(found, "`/analyse`, amending the specification")


def test_a_review_over_fewer_files_than_its_tasks_records_wrote(delivery, work, root, target,
                                                                sound_delivery, write_delivery):
    """`reviewed` cut to one file derived before: every pass was clean over a set nobody
    delivered. The set is the caller's to state, and the validator holds it to the records."""
    write_delivery("review/first", review_front(work, root, reviewed=["src/orders/place.ts"],
                                                unpaired=[]))
    said(problems_of(delivery, work, target, root),
         "review/first: `reviewed` does not list tests/place.spec.ts, which "
         "proof/checkout/record-order says it wrote in `tests`")


def dependent(work: Path, write_delivery) -> None:
    write_delivery("implementation/checkout/bill-order", {
        "title": "Bill", "summary": "Raise the bill.",
        "task": task_pin_of(work, "task/checkout/bill-order"),
        "files": [{"path": "src/bill.ts", "effect": "bills"}],
        "criteria": [{"criterion": "Recording an order twice produces one invoice.",
                      "met": True, "how": "idempotent on order_number"}],
        "nodes": [{"node": "domain/sales/invoice", "how": "the invoice shape"}],
    })


def test_nothing_builds_on_a_dependency_nobody_proved(delivery, work, root, target,
                                                      sound_delivery, write_delivery):
    """An implementation without its proof is source nobody executed under a record saying it
    stands; a dependent written over it builds on a claim."""
    (delivery / "proof/checkout/record-order.md").unlink()
    dependent(work, write_delivery)
    said(problems_of(delivery, work, target, root),
         "builds on task/checkout/record-order, which is implemented and no proof record holds up")
    (delivery / "implementation/checkout/bill-order.md").unlink()
    validator = deliver.contract()
    nodes, _ = deliver.collect(delivery, validator, deliver.pass_names())
    plan_nodes, _ = deliver.load_plan(work, root)
    report = deliver.outstanding_report(nodes, plan_nodes, target)
    assert "task/checkout/bill-order: no record; waits on task/checkout/record-order" in report, \
        report
    assert "nothing that builds on it is deliverable until one does" in report, report


def test_a_substrate_delivered_alone_is_built_on_without_a_proof(delivery, work, root, target,
                                                                 sound_delivery, write_plan,
                                                                 write_delivery):
    """The exemption is `substrate_only`'s: a task that produced the artifacts every rule needs
    and wrote nothing a test can reach has no suite to prove, and holding it to one would hold it
    to the suite the registry held back."""
    write_plan("task/checkout/scaffold", {
        "title": "Scaffold", "summary": "Set the toolchain up.",
        "objective": "The project builds and its suite runs.",
        "criteria": ["The suite runs and reports."],
        "produces": ["package.json"],
        "rationale": "No base node governs the toolchain; the plan decided this cut itself."})
    bill = json_front(work, "task/checkout/bill-order")
    bill["depends_on"] = ["task/checkout/scaffold"]
    write_plan("task/checkout/bill-order", bill)
    (target / "package.json").write_text("{}\n", encoding="utf-8")
    write_delivery("implementation/checkout/scaffold", {
        "title": "Scaffold", "summary": "The toolchain this project builds with.",
        "task": task_pin_of(work, "task/checkout/scaffold"),
        "files": [{"path": "package.json", "effect": "declares the build and the suite"}],
        "criteria": [{"criterion": "The suite runs and reports.", "met": True,
                      "how": "the suite script runs the runner over the test tree"}]})
    dependent(work, write_delivery)
    assert problems_of(delivery, work, target, root) == []


def test_a_red_suite_attempt_the_proof_does_not_name(delivery, work, root, target,
                                                     sound_delivery, write_delivery, run_dir):
    """The diagnosis of a red attempt otherwise lives only in the conversation that made it. A
    reader meeting the run directory beside the proof is owed the sentence that says why."""
    run_dir("failed", "checkout-record-order-suite")
    run_dir("passed", "checkout-record-order-suite-2")
    found = problems_of(delivery, work, target, root)
    said(found, "proof/checkout/record-order: ## Notes names none of "
                "run/checkout-record-order-suite, which ran this task's suite and did not pass")
    assert not any("suite-2" in p for p in found), "the green attempt is owed nothing"
    front = json_front(delivery, "proof/checkout/record-order")
    write_delivery("proof/checkout/record-order", front,
                   body="## What it is\nProse for a reader.\n\n## Notes\n"
                        "run/checkout-record-order-suite failed at test: the fixture order "
                        "carried no order_number.\n")
    assert problems_of(delivery, work, target, root) == []


def test_another_tasks_suite_is_not_this_proofs(delivery, work, root, target, sound_delivery,
                                                run_dir):
    run_dir("failed", "checkout-record-order-again-suite")
    run_dir("failed", "checkout-bill-order-suite")
    assert problems_of(delivery, work, target, root) == []


# ------------------------------------------------ over a closed plan, receipts and not refusals


def test_the_six_findings_are_receipts_over_a_closed_plan(delivery, work, root, target,
                                                          sound_delivery, write_delivery,
                                                          run_dir):
    """A closed plan takes no further record, so a refusal there stops no writer. The finding is
    printed as a receipt and the exit stays what it was; a live plan is refused."""
    import subprocess
    import sys
    run_dir("failed", "checkout-record-order-suite")
    write_delivery("review/first", review_front(work, root, reviewed=["src/orders/place.ts"],
                                                unpaired=[]))
    script = REPO / "src/claude/bin/deliver.py"
    live = subprocess.run([sys.executable, "-B", str(script), str(delivery), str(work),
                           str(target), str(root)], capture_output=True, text=True)
    assert live.returncode == 1
    assert "## Notes names none of run/checkout-record-order-suite" in live.stdout
    assert "`reviewed` does not list tests/place.spec.ts" in live.stdout

    (work / deliver.plan.CLOSURE_FILE).write_text("Closed.\n", encoding="utf-8")
    closed = subprocess.run([sys.executable, "-B", str(script), str(delivery), str(work),
                             str(target)], capture_output=True, text=True)
    assert closed.returncode == 0, closed.stdout + closed.stderr
    assert closed.stdout.count("a receipt, never a refusal: the plan is closed") == 2, \
        closed.stdout
    assert "## Notes names none of run/checkout-record-order-suite" in closed.stdout
    assert "`reviewed` does not list tests/place.spec.ts" in closed.stdout
    checked = subprocess.run([sys.executable, "-B", str(script), "--check", str(delivery),
                              str(work), str(target)], capture_output=True, text=True)
    assert checked.returncode == 0 and "a receipt, never a refusal" in checked.stdout
