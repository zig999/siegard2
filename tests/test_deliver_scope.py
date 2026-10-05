"""The bounds that keep orchestration from harming the framework, held to the text that states them.

`/deliver-scope` is one of the two skills allowed to take the handoffs the others only offer and
to commit — `/adopt-scope` is the other, over the adoption route, held by its own module — two
grants every other entry point explicitly refuses. Nothing mechanical can
watch a session exercise them, so what this module holds is the next best thing: the sentences
that bound the grants must survive in the artifacts, character for character where a rewording
would change what a session does. `test_skill_contract.py` already holds the skill's frontmatter,
citations and vocabulary; this file holds only what is specific to the orchestration bounds.

The analyse gate is the load-bearing one. The whole design keeps exactly one human review gate —
the specification's diff — and the skill's text is the only thing that keeps an eager session
from amending the specification to unblock a run. A rewording that dropped it would ship a
framework whose one kept gate exists in nobody's context.
"""
from __future__ import annotations

import re
from pathlib import Path

import deliver

REPO = Path(__file__).resolve().parent.parent


def flat(path: str) -> str:
    """The file's text with whitespace collapsed, so a sentence may wrap without the guard
    reading the wrap as a rewording — the same normalisation the seam guard applies."""
    return re.sub(r"\s+", " ", (REPO / path).read_text(encoding="utf-8"))


SKILL = flat("src/claude/skills/deliver-scope/SKILL.md")


def test_the_skill_states_it_never_invokes_analyse():
    """The one gate the design keeps for a person, stated as an absolute in the skill's own text —
    in the body, where the bound is argued, and in the never-do list, where a session scanning for
    its limits reads first."""
    assert "never invokes `/analyse`" in SKILL, \
        "the analyse gate is gone from the skill's body; the one kept human gate is unstated"
    assert "Invoke `/analyse`" in SKILL, \
        "the never-do list no longer opens with the analyse gate"


def test_the_skill_pastes_and_never_composes():
    """The rule that makes the orchestrator thin: every invocation is a report's handoff, so the
    seam tests that hold the handoffs hold the orchestrator for free. A skill that composed its
    own invocations would be a second home for every other skill's input contract."""
    assert "Paste, never compose." in SKILL
    assert "never composes an invocation" in SKILL


def test_the_authorization_is_verbatim_and_never_inferred():
    """The gate that keeps reachability safe — the same one the corrective increment holds: the
    ask is the human's own words, quoted, and an inferred intent is a stop."""
    assert "quoted verbatim" in SKILL
    assert "never inferred" in SKILL


def test_every_commit_is_pathspec_scoped_and_nothing_sweeps_the_tree():
    """Commit authority is the sharpest grant here. Its bound is the pathspec: a run that swept
    the tree would bury a human's pending work under an orchestration message."""
    assert "names its paths" in SKILL and "none sweeps the tree" in SKILL
    assert "never creates a branch" in SKILL


def test_every_run_ends_measured_and_a_stop_does_not_skip_it():
    """The harness keeps the transcripts a run's cost is read from for a while, not for ever, and
    a run that ended at a stop is the one whose cost a retrospective most needs."""
    assert "`deliver-scope <slug>: measure`" in SKILL
    assert "telemetry.py --probe --since <the instant step 1 began>" in SKILL
    assert "A stop ends the route, never the measure" in SKILL


def test_the_run_ends_at_the_record_and_findings_are_never_acted_on():
    """`/review-change` produces evidence, never a verdict, and the orchestrator inherits the
    restraint: the run's end state is the record's existence. A text that promised a *clean*
    review would make the orchestrator the gate the review pass refuses to be."""
    assert "The review is done when its record is written" in SKILL
    assert "never acted on" in SKILL
    assert "review clean" not in SKILL


def test_the_orchestration_log_the_skill_names_is_the_one_the_validator_keeps():
    """The skill says the validator keeps `orchestration.md`; deliver.py is what keeps it. Two
    names for the marker, or a promise the code never held, is a run that ends at its own log."""
    assert f"`{deliver.ORCHESTRATION_FILE}` at the delivery root" in SKILL
    assert "the validator keeps it" in SKILL
