"""Intent material: what a target's declared tests say the source should do, each fact beside the
test it was read at and the source file it governs (SPEC-005 R9). `--survey` holds it to
`intent.json` and to the target's declared test scope, a ledger accounts for its fact lines as it
does for survey material (R8), and an adoption over that ledger hands each governed file the nodes
its facts landed in — never a test."""
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
OTHER = "domain/troubleshooting/evidence"
RULE = "rules/troubleshooting/hypothesis-requires-evidence"
FILE = "src/orders/place.ts"
SECOND = "src/orders/bill.ts"
THIRD = "src/orders/index.ts"
PLACE_TEST = "src/orders/place.spec.ts"
BILL_TEST = "src/orders/bill.spec.ts"

MATERIAL = f"""---
contract_version: siegard-intent/1
target: backend
tests:
  - {PLACE_TEST}
  - {BILL_TEST}
files:
  - {FILE}
  - {SECOND}
  - {THIRD}
---

## Facts
- A case is opened and carries a status. `{PLACE_TEST}` (`opens a case`) → `{FILE}`.
- A hypothesis needs evidence before it is accepted. `{BILL_TEST}` (`needs evidence`) → `{SECOND}`.
- Evidence is attached to a case. `{PLACE_TEST}` (`attaches evidence`) → `{FILE}`, `{SECOND}`.
  - indented detail, part of the fact above

## Answers
- open — status missing → 422 `VALIDATION_INVALID_FORMAT`. `{PLACE_TEST}` (`refuses`) → `{FILE}`.

## Vocabularies
None.

## Upstream artifacts
None.

## Outside the domain
- The fixture builder. `{BILL_TEST}`.

## Observed and not decided here
None.
"""


def run(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(TRACE_PY), *map(str, args)],
                          capture_output=True, text=True)


@pytest.fixture
def project(tmp_path: Path) -> Path:
    """A consumer whose source no delivery wrote, declaring `.spec.ts` under `src` its tests, with
    intent material read from two of them."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, capture_output=True)
    spec_root = tmp_path / "specs"
    shutil.copytree(FIXTURE, spec_root)
    shutil.rmtree(spec_root / "projections", ignore_errors=True)
    target = tmp_path / "backend"
    (target / "src/orders").mkdir(parents=True)
    for given in (FILE, SECOND, THIRD, PLACE_TEST, BILL_TEST):
        (target / given).write_text(f"export const x = '{given}';\n", encoding="utf-8")
    (tmp_path / "siegard.json").write_text(json.dumps(
        {"specification_root": "specs", "targets": {"backend": "backend"},
         "tests": {"backend": [{"under": "src", "suffix": ".spec.ts", "nested": True}]}}) + "\n",
        encoding="utf-8")
    material = tmp_path / "siegard-survey" / "intent-orders"
    material.mkdir(parents=True)
    (material / "orders.md").write_text(MATERIAL, encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "-A"], check=True)
    return tmp_path


def material_of(project: Path) -> Path:
    return project / "siegard-survey" / "intent-orders" / "orders.md"


def rewrite(project: Path, old: str, new: str) -> Path:
    path = material_of(project)
    text = path.read_text(encoding="utf-8")
    assert old in text
    path.write_text(text.replace(old, new), encoding="utf-8")
    return path


def line_of(text: str, key: str) -> int:
    return next(n for n, line in enumerate(text.split("\n"), start=1)
                if line.startswith("- ") and key in line)


def ledger_at(project: Path, entries: list[dict] | None = None) -> Path:
    text = MATERIAL
    if entries is None:
        entries = [{"at": f"orders.md:{line_of(text, 'opened')}", "node": NODE},
                   {"at": f"orders.md:{line_of(text, 'hypothesis')}", "node": RULE},
                   {"at": f"orders.md:{line_of(text, 'attached')}", "node": OTHER},
                   {"at": f"orders.md:{line_of(text, 'status missing')}", "node": NODE}]
    front = {"contract_version": "siegard-ledger/1", "material": ["orders.md"],
             "entries": entries}
    path = material_of(project).parent / "ledger.md"
    path.write_text("---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(project), "add", "-A"], check=True)
    return path


def test_survey_holds_intent_material_and_counts_what_it_holds(project):
    done = run("--survey", material_of(project))
    assert done.returncode == 0, done.stdout + done.stderr
    assert "4 fact line(s) over 3 file(s) — Facts 3, Answers 1, Vocabularies 0, " \
           "Upstream artifacts 0" in done.stdout
    assert f"1 file(s) no fact names: {THIRD}" in done.stdout
    assert "no fact was read at" not in done.stdout


def test_a_listed_test_no_fact_was_read_at_is_reported(project):
    rewrite(project, f"  - {BILL_TEST}\nfiles:", f"  - {BILL_TEST}\n  - src/orders/ship.spec.ts\nfiles:")
    done = run("--survey", material_of(project))
    assert done.returncode == 0, done.stdout + done.stderr
    assert "1 test(s) no fact was read at: src/orders/ship.spec.ts" in done.stdout


def test_a_fact_line_naming_no_test_is_refused_by_line(project):
    path = rewrite(project, f"`{BILL_TEST}` (`needs evidence`) → ", "")
    done = run("--survey", path)
    assert done.returncode == 2
    at = line_of(path.read_text(encoding="utf-8"), "hypothesis")
    assert f"orders.md:{at}: the fact names a test of `tests` nowhere in backticks" in done.stderr


def test_a_fact_line_naming_no_governed_file_is_refused_by_line(project):
    path = rewrite(project, f"(`opens a case`) → `{FILE}`", "(`opens a case`)")
    done = run("--survey", path)
    assert done.returncode == 2
    at = line_of(path.read_text(encoding="utf-8"), "opened")
    assert f"orders.md:{at}: the fact names a file of `files` nowhere in backticks" in done.stderr


def test_a_listed_test_the_scope_does_not_declare_is_refused(project):
    rewrite(project, f"tests:\n  - {PLACE_TEST}", f"tests:\n  - {PLACE_TEST}\n  - {THIRD}")
    done = run("--survey", material_of(project))
    assert done.returncode == 2
    assert f"lists {THIRD} under `tests`, which the target's declared test scope does not hold" \
        in done.stderr


def test_a_governed_file_that_is_a_declared_test_is_refused(project):
    rewrite(project, f"files:\n  - {FILE}", f"files:\n  - {FILE}\n  - {PLACE_TEST}")
    done = run("--survey", material_of(project))
    assert done.returncode == 2
    assert f"lists {PLACE_TEST} under `files`, which the target's declared test scope holds" \
        in done.stderr


def test_a_target_declaring_no_tests_refuses_intent_material(project):
    (project / "siegard.json").write_text(json.dumps(
        {"specification_root": "specs", "targets": {"backend": "backend"}}) + "\n",
        encoding="utf-8")
    done = run("--survey", material_of(project))
    assert done.returncode == 2
    assert "the project declares no tests for target backend" in done.stderr
    assert "/siegard-config" in done.stderr


def test_intent_material_without_tests_fails_its_contract(project):
    rewrite(project, f"tests:\n  - {PLACE_TEST}\n  - {BILL_TEST}\n", "")
    done = run("--survey", material_of(project))
    assert done.returncode == 2 and "'tests' is a required property" in done.stderr


def test_a_ledger_over_intent_material_is_sound(project):
    done = run("--ledger", ledger_at(project), project / "specs")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "ledger sound: 4 fact line(s) over 1 material file(s) — 4 landed in 3 node(s), " \
           "0 left out" in done.stdout
    assert f"{FILE}: 2" in done.stdout and f"{SECOND}: 2" in done.stdout
    assert PLACE_TEST not in done.stdout, "a test is never a file of the set"


def test_a_ledger_over_intent_material_short_one_fact_is_refused(project):
    entries = [{"at": f"orders.md:{line_of(MATERIAL, 'opened')}", "node": NODE}]
    done = run("--ledger", ledger_at(project, entries), project / "specs")
    assert done.returncode == 1
    assert "no entry — «Every fact line of the material lands in a node" in done.stdout


def test_an_adoption_over_intent_material_routes_each_governed_file(project):
    ledger = ledger_at(project)
    workspace = project / "ws-intent"
    done = run("--stage", project / "backend", project / "specs", "intent-orders", workspace,
               "--adopt", "--ledger", ledger)
    assert done.returncode == 0, done.stdout + done.stderr
    manifest = json.loads((workspace / "manifest.json").read_text(encoding="utf-8"))
    assert sorted(manifest["files"]) == [SECOND, FILE], "the file no fact governs is not judged"
    assert manifest["files"][FILE]["also"] == sorted([NODE, OTHER])
    assert manifest["files"][SECOND]["also"] == sorted([OTHER, RULE])
    assert not any(given.endswith(".spec.ts") for given in manifest["files"])
    pack = Path(manifest["files"][FILE]["pack"]).read_text(encoding="utf-8")
    assert f"=== {NODE}" in pack and f"=== {RULE}" not in pack
