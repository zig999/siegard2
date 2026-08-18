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


def run(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(PROJECT_PY), *map(str, args)],
                          capture_output=True, text=True)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A consumer repository: a git toplevel holding a target source root beneath it."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, capture_output=True)
    (tmp_path / "backend").mkdir()
    return tmp_path


def declare(repo: Path, content) -> Path:
    target = repo / "siegard.json"
    target.write_text(content if isinstance(content, str) else json.dumps(content),
                      encoding="utf-8")
    return target


def test_a_declared_standard_resolves_at_the_toplevel(repo):
    (repo / "standards").mkdir()
    (repo / "standards/backend.yaml").write_text("rules: []\n", encoding="utf-8")
    declare(repo, {"standard": "standards/backend.yaml"})
    done = run(repo / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert f"standard: {repo / 'standards/backend.yaml'}" in done.stdout


def test_declared_none_is_a_full_answer(repo):
    declare(repo, {"standard": None})
    done = run(repo / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "standard: declared none" in done.stdout


def test_no_file_declares_nothing_and_is_not_a_defect(repo):
    done = run(repo / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "no project file" in done.stdout
    assert str(repo / "siegard.json") in done.stdout


def test_an_unknown_key_is_refused_rather_than_silenced(repo):
    declare(repo, {"standrd": "standards/backend.yaml"})
    done = run(repo / "backend")
    assert done.returncode == 1
    assert "standrd" in done.stdout


def test_a_file_declaring_nothing_prints_nothing(repo):
    """No field is required — a project mid-setup may have declared none of them yet, and that
    is a different fact from having decided against one: only `standard: null` says the latter."""
    declare(repo, {})
    done = run(repo / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert done.stdout.strip() == ""


def test_a_declaration_that_outlived_its_registry_is_refused(repo):
    declare(repo, {"standard": "standards/gone.yaml"})
    done = run(repo / "backend")
    assert done.returncode == 1
    assert "which does not exist" in done.stdout


def test_malformed_json_is_refused_verbatim(repo):
    declare(repo, "{not json")
    done = run(repo / "backend")
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


# ------------------------------------------------------- the roots beyond standard


def test_a_declared_specification_root_resolves_at_the_toplevel(repo):
    declare(repo, {"standard": None, "specification_root": "specs"})
    done = run(repo / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert f"specification_root: {repo / 'specs'}" in done.stdout


def test_declared_targets_resolve_sorted_by_name(repo):
    declare(repo, {"standard": None,
                   "targets": {"frontend": "frontend", "backend": "backend"}})
    done = run(repo / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    lines = done.stdout.splitlines()
    assert f"target backend: {repo / 'backend'}" in lines
    assert f"target frontend: {repo / 'frontend'}" in lines
    assert lines.index(f"target backend: {repo / 'backend'}") < \
        lines.index(f"target frontend: {repo / 'frontend'}")


def test_declared_work_and_delivery_roots_resolve(repo):
    declare(repo, {"standard": None, "work_root": "work", "delivery_root": "delivery"})
    done = run(repo / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert f"work_root: {repo / 'work'}" in done.stdout
    assert f"delivery_root: {repo / 'delivery'}" in done.stdout


def test_a_field_not_declared_prints_no_line_for_it(repo):
    """Absence is the calling skill's stop to raise, never this script's to guess around — so a
    field this file does not declare must not appear at all, not even as an empty answer."""
    declare(repo, {"standard": None})
    done = run(repo / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    for absent in ("specification_root:", "target ", "work_root:", "delivery_root:"):
        assert absent not in done.stdout


def test_a_target_name_that_will_not_reduce_is_refused(repo):
    declare(repo, {"standard": None, "targets": {"Backend Service": "backend"}})
    done = run(repo / "backend")
    assert done.returncode == 1
    assert "targets" in done.stdout


def test_every_root_declared_resolves_together(repo):
    declare(repo, {"standard": None, "specification_root": "specs",
                   "targets": {"backend": "backend"}, "work_root": "work",
                   "delivery_root": "delivery"})
    done = run(repo / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    for expected in (f"specification_root: {repo / 'specs'}", f"target backend: {repo / 'backend'}",
                     f"work_root: {repo / 'work'}", f"delivery_root: {repo / 'delivery'}"):
        assert expected in done.stdout


def test_targets_a_person_edits_by_hand_are_reported(repo):
    """`edits_freely` is read by `trace.py` from this same file, so what this script owes is the
    same thing it owes every other field: saying what stands, once, where a reader can see it."""
    declare(repo, {"targets": {"backend": "backend", "web": "web"}, "edits_freely": ["web"]})
    done = run(repo / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "edits_freely: web" in done.stdout


def test_a_project_declaring_no_freely_edited_target_says_nothing_about_it(repo):
    """Absence declares nothing here, exactly as it does for every other field: a project that
    has not got to this question is not a project that answered it."""
    declare(repo, {"targets": {"backend": "backend"}})
    done = run(repo / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "edits_freely" not in done.stdout


def test_a_freely_edited_key_the_contract_refuses(repo):
    declare(repo, {"targets": {"backend": "backend"}, "edits_freely": ["Not A Slug"]})
    assert run(repo / "backend").returncode == 1
