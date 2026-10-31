"""`project.py` — the one reader of `siegard.json`: finds it at the git toplevel, holds it
to its contract, and prints what was declared without ever deciding in its place."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

import project

PROJECT_PY = Path(project.__file__)
SHIPPED_RULES = PROJECT_PY.resolve().parent.parent / "hooks/rules.md"


def run(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(PROJECT_PY), *map(str, args)],
                          capture_output=True, text=True)


@pytest.fixture
def consumer(tmp_path: Path) -> Path:
    """A consumer repository: a git toplevel holding a target source root beneath it and no root
    `CLAUDE.md` — the rules arrive by the plugin's hooks, so this is what every install looks
    like, and everything below exercises its own field in silence."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, capture_output=True)
    (tmp_path / "backend").mkdir()
    return tmp_path


def declare(consumer: Path, content) -> Path:
    target = consumer / "siegard.json"
    target.write_text(content if isinstance(content, str) else json.dumps(content),
                      encoding="utf-8")
    return target


def test_a_declared_standard_resolves_at_the_toplevel(consumer):
    (consumer / "standards").mkdir()
    (consumer / "standards/backend.yaml").write_text("rules: []\n", encoding="utf-8")
    declare(consumer, {"standard": "standards/backend.yaml"})
    done = run(consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert f"standard: {consumer / 'standards/backend.yaml'}" in done.stdout


def test_declared_none_is_a_full_answer(consumer):
    declare(consumer, {"standard": None})
    done = run(consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "standard: declared none" in done.stdout


def test_no_file_declares_nothing_and_is_not_a_defect(consumer):
    done = run(consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "no project file" in done.stdout
    assert str(consumer / "siegard.json") in done.stdout


def test_an_unknown_key_is_refused_rather_than_silenced(consumer):
    declare(consumer, {"standrd": "standards/backend.yaml"})
    done = run(consumer / "backend")
    assert done.returncode == 1
    assert "standrd" in done.stdout


def test_a_file_declaring_nothing_prints_nothing(consumer):
    """No field is required — a project mid-setup may have declared none of them yet, and that
    is a different fact from having decided against one: only `standard: null` says the latter."""
    declare(consumer, {})
    done = run(consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert done.stdout.strip() == ""


def test_a_declaration_that_outlived_its_registry_is_refused(consumer):
    declare(consumer, {"standard": "standards/gone.yaml"})
    done = run(consumer / "backend")
    assert done.returncode == 1
    assert "which does not exist" in done.stdout


def test_malformed_json_is_refused_verbatim(consumer):
    declare(consumer, "{not json")
    done = run(consumer / "backend")
    assert done.returncode == 1
    assert "does not parse as JSON" in done.stdout


def test_without_git_the_directory_itself_holds_the_file(tmp_path):
    target = tmp_path / "tree"
    target.mkdir()
    (target / "siegard.json").write_text(json.dumps({"standard": None}), encoding="utf-8")
    done = run(target)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "standard: declared none" in done.stdout


def test_a_missing_directory_cannot_run(tmp_path):
    done = run(tmp_path / "absent")
    assert done.returncode == 2
    assert "is not a directory" in done.stderr


# ------------------------------------------------------- a standard per target


def registry(consumer: Path, name: str) -> str:
    (consumer / "standards").mkdir(exist_ok=True)
    (consumer / f"standards/{name}.yaml").write_text("rules: []\n", encoding="utf-8")
    return f"standards/{name}.yaml"


TWO_TARGETS = {"backend": "backend", "frontend": "frontend"}


def test_a_standard_per_target_prints_one_line_per_target(consumer):
    back, front = registry(consumer, "backend"), registry(consumer, "frontend")
    declare(consumer, {"targets": TWO_TARGETS, "standard": {"backend": back, "frontend": front}})
    done = run(consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    lines = done.stdout.splitlines()
    assert f"standard backend: {consumer / back}" in lines
    assert f"standard frontend: {consumer / front}" in lines
    assert "standard:" not in done.stdout


def test_null_per_target_is_that_targets_full_answer(consumer):
    back = registry(consumer, "backend")
    declare(consumer, {"targets": TWO_TARGETS, "standard": {"backend": back, "frontend": None}})
    done = run(consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "standard frontend: declared none" in done.stdout
    assert f"standard backend: {consumer / back}" in done.stdout


def test_a_target_the_object_lacks_prints_no_line_for_it(consumer):
    """An entry the object lacks declares nothing for that target — the calling skill's stop,
    exactly as an absent field is, and never this script's to fill from the other entry."""
    back = registry(consumer, "backend")
    declare(consumer, {"targets": TWO_TARGETS, "standard": {"backend": back}})
    done = run(consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "standard frontend" not in done.stdout


def test_a_standard_keyed_by_a_target_nobody_declared_is_refused(consumer):
    back = registry(consumer, "backend")
    declare(consumer, {"targets": {"backend": "backend"}, "standard": {"backend": back, "web": back}})
    done = run(consumer / "backend")
    assert done.returncode == 1
    assert "standard names web, which targets does not declare" in done.stdout


def test_one_registry_over_two_targets_is_refused_with_the_declaration_ready(consumer):
    """The case that motivated the shape: a two-stack project whose bare `standard` named the
    backend registry, so every frontend invocation had to override it by hand and any that
    forgot got the wrong registry silently — the structural check passes on it, because two npm
    packages hold the same manifest names. The refusal is here, with the fix ready to paste."""
    back = registry(consumer, "backend")
    declare(consumer, {"targets": TWO_TARGETS, "standard": back})
    done = run(consumer / "backend")
    assert done.returncode == 1
    assert "a standard governs one target" in done.stdout
    assert "/siegard-config" in done.stdout
    assert "Standard for backend:" in done.stdout
    assert "Standard for frontend:" in done.stdout


def test_one_registry_over_one_target_still_stands(consumer):
    back = registry(consumer, "backend")
    declare(consumer, {"targets": {"backend": "backend"}, "standard": back})
    done = run(consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert f"standard: {consumer / back}" in done.stdout


def test_null_over_two_targets_still_stands(consumer):
    """`null` names no registry, so it answers wrongly for nobody: none, for every target."""
    declare(consumer, {"targets": TWO_TARGETS, "standard": None})
    done = run(consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "standard: declared none" in done.stdout


def test_a_per_target_registry_that_does_not_exist_is_refused(consumer):
    back = registry(consumer, "backend")
    declare(consumer, {"targets": TWO_TARGETS,
                       "standard": {"backend": back, "frontend": "standards/gone.yaml"}})
    done = run(consumer / "backend")
    assert done.returncode == 1
    assert "standard frontend names" in done.stdout
    assert "which does not exist" in done.stdout


def test_an_absolute_per_target_registry_is_refused(consumer):
    back = registry(consumer, "backend")
    declare(consumer, {"targets": TWO_TARGETS,
                       "standard": {"backend": back, "frontend": str(consumer / back)}})
    done = run(consumer / "backend")
    assert done.returncode == 1
    assert "standard.frontend" in done.stdout
    assert "is absolute" in done.stdout


def test_an_empty_standard_object_is_refused(consumer):
    declare(consumer, {"targets": TWO_TARGETS, "standard": {}})
    assert run(consumer / "backend").returncode == 1


# ------------------------------------------------------- the roots beyond standard


def test_a_declared_specification_root_resolves_at_the_toplevel(consumer):
    declare(consumer, {"standard": None, "specification_root": "specs"})
    done = run(consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert f"specification_root: {consumer / 'specs'}" in done.stdout


def test_declared_targets_resolve_sorted_by_name(consumer):
    declare(consumer, {"standard": None,
                   "targets": {"frontend": "frontend", "backend": "backend"}})
    done = run(consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    lines = done.stdout.splitlines()
    assert f"target backend: {consumer / 'backend'}" in lines
    assert f"target frontend: {consumer / 'frontend'}" in lines
    assert lines.index(f"target backend: {consumer / 'backend'}") < \
        lines.index(f"target frontend: {consumer / 'frontend'}")


def test_declared_work_and_delivery_roots_resolve(consumer):
    declare(consumer, {"standard": None, "work_root": "work", "delivery_root": "delivery"})
    done = run(consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert f"work_root: {consumer / 'work'}" in done.stdout
    assert f"delivery_root: {consumer / 'delivery'}" in done.stdout


def test_a_field_not_declared_prints_no_line_for_it(consumer):
    """Absence is the calling skill's stop to raise, never this script's to guess around — so a
    field this file does not declare must not appear at all, not even as an empty answer."""
    declare(consumer, {"standard": None})
    done = run(consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    for absent in ("specification_root:", "target ", "work_root:", "delivery_root:"):
        assert absent not in done.stdout


def test_a_target_name_that_will_not_reduce_is_refused(consumer):
    declare(consumer, {"standard": None, "targets": {"Backend Service": "backend"}})
    done = run(consumer / "backend")
    assert done.returncode == 1
    assert "targets" in done.stdout


def test_every_root_declared_resolves_together(consumer):
    declare(consumer, {"standard": None, "specification_root": "specs",
                   "targets": {"backend": "backend"}, "work_root": "work",
                   "delivery_root": "delivery"})
    done = run(consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    for expected in (f"specification_root: {consumer / 'specs'}", f"target backend: {consumer / 'backend'}",
                     f"work_root: {consumer / 'work'}", f"delivery_root: {consumer / 'delivery'}"):
        assert expected in done.stdout


def test_targets_a_person_edits_by_hand_are_reported(consumer):
    """`edits_freely` is read by `trace.py` from this same file, so what this script owes is the
    same thing it owes every other field: saying what stands, once, where a reader can see it."""
    declare(consumer, {"targets": {"backend": "backend", "web": "web"}, "edits_freely": ["web"]})
    done = run(consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "edits_freely: web" in done.stdout


def test_a_project_declaring_no_freely_edited_target_says_nothing_about_it(consumer):
    """Absence declares nothing here, exactly as it does for every other field: a project that
    has not got to this question is not a project that answered it."""
    declare(consumer, {"targets": {"backend": "backend"}})
    done = run(consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "edits_freely" not in done.stdout


def test_a_freely_edited_key_the_contract_refuses(consumer):
    declare(consumer, {"targets": {"backend": "backend"}, "edits_freely": ["Not A Slug"]})
    assert run(consumer / "backend").returncode == 1


def test_telemetry_root_prints_resolved_like_every_other_root(consumer):
    """The one root nothing the framework builds or delivers ever reads. It prints from here so
    that `/siegard-telemetry` finds the reports where the project said they live, never where a
    session chose."""
    declare(consumer, {"telemetry_root": "telemetry"})
    done = run(consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert f"telemetry_root: {consumer / 'telemetry'}" in done.stdout


def test_an_absolute_telemetry_root_is_refused(consumer):
    declare(consumer, {"telemetry_root": "/var/telemetry"})
    done = run(consumer / "backend")
    assert done.returncode == 1
    assert "telemetry_root: /var/telemetry is absolute" in done.stdout


# ------------------------------------------------------- a root copy of the rules

SHIPPED_VERSION = json.loads(
    (PROJECT_PY.resolve().parent.parent / ".claude-plugin/plugin.json")
    .read_text(encoding="utf-8"))["version"]


def test_no_root_rules_is_the_green_path(consumer):
    """The hooks place the rules; a root holding none is every install, and a report there would
    be a line every consumer reads on every invocation and learns to skip."""
    declare(consumer, {})
    done = run(consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "rules:" not in done.stdout


def test_a_projects_own_root_rules_are_not_reported(consumer):
    """A root CLAUDE.md the project wrote for itself carries no marker and is nobody's copy."""
    (consumer / "CLAUDE.md").write_text("# My project\n\nHouse rules.\n", encoding="utf-8")
    declare(consumer, {"standard": None})
    done = run(consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "rules:" not in done.stdout


def test_a_root_copy_of_the_current_rules_is_reported_as_a_copy(consumer):
    """The same rules loaded twice: the report names the file and asks for the Siegard portion
    to go, never with a command — the file may carry rules the project added."""
    (consumer / "CLAUDE.md").write_bytes(SHIPPED_RULES.read_bytes())
    declare(consumer, {"standard": None})
    done = run(consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert f"rules: {consumer / 'CLAUDE.md'} carries the Siegard {SHIPPED_VERSION} rules" in done.stdout
    assert "keep anything the project added" in done.stdout
    assert "cp " not in done.stdout and "rm " not in done.stdout
    assert "standard: declared none" in done.stdout, "the report displaced a field; it precedes them"


def test_a_root_copy_from_another_release_names_both_versions(consumer):
    stale = project.RULES_MARKER.sub("These rules ship with Siegard 0.0.1",
                                     SHIPPED_RULES.read_text(encoding="utf-8"))
    (consumer / "CLAUDE.md").write_text(stale, encoding="utf-8")
    declare(consumer, {"standard": None})
    done = run(consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "carries the Siegard 0.0.1 rules" in done.stdout
    assert f"place the {SHIPPED_VERSION} rules" in done.stdout


def test_the_copy_report_never_refuses(consumer):
    """A root copy and a broken declaration at once: the declaration's refusal stands, the rules
    line still prints, and neither gates the other."""
    (consumer / "CLAUDE.md").write_bytes(SHIPPED_RULES.read_bytes())
    declare(consumer, {"standrd": "standards/backend.yaml"})
    done = run(consumer / "backend")
    assert done.returncode == 1
    assert "rules:" in done.stdout
    assert "standrd" in done.stdout


# ------------------------------------------------------------------------------ tests

SPEC_TS = {"under": "src", "suffix": ".spec.ts", "nested": True}


def test_declared_tests_print_one_line_per_target_in_their_parts(consumer):
    declare(consumer, {"targets": {"backend": "backend"},
                       "tests": {"backend": [SPEC_TS, {"under": "test", "suffix": ".ts"}]}})
    done = run(consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert ("tests backend: under src, suffix .spec.ts, nested; under test, suffix .ts"
            in done.stdout)


def test_tests_keyed_by_a_target_nobody_declared_is_refused(consumer):
    """A scope under a key `targets` lacks reaches no file, and every test it was written for
    would go on counting unsurveyed with nothing saying why."""
    declare(consumer, {"targets": {"backend": "backend"}, "tests": {"frontend": [SPEC_TS]}})
    done = run(consumer / "backend")
    assert done.returncode == 1
    assert "tests names frontend, which targets does not declare" in done.stdout


def test_a_test_scope_is_held_to_the_parts_a_rule_scope_admits(consumer):
    declare(consumer, {"targets": {"backend": "backend"},
                       "tests": {"backend": [{"under": "src", "suffix": ".ts", "glob": "**"}]}})
    done = run(consumer / "backend")
    assert done.returncode == 1
    assert "glob" in done.stdout


def test_no_tests_declared_prints_no_tests_line(consumer):
    declare(consumer, {"targets": {"backend": "backend"}})
    done = run(consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert not [line for line in done.stdout.splitlines() if line.startswith("tests ")]


# ------------------------------------ which named paths are declared tests (SPEC-004 R24)

def declaring(consumer: Path, **extra) -> None:
    declare(consumer, {"targets": {"backend": "backend"}, **extra})


def test_declared_tests_says_which_named_paths_are_tests(consumer):
    """«A build red whose fix lies only in files the project declares as its tests is answered by
    the delivery's test author, before the implementation record is written» (SPEC-004 R24): which
    paths those are is this match, never a reading of a directory's name."""
    declaring(consumer, tests={"backend": [{"under": "tests", "suffix": ".ts", "nested": True}]})
    done = run(consumer, "--declared-tests", "backend", "tests/contract/party/individual.test.ts",
               "src/modules/party/individual/individual.routes.ts", "tests/fixture.json")
    assert done.returncode == 0, done.stderr
    assert "declared test: tests/contract/party/individual.test.ts" in done.stdout
    assert "not a declared test: src/modules/party/individual/individual.routes.ts" in done.stdout
    assert "not a declared test: tests/fixture.json" in done.stdout
    assert "1 of 3 named path(s) are tests backend declares" in done.stdout
    assert "target backend:" not in done.stdout, "the query prints its answer, not the fields"


def test_a_target_declaring_no_tests_answers_that_none_is_one(consumer):
    declaring(consumer)
    done = run(consumer, "--declared-tests", "backend", "tests/a.test.ts")
    assert done.returncode == 0, done.stderr
    assert "tests backend: declared none" in done.stdout
    assert "declared test: tests/a.test.ts" not in done.stdout


@pytest.mark.parametrize("args", [
    ("--declared-tests", "frontend", "tests/a.test.ts"),
    ("--declared-tests", "backend", "/abs/tests/a.test.ts"),
    ("--declared-tests", "backend", "../tests/a.test.ts"),
    ("--declared-tests", "backend"),
])
def test_declared_tests_cannot_run_over_what_it_cannot_answer(consumer, args):
    declaring(consumer, tests={"backend": [{"under": "tests", "suffix": ".ts", "nested": True}]})
    assert run(consumer, *args).returncode == 2


def test_declared_tests_still_holds_the_file_to_its_contract(consumer):
    declare(consumer, {"targets": {"backend": "backend"}, "tests": {"frontend": []}})
    assert run(consumer, "--declared-tests", "backend", "tests/a.test.ts").returncode == 1
