"""The bounds that keep the adoption orchestrator from harming the framework, held to the text
that states them. `/adopt-scope` is the second skill allowed to take the handoffs the others
only offer, and to commit — over the adoption route alone. It differs from `/deliver-scope` on
one load-bearing sentence: it invokes `/analyse`, because writing the specification from adopted
source is its route, and what replaces the diff review a person gave before the commit is the
ledger, the decision log and the report. Nothing mechanical can watch a session exercise the
grants, so this module holds the sentences that bound them, character for character where a
rewording would change what a session does."""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def flat(path: str) -> str:
    return re.sub(r"\s+", " ", (REPO / path).read_text(encoding="utf-8"))


SKILL = flat("src/claude/skills/adopt-scope/SKILL.md")


def test_the_skill_invokes_analyse_only_over_its_own_survey():
    """The one place this route differs from a delivery's, stated in the body and in the never-do
    list: the analysis runs, and only over the material this run's survey wrote."""
    assert "This skill invokes `/analyse`, and only inside the ask" in SKILL
    assert "Invoke `/analyse` over anything but the material this run's survey wrote" in SKILL
    assert "«Every fact line of the material lands in a node or is left out with a stated reason» (SPEC-005 R8)" in SKILL, \
        "the ledger is what stands in for the diff review; the skill must say so in the spec's words"


def test_the_skill_never_plans_or_delivers():
    assert "never invokes is `/plan-work`, `/implement-task`, `/review-change` or `/deliver-scope`" in SKILL
    assert "Invoke `/plan-work`, `/implement-task`, `/review-change` or `/deliver-scope`" in SKILL
    assert "«Adoption changes no source» (SPEC-005 R6)" in SKILL


def test_the_skill_pastes_and_never_composes():
    assert "Paste, never compose." in SKILL
    assert "never composes an invocation" in SKILL


def test_the_authorization_is_verbatim_and_never_inferred():
    assert "quoted verbatim" in SKILL
    assert "never inferred" in SKILL


def test_every_commit_is_pathspec_scoped_and_nothing_sweeps_the_tree():
    assert "names its paths" in SKILL and "none sweeps the tree" in SKILL
    assert "never creates a branch" in SKILL
    for message in ("survey", "analyse", "adopt", "measure"):
        assert f"`adopt-scope <slug>: {message}`" in SKILL


def test_findings_and_decisions_are_relayed_and_never_acted_on():
    assert "no repair of any finding" in SKILL
    assert "no certification it proposed" in SKILL
    assert "What does not end the run, and is relayed whole instead" in SKILL


def test_the_orchestration_log_sits_with_the_survey_and_nothing_validates_it():
    assert "`orchestration.md` at `siegard-survey/<slug>/`" in SKILL
    assert "nothing reads that directory but the files named to `trace.py --survey` and `--ledger`" in SKILL
