"""The benchmarks SPEC-001 items 2 and 3 name are repository state, and their records stay sound.

No model runs here. A benchmark is a model run recorded once — its material, its written root,
its verbatim return, its grading — and what this module holds is the record: every written root
still validates under the validator as it stands, every mechanical expectation the grading
claims is recomputed from the root rather than trusted, and every scored case of the decided-fact
route says the outcome the corpus expects. A run that drifts from the skill it measured stays
sound here until the validator changes; a validator that refuses an old run is the signal, and a
new iteration is recorded beside the old one rather than over it.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

import spec

REPO = Path(__file__).resolve().parent.parent
BENCH = REPO / "tests" / "fixtures" / "benchmarks"
ANALYSE = BENCH / "analyse"
UNSTATED = BENCH / "unstated-route"
OPEN_MARKER = re.compile(r"\bTODO\b|\bTBD\b|\?\?\?|^\s*\w+:\s*unknown\s*$", re.M)
R15 = ("«Material that states no fact any of the five classes admits is an absent input, never "
       "a specification to decide» (SPEC-001 R15)")
EXPECTED_OUTCOME = {1: "decided", 2: "decided", 3: "decided", 4: "decided", 5: "decided",
                    6: "decided", 7: "contradicted", 8: "stated", 9: "stated"}


def problems_of(root: Path) -> list[str]:
    nodes, problems = spec.collect(root, spec.contracts())
    return problems + spec.cross_problems(nodes, root)


def shape(root: Path) -> str:
    done = subprocess.run([sys.executable, "-B", str(REPO / "src/claude/bin/spec.py"),
                           "--shape", str(root)], capture_output=True, text=True)
    return done.stdout


def runs() -> list[Path]:
    return sorted(p for p in (ANALYSE / "iteration-1").iterdir() if p.is_dir())


def test_the_corpora_are_committed():
    assert (ANALYSE / "materials" / "minimal.md").is_file()
    assert (ANALYSE / "materials" / "rich.md").is_file()
    assert (ANALYSE / "benchmark.md").read_text(encoding="utf-8").startswith("# `/analyse` under")
    corpus = (UNSTATED / "bench-corpus.md").read_text(encoding="utf-8")
    assert corpus.startswith("# Bench corpus for the unstated-fact route")
    assert len(re.findall(r"^## Case \d+ — ", corpus, re.M)) == 9


def test_the_other_language_material_is_recorded():
    """SPEC-001 item 2 asks for material written in another language; both materials are."""
    for name in ("minimal.md", "rich.md"):
        text = (ANALYSE / "materials" / name).read_text(encoding="utf-8")
        assert re.search(r"\b(cadastro|cliente|clientes)\b", text), f"{name} is not Portuguese"


@pytest.mark.parametrize("run", [p.name for p in runs()])
def test_each_recorded_analyse_root_is_sound_or_recorded_as_a_stop(run):
    """A written root validates as the validator stands, carries no open marker, and the
    decided-fields reading the run recorded is what `--shape` recomputes; a run that stopped
    before any write wrote nothing and its report cites the stop verbatim."""
    record = ANALYSE / "iteration-1" / run
    root = record / "spec"
    written = sorted(p for p in root.rglob("*") if p.is_file()) if root.is_dir() else []
    report = (record / "report.md").read_text(encoding="utf-8")
    if not written:
        assert R15 in report, f"{run} wrote nothing and its report does not cite the stop"
        assert not (record / "shape-decided.txt").exists()
        return
    assert problems_of(root) == [], f"{run}'s written root no longer validates"
    for path in written:
        if path.suffix == ".md" and "projections" not in path.parts:
            assert not OPEN_MARKER.search(path.read_text(encoding="utf-8")), \
                f"{path.relative_to(record)} carries an open marker"
    recorded = (record / "shape-decided.txt").read_text(encoding="utf-8")
    at = shape(root).index("decided fields per node")
    recomputed = shape(root)[at:]
    for line in recorded.splitlines()[1:]:
        if line.strip():
            assert line.strip() in recomputed, f"{run}: `{line.strip()}` is not what --shape says now"


@pytest.mark.parametrize("run", [p.name for p in runs()])
def test_every_mechanical_expectation_of_the_grading_passed_with_evidence(run):
    grading = json.loads((ANALYSE / "iteration-1" / run / "grading.json").read_text(encoding="utf-8"))
    assert grading["run"] == run
    mechanical = [e for e in grading["expectations"] if e["text"].startswith("mechanical:")]
    assert mechanical, f"{run} grades nothing mechanically"
    for expectation in mechanical:
        assert expectation["passed"] is True, f"{run}: {expectation['text']}"
        assert expectation["evidence"].strip(), f"{run}: {expectation['text']} has no evidence"


@pytest.mark.parametrize("case", sorted(EXPECTED_OUTCOME))
def test_each_unstated_route_case_is_a_sound_root_with_its_fact(case):
    folder = UNSTATED / "cases" / str(case)
    assert (folder / "fact.md").read_text(encoding="utf-8").strip()
    inputs = json.loads((folder / "inputs.json").read_text(encoding="utf-8"))
    assert inputs["expected"] == EXPECTED_OUTCOME[case]
    assert problems_of(folder / "spec") == []
    for relative in inputs["impact_set"]:
        assert (folder / "spec" / relative).is_file(), f"case {case}: {relative} is not in the root"
    for relative in inputs["intake"]:
        assert (folder / relative).is_file()


def test_the_planted_contradiction_stands_in_its_root():
    rule = UNSTATED / "cases" / "7" / "spec" / "rules" / "sales" / "invoice-immutable.md"
    assert "An issued invoice never changes." in rule.read_text(encoding="utf-8")


def test_the_stated_cases_hold_their_statement_where_the_corpus_says():
    intake = (UNSTATED / "cases" / "8" / "intake" / "scope.md").read_text(encoding="utf-8")
    assert "publishes as an operational role" in intake
    prose = (UNSTATED / "cases" / "9" / "spec" / "domain" / "troubleshooting" / "evidence.md")
    text = prose.read_text(encoding="utf-8")
    assert "citations are by name and never by identifier" in text.split("## Description", 1)[1]
    assert "citation" not in spec.FENCE.match(text).group(1), "the fact must live in prose alone"


@pytest.mark.parametrize("case", sorted(EXPECTED_OUTCOME))
def test_each_scored_case_of_the_latest_iteration_says_what_the_corpus_expects(case):
    """SPEC-001 item 3: the deciding context receives the fact without the task, every decided
    fact lands as a resolvable log entry, and a planted contradiction comes back as the stop.
    That is what is asserted. Whether a decided value agrees with the value a person once chose
    is the corpus's own reading, recorded in the score as `matches_ground_truth` and read in the
    corpus's scoring notes, never asserted: the specification asks that the fact be decided,
    disclosed and resolvable, not that it be decided the way one person did."""
    record = UNSTATED / "iteration-1" / str(case)
    assert (record / "return.md").read_text(encoding="utf-8").strip(), f"case {case} has no return"
    score = json.loads((record / "score.json").read_text(encoding="utf-8"))
    assert score["case"] == case
    assert score["outcome"] == EXPECTED_OUTCOME[case], \
        f"case {case} came back {score['outcome']!r}, the corpus expects {EXPECTED_OUTCOME[case]!r}"
    assert score["second_fact_decided"] is False
    if EXPECTED_OUTCOME[case] == "decided":
        assert score["log_entry"] is True and score["log_kind"] == "decided"
        assert score["location_resolves"] is True
        assert score["coherent_and_disclosed"] is True
        if score.get("ground_truth"):
            assert score["matches_ground_truth"] in (True, False), \
                f"case {case} has a ground truth and no reading against it"
    elif case == 8:
        # found under intake/: recorded as read — «A fact the supplied material states is read,
        # not decided, and is recorded as read» (SPEC-001 R13) — never a decided entry
        assert score["log_entry"] is True and score["log_kind"] == "read"
        assert score["location_resolves"] is True
    else:
        assert score["log_entry"] is False
    if case == 7:
        assert "invoice-immutable" in score["names"]
