"""The progress line is read from disk alone, one segment per live initiative (SPEC-009).

Each test builds a consumer repository under git — the fixture plan and delivery under the roots a
`siegard.json` declares — and runs `progress.py` the way a status line setting does: the harness's
record on stdin, naming the working directory. One test per phase of R3, the log's last line, two
initiatives, a closed one, and the silences of R4; then the setting R5 writes and removes, and the
version note R6 adds, each read against a Claude Code configuration directory of the test's own.
"""
from __future__ import annotations

import json
import os
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


@pytest.fixture(autouse=True)
def config(tmp_path_factory, monkeypatch) -> Path:
    """A Claude Code configuration directory of the test's own, holding no plugin record unless
    the test writes one, so the machine's installed plugins never reach the line."""
    where = tmp_path_factory.mktemp("claude-config")
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(where))
    return where


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


SCRIPT = BIN / "progress.py"
VERSION = json.loads((BIN.parent / ".claude-plugin" / "plugin.json").read_text())["version"]


def settings_of(home: Path) -> Path:
    return home / ".claude" / "settings.local.json"


def change(flag: str, home: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(SCRIPT), flag, str(home)],
                          capture_output=True, text=True)


def installed(config: Path, *entries: dict) -> None:
    (config / "plugins").mkdir(exist_ok=True)
    (config / "plugins" / "installed_plugins.json").write_text(json.dumps(
        {"version": 2, "plugins": {"siegard@siegard-generator": list(entries),
                                   "other@elsewhere": [{"scope": "user", "installPath": "/x"}]}}),
        encoding="utf-8")


def test_install_writes_the_entry_whose_command_prints_the_line(project):
    done = change("--install", project)
    assert done.returncode == 0, done.stderr
    assert done.stdout.startswith(f"added: statusLine in {settings_of(project)}")
    assert "--uninstall" in done.stdout and "run this again after one" in done.stdout
    entry = json.loads(settings_of(project).read_text())["statusLine"]
    assert entry == {"type": "command", "command": f"python3 -B {SCRIPT}"}
    record = json.dumps({"cwd": str(project), "workspace": {"current_dir": str(project)}})
    drawn = subprocess.run(["sh", "-c", entry["command"]], input=record, capture_output=True,
                           text=True, cwd="/")
    assert drawn.stdout.strip() == f"{SLUG} · task 1/2 delivered · phase delivery"


def test_install_merges_and_every_other_key_stands(project):
    settings_of(project).parent.mkdir()
    held = {"permissions": {"allow": ["Bash(ls:*)"]}, "env": {"A": "1"}}
    settings_of(project).write_text(json.dumps(held), encoding="utf-8")
    assert change("--install", project).returncode == 0
    written = json.loads(settings_of(project).read_text())
    assert list(written) == ["permissions", "env", "statusLine"]
    assert {k: written[k] for k in held} == held
    again = change("--install", project)
    assert again.returncode == 0 and again.stdout.startswith("unchanged:")


def test_install_replaces_its_own_entry_from_another_version_and_refuses_a_foreign_one(project):
    settings_of(project).parent.mkdir()
    old = {"type": "command",
           "command": "python3 -B '/cache/siegard generator/siegard/1.0.0/bin/progress.py'"}
    settings_of(project).write_text(json.dumps({"statusLine": old}), encoding="utf-8")
    done = change("--install", project)
    assert done.returncode == 0 and done.stdout.startswith("replaced:")
    assert json.loads(settings_of(project).read_text())["statusLine"]["command"] \
        == f"python3 -B {SCRIPT}"
    foreign = json.dumps({"statusLine": {"type": "command", "command": "~/my-line.sh"}})
    settings_of(project).write_text(foreign, encoding="utf-8")
    refused = change("--install", project)
    assert refused.returncode == 1 and refused.stdout.startswith("refused:")
    assert "my-line.sh" in refused.stdout
    assert settings_of(project).read_text() == foreign


def test_install_never_rewrites_a_file_that_does_not_parse_or_a_project_without_siegard(project,
                                                                                       tmp_path):
    settings_of(project).parent.mkdir()
    settings_of(project).write_text("{broken", encoding="utf-8")
    done = change("--install", project)
    assert done.returncode == 2 and "does not parse" in done.stderr
    assert settings_of(project).read_text() == "{broken"
    (tmp_path / "bare").mkdir()
    bare = change("--install", tmp_path / "bare")
    assert bare.returncode == 2 and "siegard.json" in bare.stderr
    assert not settings_of(tmp_path / "bare").exists()


def test_uninstall_removes_only_its_own_entry(project):
    settings_of(project).parent.mkdir()
    settings_of(project).write_text(json.dumps({"env": {"A": "1"}}), encoding="utf-8")
    assert change("--install", project).returncode == 0
    done = change("--uninstall", project)
    assert done.returncode == 0 and done.stdout.startswith("removed:")
    assert json.loads(settings_of(project).read_text()) == {"env": {"A": "1"}}
    foreign = json.dumps({"statusLine": {"type": "command", "command": "~/my-line.sh"}})
    settings_of(project).write_text(foreign, encoding="utf-8")
    assert change("--uninstall", project).returncode == 1
    assert settings_of(project).read_text() == foreign


def test_install_says_when_git_does_not_ignore_the_settings_file(project, tmp_path_factory,
                                                                 monkeypatch):
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path_factory.mktemp("xdg")))
    assert "git does not ignore" in change("--install", project).stdout
    settings_of(project).unlink()
    (project / ".gitignore").write_text(".claude/settings.local.json\n", encoding="utf-8")
    assert "git does not ignore" not in change("--install", project).stdout


def test_the_line_names_both_versions_where_the_project_loads_another(project, config):
    installed(config, {"scope": "user", "installPath": str(BIN.parent), "version": VERSION},
              {"scope": "project", "projectPath": str(project), "installPath": "/c/9.9.9",
               "version": "9.9.9"})
    assert printed(project) == (f"{SLUG} · task 1/2 delivered · phase delivery | progress.py "
                                f"{VERSION}, plugin 9.9.9 loaded: re-run the status line step of "
                                f"/siegard-config")


def test_the_line_names_no_version_where_the_loaded_one_is_its_own_or_none_is_recorded(project,
                                                                                       config):
    plain = f"{SLUG} · task 1/2 delivered · phase delivery"
    installed(config, {"scope": "local", "projectPath": str(project),
                       "installPath": str(BIN.parent), "version": VERSION},
              {"scope": "user", "installPath": "/c/9.9.9", "version": "9.9.9"})
    assert printed(project) == plain
    installed(config, {"scope": "project", "projectPath": "/another/project",
                       "installPath": "/c/9.9.9", "version": "9.9.9"})
    assert printed(project) == plain
    (config / "plugins" / "installed_plugins.json").write_text("{broken", encoding="utf-8")
    assert printed(project) == plain


def test_a_line_otherwise_empty_stays_empty_whatever_version_is_loaded(project, config):
    installed(config, {"scope": "user", "installPath": "/c/9.9.9", "version": "9.9.9"})
    (project / "plans" / SLUG / "closure.md").write_text("Closed.\n", encoding="utf-8")
    assert printed(project) == ""
