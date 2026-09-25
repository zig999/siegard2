"""A consumer tree frozen before the frontend work, held to every validator afterwards.

`tests/fixtures/backend-baseline/` is a whole small consumer: a specification, a plan with its
derived index, a delivery holding an implementation, a proof and a four-pass review with its
derived index, a target source root with a standard, a `siegard.json` declaring the five fields
that existed when it was written, and a trace carrying one drift of each class. It was generated
once, against the code as it stood before any of this, and it is **never regenerated**. That is
the whole point: the code moved and the fixture did not, so what these tests compare is the new
validator against the old artifact. One byte range is the exception, and it is recorded here so
it is never mistaken for the rule: the plan index was re-derived once when each `implements` edge
gained the digest of the node it anchors. The plan is live, a live index derived before the anchor
existed is stale by design, and that one re-derivation is the upgrade a consumer's live plan pays
too; every other byte stands as generated.

Three failure modes this exists to catch, all of them silent and all of them expensive:

- **a field that became required.** Every node here declares exactly what a node could declare
  before, so a new required field — or a new value a totality check demands, such as a fifth
  review pass — is refused here rather than in a consumer's tree.
- **a contract version bumped.** Both derived indexes are committed. `--check` compares a
  committed index against what the nodes derive to now, and a bumped `contract_version` or a new
  edge kind makes it stale — which, in a consumer, stops every entry point before it writes.
- **a drift class that stopped being reported.** The trace holds one `code`, one `moved` and one
  `orphaned` finding, and a target that declares nothing must still see all three.

The tree is copied into a temporary git toplevel per test, because `trace.py` resolves the trace's
home from git and the fixture's own home is this repository.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
BIN = REPO / "src/claude/bin"
BASELINE = REPO / "tests/fixtures/backend-baseline"

WORK = "work/troubleshooting"
DELIVERY = "delivery/troubleshooting"
TARGET = "backend"
SPEC = "specification"


def run(script: str, *args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(BIN / script), *map(str, args)],
                          capture_output=True, text=True)


@pytest.fixture
def tree(tmp_path: Path) -> Path:
    """The frozen consumer, in a git toplevel of its own."""
    home = tmp_path / "consumer"
    shutil.copytree(BASELINE, home)
    subprocess.run(["git", "init", "-q", str(home)], check=True, capture_output=True)
    return home


def test_the_frozen_plan_still_validates(tree):
    done = run("plan.py", "--check", tree / WORK, tree / SPEC)
    assert done.returncode == 0, done.stdout + done.stderr


def test_the_frozen_plan_index_is_still_what_the_nodes_derive_to(tree):
    """`--check` is the comparison; this asserts the bytes too, so a difference is readable as a
    diff rather than as one word."""
    before = (tree / WORK / "plan.json").read_text(encoding="utf-8")
    assert run("plan.py", tree / WORK, tree / SPEC).returncode == 0
    assert (tree / WORK / "plan.json").read_text(encoding="utf-8") == before, \
        "the plan index a consumer committed is no longer what these nodes derive to"


def test_the_frozen_delivery_still_validates(tree):
    done = run("deliver.py", "--check", tree / DELIVERY, tree / WORK,
               tree / TARGET, tree / SPEC)
    assert done.returncode == 0, done.stdout + done.stderr


def test_the_frozen_delivery_index_is_still_what_the_nodes_derive_to(tree):
    before = (tree / DELIVERY / "delivery.json").read_text(encoding="utf-8")
    assert run("deliver.py", tree / DELIVERY, tree / WORK, tree / TARGET,
               tree / SPEC).returncode == 0
    assert (tree / DELIVERY / "delivery.json").read_text(encoding="utf-8") == before, \
        "the delivery index a consumer committed is no longer what these nodes derive to"


def test_the_four_pass_review_is_still_a_complete_review(tree):
    """The review answers for coverage, conformance, standard and failures and for nothing else.
    A fifth pass added to the contract's totality would refuse it here — which is exactly the
    consumer whose delivery root stops validating the day the framework updates."""
    done = run("deliver.py", "--node", tree / DELIVERY / "review/first.md", tree / DELIVERY)
    assert done.returncode == 0, done.stdout + done.stderr
    extra = run("deliver.py", "--node", tree / DELIVERY / "review/first.md",
                tree / DELIVERY, tree / WORK, tree / SPEC)
    assert extra.returncode == 2 and "expected --node <file> <delivery-root>" in extra.stderr


def test_the_contract_versions_the_frozen_indexes_name_still_stand(tree):
    plan = json.loads((tree / WORK / "plan.json").read_text(encoding="utf-8"))
    delivery = json.loads((tree / DELIVERY / "delivery.json").read_text(encoding="utf-8"))
    assert plan["contract_version"] == "siegard-plan/3"
    assert delivery["contract_version"] == "siegard-delivery/2"


def test_the_frozen_project_file_still_resolves(tree):
    done = run("project.py", tree)
    assert done.returncode == 0, done.stdout + done.stderr
    for line in ("standard:", "specification_root:", "target backend:", "work_root:",
                 "delivery_root:"):
        assert line in done.stdout, \
            f"{line!r} is no longer reported for a project that declares it"


def test_the_frozen_standard_still_holds_together(tree):
    done = run("deliver.py", "--standard", tree / TARGET / "standard.yaml")
    assert done.returncode == 0, done.stdout + done.stderr


def test_a_target_declaring_nothing_still_sees_all_three_drift_classes(tree):
    """The baseline declares no exemption of any kind, so every class the trace can report is
    reported. A suppression that reached a target nobody exempted would show up here."""
    done = run("trace.py", "--check", tree / TARGET)
    assert done.returncode == 1, done.stdout + done.stderr
    assert "1 orphaned" in done.stdout
    assert "1 moved" in done.stdout
    assert "1 code" in done.stdout
    assert "3 drift finding(s)" in done.stdout
