"""What the base pin must catch, and about which task — the scenarios option C has to satisfy.

**The defect these tests describe.** A task's `base` pin is the SHA-256 of the whole derived
`graph.json` text, and that index carries per node only `id, kind, file, context, title, summary`
plus `aggregate`, `ddd` and the names of its open gap fields. It does not carry the node's content.
Measured on this tree:

    rewrote definition/sales/order's attributes (max_length 20 → 8, one field added)
      → the pin did not move, and a task binding that node validated clean
    changed the same node's title, and nothing else
      → the pin moved, and BOTH tasks of the plan went stale, including the one
        that binds a different node

So the granularity is inverted twice over: silent on a change to what a bound node says, and loud on
a change that reaches no task at all. `src/claude/CLAUDE.md` claims "each hop pinned by content, so a
root that moved after the hop was made is visible rather than assumed", which is not true of the
first case.

**Option C, which these tests specify.** The derived index carries a `digest` per node — the SHA-256
of that node's file — and a task's binding carries, per bound node, the digest it read:

    nodes:
      - node: definition/sales/order
        digest: sha256:<the digest the index listed>

The aggregate `base` field goes away. A task is stale when a node **it binds** has moved, the
refusal names that node, and a reader recomputes any digest by hand with
`sha256sum <knowledge-root>/<node-id>.md`.

**How this module behaves before and after.** Every test that requires C is marked
`xfail(strict=True)`. Before C they fail and the suite stays green; the day C lands they pass, strict
xfail turns an unexpected pass into a failure, and the markers have to come off in the same change
that earns it. Nothing here can be left behind quietly.

The tests that carry no marker are the opposite: they pass today and must still pass after C. They
are the properties C must not cost — a bound node that was removed is still refused, a task that
binds nothing still validates, a closed plan still validates without the base, and the derivation
stays byte-stable.

**Why these drive the CLI rather than the library.** C changes `base_pin`, the signature of
`cross_problems` and the shape `references` reads. A test importing those would have to be rewritten
by the same change it exists to hold, which is how a guard ends up adjusted until it passes. What C
does not change is how a consumer runs the validators, so that is the surface used here.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
GRAPH = REPO / "src/claude/bin/graph.py"
PLAN = REPO / "src/claude/bin/plan.py"

NEEDS_C = pytest.mark.xfail(strict=True, reason="option C is not implemented: the index carries no "
                                               "per-node digest and the pin is one value over the "
                                               "whole base")

BASE_BODY = "## What it is\nProse for a reader.\n\n## Rules\nNone.\n"
PLAN_BODY = "## What it is\nProse for a reader.\n\n## Notes\nNone.\n"


# ----------------------------------------------------------------- running the shipped scripts


def run(script: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(script), *args],
                          capture_output=True, text=True, cwd=REPO)


def refusals(work: Path, root: Path) -> str:
    """What the plan validator says about this plan, as a consumer sees it."""
    done = run(PLAN, str(work), str(root))
    return done.stdout + done.stderr


def stale_tasks(work: Path, root: Path) -> set[str]:
    """Every task the validator reports as reading a base that has since moved. Read off the
    refusals rather than computed, because which tasks go stale is exactly what is under test."""
    found = set()
    for line in refusals(work, root).splitlines():
        identifier, _, rest = line.partition(":")
        if identifier.startswith("task/") and ("pin" in rest and "moved" in rest
                                               or "as it stands" in rest):
            found.add(identifier)
    return found


def digest_of(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


# ----------------------------------------------------------------------------- the fixture tree


def put(root: Path, relative: str, front: str, body: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{front}---\n{body}", encoding="utf-8")
    return path


@pytest.fixture
def base(tmp_path: Path) -> Path:
    """A sound base with two bindable definitions, so a change can reach one task and not the
    other. Without two, every scenario below would be indistinguishable from a plan-wide stale."""
    root = tmp_path / "knowledge"
    put(root, "context/sales.md",
        "title: Sales\nsummary: Ordering.\nstrategic: core\n", BASE_BODY)
    put(root, "aggregate/sales/orders.md",
        "title: Orders\nsummary: An order and its lines together.\n", BASE_BODY)
    put(root, "definition/sales/order.md",
        "title: Order\nsummary: A customer's order.\nddd: aggregate-root\naggregate: orders\n"
        "identity:\n  - order_number\nattributes:\n"
        "  - {name: order_number, type: string, max_length: 20}\n", BASE_BODY)
    put(root, "definition/sales/coupon.md",
        "title: Coupon\nsummary: A discount code.\nddd: value-object\nattributes:\n"
        "  - {name: code, type: string, max_length: 10}\n", BASE_BODY)
    assert run(GRAPH, str(root)).returncode == 0, "the fixture base does not hold together"
    return root


TASKS = {"task/checkout/record-order": "definition/sales/order",
         "task/checkout/apply-coupon": "definition/sales/coupon"}


def scaffold(work: Path) -> None:
    put(work, "inventory/order-service.md",
        "title: Order service\nsummary: One service.\narea:\n  - src/\n", PLAN_BODY)
    put(work, "epic/checkout.md",
        "title: Checkout\nsummary: Everything placement needs.\ncovers:\n"
        + "".join(f"  - {node}\n" for node in sorted(TASKS.values())), PLAN_BODY)


def task_front(title: str, extra: str) -> str:
    return (f"title: {title}\nsummary: {title}.\n"
            f"objective: {title} completes and is observable afterwards.\n"
            f"criteria:\n  - The outcome is observable afterwards.\n{extra}")


@pytest.fixture
def target_plan(base: Path, tmp_path: Path) -> Path:
    """The plan as option C shapes it: each bound node carried with the digest that was read."""
    work = tmp_path / "work"
    scaffold(work)
    for tid, node in TASKS.items():
        digest = digest_of(base / f"{node}.md")
        put(work, f"{tid}.md", task_front(tid.split("/")[-1],
            f"nodes:\n  - node: {node}\n    digest: {digest}\n"), PLAN_BODY)
    return work


@pytest.fixture
def current_plan(base: Path, tmp_path: Path) -> Path:
    """The plan as it is shaped today: bare identifiers, and one aggregate pin on every task,
    computed the way the contract says a reader computes it by hand."""
    work = tmp_path / "work"
    scaffold(work)
    pin = digest_of(base / "graph.json")
    for tid, node in TASKS.items():
        put(work, f"{tid}.md", task_front(tid.split("/")[-1],
            f"nodes:\n  - {node}\nbase: {pin}\n"), PLAN_BODY)
    return work


# ------------------------------------------------------------------------------------ the canary


def test_the_fixture_builds_a_sound_plan_today(base, current_plan):
    """The canary. Every expected failure below is only evidence about C if the tree the tests
    build is otherwise sound — an `xfail` over a malformed fixture reads exactly like an `xfail`
    over a missing feature, and reports success either way."""
    done = run(PLAN, str(current_plan), str(base))
    assert done.returncode == 0, done.stdout + done.stderr
    assert (current_plan / "plan.json").is_file()


# -------------------------------------------------------------------- what the index must carry


@NEEDS_C
def test_the_index_carries_a_digest_for_every_node(base):
    index = json.loads((base / "graph.json").read_text(encoding="utf-8"))
    missing = [entry["id"] for entry in index["nodes"] if "digest" not in entry]
    assert missing == [], f"the index lists no digest for {missing}"


@NEEDS_C
def test_each_digest_is_the_sha256_of_that_node_file(base):
    """Recomputable by hand, which is the whole reason a pin is a hash: a value only the tool can
    verify is a claim, and the point of a pin is to be a verification."""
    index = json.loads((base / "graph.json").read_text(encoding="utf-8"))
    for entry in index["nodes"]:
        assert entry.get("digest") == digest_of(base / entry["file"]), \
            f"{entry['id']}: the index digest is not `sha256sum {entry['file']}`"


# ------------------------------------------------------------------------- the granularity table


@NEEDS_C
def test_a_change_to_what_a_bound_node_says_stales_the_task_that_binds_it(base, target_plan):
    """The defect, stated as the requirement. `max_length` 20 → 8 narrows what the domain admits;
    a task bound to that node was written against the wider field and nobody is told."""
    node = base / "definition/sales/order.md"
    node.write_text(node.read_text(encoding="utf-8").replace("max_length: 20", "max_length: 8"),
                    encoding="utf-8")
    assert run(GRAPH, str(base)).returncode == 0
    assert stale_tasks(target_plan, base) == {"task/checkout/record-order"}


@NEEDS_C
def test_a_change_to_a_bound_node_leaves_the_other_task_alone(base, target_plan):
    """The other half of the same event, and the half today gets wrong in the opposite direction:
    `apply-coupon` binds a node nothing touched, so it has nothing to re-read."""
    node = base / "definition/sales/order.md"
    node.write_text(node.read_text(encoding="utf-8").replace("title: Order", "title: Sales order"),
                    encoding="utf-8")
    assert run(GRAPH, str(base)).returncode == 0
    stale = stale_tasks(target_plan, base)
    assert "task/checkout/record-order" in stale, "the task binding the moved node is not stale"
    assert "task/checkout/apply-coupon" not in stale, \
        "a task binding a node nothing touched was staled by another task's node moving"


@NEEDS_C
def test_a_new_unrelated_node_stales_nothing(base, target_plan):
    """A base that grew says nothing about a binding that already holds. Today this stales every
    task in the plan, which is the noise that makes a real stale easy to wave through.

    Asserted as a clean exit rather than an empty stale set: an invalid plan reports no stale task
    either, so `stale_tasks(...) == set()` passes while nothing under test has been exercised. The
    first draft of this test did exactly that, and strict xfail is what reported it."""
    put(base, "definition/sales/invoice.md",
        "title: Invoice\nsummary: The bill.\nddd: value-object\nattributes:\n"
        "  - {name: number, type: string, max_length: 20}\n", BASE_BODY)
    assert run(GRAPH, str(base)).returncode == 0
    done = run(PLAN, str(target_plan), str(base))
    assert done.returncode == 0, done.stdout + done.stderr


@NEEDS_C
def test_the_refusal_names_the_node_that_moved(base, target_plan):
    """Diagnosability is criterion 1 in this repository's decision order, and two opaque hashes are
    not a diagnosis. The aggregate pin cannot name the node because the old per-node digests are
    not kept anywhere; carrying them per bound node is what makes the message possible.

    The staleness is established before the wording is read, so a refusal about anything else —
    a shape the schema rejects, say — cannot satisfy this by mentioning the node in passing."""
    node = base / "definition/sales/order.md"
    node.write_text(node.read_text(encoding="utf-8").replace("max_length: 20", "max_length: 8"),
                    encoding="utf-8")
    assert run(GRAPH, str(base)).returncode == 0
    assert stale_tasks(target_plan, base) == {"task/checkout/record-order"}
    said = [line for line in refusals(target_plan, base).splitlines()
            if line.startswith("task/checkout/record-order:")]
    assert said, "no refusal is attributed to the task whose bound node moved"
    assert any("definition/sales/order" in line for line in said), \
        f"the refusal does not name the node that moved: {said}"
    assert not any("definition/sales/coupon" in line for line in said), \
        "the refusal names a node that did not move, which is a diagnosis a reader has to undo"


# ------------------------------------------- the check C could disable without saying anything


@NEEDS_C
def test_a_record_still_cannot_pass_over_a_bound_node(base, target_plan, tmp_path):
    """The riskiest line in implementing C, held from the outside.

    `deliver.py` reads a task's binding as `[n for n in listed(tfront, "nodes") if isinstance(n,
    str)]`. Turn those items into objects and leave that line alone and the list comes back empty:
    the loop that refuses a record for passing over a bound node then has nothing to iterate. And
    `nodes` is not required on an implementation record, so a record answering nothing at all —
    exactly what the totality exists to refuse — would validate in silence. `plan.py` degrades the
    same way in two more places, but loudly: its coverage check reports a covered node nothing
    binds, which is wrong but at least visible.

    So this is the scenario a partial implementation passes and this test does not."""
    record = tmp_path / "delivery"
    task_file = target_plan / "task/checkout/record-order.md"
    put(record, "implementation/checkout/record-order.md",
        "title: Record a placed order\n"
        "summary: The entry point that persists a valid order.\n"
        f"task: {digest_of(task_file)}\n"
        "files:\n  - path: src/orders/place.ts\n"
        "    effect: persists a submitted order and answers with its order_number\n"
        "criteria:\n  - criterion: The outcome is observable afterwards.\n"
        "    met: true\n    how: place() answers with the persisted order_number\n",
        PLAN_BODY)
    done = run(REPO / "src/claude/bin/deliver.py",
               str(record), str(target_plan), str(base))
    said = done.stdout + done.stderr
    # The refusal itself is the subject, not the exit code: a plan the validator cannot read at all
    # also exits non-zero, and that would satisfy a status check while proving nothing.
    assert "the base going unanswered in code" in said, \
        f"a record answering no bound node was not refused for it: {said}"
    assert "definition/sales/order" in said, f"the refusal does not name the bound node: {said}"


# ------------------------------------------------------------- what C must not cost (no marker)


def test_a_bound_node_that_was_removed_is_still_refused(base, current_plan):
    """The pin is not what catches a deleted node, and must not become what catches it: a binding
    that resolves to nothing is refused on its own, before any digest is compared."""
    (base / "definition/sales/coupon.md").unlink()
    assert run(GRAPH, str(base)).returncode == 0
    said = refusals(current_plan, base)
    assert "definition/sales/coupon" in said and "does not hold" in said, said


@NEEDS_C
def test_a_task_that_binds_nothing_carries_no_digest_and_still_validates(base, tmp_path):
    """A task may be ungoverned by the base if it says why. Under C it carries no digest at all —
    there is nothing it read — and that must read as a valid task rather than as a missing pin.

    This one needs C because today `base` is required on every task, ungoverned ones included, so
    the file below is refused for the field C removes. That today's shape validates with its
    aggregate pin is held by `test_plan.py::test_a_task_binding_nothing_needs_a_rationale`."""
    work = tmp_path / "work"
    put(work, "inventory/order-service.md",
        "title: Order service\nsummary: One service.\narea:\n  - src/\n", PLAN_BODY)
    put(work, "epic/checkout.md", "title: Checkout\nsummary: Placement.\n"
        "covers:\n  - definition/sales/order\n  - definition/sales/coupon\n"
        "uncovered:\n"
        "  - node: definition/sales/order\n    why: Out of this increment.\n"
        "  - node: definition/sales/coupon\n    why: Out of this increment.\n", PLAN_BODY)
    put(work, "task/checkout/scaffold.md", task_front(
        "Scaffold", "rationale: Scaffolding, bound to no base node on purpose.\n"), PLAN_BODY)
    done = run(PLAN, str(work), str(base))
    assert done.returncode == 0, done.stdout + done.stderr


def test_a_closed_plan_still_validates_without_the_base(base, current_plan):
    """Closed, a plan is history and every pin stands as the anchor naming what its binding read.
    C changes what a pin is; it must not change that a closed plan validates with no base at all,
    and with no complaint about pins it can no longer compare."""
    (current_plan / "closure.md").write_text(
        "The initiative is over.\nRead from intake/ask.md.\n", encoding="utf-8")
    done = run(PLAN, str(current_plan))
    assert done.returncode == 0, done.stdout + done.stderr


def test_the_index_derivation_stays_byte_stable(base):
    """Two derivations of one base produce one text, which is what makes any pin over it
    recomputable at all. A digest keyed on anything but the file's bytes would break this."""
    first = (base / "graph.json").read_bytes()
    assert run(GRAPH, str(base)).returncode == 0
    assert (base / "graph.json").read_bytes() == first


def test_the_index_check_reports_a_stale_index(base):
    """`--check` is how a consumer learns the index is behind the nodes. Adding a field to the
    index must keep that working, because a digest read out of a stale index would pin a version
    of a node that is not the one on disk — the exact failure a pin exists to prevent."""
    put(base, "definition/sales/invoice.md",
        "title: Invoice\nsummary: The bill.\nddd: value-object\nattributes:\n"
        "  - {name: number, type: string, max_length: 20}\n", BASE_BODY)
    done = run(GRAPH, "--check", str(base))
    assert done.returncode == 1
    assert "STALE" in done.stdout + done.stderr
