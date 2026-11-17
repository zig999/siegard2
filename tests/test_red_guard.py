"""`deliver.py --red-guard`: a proof-only re-delivery that goes on as the task's re-delivery holds
its implementer to the tests already in the tree (SPEC-004 R32).

Each consumer is a git repository with one committed baseline. The test author's file is pending
when the hold runs, as it is in the invocation; what changes after the hold is the implementer's.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
DELIVER = REPO / "src" / "claude" / "bin" / "deliver.py"


def git(home: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(home), "-c", "user.email=t@t", "-c", "user.name=t", *args],
                   check=True, capture_output=True)


def put(path: Path, text: str = "x\n") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def guard(verb: str, target: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(DELIVER), "--red-guard", verb, str(target)],
                          capture_output=True, text=True)


@pytest.fixture
def consumer(tmp_path: Path) -> Path:
    home = tmp_path / "consumer"
    put(home / "siegard.json", json.dumps({
        "specification_root": "knowledge", "work_root": "work", "delivery_root": "delivery",
        "telemetry_root": "telemetry", "targets": {"backend": "backend"},
        "tests": {"backend": [{"under": "tests", "suffix": ".ts", "nested": True}]}}))
    put(home / "backend" / "src" / "load-error.ts", "export const a = 1;\n")
    put(home / "backend" / "tests" / "jornadas" / "other-task.test.ts", "journey\n")
    put(home / "backend" / "tests" / "unidade" / "failures.test.ts", "old\n")
    git(home, "init", "-q")
    git(home, "add", "-A")
    git(home, "commit", "-qm", "base")
    put(home / "backend" / "tests" / "unidade" / "failures.test.ts", "written by the test author\n")
    put(home / "backend" / "tests" / "unidade" / "new-proof.test.ts", "new test\n")
    return home


def test_a_source_fix_with_the_held_tests_untouched_is_accepted(consumer):
    target = consumer / "backend"
    assert guard("hold", target).returncode == 0
    put(target / "src" / "load-error.ts", "export const a = 2;\n")
    put(target / "src" / "resource-type.ts", "export const b = 1;\n")
    checked = guard("check", target)
    assert checked.returncode == 0, checked.stdout + checked.stderr
    assert checked.stdout.startswith("accepts:")


def test_another_tasks_test_edited_after_the_hold_is_refused_and_restored(consumer):
    target = consumer / "backend"
    guard("hold", target)
    put(target / "tests" / "jornadas" / "other-task.test.ts", "journey edited\n")
    put(target / "src" / "load-error.ts", "export const a = 2;\n")
    checked = guard("check", target)
    assert checked.returncode == 1
    assert "changed test: tests/jornadas/other-task.test.ts" in checked.stdout
    assert "src/load-error.ts" not in checked.stdout
    restored = guard("restore", target)
    assert restored.returncode == 0
    assert (target / "tests" / "jornadas" / "other-task.test.ts").read_text() == "journey\n"
    assert (target / "src" / "load-error.ts").read_text() == "export const a = 2;\n"
    assert guard("check", target).returncode == 0


def test_the_test_authors_own_test_edited_after_the_hold_is_put_back_as_held(consumer):
    target = consumer / "backend"
    guard("hold", target)
    put(target / "tests" / "unidade" / "failures.test.ts", "weakened\n")
    checked = guard("check", target)
    assert checked.returncode == 1
    assert "changed test: tests/unidade/failures.test.ts" in checked.stdout
    guard("restore", target)
    assert (target / "tests" / "unidade" / "failures.test.ts").read_text() == \
        "written by the test author\n"


def test_a_test_added_or_deleted_after_the_hold_is_refused_and_undone(consumer):
    target = consumer / "backend"
    guard("hold", target)
    put(target / "tests" / "support" / "helper.ts", "helper\n")
    (target / "tests" / "unidade" / "new-proof.test.ts").unlink()
    (target / "tests" / "jornadas" / "other-task.test.ts").unlink()
    checked = guard("check", target)
    assert checked.returncode == 1
    for path in ("tests/support/helper.ts", "tests/unidade/new-proof.test.ts",
                 "tests/jornadas/other-task.test.ts"):
        assert f"changed test: {path}" in checked.stdout
    guard("restore", target)
    assert not (target / "tests" / "support" / "helper.ts").exists()
    assert (target / "tests" / "unidade" / "new-proof.test.ts").read_text() == "new test\n"
    assert (target / "tests" / "jornadas" / "other-task.test.ts").read_text() == "journey\n"
    assert guard("check", target).returncode == 0


def test_the_hold_lives_under_the_git_directory_and_check_needs_one(consumer):
    target = consumer / "backend"
    refused = guard("check", target)
    assert refused.returncode == 2 and "no hold" in refused.stderr
    guard("hold", target)
    assert (consumer / ".git" / "siegard" / "red-guard.json").is_file()
    status = subprocess.run(["git", "-C", str(consumer), "status", "--porcelain"],
                            capture_output=True, text=True).stdout
    assert "red-guard" not in status
