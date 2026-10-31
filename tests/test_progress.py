"""The progress line is read from disk alone, one segment per live initiative (SPEC-009).

Each test builds a consumer repository under git — the fixture plan and delivery under the roots a
`siegard.json` declares — and runs `progress.py` the way a status line setting does: the harness's
record on stdin, naming the working directory. One test per phase of R3, the log's last line, two
initiatives, a closed one, and the silences of R4.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from conftest import derive_plan

REPO = Path(__file__).resolve().parent.parent
BIN = REPO / "src/claude/bin"
SLUG = "s"
RECORDED = "task/checkout/record-order"
READY = "task/checkout/bill-order"


def line(start: Path, *, by: str = "stdin") -> subprocess.CompletedProcess:
    if by == "stdin":
        record = json.dumps({"cwd": str(start), "workspace": {"current_dir": str(start)}})
        return subprocess.run([sys.executable, "-B", str(BIN / "progress.py")], input=record,
                              capture_output=True, text=True)
    return subprocess.run([sys.executable, "-B", str(BIN / "progress.py"), str(start)],
                          input="", capture_output=True, text=True)


def printed(start: Path) -> str:
    result = line(start)
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    assert len(result.stdout.splitlines()) <= 1, "the progress line is one line"
    return result.stdout.strip()


@pytest.fixture
def project(tmp_path, root, work, delivery, target, sound_delivery):
    """A live plan of two tasks; the first delivered and proven, the second not."""
    home = tmp_path
    (home / "plans").mkdir()
    shutil.move(str(work), str(home / "plans" / SLUG))
    (home / "deliveries").mkdir()
    shutil.move(str(delivery), str(home / "deliveries" / SLUG))
    (target / "siegard.json").unlink()
    (home / "siegard.json").write_text(json.dumps({
        "specification_root": "specification", "targets": {"app": "target"},
        "work_root": "plans", "delivery_root": "deliveries"}), encoding="utf-8")
    subprocess.run(["git", "-C", str(home), "init", "-q"], check=True)
    derive_plan(home / "plans" / SLUG, root)
    return home


def record(home: Path, kind: str, task: str) -> None:
    source = home / "deliveries" / SLUG / kind / f"{RECORDED[5:]}.md"
    path = home / "deliveries" / SLUG / kind / f"{task[5:]}.md"
    path.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


def review(home: Path, *tasks: str) -> None:
    path = home / "deliveries" / SLUG / "review" / "first.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("---\n" + yaml.safe_dump({"tasks": list(tasks)}) + "---\n", encoding="utf-8")


def test_a_plan_with_a_task_left_reads_delivery(project):
    assert printed(project) == f"{SLUG} · task 1/2 delivered · phase delivery"


def test_the_working_directory_may_be_anywhere_in_the_project(project):
    assert printed(project / "target" / "tests").startswith(f"{SLUG} · task 1/2")
    by_argument = line(project / "plans", by="argument")
    assert by_argument.stdout.strip().startswith(f"{SLUG} · task 1/2")


def test_no_plan_yet_reads_plan(project):
    (project / "plans" / "refunds").mkdir()
    assert f"refunds · phase plan" in printed(project)


def test_every_task_delivered_and_one_unproven_reads_proof(project):
    record(project, "implementation", READY)
    assert printed(project) == f"{SLUG} · task 2/2 delivered · phase proof"


def test_every_task_proven_and_none_reviewed_reads_review(project):
    record(project, "implementation", READY)
    record(project, "proof", READY)
    review(project, RECORDED)
    assert printed(project) == f"{SLUG} · task 2/2 delivered · phase review"


def test_every_task_reviewed_reads_reviewed(project):
    record(project, "implementation", READY)
    record(project, "proof", READY)
    review(project, RECORDED, READY)
    assert printed(project) == f"{SLUG} · task 2/2 delivered · phase reviewed"


def test_the_last_line_of_the_orchestration_log_is_shown_and_cut(project):
    log = project / "deliveries" / SLUG / "orchestration.md"
    log.write_text("- plan — 1a2b3c — planned two tasks\n- stop: blocking — " + "x" * 200 + "\n\n",
                   encoding="utf-8")
    shown = printed(project)
    assert " · last: stop: blocking — x" in shown
    assert shown.endswith("…")
    assert len(shown.split(" · last: ")[1]) == 80


def test_two_live_initiatives_share_the_line_and_a_closed_one_is_left_out(project):
    (project / "plans" / "refunds").mkdir()
    (project / "plans" / "archive-me").mkdir()
    (project / "plans" / "archive-me" / "closure.md").write_text("Closed.\n", encoding="utf-8")
    shown = printed(project)
    assert shown == f"refunds · phase plan | {SLUG} · task 1/2 delivered · phase delivery"


def test_outside_a_siegard_project_the_line_is_empty(tmp_path):
    (tmp_path / "elsewhere").mkdir()
    subprocess.run(["git", "-C", str(tmp_path / "elsewhere"), "init", "-q"], check=True)
    assert printed(tmp_path / "elsewhere") == ""
    assert printed(tmp_path / "no-such-directory") == ""


def test_a_project_with_nothing_live_or_nothing_readable_is_empty(project):
    (project / "plans" / SLUG / "closure.md").write_text("Closed.\n", encoding="utf-8")
    assert printed(project) == ""
    (project / "siegard.json").write_text("{not json", encoding="utf-8")
    assert printed(project) == ""
