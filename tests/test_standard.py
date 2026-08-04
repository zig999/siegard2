"""A project's standard is held to its contract, and the scope matcher is held to its semantics.

The matcher is the part worth testing hardest. A scope is stated in parts — a directory, an ending,
and whether it reaches below — rather than as a glob pattern, because in Python 3.12 neither
`PurePath.match` nor `fnmatch` gives what a reader expects: the first treats a double star as
exactly one directory, the second lets a single star cross a separator. Either would decide whether
a finding is refused, so the semantics are pinned here rather than borrowed.

The example registry under `src/standards/` is exercised as a real fixture. It is not distributed —
Siegard ships the slot and the enforcement, never the content — and until this module existed
nothing read it at all.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator

import deliver

REPO = Path(__file__).resolve().parent.parent
EXAMPLE = REPO / "src/standards/backend-typescript.yaml"


@pytest.fixture(scope="module")
def contract() -> Draft202012Validator:
    return deliver.standard_contract()


# ------------------------------------------------------------------- the contract


def test_the_contract_carries_its_own_worked_example(contract):
    schema = json.loads((REPO / "src/claude/schemas/standard.json").read_text(encoding="utf-8"))
    examples = schema.get("examples", [])
    assert len(examples) == 1, "the contract is one worked example, not none and not several"
    assert [e.message for e in contract.iter_errors(examples[0])] == []
    rules = examples[0]["rules"]
    assert {r["decided_by"] for r in rules} == {"reading", "tool"}, \
        "the example must show both halves; a contract that only shows one teaches only one"


def test_the_example_registry_holds_together(contract):
    data, problems = deliver.load_standard(EXAMPLE, contract)
    assert problems == [], f"{EXAMPLE.name}: {problems}"
    assert data is not None


def test_the_example_registry_parses_as_yaml():
    """A description holding an unquoted `: ` is not a description — it is a mapping the loader
    refuses, and the file never loads at all."""
    assert isinstance(yaml.safe_load(EXAMPLE.read_text(encoding="utf-8")), dict)


def test_the_example_registry_states_no_domain_fact(contract):
    """The contract's first exclusion, checked the only way prose can be: a status code or an
    error code written into a rule's statement is a fact the base owns, and a standard holding one
    would put two review passes in contradiction over the same line."""
    data, _ = deliver.load_standard(EXAMPLE, contract)
    import re
    status = re.compile(r"\b(200|201|204|400|401|403|404|409|422|429|500)\b")
    code = re.compile(r"\b[A-Z][A-Z_]{6,}\b")
    offenders = [r["id"] for r in data["rules"]
                 if status.search(r["statement"]) or code.search(r["statement"])]
    assert offenders == [], \
        f"{offenders} state what the system answers; that belongs to the knowledge base, and the " \
        f"registry's own `elsewhere` section says so"


def test_a_tool_rule_names_what_decides_it(contract):
    data, _ = deliver.load_standard(EXAMPLE, contract)
    for rule in data["rules"]:
        if rule["decided_by"] == "tool":
            assert rule.get("tool"), f"{rule['id']} is a tool's and names none"
        else:
            assert "tool" not in rule, f"{rule['id']} is a reading and names a tool"


def test_both_halves_are_populated(contract):
    """Half of a real registry being a tool's is the finding that shaped this design. A registry
    where everything is a reading is one that re-implements a linter in a model."""
    data, _ = deliver.load_standard(EXAMPLE, contract)
    reading = [r for r in data["rules"] if r["decided_by"] == "reading"]
    tool = [r for r in data["rules"] if r["decided_by"] == "tool"]
    assert reading and tool
    assert len(tool) >= len(data["rules"]) // 4, \
        "a registry with almost nothing left to a tool has not been triaged"


# ------------------------------------------------------------------ what it refuses


def broken(tmp_path: Path, data: dict) -> Path:
    path = tmp_path / "broken.yaml"
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return path


def base(**overrides) -> dict:
    from conftest import STANDARD
    return {**STANDARD, **overrides}


def test_two_rules_under_one_id(tmp_path, contract):
    one = base()["rules"][0]
    data, problems = deliver.load_standard(broken(tmp_path, base(rules=[one, dict(one)])),
                                           contract)
    assert data is None
    assert any("cannot be told apart by the finding that cites it" in p for p in problems)


def test_a_reading_rule_that_names_a_tool(tmp_path, contract):
    rule = {**base()["rules"][0], "tool": "lint"}
    data, problems = deliver.load_standard(broken(tmp_path, base(rules=[rule])), contract)
    assert data is None
    assert any("is one or the other" in p for p in problems)


def test_a_missing_registry_is_a_problem_not_an_empty_one(tmp_path, contract):
    data, problems = deliver.load_standard(tmp_path / "nowhere.yaml", contract)
    assert data is None and any("does not exist" in p for p in problems)


def test_a_registry_that_does_not_parse(tmp_path, contract):
    path = tmp_path / "bad.yaml"
    path.write_text("rules: [\n", encoding="utf-8")
    data, problems = deliver.load_standard(path, contract)
    assert data is None and any("cannot be read" in p for p in problems)


# ------------------------------------------------------------------- the scope matcher


@pytest.mark.parametrize("scope, path, expected", [
    # a scope that reaches below its directory
    ({"under": "src", "suffix": ".ts", "nested": True}, "src/a.ts", True),
    ({"under": "src", "suffix": ".ts", "nested": True}, "src/a/b/c.ts", True),
    # and one that does not — this is the case a single star gets wrong
    ({"under": "src", "suffix": ".ts"}, "src/a.ts", True),
    ({"under": "src", "suffix": ".ts"}, "src/a/b.ts", False),
    # a role and an extension together
    ({"under": "src", "suffix": ".service.ts", "nested": True},
     "src/orders/order.service.ts", True),
    ({"under": "src", "suffix": ".service.ts", "nested": True},
     "src/orders/order.controller.ts", False),
    # a deeper directory, which is the case a double star gets wrong
    ({"under": "src/config", "suffix": ".ts"}, "src/config/env.ts", True),
    ({"under": "src/config", "suffix": ".ts"}, "src/config/db/pool.ts", False),
    ({"under": "src/__tests__", "suffix": ".ts", "nested": True},
     "src/__tests__/unit/a/b.ts", True),
    # outside the directory entirely
    ({"under": "src", "suffix": ".ts", "nested": True}, "tests/a.ts", False),
    ({"under": "src", "suffix": ".ts", "nested": True}, "srcx/a.ts", False),
    # a trailing separator is tolerated rather than made a second way to write one thing
    ({"under": "src/", "suffix": ".ts", "nested": True}, "src/a/b.ts", True),
    # a shape the schema already reported never matches
    ({"under": "src"}, "src/a.ts", False),
    ("src/**", "src/a.ts", False),
])
def test_a_scope_reaches_exactly_what_it_says(scope, path, expected):
    assert deliver.reaches(scope, path) is expected


def test_every_scope_in_the_example_reaches_something_plausible(contract):
    """A scope that reaches nothing under its own project is a scope nobody can have meant."""
    data, _ = deliver.load_standard(EXAMPLE, contract)
    candidates = ["src/orders/place.ts", "src/orders/order.service.ts",
                  "src/orders/order.controller.ts", "src/orders/order.repository.ts",
                  "src/routes/order.routes.ts", "src/dto/create-order.dto.ts",
                  "src/types/pagination.ts", "src/config/env.ts", "src/factories/order.factory.ts",
                  "src/middleware/error.middleware.ts", "src/clients/billing.ts",
                  "src/migrations/001-orders.ts", "src/orders/place.spec.ts",
                  "src/__tests__/unit/place.ts"]
    for rule in data["rules"]:
        assert deliver.in_scope(rule, candidates), \
            f"{rule['id']} reaches none of an ordinary tree's paths; its scope is unusable"


# -------------------------------------------------------------------- the subcommand


def invoke(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(REPO / "src/claude/bin/deliver.py"), *args],
                          capture_output=True, text=True)


def test_the_subcommand_checks_a_registry_and_reports_the_split():
    done = invoke("--standard", str(EXAMPLE))
    assert done.returncode == 0, done.stderr
    assert "decided by reading" in done.stdout and "by a tool" in done.stdout
    assert "pin sha256:" in done.stdout, \
        "the pin is printed so a reviewer can put it in the record by hand"


def test_the_subcommand_refuses_a_registry_that_does_not_hold(tmp_path):
    one = base()["rules"][0]
    done = invoke("--standard", str(broken(tmp_path, base(rules=[one, dict(one)]))))
    assert done.returncode == 1
    assert "A review is never checked against a standard that does not hold together" in done.stdout


def test_the_subcommand_stands_alone(tmp_path):
    done = invoke("--standard", str(EXAMPLE), "--check", str(tmp_path))
    assert done.returncode == 2
    assert "stands alone" in done.stderr


def test_the_subcommand_needs_a_file():
    done = invoke("--standard")
    assert done.returncode == 2
    assert "--standard takes a file" in done.stderr


def test_a_path_under_standards_is_reported_as_material(tmp_path):
    """`--node` pointed at the copy a review took must say what it is, the way it does for a run —
    reporting "the path computes to no identifier" over material is reporting a problem where
    there is none."""
    delivery, work = tmp_path / "delivery", tmp_path / "work"
    (delivery / "standards").mkdir(parents=True)
    work.mkdir()
    copy = delivery / "standards" / "backend.yaml"
    copy.write_text(EXAMPLE.read_text(encoding="utf-8"), encoding="utf-8")
    done = invoke("--node", str(copy), str(delivery), str(work), str(tmp_path))
    assert done.returncode == 0, done.stderr + done.stdout
    assert "never validated as a node" in done.stdout


def test_the_example_is_not_distributed():
    """Siegard ships the slot and the enforcement, never the content."""
    assert not (REPO / "dist/.claude/standards").exists()
    assert EXAMPLE.is_file() and "src/claude" not in EXAMPLE.as_posix()
