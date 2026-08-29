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
AUTHORED_RULES = PROJECT_PY.resolve().parent.parent.parent / "consumer/CLAUDE.md"


def run(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(PROJECT_PY), *map(str, args)],
                          capture_output=True, text=True)


@pytest.fixture
def consumer(tmp_path: Path) -> Path:
    """A consumer repository: a git toplevel holding a target source root beneath it, with the
    current rules placed at its root the way every install places them — so that everything below
    exercises its own field in silence, and the drift report is exercised where it is the
    subject."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, capture_output=True)
    (tmp_path / "backend").mkdir()
    (tmp_path / "CLAUDE.md").write_bytes(AUTHORED_RULES.read_bytes())
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


# ------------------------------------------------------- the rules the root carries

SHIPPED_VERSION = json.loads(
    (PROJECT_PY.resolve().parent.parent / ".claude-plugin/plugin.json")
    .read_text(encoding="utf-8"))["version"]


def test_current_rules_pass_in_silence(consumer):
    """The fixture places the rules every install places; a report on the green path would be a
    line every consumer reads on every invocation and learns to skip."""
    declare(consumer, {})
    done = run(consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "rules:" not in done.stdout


def test_absent_rules_are_reported_with_the_placement_ready(consumer):
    (consumer / "CLAUDE.md").unlink()
    declare(consumer, {"standard": None})
    done = run(consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert f"rules: {consumer / 'CLAUDE.md'} does not exist" in done.stdout
    assert f"cp {AUTHORED_RULES} {consumer / 'CLAUDE.md'}" in done.stdout
    assert "standard: declared none" in done.stdout, "the report displaced a field; it precedes them"


def test_unmarked_rules_are_reported_without_a_clobbering_command(consumer):
    """A root CLAUDE.md a project wrote before adopting the framework, or one whose marker was
    edited away: the report names the current copy and says to keep what the project added — a
    ready `cp` here would be an instruction to destroy the consumer's own rules."""
    (consumer / "CLAUDE.md").write_text("# My project\n\nHouse rules.\n", encoding="utf-8")
    declare(consumer, {"standard": None})
    done = run(consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "carries no Siegard version" in done.stdout
    assert str(AUTHORED_RULES) in done.stdout
    assert "keep anything the project added" in done.stdout
    assert "cp " not in done.stdout


def test_rules_from_another_release_report_both_versions(consumer):
    stale = project.RULES_MARKER.sub("These rules ship with Siegard 0.0.1",
                                     AUTHORED_RULES.read_text(encoding="utf-8"))
    (consumer / "CLAUDE.md").write_text(stale, encoding="utf-8")
    declare(consumer, {"standard": None})
    done = run(consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "says Siegard 0.0.1" in done.stdout
    assert f"this framework is {SHIPPED_VERSION}" in done.stdout


def test_the_drift_report_never_refuses(consumer):
    """Stale rules and a broken declaration at once: the declaration's refusal stands, the drift
    line still prints, and neither gates the other."""
    (consumer / "CLAUDE.md").unlink()
    declare(consumer, {"standrd": "standards/backend.yaml"})
    done = run(consumer / "backend")
    assert done.returncode == 1
    assert "rules:" in done.stdout
    assert "standrd" in done.stdout
