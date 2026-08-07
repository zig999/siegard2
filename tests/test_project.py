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


def test_a_file_declaring_nothing_is_refused(repo):
    declare(repo, {})
    done = run(repo / "backend")
    assert done.returncode == 1
    assert "'standard' is a required property" in done.stdout


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
