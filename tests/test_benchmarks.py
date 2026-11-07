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


# ---------------------------------------------------------------- iteration 2 onward: cases
# From iteration 2 a run names the case it ran (cases/<name>/case.json) and its grading is
# produced by tools/bench_analyse.py; this module recomputes every expectation from the record
# with the same checks, so a grading is re-read, never trusted. iteration-1 predates the cases
# and stays under the tests above.

sys.path.insert(0, str(REPO / "tools"))
import bench_analyse  # noqa: E402

CASES = ANALYSE / "cases"


def case_runs() -> list[Path]:
    return sorted(p for it in sorted(ANALYSE.glob("iteration-*")) if it.name != "iteration-1"
                  for p in it.iterdir() if (p / "grading.json").is_file())


def test_every_case_names_only_checks_the_grader_knows(tmp_path):
    names = sorted(p.parent.name for p in CASES.glob("*/case.json"))
    assert names == ["change-populated-root", "compaction-resume", "file-material-empty-root"]
    for name in names:
        project = tmp_path / name
        bench_analyse.setup(name, project, bench_analyse.SKILL)
        assert problems_of(project / "spec") == [], f"{name}: the seed does not validate"
        (project / "report.md").write_text("", encoding="utf-8")
        bench_analyse.checks(name, project)


def test_the_resumed_case_cuts_the_skill_where_a_compaction_reattaches_it(tmp_path):
    """The case exists to hold the skill to surviving a compaction: the cut must keep the
    checklist that tells a resumed session to read the skill again, and must lose a later step."""
    project = tmp_path / "compaction-resume"
    bench_analyse.setup("compaction-resume", project, bench_analyse.SKILL)
    cut = (tmp_path / "compaction-resume.skill-after-compaction.md").read_text(encoding="utf-8")
    assert "## Progress checklist" in cut and "read `${CLAUDE_PLUGIN_ROOT}/skills/analyse/SKILL.md` again" in cut
    assert "### 6. Report, and stop" not in cut, "the cut keeps the whole skill; the case lost its subject"


@pytest.mark.parametrize("run", [str(p.relative_to(ANALYSE)) for p in case_runs()])
def test_each_case_run_grades_as_recomputed_from_its_record(run):
    record = ANALYSE / run
    grading = json.loads((record / "grading.json").read_text(encoding="utf-8"))
    recomputed = {e["text"]: e["passed"] for e in bench_analyse.checks(grading["case"], record)}
    for expectation in grading["expectations"]:
        assert recomputed[expectation["text"]] == expectation["passed"], \
            f"{run}: '{expectation['text']}' was recorded {expectation['passed']} and recomputes otherwise"


def test_the_latest_iteration_passes_every_expectation_on_every_case():
    """The regression gate: the newest recorded iteration ran the skill as it ships and passed.
    A change to the skill records a new iteration beside this one rather than over it."""
    latest = max((p for p in ANALYSE.glob("iteration-*") if p.name != "iteration-1"),
                 key=lambda p: int(p.name.split("-")[1]), default=None)
    assert latest, "no case iteration is recorded"
    graded = sorted(p.parent.name for p in latest.glob("*/grading.json"))
    assert graded == sorted(p.parent.name for p in CASES.glob("*/case.json")), \
        f"{latest.name} does not hold one run per case"
    for path in latest.glob("*/grading.json"):
        failed = [e["text"] for e in json.loads(path.read_text(encoding="utf-8"))["expectations"]
                  if not e["passed"]]
        assert not failed, f"{path.parent.name}: {failed}"


# ---------------------------------------------------------------- /implement-task: cases
# Each run delivers the one task of tests/fixtures/benchmarks/implement-task/project/ and names
# the case it ran; tools/bench_implement_task.py grades it and this module recomputes every
# expectation from the record. A run's `arm` says which skill it ran: `shipped:` is the skill as
# this repository holds it at the iteration's commit, `before:` the skill it replaced.

import bench_implement_task  # noqa: E402

IMPLEMENT = BENCH / "implement-task"
IMPLEMENT_CASES = IMPLEMENT / "cases"


def implement_runs() -> list[Path]:
    return sorted(p for it in sorted(IMPLEMENT.glob("iteration-*"))
                  for p in it.iterdir() if (p / "grading.json").is_file())


def grading_of(record: Path) -> dict:
    return json.loads((record / "grading.json").read_text(encoding="utf-8"))


def test_every_implement_task_case_names_only_checks_the_grader_knows(tmp_path):
    names = sorted(p.parent.name for p in IMPLEMENT_CASES.glob("*/case.json"))
    assert names == ["compaction-resume", "first-delivery", "reading-quiz"]
    for name in names:
        project = tmp_path / name
        bench_implement_task.setup(name, project, bench_implement_task.SKILL)
        bench_implement_task.checks(name, project)


def test_the_implement_task_fixture_plan_and_specification_hold_together(tmp_path):
    project = tmp_path / "project"
    bench_implement_task.setup("first-delivery", project, bench_implement_task.SKILL)
    assert problems_of(project / "spec") == []
    done = subprocess.run([sys.executable, "-B", str(REPO / "src/claude/bin/plan.py"), "--check",
                           str(project / "work/lending"), str(project / "spec")],
                          capture_output=True, text=True)
    assert done.returncode == 0, done.stdout + done.stderr


def test_the_resumed_implement_task_case_starts_where_step_4_ends(tmp_path):
    """The case holds the skill to the steps a compaction leaves: steps 1-4 ran through the
    framework's writers, the implementation record validates, and nothing past it exists."""
    project = tmp_path / "compaction-resume"
    bench_implement_task.setup("compaction-resume", project, bench_implement_task.SKILL)
    assert (project / bench_implement_task.IMPLEMENTATION).is_file()
    assert not (project / bench_implement_task.PROOF).exists()
    assert not (project / "siegard-trace.json").exists()
    graded = {e["text"]: e["passed"] for e in bench_implement_task.checks("compaction-resume", project)}
    assert graded["mechanical: deliver.py over the recorded delivery exits 0"] is True
    assert graded["mechanical: the proof record exists"] is False


def test_the_resumed_implement_task_case_cuts_the_skill_where_a_compaction_reattaches_it(tmp_path):
    """The cut keeps the checklist that tells a resumed session to read the skill again, and
    loses every step past the implement step — which is the subject of the case."""
    project = tmp_path / "compaction-resume"
    bench_implement_task.setup("compaction-resume", project, bench_implement_task.SKILL)
    cut = (tmp_path / "compaction-resume.skill-after-compaction.md").read_text(encoding="utf-8")
    assert "## Progress checklist" in cut
    assert "read `${CLAUDE_PLUGIN_ROOT}/skills/implement-task/SKILL.md`" in " ".join(cut.split())
    assert "### 6. Suite" not in cut, "the cut keeps the suite step; the case lost its subject"


@pytest.mark.parametrize("run", [str(p.relative_to(IMPLEMENT)) for p in implement_runs()])
def test_each_implement_task_run_grades_as_recomputed_from_its_record(run):
    record = IMPLEMENT / run
    grading = grading_of(record)
    assert grading["arm"].split(":")[0] in ("shipped", "before"), f"{run}: arm {grading['arm']!r}"
    recomputed = {e["text"]: e["passed"] for e in bench_implement_task.checks(grading["case"], record)}
    for expectation in grading["expectations"]:
        assert recomputed[expectation["text"]] == expectation["passed"], \
            f"{run}: '{expectation['text']}' was recorded {expectation['passed']} and recomputes otherwise"


def test_the_latest_implement_task_iteration_passes_every_expectation_with_the_shipped_skill():
    """The regression gate: the newest recorded iteration ran the skill as it ships, over every
    case, and passed. A change to the skill records a new iteration beside this one."""
    latest = max(IMPLEMENT.glob("iteration-*"), key=lambda p: int(p.name.split("-")[1]), default=None)
    assert latest, "no iteration is recorded"
    shipped = [p for p in latest.iterdir() if (p / "grading.json").is_file()
               and grading_of(p)["arm"].startswith("shipped:")]
    assert sorted({grading_of(p)["case"] for p in shipped}) == \
        sorted(p.parent.name for p in IMPLEMENT_CASES.glob("*/case.json")), \
        f"{latest.name} does not run the shipped skill over every case"
    for record in shipped:
        failed = [e["text"] for e in grading_of(record)["expectations"] if not e["passed"]]
        assert not failed, f"{record.name}: {failed}"


def test_the_checklist_is_what_carries_a_resumed_delivery_to_its_end():
    """The benefit the progress checklist was shipped for, as measured in iteration 1: over the
    resumed case, every run of the skill it replaced left a mechanical expectation unmet, and
    every run of the shipped skill met all of them. A later iteration need not re-run the old
    skill; this record is what the change was decided on."""
    runs = [p for p in (IMPLEMENT / "iteration-1").iterdir()
            if (p / "grading.json").is_file() and grading_of(p)["case"] == "compaction-resume"]
    before = [p for p in runs if grading_of(p)["arm"].startswith("before:")]
    shipped = [p for p in runs if grading_of(p)["arm"].startswith("shipped:")]
    assert len(before) >= 2 and len(shipped) >= 2, "the comparison needs two runs per arm"
    for record in before:
        mechanical = [e for e in grading_of(record)["expectations"] if e["text"].startswith("mechanical:")]
        assert any(not e["passed"] for e in mechanical), \
            f"{record.name} ran the old skill and met every mechanical expectation"
    for record in shipped:
        assert all(e["passed"] for e in grading_of(record)["expectations"]), record.name


def test_the_reading_quiz_has_one_answer_per_question_spread_over_the_letters():
    quiz = bench_implement_task.case("reading-quiz")
    keys = [bench_implement_task.quiz_options(q)[1] for q in quiz["questions"]]
    assert [q["id"] for q in quiz["questions"]] == list(range(1, len(keys) + 1))
    assert all(len(q["options"]) == 4 for q in quiz["questions"])
    assert len(set(keys)) == 4, f"the shuffled answers sit on {sorted(set(keys))} only"


def runs_of(iteration: str, case_name: str, arm: str) -> list[dict]:
    folder = IMPLEMENT / iteration
    return [grading_of(p) for p in sorted(folder.iterdir()) if (p / "grading.json").is_file()
            and grading_of(p)["case"] == case_name and grading_of(p)["arm"].startswith(arm)]


def test_the_5_62_0_rewrite_reads_as_well_for_less():
    """Iteration 2 compares the 5.62.0 rewrite with the 5.61.0 text it replaced, both read whole by
    fresh agents. Reading: every quiz run of both arms answered every question as the text decides
    — the quiz holds the rewrite to losing no meaning, and cannot show the old text misread.
    Cost: the rewrite's quiz runs spent fewer tokens than every run of the old text, since the
    agent reads all fifteen files once. Behaviour: the rewrite passes both delivery cases."""
    before = runs_of("iteration-2", "reading-quiz", "before:")
    shipped = runs_of("iteration-2", "reading-quiz", "shipped:")
    assert len(before) >= 2 and len(shipped) >= 2
    for grading in before + shipped:
        failed = [e["text"] for e in grading["expectations"] if not e["passed"]]
        assert not failed, f"{grading['run']}: {failed}"
    assert max(g["subagent_tokens"] for g in shipped) < min(g["subagent_tokens"] for g in before), \
        "the rewrite's quiz runs did not read for fewer tokens than the 5.61.0 text"
    for case_name in ("first-delivery", "compaction-resume"):
        for grading in runs_of("iteration-2", case_name, "shipped:"):
            assert all(e["passed"] for e in grading["expectations"]), grading["run"]


# ---------------------------------------------------------------- /plan-work: cases
# Plans over the implement-task benchmark's fixture project, its plan removed; graded by
# tools/bench_plan_work.py and recomputed here from each record.

import bench_plan_work  # noqa: E402

PLAN = BENCH / "plan-work"


def plan_runs() -> list[Path]:
    return sorted(p for it in sorted(PLAN.glob("iteration-*"))
                  for p in it.iterdir() if (p / "grading.json").is_file())


def plan_runs_of(iteration: str, case_name: str, arm: str) -> list[dict]:
    return [grading_of(p) for p in sorted((PLAN / iteration).iterdir())
            if (p / "grading.json").is_file() and grading_of(p)["case"] == case_name
            and grading_of(p)["arm"].startswith(arm)]


def test_every_plan_work_case_names_only_checks_the_grader_knows(tmp_path):
    names = sorted(p.parent.name for p in (PLAN / "cases").glob("*/case.json"))
    assert names == ["compaction-resume", "first-plan", "reading-quiz"]
    for name in names:
        project = tmp_path / name
        bench_plan_work.setup(name, project, bench_plan_work.SKILL)
        bench_plan_work.checks(name, project)


def test_the_resumed_plan_work_case_starts_where_step_4_ends(tmp_path):
    """The pre-written work root validates and derives: what is left is steps 5 and 6."""
    project = tmp_path / "compaction-resume"
    bench_plan_work.setup("compaction-resume", project, bench_plan_work.SKILL)
    work = project / "work" / bench_plan_work.SLUG
    assert not (work / "plan.json").exists()
    done = subprocess.run([sys.executable, "-B", str(REPO / "src/claude/bin/plan.py"),
                           str(work), str(project / "spec")], capture_output=True, text=True)
    assert done.returncode == 0, done.stdout + done.stderr


@pytest.mark.parametrize("run", [str(p.relative_to(PLAN)) for p in plan_runs()])
def test_each_plan_work_run_grades_as_recomputed_from_its_record(run):
    record = PLAN / run
    grading = grading_of(record)
    assert grading["arm"].split(":")[0] in ("shipped", "before"), f"{run}: arm {grading['arm']!r}"
    recomputed = {e["text"]: e["passed"] for e in bench_plan_work.checks(grading["case"], record)}
    for expectation in grading["expectations"]:
        assert recomputed[expectation["text"]] == expectation["passed"], \
            f"{run}: '{expectation['text']}' was recorded {expectation['passed']} and recomputes otherwise"


def test_the_latest_plan_work_iteration_passes_every_expectation_with_the_shipped_skill():
    latest = max(PLAN.glob("iteration-*"), key=lambda p: int(p.name.split("-")[1]), default=None)
    assert latest, "no iteration is recorded"
    shipped = [p for p in latest.iterdir() if (p / "grading.json").is_file()
               and grading_of(p)["arm"].startswith("shipped:")]
    assert sorted({grading_of(p)["case"] for p in shipped}) == \
        sorted(p.parent.name for p in (PLAN / "cases").glob("*/case.json")), \
        f"{latest.name} does not run the shipped skill over every case"
    for record in shipped:
        failed = [e["text"] for e in grading_of(record)["expectations"] if not e["passed"]]
        assert not failed, f"{record.name}: {failed}"


def test_the_5_65_0_plan_work_carries_a_resumed_plan_to_its_handoff_and_reads_for_less():
    """Iteration 1 compares the 5.65.0 rewrite with the 5.64.0 text. Resumed after step 4 holding
    the first 20,000 characters, every 5.64.0 run left a mechanical expectation unmet and every
    5.65.0 run met all of them. Every quiz run of both arms answered every question as the text
    decides, and the rewrite's quiz runs read for fewer tokens than every 5.64.0 run."""
    before = plan_runs_of("iteration-1", "compaction-resume", "before:")
    shipped = plan_runs_of("iteration-1", "compaction-resume", "shipped:")
    assert len(before) >= 2 and len(shipped) >= 2
    for grading in before:
        mechanical = [e for e in grading["expectations"] if e["text"].startswith("mechanical:")]
        assert any(not e["passed"] for e in mechanical), \
            f"{grading['run']} ran the old skill and met every mechanical expectation"
    for grading in shipped:
        assert all(e["passed"] for e in grading["expectations"]), grading["run"]
    quiz_before = plan_runs_of("iteration-1", "reading-quiz", "before:")
    quiz_shipped = plan_runs_of("iteration-1", "reading-quiz", "shipped:")
    assert len(quiz_before) >= 2 and len(quiz_shipped) >= 2
    for grading in quiz_before + quiz_shipped:
        assert all(e["passed"] for e in grading["expectations"]), grading["run"]
    assert max(g["subagent_tokens"] for g in quiz_shipped) < \
        min(g["subagent_tokens"] for g in quiz_before)


# ---------------------------------------------------------------- /review-change: cases
# Reviews the implement-task benchmark's recorded first delivery, laid over its fixture project and
# committed; graded by tools/bench_review_change.py and recomputed here from each record.

import bench_review_change  # noqa: E402

REVIEW = BENCH / "review-change"


def review_runs() -> list[Path]:
    return sorted(p for it in sorted(REVIEW.glob("iteration-*"))
                  for p in it.iterdir() if (p / "grading.json").is_file())


def review_runs_of(iteration: str, case_name: str, arm: str) -> list[dict]:
    return [grading_of(p) for p in sorted((REVIEW / iteration).iterdir())
            if (p / "grading.json").is_file() and grading_of(p)["case"] == case_name
            and grading_of(p)["arm"].startswith(arm)]


def test_every_review_change_case_names_only_checks_the_grader_knows(tmp_path):
    names = sorted(p.parent.name for p in (REVIEW / "cases").glob("*/case.json"))
    assert names == ["compaction-resume", "full-review", "reading-quiz"]
    for name in names:
        project = tmp_path / name
        bench_review_change.setup(name, project, bench_review_change.SKILL)
        bench_review_change.checks(name, project)


def test_the_review_change_fixture_holds_a_sound_delivery_to_review(tmp_path):
    """The recorded delivery laid over the fixture is what a review starts from: the plan and the
    delivery check clean, and the trace shows no drift."""
    project = tmp_path / "full-review"
    bench_review_change.setup("full-review", project, bench_review_change.SKILL)
    bins = REPO / "src/claude/bin"
    for args in (("plan.py", "--check", "work/lending", "spec"),
                 ("deliver.py", "--check", "delivery/lending", "work/lending", "app", "spec"),
                 ("trace.py", "--check", "app")):
        done = subprocess.run([sys.executable, "-B", str(bins / args[0]), *args[1:]],
                              capture_output=True, text=True, cwd=project)
        assert done.returncode == 0, done.stdout + done.stderr


def test_the_resumed_review_change_case_starts_where_step_3b_ends(tmp_path):
    """Staged, captured, folded and bound through the framework's own writers, uncommitted: what
    is left is compose, validate and report."""
    project = tmp_path / "compaction-resume"
    bench_review_change.setup("compaction-resume", project, bench_review_change.SKILL)
    assert (project / bench_review_change.RECONCILIATION).is_file()
    assert (project / f"delivery/lending/run/{bench_review_change.REVIEW}/run.json").is_file()
    assert not (project / bench_review_change.REVIEW_RECORD).exists()
    trace = json.loads((project / "siegard-trace.json").read_text(encoding="utf-8"))
    assert any(f.get("judged") for b in trace["bindings"] for f in b["files"])


@pytest.mark.parametrize("run", [str(p.relative_to(REVIEW)) for p in review_runs()])
def test_each_review_change_run_grades_as_recomputed_from_its_record(run):
    record = REVIEW / run
    grading = grading_of(record)
    assert grading["arm"].split(":")[0] in ("shipped", "before", "draft"), \
        f"{run}: arm {grading['arm']!r}"
    recomputed = {e["text"]: e["passed"] for e in bench_review_change.checks(grading["case"], record)}
    for expectation in grading["expectations"]:
        assert recomputed[expectation["text"]] == expectation["passed"], \
            f"{run}: '{expectation['text']}' was recorded {expectation['passed']} and recomputes otherwise"


def test_the_latest_review_change_iteration_passes_every_expectation_with_the_shipped_skill():
    latest = max(REVIEW.glob("iteration-*"), key=lambda p: int(p.name.split("-")[1]), default=None)
    assert latest, "no iteration is recorded"
    shipped = [p for p in latest.iterdir() if (p / "grading.json").is_file()
               and grading_of(p)["arm"].startswith("shipped:")]
    assert sorted({grading_of(p)["case"] for p in shipped}) == \
        sorted(p.parent.name for p in (REVIEW / "cases").glob("*/case.json")), \
        f"{latest.name} does not run the shipped skill over every case"
    for record in shipped:
        failed = [e["text"] for e in grading_of(record)["expectations"] if not e["passed"]]
        assert not failed, f"{record.name}: {failed}"


def test_the_review_change_reading_quiz_has_one_answer_per_question_spread_over_the_letters():
    questions = bench_review_change.case("reading-quiz")["questions"]
    assert [q["id"] for q in questions] == list(range(1, 19))
    keys = {bench_review_change.quiz_options(q)[1] for q in questions}
    assert keys == set("abcd")


def test_the_5_66_0_review_change_carries_a_resumed_review_to_its_handoff_and_reads_as_well():
    """Iteration 1 compares the 5.66.0 rewrite with the 5.65.0 text. Resumed after step 3b holding
    the first 20,000 characters, every 5.65.0 run left a mechanical expectation unmet and every
    5.66.0 run met all of them. Every quiz run of both arms answered every question as the text
    decides; the quiz does not separate the arms on cost, so it is held as no regression only."""
    before = review_runs_of("iteration-1", "compaction-resume", "before:")
    shipped = review_runs_of("iteration-1", "compaction-resume", "shipped:")
    assert len(before) >= 2 and len(shipped) >= 2
    for grading in before:
        mechanical = [e for e in grading["expectations"] if e["text"].startswith("mechanical:")]
        assert any(not e["passed"] for e in mechanical), \
            f"{grading['run']} ran the old skill and met every mechanical expectation"
    for grading in shipped:
        assert all(e["passed"] for e in grading["expectations"]), grading["run"]
    quiz = review_runs_of("iteration-1", "reading-quiz", "")
    assert len([g for g in quiz if g["arm"].startswith("before:")]) >= 2
    assert len([g for g in quiz if g["arm"].startswith("shipped:")]) >= 2
    for grading in quiz:
        assert all(e["passed"] for e in grading["expectations"]), grading["run"]


# ---------------------------------------------------------------- the reconcile benchmark
# tests/fixtures/benchmarks/reconcile: the review-change benchmark's seeded repository with a
# second commit editing lending/fees.py after its bind, so the trace reports `code` drift on it;
# graded by tools/bench_reconcile.py and recomputed here from each record.

import bench_reconcile  # noqa: E402

RECONCILE = BENCH / "reconcile"


def reconcile_runs() -> list[Path]:
    return sorted(p for it in sorted(RECONCILE.glob("iteration-*"))
                  for p in it.iterdir() if (p / "grading.json").is_file())


def reconcile_runs_of(iteration: str, case_name: str, arm: str) -> list[dict]:
    return [grading_of(p) for p in sorted((RECONCILE / iteration).iterdir())
            if (p / "grading.json").is_file() and grading_of(p)["case"] == case_name
            and grading_of(p)["arm"].startswith(arm)]


def test_every_reconcile_case_names_only_checks_the_grader_knows(tmp_path):
    names = sorted(p.parent.name for p in (RECONCILE / "cases").glob("*/case.json"))
    assert names == ["compaction-resume", "full-reconcile", "reading-quiz"]
    for name in names:
        project = tmp_path / name
        bench_reconcile.setup(name, project, bench_reconcile.SKILL)
        bench_reconcile.checks(name, project)


def test_the_reconcile_fixture_holds_code_drift_on_the_edited_file(tmp_path):
    """The specification and the trace check clean, the edit is committed, and `--check` reports
    the `code` drift a reconciliation exists to answer, on the one file the edit touched."""
    project = tmp_path / "full-reconcile"
    bench_reconcile.setup("full-reconcile", project, bench_reconcile.SKILL)
    bins = REPO / "src/claude/bin"
    for args in (("spec.py", "spec"), ("trace.py", "app")):
        done = subprocess.run([sys.executable, "-B", str(bins / args[0]), *args[1:]],
                              capture_output=True, text=True, cwd=project)
        assert done.returncode == 0, done.stdout + done.stderr
    done = subprocess.run([sys.executable, "-B", str(bins / "trace.py"), "--check", "app"],
                          capture_output=True, text=True, cwd=project)
    assert done.returncode != 0
    assert "app/lending/fees.py: the file changed without a rebind" in done.stdout
    assert "1 code over 1 file(s)" in done.stdout
    status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True,
                            cwd=project)
    assert status.stdout == ""


def test_the_resumed_reconcile_case_starts_where_step_4_ends(tmp_path):
    """Staged, the return saved, folded and validated through the framework's own writers,
    uncommitted: what is left is the bind and the report."""
    project = tmp_path / "compaction-resume"
    bench_reconcile.setup("compaction-resume", project, bench_reconcile.SKILL)
    assert (project / bench_reconcile.RECONCILIATION).is_file()
    assert (project / bench_reconcile.RETURNS / "lending__fees.py.yaml").is_file()
    trace = json.loads((project / "siegard-trace.json").read_text(encoding="utf-8"))
    assert not any(f.get("judged") for b in trace["bindings"] for f in b["files"])
    held = (project.parent / "compaction-resume.skill-after-compaction.md").read_text(
        encoding="utf-8")
    assert "--bind-record" in held and "handoff.py --render" in held


@pytest.mark.parametrize("run", [str(p.relative_to(RECONCILE)) for p in reconcile_runs()])
def test_each_reconcile_run_grades_as_recomputed_from_its_record(run):
    record = RECONCILE / run
    grading = grading_of(record)
    assert grading["arm"].split(":")[0] in ("shipped", "before", "draft"), \
        f"{run}: arm {grading['arm']!r}"
    recomputed = {e["text"]: e["passed"] for e in bench_reconcile.checks(grading["case"], record)}
    for expectation in grading["expectations"]:
        assert recomputed[expectation["text"]] == expectation["passed"], \
            f"{run}: '{expectation['text']}' was recorded {expectation['passed']} and recomputes otherwise"


def test_the_latest_reconcile_iteration_passes_every_expectation_with_the_shipped_skill():
    latest = max(RECONCILE.glob("iteration-*"), key=lambda p: int(p.name.split("-")[1]),
                 default=None)
    assert latest, "no iteration is recorded"
    shipped = [p for p in latest.iterdir() if (p / "grading.json").is_file()
               and grading_of(p)["arm"].startswith("shipped:")]
    assert sorted({grading_of(p)["case"] for p in shipped}) == \
        sorted(p.parent.name for p in (RECONCILE / "cases").glob("*/case.json")), \
        f"{latest.name} does not run the shipped skill over every case"
    for record in shipped:
        failed = [e["text"] for e in grading_of(record)["expectations"] if not e["passed"]]
        assert not failed, f"{record.name}: {failed}"


def test_the_reconcile_reading_quiz_has_one_answer_per_question_spread_over_the_letters():
    questions = bench_reconcile.case("reading-quiz")["questions"]
    assert [q["id"] for q in questions] == list(range(1, 19))
    keys = {bench_reconcile.quiz_options(q)[1] for q in questions}
    assert keys == set("abcd")


def test_the_5_67_0_reconcile_carries_a_resumed_reconciliation_to_its_handoff_and_reads_as_well():
    """Iteration 1 compares the 5.67.0 rewrite with the 5.66.0 text. Resumed after step 4 holding
    the first 20,000 characters, every 5.66.0 run left a mechanical expectation unmet and every
    5.67.0 run met all of them. Every quiz run of both arms answered every question as the text
    decides; the quiz does not separate the arms on cost, so it is held as no regression only."""
    before = reconcile_runs_of("iteration-1", "compaction-resume", "before:")
    shipped = reconcile_runs_of("iteration-1", "compaction-resume", "shipped:")
    assert len(before) >= 2 and len(shipped) >= 2
    for grading in before:
        mechanical = [e for e in grading["expectations"] if e["text"].startswith("mechanical:")]
        assert any(not e["passed"] for e in mechanical), \
            f"{grading['run']} ran the old skill and met every mechanical expectation"
    for grading in shipped:
        assert all(e["passed"] for e in grading["expectations"]), grading["run"]
    quiz = reconcile_runs_of("iteration-1", "reading-quiz", "")
    assert len([g for g in quiz if g["arm"].startswith("before:")]) >= 2
    assert len([g for g in quiz if g["arm"].startswith("shipped:")]) >= 2
    for grading in quiz:
        assert all(e["passed"] for e in grading["expectations"]), grading["run"]


# ---------------------------------------------------------------- the deliver-scope benchmark
# tests/fixtures/benchmarks/deliver-scope: the implement-task benchmark's fixture project, a
# telemetry root declared, committed as the seed; the ask names the reach epic/fees, so the plan
# step plans nothing. The skill commits, so each record carries every commit the run added above
# the seed. Graded by tools/bench_deliver_scope.py and recomputed here from each record.

import bench_deliver_scope  # noqa: E402

DELIVER = BENCH / "deliver-scope"


def deliver_runs() -> list[Path]:
    return sorted(p for it in sorted(DELIVER.glob("iteration-*"))
                  for p in it.iterdir() if (p / "grading.json").is_file())


def deliver_runs_of(iteration: str, case_name: str, arm: str) -> list[dict]:
    return [grading_of(p) for p in sorted((DELIVER / iteration).iterdir())
            if (p / "grading.json").is_file() and grading_of(p)["case"] == case_name
            and grading_of(p)["arm"].startswith(arm)]


def test_every_deliver_scope_case_names_only_checks_the_grader_knows(tmp_path):
    names = sorted(p.parent.name for p in (DELIVER / "cases").glob("*/case.json"))
    assert names == ["compaction-resume", "full-deliver", "reading-quiz"]
    for name in names:
        project = tmp_path / name
        bench_deliver_scope.setup(name, project, bench_deliver_scope.SKILL)
        bench_deliver_scope.checks(name, project)


def test_the_deliver_scope_fixture_holds_one_undelivered_task_under_the_reach(tmp_path):
    """The seed is clean, its specification and plan check, it declares every root the skill
    reads, and `--outstanding` over the reach lists the one task as deliverable once the
    initiative's delivery root exists."""
    project = tmp_path / "full-deliver"
    bench_deliver_scope.setup("full-deliver", project, bench_deliver_scope.SKILL)
    bins = REPO / "src/claude/bin"

    def run(*args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "-B", *args], capture_output=True, text=True,
                              cwd=project)
    assert run(str(bins / "spec.py"), "spec").returncode == 0
    assert run(str(bins / "plan.py"), "--check", "work/lending", "spec").returncode == 0
    declared = run(str(bins / "project.py"), ".").stdout
    for root in ("specification_root:", "work_root:", "delivery_root:", "telemetry_root:",
                 "standard:"):
        assert root in declared, declared
    (project / "delivery/lending").mkdir(parents=True)
    done = run(str(bins / "deliver.py"), "--outstanding", "delivery/lending", "work/lending",
               "app", "spec", "--scope", "epic/fees")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "task/fees/compute-late-fee" in done.stdout
    (project / "delivery/lending").rmdir()
    status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True,
                            cwd=project)
    assert status.stdout == ""


def test_the_resumed_deliver_scope_case_starts_where_step_4_ends(tmp_path):
    """The delivery and the review committed under the run's name, both validating, the review's
    log line left uncommitted: what is left is step 5, which has nothing to prove, the measure and
    the report."""
    project = tmp_path / "compaction-resume"
    bench_deliver_scope.setup("compaction-resume", project, bench_deliver_scope.SKILL)
    bins = REPO / "src/claude/bin"
    for args in (("--check", "delivery/lending", "work/lending", "app", "spec"),
                 ("--review", "lending", "delivery/lending", "work/lending", "app", "spec")):
        done = subprocess.run([sys.executable, "-B", str(bins / "deliver.py"), *args],
                              capture_output=True, text=True, cwd=project)
        assert done.returncode == 0, done.stdout + done.stderr
    commits = bench_deliver_scope.commits_above_seed(project)
    assert [k["subject"] for k in commits] == [
        "deliver-scope lending: deliver task/fees/compute-late-fee", "deliver-scope lending: review"]
    status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True,
                            cwd=project)
    assert sorted(status.stdout.splitlines()) == [" M delivery/lending/orchestration.md",
                                                  "?? telemetry/"]
    (asked,) = (project / "telemetry").glob("ask-*.md")
    assert asked.read_text(encoding="utf-8") == bench_deliver_scope.ASK
    read = (project.parent / "compaction-resume.ask-read.txt").read_text(encoding="utf-8")
    assert read.startswith("read: ") and str(asked) in read
    review = bench_deliver_scope.front(project / bench_deliver_scope.REVIEW_RECORD)
    assert "certifications" not in review or not review["certifications"]
    held = (project.parent / "compaction-resume.skill-after-compaction.md").read_text(
        encoding="utf-8")
    assert "telemetry.py --probe" in held


@pytest.mark.parametrize("run", [str(p.relative_to(DELIVER)) for p in deliver_runs()])
def test_each_deliver_scope_run_grades_as_recomputed_from_its_record(run):
    record = DELIVER / run
    grading = grading_of(record)
    assert grading["arm"].split(":")[0] in ("shipped", "before", "draft"), \
        f"{run}: arm {grading['arm']!r}"
    recomputed = {e["text"]: e["passed"]
                  for e in bench_deliver_scope.checks(grading["case"], record)}
    for expectation in grading["expectations"]:
        assert recomputed[expectation["text"]] == expectation["passed"], \
            f"{run}: '{expectation['text']}' was recorded {expectation['passed']} and recomputes otherwise"


def latest_deliver_iteration_of(case_name: str) -> str:
    held = [it for it in sorted(DELIVER.glob("iteration-*"), key=lambda p: int(p.name.split("-")[1]))
            if any(grading_of(p)["case"] == case_name for p in it.iterdir()
                   if (p / "grading.json").is_file())]
    assert held, f"no iteration records {case_name}"
    return held[-1].name


@pytest.mark.parametrize("case_name", sorted(p.parent.name for p in
                                             (DELIVER / "cases").glob("*/case.json")))
def test_the_latest_deliver_scope_iteration_of_each_case_passes_with_the_shipped_skill(case_name):
    """Iteration 2 re-runs only the resumed case, whose setup gained the recorded ask; each case
    is held to the latest iteration that recorded it."""
    shipped = deliver_runs_of(latest_deliver_iteration_of(case_name), case_name, "shipped:")
    assert shipped, f"{case_name}: no run of the shipped skill in its latest iteration"
    for grading in shipped:
        failed = [e["text"] for e in grading["expectations"] if not e["passed"]]
        assert not failed, f"{grading['run']}: {failed}"


def test_the_deliver_scope_reading_quiz_has_one_answer_per_question_spread_over_the_letters():
    questions = bench_deliver_scope.case("reading-quiz")["questions"]
    assert [q["id"] for q in questions] == list(range(1, 19))
    keys = {bench_deliver_scope.quiz_options(q)[1] for q in questions}
    assert keys == set("abcd")


def test_the_5_68_0_deliver_scope_carries_a_resumed_run_to_its_handoff_and_reads_as_well():
    """Iteration 2 resumes after step 4 holding the first 20,000 characters, the ask recorded:
    every 5.67.0 run left a mechanical expectation unmet and every 5.68.0 run met all of them.
    Iteration 1's quiz runs of both arms answered every question as the text decides; the quiz
    does not separate the arms on cost, so it is held as no regression only."""
    before = deliver_runs_of("iteration-2", "compaction-resume", "before:")
    shipped = deliver_runs_of("iteration-2", "compaction-resume", "shipped:")
    assert len(before) >= 2 and len(shipped) >= 2
    for grading in before:
        mechanical = [e for e in grading["expectations"] if e["text"].startswith("mechanical:")]
        assert any(not e["passed"] for e in mechanical), \
            f"{grading['run']} ran the old skill and met every mechanical expectation"
    for grading in shipped:
        assert all(e["passed"] for e in grading["expectations"]), grading["run"]
    quiz = deliver_runs_of("iteration-1", "reading-quiz", "")
    assert len([g for g in quiz if g["arm"].startswith("before:")]) >= 2
    assert len([g for g in quiz if g["arm"].startswith("shipped:")]) >= 2
    for grading in quiz:
        assert all(e["passed"] for e in grading["expectations"]), grading["run"]
