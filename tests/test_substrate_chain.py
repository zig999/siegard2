"""The substrate chain, end to end, in the order a consumer walks it.

Every link here is unit-tested beside its own script. This module exists because the links were
what went wrong: the first cut of this design refused to write source over an absent artifact
*unless the task produced it*, which reads correctly and deadlocks — a plan splitting the manifest
and the compiler configuration across two tasks stops both, each on the other's artifact, with
nothing able to write either. The exemption is the task declaring `produces` at all, and only a
test that walks the whole chain in order can tell the two rules apart.

The commands are invoked as the skills invoke them, because which command runs is the whole of
what `/implement-task` decides here: `--against` for a task that produces nothing, without it for
the task building the substrate. That choice is one field read as a yes or a no, and these are the
two answers.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

import deliver
from conftest import STANDARD, task_pin_of

REPO = Path(__file__).resolve().parent.parent
PLAN_PY = REPO / "src/claude/bin/plan.py"
DELIVER_PY = REPO / "src/claude/bin/deliver.py"


def invoke(script: Path, *args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(script), *map(str, args)],
                          capture_output=True, text=True)


@pytest.fixture
def tree(tmp_path: Path) -> Path:
    """The target source root, greenfield: it exists and holds nothing, which is an answer."""
    where = tmp_path / "tree"
    where.mkdir()
    return where


@pytest.fixture
def registry(tmp_path: Path) -> Path:
    """A registry that presupposes a manifest, like every registry for a stack that has to be set
    up before one rule of it applies."""
    path = tmp_path / "registry.yaml"
    path.write_text(yaml.safe_dump({**STANDARD, "presupposes": [{
        "path": "package.json",
        "provides": "the `lint` step PRH-01 is decided by, and the logger it requires.",
        "rules": ["PRH-01"]}]}, sort_keys=False), encoding="utf-8")
    return path


def front_of(root: Path, nid: str) -> dict:
    text = (root / f"{nid}.md").read_text(encoding="utf-8")
    return yaml.safe_load(re.match(r"^---\n(.*?)\n---\n", text, re.S).group(1))


def test_the_chain_holds_from_an_absent_manifest_to_a_delivered_one(
        tmp_path, tree, registry, work, root, delivery, sound_plan, write_plan, sound_delivery,
        write_delivery):

    # 1. The plan as cut answers the scope and nothing else, and the tree holds no manifest. The
    #    plan is refused: every task in it would stop, on a condition only the plan can end.
    unplanned = invoke(PLAN_PY, "--standard", registry, "--against", tree, work, root)
    assert unplanned.returncode == 1, unplanned.stdout + unplanned.stderr
    assert "no task produces" in unplanned.stdout
    assert "PRH-01 cannot be applied" in unplanned.stdout

    # 2. A task declaring the artifact answers for it, and the plan derives.
    task = front_of(work, "task/checkout/record-order")
    write_plan("task/checkout/record-order", {**task, "produces": ["package.json"]})
    planned = invoke(PLAN_PY, "--standard", registry, "--against", tree, work, root)
    assert planned.returncode == 0, planned.stdout + planned.stderr
    assert (work / "plan.json").is_file()

    # 3. Delivering a task that produces nothing: the skill runs the check with --against, and it
    #    refuses before a single file is written.
    blocked = invoke(DELIVER_PY, "--standard", registry, "--against", tree)
    assert blocked.returncode == 1, blocked.stdout
    assert "package.json: ABSENT" in blocked.stdout
    assert "declares it in `produces`" in blocked.stdout

    # 4. Delivering the task that produces it: the skill drops --against, and the same registry
    #    over the same absent tree is a clean pass. Without this the artifact could never be
    #    written by anything, and a split across two tasks would stop both.
    exempt = invoke(DELIVER_PY, "--standard", registry)
    assert exempt.returncode == 0, exempt.stdout + exempt.stderr

    # 5. The claim is held to what was written: a record for that task that does not list the
    #    artifact is refused, so a substrate task cannot be delivered having built nothing.
    record = front_of(delivery, "implementation/checkout/record-order")
    record["task"] = task_pin_of(work, "task/checkout/record-order")
    write_delivery("implementation/checkout/record-order", record)
    proof = front_of(delivery, "proof/checkout/record-order")
    proof["implementation"] = deliver.pin_of(
        delivery / "implementation/checkout/record-order.md")
    write_delivery("proof/checkout/record-order", proof)
    validator, allowed = deliver.contract()
    names = deliver.pass_names()
    nodes, found = deliver.collect(delivery, validator, allowed, names)
    plan_nodes, _ = deliver.load_plan(work, root)
    empty_handed = deliver.cross_problems(nodes, plan_nodes, work, names, delivery, tree)
    assert any("the task says it produces package.json" in p for p in empty_handed), empty_handed

    # 6. The record that lists it holds.
    record["files"] = record["files"] + [
        {"path": "package.json", "effect": "declares the lint step and the logger dependency"}]
    write_delivery("implementation/checkout/record-order", record)
    proof["implementation"] = deliver.pin_of(
        delivery / "implementation/checkout/record-order.md")
    write_delivery("proof/checkout/record-order", proof)
    nodes, found = deliver.collect(delivery, validator, allowed, names)
    assert found + deliver.cross_problems(nodes, plan_nodes, work, names, delivery, tree) == []

    # 7. And once the artifact stands, the gate opens for every task, including the ones that
    #    produce nothing. Nothing had to be told it was over: the tree is the state.
    (tree / "package.json").write_text(json.dumps({"name": "x"}), encoding="utf-8")
    opened = invoke(DELIVER_PY, "--standard", registry, "--against", tree)
    assert opened.returncode == 0, opened.stdout
    assert "stands, and PRH-01 can be applied" in opened.stdout


def test_a_split_substrate_stops_neither_half(tmp_path, tree, work, root, sound_plan, write_plan):
    """The deadlock the first cut of this design had. Two artifacts, one task producing each: the
    exemption is declaring `produces` at all, so neither task is held to the other's artifact, and
    the plan reconciles because between them they produce both."""
    registry = tmp_path / "split.yaml"
    registry.write_text(yaml.safe_dump({**STANDARD, "presupposes": [
        {"path": p, "provides": f"what {p} provides.", "rules": ["PRH-01"]}
        for p in ("package.json", "tsconfig.json")]}, sort_keys=False), encoding="utf-8")

    for nid, produces in (("task/checkout/record-order", ["package.json"]),
                          ("task/checkout/bill-order", ["tsconfig.json"])):
        write_plan(nid, {**front_of(work, nid), "produces": produces})

    done = invoke(PLAN_PY, "--standard", registry, "--against", tree, work, root)
    assert done.returncode == 0, done.stdout + done.stderr

    # Each is delivered with the check the skill runs for a task that declares `produces` — the
    # one without --against — and each passes while the other's artifact is still absent.
    for _ in range(2):
        assert invoke(DELIVER_PY, "--standard", registry).returncode == 0


def test_a_task_producing_what_no_registry_presupposes_is_refused(
        tmp_path, tree, registry, work, root, sound_plan, write_plan):
    """The reconciliation's other direction, which went unchecked on the reading that producing an
    unpresupposed artifact is ordinary work. `produces` is not a description of output: it is the
    declaration that takes three exemptions — the offer order of `--outstanding`, the dropped
    substrate check at `/implement-task`, and owing the install instead of the build and the suite
    — and a plan handing them to ordinary work has disarmed them without deciding to. A consumer's
    plan arrived with six of nine tasks declaring it, none of them building substrate, against a
    schema that had said `Ordinary work declares none` the whole time."""
    task = front_of(work, "task/checkout/record-order")
    write_plan("task/checkout/record-order",
               {**task, "produces": ["package.json", "src/orders/place.ts"]})

    done = invoke(PLAN_PY, "--standard", registry, "--against", tree, work, root)
    assert done.returncode == 1, done.stdout + done.stderr
    assert "produces src/orders/place.ts, which" in done.stdout
    assert "presupposes nowhere" in done.stdout
    # The corrective act, both halves of it: this is not a refusal a reader has to interpret.
    assert "drop src/orders/place.ts from `produces`" in done.stdout
    assert "`presupposes`" in done.stdout
    # And the genuine half of the same declaration is untouched — the two sets coincide by
    # construction, so a real substrate task is refused by nothing here.
    assert "produces package.json, which" not in done.stdout
    assert not (work / "plan.json").is_file(), \
        "a refused plan derives nothing"


def test_the_check_runs_only_where_a_standard_is_named(
        tmp_path, tree, work, root, sound_plan, write_plan):
    """What a registry presupposes is the only thing that says what substrate is, so a plan
    validated without one is not held to a question nothing in front of it can answer."""
    task = front_of(work, "task/checkout/record-order")
    write_plan("task/checkout/record-order", {**task, "produces": ["src/orders/place.ts"]})
    done = invoke(PLAN_PY, work, root)
    assert done.returncode == 0, done.stdout + done.stderr
