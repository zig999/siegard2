"""`tools/migrate_decision_log.py`: a root `decision-log.md` becomes one log beside each node.

The fixture is rebuilt from the sound specification: its two logs are folded back into one root
log the way a 4.x consumer holds it, including the shape that defeated the 4.x validator — a
second and a third `---` fence with entries past them — and the migration must read all of it.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

import spec

REPO = Path(__file__).resolve().parent.parent
FIXTURE = REPO / "tests" / "fixtures" / "spec-model"
TOOL = REPO / "tools" / "migrate_decision_log.py"

EVIDENCE = {"location": "domain/troubleshooting/evidence.md", "field": "attributes.value.type",
            "unstated": "The material does not say what shape an evidence value takes.",
            "decided": "string", "why": "Every evidence sample in the material is shown as free text."}
TRANSITIONS = {"location": "rules/troubleshooting/case-transitions.md", "field": "rejections",
               "unstated": "The material never says what resolving an open case does.",
               "decided": "The trigger is rejected in the open state.",
               "why": "Resolution without an investigation contradicts the stated flow."}
PAST_THE_FENCE = {"location": "domain/troubleshooting/case.md", "field": "type",
                  "unstated": "Whether a case,\nopened by name,\nis the root.",
                  "decided": "aggregate-root", "why": "A case owns its evidence."}
THIRD_BLOCK = {"location": "domain/troubleshooting/evidence.md", "field": "attributes",
               "unstated": "second decision over evidence", "decided": "kept",
               "why": "one claim"}


@pytest.fixture
def root(tmp_path: Path) -> Path:
    """The sound fixture as a 4.x consumer held it: one root log, three fence lines."""
    root = tmp_path / "knowledge"
    shutil.copytree(FIXTURE, root)
    shutil.rmtree(root / "projections", ignore_errors=True)
    for log in root.rglob("*.log.md"):
        log.unlink()
    (root / "projections").mkdir()
    (root / "projections" / "decisions-by-node.md").write_text("derived\n", encoding="utf-8")
    first = yaml.safe_dump({"entries": [EVIDENCE, TRANSITIONS]}, sort_keys=False)
    past = yaml.safe_dump([PAST_THE_FENCE], sort_keys=False)
    third = yaml.safe_dump({"entries": [THIRD_BLOCK]}, sort_keys=False)
    (root / "decision-log.md").write_text(f"---\n{first}---\n{past}\n---\n{third}",
                                          encoding="utf-8")
    return root


def migrate(root: Path, *flags: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(TOOL), *flags, str(root)],
                          capture_output=True, text=True)


def entries_of(path: Path) -> list[dict]:
    return yaml.safe_load(spec.FENCE.match(path.read_text(encoding="utf-8")).group(1))["entries"]


def test_every_entry_of_every_block_lands_beside_its_node(root):
    done = migrate(root)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "read 4 entry(ies)" in done.stdout and "across 3 fence line(s)" in done.stdout
    assert "written 4 entry(ies) into 3 log(s)" in done.stdout
    assert not (root / "decision-log.md").exists()
    assert not (root / "projections" / "decisions-by-node.md").exists()
    assert entries_of(root / "domain/troubleshooting/evidence.log.md") == [
        {k: v for k, v in EVIDENCE.items() if k != "location"},
        {k: v for k, v in THIRD_BLOCK.items() if k != "location"}]
    assert entries_of(root / "domain/troubleshooting/case.log.md") == [
        {k: v for k, v in PAST_THE_FENCE.items() if k != "location"}]
    assert "specification sound" in done.stdout and "4 decision(s) disclosed" in done.stdout
    text = (root / "domain/troubleshooting/evidence.log.md").read_text(encoding="utf-8")
    assert f"  why: {EVIDENCE['why']}\n" in text, \
        "a scalar is never wrapped: one physical line, as the writer lays it out"
    assert spec.FENCE.match(text).end() == len(text), "a log is frontmatter alone"


def test_a_log_whose_node_is_gone_is_written_and_reported_not_repaired(root):
    """The tool decides nothing: a decision about a node that left is written beside where the
    node was, and `spec.py` says it needs a retirement — that entry is a person's to make."""
    (root / "domain/troubleshooting/case.md").unlink()
    done = migrate(root)
    assert done.returncode == 1, done.stdout + done.stderr
    assert (root / "domain/troubleshooting/case.log.md").is_file()
    assert "sits beside no node domain/troubleshooting/case" in done.stdout


def test_a_dry_run_writes_nothing(root):
    before = sorted(p.relative_to(root).as_posix() for p in root.rglob("*"))
    done = migrate(root, "--dry-run")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "dry run: 4 entry(ies) would land in 3 log(s)" in done.stdout
    assert sorted(p.relative_to(root).as_posix() for p in root.rglob("*")) == before


def test_an_entry_that_does_not_parse_is_named_by_its_lines_and_nothing_is_written(root):
    """An entry typed by hand past the fence with a colon inside an unquoted scalar breaks its
    whole block; the refusal names the lines of the file to repair, not a position in a block."""
    log = root / "decision-log.md"
    text = log.read_text(encoding="utf-8")
    log.write_text(text + "- location: domain/troubleshooting/case.md\n  field: type\n"
                   "  unstated: broken\n  decided: d\n  why: sends code: error.name here\n",
                   encoding="utf-8")
    lines = log.read_text(encoding="utf-8").splitlines()
    bad_line = next(n for n, held in enumerate(lines, 1) if held == "  unstated: broken") - 2
    before = sorted(p.relative_to(root).as_posix() for p in root.rglob("*"))
    done = migrate(root)
    assert done.returncode == 2, done.stdout + done.stderr
    assert "1 entry(ies) of the log do not parse" in done.stderr
    assert f"lines {bad_line}-{bad_line + 4}:" in done.stderr
    assert sorted(p.relative_to(root).as_posix() for p in root.rglob("*")) == before


def test_a_second_run_is_refused(root):
    assert migrate(root).returncode == 0
    (root / "decision-log.md").write_text("---\nentries:\n- location: domain/troubleshooting/"
                                          "evidence.md\n  field: type\n  unstated: u\n"
                                          "  decided: d\n  why: w\n---\n", encoding="utf-8")
    done = migrate(root)
    assert done.returncode == 2 and "this migration runs once" in done.stderr
