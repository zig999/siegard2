"""The plugin's hooks are what place the session rules.

`hooks/rules.md` reaches a context only through `hooks/hooks.json`: a `SessionStart` reaches the
session and never the agents it spawns, a `SubagentStart` reaches that agent alone, and both run
`hooks/rules.py` over the one file. A hook declared for one event and not the other is rules half
the contexts never hold; a script that fails is every session of every project stopped at start.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "src/claude"
HOOKS = SRC / "hooks"
RULES = HOOKS / "rules.md"
SCRIPT = HOOKS / "rules.py"
EVENTS = ("SessionStart", "SubagentStart")


def declared() -> dict:
    return json.loads((HOOKS / "hooks.json").read_text(encoding="utf-8"))["hooks"]


def commands(event: str) -> list[str]:
    return [h["command"] for group in declared()[event] for h in group["hooks"]]


def run(stdin: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT)], input=stdin, cwd=cwd,
                          capture_output=True, text=True)


def git_init(where: Path) -> None:
    subprocess.run(["git", "init", "-q", str(where)], check=True, capture_output=True)


@pytest.fixture
def siegard_project(tmp_path: Path) -> Path:
    """A repository that declares the framework: `siegard.json` at its git toplevel."""
    project = tmp_path / "consumer"
    project.mkdir()
    git_init(project)
    (project / "siegard.json").write_text('{"specification_root": "specs"}\n', encoding="utf-8")
    return project


@pytest.fixture
def foreign_project(tmp_path: Path) -> Path:
    """A repository that never adopted the framework: no `siegard.json` anywhere in it."""
    project = tmp_path / "foreign"
    (project / "src").mkdir(parents=True)
    git_init(project)
    return project


def record(event: str, cwd: Path) -> str:
    return json.dumps({"hook_event_name": event, "session_id": "x", "cwd": str(cwd)})


def test_both_starts_are_declared_and_neither_is_narrowed():
    hooks = declared()
    assert sorted(hooks) == sorted(EVENTS), \
        f"hooks.json declares {sorted(hooks)}; the rules must reach the session and every agent"
    for event in EVENTS:
        for group in hooks[event]:
            assert "matcher" not in group, \
                f"{event} carries a matcher; the rules hold for every {event}, not a subset"


def test_both_starts_run_the_one_script_over_the_one_file():
    """One script places the rules, and it is the same one at both starts. A start may declare a
    second hook beside it — the drift receipt does — but never a second placer of the rules, and
    never a rules command that differs between the two events."""
    for event in EVENTS:
        placing = [c for c in commands(event) if "hooks/rules.py" in c]
        assert len(placing) == 1, f"{event} runs {len(placing)} commands over the rules; one places them"
        command = placing[0]
        assert "${CLAUDE_PLUGIN_ROOT}/hooks/rules.py" in command, \
            f"{event} runs {command!r}; the plugin root is the only path a hook may rely on"
        resolved = Path(command.split('"')[1].replace("${CLAUDE_PLUGIN_ROOT}", str(SRC)))
        assert resolved == SCRIPT and resolved.is_file()
    assert [c for c in commands(EVENTS[0]) if "rules.py" in c] == \
           [c for c in commands(EVENTS[1]) if "rules.py" in c]
    assert os.access(SCRIPT, os.X_OK), f"{SCRIPT} is not executable"


def test_every_declared_hook_runs_a_script_the_plugin_ships():
    """A hook naming a path the distribution does not hold is every session printing an error at
    its start, and the harness reporting it is the only thing that would say so."""
    for event in EVENTS:
        for command in commands(event):
            assert "${CLAUDE_PLUGIN_ROOT}/hooks/" in command, command
            resolved = Path(command.split('"')[1].replace("${CLAUDE_PLUGIN_ROOT}", str(SRC)))
            assert resolved.is_file(), f"{event} runs {resolved}, which the plugin does not hold"


def placed(done: subprocess.CompletedProcess, event: str) -> bool:
    assert done.returncode == 0, done.stderr
    if not done.stdout:
        return False
    out = json.loads(done.stdout)["hookSpecificOutput"]
    assert out["hookEventName"] == event
    assert out["additionalContext"] == RULES.read_text(encoding="utf-8")
    return True


@pytest.mark.parametrize("event", EVENTS)
def test_the_script_places_the_rules_verbatim_for_the_event_it_was_run_for(event, siegard_project):
    assert placed(run(record(event, siegard_project)), event)


def test_an_unreadable_or_foreign_event_record_still_places_the_rules(siegard_project):
    """A record that names no working directory is read as the process's own, which is where the
    harness runs the hook."""
    for stdin in ("", "not json", json.dumps({"hook_event_name": "PreToolUse"})):
        assert placed(run(stdin, cwd=siegard_project), EVENTS[0]), stdin


@pytest.mark.parametrize("event", EVENTS)
def test_a_project_that_declares_no_siegard_json_receives_nothing(event, foreign_project):
    """The rules are this framework's, and a repository that never adopted it holds none of what
    they govern — a plugin enabled for every project would otherwise hand them to all of them."""
    assert not placed(run(record(event, foreign_project / "src")), event)
    assert not placed(run(json.dumps({"hook_event_name": event}), cwd=foreign_project), event)


@pytest.mark.parametrize("event", EVENTS)
def test_a_context_started_below_the_toplevel_still_receives_the_rules(event, siegard_project):
    below = siegard_project / "backend" / "src"
    below.mkdir(parents=True)
    assert placed(run(record(event, below)), event)


def test_a_directory_git_does_not_hold_is_read_as_its_own_toplevel(tmp_path):
    bare = tmp_path / "loose"
    bare.mkdir()
    assert not placed(run(record(EVENTS[0], bare)), EVENTS[0])
    (bare / "siegard.json").write_text("{}\n", encoding="utf-8")
    assert placed(run(record(EVENTS[0], bare)), EVENTS[0])


def test_a_project_that_cannot_be_resolved_still_receives_the_rules(tmp_path):
    """Withholding the rules from a Siegard project loses every rule silently; placing them where
    they were not needed costs context. Where the question cannot be answered, the second wins."""
    assert placed(run(record(EVENTS[1], tmp_path / "gone")), EVENTS[1])


def test_the_toplevel_reader_is_importable_with_the_standard_library_alone():
    """The hook imports `toplevel_of` at every start; an import that needed jsonschema would turn
    every session on a machine without it into one that starts on a hook error."""
    probe = (f"import sys; sys.modules['jsonschema'] = None; sys.path.insert(0, {str(SRC / 'bin')!r}); "
             f"from project import PROJECT_FILE, toplevel_of; print(PROJECT_FILE)")
    done = subprocess.run([sys.executable, "-B", "-c", probe], capture_output=True, text=True)
    assert done.returncode == 0 and done.stdout.strip() == "siegard.json", done.stderr


def test_a_git_that_does_not_answer_is_not_read_as_no_project(tmp_path):
    """Not answering is not the same answer as not holding the directory: the caller that named a
    timeout is told, and decides."""
    fake = tmp_path / "bin"
    fake.mkdir()
    (fake / "git").write_text("#!/bin/sh\nsleep 5\n", encoding="utf-8")
    (fake / "git").chmod(0o755)
    probe = (f"import os, subprocess, sys; os.environ['PATH'] = {str(fake)!r} + os.pathsep + os.environ['PATH']; "
             f"sys.path.insert(0, {str(SRC / 'bin')!r}); from pathlib import Path; from project import toplevel_of\n"
             f"try:\n    toplevel_of(Path({str(tmp_path)!r}), timeout=0.5)\nexcept subprocess.TimeoutExpired:\n    print('timed out')")
    done = subprocess.run([sys.executable, "-B", "-c", probe], capture_output=True, text=True)
    assert done.stdout.strip() == "timed out", done.stderr


def test_the_script_never_fails_a_session_over_a_missing_file(tmp_path):
    """A hook that exits non-zero starts the session on a hook error the session itself never
    reads; a missing rules file is the distribution's
    defect, reported by the distribution suite, never by stopping every consumer."""
    copy = tmp_path / "rules.py"
    copy.write_bytes(SCRIPT.read_bytes())
    done = subprocess.run([sys.executable, str(copy)], input="{}", capture_output=True, text=True)
    assert done.returncode == 0 and done.stdout == ""


# ------------------------------------------------- the drift a session starts on top of

DRIFT = HOOKS / "drift.py"
FIXTURE = REPO / "tests" / "fixtures" / "spec-model"
NODE = "domain/troubleshooting/case"
FILE = "src/orders/place.ts"
TRACE = SRC / "bin" / "trace.py"


def drift_run(cwd: Path | None, event: str = "SessionStart") -> subprocess.CompletedProcess:
    record = {"hook_event_name": event}
    if cwd is not None:
        record["cwd"] = str(cwd)
    return subprocess.run([sys.executable, "-B", str(DRIFT)], input=json.dumps(record),
                          capture_output=True, text=True)


@pytest.fixture
def traced(tmp_path: Path) -> Path:
    """A consumer repository whose project file declares a target, with one node bound to one
    file — the state every receipt below is computed over."""
    import shutil
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, capture_output=True)
    shutil.copytree(FIXTURE, tmp_path / "specs")
    shutil.rmtree(tmp_path / "specs" / "projections", ignore_errors=True)
    (tmp_path / "backend/src/orders").mkdir(parents=True)
    (tmp_path / "backend" / FILE).write_text("export function place() {}\n", encoding="utf-8")
    (tmp_path / "siegard.json").write_text(json.dumps({
        "specification_root": "specs", "targets": {"backend": "backend"},
        "work_root": "work", "delivery_root": "delivery"}) + "\n", encoding="utf-8")
    subprocess.run([sys.executable, "-B", str(TRACE), "--bind", str(tmp_path / "backend"),
                    str(tmp_path / "specs"), NODE, FILE], check=True, capture_output=True)
    return tmp_path


def context_of(done: subprocess.CompletedProcess) -> str:
    return json.loads(done.stdout)["hookSpecificOutput"]["additionalContext"]


def test_the_session_start_declares_both_the_rules_and_the_drift():
    """Detection was mechanical before this and had no trigger: it ran when a person invoked a
    skill, so a tree accumulated drift between the moments somebody thought to look."""
    assert len(commands("SessionStart")) == 2, commands("SessionStart")
    assert any("hooks/drift.py" in c for c in commands("SessionStart"))
    assert not any("drift.py" in c for c in commands("SubagentStart")), \
        "a subagent inherits a context whose opening already carries this; paying per spawn " \
        "buys nothing the session does not hold"
    assert os.access(DRIFT, os.X_OK), f"{DRIFT} is not executable"


def test_a_tree_carrying_drift_says_so_at_the_start_of_the_session(traced):
    path = traced / "backend" / FILE
    path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    done = drift_run(traced)
    assert done.returncode == 0, done.stderr
    said = context_of(done)
    assert "1 drift finding(s)" in said and "1 code" in said, said
    assert "/reconcile" in said, "a count whose door is unnamed is a count nobody can act on"


def test_the_receipt_is_a_tally_and_never_a_listing(traced):
    """What a reader acts on is the count per class and the door it opens. A hook that pasted
    the findings would spend a session's opening context on a report nobody asked for."""
    path = traced / "backend" / FILE
    path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    said = context_of(drift_run(traced))
    assert FILE not in said, said
    assert len(said.splitlines()) < 12, said


def test_a_clean_tree_says_nothing_at_all(traced):
    done = drift_run(traced)
    assert done.returncode == 0 and done.stdout == "", done.stdout


def test_a_project_the_framework_does_not_hold_says_nothing(tmp_path):
    done = drift_run(tmp_path)
    assert done.returncode == 0 and done.stdout == ""


def test_a_node_owed_a_test_is_counted_at_the_start_of_the_session(traced):
    """A refused certification that named the assertion closing it is owed that test, and no
    drift report shows it: the count here is `--owed`'s own, placed where the session starts."""
    import yaml
    record = {"contract_version": "siegard-reconcile/5", "title": "An audit",
              "summary": "The claims were re-read; the source did not change.",
              "target": "backend",
              "files": [{"path": FILE, "change": "unchanged; re-read"}],
              "nodes": [{"node": NODE, "conforms": True, "decided_by": "reading",
                         "how": "`export function place() {}` is where the case is placed",
                         "encoded_at": [FILE], "remainder": "testable",
                         "remainder_why": "one input, an order with no lines, against one "
                                          "refusal"}]}
    (traced / "siegard-reconcile").mkdir()
    (traced / "siegard-reconcile" / "audit.md").write_text(
        f"---\n{yaml.safe_dump(record, sort_keys=False)}---\n\n## Notes\nNone.\n",
        encoding="utf-8")
    done = drift_run(traced)
    assert done.returncode == 0, done.stderr
    said = context_of(done)
    assert "1 node(s) a finite test would decide are still decided by a reading or a step" in said
    assert "hands the proof increment that writes those tests" in said


def test_the_drift_hook_never_fails_a_session(traced):
    """A hook that exits non-zero starts every session of every project holding the plugin on a
    hook error. An unreadable trace is the drift report's to refuse properly, where somebody
    asked it."""
    (traced / "siegard-trace.json").write_text("{ not json", encoding="utf-8")
    for stdin in ("", "not json", json.dumps({"hook_event_name": "SessionStart",
                                              "cwd": str(traced)})):
        done = subprocess.run([sys.executable, "-B", str(DRIFT)], input=stdin,
                              capture_output=True, text=True)
        assert done.returncode == 0, done.stderr
        assert done.stdout == "", done.stdout


def drift_without(cwd: Path, *modules: str) -> subprocess.CompletedProcess:
    """The hook run by a `python3` that cannot import the named modules, the way a machine
    without the validators runs it."""
    blocked = "".join(f"sys.modules[{name!r}] = None; " for name in modules)
    probe = (f"import runpy, sys; {blocked}sys.argv = [{str(DRIFT)!r}]; "
             f"runpy.run_path({str(DRIFT)!r}, run_name='__main__')")
    record = json.dumps({"hook_event_name": "SessionStart", "cwd": str(cwd)})
    return subprocess.run([sys.executable, "-B", "-c", probe], input=record,
                          capture_output=True, text=True)


@pytest.mark.parametrize("modules, named", [
    (("yaml", "jsonschema"), "PyYAML and jsonschema"),
    (("yaml",), "PyYAML"),
    (("jsonschema",), "jsonschema"),
])
def test_a_declared_project_on_a_machine_without_the_validators_is_told_the_count_was_not_taken(
        traced, modules, named):
    """A session starting with no count reads as one starting with no drift. Where the count
    could not be taken, the person and the session are both told why, in one line, and the
    session still starts."""
    done = drift_without(traced, *modules)
    assert done.returncode == 0, done.stderr
    assert done.stderr == "", done.stderr
    said = json.loads(done.stdout)
    line = said["hookSpecificOutput"]["additionalContext"]
    assert said["systemMessage"] == line
    assert "\n" not in line
    assert "did not count the drift" in line and f"need {named}," in line, line
    assert f"pip install {named.lower().replace(' and ', ' ')})" in line, line


def test_an_undeclared_project_on_a_machine_without_the_validators_hears_nothing(tmp_path):
    """The plugin's scripts are no undeclared project's to run, so their absence is not that
    project's news."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, capture_output=True)
    done = drift_without(tmp_path, "yaml", "jsonschema")
    assert done.returncode == 0, done.stderr
    assert done.stdout == "" and done.stderr == "", done.stdout + done.stderr


def test_a_subagent_start_record_is_not_answered(traced):
    path = traced / "backend" / FILE
    path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    done = drift_run(traced, event="SubagentStart")
    assert done.returncode == 0 and done.stdout == ""


def test_the_receipt_names_the_route_for_a_node_that_moved(traced):
    """`moved` has one route, said once: `/reconcile` over the bound files, or the delivery of
    a task implementing the node. A count whose door is unnamed is a count nobody can act on."""
    node = traced / "specs" / f"{NODE}.md"
    node.write_text(node.read_text(encoding="utf-8") + "\nA line the bind never read.\n",
                    encoding="utf-8")
    said = context_of(drift_run(traced))
    assert "1 moved" in said, said
    assert "`/reconcile` over the bound files" in said and "delivery" in said, said
