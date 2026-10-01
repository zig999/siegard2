"""`spec.py --decide`: the one route a decision-log entry is written by (SPEC-001 R9).

Every test copies the sound fixture, hands the writer one entry on stdin, and reads what it did
back from the log beside the node — the file is the evidence, the printed first line is what a
skill quotes, and a refusal leaves no byte behind.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

import spec

REPO = Path(__file__).resolve().parent.parent
FIXTURE = REPO / "tests" / "fixtures" / "spec-model"
SCRIPT = REPO / "src" / "claude" / "bin" / "spec.py"

CASE = "domain/troubleshooting/case"
CASE_LOG = "domain/troubleshooting/case.log.md"
DECIDED = {"field": "type", "unstated": "No node said what class a case is.",
           "decided": "aggregate-root", "why": "A case owns its evidence and is opened by name."}


@pytest.fixture
def spec_root(tmp_path: Path) -> Path:
    root = tmp_path / "specification"
    shutil.copytree(FIXTURE, root)
    shutil.rmtree(root / "projections", ignore_errors=True)
    return root


def decide(root: Path, identity: str, entry, *flags: str) -> subprocess.CompletedProcess:
    raw = entry if isinstance(entry, str) else json.dumps(entry)
    return subprocess.run([sys.executable, "-B", str(SCRIPT), *flags, "--decide", identity,
                           str(root)], input=raw, capture_output=True, text=True)


def entries_of(root: Path, relative: str) -> list[dict]:
    text = (root / relative).read_text(encoding="utf-8")
    return yaml.safe_load(spec.FENCE.match(text).group(1))["entries"]


def test_a_decision_lands_in_a_new_log_beside_the_node(spec_root):
    done = decide(spec_root, CASE, DECIDED)
    assert done.returncode == 0, done.stdout + done.stderr
    assert done.stdout.splitlines()[0] == f"decided: {CASE}.log.md entries[0] — type"
    assert entries_of(spec_root, CASE_LOG) == [DECIDED]
    assert "specification sound: 3 decision(s) disclosed" in done.stdout
    text = (spec_root / CASE_LOG).read_text(encoding="utf-8")
    assert text.startswith("---\nentries:\n- field: type\n") and text.endswith("---\n")
    assert spec.FENCE.match(text).end() == len(text), "a log is frontmatter alone"


def test_an_appended_entry_leaves_every_earlier_byte_in_place(spec_root):
    """«An entry is never edited or removed» (SPEC-001 R9) is a property of the diff: the writer
    appends a block and never re-serialises what stands, so the old text is a prefix of the new
    one up to the closing fence."""
    log = spec_root / "domain/troubleshooting/evidence.log.md"
    before = log.read_text(encoding="utf-8")
    long_why = " ".join(["one claim"] * 60)
    done = decide(spec_root, "domain/troubleshooting/evidence",
                  {**DECIDED, "field": "attributes", "why": long_why})
    assert done.returncode == 0, done.stdout + done.stderr
    after = log.read_text(encoding="utf-8")
    assert after.startswith(before[:-len("---\n")]) and after.endswith("---\n")
    assert after.count("\n- field:") == 2
    assert f"why: {long_why}\n" in after, "every scalar stays on one physical line"
    assert done.stdout.splitlines()[0].endswith("entries[1] — attributes")


def test_a_read_entry_and_a_retirement_print_their_shape(spec_root):
    read = {"field": "type", "unstated": "No node said what a case is.",
            "found": "work/x/intake/scope.md: a case is the unit an operator opens and closes."}
    done = decide(spec_root, CASE, read)
    assert done.returncode == 0, done.stdout + done.stderr
    assert done.stdout.splitlines()[0].startswith("read: ")
    assert "`why`" not in done.stdout
    done = decide(spec_root, CASE, {"field": "type", "retired": "held by rules/x/y statement"})
    assert done.returncode == 0, done.stdout + done.stderr
    assert done.stdout.splitlines()[0].startswith("retired: ")
    assert "1 fact(s) recorded as read, 1 location(s) retired" in done.stdout


def test_a_retirement_may_land_beside_a_node_that_left(spec_root):
    """The tombstone route: the node is gone, its log stays, and the last entry says where the
    fact went — the one write the validator accepts beside no node."""
    (spec_root / "domain/troubleshooting/evidence.md").unlink()
    done = decide(spec_root, "domain/troubleshooting/evidence",
                  {"field": "attributes.value.type", "retired": "held nowhere; the element left"})
    assert done.stdout.splitlines()[0].startswith("retired: ")
    assert "sits beside no node" not in done.stdout


def test_the_why_is_measured_against_the_roots_p90(spec_root):
    done = decide(spec_root, CASE, {**DECIDED, "why": " ".join(["an argument"] * 50)})
    assert done.returncode == 0, done.stdout + done.stderr
    line = next(l for l in done.stdout.splitlines() if l.startswith("`why`"))
    assert "100w" in line and "p90" in line and "at or past the p90" in line
    done = decide(spec_root, CASE, {**DECIDED, "field": "attributes", "why": "short"})
    line = next(l for l in done.stdout.splitlines() if l.startswith("`why`"))
    assert line.startswith("`why` 1w") and "at or past" not in line


def test_a_landed_entry_over_an_unsound_root_is_reported_not_unwritten(spec_root):
    """The analysis appends mid-authoring; a write refused for a problem elsewhere would send it
    back to editing YAML by hand. The entry lands, the first line says so, and the exit says the
    root is not sound."""
    (spec_root / "domain/monitoring/_context.md").unlink()
    done = decide(spec_root, CASE, DECIDED)
    assert done.returncode == 1
    assert done.stdout.splitlines()[0].startswith("decided: ")
    assert "carries no _context.md" in done.stdout and "the entry landed" in done.stdout
    assert entries_of(spec_root, CASE_LOG) == [DECIDED]


# ------------------------------------------------------------------ refusals


def test_a_field_the_node_does_not_declare_is_refused(spec_root):
    done = decide(spec_root, CASE, {**DECIDED, "field": "values.open"})
    assert done.returncode == 1
    assert done.stdout.startswith("refused: domain/troubleshooting/case declares no `values`")
    assert "SPEC-001 R9" in done.stdout
    assert not (spec_root / CASE_LOG).exists()


def test_a_node_that_does_not_exist_is_refused_unless_retiring(spec_root):
    done = decide(spec_root, "domain/troubleshooting/ghost", DECIDED)
    assert done.returncode == 1
    assert done.stdout.startswith("refused: domain/troubleshooting/ghost names no node")
    assert not (spec_root / "domain/troubleshooting/ghost.log.md").exists()


def test_an_entry_the_schema_refuses_is_refused_by_the_schema(spec_root):
    done = decide(spec_root, CASE, {"field": "type", "unstated": "x", "decided": "y"})
    assert done.returncode == 1 and "refused: " in done.stdout
    assert "'why' is a required property" in done.stdout
    done = decide(spec_root, CASE, {**DECIDED, "location": "domain/troubleshooting/case.md"})
    assert done.returncode == 1 and "'location' was unexpected" in done.stdout
    assert not (spec_root / CASE_LOG).exists()


def test_a_log_carrying_text_after_its_fence_is_refused(spec_root):
    log = spec_root / "domain/troubleshooting/evidence.log.md"
    before = log.read_text(encoding="utf-8") + "- field: type\n  unstated: lost\n"
    log.write_text(before, encoding="utf-8")
    done = decide(spec_root, "domain/troubleshooting/evidence", {**DECIDED, "field": "type"})
    assert done.returncode == 1
    assert "refused: domain/troubleshooting/evidence.log carries text after its fence" in done.stdout
    assert log.read_text(encoding="utf-8") == before, "nothing written"


def test_a_retirement_no_earlier_entry_filled_is_refused(spec_root):
    done = decide(spec_root, CASE, {"field": "type", "retired": "held nowhere"})
    assert done.returncode == 1
    assert done.stdout.startswith("refused: no earlier entry of domain/troubleshooting/case.log")
    assert not (spec_root / CASE_LOG).exists()


def test_the_flag_cannot_run_without_an_identity_an_object_or_alone(spec_root):
    done = subprocess.run([sys.executable, "-B", str(SCRIPT), str(spec_root), "--decide"],
                          input="{}", capture_output=True, text=True)
    assert done.returncode == spec.CANNOT_RUN and "takes a node identity" in done.stderr
    done = decide(spec_root, CASE, "not json")
    assert done.returncode == spec.CANNOT_RUN and "not one JSON object" in done.stderr
    done = decide(spec_root, CASE, "[1, 2]")
    assert done.returncode == spec.CANNOT_RUN and "not one JSON object" in done.stderr
    done = decide(spec_root, CASE, DECIDED, "--project")
    assert done.returncode == spec.CANNOT_RUN and "stands beside no other flag" in done.stderr
    done = decide(spec_root, "domain/troubleshooting/case.log", DECIDED)
    assert done.returncode == spec.CANNOT_RUN and "computes to no node identity" in done.stderr
    assert not (spec_root / CASE_LOG).exists()
