"""`deliver.py --test-owner`: which answer a suite red on an earlier task's test takes (SPEC-004 R25).

«Where every plan whose proof names the test is closed, this delivery adopts the test whatever the
files share» (SPEC-004 R25). Each consumer here holds one delivering task and the proofs of other
tasks, under plans a `closure.md` closes or leaves live; the query reads the records and the
closure markers and prints the exit, so no session reads two implementation records by hand.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent
DELIVER = REPO / "src" / "claude" / "bin" / "deliver.py"
TEST = "tests/orders.test.ts"
NAMED = "rejects an order with no lines"


def put(path: Path, text: str = "x\n") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def record(home: Path, slug: str, kind: str, task: str, **front) -> Path:
    body = yaml.safe_dump(dict({"target": "backend"}, **front), sort_keys=False)
    return put(home / "delivery" / slug / kind / f"{task}.md",
               f"---\n{body}---\n## What was done\nProse.\n\n## Notes\nNone.\n")


def owner(home: Path, slug: str, task: str, files: list[str], closed: bool,
          tests: list[dict] | None = None, target: str = "backend") -> None:
    record(home, slug, "implementation", task, files=[{"path": p, "effect": "e"} for p in files])
    record(home, slug, "proof", task, target=target,
           tests=tests or [{"file": TEST, "name": NAMED, "proves": "p", "fails_when": "f"}])
    put(home / "work" / slug / "task" / f"{task}.md")
    if closed:
        put(home / "work" / slug / "closure.md")


def run(home: Path, *tests: str, task: str = "orders/add-line") -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(DELIVER), "--test-owner",
                           str(home / "delivery" / "now"), task, *tests],
                          capture_output=True, text=True, cwd=home)


@pytest.fixture
def consumer(tmp_path: Path) -> Path:
    home = tmp_path / "consumer"
    put(home / "siegard.json", json.dumps({
        "specification_root": "knowledge", "work_root": "work", "delivery_root": "delivery",
        "telemetry_root": "telemetry", "targets": {"backend": "src", "web": "web"}}))
    subprocess.run(["git", "init", "-q", str(home)], check=True)
    record(home, "now", "implementation", "orders/add-line",
           files=[{"path": "orders/lines.ts", "effect": "e"}])
    put(home / "work" / "now" / "task" / "orders" / "add-line.md")
    return home


def exit_line(result: subprocess.CompletedProcess) -> list[str]:
    return [line.split(": ", 1)[1] for line in result.stdout.splitlines()
            if line.startswith("  exit, for a red the diagnosis reads as `test`: ")]


def test_a_test_whose_every_owning_plan_is_closed_is_adopted_whatever_is_shared(consumer):
    owner(consumer, "skeleton", "orders/place", ["orders/place.ts"], closed=True)
    owner(consumer, "earlier", "orders/total", ["orders/lines.ts"], closed=True)
    result = run(consumer, TEST)
    assert result.returncode == 0, result.stderr
    assert "skeleton/orders/place — plan closed, shares no file" in result.stdout
    assert "earlier/orders/total — plan closed, shares orders/lines.ts" in result.stdout
    assert exit_line(result) == ["adopt"]


def test_a_live_owner_sharing_no_file_is_answered_by_its_re_delivery(consumer):
    owner(consumer, "parallel", "orders/sweep", ["orders/sweep.ts"], closed=False)
    result = run(consumer, TEST)
    assert "parallel/orders/sweep — plan live, shares no file" in result.stdout
    assert exit_line(result) == ["re-deliver parallel/orders/sweep"]


def test_a_live_owner_sharing_a_file_makes_the_test_this_deliverys_to_rewrite(consumer):
    owner(consumer, "parallel", "orders/total", ["orders/lines.ts", "orders/total.ts"],
          closed=False)
    result = run(consumer, TEST)
    assert "parallel/orders/total — plan live, shares orders/lines.ts" in result.stdout
    assert exit_line(result) == ["rewrite"]


def test_one_live_owner_sharing_nothing_decides_beside_a_closed_one(consumer):
    owner(consumer, "skeleton", "orders/place", ["orders/place.ts"], closed=True)
    owner(consumer, "parallel", "orders/sweep", ["orders/sweep.ts"], closed=False)
    assert exit_line(run(consumer, TEST)) == ["re-deliver parallel/orders/sweep"]


def test_a_named_test_is_owned_only_by_the_proofs_naming_it(consumer):
    owner(consumer, "skeleton", "orders/place", ["orders/place.ts"], closed=True)
    owner(consumer, "parallel", "orders/sweep", ["orders/sweep.ts"], closed=False,
          tests=[{"file": TEST, "name": "another test", "proves": "p", "fails_when": "f"}])
    assert exit_line(run(consumer, TEST)) == ["re-deliver parallel/orders/sweep"]
    assert exit_line(run(consumer, f"{TEST}::{NAMED}")) == ["adopt"]
    result = run(consumer, f"{TEST}::the order intake > {NAMED}")
    assert "skeleton/orders/place" in result.stdout and "parallel" not in result.stdout
    assert exit_line(result) == ["adopt"]


def test_a_test_no_other_proof_names_is_held_by_no_plan(consumer):
    record(consumer, "now", "proof", "orders/add-line",
           tests=[{"file": TEST, "name": NAMED, "proves": "p", "fails_when": "f"}])
    owner(consumer, "elsewhere", "web/form", ["form.ts"], closed=False, target="web")
    result = run(consumer, TEST, task="task/orders/add-line")
    assert "no other task's proof names it, so no plan holds it" in result.stdout
    assert exit_line(result) == ["adopt"]


def test_before_the_record_a_closed_owner_is_answered_and_a_live_ones_files_are_listed(consumer):
    (consumer / "delivery" / "now" / "implementation" / "orders" / "add-line.md").unlink()
    owner(consumer, "skeleton", "orders/place", ["orders/place.ts"], closed=True)
    assert exit_line(run(consumer, TEST)) == ["adopt"]
    owner(consumer, "parallel", "orders/sweep", ["orders/sweep.ts"], closed=False)
    result = run(consumer, TEST)
    assert "parallel/orders/sweep — plan live, no record of this task yet; the owner's names " \
           "orders/sweep.ts" in result.stdout
    assert exit_line(result) == ["rewrite where the implementer's return names a file the record "
                                 "of parallel/orders/sweep names, else re-deliver "
                                 "parallel/orders/sweep"]


def test_each_test_named_is_answered_on_its_own(consumer):
    owner(consumer, "skeleton", "orders/place", ["orders/place.ts"], closed=True)
    owner(consumer, "parallel", "orders/sweep", ["orders/sweep.ts"], closed=False,
          tests=[{"file": "tests/sweep.test.ts", "name": "n", "proves": "p", "fails_when": "f"}])
    assert exit_line(run(consumer, TEST, "tests/sweep.test.ts")) == [
        "adopt", "re-deliver parallel/orders/sweep"]


@pytest.mark.parametrize("args", [[], ["delivery/now"], ["delivery/now", "orders/add-line"],
                                  ["delivery/missing", "orders/add-line", TEST]])
def test_what_it_cannot_read_it_refuses(consumer, args):
    result = subprocess.run([sys.executable, "-B", str(DELIVER), "--test-owner",
                             *[str(consumer / a) if a.startswith("delivery") else a for a in args]],
                            capture_output=True, text=True, cwd=consumer)
    assert result.returncode == 2
    assert result.stderr.startswith("cannot run:")
