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

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator

import deliver
import project

REPO = Path(__file__).resolve().parent.parent
EXAMPLE = REPO / "src/standards/backend-node-service.yaml"


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


SAMPLES = sorted((REPO / "src/standards").glob("*.yaml"))


def test_the_sample_directory_is_not_empty():
    """The guard below is parametrized over a glob, and a glob that matches nothing passes in
    silence. If the samples ever move, this is what says so."""
    assert SAMPLES, "src/standards holds no registry; the sample guard lost its subject"


@pytest.mark.parametrize("sample", SAMPLES, ids=lambda p: p.stem)
def test_every_sample_registry_holds_to_the_contract(sample, contract):
    """Every registry under `src/standards/`, not only the one the rest of this module reads. These
    are worked examples a consumer copies, so one that stopped holding would teach the wrong shape —
    and nothing read them at all until this test was parametrized, which left two of the three
    unchecked whenever the contract moved."""
    data, problems = deliver.load_standard(sample, contract)
    assert problems == [], f"{sample.name}: {problems}"
    assert data is not None


@pytest.mark.parametrize("sample", SAMPLES, ids=lambda p: p.stem)
def test_the_sample_readme_quotes_the_pin_each_registry_actually_computes_to(sample):
    """`src/standards/README.md` quotes `deliver.py --standard`'s real output over these files,
    and a quoted figure is a second home for a value the file itself holds. The pin is the one
    line of that block that moves whenever a registry is edited, and it moved twice without the
    quote following, so this reads it back: the elided form the README prints, against the digest
    the registry computes to now."""
    readme = (REPO / "src/standards/README.md").read_text(encoding="utf-8")
    digest = hashlib.sha256(sample.read_bytes()).hexdigest()
    elided = f"sha256:{digest[:8]}…{digest[-8:]}"
    assert elided in readme, (f"{sample.name} computes to {elided} and the README quotes another "
                              f"pin for it; the quoted output is not what the command prints")


def test_the_example_registry_parses_as_yaml():
    """A description holding an unquoted `: ` is not a description — it is a mapping the loader
    refuses, and the file never loads at all."""
    assert isinstance(yaml.safe_load(EXAMPLE.read_text(encoding="utf-8")), dict)


def test_the_example_registry_states_no_domain_fact(contract):
    """The contract's first exclusion, checked the only way prose can be: a status code or an
    error code written into a rule's statement is a fact the specification owns, and a standard
    holding one would put two review passes in contradiction over the same line."""
    data, _ = deliver.load_standard(EXAMPLE, contract)
    import re
    status = re.compile(r"\b(200|201|204|400|401|403|404|409|422|429|500)\b")
    code = re.compile(r"\b[A-Z][A-Z_]{6,}\b")
    offenders = [r["id"] for r in data["rules"]
                 if status.search(r["statement"]) or code.search(r["statement"])]
    assert offenders == [], \
        f"{offenders} state what the system answers; that belongs to the specification, and the " \
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
    assert project.reaches(scope, path) is expected


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


def test_a_declared_test_is_scoped_in_the_parts_a_rule_is():
    """`siegard.json`'s `tests` and a rule's `applies_to` are read by one `project.reaches`, so
    the two contracts must state the same parts: a property one admitted and the other refused
    would be a scope one file accepts and the matcher reads as the other's."""
    standard = json.loads((REPO / "src/claude/schemas/standard.json").read_text(encoding="utf-8"))
    declared = json.loads((REPO / "src/claude/schemas/project.json").read_text(encoding="utf-8"))
    assert declared["$defs"]["scope"] == standard["$defs"]["scope"]


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


def test_the_subcommand_says_how_many_rules_rest_on_each_step():
    """The one thing this framework can do about a step that decides nothing. It cannot read a
    stack, so it cannot tell a linter with no rule loaded for the files it read from one deciding
    every rule resting on it — both exit 0. What it can do is show the weight at the moment
    somebody is in a position to check it: a number beside each step, and a sentence saying that
    exit 0 is the whole of what a green step settles."""
    done = invoke("--standard", str(EXAMPLE))
    assert done.returncode == 0, done.stderr
    data = yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))
    tools = [r["tool"] for r in data["rules"] if r.get("tool")]
    for step in sorted(set(tools)):
        assert f"{step} ({tools.count(step)} rule(s))" in done.stdout, done.stdout
    assert "a step deciding nothing passes exactly like one deciding all of them" in done.stdout


def test_a_registry_with_no_tool_rule_claims_nothing_about_a_green_step(tmp_path):
    """The sentence is printed where it is true and nowhere else: a registry every rule of which is
    decided by reading has no step carrying anything, so there is no weight to show."""
    one = {**base()["rules"][0], "decided_by": "reading"}
    one.pop("tool", None)
    reading_only = base(rules=[one],
                        dependencies=[{"package": "pino", "why": "the project logs through it."}])
    done = invoke("--standard", str(broken(tmp_path, reading_only)))
    assert done.returncode == 0, done.stderr
    assert "named nothing" in done.stdout
    assert "passes exactly like one deciding all of them" not in done.stdout


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


def test_the_example_is_not_distributed():
    """Siegard ships the slot and the enforcement, never the content."""
    assert not (REPO / "dist/.claude/standards").exists()
    assert EXAMPLE.is_file() and "src/claude" not in EXAMPLE.as_posix()


# --------------------------------------------------- what a registry presupposes

def presupposing(tmp_path: Path, **entry) -> Path:
    """A registry that presupposes one artifact, written where a tree can be held against it."""
    return broken(tmp_path, base(presupposes=[{
        "path": "package.json",
        "provides": "the `lint` step PRH-01 is decided by.",
        "rules": ["PRH-01"], **entry}]))


def test_a_presupposition_citing_a_rule_the_registry_does_not_declare(tmp_path, contract):
    """The same discipline a finding is held to: an absence is stated with what it costs, and a
    cost naming a rule nobody declares is a cost nobody can weigh."""
    data, problems = deliver.load_standard(presupposing(tmp_path, rules=["ZZZ-99"]), contract)
    assert data is None
    assert any("a cost nobody can weigh" in p for p in problems)


def test_a_registry_that_presupposes_nothing_says_so(tmp_path):
    """A registry declaring none says which of the two silences it is: nothing to check, rather
    than nothing checked. Every sample under src/standards presupposes something, which is why
    this one is written here instead of read from there."""
    done = invoke("--standard", str(broken(tmp_path, base())))
    assert done.returncode == 0, done.stderr
    assert "none needs one to exist first" in done.stdout


def test_an_absent_artifact_is_refused_and_named_with_what_it_costs(tmp_path):
    """The refusal this whole field exists for. Exit 1 before a single file is written, naming the
    artifact and every rule that cannot be applied while it is missing."""
    tree = tmp_path / "tree"
    tree.mkdir()
    done = invoke("--standard", str(presupposing(tmp_path)), "--against", str(tree))
    assert done.returncode == 1, done.stdout
    assert "package.json: ABSENT" in done.stdout
    assert "unanswerable while it is: PRH-01" in done.stdout, \
        "an absence reported without the rules it takes with it says nothing a reader can weigh"
    assert "declares it in `produces`" in done.stdout, \
        "a stop names the way out, and this one's is a task that builds the artifact"


def test_an_artifact_that_stands_is_reported_as_standing(tmp_path):
    tree = tmp_path / "tree"
    tree.mkdir()
    (tree / "package.json").write_text("{}", encoding="utf-8")
    done = invoke("--standard", str(presupposing(tmp_path)), "--against", str(tree))
    assert done.returncode == 0, done.stdout
    assert "stands, and PRH-01 can be applied" in done.stdout


def test_a_registry_presupposing_nothing_holds_against_any_tree(tmp_path):
    tree = tmp_path / "tree"
    tree.mkdir()
    done = invoke("--standard", str(broken(tmp_path, base())), "--against", str(tree))
    assert done.returncode == 0, done.stdout
    assert "holds everything it needs to" in done.stdout


def test_against_says_which_tree_and_needs_one(tmp_path):
    assert invoke("--standard", str(EXAMPLE), "--against").returncode == 2
    done = invoke("--standard", str(EXAMPLE), "--against", str(tmp_path / "nowhere"))
    assert done.returncode == 2
    assert "is not a directory" in done.stderr


def test_against_holds_a_standard_and_nothing_else(tmp_path):
    """Only a standard is held against a tree; --against on a root would read as a check nobody
    wrote, and a flag that silently does nothing is worse than one that refuses."""
    done = invoke("--against", str(tmp_path), str(tmp_path), str(tmp_path))
    assert done.returncode == 2
    assert "only --standard holds one" in done.stderr


def test_every_sample_registry_states_what_it_presupposes():
    """The samples are the worked examples a consumer copies, and every one of them is a registry
    for a stack that has to be set up before a single rule applies. One that declared nothing would
    teach exactly the silence this field was added to end."""
    for sample in SAMPLES:
        data = yaml.safe_load(sample.read_text(encoding="utf-8"))
        assert data.get("presupposes"), \
            f"{sample.name} presupposes nothing, and every rule in it is a condition over a file " \
            f"that some manifest or compiler configuration had to exist first for"


# ------------------------------------ what a registry authorizes, and how it is run

def test_a_tool_rule_with_no_command_is_refused(tmp_path, contract):
    """The join the whole reading/tool split rests on. PRH-01 says `lint` decides it; a registry
    declaring commands and not that one has a rule nothing can apply — which the contract's own
    `tool` field already calls worse than a rule nobody wrote."""
    data, problems = deliver.load_standard(broken(tmp_path, base(commands=[
        {"step": "install", "command": "true", "timeout_seconds": 60, "role": "install"}])), contract)
    assert data is None
    assert any("declares no such command" in p for p in problems)


def test_a_registry_declaring_no_command_is_held_to_none_of_it(tmp_path, contract):
    """The condition that keeps this additive: a registry from before the field still holds, and
    PRH-01's `lint` goes unanswered the way it always did rather than becoming a refusal."""
    without = {k: v for k, v in base().items() if k not in ("commands", "dependencies")}
    data, problems = deliver.load_standard(broken(tmp_path, without), contract)
    assert problems == [], problems
    assert data is not None


def test_two_commands_under_one_step(tmp_path, contract):
    data, problems = deliver.load_standard(broken(tmp_path, base(commands=[
        {"step": "lint", "command": "a", "timeout_seconds": 60},
        {"step": "lint", "command": "b", "timeout_seconds": 60}])), contract)
    assert data is None
    assert any("cannot both be it" in p for p in problems)


def test_two_steps_carrying_one_role(tmp_path, contract):
    """Which step installs is not something a caller may pick at the moment of running."""
    data, problems = deliver.load_standard(broken(tmp_path, base(commands=[
        {"step": "lint", "command": "a", "timeout_seconds": 60},
        {"step": "one", "command": "b", "timeout_seconds": 60, "role": "install"},
        {"step": "two", "command": "c", "timeout_seconds": 60, "role": "install"}])), contract)
    assert data is None
    assert any("all carry the role `install`" in p for p in problems)


def test_a_package_authorized_twice(tmp_path, contract):
    data, problems = deliver.load_standard(broken(tmp_path, base(dependencies=[
        {"package": "pino", "why": "one reason."},
        {"package": "pino", "why": "another."}])), contract)
    assert data is None
    assert any("cannot both be the reason it was admitted" in p for p in problems)


def test_a_package_citing_a_rule_the_registry_does_not_declare(tmp_path, contract):
    data, problems = deliver.load_standard(broken(tmp_path, base(dependencies=[
        {"package": "pino", "why": "because.", "rules": ["ZZZ-99"]}])), contract)
    assert data is None
    assert any("dependencies[0] names ZZZ-99" in p for p in problems)


def test_a_registry_may_authorize_packages_and_own_no_install(tmp_path, contract):
    """The split working: where a project holds several registries, one owns the manifest and the
    others own the steps their own rules are decided by. A registry naming only the steps it
    decides rules by, and no install role at all, is a legitimate shape a consumer may still
    reach for even though no sample under src/standards/ is written that way today — refusing
    it would make that split unrepresentable."""
    data, problems = deliver.load_standard(broken(tmp_path, base(commands=[
        {"step": "lint", "command": "npm run lint", "timeout_seconds": 60}])), contract)
    assert problems == [], problems
    assert data is not None


def test_the_subcommand_prints_the_commands_and_the_packages():
    done = invoke("--standard", str(EXAMPLE))
    assert done.returncode == 0, done.stderr
    assert "it declares 5 command(s)" in done.stdout
    assert "installs with install" in done.stdout, \
        "backend-node-service owns the manifest for its own stack, and saying which step " \
        "installs is how a caller learns it does not need a registry beside it for that"
    assert "it authorizes 11 direct dependency(ies)" in done.stdout
    assert "transitively is nobody's approval" in done.stdout, \
        "the limit is stated where a reader meets it rather than left out"


def test_each_printed_command_carries_its_own_bound():
    """The timeout beside each command, because it was the one fact a caller composing a run still
    had to open the registry for — the steps, the roles and the packages were all printed, and one
    missing number sent every invocation back to the whole file."""
    done = invoke("--standard", str(EXAMPLE))
    assert done.returncode == 0, done.stderr
    data = yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))
    for command in data["commands"]:
        assert f"{command['step']} = {command['command']} ({command['timeout_seconds']}s)" \
            in done.stdout, f"the step {command['step']} prints without its bound"


def test_the_subcommand_composes_each_phase_for_the_runner():
    """The prose rule — everything except the suite, install first — was interpreted anew at
    every delivery, and one omitted install cost a full build to learn what a printed line says
    for free. The phases print composed for bin/run.py, by the same selection the validator
    holds the captured run to, so composed and owed cannot drift apart."""
    import shlex
    done = invoke("--standard", str(EXAMPLE))
    assert done.returncode == 0, done.stderr
    commands = yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))["commands"]
    install = [c for c in commands if c.get("role") == "install"]
    middle = [c for c in commands if c.get("role") not in ("prepare", "install", "suite")]
    suite = [c for c in commands if c.get("role") == "suite"]

    def line(phase: str, steps: list[dict]) -> str:
        largest = max(c["timeout_seconds"] for c in steps)
        return f"{phase}: --timeout-seconds {largest} " + " ".join(
            "--step " + shlex.quote(f"{c['step']}={c['command']}") for c in steps)

    for phase, steps in (("setup", install), ("build", install + middle),
                         ("suite", install + middle + suite)):
        assert line(phase, steps) in done.stdout, \
            f"the {phase} phase does not print composed in the order it runs"
    assert "a task declaring `produces` runs the setup line" in done.stdout, \
        "the substrate exemption is stated beside the lines it bends"


def test_a_registry_with_no_install_role_composes_an_empty_setup(tmp_path):
    """A phase whose role no step carries says nothing runs, rather than going unmentioned —
    a missing line reads as a line the caller should derive, which is the habit this replaces."""
    registry = broken(tmp_path, base(commands=[
        {"step": "lint", "command": "npm run lint", "timeout_seconds": 60}]))
    done = invoke("--standard", str(registry))
    assert done.returncode == 0, done.stdout + done.stderr
    assert "setup: nothing runs — no step carries the role this phase needs" in done.stdout
    assert "build: --timeout-seconds 60 --step 'lint=npm run lint'" in done.stdout


def test_every_sample_registry_declares_how_it_is_run():
    """Every sample is a registry for a stack that has to be installed and checked. One declaring
    no command would teach the silence that left twenty-four tool-decided rules unanswered."""
    for sample in SAMPLES:
        data = yaml.safe_load(sample.read_text(encoding="utf-8"))
        assert data.get("commands"), f"{sample.name} declares no command"
        assert data.get("dependencies"), f"{sample.name} authorizes no package"


def test_the_refusal_hands_over_the_invocation(tmp_path):
    """A stop is a door, not a wall: the refusal over an absent presupposed artifact ends with
    the /plan-work invocation filled with everything this command already knows, leaving only
    the two roots the caller alone can name."""
    tree = tmp_path / "tree"
    tree.mkdir()
    registry = presupposing(tmp_path)
    done = invoke("--standard", str(registry), "--against", str(tree))
    assert done.returncode == 1, done.stdout
    assert "/plan-work" in done.stdout
    assert "package.json" in done.stdout
    assert f"Target source root: {tree}" in done.stdout
    assert f"Project standard: {registry}" in done.stdout
    assert "Work root: <" in done.stdout, \
        "what this command cannot know stays a named slot, never a guess"


# -------------------------------------------------------------- what a step decides


def deciding(tmp_path: Path, decides: list[str]) -> Path:
    """The base registry with one more step, holding the tree to the constraints named."""
    commands = list(base().get("commands") or [
        {"step": "lint", "command": "true", "timeout_seconds": 60},
        {"step": "test", "command": "true", "timeout_seconds": 60, "role": "suite"}])
    commands.insert(1, {"step": "boundaries", "command": "true", "timeout_seconds": 60,
                        "decides": decides})
    return broken(tmp_path, base(commands=commands))


def constrained(tmp_path: Path, *slugs: str) -> Path:
    """A specification root holding exactly the constraints named and nothing else — existence is
    the whole of what `--specification` reads, so nothing else needs to stand."""
    root = tmp_path / "spec"
    (root / "constraints").mkdir(parents=True)
    for slug in slugs:
        (root / "constraints" / f"{slug}.md").write_text(
            "---\nstatement: One condition over the implementation.\nscope: system\n---\n\n"
            "## Description\n\nNone.\n", encoding="utf-8")
    return root


def test_a_step_may_declare_the_constraints_it_decides(tmp_path, contract):
    """The join the constraint side rests on, and the canary for the field: before `decides`
    existed this registry was refused by the command's closed shape."""
    data, problems = deliver.load_standard(
        deciding(tmp_path, ["constraints/asynchronous-events"]), contract)
    assert problems == [], problems
    assert data["commands"][1]["decides"] == ["constraints/asynchronous-events"]


def test_a_decides_entry_outside_constraints_is_refused(tmp_path, contract):
    """A step decides an Architecture Constraint and nothing of another class: a rule is a
    conformance test's, a scenario an acceptance test's, and neither is a command's to hold."""
    data, problems = deliver.load_standard(deciding(tmp_path, ["rules/sales/order-total"]), contract)
    assert data is None
    assert any("decides" in p for p in problems), problems


def test_the_contract_example_decides_a_constraint(contract):
    """The worked example carries one, so an author sees the shape without reading the schema."""
    example = contract.schema["examples"][0]
    assert any(c.get("decides") for c in example["commands"])


def test_decides_is_resolved_against_the_specification(tmp_path):
    """Both halves of the report: the step that decides, and the constraint no step decides —
    the second is the list of constraints held by reading alone, said rather than left out."""
    root = constrained(tmp_path, "asynchronous-events", "domain-imports-nothing")
    done = invoke("--standard", str(deciding(tmp_path, ["constraints/asynchronous-events"])),
                  "--specification", str(root))
    assert done.returncode == 0, done.stdout
    assert "boundaries decides constraints/asynchronous-events" in done.stdout
    assert "no step decides constraints/domain-imports-nothing: held by reading alone" \
        in done.stdout


def test_a_decides_naming_a_constraint_the_specification_does_not_hold_is_refused(tmp_path):
    root = constrained(tmp_path, "asynchronous-events")
    done = invoke("--standard", str(deciding(tmp_path, ["constraints/never-written"])),
                  "--specification", str(root))
    assert done.returncode == 1, done.stdout
    assert "decides constraints/never-written, which" in done.stdout
    assert "does not hold" in done.stdout
    assert "1 `decides` reference(s) do not resolve" in done.stdout


def test_decides_without_a_specification_says_who_resolves_it(tmp_path):
    """Alone, the registry check cannot resolve a constraint — the same honesty `presupposes` has
    without `--against`: count it, and name the flag that answers."""
    done = invoke("--standard", str(deciding(tmp_path, ["constraints/asynchronous-events"])))
    assert done.returncode == 0, done.stdout
    assert "1 constraint reference(s) in `decides`, unresolved here" in done.stdout
    assert "--specification <root> resolves them" in done.stdout


def test_a_registry_deciding_nothing_still_names_what_is_held_by_reading(tmp_path):
    """A registry from before the field, held against a specification with constraints: every one
    of them is held by reading alone, and the check says so rather than staying silent."""
    root = constrained(tmp_path, "asynchronous-events")
    done = invoke("--standard", str(broken(tmp_path, base())), "--specification", str(root))
    assert done.returncode == 0, done.stdout
    assert "no step decides constraints/asynchronous-events: held by reading alone" in done.stdout


def test_a_specification_holding_no_constraint_is_said(tmp_path):
    root = tmp_path / "spec"
    (root / "domain").mkdir(parents=True)
    done = invoke("--standard", str(broken(tmp_path, base())), "--specification", str(root))
    assert done.returncode == 0, done.stdout
    assert "holds no constraint" in done.stdout


def test_specification_holds_a_standard_and_nothing_else(tmp_path):
    done = invoke("--specification", str(tmp_path), str(tmp_path), str(tmp_path))
    assert done.returncode == 2
    assert "only --standard holds one" in done.stderr
    nowhere = invoke("--standard", str(EXAMPLE), "--specification", str(tmp_path / "nowhere"))
    assert nowhere.returncode == 2
    assert "is not a directory" in nowhere.stderr


def reach(target, write_standard, *paths):
    import subprocess
    import sys
    ref = write_standard()
    args = [a for each in paths for a in ("--for", each)]
    return subprocess.run(
        [sys.executable, "-B", str(REPO / "src/claude/bin/deliver.py"), "--standard",
         str(target / ref["at"]), "--reach", *args], capture_output=True, text=True)


def test_reach_says_per_path_which_rules_reach_it_apart_by_what_decides_them(target,
                                                                           write_standard):
    result = reach(target, write_standard, "src/a.ts")
    assert result.returncode == 0, result.stderr
    assert "src/a.ts: reading ARC-01; tool PRH-01" in result.stdout


def test_reach_names_every_path_no_rule_reaches_and_how_many_that_is(target, write_standard):
    result = reach(target, write_standard, "src/a.ts", "README.md", "notes/b.md")
    assert result.returncode == 0, result.stderr
    assert "reached by no rule: 2 of 3" in result.stdout
    assert "  README.md" in result.stdout and "  notes/b.md" in result.stdout
    assert "  src/a.ts" not in result.stdout


def test_reach_over_a_set_every_rule_reaches_reports_none_unreached(target, write_standard):
    result = reach(target, write_standard, "src/a.ts")
    assert "reached by no rule: 0 of 1" in result.stdout


def test_reach_needs_a_path_and_stands_with_nothing_else(target, write_standard):
    assert reach(target, write_standard).returncode == 2
    import subprocess
    import sys
    ref = write_standard()
    mixed = subprocess.run(
        [sys.executable, "-B", str(REPO / "src/claude/bin/deliver.py"), "--standard",
         str(target / ref["at"]), "--reach", "--reading", "--for", "src/a.ts"],
        capture_output=True, text=True)
    assert mixed.returncode == 2


def test_reach_refuses_a_registry_that_does_not_hold_together(tmp_path):
    import subprocess
    import sys
    broken = tmp_path / "standard.yaml"
    broken.write_text("rules: []\n", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-B", str(REPO / "src/claude/bin/deliver.py"), "--standard",
         str(broken), "--reach", "--for", "src/a.ts"], capture_output=True, text=True)
    assert result.returncode == 1


def test_reading_is_unchanged_by_reach_existing(target, write_standard):
    """What a reading judgment is handed is JSON the judge pastes whole; --reach prints beside it
    and never into it."""
    import subprocess
    import sys
    ref = write_standard()
    out = subprocess.run(
        [sys.executable, "-B", str(REPO / "src/claude/bin/deliver.py"), "--standard",
         str(target / ref["at"]), "--reading", "--for", "src/a.ts"], capture_output=True, text=True)
    assert out.returncode == 0
    assert json.loads(out.stdout)


# ------------------------------------ which rules run before a task's tests exist (SPEC-007 R4)

@pytest.mark.parametrize("one, other, expected", [
    ({"under": "tests", "suffix": ".ts", "nested": True},
     {"under": "tests/contract", "suffix": ".ts", "nested": True}, True),
    ({"under": "tests/contract", "suffix": ".ts"},
     {"under": "tests", "suffix": ".ts", "nested": True}, True),
    ({"under": "tests", "suffix": ".ts"},
     {"under": "tests/contract", "suffix": ".ts"}, False),
    ({"under": "src", "suffix": ".ts", "nested": True},
     {"under": "tests", "suffix": ".ts", "nested": True}, False),
    ({"under": "tests", "suffix": ".json", "nested": True},
     {"under": "tests", "suffix": ".ts", "nested": True}, False),
    ({"under": "tests", "suffix": ".test.ts", "nested": True},
     {"under": "tests", "suffix": ".ts", "nested": True}, True),
    ({"under": ".", "suffix": ".ts", "nested": True},
     {"under": "tests", "suffix": ".ts", "nested": True}, True),
])
def test_two_scopes_meet_where_some_path_is_reached_by_both(one, other, expected):
    assert project.scopes_meet(one, other) is expected
    assert project.scopes_meet(other, one) is expected


def declaring_tests(tmp_path: Path, rules: list[dict]) -> tuple[Path, Path]:
    """A git toplevel declaring its tests under `tests`, a target beneath it, and a registry."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, capture_output=True)
    (tmp_path / "backend").mkdir()
    (tmp_path / "siegard.json").write_text(json.dumps({
        "targets": {"backend": "backend"},
        "tests": {"backend": [{"under": "tests", "suffix": ".ts", "nested": True}]}}),
        encoding="utf-8")
    return broken(tmp_path, base(rules=rules)), tmp_path / "backend"


def tool_rule(rule_id: str, tool: str, *scopes: dict) -> dict:
    return {"id": rule_id, "statement": "A condition a step decides.",
            "because": "A departure goes unseen.", "decided_by": "tool", "tool": tool,
            "applies_to": list(scopes)}


def test_a_rule_a_build_step_decides_over_the_tests_is_named_and_refused_nowhere(tmp_path):
    """«A rule decided by a step other than the one whose role is `suite` holds over a tree that
    holds no test of the task being delivered» (SPEC-007 R4). Whether a rule requires a test to
    exist is a reading — a scope cannot say — so the check names the rules whose scope meets the
    declared tests and exits as it would without them."""
    registry, target = declaring_tests(tmp_path, [
        tool_rule("TST-07", "lint", {"under": "src/modules", "suffix": ".routes.ts", "nested": True},
                  {"under": "tests/contract", "suffix": ".ts", "nested": True}),
        tool_rule("PRH-01", "lint", {"under": "src", "suffix": ".ts", "nested": True}),
        tool_rule("STK-11", "test", {"under": "tests", "suffix": ".ts", "nested": True}),
        tool_rule("STK-16", "lint", {"under": "tests", "suffix": ".json", "nested": True})])
    done = invoke("--standard", str(registry), "--against", str(target))
    assert done.returncode == 0, done.stdout + done.stderr
    line = next(l for l in done.stdout.splitlines() if "a step other than the suite" in l)
    assert "1 rule(s)" in line and "TST-07" in line
    for absent in ("PRH-01", "STK-11", "STK-16"):
        assert absent not in line, line
    assert "«a rule that requires a test file to exist names the `suite` step» (SPEC-007 R4)" \
        in line


def test_a_project_declaring_no_tests_draws_no_line(tmp_path):
    """Nothing says which files are tests, so nothing is said about which rules reach them."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, capture_output=True)
    (tmp_path / "backend").mkdir()
    (tmp_path / "siegard.json").write_text(json.dumps({"targets": {"backend": "backend"}}),
                                           encoding="utf-8")
    registry = broken(tmp_path, base(rules=[
        tool_rule("PRH-01", "lint", {"under": "tests", "suffix": ".ts", "nested": True})]))
    done = invoke("--standard", str(registry), "--against", str(tmp_path / "backend"))
    assert done.returncode == 0, done.stdout + done.stderr
    assert "a step other than the suite" not in done.stdout
