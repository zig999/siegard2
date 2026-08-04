"""What the delivery validator refuses, and why each refusal exists.

Every test here is a rule somebody could otherwise satisfy by leaving something out. The
totality checks are the heart of it — a record answers every criterion its task states and every
base node its task binds — because an omission is invisible in the record that omits it and
reads as work that went fine. The rest holds the seams: a record answers a task that exists, a
proof stands beside an implementation, no task the base leaves unresolved is delivered at all,
nothing is delivered before what it builds on, and no pin outlives the plan it read.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import deliver
from conftest import plan_pin_of

REPO = Path(__file__).resolve().parent.parent


def problems_of(delivery: Path, work: Path, root: Path) -> list[str]:
    """Everything the validator would report over this delivery, in one list."""
    validator, allowed = deliver.contract()
    names = deliver.pass_names()
    plan_nodes, plan_problems = deliver.load_plan(work, root)
    assert plan_problems == [], f"the fixture plan does not hold together: {plan_problems}"
    pin = deliver.plan_pin(plan_nodes)
    nodes, found = deliver.collect(delivery, validator, allowed, names)
    return found + deliver.cross_problems(nodes, plan_nodes, pin, names, delivery)


def said(problems: list[str], fragment: str) -> None:
    assert any(fragment in p for p in problems), \
        f"nothing reported {fragment!r}; what was reported was {problems}"


# ------------------------------------------------------------------- the sound case


def test_the_sound_delivery_holds_together(delivery, work, root, sound_delivery):
    assert problems_of(delivery, work, root) == []


def test_it_derives_the_index_it_promises(delivery, work, root, sound_delivery):
    validator, allowed = deliver.contract()
    names = deliver.pass_names()
    nodes, _ = deliver.collect(delivery, validator, allowed, names)
    graph = deliver.derive(nodes, names)
    assert graph["contract_version"] == "siegard-delivery/1"
    assert [n["id"] for n in graph["nodes"]] == ["implementation/checkout/record-order",
                                                 "proof/checkout/record-order"]
    kinds = {(e["from"], e["kind"], e["to"]) for e in graph["edges"]}
    assert ("implementation/checkout/record-order", "implements",
            "task/checkout/record-order") in kinds, "the path is what names the task answered"
    assert ("implementation/checkout/record-order", "encodes",
            "definition/sales/order") in kinds, "a fact in the source traces to the base node"
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


def test_a_path_that_computes_to_no_identifier_is_refused(delivery, work, root, sound_delivery):
    (delivery / "notes.md").write_text("---\ntitle: x\n---\n", encoding="utf-8")
    said(problems_of(delivery, work, root), "the path is the identity and this one computes to none")


def test_run_holds_material_and_is_never_a_node(delivery, work, root, sound_delivery):
    (delivery / "run" / "first").mkdir(parents=True)
    (delivery / "run" / "first" / "notes.md").write_text("not a node\n", encoding="utf-8")
    assert problems_of(delivery, work, root) == [], \
        "run/ holds what the commands printed; validating it as a node would refuse a log"


def test_the_body_carries_exactly_two_headings(delivery, work, root, sound_delivery,
                                               write_delivery):
    path = delivery / "proof/checkout/record-order.md"
    path.write_text(path.read_text(encoding="utf-8").replace("## Notes", "## Findings"),
                    encoding="utf-8")
    said(problems_of(delivery, work, root), "body headings are")


def test_a_status_field_does_not_exist(delivery, work, root, sound_delivery, write_delivery):
    front = {"title": "Proof", "summary": "What proves it.", "status": "done",
             "tests": [{"file": "t.spec.ts", "name": "n", "proves": "p", "fails_when": "f"}]}
    write_delivery("proof/checkout/record-order", front)
    said(problems_of(delivery, work, root),
         "Additional properties are not allowed ('status' was unexpected)")


# ------------------------------------------------------------------ against the plan


def test_a_record_for_a_task_the_plan_does_not_hold(delivery, work, root, sound_delivery,
                                                    write_delivery):
    write_delivery("implementation/checkout/ship-order", {
        "title": "Ship", "summary": "Ship it.", "plan": plan_pin_of(work, root),
        "files": [{"path": "src/ship.ts", "effect": "ships"}],
        "criteria": [{"criterion": "c", "met": True, "how": "h"}],
        "nodes": [{"node": "definition/sales/order", "how": "read only"}],
    })
    said(problems_of(delivery, work, root), "which the plan does not hold as a task")


def test_a_criterion_the_record_leaves_unanswered(delivery, work, root, sound_delivery,
                                                  write_plan):
    task = work / "task/checkout/record-order.md"
    task.write_text(task.read_text(encoding="utf-8").replace(
        "- Submitting a valid order returns its order_number.",
        "- Submitting a valid order returns its order_number.\n"
        "- A non-positive total is refused."), encoding="utf-8")
    said(problems_of(delivery, work, root), "cannot be read as complete")


def test_a_criterion_the_task_does_not_state(delivery, work, root, sound_delivery,
                                            write_delivery):
    front = json_front(delivery, "implementation/checkout/record-order")
    front["criteria"].append({"criterion": "Something nobody wrote.", "met": True, "how": "h"})
    write_delivery("implementation/checkout/record-order", front)
    said(problems_of(delivery, work, root), "which the task does not state")


def test_a_bound_node_the_record_passes_over(delivery, work, root, sound_delivery,
                                             write_delivery):
    front = json_front(delivery, "implementation/checkout/record-order")
    front["nodes"] = []
    write_delivery("implementation/checkout/record-order", front)
    said(problems_of(delivery, work, root), "the base going unanswered in code")


def test_a_node_the_task_never_bound(delivery, work, root, sound_delivery, write_delivery):
    front = json_front(delivery, "implementation/checkout/record-order")
    front["nodes"].append({"node": "definition/sales/invoice", "how": "read only"})
    write_delivery("implementation/checkout/record-order", front)
    said(problems_of(delivery, work, root), "which the task does not bind")


def test_an_unresolved_task_is_not_delivered(delivery, work, root, sound_delivery,
                                             write_delivery):
    """The gate that matters most: the plan's own triage decides whether a task can be written
    at all, and it is decided mechanically rather than by anybody's judgment at delivery time."""
    write_delivery("implementation/checkout/bill-order", {
        "title": "Bill", "summary": "Raise the bill.", "plan": plan_pin_of(work, root),
        "files": [{"path": "src/bill.ts", "effect": "bills"}],
        "criteria": [{"criterion": "Recording an order twice produces one invoice.",
                      "met": True, "how": "idempotent on order_number"}],
        "nodes": [{"node": "definition/sales/invoice", "how": "the invoice shape"}],
    })
    said(problems_of(delivery, work, root),
         "unresolved entry(ies), and this record delivers it anyway")


def test_nothing_is_delivered_before_what_it_builds_on(delivery, work, root, sound_delivery,
                                                       write_delivery, write_plan):
    """bill-order builds on record-order. Remove record-order's record and the dependency is
    what has to be delivered first — with no status field to ask, the records are how that is
    known."""
    (delivery / "implementation/checkout/record-order.md").unlink()
    (delivery / "proof/checkout/record-order.md").unlink()
    task = work / "task/checkout/bill-order.md"
    before = task.read_text(encoding="utf-8")
    after = before.replace(
        "unresolved:\n- gap: definition/sales/invoice#attributes\n",
        "waived:\n- gap: definition/sales/invoice#attributes\n  why: not on this path\n")
    assert after != before, "the fixture's triage was not rewritten; the test would then prove " \
                            "the unresolved gate rather than the dependency one"
    task.write_text(after, encoding="utf-8")
    write_delivery("implementation/checkout/bill-order", {
        "title": "Bill", "summary": "Raise the bill.", "plan": plan_pin_of(work, root),
        "files": [{"path": "src/bill.ts", "effect": "bills"}],
        "criteria": [{"criterion": "Recording an order twice produces one invoice.",
                      "met": True, "how": "idempotent on order_number"}],
        "nodes": [{"node": "definition/sales/invoice", "how": "the invoice shape"}],
    })
    found = problems_of(delivery, work, root)
    said(found, "the dependency is what has to be delivered first")
    assert not any("delivers it anyway" in p for p in found), \
        "the waived triage means the unresolved gate must not fire; only the dependency one does"


def test_a_pin_that_outlived_its_plan(delivery, work, root, sound_delivery, write_plan):
    write_plan("epic/shipping", {"title": "Shipping", "summary": "Later.",
                                 "covers": ["definition/sales/order"]})
    write_plan("task/shipping/ship-order", {
        "title": "Ship order", "summary": "Ship it.",
        "objective": "A recorded order ships once.",
        "criteria": ["A recorded order ships once."],
        "nodes": ["definition/sales/order"],
        "base": _base_pin(work),
    })
    said(problems_of(delivery, work, root), "is not the plan as it stands")


def test_a_proof_without_an_implementation(delivery, work, root, sound_delivery):
    (delivery / "implementation/checkout/record-order.md").unlink()
    said(problems_of(delivery, work, root), "what a proof holds up has to exist first")


# ------------------------------------------------------------------------ the review


def review_front(work: Path, root: Path, **overrides) -> dict:
    front = {
        "title": "Checkout, first review",
        "summary": "What the passes found.",
        "plan": plan_pin_of(work, root),
        "reviewed": ["src/orders/place.ts", "tests/place.spec.ts"],
        "tasks": ["task/checkout/record-order"],
        "passes": [
            {"pass": "coverage"},
            {"pass": "conformance"},
            {"pass": "failures", "missing": "no run was captured"},
        ],
        "coverage": [{"criterion": "Submitting a valid order returns its order_number.",
                      "state": "covered",
                      "tests": [{"file": "tests/place.spec.ts",
                                 "name": "returns the order_number for a valid submission"}]}],
    }
    front.update(overrides)
    return front


def test_a_review_that_answers_for_every_pass_holds(delivery, work, root, sound_delivery,
                                                    write_delivery):
    write_delivery("review/first", review_front(work, root))
    assert problems_of(delivery, work, root) == []


def test_a_pass_left_unanswered_is_refused(delivery, work, root, sound_delivery,
                                           write_delivery):
    front = review_front(work, root)
    front["passes"] = front["passes"][:2]
    write_delivery("review/first", front)
    said(problems_of(delivery, work, root), "passes names no entry for `failures`")


def test_a_finding_cannot_claim_a_pass_that_did_not_run(delivery, work, root, sound_delivery,
                                                        write_delivery):
    front = review_front(work, root)
    front["findings"] = [{"pass": "failures", "where": "src/orders/place.ts:3",
                          "evidence": "expected the stated refusal, got a generic error",
                          "cost": "the refusal is unproven", "cause": "code"}]
    write_delivery("review/first", front)
    said(problems_of(delivery, work, root), "a pass that did not run found nothing")


def test_a_cause_belongs_to_the_failures_pass_and_nowhere_else(delivery, work, root,
                                                               sound_delivery, write_delivery):
    front = review_front(work, root)
    front["findings"] = [{"pass": "conformance", "where": "src/orders/place.ts:3",
                          "evidence": "return refuse('ORDER_TOTAL_INVALID')",
                          "cost": "the code became the home of the refusal code",
                          "cause": "code"}]
    write_delivery("review/first", front)
    said(problems_of(delivery, work, root),
         "states a `cause` outside the failures pass")


def test_a_failure_finding_without_a_cause(delivery, work, root, sound_delivery, write_delivery,
                                           run_dir):
    front = review_front(work, root)
    front["passes"][2] = {"pass": "failures"}
    front["run"] = "run/first"
    front["failures_counted"] = 1
    front["findings"] = [{"pass": "failures", "where": "tests/place.spec.ts:8",
                          "evidence": "expected 409, got 500",
                          "cost": "the refusal answers the wrong way"}]
    write_delivery("review/first", front)
    said(problems_of(delivery, work, root), "states no `cause`")


def test_a_count_that_disagrees_with_the_findings(delivery, work, root, sound_delivery,
                                                  write_delivery, run_dir):
    front = review_front(work, root)
    front["passes"][2] = {"pass": "failures"}
    front["run"] = "run/first"
    front["failures_counted"] = 3
    front["findings"] = [{"pass": "failures", "where": "tests/place.spec.ts:8",
                          "evidence": "expected 409, got 500", "cause": "code",
                          "cost": "the refusal answers the wrong way"}]
    write_delivery("review/first", front)
    said(problems_of(delivery, work, root),
         "how a failure goes unexamined while the record still looks complete")


def test_a_pass_that_ran_and_recorded_nothing_of_what_it_read(delivery, work, root,
                                                              sound_delivery, write_delivery):
    front = review_front(work, root)
    del front["coverage"]
    write_delivery("review/first", front)
    said(problems_of(delivery, work, root), "the coverage pass ran and `coverage` is absent")


def test_a_criterion_the_coverage_pass_left_out(delivery, work, root, sound_delivery,
                                                write_delivery):
    front = review_front(work, root)
    front["coverage"] = [{"criterion": "Something nobody wrote.", "state": "covered"}]
    write_delivery("review/first", front)
    said(problems_of(delivery, work, root), "an omitted criterion reads as one that passed")


def test_a_review_of_a_task_nothing_delivered(delivery, work, root, sound_delivery,
                                              write_delivery):
    front = review_front(work, root)
    front["tasks"] = ["task/checkout/bill-order"]
    front["coverage"] = [{"criterion": "Recording an order twice produces one invoice.",
                          "state": "uncovered", "why": "nothing exercises it"}]
    write_delivery("review/first", front)
    said(problems_of(delivery, work, root), "a review of a task nothing delivered has no subject")


def test_a_run_the_delivery_root_does_not_hold(delivery, work, root, sound_delivery,
                                               write_delivery):
    front = review_front(work, root)
    front["passes"][2] = {"pass": "failures"}
    front["run"] = "run/nowhere"
    front["failures_counted"] = 0
    write_delivery("review/first", front)
    said(problems_of(delivery, work, root), "which the delivery root does not hold")


# ----------------------------------------------------------------- what remains open


def test_the_outstanding_report_derives_what_no_field_records(delivery, work, root,
                                                              sound_delivery):
    validator, allowed = deliver.contract()
    names = deliver.pass_names()
    nodes, _ = deliver.collect(delivery, validator, allowed, names)
    plan_nodes, _ = deliver.load_plan(work, root)
    report = deliver.outstanding_report(nodes, plan_nodes)
    assert "task/checkout/bill-order: no record" in report
    assert "1 unresolved entry(ies)" in report, \
        "what a task waits on is a fact of the plan, read here rather than tracked"
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


def test_a_closed_plan_is_delivered_against_without_the_base(delivery, work, root,
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
    assert deliver.cross_problems(found, nodes, deliver.plan_pin(nodes), names, delivery) == []


def test_the_cli_derives_checks_and_reports(delivery, work, root, sound_delivery):
    import subprocess
    import sys
    script = REPO / "src/claude/bin/deliver.py"

    def invoke(*args):
        return subprocess.run([sys.executable, "-B", str(script), *args, str(delivery),
                               str(work), str(root)], capture_output=True, text=True)

    stale = invoke("--check")
    assert stale.returncode == 1 and "STALE" in stale.stdout, \
        "an index that has never been derived is stale, not sound"

    derived = invoke()
    assert derived.returncode == 0, derived.stderr
    assert "contract siegard-delivery/1" in derived.stdout
    assert (delivery / "delivery.json").is_file()

    assert invoke("--check").returncode == 0, "what was just derived must read as current"

    by_hand = json.loads((delivery / "delivery.json").read_text(encoding="utf-8"))
    assert by_hand["contract_version"] == "siegard-delivery/1"

    outstanding = invoke("--outstanding")
    assert outstanding.returncode == 0, outstanding.stderr
    assert "task/checkout/bill-order" in outstanding.stdout


def test_the_cli_refuses_a_plan_that_does_not_hold(delivery, work, root, sound_delivery):
    import subprocess
    import sys
    (work / "epic/checkout.md").unlink()
    done = subprocess.run([sys.executable, "-B", str(REPO / "src/claude/bin/deliver.py"),
                           str(delivery), str(work), str(root)], capture_output=True, text=True)
    assert done.returncode == 2, done.stdout
    assert "fix it with plan.py before" in done.stderr


def test_the_cli_needs_the_base_while_the_plan_is_live(delivery, work, root, sound_delivery):
    import subprocess
    import sys
    done = subprocess.run([sys.executable, "-B", str(REPO / "src/claude/bin/deliver.py"),
                           str(delivery), str(work)], capture_output=True, text=True)
    assert done.returncode == 2
    assert "name the knowledge root" in done.stderr


def test_a_captured_run_reaches_a_review(delivery, work, root, sound_delivery, write_delivery):
    """The whole chain the review skill describes: the runner writes evidence to disk, the review
    points at it by directory, and the validator holds the two together."""
    import subprocess
    import sys
    captured = subprocess.run(
        [sys.executable, "-B", str(REPO / "src/claude/bin/run.py"), str(delivery),
         "--run", "first", "--timeout-seconds", "20",
         "--step", "suite=python3 -c 'raise SystemExit(1)'"],
        capture_output=True, text=True)
    assert captured.returncode == 1, captured.stderr
    record = json.loads((delivery / "run/first/run.json").read_text(encoding="utf-8"))
    assert record["run"] == "run/first" and record["outcome"] == "failed"

    front = review_front(work, root)
    front["passes"][2] = {"pass": "failures"}
    front["run"] = record["run"]
    front["failures_counted"] = 1
    front["findings"] = [{"pass": "failures", "where": "tests/place.spec.ts:8",
                          "evidence": "expected the stated refusal, got a generic error",
                          "cause": "code", "cost": "the refusal answers the wrong way",
                          "correction": "answer with the refusal the bound rule names"}]
    write_delivery("review/first", front)
    assert problems_of(delivery, work, root) == []


# ------------------------------------------------------------------------- fixtures


@pytest.fixture
def run_dir(delivery: Path) -> Path:
    where = delivery / "run" / "first"
    where.mkdir(parents=True)
    return where


def json_front(delivery: Path, did: str) -> dict:
    """One node's frontmatter, read back so a test can change exactly one field of it."""
    import re

    import yaml
    text = (delivery / f"{did}.md").read_text(encoding="utf-8")
    return yaml.safe_load(re.match(r"^---\n(.*?)\n---\n", text, re.S).group(1))


def _base_pin(work: Path) -> str:
    """The base pin the plan's existing tasks already carry, reused for a task added mid-test."""
    return json_front(work, "task/checkout/record-order")["base"]
