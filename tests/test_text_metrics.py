"""The implement-task skill, its references and its three agents, measured as a reader pays for them.

`tools/text_metrics.py` counts: characters, words per sentence, prose lines past 100 columns, the
synonyms one concept must not carry, and the length of every description a session loads. The
5.61.0 text was measured by the same function and recorded in
tests/fixtures/benchmarks/implement-task/text-metrics-5.61.0.json; 5.62.0 rewrote the text for
one term per concept, shorter sentences, a stated rule over its justification and descriptions
that name the trigger first (Anthropic's guidance for skills, prompts and subagents).

Two holds. Against the baseline, every measure the rewrite claimed is strictly better, so the
claim is checkable rather than told. Against the pins below, no measure grows silently: a change
that raises one raises its pin in the same change and says in its commit message what the growth
bought — the ratchet `tests/test_rules_health.py` keeps for the session rules.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import text_metrics  # noqa: E402

BASELINE = REPO / "tests/fixtures/benchmarks/implement-task/text-metrics-5.61.0.json"
AGENTS = ("task-implementer", "test-author", "failure-diagnostician")

PINS = {
    "chars": 103_000,
    "skill_chars": 19_900,
    "sentence_words_median": 18,
    "sentence_words_p90": 35,
    "sentences_over_60_words": 3,
    "prose_lines_over_100": 0,
}
DESCRIPTION_PIN = 520


def current() -> dict:
    return text_metrics.measure(text_metrics.files_of(REPO / "src/claude", "implement-task", AGENTS))


def baseline() -> dict:
    return json.loads(BASELINE.read_text(encoding="utf-8"))


def test_the_baseline_measures_the_same_files():
    assert baseline()["files"] == current()["files"] == 15


@pytest.mark.parametrize("measure", ["chars", "skill_chars", "sentence_words_median",
                                     "sentence_words_p90", "sentence_words_max",
                                     "sentences_over_60_words", "prose_lines_over_100"])
def test_the_rewrite_is_strictly_better_than_5_61_0(measure):
    before, now = baseline()[measure], current()[measure]
    assert now < before, f"{measure}: {now} is not below 5.61.0's {before}"


@pytest.mark.parametrize("concept", sorted(text_metrics.SYNONYMS))
def test_one_concept_carries_one_name(concept):
    """The synonyms are schemas/terms.json's `forbidden` variants. 5.61.0 called the decider
    `the human` 21 times beside `the person`, a spawned agent a `delegation` 17 times beside
    `subagent`, and the test-author agent `test author` 8 times, quotations left out."""
    assert baseline()["synonyms"].get(concept, 0) > 0, \
        "the baseline lost the drift this test exists for"
    assert current()["synonyms"][concept] == 0, \
        f"a synonym of '{concept}' is back: {text_metrics.SYNONYMS[concept]}"


@pytest.mark.parametrize("name", ["skill", *AGENTS])
def test_every_description_is_shorter_than_5_61_0_and_under_its_pin(name):
    before, now = baseline()["description_chars"][name], current()["description_chars"][name]
    assert now < before, f"{name}: description {now} chars is not below 5.61.0's {before}"
    assert now <= DESCRIPTION_PIN, f"{name}: description {now} chars passes the pin {DESCRIPTION_PIN}"


def test_the_skill_description_names_its_trigger_first():
    """Claude Code truncates a skill listing; the key use case leads (code.claude.com skills)."""
    import yaml
    text = (REPO / "src/claude/skills/implement-task/SKILL.md").read_text(encoding="utf-8")
    front = yaml.safe_load(text.split("---", 2)[1])
    assert front["description"].startswith("Use when "), front["description"][:60]


@pytest.mark.parametrize("measure", sorted(PINS))
def test_no_measure_grows_past_its_pin(measure):
    now = current()[measure]
    assert now <= PINS[measure], \
        f"{measure} grew to {now}, past its pin {PINS[measure]}: raise the pin in the same change " \
        f"and say in the commit what the growth bought"


# ---------------------------------------------------------------- plan-work, rewritten at 5.65.0
PLAN_AGENTS = ("backlog-decomposer", "codebase-surveyor", "execution-contract-binder",
               "unstated-fact-decider")
PLAN_BASELINE = REPO / "tests/fixtures/benchmarks/plan-work/text-metrics-5.64.0.json"
PLAN_PINS = {
    "chars": 73_613,
    "skill_chars": 19_500,
    "sentence_words_median": 17,
    "sentence_words_p90": 35,
    "sentences_over_60_words": 3,
    "prose_lines_over_100": 0,
}
PLAN_DESCRIPTION_PIN = 561


def plan_current() -> dict:
    return text_metrics.measure(text_metrics.files_of(REPO / "src/claude", "plan-work", PLAN_AGENTS))


def plan_baseline() -> dict:
    return json.loads(PLAN_BASELINE.read_text(encoding="utf-8"))


@pytest.mark.parametrize("measure", ["chars", "skill_chars", "sentence_words_median",
                                     "sentence_words_p90", "sentence_words_max",
                                     "sentences_over_60_words", "prose_lines_over_100"])
def test_the_plan_work_rewrite_is_strictly_better_than_5_64_0(measure):
    before, now = plan_baseline()[measure], plan_current()[measure]
    assert now < before, f"plan-work {measure}: {now} is not below 5.64.0's {before}"


@pytest.mark.parametrize("name", ["skill", *PLAN_AGENTS])
def test_every_plan_work_description_is_shorter_than_5_64_0_and_under_its_pin(name):
    before = plan_baseline()["description_chars"][name]
    now = plan_current()["description_chars"][name]
    assert now < before, f"{name}: description {now} chars is not below 5.64.0's {before}"
    assert now <= PLAN_DESCRIPTION_PIN, f"{name}: description {now} passes {PLAN_DESCRIPTION_PIN}"


@pytest.mark.parametrize("measure", sorted(PLAN_PINS))
def test_no_plan_work_measure_grows_past_its_pin(measure):
    now = plan_current()[measure]
    assert now <= PLAN_PINS[measure], \
        f"plan-work {measure} grew to {now}, past its pin {PLAN_PINS[measure]}: raise the pin in " \
        f"the same change and say in the commit what the growth bought"


def test_the_plan_work_skill_names_its_trigger_first():
    import yaml
    text = (REPO / "src/claude/skills/plan-work/SKILL.md").read_text(encoding="utf-8")
    assert yaml.safe_load(text.split("---", 2)[1])["description"].startswith("Use when ")


# ---------------------------------------------------------------- review-change, rewritten at 5.66.0
REVIEW_AGENTS = ("coverage-auditor", "specification-conformance-reviewer",
                 "standard-conformance-reviewer")
REVIEW_BASELINE = REPO / "tests/fixtures/benchmarks/review-change/text-metrics-5.65.0.json"
REVIEW_PINS = {
    "chars": 90_608,
    "skill_chars": 19_850,
    "sentence_words_median": 19,
    "sentence_words_p90": 37,
    "sentences_over_60_words": 1,
    "prose_lines_over_100": 0,
}
REVIEW_DESCRIPTION_PIN = 572


def review_current() -> dict:
    return text_metrics.measure(text_metrics.files_of(REPO / "src/claude", "review-change",
                                                      REVIEW_AGENTS))


def review_baseline() -> dict:
    return json.loads(REVIEW_BASELINE.read_text(encoding="utf-8"))


@pytest.mark.parametrize("measure", ["chars", "skill_chars", "sentence_words_median",
                                     "sentence_words_p90", "sentence_words_max",
                                     "sentences_over_60_words", "prose_lines_over_100"])
def test_the_review_change_rewrite_is_strictly_better_than_5_65_0(measure):
    before, now = review_baseline()[measure], review_current()[measure]
    assert now < before, f"review-change {measure}: {now} is not below 5.65.0's {before}"


@pytest.mark.parametrize("name", ["skill", *REVIEW_AGENTS])
def test_every_review_change_description_is_shorter_than_5_65_0_and_under_its_pin(name):
    before = review_baseline()["description_chars"][name]
    now = review_current()["description_chars"][name]
    assert now < before, f"{name}: description {now} chars is not below 5.65.0's {before}"
    assert now <= REVIEW_DESCRIPTION_PIN, f"{name}: description {now} passes {REVIEW_DESCRIPTION_PIN}"


@pytest.mark.parametrize("measure", sorted(REVIEW_PINS))
def test_no_review_change_measure_grows_past_its_pin(measure):
    now = review_current()[measure]
    assert now <= REVIEW_PINS[measure], \
        f"review-change {measure} grew to {now}, past its pin {REVIEW_PINS[measure]}: raise the " \
        f"pin in the same change and say in the commit what the growth bought"


def test_the_review_change_skill_names_its_trigger_first():
    import yaml
    text = (REPO / "src/claude/skills/review-change/SKILL.md").read_text(encoding="utf-8")
    assert yaml.safe_load(text.split("---", 2)[1])["description"].startswith("Use when ")


# ---------------------------------------------------------------- reconcile, rewritten at 5.67.0
# The two agents were rewritten at 5.66.0 and are unchanged here: they enter the measure as the
# context a reconciliation reads, and the gain held below is the skill's.
RECONCILE_AGENTS = ("coverage-auditor", "specification-conformance-reviewer")
RECONCILE_BASELINE = REPO / "tests/fixtures/benchmarks/reconcile/text-metrics-5.66.0.json"
RECONCILE_PINS = {
    "chars": 82_555,
    "skill_chars": 17_127,
    "sentence_words_median": 19,
    "sentence_words_p90": 38,
    "sentences_over_60_words": 1,
    "prose_lines_over_100": 0,
}
RECONCILE_DESCRIPTION_PIN = 582


def reconcile_current() -> dict:
    return text_metrics.measure(text_metrics.files_of(REPO / "src/claude", "reconcile",
                                                      RECONCILE_AGENTS))


def reconcile_baseline() -> dict:
    return json.loads(RECONCILE_BASELINE.read_text(encoding="utf-8"))


@pytest.mark.parametrize("measure", ["chars", "skill_chars", "sentence_words_median",
                                     "sentence_words_p90", "sentence_words_max",
                                     "sentences_over_60_words", "prose_lines_over_100"])
def test_the_reconcile_rewrite_is_strictly_better_than_5_66_0(measure):
    before, now = reconcile_baseline()[measure], reconcile_current()[measure]
    assert now < before, f"reconcile {measure}: {now} is not below 5.66.0's {before}"


def test_the_reconcile_description_is_shorter_than_5_66_0_and_under_its_pin():
    before = reconcile_baseline()["description_chars"]["skill"]
    now = reconcile_current()["description_chars"]["skill"]
    assert now < before, f"reconcile: description {now} chars is not below 5.66.0's {before}"
    assert now <= RECONCILE_DESCRIPTION_PIN, \
        f"reconcile: description {now} passes {RECONCILE_DESCRIPTION_PIN}"


@pytest.mark.parametrize("measure", sorted(RECONCILE_PINS))
def test_no_reconcile_measure_grows_past_its_pin(measure):
    now = reconcile_current()[measure]
    assert now <= RECONCILE_PINS[measure], \
        f"reconcile {measure} grew to {now}, past its pin {RECONCILE_PINS[measure]}: raise the " \
        f"pin in the same change and say in the commit what the growth bought"


def test_the_reconcile_skill_names_its_trigger_first():
    import yaml
    text = (REPO / "src/claude/skills/reconcile/SKILL.md").read_text(encoding="utf-8")
    assert yaml.safe_load(text.split("---", 2)[1])["description"].startswith("Use when ")


def test_the_reconcile_terms_are_schemas_terms_json_s_and_each_is_used_outside_its_section():
    """`## Terms` defines each term by schemas/terms.json's `means`, verbatim, and names no term
    the skill and its references never use elsewhere."""
    import re
    means = {c["term"].lower(): c["means"] for c in
             json.loads((REPO / "schemas/terms.json").read_text(encoding="utf-8"))["concepts"]}
    folder = REPO / "src/claude/skills/reconcile"
    skill = (folder / "SKILL.md").read_text(encoding="utf-8")
    section = skill.split("## Terms\n", 1)[1].split("\n## ", 1)[0]
    rest = skill.replace(section, "") + "".join(
        p.read_text(encoding="utf-8") for p in sorted(folder.glob("references/*.md")))
    entries = re.findall(r"^- \*\*(.+?)\*\* — (.+?)\.(?: |$)", section, re.M)
    assert entries, "reconcile's ## Terms holds no entry"
    for term, said in entries:
        assert term.lower() in means, f"{term} is not a term schemas/terms.json lists"
        assert said == means[term.lower()], f"{term}: {said!r} is not terms.json's means"
        assert re.search(rf"\b{re.escape(term.lower())}\b", rest.lower()), \
            f"{term} is never used outside ## Terms"


# ---------------------------------------------------------------- deliver-scope, rewritten at 5.68.0
# Its one agent, door-decider, gained a description in the form the other agents carry and lost a
# paragraph of justification; it enters the measure as the context a judged choice reads.
DELIVER_AGENTS = ("door-decider",)
DELIVER_BASELINE = REPO / "tests/fixtures/benchmarks/deliver-scope/text-metrics-5.67.0.json"
DELIVER_PINS = {
    "chars": 34_360,
    "skill_chars": 16_700,
    "sentence_words_median": 19,
    "sentence_words_p90": 35,
    "sentences_over_60_words": 3,
    "prose_lines_over_100": 0,
}
DELIVER_DESCRIPTION_PIN = 606


def deliver_current() -> dict:
    return text_metrics.measure(text_metrics.files_of(REPO / "src/claude", "deliver-scope",
                                                      DELIVER_AGENTS))


def deliver_baseline() -> dict:
    return json.loads(DELIVER_BASELINE.read_text(encoding="utf-8"))


@pytest.mark.parametrize("measure", ["chars", "skill_chars", "sentence_words_median",
                                     "sentence_words_p90", "sentence_words_max",
                                     "sentences_over_60_words", "prose_lines_over_100"])
def test_the_deliver_scope_rewrite_is_strictly_better_than_5_67_0(measure):
    before, now = deliver_baseline()[measure], deliver_current()[measure]
    assert now < before, f"deliver-scope {measure}: {now} is not below 5.67.0's {before}"


@pytest.mark.parametrize("name", ["skill", "door-decider"])
def test_every_deliver_scope_description_is_shorter_than_5_67_0_and_under_its_pin(name):
    before = deliver_baseline()["description_chars"][name]
    now = deliver_current()["description_chars"][name]
    assert now < before, f"deliver-scope {name}: description {now} chars is not below {before}"
    assert now <= DELIVER_DESCRIPTION_PIN, \
        f"deliver-scope {name}: description {now} passes {DELIVER_DESCRIPTION_PIN}"


@pytest.mark.parametrize("measure", sorted(DELIVER_PINS))
def test_no_deliver_scope_measure_grows_past_its_pin(measure):
    now = deliver_current()[measure]
    assert now <= DELIVER_PINS[measure], \
        f"deliver-scope {measure} grew to {now}, past its pin {DELIVER_PINS[measure]}: raise " \
        f"the pin in the same change and say in the commit what the growth bought"


def test_the_deliver_scope_skill_names_its_trigger_first():
    import yaml
    text = (REPO / "src/claude/skills/deliver-scope/SKILL.md").read_text(encoding="utf-8")
    description = yaml.safe_load(text.split("---", 2)[1])["description"]
    assert description.startswith("Use when ") and ": " not in description


def test_the_deliver_scope_terms_are_schemas_terms_json_s_and_each_is_used_outside_its_section():
    """`## Terms` defines each term by schemas/terms.json's `means`, verbatim, and names no term
    the skill and its references never use elsewhere."""
    import re
    means = {c["term"].lower(): c["means"] for c in
             json.loads((REPO / "schemas/terms.json").read_text(encoding="utf-8"))["concepts"]}
    folder = REPO / "src/claude/skills/deliver-scope"
    skill = (folder / "SKILL.md").read_text(encoding="utf-8")
    section = skill.split("## Terms\n", 1)[1].split("\n## ", 1)[0]
    rest = skill.replace(section, "") + "".join(
        p.read_text(encoding="utf-8") for p in sorted(folder.glob("references/*.md")))
    entries = re.findall(r"^- \*\*(.+?)\*\* — (.+?)\.(?: |$)", section, re.M)
    assert entries, "deliver-scope's ## Terms holds no entry"
    for term, said in entries:
        assert term.lower() in means, f"{term} is not a term schemas/terms.json lists"
        assert said == means[term.lower()], f"{term}: {said!r} is not terms.json's means"
        assert re.search(rf"\b{re.escape(term.lower())}\b", rest.lower()), \
            f"{term} is never used outside ## Terms"


# ---------------------------------------------------------------- implement-task, wave B at 5.69.0
# The same fifteen files as the 5.62.0 section above, measured against the 5.68.0 text: SKILL.md
# fits the compaction cut, the two spawn blocks moved into references/delegation.md, and the three
# agents are untouched. A rewrite that moves text is held to falling in characters and to growing
# in no other measure.
IMPLEMENT_B_BASELINE = REPO / "tests/fixtures/benchmarks/implement-task/text-metrics-5.68.0.json"
IMPLEMENT_B_PINS = {
    "chars": 101_143,
    "skill_chars": 19_900,
    "sentence_words_median": 18,
    "sentence_words_p90": 35,
    "sentences_over_60_words": 3,
    "prose_lines_over_100": 0,
}


def implement_b_baseline() -> dict:
    return json.loads(IMPLEMENT_B_BASELINE.read_text(encoding="utf-8"))


@pytest.mark.parametrize("measure", ["chars", "skill_chars"])
def test_the_implement_task_wave_b_is_strictly_shorter_than_5_68_0(measure):
    before, now = implement_b_baseline()[measure], current()[measure]
    assert now < before, f"implement-task {measure}: {now} is not below 5.68.0's {before}"


@pytest.mark.parametrize("measure", ["sentence_words_median", "sentence_words_p90",
                                     "sentence_words_max", "sentences_over_60_words",
                                     "prose_lines_over_100"])
def test_the_implement_task_wave_b_is_no_worse_than_5_68_0(measure):
    before, now = implement_b_baseline()[measure], current()[measure]
    assert now <= before, f"implement-task {measure}: {now} is above 5.68.0's {before}"


@pytest.mark.parametrize("name", ["skill", *AGENTS])
def test_no_implement_task_description_grew_past_5_68_0(name):
    before = implement_b_baseline()["description_chars"][name]
    assert current()["description_chars"][name] <= before


@pytest.mark.parametrize("measure", sorted(IMPLEMENT_B_PINS))
def test_no_implement_task_measure_grows_past_its_5_69_0_pin(measure):
    now = current()[measure]
    assert now <= IMPLEMENT_B_PINS[measure], \
        f"implement-task {measure} grew to {now}, past its pin {IMPLEMENT_B_PINS[measure]}: raise " \
        f"the pin in the same change and say in the commit what the growth bought"
