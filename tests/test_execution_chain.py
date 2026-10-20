"""The execution chain, end to end, with the runner actually running.

Every link is unit-tested beside its own script, and this module exists for the same reason
`test_substrate_chain.py` does: the links are what go wrong. Here the runs are real — `bin/run.py`
executes real commands into real directories — because the two rules that make this arrangement
safe are both properties of the runner rather than of any prose. It refuses a slug that already
exists, which is what turns iterating from something forbidden into something recorded. And it
stops at the first step that does not pass, which is what keeps a suite from running against a tree
that never installed.

The commands are `true` and `false`. What is under test is the chain, not a package manager.
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
from conftest import STANDARD, derive_plan, task_pin_of

REPO = Path(__file__).resolve().parent.parent
RUN_PY = REPO / "src/claude/bin/run.py"
DELIVER_PY = REPO / "src/claude/bin/deliver.py"


def invoke(script: Path, *args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(script), *map(str, args)],
                          capture_output=True, text=True)


def capture(delivery: Path, tree: Path, slug: str, *steps: tuple[str, str]):
    """One run, as a skill makes it: the runner, the project's own commands, a name of its own."""
    return invoke(RUN_PY, delivery, "--run", slug, "--cwd", tree, "--timeout-seconds", "60",
                  *[f"--step={name}={command}" for name, command in steps])


def front_of(root: Path, nid: str) -> dict:
    text = (root / f"{nid}.md").read_text(encoding="utf-8")
    return yaml.safe_load(re.match(r"^---\n(.*?)\n---\n", text, re.S).group(1))


@pytest.fixture
def tree(tmp_path: Path) -> Path:
    where = tmp_path / "tree"
    where.mkdir()
    (where / "siegard.json").write_text(json.dumps({"targets": {"app": "."}}), encoding="utf-8")
    return where


@pytest.fixture
def registry(tree: Path):
    """The project's registry, at its own path in the target source root — nothing copies it —
    returned as the reference a record pins."""
    def put(**overrides) -> tuple[Path, dict]:
        data = {**STANDARD, **overrides}
        path = tree / "example-service.yaml"
        path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
        return path, {"at": "example-service.yaml", "pin": deliver.pin_of(path)}
    return put


def problems_of(delivery: Path, work: Path, target: Path, root: Path) -> list[str]:
    validator = deliver.contract()
    names = deliver.pass_names()
    derive_plan(work, root)
    plan_nodes, plan_problems = deliver.load_plan(work, root)
    assert plan_problems == [], plan_problems
    nodes, found = deliver.collect(delivery, validator, names)
    return found + deliver.cross_problems(nodes, plan_nodes, work, names, delivery, target)


def test_the_chain_holds_from_an_empty_tree_to_a_delivery_that_ran(
        tree, delivery, work, root, sound_plan, write_plan, sound_delivery, write_delivery,
        registry):

    # 1. The registry presupposes a manifest, authorizes one package, and declares how the project
    #    is installed and checked. The tree holds none of it.
    path, ref = registry(presupposes=[{
        "path": "package.json", "provides": "the lint step and the logger.", "rules": ["PRH-01"]}])
    blocked = invoke(DELIVER_PY, "--standard", path, "--against", tree)
    assert blocked.returncode == 1, blocked.stdout
    assert "package.json: ABSENT" in blocked.stdout

    # 2. The task that produces the manifest is the one task that absence cannot stop, and the
    #    skill reads that as a yes or a no: it runs the same check without --against.
    write_plan("task/checkout/record-order",
               {**front_of(work, "task/checkout/record-order"), "produces": ["package.json"]})
    assert invoke(DELIVER_PY, "--standard", path).returncode == 0

    # 3. The implementer writes the manifest and adds the one package the registry admits. The
    #    skill then runs install and every step that is not the suite.
    (tree / "package.json").write_text(json.dumps({"name": "x"}), encoding="utf-8")
    (tree / "tests").mkdir()
    (tree / "tests/place.spec.ts").write_text("it('places', () => {})\n", encoding="utf-8")
    built = capture(delivery, tree, "checkout-record-order-build",
                    ("install", "true"), ("lint", "true"))
    assert built.returncode == 0, built.stdout + built.stderr
    assert (delivery / "run/checkout-record-order-build/run.json").is_file()

    # 4. The record carries the run that passed, what it installed, and the standard it read.
    record = front_of(delivery, "implementation/checkout/record-order")
    record["task"] = task_pin_of(work, "task/checkout/record-order")
    record["standard"] = ref
    record["run"] = "run/checkout-record-order-build"
    record["installed"] = ["pino"]
    record["files"] = record["files"] + [
        {"path": "package.json", "effect": "declares the lint step and the logger dependency"}]
    write_delivery("implementation/checkout/record-order", record)

    proof = front_of(delivery, "proof/checkout/record-order")
    proof["implementation"] = deliver.pin_of(
        delivery / "implementation/checkout/record-order.md")
    write_delivery("proof/checkout/record-order", proof)

    # The proof owes a run of its own — its registry declares commands — and until it has one the
    # delivery does not hold together.
    proof["standard"] = ref
    write_delivery("proof/checkout/record-order", proof)
    assert any("captured no run" in p for p in problems_of(delivery, work, tree, root))

    # 5. The suite goes red. The runner stops at the failing step, and nothing further is written.
    red = capture(delivery, tree, "checkout-record-order-suite",
                  ("install", "true"), ("lint", "true"), ("test", "false"))
    assert red.returncode == 1
    captured = json.loads(
        (delivery / "run/checkout-record-order-suite/run.json").read_text(encoding="utf-8"))
    assert captured["outcome"] == "failed" and captured["failed_step"] == "test"

    proof["run"] = "run/checkout-record-order-suite"
    write_delivery("proof/checkout/record-order", proof)
    assert any("run again under a name of its own" in p for p in problems_of(delivery, work, tree, root)), \
        "a proof over a red suite is refused; the delivery is not talked into holding together"

    # 6. The source is fixed and the suite runs again. The first run keeps its name, so what it
    #    took is readable afterwards by somebody who was not here.
    again = capture(delivery, tree, "checkout-record-order-suite",
                    ("install", "true"), ("test", "true"))
    assert again.returncode == 2 and "already exists" in again.stderr, \
        "the runner refuses to overwrite the evidence of the attempt that failed"

    green = capture(delivery, tree, "checkout-record-order-suite-2",
                    ("install", "true"), ("lint", "true"), ("test", "true"))
    assert green.returncode == 0, green.stdout + green.stderr
    proof["run"] = "run/checkout-record-order-suite-2"
    write_delivery("proof/checkout/record-order", proof)
    assert any("## Notes names none of run/checkout-record-order-suite," in p
               for p in problems_of(delivery, work, tree, root)), \
        "the red attempt beside the proof is named in its Notes with its cause, or the proof " \
        "is refused"
    write_delivery("proof/checkout/record-order", proof,
                   body="## What it is\nProse for a reader.\n\n## Notes\n"
                        "run/checkout-record-order-suite failed at test: the assertion "
                        "read the stored order_number before it was persisted.\n")
    assert problems_of(delivery, work, tree, root) == []

    # Both attempts are on disk, which is the whole of what replaced "this invocation runs nothing".
    assert (delivery / "run/checkout-record-order-suite/run.json").is_file()
    assert (delivery / "run/checkout-record-order-suite-2/run.json").is_file()

    # 7. And the substrate now stands, so the gate opens for every task that produces nothing.
    opened = invoke(DELIVER_PY, "--standard", path, "--against", tree)
    assert opened.returncode == 0, opened.stdout


def test_a_package_the_registry_never_admitted_does_not_reach_a_record(
        tree, delivery, work, root, sound_plan, sound_delivery, write_delivery, registry):
    """The allowlist is where a human's approval of a package survives the session it was given in.
    A delivery able to install past it would make the approval decorative."""
    _, ref = registry()
    built = capture(delivery, tree, "build", ("install", "true"), ("lint", "true"))
    assert built.returncode == 0

    record = front_of(delivery, "implementation/checkout/record-order")
    record["standard"] = ref
    record["run"] = "run/build"
    record["installed"] = ["pino", "left-pad"]
    write_delivery("implementation/checkout/record-order", record)
    proof = front_of(delivery, "proof/checkout/record-order")
    proof["implementation"] = deliver.pin_of(delivery / "implementation/checkout/record-order.md")
    write_delivery("proof/checkout/record-order", proof)

    problems = problems_of(delivery, work, tree, root)
    assert any("left-pad, which example-service.yaml does not authorize" in p
               for p in problems), problems
    assert not any("pino" in p for p in problems), "the admitted package is not the finding"


def test_a_step_never_runs_against_a_tree_that_did_not_install(tree, delivery):
    """The runner's own rule, exercised where it matters: a suite run against a tree that failed to
    install would report failures about a build nobody made."""
    done = capture(delivery, tree, "build", ("install", "false"), ("lint", "true"),
                   ("test", "true"))
    assert done.returncode == 1
    captured = json.loads((delivery / "run/build/run.json").read_text(encoding="utf-8"))
    assert captured["failed_step"] == "install"
    assert [s["outcome"] for s in captured["steps"]] == ["failed", "not_run", "not_run"]


SUBSTRATE = [{"path": "package.json", "provides": "the lint step and the logger.",
              "rules": ["PRH-01"]}]
CHECK_WITH_NOTHING_TO_CHECK = [
    {"step": "install", "command": "true", "timeout_seconds": 60, "role": "install"},
    {"step": "lint", "command": "ls src", "timeout_seconds": 60},
    {"step": "test", "command": "true", "timeout_seconds": 60, "role": "suite"},
]


def test_a_check_with_nothing_to_check_is_not_what_the_substrate_owes(
        tree, delivery, work, root, sound_plan, write_plan, sound_delivery, write_delivery,
        registry):
    """The case every other test here could not express. `true` passes whether it checked
    everything or nothing, so a fixture built from it proves the chain and says nothing about what
    the steps decide — and what goes wrong in a real tree is exactly a step with nothing to decide.
    `ls src` is the smallest command that fails for that reason and holds no knowledge of any
    stack: it exits non-zero precisely while the directory a rule's scope names is not there.

    Run in full, the substrate's build is red and can never be anything else — the check needs
    source, no task may invent source, and the task that would write it waits on this one. That is
    the circularity `produces` breaks at the plan gate, reappearing one gate later. What the
    substrate owes is the install, which decides the one thing decidable here: the manifest is well
    formed and what it names resolves.

    What this discriminates, said plainly: not the skill's old rule, which no test can execute, but
    the pairing. Remove the exemption while the coverage check stands and this fails — which is the
    deadlock moved from the skill into the validator, where there is no recovering from it. The two
    halves ship together or neither does, and this is what says so."""
    path, ref = registry(presupposes=SUBSTRATE, commands=CHECK_WITH_NOTHING_TO_CHECK)
    write_plan("task/checkout/record-order",
               {**front_of(work, "task/checkout/record-order"), "produces": ["package.json"]})
    (tree / "package.json").write_text(json.dumps({"name": "x"}), encoding="utf-8")
    assert invoke(DELIVER_PY, "--standard", path).returncode == 0

    full = capture(delivery, tree, "checkout-record-order-build",
                   ("install", "true"), ("lint", "ls src"))
    assert full.returncode == 1, "a check over a tree with no source is red, and stays red"
    assert json.loads((delivery / "run/checkout-record-order-build/run.json")
                      .read_text(encoding="utf-8"))["failed_step"] == "lint"

    ran = capture(delivery, tree, "checkout-record-order-build-2", ("install", "true"))
    assert ran.returncode == 0, ran.stdout + ran.stderr

    record = front_of(delivery, "implementation/checkout/record-order")
    record["task"] = task_pin_of(work, "task/checkout/record-order")
    record["standard"] = ref
    record["run"] = "run/checkout-record-order-build-2"
    record["files"] = [{"path": "package.json",
                        "effect": "declares the lint step and the logger dependency"}]
    record["nodes"] = [{"node": "domain/sales/order",
                        "how": "the substrate encodes no fact of it; what it holds is what every "
                               "rule needs before any of them can be applied"}]
    write_delivery("implementation/checkout/record-order", record)
    # No proof, and that is the state rather than an omission: there is no source for a test to
    # reach, and a proof requires at least one test that can be said to fail.
    (delivery / "proof/checkout/record-order.md").unlink()

    assert problems_of(delivery, work, tree, root) == []
    derive_plan(work, root)
    outstanding = invoke(DELIVER_PY, "--outstanding", delivery, work, tree, root)
    assert "implemented, and no proof record holds it up" in outstanding.stdout, outstanding.stdout


def test_a_record_pointing_at_a_fraction_of_the_steps_is_refused(
        tree, delivery, work, root, sound_plan, sound_delivery, write_delivery, registry):
    """Presence was never the whole question, and until this it was the whole check. The registry
    declares an install and a check, this delivery ran the install alone, and a record pointing at
    it was read as a delivery whose project had been checked. Nothing decided the rules the check
    owns, which is the state the owed run exists to end."""
    _, ref = registry()
    part = capture(delivery, tree, "build", ("install", "true"))
    assert part.returncode == 0

    record = front_of(delivery, "implementation/checkout/record-order")
    record["standard"] = ref
    record["run"] = "run/build"
    write_delivery("implementation/checkout/record-order", record)
    proof = front_of(delivery, "proof/checkout/record-order")
    proof["implementation"] = deliver.pin_of(delivery / "implementation/checkout/record-order.md")
    write_delivery("proof/checkout/record-order", proof)

    problems = problems_of(delivery, work, tree, root)
    assert any("passed only install" in p and "nothing decided the rules lint own" in p
               for p in problems), problems
    assert not any("declares `produces`" in p for p in problems), \
        "this task produces nothing, so the exemption is not what the refusal is about"


def test_a_task_that_produces_and_also_writes_source_owes_every_step(
        tree, delivery, work, root, sound_plan, write_plan, sound_delivery, write_delivery,
        registry):
    """The exemption is not a licence. `produces` alone would let any task run the install and call
    every check answered; what bounds it is that nothing the record wrote sits in the scope of a
    rule. This one wrote `src/orders/place.ts`, which PRH-01 reaches, so the source it wrote beside
    the substrate owes the steps that decide the rules reaching it."""
    _, ref = registry(presupposes=SUBSTRATE)
    write_plan("task/checkout/record-order",
               {**front_of(work, "task/checkout/record-order"), "produces": ["package.json"]})
    part = capture(delivery, tree, "build", ("install", "true"))
    assert part.returncode == 0

    record = front_of(delivery, "implementation/checkout/record-order")
    record["task"] = task_pin_of(work, "task/checkout/record-order")
    record["standard"] = ref
    record["run"] = "run/build"
    record["files"] = record["files"] + [
        {"path": "package.json", "effect": "declares the lint step and the logger dependency"}]
    write_delivery("implementation/checkout/record-order", record)
    (delivery / "proof/checkout/record-order.md").unlink()

    problems = problems_of(delivery, work, tree, root)
    assert any("wrote a file a rule of example-service.yaml reaches" in p
               for p in problems), problems
