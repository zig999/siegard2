"""`deliver.py --check-record` — the record /check-source leaves behind, and the citations in it.

The record exists for source no task delivered. Every other reading of a standard happens inside a
review, and a review's file set comes out of implementation and proof records, so a change made
without a task is read by nothing at all. What matters most here is that the citations are held to
exactly what a review's are held to — declared, left to a reading, in scope for the file — because
a finding from this route and a finding from a review answer to one registry, and a reading held to
less would produce findings a reader cannot tell apart from ones held to more.
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

import deliver

DELIVER_PY = Path(deliver.__file__)
BODY = "## What it is\nProse for a reader.\n\n## Notes\nNone.\n"

STANDARD = {
    "contract_version": "siegard-standard/1",
    "standard": "frontend",
    "summary": "How this project's screens are composed and wired.",
    "rules": [
        {"id": "ARC-01",
         "statement": "A component composes an existing primitive rather than reimplementing it.",
         "because": "A hand-rolled equivalent drifts from the catalogued one the day either moves.",
         "decided_by": "reading",
         "applies_to": [{"under": "src", "suffix": ".tsx", "nested": True}]},
        {"id": "TST-01",
         "statement": "A test asserts what a user would observe.",
         "because": "A test bound to an internal call fails when nothing a user sees has changed.",
         "decided_by": "reading",
         "applies_to": [{"under": "tests", "suffix": ".spec.tsx", "nested": True}]},
        {"id": "MNT-02",
         "statement": "A visual value is referenced through a design token, never a literal.",
         "because": "The same literal in three places is three places to change and two forgotten.",
         "decided_by": "tool",
         "tool": "style",
         "applies_to": [{"under": "src", "suffix": ".tsx", "nested": True}]},
    ],
    "commands": [{"step": "style", "command": "true", "timeout_seconds": 60}],
}


def run(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(DELIVER_PY), *map(str, args)],
                          capture_output=True, text=True)


@pytest.fixture
def tree(tmp_path: Path) -> Path:
    """A target source root holding a registry, and the check directory beside it."""
    target = tmp_path / "frontend"
    (target / "src/features").mkdir(parents=True)
    (target / "src/features/case-list.tsx").write_text("export const List = () => null;\n",
                                                       encoding="utf-8")
    (target / "standard.yaml").write_text(yaml.safe_dump(STANDARD, sort_keys=False),
                                          encoding="utf-8")
    (tmp_path / "siegard-check").mkdir()
    return tmp_path


def pin_of(tree: Path) -> str:
    return "sha256:" + hashlib.sha256(
        (tree / "frontend/standard.yaml").read_bytes()).hexdigest()


def record(tree: Path, name: str = "week.md", **overrides) -> Path:
    front = {
        "contract_version": "siegard-check/1",
        "title": "The week's direct edits",
        "summary": "The files a drift receipt counted as suppressed, read once.",
        "target": "frontend",
        "reviewed": ["src/features/case-list.tsx"],
        "standard": {"at": "standard.yaml", "pin": pin_of(tree)},
    }
    front.update(overrides)
    path = tree / "siegard-check" / name
    path.write_text(f"---\n{yaml.safe_dump(front, sort_keys=False, allow_unicode=True)}---\n{BODY}",
                    encoding="utf-8")
    return path


def finding(**overrides) -> dict:
    entry = {
        "file": "src/features/case-list.tsx",
        "where": "the filter at line 40",
        "cites": "ARC-01",
        "evidence": "<div className='row'>{...}</div> built by hand",
        "cost": "a second implementation of a catalogued primitive, drifting from the day either moves",
    }
    entry.update(overrides)
    return entry


def said(done: subprocess.CompletedProcess, fragment: str) -> None:
    assert fragment in done.stdout + done.stderr, \
        f"nothing said {fragment!r}; what was said was {done.stdout}{done.stderr}"


# ---------------------------------------------------------------- the sound case


def test_a_reading_that_found_nothing_holds(tree):
    done = run("--check-record", record(tree), tree / "frontend")
    assert done.returncode == 0, done.stdout + done.stderr
    said(done, "0 finding(s) over 1 file(s)")


def test_a_reading_with_a_finding_holds(tree):
    done = run("--check-record", record(tree, findings=[finding()]), tree / "frontend")
    assert done.returncode == 0, done.stdout + done.stderr


def test_it_says_the_half_it_did_not_answer_for(tree):
    """A reader who takes a clean result here for a clean result against the registry has read
    half of one, so the command says which half every time."""
    done = run("--check-record", record(tree), tree / "frontend")
    said(done, "the rules a tool decides were not read here")


# ---------------------------------------------------------------- the citations


def test_a_citation_to_a_rule_the_registry_does_not_declare(tree):
    done = run("--check-record", record(tree, findings=[finding(cites="ZZZ-99")]),
               tree / "frontend")
    assert done.returncode == 1
    said(done, "cites ZZZ-99, which standard.yaml does not declare")


def test_a_citation_to_a_rule_a_tool_decides(tree):
    """The line the whole split rests on. A model hunting a literal colour competes with the
    style checker that owns it and loses, and a finding here would make that tool's own output
    look like one opinion among two."""
    done = run("--check-record", record(tree, findings=[finding(cites="MNT-02")]),
               tree / "frontend")
    assert done.returncode == 1
    said(done, "which standard.yaml says a tool decides")


def test_a_citation_whose_scope_does_not_reach_the_file(tree):
    done = run("--check-record", record(tree, findings=[finding(cites="TST-01")]),
               tree / "frontend")
    assert done.returncode == 1
    said(done, "which that rule's scope does not reach")


def test_a_finding_outside_the_file_set(tree):
    done = run("--check-record",
               record(tree, findings=[finding(file="src/features/other.tsx")]),
               tree / "frontend")
    assert done.returncode == 1
    said(done, "which `reviewed` does not list")


# ---------------------------------------------------------------- the record itself


def test_a_record_filed_outside_the_check_directory(tree):
    """A reading nobody can find is a reading nobody made. It lives beside the trace because what
    it is about — source, standing on its own — outlives every plan and delivery root."""
    stray = tree / "frontend" / "week.md"
    stray.write_text(record(tree).read_text(encoding="utf-8"), encoding="utf-8")
    done = run("--check-record", stray, tree / "frontend")
    assert done.returncode == 2
    said(done, "does not sit under siegard-check/")


def test_a_record_naming_a_registry_that_is_not_there(tree):
    done = run("--check-record",
               record(tree, standard={"at": "gone.yaml", "pin": pin_of(tree)}),
               tree / "frontend")
    assert done.returncode == 1
    # The record also carries a pin matching nothing, so the exit code alone cannot say which of
    # the two was reported. Every sibling test here pairs the code with a fragment for that reason.
    said(done, "gone.yaml")
    said(done, "does not exist")


def test_a_record_missing_the_file_set(tree):
    path = record(tree)
    front = yaml.safe_load(path.read_text(encoding="utf-8").split("---\n")[1])
    del front["reviewed"]
    path.write_text(f"---\n{yaml.safe_dump(front, sort_keys=False)}---\n{BODY}", encoding="utf-8")
    done = run("--check-record", path, tree / "frontend")
    assert done.returncode == 1
    said(done, "reviewed")


def test_a_record_of_a_different_contract_version(tree):
    done = run("--check-record", record(tree, contract_version="siegard-check/2"),
               tree / "frontend")
    assert done.returncode == 1


def test_the_body_is_held_to_the_two_headings(tree):
    path = record(tree)
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(BODY, "## What it is\nProse.\n"), encoding="utf-8")
    assert run("--check-record", path, tree / "frontend").returncode == 1
