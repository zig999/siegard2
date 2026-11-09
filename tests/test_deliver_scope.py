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
    assert f"`{deliver.ORCHESTRATION_FILE}` at the initiative's delivery root, `<delivery_root>/<slug>/`" in SKILL
    assert "the validator keeps it" in SKILL


def test_under_a_goal_the_judgment_is_the_blind_deciders_and_the_reserved_questions_stay():
    """SPEC-006 R7: a goal takes a derived door itself and a judged one only as the door decider
    returned it; the decider never sees the condition, and the three questions R3 reserves are
    never taken. A rewording that dropped any of the three would hand the judgment back to the
    context the goal pushes toward ending. The goal's branches live in references/goal.md, which
    the skill names at the gate and at step 3."""
    assert "references/goal.md" in SKILL
    section = flat("src/claude/skills/deliver-scope/references/goal.md")
    assert "`decided: <door> — <criterion> — <deciding fact>`" in section
    assert "`siegard:door-decider`" in section
    assert "Never the conversation, never the attempts' story, never what ends the goal" in section
    assert ("a contradiction, two readings of one piece of evidence, a finding's worth — is never "
            "taken") in section


def test_the_one_analyse_a_goal_may_ask_for_is_bounded():
    """SPEC-008 R10: under a goal that asks to specify, /analyse runs once, before the plan,
    over the objective as the person armed it — never to unblock a stop, and its two stops over
    no fact and no change read from a line, not from prose."""
    text = flat("src/claude/skills/deliver-scope/SKILL.md")
    assert "never invokes `/analyse`" in text
    assert "`/analyse` once, before the plan and never to unblock a stop" in text
    assert "references/goal.md" in text
    section = flat("src/claude/skills/deliver-scope/references/goal.md")
    assert "`stop: no-fact —` or `stop: no-change —` is nothing to specify" in section
    assert "`analyse <slug>: specify`" in section, "the analysis commits itself (SPEC-010 R7)"
    analyse = flat("src/claude/skills/analyse/SKILL.md")
    assert "`stop: no-fact — <what the material would have to state>`" in analyse


DOORS = flat("src/claude/skills/deliver-scope/references/doors.md")


def test_a_derived_door_is_taken_under_the_ask_that_invoked_the_run():
    """SPEC-006 R7: the ask that invoked the route is the go-ahead for a derived door, with or
    without a goal. Measured on 2026-11-09 over five sales consumers: no goal was armed in any run
    of the window, and every stop handing a door a fact decided waited for "siga", "Sim" or "Pq
    parou?". The bounds stay in the text: the door's own entry point accepts it, the same door
    over the same task once, and the judged door and the three reserved questions never."""
    assert "references/doors.md" in SKILL
    assert "the go-ahead, with or without a goal" in DOORS
    assert "SPEC-006 R7" in DOORS
    assert "`door.py --check` accepts" in DOORS
    assert "no `decided:` line of this run took over the same task" in DOORS
    assert "A judged door is `references/goal.md`'s" in DOORS
    assert "the three reserved questions are never taken" in DOORS
    assert "`decided: <door> — <criterion> — <deciding fact>`" in DOORS
    assert "take its derived door (`references/doors.md`)" in SKILL


def test_a_record_the_writer_refused_is_reconciled_and_delivered_again_once():
    """SPEC-004 R20: the reconciliation the record writer names is the delivery's one door, taken
    once per task; it is committed with the passed runs the stopped delivery left, so the task's
    next delivery starts from a clean tree, and a second refusal ends the run as the person's."""
    assert "**A record carrying `stands` the writer refused**" in DOORS
    assert "from the writer's `door:` line" in DOORS
    assert "`deliver-scope <slug>: runs <task>`" in DOORS, "the stopped delivery's runs"
    assert "each `passed`" in DOORS
    assert "A second refusal ends the run" in DOORS
    stops = flat("src/claude/skills/deliver-scope/references/stops.md")
    assert ("a task found already met that the record writer refuses again after its "
            "reconciliation") in stops
    assert "where the door the trace decides is not one this run takes" not in stops


def test_the_re_bind_and_the_decided_fact_are_taken_without_a_goal():
    """SPEC-008 R8 holds in an orchestrating run under a goal or under the ask alike; the two
    sections left the goal's file for the doors' file, and the goal's file names what a goal
    still changes alone."""
    assert "**A task waiting on a re-bind**" in DOORS and "**A fact no node states**" in DOORS
    assert "it commits what it wrote" in DOORS, "each door's skill commits itself (SPEC-010 R7)"
    goal = flat("src/claude/skills/deliver-scope/references/goal.md")
    assert "## A task waiting on a re-bind" not in goal
    assert "## A derived recommendation" not in goal
    assert "the derived doors stay this run's either way" in goal
    decided_fact = flat("src/claude/skills/plan-work/references/decided-fact.md")
    assert "A `/deliver-scope` run takes this one, with or without a goal" in decided_fact


def test_each_skill_the_run_invokes_commits_itself_and_the_run_commits_its_log():
    """SPEC-010 R7. Read on 2026-11-09: 92 of the person's messages over one week authorized a
    commit, nearly all after a route skill run alone. The orchestrator keeps its own commits — the
    log before each invocation, so the next skill finds its roots clean, the measure, and a stopped
    delivery's runs — and never the skills' own."""
    assert "Each skill this run invokes commits what it wrote itself, under its own name" in SKILL
    assert "`deliver-scope <slug>: log`, before each invocation" in SKILL
    assert "`plan-work <slug>: plan`" in SKILL and "`implement-task <slug>: deliver <task>`" in SKILL
    assert "`deliver-scope <slug>: deliver <task>`" not in SKILL
