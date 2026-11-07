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
    "skill_chars": 26_000,
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
    "chars": 73_000,
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
