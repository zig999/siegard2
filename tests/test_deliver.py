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
from pathlib import Path

import pytest

import deliver
from conftest import task_pin_of

REPO = Path(__file__).resolve().parent.parent


def problems_of(delivery: Path, work: Path, target: Path, root: Path) -> list[str]:
    """Everything the validator would report over this delivery, in one list."""
    validator, allowed = deliver.contract()
    names = deliver.pass_names()
    plan_nodes, plan_problems = deliver.load_plan(work, root)
    assert plan_problems == [], f"the fixture plan does not hold together: {plan_problems}"
    nodes, found = deliver.collect(delivery, validator, allowed, names)
    return found + deliver.cross_problems(nodes, plan_nodes, work, names, delivery, target)


def said(problems: list[str], fragment: str) -> None:
    assert any(fragment in p for p in problems), \
        f"nothing reported {fragment!r}; what was reported was {problems}"


# ------------------------------------------------------------------- the sound case


def test_the_sound_delivery_holds_together(delivery, work, root, target, sound_delivery):
    assert problems_of(delivery, work, target, root) == []


def test_it_derives_the_index_it_promises(delivery, work, root, sound_delivery):
    validator, allowed = deliver.contract()
    names = deliver.pass_names()
    nodes, _ = deliver.collect(delivery, validator, allowed, names)
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
    validator, allowed = deliver.contract()
    names = deliver.pass_names()
    nodes, _ = deliver.collect(delivery, validator, allowed, names)
    once = json.dumps(deliver.derive(nodes, names), indent=2, ensure_ascii=False)
    twice = json.dumps(deliver.derive(nodes, names), indent=2, ensure_ascii=False)
    assert once == twice, "identical input must be byte-identical output, or --check is noise"


def test_the_index_satisfies_its_own_contract(repo, delivery, work, root, sound_delivery):
    from jsonschema import Draft202012Validator
    validator, allowed = deliver.contract()
    names = deliver.pass_names()
    nodes, _ = deliver.collect(delivery, validator, allowed, names)
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




# ------------------------------------------------------- the project's own standard


def standard_review(work: Path, root: Path, ref: dict, **overrides) -> dict:
    front = review_front(work, root)
    set_pass(front, "standard")
    front["standard"] = ref
    front.update(overrides)
    return front


def test_a_review_against_a_standard_holds(delivery, work, root, target, sound_delivery,
                                           write_delivery, write_standard):
    front = standard_review(work, root, write_standard())
    front["findings"] = [{"pass": "standard", "file": "src/orders/place.ts",
                          "where": "line 12, the constructor", "cites": "ARC-01",
                          "evidence": "constructor(private readonly store: PostgresStore)",
                          "cost": "the entry point cannot be exercised without a live store"}]
    write_delivery("review/first", front)
    assert problems_of(delivery, work, target, root) == []


def test_a_clean_standard_pass_says_what_it_was_clean_over(delivery, work, root, target,
                                                           sound_delivery, write_delivery,
                                                           write_standard):
    """No findings at all is a real result: the copy and its pin are what the set of rules in
    scope derives from, so the record needs no list of them to be answerable."""
    write_delivery("review/first", standard_review(work, root, write_standard()))
    assert problems_of(delivery, work, target, root) == []


def test_the_standard_must_be_there_to_be_checked(delivery, work, root, target, sound_delivery,
                                                  write_delivery, write_standard):
    ref = write_standard()
    (target / ref["at"]).unlink()
    write_delivery("review/first", standard_review(work, root, ref))
    said(problems_of(delivery, work, target, root), "does not exist")


def test_a_standard_that_does_not_hold_together(delivery, work, root, target, sound_delivery,
                                                write_delivery, write_standard):
    from conftest import STANDARD
    broken = {**STANDARD, "rules": [{**STANDARD["rules"][0], "decided_by": "tool"}]}
    write_delivery("review/first", standard_review(work, root, write_standard(broken)))
    said(problems_of(delivery, work, target, root), "'tool' is a required property")


def test_a_review_pin_is_never_reverified_against_the_live_standard(
        delivery, work, root, target, sound_delivery, write_delivery, write_standard):
    """Same discipline as an implementation's: the pin is a citation of what this review read
    when it was written, never mechanically reverified against the file as it stands today."""
    ref = write_standard()
    path = target / ref["at"]
    path.write_text(path.read_text(encoding="utf-8") + "\n# edited after the review\n",
                    encoding="utf-8")
    write_delivery("review/first", standard_review(work, root, ref))
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
    validator, allowed = deliver.contract()
    names = deliver.pass_names()
    nodes, _ = deliver.collect(delivery, validator, allowed, names)
    graph = deliver.derive(nodes, names)
    entry = next(n for n in graph["nodes"] if n["kind"] == "review")
    assert entry["ran"] == ["coverage", "conformance", "standard"], \
        "the index names the passes that ran, in the order the contract declares them"
    from jsonschema import Draft202012Validator
    schema = json.loads((REPO / "src/claude/schemas/delivery.json").read_text(encoding="utf-8"))
    assert [e.message for e in Draft202012Validator(schema).iter_errors(graph)] == []


# ----------------------------------------------------------------- what remains open


def test_the_outstanding_report_derives_what_no_field_records(delivery, work, root,
                                                              sound_delivery):
    validator, allowed = deliver.contract()
    names = deliver.pass_names()
    nodes, _ = deliver.collect(delivery, validator, allowed, names)
    plan_nodes, _ = deliver.load_plan(work, root)
    report = deliver.outstanding_report(nodes, plan_nodes)
    assert "task/checkout/bill-order: no record" in report
    assert "task/checkout/record-order" not in report, \
        "a task with a record and a proof is not outstanding"


def test_an_implementation_without_its_proof_is_reported(delivery, work, root, sound_delivery):
    (delivery / "proof/checkout/record-order.md").unlink()
    validator, allowed = deliver.contract()
    names = deliver.pass_names()
    nodes, _ = deliver.collect(delivery, validator, allowed, names)
    plan_nodes, _ = deliver.load_plan(work, root)
    assert "no proof record holds it up" in deliver.outstanding_report(nodes, plan_nodes)


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
    validator, allowed = deliver.contract()
    names = deliver.pass_names()
    found, _ = deliver.collect(delivery, validator, allowed, names)
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
def run_dir(delivery: Path):
    """A captured run, as the runner writes one. The validator opens it, so a bare directory is
    not a run."""
    def put(outcome: str = "failed", slug: str = "first",
            steps: tuple[str, ...] = ("install", "lint", "test")) -> Path:
        # The step names are the registry's, because that is the join the whole split hangs on: a
        # rule names the step that decides it, the runner records the outcome under that name, and
        # a record is held to having covered it. A fixture inventing a name of its own would be a
        # run nothing could be checked against, which is what it was until this took the registry's.
        recorded, stopped = [], False
        for name in steps:
            if stopped:
                said = "not_run"
            elif name == steps[-1]:
                said = outcome
            else:
                said = "passed"
            recorded.append({"name": name, "command": f"run-{name}", "outcome": said,
                             "exit_code": 0 if said == "passed" else 1,
                             "output": None if said == "not_run" else f"{name}.log"})
            stopped = stopped or said not in ("passed",)
        where = delivery / "run" / slug
        where.mkdir(parents=True, exist_ok=True)
        (where / "run.json").write_text(json.dumps({
            "contract_version": "siegard-run/1", "run": f"run/{slug}", "cwd": "/tmp/project",
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
    produces(work, delivery, write_plan, write_delivery, ["src/orders/place.ts"])
    assert problems_of(delivery, work, target, root) == []


def test_the_outstanding_report_names_the_standard_this_root_remembers(delivery, work, root,
                                                                       sound_delivery,
                                                                       write_delivery,
                                                                       write_standard):
    """A delivery written against no rules and one written against rules nobody handed over
    produce the same clean output, and only the root can tell them apart."""
    write_delivery("implementation/checkout/record-order",
                   disclosed(delivery, work, write_standard()))
    repin_proof(delivery, write_delivery)
    validator, allowed = deliver.contract()
    nodes, _ = deliver.collect(delivery, validator, allowed, deliver.pass_names())
    plan_nodes, _ = deliver.load_plan(work, root)
    report = deliver.outstanding_report(nodes, plan_nodes)
    assert "standard.yaml: pinned by 1 record(s)" in report
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
