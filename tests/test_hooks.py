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


def run(stdin: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT)], input=stdin,
                          capture_output=True, text=True)


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


@pytest.mark.parametrize("event", EVENTS)
def test_the_script_places_the_rules_verbatim_for_the_event_it_was_run_for(event):
    done = run(json.dumps({"hook_event_name": event, "session_id": "x"}))
    assert done.returncode == 0, done.stderr
    out = json.loads(done.stdout)["hookSpecificOutput"]
    assert out["hookEventName"] == event
    assert out["additionalContext"] == RULES.read_text(encoding="utf-8")


def test_an_unreadable_or_foreign_event_record_still_places_the_rules():
    for stdin in ("", "not json", json.dumps({"hook_event_name": "PreToolUse"})):
        done = run(stdin)
        assert done.returncode == 0, done.stderr
        out = json.loads(done.stdout)["hookSpecificOutput"]
        assert out["hookEventName"] == EVENTS[0]
        assert out["additionalContext"] == RULES.read_text(encoding="utf-8")


def test_the_script_never_fails_a_session_over_a_missing_file(tmp_path):
    """A hook that exits non-zero stops the session; a missing rules file is the distribution's
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
    """A hook that exits non-zero stops every session of every project holding the plugin. An
    unreadable trace is the drift report's to refuse properly, where somebody asked it."""
    (traced / "siegard-trace.json").write_text("{ not json", encoding="utf-8")
    for stdin in ("", "not json", json.dumps({"hook_event_name": "SessionStart",
                                              "cwd": str(traced)})):
        done = subprocess.run([sys.executable, "-B", str(DRIFT)], input=stdin,
                              capture_output=True, text=True)
        assert done.returncode == 0, done.stderr
        assert done.stdout == "", done.stdout


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
