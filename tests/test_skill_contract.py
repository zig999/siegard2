"""Every skill stays bound to its contract: it cites what exists, and restates nothing.

The last test is the unusual one. Every closed-vocabulary value the shipped contracts declare must
be absent from every skill's text — a value listed in a prompt is a second home the moment the
schema changes, and the prompt is the copy nothing validates. The subject is the union of all of
them rather than each skill's own, for two reasons: a skill has no more business restating another
root's vocabulary than its own, and two of the contracts happen to declare no hyphenated value at
all, which would leave a per-skill guard with nothing to check. Only hyphenated values are checked:
they are distinctive tokens, where bare words like `core`, `task`, `covered` or `standard` occur in
ordinary prose.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
CITATION = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([\w./-]+)")
FENCE = re.compile(r"^---\n(.*?)\n---\n", re.S)

NODE_CONTRACTS = ("schemas/plan-node.json", "schemas/delivery-node.json",
                  "schemas/standard.json", "schemas/spec/context.json",
                  "schemas/spec/element.json", "schemas/spec/rule.json",
                  "schemas/spec/scenario.json", "schemas/spec/contract.json",
                  "schemas/spec/constraint.json", "schemas/spec/decision-log.json")

SKILLS = {
    "analyse": {"contract": "schemas/spec/element.json", "validator": "bin/spec.py",
               "delegates": []},
    "siegard-config": {"contract": "schemas/project.json", "validator": "bin/project.py",
                       "delegates": []},
    "deliver-scope": {"contract": "schemas/plan.json", "validator": "bin/deliver.py",
                      "delegates": ["door-decider"]},
    "plan-work": {"contract": "schemas/plan-node.json", "validator": "bin/plan.py",
                  "delegates": ["codebase-surveyor", "backlog-decomposer",
                                "execution-contract-binder", "unstated-fact-decider"]},
    "implement-task": {"contract": "schemas/delivery-node.json", "validator": "bin/deliver.py",
                       "delegates": ["task-implementer", "test-author",
                                     "failure-diagnostician"]},
    "review-change": {"contract": "schemas/delivery-node.json", "validator": "bin/deliver.py",
                      "delegates": ["coverage-auditor", "specification-conformance-reviewer",
                                    "standard-conformance-reviewer", "failure-diagnostician"]},
    "reconcile": {"contract": "schemas/reconciliation.json", "validator": "bin/trace.py",
                  "delegates": ["specification-conformance-reviewer", "coverage-auditor"]},
    "siegard-status": {"contract": "schemas/project.json", "validator": "bin/project.py",
                       "delegates": []},
    "siegard-progress": {"contract": "schemas/plan.json", "validator": "bin/deliver.py",
                         "delegates": []},
    "siegard-goal": {"contract": "schemas/plan.json", "validator": "bin/goal.py",
                     "delegates": []},
    "siegard-archive": {"contract": "schemas/plan.json", "validator": "bin/plan.py",
                        "delegates": []},
    "siegard-standard": {"contract": "schemas/standard.json", "validator": "bin/deliver.py",
                         "delegates": []},
    "check-source": {"contract": "schemas/check.json", "validator": "bin/deliver.py",
                     "delegates": ["standard-conformance-reviewer"]},
    "siegard-telemetry": {"contract": "schemas/telemetry.json", "validator": "bin/telemetry.py",
                          "delegates": []},
    "survey": {"contract": "schemas/survey.json", "validator": "bin/trace.py",
               "also": ["schemas/intent.json"],
               "delegates": ["domain-surveyor", "test-intent-reader"]},
    "adopt-scope": {"contract": "schemas/ledger.json", "validator": "bin/trace.py",
                    "delegates": []},
    "clarify-request": {"contract": "schemas/clarified-request.json",
                        "validator": "bin/clarify.py", "delegates": []},
}


@pytest.fixture(params=sorted(SKILLS), scope="module")
def case(request) -> dict:
    name = request.param
    pairing = SKILLS[name]
    text = (REPO / "src/claude/skills" / name / "SKILL.md").read_text(encoding="utf-8")
    schema = json.loads((REPO / "src/claude" / pairing["contract"]).read_text(encoding="utf-8"))
    return {"name": name, "text": text, "schema": schema, **pairing}


def test_the_frontmatter_parses_and_names_the_skill(case):
    """A description holding an unquoted `: ` is not a description — it is a mapping the loader
    refuses, and the skill never loads at all. Cheap to write and cheap to break."""
    import yaml
    match = FENCE.match(case["text"])
    assert match, f"{case['name']} carries no frontmatter fence"
    front = yaml.safe_load(match.group(1))
    assert isinstance(front, dict), f"{case['name']}: frontmatter is not a mapping"
    assert front.get("name") == case["name"], \
        "a skill whose name is not its directory's breaks path-based traceability"
    assert isinstance(front.get("description"), str) and front["description"], \
        f"{case['name']}: the description is the trigger, and it must be a non-empty string"


@pytest.fixture(scope="module")
def skill_schema():
    from jsonschema import Draft202012Validator
    return Draft202012Validator(
        json.loads((REPO / "schemas/skill.json").read_text(encoding="utf-8")))


MODEL_MAY_REACH = {
    "analyse": True,
    # Reachable because its gate is inside it, the same way the corrective increment's is: the
    # ask must be the human's own words stating the whole route, quoted verbatim, and an intent
    # inferred from anything less is the skill's own stop. Closing it would only stop the
    # routing — a standing automation the human armed could then never reach the route at all.
    "deliver-scope": True,
    # The same gate as /deliver-scope's, over the adoption route: the ask is the human's own
    # words end to end, quoted verbatim, and this skill's stop otherwise.
    "adopt-scope": True,
    "plan-work": True,
    "implement-task": True,
    "review-change": True,
    "reconcile": True,
    # Reachable: its inputs — the target, the slug and the areas — are stated in the invocation,
    # and what it writes is material a human reads before any node exists. The gate it has is the
    # committed tree.
    "survey": True,
    "siegard-config": False,
    # Read-only and input-free beyond the project root: nothing here is the human's to assert,
    # so a session may reach for it when asked how the work stands — that reachability is the
    # skill's point.
    "siegard-status": True,
    # The same reachability as /siegard-status, one initiative narrower: read-only, and its one
    # extra input (the initiative) is inferred exactly as /siegard-status infers the project
    # root — named when ambiguous, never asserted by the session.
    "siegard-progress": True,
    # It writes nothing and arms nothing: the condition it prints becomes a goal only when the
    # person pastes it, so a session may reach for it when asked to carry a scope unattended.
    "siegard-goal": True,
    # Removal is the one act whose want only the human can state — the same criterion that
    # closes /siegard-config: a session that "tidied up" on its own would be deciding an input
    # that was never its to assert.
    "siegard-archive": False,
    # It shapes what every later review holds the project to, the same standing /siegard-config
    # already holds over the project's structural roots — a session drafting its own future
    # judge, unasked, is deciding an input that was never its to assert either.
    "siegard-standard": False,
    # The file set is the human's to assert and the reading writes no source — the same shape
    # that leaves /reconcile reachable. A session asked to check some files may reach for it.
    "check-source": True,
    # The window is anyone's to name and the two files it writes land under a root nothing
    # else reads — a session asked for a retrospective or a cost breakdown may reach for it.
    # The one read it makes outside the project is gated inside the skill, by a probe the
    # human sees before it happens, not by who may invoke it.
    "siegard-telemetry": True,
    # Closed: the input is the person's own request, and only they can say it needs rewriting. A
    # session that rewrote requests unasked would be deciding an input that was never its to
    # assert, and would put its reading between the person and what they said.
    "clarify-request": False,
}


def test_only_the_declared_skills_are_closed_to_the_model(case):
    """Which entry points a session may load by itself is a policy, and until this test existed it
    lived in three YAML values that no commit message, rule or schema ever explained — which is how
    a skill authored beside another inherited the flag by copying the file next to it.

    The criterion is who has the right to state the input, and never how much the skill writes:
    `/implement-task` writes source, installs packages and runs commands, and is reachable, while
    `/siegard-config` writes one JSON file every other entry point reads, and is not. The reachable
    ones are held by what is inside them — an input nobody named is a stop, a pending root is a
    stop, a judgment is delegated — and by the fact that a skill's description is the only
    instruction that reaches a plugin install at all. A new skill has to appear here to ship, which
    is the point: the decision gets made rather than inherited."""
    import yaml
    assert sorted(MODEL_MAY_REACH) == sorted(SKILLS), \
        "a skill was added or removed without deciding whether a session may reach for it"
    front = yaml.safe_load(FENCE.match(case["text"]).group(1))
    closed = front.get("disable-model-invocation", False)
    assert closed is not MODEL_MAY_REACH[case["name"]], \
        f"{case['name']}: the frontmatter and the policy disagree about who may invoke it"


def test_frontmatter_satisfies_the_skill_contract(case, skill_schema):
    """The agents have been held to `schemas/agent.json` since they shipped; the skills were held
    to nothing but a name-and-description spot check. The contract sets `additionalProperties:
    false` precisely because Claude Code ignores a frontmatter key it does not recognise — so a
    misspelled field, or a value outside a closed vocabulary like `effort`, ships as a silent
    no-op. Nothing else in this suite would notice."""
    import yaml
    front = yaml.safe_load(FENCE.match(case["text"]).group(1))
    problems = [e.message for e in skill_schema.iter_errors(front)]
    assert problems == [], f"{case['name']}: {problems}"


def test_every_cited_path_exists(repo, case):
    cited = CITATION.findall(case["text"])
    assert cited, f"{case['name']} cites nothing under the plugin root; it must cite the contract"
    for relative in cited:
        assert (repo / "src/claude" / relative).is_file(), \
            f"{case['name']} cites {relative}, which src/claude does not hold"


def test_the_contract_and_the_validator_are_both_cited(case):
    cited = set(CITATION.findall(case["text"]))
    assert case["contract"] in cited
    assert case["validator"] in cited
    for contract in case.get("also", []):
        assert contract in cited, f"{case['name']} writes {contract} and never cites it"


def test_every_delegate_is_cited_and_exists(repo, case):
    for name in case["delegates"]:
        assert f"agents/{name}.md" in case["text"], \
            f"{case['name']} delegates to {name} and never cites its file"
        assert (repo / "src/claude/agents" / f"{name}.md").is_file(), \
            f"{case['name']} delegates to {name}, which src/claude/agents does not hold"


SPAWNED = re.compile(r"siegard:([a-z][a-z-]*)")


def test_every_spawned_agent_is_a_declared_delegate(case):
    """The inverse of the test above: an agent a skill spawns by its plugin-scoped name and this
    table does not list is a delegation nothing checks the file of."""
    spawned = set(SPAWNED.findall(case["text"]))
    missing = sorted(spawned - set(case["delegates"]))
    assert not missing, f"{case['name']} spawns {missing}, absent from its delegates"


def enum_values(node):
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "enum" and isinstance(value, list):
                yield from (v for v in value if isinstance(v, str))
            else:
                yield from enum_values(value)
    elif isinstance(node, list):
        for value in node:
            yield from enum_values(value)


def shipped_vocabulary() -> list[str]:
    """Every distinctive value the node contracts declare, across all three roots."""
    values: set[str] = set()
    for relative in NODE_CONTRACTS:
        schema = json.loads((REPO / "src/claude" / relative).read_text(encoding="utf-8"))
        values |= {v for v in enum_values(schema) if "-" in v}
    return sorted(values)


def test_the_skill_restates_no_vocabulary(case):
    distinctive = shipped_vocabulary()
    assert distinctive, "the contracts declare no hyphenated vocabulary; the guard lost its subject"
    restated = [v for v in distinctive if v in case["text"]]
    assert restated == [], \
        f"{case['name']} restates {restated}; a vocabulary listed in a prompt is a second home"


INPUT_TERM = re.compile(r"^\d+\. \*\*the ([a-z ]+)\*\*", re.M)


def handoff_blocks(text: str, invocation: str) -> list[str]:
    """Chunks holding a handoff, whitespace collapsed so prose may wrap.

    A handoff written as one bullet of a long report list is judged on its own bullet. Splitting
    only on blank lines made the whole list the chunk, and an unrelated bullet naming `target` or
    `slug` then satisfied the guard for a handoff that named neither — which is exactly how the
    implement-task → reconcile handoff came to omit the slug with a green suite."""
    marker = f"`{invocation}` invocation ready to paste"
    chunks: list[str] = []
    for paragraph in text.split("\n\n"):
        if marker not in re.sub(r"\s+", " ", paragraph):
            continue
        bullets = re.split(r"\n(?=- )", paragraph)
        chunks.extend(re.sub(r"\s+", " ", b) for b in bullets
                      if marker in re.sub(r"\s+", " ", b))
    return chunks


def skill_text(name: str) -> str:
    return (REPO / "src/claude/skills" / name / "SKILL.md").read_text(encoding="utf-8")


# analyse-domain -> plan-work stays absent for good: analyse-domain is retired, not renamed,
# and it authors the pre-redesign knowledge base plan-work no longer accepts. Its replacement is
# named below instead of appended beside it.
FORWARD_SEAMS = (
    ("survey", "analyse"),
    ("analyse", "reconcile"),
    ("analyse", "plan-work"),
    ("plan-work", "implement-task"),
    ("implement-task", "review-change"),
    ("implement-task", "reconcile"),
    ("reconcile", "analyse"),
    ("reconcile", "plan-work"),
)


@pytest.mark.parametrize("handing,receiving", FORWARD_SEAMS)
def test_the_seam_hands_off_every_input_the_other_skill_requires(handing, receiving):
    """Each report ends with the next skill's invocation ready to paste. A handoff that omits an
    input the receiving skill requires reintroduces the stop it exists to spare, so every seam is
    held mechanically: change what one side requires or hands off and this test forces the other
    file into the same change. Every forward seam is covered — a seam left out of this list is a
    seam where the two files can drift apart in silence, which is how the first two ended up being
    the only ones anybody checked."""
    required = INPUT_TERM.findall(skill_text(receiving))
    assert required, f"{receiving} numbers no required inputs; the seam guard lost its subject"
    outgoing = handoff_blocks(skill_text(handing), f"/{receiving}")
    assert len(outgoing) == 1, \
        f"the {handing} report ends with exactly one /{receiving} handoff"
    for term in required:
        assert term in outgoing[0], \
            f"the {handing} handoff never names '{term}'; the stop it exists to spare returns"


# test_the_plan_hands_open_questions_back_to_the_analysis retired with it: it held plan-work to
# a fixed two-block /analyse-domain handoff carrying gaps and questions, and neither exists any
# more — the specification never carries an open fact under decide-and-disclose, so there is
# nothing left to hand back in that shape. What replaces it is a blocking note, reported by
# plan-work and implement-task alike but pointed at no fixed invocation — a route named in prose
# ("through /analyse extending the specification"), never a filled slot the way a real handoff
# is. A seam test for it would be checking a sentence, not a contract, and stays unwritten for
# that reason rather than for want of a name.


def test_the_review_hands_nothing_forward_as_an_invocation():
    """The one skill that ends the chain, and deliberately: which route a finding deserves — or
    whether it deserves one — is the decision this pass does not make. A pasteable invocation here
    would be that decision, taken by the reviewer, so its absence is held rather than assumed."""
    text = skill_text("review-change")
    assert handoff_blocks(text, "/implement-task") == []
    assert handoff_blocks(text, "/plan-work") == []
    assert handoff_blocks(text, "/analyse") == []


# ------------------------------------------------- the note-opening vocabulary


OPENING_CONSTANTS = ("BLOCKING_OPENING", "UNDERDETERMINED_OPENING", "UNSTATED_OPENING")


def opening_literals() -> dict[str, str]:
    """The note-class openings as bin/plan.py defines them — the constants a validator matches on,
    read from the script rather than restated here."""
    source = (REPO / "src/claude/bin/plan.py").read_text(encoding="utf-8")
    found = {}
    for name in OPENING_CONSTANTS:
        line = next(l for l in source.splitlines() if l.startswith(f"{name} = "))
        found[name] = line.split('"', 1)[1].rsplit('"', 1)[0]
    return found


def test_every_skill_spelling_of_a_note_opening_is_the_validators_own(case):
    """`plan.py` refuses a task persisting an UNSTATED opening and `/implement-task` collects
    underdetermined entries by their opening and nothing else. The literals are restated across
    plan-work, implement-task and siegard-status, and the existing vocabulary guard covers only
    hyphenated schema enums — so a reworded constant would orphan every prose copy in silence,
    leaving skills sorting notes by an opening no validator writes any more.

    This holds the direction that matters: a skill may name an opening or not, but where it names
    one it must be the script's, character for character."""
    literals = opening_literals()
    assert literals, "bin/plan.py declares no note openings; the guard lost its subject"
    for name, literal in sorted(literals.items()):
        # The trigger is the opening's own shape — the class word followed by its comma — not a
        # mention of the class by name, which is prose about the vocabulary rather than a use of
        # it. A skill may write "an `UNSTATED` opening"; what it may not write is a second
        # spelling of the opening itself.
        head = literal.split(",")[0] + ","
        text = case["text"]
        at = text.find(head)
        while at != -1:
            # Every occurrence, not merely one: a file carrying the literal correctly in three
            # places and reworded in a fourth would satisfy a membership test while shipping the
            # spelling no validator writes.
            assert text[at:at + len(literal)] == literal, \
                f"{case['name']} opens a note with {text[at:at + len(literal)]!r}, which is not " \
                f"how bin/plan.py spells it ({literal!r})"
            at = text.find(head, at + 1)


REPORT_HEADING = re.compile(r"^#{2,3} (?:\d+\. )?(?:Report\b|The report\b)|^\d+\. \*\*Report, and stop", re.M)


@pytest.mark.parametrize("skill", sorted(p.parent.name for p in
                                         (REPO / "src/claude/skills").glob("*/SKILL.md")))
def test_every_skill_that_reports_opens_its_report_as_the_handoff_states(skill):
    """A skill whose file states a report states what that report opens with, by citing the
    requirement that fixes it — so a skill added later cannot hand a person a report in an
    order of its own."""
    text = (REPO / "src/claude/skills" / skill / "SKILL.md").read_text(encoding="utf-8")
    if not REPORT_HEADING.search(text):
        pytest.skip("this skill states no report")
    assert "(SPEC-006 R1)" in text, f"{skill}: its report never cites SPEC-006 R1"


OUTSTANDING = re.compile(r"bin/deliver\.py --outstanding")


@pytest.mark.parametrize("skill", sorted(p.parent.name for p in
                                         (REPO / "src/claude/skills").glob("*/SKILL.md")))
def test_every_skill_that_runs_outstanding_relays_the_records_pinning_no_standard(skill):
    """SPEC-007 R1: the lines `--outstanding` prints of records pinning no standard, or another
    than their target declares, are reported where the command ran, never dropped by a reading
    that only wanted the tasks. A skill that hands the command in a handoff without running it
    states no report over its output and owes nothing here."""
    text = (REPO / "src/claude/skills" / skill / "SKILL.md").read_text(encoding="utf-8")
    if not OUTSTANDING.search(text):
        pytest.skip("this skill never runs --outstanding")
    assert "(SPEC-007 R1)" in text, f"{skill}: runs --outstanding and never cites SPEC-007 R1"


WITHHELD = ("no preference", "without preference", "recommend neither", "recommends neither",
            "recommends nothing", "nobody recommends", "choose neither", "doors and names none")
QUOTED_SPAN = re.compile(r"«[^»]*»")


def handoff_governing_files() -> list[Path]:
    """Every shipped file whose prose a session or an agent reads as instructions: the skills
    with their references, the agents, and the session rules."""
    root = REPO / "src/claude"
    return sorted([*root.glob("skills/**/*.md"), *root.glob("agents/*.md"),
                   root / "hooks/rules.md"])


def instruction_prose(path: Path) -> str:
    """The file's prose, lower-cased and on one line, without the «…» quotations — the
    citation test owns those, and a requirement's own words are not an instruction's."""
    text = QUOTED_SPAN.sub(" ", path.read_text(encoding="utf-8"))
    return re.sub(r"\s+", " ", text).lower()


@pytest.mark.parametrize("path", handoff_governing_files(),
                         ids=lambda p: p.relative_to(REPO / "src/claude").as_posix())
def test_no_instruction_tells_a_handoff_to_say_it_withholds_a_recommendation(path):
    """SPEC-006 R3: a choice that is the person's is said as the person's own decision, with
    what each option assumes and what would settle it. An instruction phrased as an absence —
    "recommend neither", "no preference" — is rendered into the session's language as written,
    and the person reads an answer withheld rather than a decision handed to them."""
    prose = instruction_prose(path)
    said = [phrase for phrase in WITHHELD if phrase in prose]
    assert not said, f"{path.name} tells a handoff to withhold, in words a session repeats: {said}"


def test_every_file_citing_the_person_s_own_questions_says_how_to_hand_them():
    """The ban above proves only that the old words are gone; this anchors on the words that
    replaced them, so a later rewrite that drops them goes red rather than passing silently."""
    citing = [p for p in handoff_governing_files() if "(SPEC-006 R3)" in p.read_text(encoding="utf-8")]
    assert citing, "nothing cites SPEC-006 R3; the anchor lost its subject"
    for path in citing:
        text = re.sub(r"\s+", " ", path.read_text(encoding="utf-8"))
        assert "the person's own decision" in text, \
            f"{path.name} cites SPEC-006 R3 and never says the choice is the person's own decision"
        assert re.search(r"what each (?:door|option) assumes", text), \
            f"{path.name} cites SPEC-006 R3 and never says what each option assumes"


def test_the_session_rules_name_the_route_when_every_option_is_excluded():
    """SPEC-006 R6 reaches every session through the rules, not through one skill's file."""
    text = (REPO / "src/claude/hooks/rules.md").read_text(encoding="utf-8")
    assert "(SPEC-006 R6)" in text


PROCEEDING = ("review-change", "check-source", "deliver-scope")


@pytest.mark.parametrize("skill", PROCEEDING)
def test_a_skill_that_proceeds_past_a_check_lists_it_and_stops_on_no_finding(skill):
    """SPEC-006 R4: a finding stops nothing, and a report that says a step may proceed lists the
    checks it ran with their output. The three skills that run checks and go on are where the
    rule is read; the session-wide rules carry its first sentence for every other report."""
    text = (REPO / "src/claude/skills" / skill / "SKILL.md").read_text(encoding="utf-8")
    assert "«A finding stops nothing» (SPEC-006 R4)" in text, \
        f"{skill}: never says a finding stops nothing"
    assert "it lists the checks it ran and their output verbatim» (SPEC-006 R4)" in text, \
        f"{skill}: proceeds past a check without listing it"


def test_the_session_rules_carry_that_a_finding_stops_nothing():
    text = (REPO / "src/claude/hooks/rules.md").read_text(encoding="utf-8")
    assert "«A finding stops nothing» (SPEC-006 R4)" in text


WAVED = ("review-change", "reconcile", "survey")


@pytest.mark.parametrize("skill", WAVED)
def test_a_skill_that_fans_out_dispatches_by_the_waves_the_staging_cuts(skill):
    """A sentence asking for batches no larger than the harness allows sized nothing, and the
    harness refused launches in series under it. The wave is a list the staging prints, or for
    the one skill that stages nothing a number stated beside the staging's own, and a refused
    launch is a wave cut too wide — never a delegation dispatched again on the skill's own
    account."""
    text = (REPO / "src/claude/skills" / skill / "SKILL.md").read_text(encoding="utf-8")
    assert "batches no larger" not in text, f"{skill} still sizes its fan-out by a sentence"
    assert "wave" in text and "cut too wide" in text, f"{skill} never dispatches by waves"
    if skill != "survey":
        assert "--concurrency" in text, f"{skill} hands no route when a wave is refused"


@pytest.mark.parametrize("skill", ("siegard-status", "siegard-progress"))
def test_a_state_question_s_skill_opens_its_description_with_the_trigger(skill):
    """The description is the only instruction that reaches a session before the skill loads,
    and the platform truncates it; a trigger stated last is a trigger never read. A question
    about where the project stands has to reach disk, and the description is what routes it."""
    text = (REPO / "src/claude/skills" / skill / "SKILL.md").read_text(encoding="utf-8")
    import yaml
    front = yaml.safe_load(FENCE.match(text).group(1))
    assert front["description"].startswith("Use whenever a person asks"), \
        f"{skill}: the description opens with what it does, not with when to use it"


WAITING = ("review-change", "reconcile", "survey", "plan-work", "implement-task")


@pytest.mark.parametrize("skill", WAITING)
def test_a_skill_that_delegates_waits_for_the_harness_and_never_polls(skill):
    """A spawned delegation runs in the background and the harness notifies when it answers.
    A session that sleeps, schedules wakeups, lists agents or messages the judge in between
    spends turns reading nothing; the text names the one signal and forbids the rest."""
    text = (REPO / "src/claude/skills" / skill / "SKILL.md").read_text(encoding="utf-8")
    assert "waits for that notification and nothing else" in text, \
        f"{skill} never says what the session waits for"
    assert "never a `sleep`" in text, f"{skill} never forbids polling"


def test_review_change_saves_each_return_before_it_folds():
    """The fold reads returns from disk; a skill that folds and never says how the returns got
    there leaves the one copy to a session's own retyping."""
    text = (REPO / "src/claude/skills/review-change/SKILL.md").read_text(encoding="utf-8")
    assert "--save-return" in text


WAVED = ("review-change", "reconcile")


@pytest.mark.parametrize("skill", WAVED)
def test_a_wave_ends_on_the_save_s_receipt_and_never_on_a_count_kept_in_the_session(skill):
    """The harness delivers several notifications in one turn and some inside the turn that
    spawned the wave, so a tally the session keeps undercounts what arrived; the one signal is
    what `--save-return` reads from the returns on disk, and the text says so in the agent's words
    for the form of the reply too — the delegation prompt is where the form was shown to hold."""
    text = (REPO / "src/claude/skills" / skill / "SKILL.md").read_text(encoding="utf-8")
    flat = " ".join(text.split())
    assert "A wave ends when `--save-return` reports `0 pending` for it, read from the returns " \
           "on disk; a count of notifications kept in the session is never the signal" in flat, \
        f"{skill} lets the session count notifications"
    assert "ends with the mapping's last line; no ``` line anywhere" in flat, \
        f"{skill} hands the delegation no form for its reply"
    assert "whether the fold will refuse what was just saved" in flat, \
        f"{skill} never says the save's receipt is to be read"


def test_implement_task_writes_both_records_through_the_writer():
    """A record composed by hand has pins and a shape that depend on the session; the writer
    makes it a function of the return, the task file, the standard and the run."""
    text = skill_text("implement-task")
    assert "deliver.py --write-implementation" in text
    assert "deliver.py --write-proof" in text
    assert "--write-proof --replace" in text
    assert "yaml.safe_dump" not in text, "the frontmatter is the writer's, never typed"


def test_plan_work_spawns_the_decider_and_never_offers_it():
    """R13 decides an unstated fact and discloses it; a session that asks permission first has
    turned the one stop R13 removed back into a question with a default answer."""
    text = (REPO / "src/claude/skills/plan-work/SKILL.md").read_text(encoding="utf-8")
    assert "The decider is spawned, never offered" in text
    assert "(SPEC-001 R13)" in text


def test_a_closure_reads_what_it_leaves_standing_before_the_marker_is_written():
    """Closing is the human's act and stays one; what it closes over is three counts a script
    prints — findings nobody routed, nodes still owed a test, notes still standing — never a
    verdict, and never a stop."""
    text = (REPO / "src/claude/skills/plan-work/SKILL.md").read_text(encoding="utf-8")
    closing = text.split("## Closing the plan", 1)[1]
    assert "what this closure leaves standing" in closing
    for command in ("deliver.py --findings", "trace.py --owed", "--plan <work-root>",
                    "plan.py --notes"):
        assert command in closing, f"the closing step never cites {command}"
    assert "None of the three is a stop" in closing


def unwrapped(text: str) -> str:
    """Prose may wrap anywhere; a sentence anchor is judged on the words, not on the line break."""
    return re.sub(r"\s+", " ", text)


def test_the_analysis_stops_on_material_that_states_no_fact():
    """SPEC-001 R15: material that states nothing is an absent input, and the stop is over the
    input — never a question about content, which R10 keeps out of the route. The sentence is held
    because a skill that decides everything the material leaves unsaid would otherwise produce a
    floor from no material at all."""
    text = unwrapped(skill_text("analyse"))
    assert "(SPEC-001 R15)" in text, "the skill never cites the stop over an absent material"
    assert "Material present and stating nothing is the first input absent" in text
    assert "never a question about the content" in text


def test_the_analysis_discloses_a_node_the_material_does_not_name():
    """SPEC-001 R9: the log is the only place a decided fact is told from a stated one, and a node
    the analysis introduced is a decided fact with no field of its own — so its first entry, over
    the field its class requires, is what discloses it. Both writers of such a node state it."""
    decider = (REPO / "src/claude/agents/unstated-fact-decider.md").read_text(encoding="utf-8")
    for text in (unwrapped(skill_text("analyse")), unwrapped(decider)):
        assert "names no such thing" in text
        assert "(SPEC-001 R9)" in text


def test_the_analysis_reports_how_many_fields_it_decided_per_node():
    """The count is the one line a reviewer reads before any node; it opens the report's body
    beside every node written, read from `--shape --of` and never composed."""
    report = unwrapped(skill_text("analyse").split("### 6. Report, and stop", 1)[1])
    assert "how many of its declared fields this invocation decided" in report
    assert "`--shape --of` printed it" in report


def test_a_proof_task_is_bound_against_the_nodes_that_name_its_node():
    """An auditor's assertion can contradict a contract that answers the same case; a binder
    handed the one node alone cannot see it, and the contradiction then surfaces as a red test
    after a delivery was paid for. The neighbours come from `spec.py --impact`, read."""
    text = (REPO / "src/claude/skills/plan-work/SKILL.md").read_text(encoding="utf-8")
    increment = text.split("## The proof increment", 1)[1].split("### 1. Situate", 1)[0]
    assert "spec.py --impact" in increment
    assert "every node that names it" in increment
    assert "the one node as its whole candidate set" not in increment
    assert "BLOCKING, from the specification" in increment
