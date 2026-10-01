"""trace.py --ledger: a material ledger says where every fact line of survey material went —
the node that holds it, or why none does — and is refused whole where a fact has no entry
(SPEC-005 R2a). Sound, it prints what an adoption reads from it: the file set and the
candidates per file."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

import trace

REPO = Path(__file__).resolve().parent.parent
TRACE_PY = Path(trace.__file__)
FIXTURE = REPO / "tests" / "fixtures" / "spec-model"

NODE = "domain/troubleshooting/case"
RULE = "rules/troubleshooting/hypothesis-requires-evidence"
FILE = "src/orders/place.ts"
SECOND = "src/orders/bill.ts"

MATERIAL = """---
contract_version: siegard-survey/1
target: backend
files:
  - src/orders/place.ts
  - src/orders/bill.ts
---

## Facts
### Cases
- A case is opened by an operator and carries a status. `src/orders/place.ts` (`place`).
- A hypothesis needs evidence before it is accepted. `src/orders/bill.ts` (`bill`).
  - indented detail, part of the fact above
- Billing logs every call. `src/orders/bill.ts` (`log`).

## Answers
- open — status missing → 422 `VALIDATION_INVALID_FORMAT`. `src/orders/place.ts` (`schema`).

## Vocabularies
None.

## Upstream artifacts
None.

## Outside the domain
- The route prefix. `src/orders/place.ts`.

## Observed and not decided here
None.
"""


def run(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(TRACE_PY), *map(str, args)],
                          capture_output=True, text=True)


@pytest.fixture
def surveyed(tmp_path: Path) -> Path:
    spec_root = tmp_path / "specs"
    shutil.copytree(FIXTURE, spec_root)
    shutil.rmtree(spec_root / "projections", ignore_errors=True)
    survey = tmp_path / "siegard-survey" / "adopt-orders"
    survey.mkdir(parents=True)
    (survey / "orders.md").write_text(MATERIAL, encoding="utf-8")
    return tmp_path


def fact_lines(path: Path) -> dict[str, int]:
    """Line numbers of the fact lines, keyed by a word each carries."""
    found = {}
    for number, line in enumerate(path.read_text(encoding="utf-8").split("\n"), start=1):
        for key in ("opened", "hypothesis", "Billing logs", "status missing"):
            if line.startswith("- ") and key in line:
                found[key] = number
    return found


def ledger_at(surveyed: Path, entries: list[dict], material=("orders.md",)) -> Path:
    path = surveyed / "siegard-survey" / "adopt-orders" / "ledger.md"
    front = {"contract_version": "siegard-ledger/1", "material": list(material),
             "entries": entries}
    path.write_text("---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n", encoding="utf-8")
    return path


def full_entries(surveyed: Path) -> list[dict]:
    at = fact_lines(surveyed / "siegard-survey" / "adopt-orders" / "orders.md")
    return [{"at": f"orders.md:{at['opened']}", "node": NODE},
            {"at": f"orders.md:{at['hypothesis']}", "node": RULE},
            {"at": f"orders.md:{at['Billing logs']}", "outside": "logging is implementation"},
            {"at": f"orders.md:{at['status missing']}", "node": NODE}]


def test_a_complete_ledger_is_sound_and_prints_the_candidates_per_file(surveyed):
    done = run("--ledger", ledger_at(surveyed, full_entries(surveyed)), surveyed / "specs")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "ledger sound: 4 fact line(s) over 1 material file(s) — 3 landed in 2 node(s), 1 left out" \
        in done.stdout
    assert f"{FILE}: 1" in done.stdout and f"{SECOND}: 1" in done.stdout
    assert f"candidates, all: {NODE} {RULE}" in done.stdout


def test_a_fact_line_with_no_entry_refuses_the_ledger(surveyed):
    entries = full_entries(surveyed)[:-1]
    done = run("--ledger", ledger_at(surveyed, entries), surveyed / "specs")
    assert done.returncode == 1
    assert "no entry — «Every fact line of the material lands in a node" in done.stdout
    assert "status missing" in done.stdout


def test_an_entry_at_no_fact_line_is_refused(surveyed):
    entries = full_entries(surveyed) + [{"at": "orders.md:1", "outside": "not a fact"}]
    done = run("--ledger", ledger_at(surveyed, entries), surveyed / "specs")
    assert done.returncode == 1 and "orders.md:1 is no fact line" in done.stdout


def test_an_indented_bullet_and_an_outside_the_domain_line_are_not_fact_lines(surveyed):
    """Only the four fact headings' top-level bullets are owed an entry."""
    done = run("--ledger", ledger_at(surveyed, full_entries(surveyed)), surveyed / "specs")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "4 fact line(s)" in done.stdout


def test_a_node_the_specification_does_not_hold_is_refused(surveyed):
    entries = full_entries(surveyed)
    entries[0] = {"at": entries[0]["at"], "node": "domain/troubleshooting/ghost"}
    done = run("--ledger", ledger_at(surveyed, entries), surveyed / "specs")
    assert done.returncode == 1 and "holds no node domain/troubleshooting/ghost" in done.stdout


def test_an_entry_naming_both_a_node_and_a_reason_is_refused_by_the_contract(surveyed):
    entries = full_entries(surveyed)
    entries[0] = {**entries[0], "outside": "and also out"}
    done = run("--ledger", ledger_at(surveyed, entries), surveyed / "specs")
    assert done.returncode == 2 and "entries/0" in done.stderr


def test_material_that_fails_its_own_contract_stops_the_ledger(surveyed):
    material = surveyed / "siegard-survey" / "adopt-orders" / "orders.md"
    material.write_text(MATERIAL.replace("target: backend\n", ""), encoding="utf-8")
    done = run("--ledger", ledger_at(surveyed, []), surveyed / "specs")
    assert done.returncode == 2 and "'target' is a required property" in done.stderr


def test_ledger_is_its_own_form(surveyed):
    done = run("--ledger", ledger_at(surveyed, full_entries(surveyed)), surveyed / "specs",
               "--check")
    assert done.returncode == 2 and "mutually exclusive" in done.stderr


def test_survey_holds_material_to_its_contract_and_counts_its_fact_lines(surveyed):
    material = surveyed / "siegard-survey" / "adopt-orders" / "orders.md"
    done = run("--survey", material)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "4 fact line(s) over 2 file(s) — Facts 3, Answers 1, Vocabularies 0, Upstream artifacts 0" \
        in done.stdout
    assert "no fact names" not in done.stdout
    broken = surveyed / "siegard-survey" / "adopt-orders" / "broken.md"
    broken.write_text(MATERIAL.replace("  - src/orders/bill.ts\n", "  - src/orders/bill.ts\n  - src/orders/quiet.ts\n"),
                      encoding="utf-8")
    done = run("--survey", material, broken)
    assert done.returncode == 0 and "1 file(s) no fact names: src/orders/quiet.ts" in done.stdout
    broken.write_text(MATERIAL.replace("contract_version: siegard-survey/1", "contract_version: x"),
                      encoding="utf-8")
    done = run("--survey", material, broken)
    assert done.returncode == 2 and "contract_version" in done.stderr


def declared_tests(surveyed: Path) -> Path:
    """The surveyed tree as a project declaring `src/orders/*.ts` its tests, so material over
    `src/orders` lists only tests."""
    subprocess.run(["git", "init", "-q", str(surveyed)], check=True, capture_output=True)
    (surveyed / "siegard.json").write_text(json.dumps(
        {"specification_root": "specs", "targets": {"backend": "backend"},
         "tests": {"backend": [{"under": "src/orders", "suffix": "bill.ts"}]}}) + "\n",
        encoding="utf-8")
    return surveyed / "siegard-survey" / "adopt-orders" / "orders.md"


def test_survey_refuses_material_that_lists_a_declared_test(surveyed):
    material = declared_tests(surveyed)
    done = run("--survey", material)
    assert done.returncode == 2
    assert "lists src/orders/bill.ts, which the target's declared test scope holds" in done.stderr


def test_a_ledger_still_reads_material_held_before_tests_were_declared(surveyed):
    """The refusal is the `--survey` form's: a ledger rereads its material as it was held, and a
    declaration added afterwards does not unmake an increment already analysed."""
    declared_tests(surveyed)
    ledger = ledger_at(surveyed, full_entries(surveyed))
    done = run("--ledger", ledger, surveyed / "specs")
    assert done.returncode == 0, done.stdout + done.stderr
