"""A handoff is rendered from its record, and a handoff written as free text is held to what the
text alone decides (SPEC-006 R8).

The fixtures under `fixtures/handoff/` are synthetic, written in the shapes the handoffs that
motivated R8 took — a Portuguese report that opens on the framework's own words and buries its
recommendation under pending items, hashes and measurements; an English one asking which door
without recommending any; a long status answer that hands nothing — and the shapes R8 asks for.
No consumer's text is copied. Each message fixture is named with what it is, and the expected
violations are the prefixes `--check` prints: `opening`, `length`, `decision`.

`--prepare` and the state `--render` reads again (SPEC-006 R10) are held over the committed
consumer repository `test_door.py` builds, so a door's mark is what `door.py --check` answers there.
"""
from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

import handoff

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "src/claude/bin/handoff.py"
FIXTURES = REPO / "tests/fixtures/handoff"
CONTRACT = handoff.load_contract()

MESSAGES = {
    "pt-long-jargon-late-decision.md": {"opening", "length", "decision"},
    "en-clean-decision.md": set(),
    "pt-clean-decision.md": set(),
    "en-asks-without-recommending.md": {"decision"},
    "pt-long-status-answer.md": set(),
    "en-command-fenced-in-opening.md": set(),
    "pt-flag-in-opening.md": {"opening"},
    "en-decision-word-late.md": {"decision"},
}


def run(*args: str, stdin: str | None = None, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(SCRIPT), *args], input=stdin,
                          capture_output=True, text=True, cwd=cwd)


def record(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def kinds(problems: list[str]) -> set[str]:
    return {problem.split(":", 1)[0] for problem in problems}


def echo(data: dict):
    """A `state_from` reader that answers what the record already holds: the rendering is under
    test, and the script's line is pinned by the tests over fixture repositories below."""
    return lambda source, language, contract: data.get("state")


def rendered(data: dict, state_of=None) -> tuple[str | None, list[str]]:
    return handoff.render(data, CONTRACT, FIXTURES, state_of or echo(data))


# ------------------------------------------------------------------ the specification


def test_every_message_fixture_is_listed():
    on_disk = {p.name for p in FIXTURES.glob("*.md")}
    assert on_disk == set(MESSAGES), "a fixture with no expectation is a fixture nothing reads"


def test_the_ceilings_the_schema_holds_are_the_ones_the_specification_states():
    """The numbers live in the schema so the script reads them from one place; the specification
    states them so a person can dispute them. The two are one decision, held together here."""
    text = (REPO / "specs/handoff.md").read_text(encoding="utf-8")
    r8 = re.search(r"^- \*\*R8\*\* — (.*)$", text, re.M).group(1)
    ceilings = CONTRACT["x-ceilings"]
    assert f"its state within {ceilings['state']} characters" in r8
    assert f"each decision's block within {ceilings['block']}" in r8
    assert f"the whole message within {ceilings['message']}" in r8
    assert f"in its first {ceilings['opening']} characters" in r8


def test_every_language_the_record_admits_has_its_labels_and_they_carry_a_decision_word():
    admitted = CONTRACT["properties"]["language"]["enum"]
    labels = {k: v for k, v in CONTRACT["x-labels"].items() if k != "description"}
    assert sorted(admitted) == sorted(labels)
    for language, words in labels.items():
        for key in ("recommended", "own"):
            assert handoff.decision_word_at(words[key], CONTRACT) is not None, (language, key)
        assert handoff.decision_word_at(words["recommended"], CONTRACT, ("recommendation",)) == 0
        for word in words.values():
            assert handoff.jargon_in(word, CONTRACT) == [], (language, word)


def test_the_schema_s_own_example_satisfies_it():
    from jsonschema import Draft202012Validator
    for example in CONTRACT["examples"]:
        assert list(Draft202012Validator(CONTRACT).iter_errors(example)) == []


# ------------------------------------------------------------------------- --check


@pytest.mark.parametrize("name", sorted(MESSAGES))
def test_a_written_handoff_is_held_to_what_its_text_decides(name):
    text = (FIXTURES / name).read_text(encoding="utf-8")
    problems = handoff.violations(handoff.reading(text, CONTRACT), CONTRACT)
    assert kinds(problems) == MESSAGES[name], problems


@pytest.mark.parametrize("name", sorted(MESSAGES))
def test_the_command_exits_on_what_the_functions_return(name):
    done = run("--check", str(FIXTURES / name))
    assert done.returncode == (1 if MESSAGES[name] else 0), done.stdout + done.stderr
    assert kinds(done.stdout.splitlines()) == MESSAGES[name]
    assert done.stderr == ""


def test_a_hit_names_the_list_s_entry_and_the_reading_keeps_no_words():
    text = (FIXTURES / "pt-long-jargon-late-decision.md").read_text(encoding="utf-8")
    read = handoff.reading(text, CONTRACT)
    assert {"state A or B", "a script name", "a command flag", "binder", "rebind", "juiz"} \
        <= set(read["jargon_in_opening"])
    assert read["hands_decision"] is True and read["recommendation_word"] is True
    assert read["decision_word_at"] > CONTRACT["x-ceilings"]["opening"]
    assert 0.5 < read["decision_word_share"] < 1
    assert set(read) == {"characters", "hands_decision", "jargon_in_opening",
                         "recommendation_word", "decision_word_at", "decision_word_share"}


def test_a_status_answer_hands_nothing_and_has_no_ceiling():
    text = (FIXTURES / "pt-long-status-answer.md").read_text(encoding="utf-8")
    read = handoff.reading(text, CONTRACT)
    assert read["characters"] > CONTRACT["x-ceilings"]["message"]
    assert read["hands_decision"] is False and read["decision_word_at"] is None


def test_a_fenced_paste_is_not_prose():
    text = (FIXTURES / "en-command-fenced-in-opening.md").read_text(encoding="utf-8")
    assert handoff.jargon_in(text, CONTRACT), "the fixture lost the words its fence holds"
    assert handoff.reading(text, CONTRACT)["jargon_in_opening"] == []


def test_a_term_matches_as_a_whole_word_only():
    assert handoff.jargon_in("the outstanding order", CONTRACT) == []
    assert handoff.jargon_in("the state art of a door", CONTRACT) == [("door", "door")]
    assert handoff.jargon_in("Estado B ainda", CONTRACT) == []
    assert handoff.jargon_in("estado B ainda", CONTRACT) == [("state A or B", "estado B")]
    assert handoff.jargon_in("see /home/user/notes", CONTRACT) == []
    assert not handoff.hands_a_decision("Saved to\n/home/user/notes.md\n", CONTRACT)
    assert handoff.hands_a_decision("Ready:\n\n/plan-work checkout\n", CONTRACT)


def test_check_reads_standard_input():
    done = run("--check", "-", stdin="Done. Which one?\n")
    assert done.returncode == 1 and done.stdout.startswith("decision:")


# ------------------------------------------------------------------------ --render


@pytest.mark.parametrize("name", ["record-pt-own-decision.json", "record-en-two-decisions.json",
                                  "record-pt-status.json", "record-pt-route-steps.json",
                                  "record-pt-path-in-order.json",
                                  "record-en-independent-doors.json"])
def test_a_record_renders_and_what_it_renders_holds(name):
    message, problems = rendered(record(name))
    assert problems == [] and message
    assert handoff.violations(handoff.reading(message, CONTRACT), CONTRACT) == []


def test_the_rendering_opens_with_the_state_and_the_recommendation_first():
    message, _ = rendered(record("record-en-two-decisions.json"))
    assert message.startswith("```\ncheckout · task 2/2 delivered · phase review")
    first = message.index("1. Should an empty order")
    assert message.index("**Recommended** `a`: Refuse it") > first
    assert "needs at least one item. It would change if a product owner says" in message
    assert message.index("**Recommended** `a`") < message.index("`b`: Accept it")
    assert message.index("`b`: Accept it") < message.index("If none is taken: The screen")
    assert "```\n   /plan-work checkout\n   ```" in message
    assert message.rstrip().endswith("Full report: full-report.txt")
    assert message.index("The earlier note") < first


def test_a_choice_that_is_the_person_s_renders_in_their_language():
    message, _ = rendered(record("record-pt-own-decision.json"))
    assert "**Decisão sua**: A primeira assume" in message
    assert "Se nenhuma for tomada: A busca fica" in message
    assert "Relatório completo: full-report.txt" in message
    assert "Recommended" not in message and "Full report" not in message


def test_the_command_renders_from_a_file_and_from_standard_input(tmp_path):
    """A directory no project file declares prints no progress line, so the state the script
    answers there is the fixed words for a project with nothing live."""
    data = record("record-en-two-decisions.json")
    data["state"] = CONTRACT["x-labels"]["en"]["quiet"]
    data["state_from"] = {"script": "progress.py", "project": str(tmp_path)}
    path = tmp_path / "record.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    from_file = run("--render", str(path), cwd=FIXTURES)
    from_stdin = run("--render", "-", stdin=json.dumps(data), cwd=FIXTURES)
    assert from_file.returncode == 0 and from_stdin.returncode == 0, from_file.stdout
    assert from_file.stdout == from_stdin.stdout == rendered(data)[0]


def test_a_rendered_record_is_kept_as_json_beside_the_report_it_names(tmp_path):
    """«`bin/handoff.py --render` keeps the record it rendered, as JSON beside the report its
    `report` names, so that the run that receives a stop can ask the grant over the doors it
    handed.» (SPEC-011 R9)"""
    data = record("record-en-two-decisions.json")
    data["state"] = CONTRACT["x-labels"]["en"]["quiet"]
    data["state_from"] = {"script": "progress.py", "project": str(tmp_path)}
    report = tmp_path / "20261113T000000Z-implement-task.md"
    report.write_text("# the report\n", encoding="utf-8")
    data["report"] = str(report)
    done = run("--render", "-", stdin=json.dumps(data), cwd=FIXTURES)
    assert done.returncode == 0, done.stdout
    kept = json.loads(report.with_suffix(".json").read_text(encoding="utf-8"))
    assert kept == data


def test_a_record_naming_no_report_is_kept_nowhere_and_a_refused_one_is_not_kept(tmp_path):
    data = record("record-en-two-decisions.json")
    data["state"] = CONTRACT["x-labels"]["en"]["quiet"]
    data["state_from"] = {"script": "progress.py", "project": str(tmp_path)}
    data.pop("report", None)
    assert run("--render", "-", stdin=json.dumps(data), cwd=FIXTURES).returncode == 0
    gone = tmp_path / "gone" / "x.md"
    data["report"] = str(gone)
    refused = run("--render", "-", stdin=json.dumps(data), cwd=FIXTURES)
    assert refused.returncode == 1 and not gone.with_suffix(".json").exists()


def refusal(mutate) -> list[str]:
    data = copy.deepcopy(record("record-en-two-decisions.json"))
    mutate(data)
    message, problems = rendered(data)
    assert message is None
    return problems


def test_a_record_the_schema_refuses_prints_nothing_for_the_person():
    problems = refusal(lambda d: d["decisions"][0].pop("if_none"))
    assert any("'if_none' is a required property" in p for p in problems)


def test_a_recommendation_and_a_person_s_own_choice_are_never_both_handed():
    problems = refusal(lambda d: d["decisions"][0].update(settles="Either holds."))
    assert any(p.startswith("decisions/0") for p in problems)


def test_a_state_over_its_ceiling_is_refused():
    problems = refusal(lambda d: d.update(state="x" * (CONTRACT["x-ceilings"]["state"] + 1)))
    assert any(p.startswith("state:") and "over the ceiling" in p for p in problems)


def test_a_block_over_its_ceiling_is_refused_and_the_paste_is_not_counted():
    long = "word " * (CONTRACT["x-ceilings"]["block"] // 5)
    problems = refusal(lambda d: d["decisions"][0]["others"][0].update(what_it_does=long.strip()))
    assert any(p.startswith("decisions/0: its block renders to") for p in problems)
    data = record("record-en-two-decisions.json")
    data["decisions"][1]["invocation"] = "/implement-task " + "x" * 500
    message, problems = rendered(data)
    assert not any("its block renders" in p for p in problems)


def test_a_message_over_its_ceiling_is_refused():
    def three_more(d):
        for word in ("d", "e", "f"):
            extra = copy.deepcopy(d["decisions"][0])
            extra["recommended"]["reply_word"] = word
            extra["others"][0]["reply_word"] = word + "2"
            d["decisions"].append(extra)
    problems = refusal(three_more)
    assert any(p.startswith("length:") for p in problems)


def test_a_framework_word_in_any_prose_field_is_refused_with_where_it_sits():
    problems = refusal(lambda d: d["decisions"][1]["recommended"].update(
        why="The binder found nothing and trace.py --check is clean"))
    joined = "\n".join(problems)
    assert "decisions/1/recommended/why: carries binder" in joined
    assert "a script name ('trace.py')" in joined and "a command flag ('--check')" in joined


def test_the_line_ready_to_paste_may_name_a_command():
    data = record("record-en-two-decisions.json")
    data["decisions"][1]["invocation"] = "python3 bin/trace.py --check ."
    assert rendered(data)[1] == []


def test_one_reply_word_names_one_door_across_the_handoff():
    problems = refusal(lambda d: d["decisions"][1]["recommended"].update(reply_word="A"))
    assert any("reply word 'A' already names a door in decisions/0" in p for p in problems)


def test_a_report_path_that_names_no_file_is_refused():
    problems = refusal(lambda d: d.update(report="nowhere-to-be-found.txt"))
    assert any(p.startswith("report:") and "names no file" in p for p in problems)


def test_a_language_with_no_labels_is_refused():
    problems = refusal(lambda d: d.update(language="fr"))
    assert any(p.startswith("language:") for p in problems)


def test_a_report_kind_carries_a_body_or_a_path_and_no_decision():
    data = record("record-pt-status.json")
    data.pop("body")
    assert rendered(data)[0] is None
    data["report"] = "full-report.txt"
    assert rendered(data)[1] == []
    data["decisions"] = record("record-pt-own-decision.json")["decisions"]
    assert rendered(data)[0] is None
    data = record("record-en-two-decisions.json")
    data["body"] = "inline"
    assert rendered(data)[0] is None


PADDING = "A iniciativa de pedidos tem a tela principal entregue e falta a parte de devoluções. " * 6


def test_a_short_form_above_a_report_path_is_read_whole_for_the_term_list():
    """«Where kind `report` carries a `report` path, its `body` is the short form above the full
    report, and `bin/handoff.py --render` refuses it where it carries a term of the closed list
    anywhere» (SPEC-006 R11)."""
    data = record("record-pt-status.json")
    data["report"] = "full-report.txt"
    data["body"] = PADDING + "Falta apenas você escolher o slug."
    assert any(p.startswith("body: carries slug") for p in rendered(data)[1])


def test_a_body_with_no_path_is_read_over_its_opening_span():
    data = record("record-pt-status.json")
    data["body"] = PADDING + "O slug fica para depois."
    assert rendered(data)[1] == []
    data["body"] = "O slug fica para depois. " + PADDING
    assert any(p.startswith("body: carries slug") for p in rendered(data)[1])


@pytest.mark.parametrize("words", ["13 moved, 4 proof", "uma leitura devida", "um orphaned"])
def test_drift_class_names_and_owed_in_portuguese_are_terms(words):
    data = record("record-pt-status.json")
    data["body"] = f"O vínculo tem {words} a reler."
    assert any(p.startswith("body: carries") for p in rendered(data)[1]), words


def test_a_body_that_recommends_carries_the_fact_that_would_change_it():
    """«A body that recommends carries the fixed words the schema holds for the reversing fact
    in the record's language, followed by that fact, or `--render` refuses it» (SPEC-006 R11)."""
    data = record("record-pt-status.json")
    data["body"] = "Sugiro reler os 58 arquivos agora, porque cada um é lido uma vez só."
    assert any(p.startswith("body: recommends without") for p in rendered(data)[1])
    data["body"] += " Mudaria se um commit novo tocasse esses arquivos."
    assert rendered(data)[1] == []


def test_the_command_refuses_with_one_line_per_problem_and_exit_one(tmp_path):
    data = record("record-en-two-decisions.json")
    data["state"] = "The order screen is done"
    data["state_from"] = {"script": "progress.py", "project": str(tmp_path)}
    data["report"] = "missing.txt"
    path = tmp_path / "r.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    done = run("--render", str(path), cwd=FIXTURES)
    assert done.returncode == 1
    assert {line.split(":", 1)[0] for line in done.stdout.splitlines()} == {"state", "report"}


@pytest.mark.parametrize("args", [[], ["--render"], ["--other", "x"], ["--check", "a", "b"]])
def test_arguments_it_cannot_read_cannot_run(args):
    done = run(*args)
    assert done.returncode == handoff.CANNOT_RUN and done.stderr.startswith("cannot run:")


def test_a_record_that_is_not_json_cannot_run():
    done = run("--render", "-", stdin="{not json")
    assert done.returncode == handoff.CANNOT_RUN and "not JSON" in done.stderr


# ------------------------------------------------------------ the state is a script's (R10)


def test_a_decision_with_no_state_from_is_refused():
    problems = refusal(lambda d: d.pop("state_from"))
    assert any("'state_from' is a required property" in p for p in problems)


def test_a_state_that_differs_from_what_its_script_prints_now_is_refused():
    data = record("record-en-two-decisions.json")
    message, problems = rendered(data, lambda source, language, contract: "checkout · phase plan")
    assert message is None
    assert any(p.startswith("state: differs from what progress.py prints now") for p in problems)
    assert any("run handoff.py --prepare again" in p for p in problems)


def test_a_state_a_script_printed_is_quoted_and_not_read_for_the_term_list():
    data = record("record-en-two-decisions.json")
    data["state"] = "state B — stop: stands — the bound file moved; see trace.py --check"
    message, problems = rendered(data)
    assert problems == [], problems
    assert message.startswith(f"```\n{data['state']}\n```\n")
    assert handoff.violations(handoff.reading(message, CONTRACT), CONTRACT) == []


def test_a_state_the_agent_wrote_is_read_for_the_term_list():
    data = record("record-pt-status.json")
    data["state"] = "O binder terminou; nada espera por você."
    message, problems = rendered(data)
    assert message is None and any(p.startswith("state: carries binder") for p in problems)


@pytest.mark.parametrize("key", ["why", "reverses_if"])
@pytest.mark.parametrize("blank", ["", "   "])
def test_a_recommendation_with_an_empty_why_or_reversal_is_refused(key, blank):
    problems = refusal(lambda d: d["decisions"][0]["recommended"].update({key: blank}))
    assert any(p.startswith(f"decisions/0/recommended/{key}: empty") for p in problems), problems


def test_a_door_its_entry_point_refuses_is_never_recommended():
    def refused(d):
        d["decisions"][0]["recommended"]["entry"] = "/implement-task"
        d["decisions"][0]["recommended"]["check"] = {
            "answer": "refuses", "refused": ["plans/s/closure.md exists — the plan is history"]}
    problems = refusal(refused)
    assert any(p.startswith("decisions/0/recommended: /implement-task is refused") and
               "closure.md exists" in p for p in problems), problems


def test_a_door_its_entry_point_refuses_may_be_handed_excluded():
    data = record("record-en-two-decisions.json")
    data["decisions"][0]["others"][0].update(entry="/implement-task", check={
        "answer": "refuses", "refused": ["plans/s/closure.md exists — the plan is history"]})
    assert rendered(data)[1] == []


# --------------------------------------------------------- the narrowed list of terms


ENGLISH_WORDS = ("stands", "nowhere", "owed", "offered")


@pytest.mark.parametrize("word", ENGLISH_WORDS)
def test_a_plain_english_word_is_no_term_in_english_prose(word):
    text = f"The rule {word} as it is, and the screen is ready for the person to read."
    assert handoff.jargon_in(text, CONTRACT) == []
    assert handoff.jargon_in(text, CONTRACT, "en") == []


@pytest.mark.parametrize("word", ENGLISH_WORDS)
def test_a_backticked_framework_word_is_a_term_in_any_language(word):
    text = f"The task carries `{word}` and the screen is ready."
    assert handoff.jargon_in(text, CONTRACT) == [(word, f"`{word}`")]
    assert handoff.jargon_in(text, CONTRACT, "en") == [(word, f"`{word}`")]


@pytest.mark.parametrize("word", ENGLISH_WORDS)
def test_a_framework_word_in_portuguese_prose_is_still_a_term(word):
    text = f"A tarefa ficou em {word} e não há nada para fazer com ela."
    assert [name for name, _ in handoff.jargon_in(text, CONTRACT)] == [word]
    assert [name for name, _ in handoff.jargon_in(text, CONTRACT, "pt-BR")] == [word]


def test_a_framework_phrase_is_a_term_in_english_prose():
    text = "The owed act is a commit, and the offered acts can wait; the pair is read nowhere."
    names = [name for name, _ in handoff.jargon_in(text, CONTRACT)]
    assert {"owed act", "offered acts", "read nowhere"} <= set(names)


def test_the_portuguese_baseline_fixture_still_carries_every_term_it_carried():
    """Narrowing the list for English prose never loosens what the check reads in Portuguese."""
    text = (FIXTURES / "pt-long-jargon-late-decision.md").read_text(encoding="utf-8")
    read = handoff.reading(text + "\nA linha stands ficou nowhere, owed e offered.\n", CONTRACT)
    assert read["jargon_in_opening"]
    names = [name for name, _ in handoff.jargon_in(handoff.prose_of(text) + " stands nowhere "
                                                   "owed offered", CONTRACT)]
    assert set(ENGLISH_WORDS) <= set(names)


def test_a_record_in_english_may_say_stands_and_one_in_portuguese_may_not():
    data = record("record-en-two-decisions.json")
    data["decisions"][1]["recommended"]["why"] = "Every test passed and the rule stands"
    assert rendered(data)[1] == []
    data = record("record-pt-own-decision.json")
    data["decisions"][0]["if_none"] = "A busca fica como stands."
    assert any("carries stands" in p for p in rendered(data)[1])


# ------------------------------------------- how the doors of a decision relate (SPEC-006 R1, R8)
#
# A handoff that hands two doors or more used to print them as bare bullets, and the person could
# not tell a choice between them from a path through them, or from doors each worth taking. The
# record now says which, a decision's block opens its doors with that, and nothing but a door is
# a bullet. These tests hold each half so the bare list cannot come back.

RELATIONS = CONTRACT["$defs"]["decision"]["properties"]["relation"]["enum"]
LABELS = {k: v for k, v in CONTRACT["x-labels"].items() if k != "description"}
DOOR_BULLET = re.compile(r"^   - (?:(?:Step|Passo) \d+ (?:of|de) \d+ · )?(?:\*\*\S+\*\* )?`[\w-]+`: ")
RECORD_FIXTURES = sorted(p.name for p in FIXTURES.glob("record-*.json"))


def label_of(relation: str, language: str) -> str:
    return LABELS[language][relation.replace("-", "_")]


def block_lines(message: str, ask: str) -> list[str]:
    """The lines of the block that opens with `ask`, up to the blank line that ends it."""
    lines = message.split("\n")
    start = next(at for at, line in enumerate(lines) if line.endswith(ask))
    end = next((at for at in range(start, len(lines)) if lines[at] == ""), len(lines))
    return lines[start:end]


def with_two_doors(language: str, relation: str, own: bool) -> dict:
    data = record("record-pt-own-decision.json" if language == "pt-BR"
                  else "record-en-two-decisions.json")
    data["decisions"][0]["relation"] = relation
    if own and language == "en":
        decision = data["decisions"][0]
        decision.pop("recommended")
        decision["settles"] = "The first assumes the rule holds, the second that it does not."
        decision["others"].insert(0, {"reply_word": "a", "what_it_does": "Refuse it"})
    return data


@pytest.mark.parametrize("own", [False, True])
@pytest.mark.parametrize("language", ["en", "pt-BR"])
@pytest.mark.parametrize("relation", RELATIONS)
def test_a_decision_of_two_doors_opens_them_with_how_they_relate(relation, language, own):
    data = with_two_doors(language, relation, own)
    message, problems = rendered(data)
    assert problems == [], problems
    block = block_lines(message, data["decisions"][0]["ask"])
    header = f"   {label_of(relation, language)}:"
    assert block.count(header) == 1, block
    first_door = next(at for at, line in enumerate(block) if DOOR_BULLET.match(line))
    assert block.index(header) == first_door - 1, "the words open the doors, directly above them"
    assert not any(label_of(other, language) in "\n".join(block)
                   for other in RELATIONS if other != relation), "one relation per decision"


def test_the_three_relations_say_three_different_things_in_every_language():
    assert RELATIONS == ["one-of", "in-order", "independent"]
    for language, words in LABELS.items():
        said = [label_of(relation, language) for relation in RELATIONS]
        assert len(set(said)) == 3, (language, said)
        assert all(handoff.jargon_in(word, CONTRACT, language) == [] for word in said)
    assert "one" in label_of("one-of", "en").lower() and "order" in label_of("in-order", "en")
    assert "uma" in label_of("one-of", "pt-BR") and "ordem" in label_of("in-order", "pt-BR")


def test_a_path_numbers_its_steps_and_a_choice_or_a_set_of_doors_numbers_none():
    message, problems = rendered(record("record-pt-path-in-order.json"))
    assert problems == [], problems
    block = block_lines(message, "Levar a regra nova do frete até a entrega?")
    doors = [line for line in block if DOOR_BULLET.match(line)]
    assert [line.split(" · ")[0] for line in doors] == [
        "   - Passo 1 de 3", "   - Passo 2 de 3", "   - Passo 3 de 3"]
    assert "**Recomendado** `conferir`" in doors[0], "the recommended door is the first step"
    assert "`planejar`" in doors[1] and "`entregar`" in doors[2]
    for name in ("record-pt-route-steps.json", "record-en-independent-doors.json"):
        text, _ = rendered(record(name))
        assert not re.search(r"\b(?:Passo|Step) \d", text), name


def test_a_decision_of_two_doors_or_more_with_no_relation_is_refused_saying_what_each_means():
    for own in (False, True):
        data = with_two_doors("en", "one-of", own)
        data["decisions"][0].pop("relation")
        message, problems = rendered(data)
        assert message is None
        said = [p for p in problems if "relation" in p]
        assert len(said) == 1 and said[0].startswith("decisions/0/relation:"), problems
        assert all(value in said[0] for value in RELATIONS)
        assert "the person takes one" in said[0] and "all are taken in the order" in said[0]


@pytest.mark.parametrize("value", ["", "either", "One-Of", None, 1])
def test_a_relation_that_is_none_of_the_three_is_refused_once_and_names_the_values(value):
    data = with_two_doors("en", "one-of", False)
    data["decisions"][0]["relation"] = value
    message, problems = rendered(data)
    assert message is None
    said = [p for p in problems if "relation" in p]
    assert len(said) == 1 and all(v in said[0] for v in RELATIONS), problems


def test_a_decision_handing_one_door_needs_no_relation_and_prints_no_opening_words():
    data = record("record-en-two-decisions.json")
    assert "relation" not in data["decisions"][1]
    message, problems = rendered(data)
    assert problems == []
    block = block_lines(message, "Record the delivery before the next one starts?")
    assert not any(label_of(relation, "en") in "\n".join(block) for relation in RELATIONS)
    schema_refusal = copy.deepcopy(data)
    schema_refusal["decisions"][1]["others"] = [{"reply_word": "d", "what_it_does": "Wait"}]
    assert rendered(schema_refusal)[0] is None, "a second door brings the requirement with it"


def test_only_a_door_is_a_bullet_and_the_person_s_own_choice_and_what_stays_are_not():
    for name in RECORD_FIXTURES:
        message, problems = rendered(record(name))
        assert problems == [], (name, problems)
        language = record(name)["language"]
        for line in message.split("\n"):
            if line.startswith("   - "):
                assert DOOR_BULLET.match(line), (name, line)
            for fixed in ("own", "if_none"):
                if LABELS[language][fixed] in line:
                    assert not line.lstrip().startswith("-"), (name, line)
                    assert line.startswith("   "), (name, line)


def test_a_lone_decision_is_not_numbered_and_several_are_counted_before_the_first():
    one, _ = rendered(record("record-pt-own-decision.json"))
    assert "1. " not in one and "perguntas" not in one
    assert "\nOs resultados da busca devem ignorar acentos ao ordenar?\n" in one
    two, _ = rendered(record("record-en-two-decisions.json"))
    count = "2 questions, each answered on its own:"
    assert count in two and two.index(count) < two.index("1. Should an empty order")
    assert "2. Record the delivery" in two
    assert two.count("questions, each answered") == 1


def test_every_record_fixture_with_two_doors_or_more_opens_them_with_a_relation():
    """The sweep the next fixture is held to without anyone remembering to add it here."""
    seen: set[tuple[str, str]] = set()
    for name in RECORD_FIXTURES:
        data = record(name)
        message, problems = rendered(data)
        assert problems == [], (name, problems)
        for decision in data.get("decisions", []):
            doors = ([decision["recommended"]] if "recommended" in decision else []) + decision["others"]
            block = block_lines(message, decision["ask"])
            headers = [line for line in block
                       if any(line == f"   {label_of(r, data['language'])}:" for r in RELATIONS)]
            assert len(headers) == (1 if len(doors) >= 2 else 0), (name, block)
            if headers:
                seen.add((decision["relation"], data["language"]))
    assert {relation for relation, _ in seen} == set(RELATIONS)
    assert {language for _, language in seen} == set(LABELS), "the fixtures hold both languages"


def test_the_specification_states_the_relation_and_the_rendering_it_requires():
    text = (REPO / "specs/handoff.md").read_text(encoding="utf-8")
    r1 = re.search(r"^- \*\*R1\*\* — (.*)$", text, re.M).group(1)
    r8 = re.search(r"^- \*\*R8\*\* — (.*)$", text, re.M).group(1)
    for value in RELATIONS:
        assert f"`{value}`" in r8, value
    assert "how the doors relate" in r1 and "a lone decision is not numbered" in r1.lower()
    assert "`relation`" in r8 and "only a door is a bullet" in r1.lower()


# ------------------------------------------------------- --prepare over fixture repositories


from test_door import RECORDED, READY, SLUG, commit, project  # noqa: E402,F401

PREPARED_SKILLS = ("deliver-scope", "adopt-scope", "plan-work", "implement-task", "review-change",
                   "reconcile", "analyse", "siegard-goal", "siegard-status")


def prepare(home: Path, skill: str, *extra: str) -> dict:
    done = run("--prepare", "--skill", skill, "--project", str(home), *extra)
    assert done.returncode == 0, done.stdout + done.stderr
    return json.loads(done.stdout)


def doors_of(prepared: dict) -> dict[str, dict]:
    return {door["entry"]: door["check"] for decision in prepared.get("decisions", [])
            for door in decision["others"]}


def test_every_door_a_report_hands_ready_to_paste_is_named_from_its_own_file():
    assert handoff.next_doors("plan-work") == ["implement-task"]
    assert sorted(handoff.next_doors("implement-task")) == ["reconcile", "review-change"]
    assert sorted(handoff.next_doors("analyse")) == ["plan-work", "reconcile"]
    assert sorted(handoff.next_doors("reconcile")) == ["analyse", "plan-work"]
    assert handoff.next_doors("siegard-status") == ["reconcile"]
    assert handoff.next_doors("review-change") == []


def test_the_state_is_progress_s_segment_for_the_slug(project):
    import progress
    prepared = prepare(project, "plan-work", "--slug", SLUG)
    line = progress.line_of(project)
    assert prepared["state"] == handoff.cut(line, CONTRACT) and prepared["state"].startswith(f"{SLUG} · ")
    assert prepared["state_from"] == {"script": "progress.py", "project": str(project),
                                      "slug": SLUG}


def test_with_no_slug_the_state_is_the_project_s_line(project):
    import progress
    prepared = prepare(project, "siegard-status")
    assert prepared["state"] == handoff.cut(progress.line_of(project), CONTRACT)
    assert "slug" not in prepared["state_from"]


def test_with_nothing_live_the_state_is_the_fixed_words_in_the_record_s_language(tmp_path):
    prepared = prepare(tmp_path, "siegard-status", "--language", "pt-BR")
    assert prepared["state"] == CONTRACT["x-labels"]["pt-BR"]["quiet"]
    assert prepared["language"] == "pt-BR" and "report" not in prepared


def arm(home: Path) -> dict:
    import goal
    record = {"contract": goal.ARMED_CONTRACT, "project_root": str(home), "slug": SLUG,
              "target": "app", "scope": [], "since": commit_of(home), "version": goal.plugin_version(),
              "untouched": [], "objective": None, "objective_sha256": None, "condition": "c",
              "armed_at": "2026-10-31T00:00:00Z", "session_id": None, "blocks": 0,
              "last_state": None}
    goal.write_armed(goal.armed_path(home), record)
    return record


def commit_of(home: Path) -> str:
    return subprocess.run(["git", "-C", str(home), "rev-parse", "HEAD"], capture_output=True,
                          text=True, check=True).stdout.strip()


def test_under_an_armed_goal_the_state_is_the_goal_s_first_line(project):
    import goal
    armed = arm(project)
    prepared = prepare(project, "implement-task", "--slug", SLUG)
    fields = goal.resolve(project, "app")
    first, _ = goal.state(fields, SLUG, armed["since"], armed["version"], [], [])
    assert prepared["state_from"] == {"script": "goal.py", "project": str(project)}
    assert prepared["state"] == handoff.cut(first, CONTRACT)
    assert prepared["state"].startswith(("state A", "state B", "not yet"))


def test_each_door_is_marked_with_what_its_entry_point_answers(project):
    prepared = prepare(project, "implement-task", "--slug", SLUG)
    doors = doors_of(prepared)
    assert doors["/review-change"] == {"answer": "accepts", "refused": []}
    assert doors["/reconcile"]["answer"] == "not checked"
    assert "recommended" not in prepared["decisions"][0]
    assert all(door["reply_word"] == "" and door["what_it_does"] == ""
               for door in prepared["decisions"][0]["others"])
    assert doors_of(prepare(project, "plan-work", "--slug", SLUG))["/implement-task"]["answer"] \
        == "accepts"


def test_a_door_its_entry_point_refuses_is_marked_with_its_fact(project):
    (project / "deliveries" / SLUG / "run").mkdir()
    (project / "deliveries" / SLUG / "run/x.log").write_text("x\n", encoding="utf-8")
    check = doors_of(prepare(project, "implement-task", "--slug", SLUG))["/review-change"]
    assert check["answer"] == "refuses"
    assert any(fact.startswith("git status --porcelain") for fact in check["refused"])
    check = doors_of(prepare(project, "plan-work", "--slug", SLUG))["/implement-task"]
    assert check["answer"] == "refuses"


def test_a_door_no_script_decides_is_never_marked_accepted(project):
    doors = doors_of(prepare(project, "reconcile", "--slug", SLUG))
    assert doors["/analyse"]["answer"] == "not checked" and doors["/analyse"]["why"]
    assert doors["/plan-work"]["answer"] == "accepts"


def test_a_skill_whose_report_hands_no_door_prepares_a_report(project):
    prepared = prepare(project, "siegard-goal")
    assert prepared["kind"] == "report" and "decisions" not in prepared


def test_the_goal_report_followed_by_its_two_lines_to_paste_passes_the_check(project):
    """SPEC-008 R6: the two ways to arm follow the rendered report, each fenced, and a condition
    as long as a consumer's leaves the handoff within what `--check` decides."""
    prepared = prepare(project, "siegard-goal", "--language", "pt-BR")
    Path(prepared["report"]).write_text("full\n", encoding="utf-8")
    prepared["body"] = ("O goal leva o escopo do começo ao fim, faz um commit por passo e termina "
                        "quando o estado lido do disco disser que acabou ou que parou para você.")
    message, problems = handoff.render(prepared, CONTRACT, project)
    assert problems == [], problems
    condition = "Carry this scope end to end through /siegard:deliver-scope. " + "x" * 1200
    text = (message + "\nAs duas formas levam à mesma rota, as duas podem ser encerradas e nenhum "
            "comando mediu custo; pelo framework, o fim é a resposta do script a cada parada e "
            "pressupõe os hooks deste plugin nesta sessão; pelo harness, basta colar.\n\n"
            "```\n/siegard:siegard-goal --arm /p --slug s --target backend --scope epic/e\n```\n\n"
            f"```\n/goal {condition}\n```\n")
    assert handoff.violations(handoff.reading(text, CONTRACT), CONTRACT) == []


def test_the_skeleton_fails_the_schema_only_on_what_the_model_fills(project):
    from jsonschema import Draft202012Validator
    prepared = prepare(project, "implement-task", "--slug", SLUG)
    report = Path(prepared["report"])
    assert report.parent == project / ".git" / "siegard" / "handoff" and report.parent.is_dir()
    assert report.name.endswith("-implement-task.md")
    paths = {"/".join(map(str, e.absolute_path))
             for e in Draft202012Validator(CONTRACT).iter_errors(prepared)}
    fillable = {"decisions/0", "decisions/0/ask", "decisions/0/if_none",
                "decisions/0/relation"} | {
        f"decisions/0/others/{i}/{key}" for i in range(2) for key in ("reply_word", "what_it_does")}
    assert paths and paths <= fillable, paths


def test_a_filled_skeleton_renders_and_a_moved_state_refuses_it(project):
    prepared = prepare(project, "implement-task", "--slug", SLUG)
    decision = prepared["decisions"][0]
    review, reconcile = sorted(decision["others"], key=lambda d: d["entry"] != "/review-change")
    decision.update(ask="Review the task just delivered?", if_none="The delivery waits unreviewed.",
                    relation="one-of",
                    recommended={"entry": review["entry"], "check": review["check"],
                                 "reply_word": "a", "door": "Review it now",
                                 "why": "The check over the review accepts the tree as it stands",
                                 "reverses_if": "a file under the delivery changes first"},
                    others=[{**reconcile, "reply_word": "b",
                             "what_it_does": "Re-check the moved files alone, without a review"}])
    Path(prepared["report"]).write_text("full\n", encoding="utf-8")
    path = project / ".git" / "record.json"
    path.write_text(json.dumps(prepared), encoding="utf-8")
    done = run("--render", str(path))
    assert done.returncode == 0, done.stdout
    assert done.stdout.startswith(f"```\n{prepared['state']}\n```")
    log = project / "deliveries" / SLUG / "orchestration.md"
    log.write_text("- implement-task task/checkout/bill-order — accepted\n", encoding="utf-8")
    done = run("--render", str(path))
    assert done.returncode == 1 and done.stdout.startswith("state: differs from what progress.py")


def write_ledger(home: Path, entries: list[dict]) -> Path:
    """A material ledger as /analyse answers it; `--prepare` reads only how many lines it leaves
    open, so the material it names need not exist here."""
    path = home / "ledger.md"
    front = {"contract_version": "siegard-ledger/1", "material": ["agenda.md"], "entries": entries}
    path.write_text("---\n" + json.dumps(front) + "\n---\n", encoding="utf-8")
    return path


def test_a_ledger_with_open_lines_leads_the_state_and_hands_the_analysis_back(tmp_path):
    """SPEC-001 R16 and SPEC-006 R10: the count of open lines leads the state, before the
    script's line, and the skill itself is a door beside the others."""
    ledger = write_ledger(tmp_path, [{"at": "agenda.md:3", "node": "rules/a/b"},
                                     {"at": "agenda.md:3", "open": "the rest"},
                                     {"at": "agenda.md:5", "open": "all of it"}])
    prepared = prepare(tmp_path, "analyse", "--ledger", str(ledger), "--language", "pt-BR")
    quiet = CONTRACT["x-labels"]["pt-BR"]["quiet"]
    assert prepared["state"] == f"2 linha(s) do material ainda em aberto · {quiet}"
    assert prepared["state_from"]["ledger"] == str(ledger.resolve())
    doors = [door["entry"] for door in prepared["decisions"][0]["others"]]
    assert doors[0] == "/analyse" and "/plan-work" in doors
    assert doors_of(prepared)["/analyse"]["answer"] == "not checked"


def test_a_ledger_with_no_open_line_changes_nothing(tmp_path):
    ledger = write_ledger(tmp_path, [{"at": "agenda.md:3", "node": "rules/a/b"}])
    prepared = prepare(tmp_path, "analyse", "--ledger", str(ledger))
    assert prepared["state"] == CONTRACT["x-labels"]["en"]["quiet"]
    assert "/analyse" not in doors_of(prepared)


def test_a_record_whose_open_count_moved_is_refused_at_render(tmp_path):
    ledger = write_ledger(tmp_path, [{"at": "agenda.md:5", "open": "all of it"}])
    prepared = prepare(tmp_path, "analyse", "--ledger", str(ledger))
    assert prepared["state"].startswith("1 line(s) of the material still open · ")
    write_ledger(tmp_path, [{"at": "agenda.md:5", "node": "rules/a/b"}])
    now = handoff.state_now(prepared["state_from"], "en", CONTRACT)
    assert now == CONTRACT["x-labels"]["en"]["quiet"] != prepared["state"]
    data = record("record-en-two-decisions.json")
    data.update(state=prepared["state"], state_from=prepared["state_from"])
    _, problems = rendered(data, handoff.state_now)
    assert any(p.startswith("state: differs from what progress.py prints now") for p in problems)


def test_prepare_refuses_a_ledger_that_is_no_file(tmp_path):
    done = run("--prepare", "--skill", "analyse", "--project", str(tmp_path),
               "--ledger", str(tmp_path / "missing.md"))
    assert done.returncode == handoff.CANNOT_RUN and "is no ledger file" in done.stderr


@pytest.mark.parametrize("args", [["--prepare"], ["--prepare", "--skill", "plan-work"],
                                  ["--prepare", "--skill", "no-such-skill", "--project", "."],
                                  ["--prepare", "--skill", "plan-work", "--project", ".",
                                   "--language", "fr"]])
def test_prepare_refuses_arguments_it_cannot_read(args):
    done = run(*args)
    assert done.returncode == handoff.CANNOT_RUN and done.stderr.startswith("cannot run:")


@pytest.mark.parametrize("skill", PREPARED_SKILLS)
def test_every_skill_that_reports_through_the_record_names_prepare_and_render(skill):
    text = re.sub(r"\s+", " ", (REPO / "src/claude/skills" / skill / "SKILL.md")
                  .read_text(encoding="utf-8"))
    assert "handoff.py --prepare --skill" in text, f"{skill} never runs --prepare"
    assert "handoff.py --render" in text, f"{skill} never hands what --render prints"
    assert "(SPEC-006 R10)" in text, f"{skill} never cites SPEC-006 R10"


def save_report(path: Path, text: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(SCRIPT), "--save-report", str(path)],
                          input=text, capture_output=True, text=True)


def test_save_report_writes_the_report_under_the_handoff_directory(tmp_path):
    path = tmp_path / ".git" / "siegard" / "handoff" / "20261031T000000Z-plan-work.md"
    done = save_report(path, "the full report")
    assert done.returncode == 0, done.stdout + done.stderr
    assert path.read_text(encoding="utf-8") == "the full report\n"
    assert done.stdout.strip() == str(path.resolve())


def test_save_report_refuses_a_path_outside_the_handoff_directory_and_writes_nothing(tmp_path):
    path = tmp_path / "notes.md"
    done = save_report(path, "the full report")
    assert done.returncode == 1 and done.stdout.startswith("refused:")
    assert not path.exists()


def test_save_report_refuses_a_report_already_written_and_an_empty_one(tmp_path):
    path = tmp_path / ".git" / "siegard" / "handoff" / "20261031T000000Z-plan-work.md"
    assert save_report(path, "first").returncode == 0
    again = save_report(path, "second")
    assert again.returncode == 1 and "already written" in again.stdout
    assert path.read_text(encoding="utf-8") == "first\n"
    empty = save_report(path.with_name("other.md"), "  \n")
    assert empty.returncode == 1 and "empty" in empty.stdout


def test_a_recommendation_written_as_convem_is_read_as_one():
    """Read on 2026-11-09 over 77 stops the Stop hook flagged in the sales consumers: one opened
    "Convém rodar…" — a recommendation in plain Portuguese the stems did not hold."""
    text = "Convém rodar o /reconcile sobre os três arquivos antes de entregar a tarefa de novo."
    assert handoff.decision_word_at(text, CONTRACT, ("recommendation",)) == 0


def test_the_skeleton_carries_an_empty_relation_where_it_hands_two_doors_and_none_for_one(project):
    two = prepare(project, "implement-task", "--slug", SLUG)
    assert len(two["decisions"][0]["others"]) == 2 and two["decisions"][0]["relation"] == ""
    one = prepare(project, "plan-work", "--slug", SLUG)
    assert len(one["decisions"][0]["others"]) == 1 and "relation" not in one["decisions"][0]


def test_a_skeleton_filled_but_for_its_relation_is_refused_on_that_field_alone(project):
    prepared = prepare(project, "implement-task", "--slug", SLUG)
    decision = prepared["decisions"][0]
    review, reconcile = decision["others"]
    decision.update(ask="Review the task just delivered?", if_none="The delivery waits.",
                    recommended={"entry": review["entry"], "check": review["check"],
                                 "reply_word": "a", "door": "Review it now",
                                 "why": "The check accepts the tree as it stands",
                                 "reverses_if": "a file under the delivery changes first"},
                    others=[{**reconcile, "reply_word": "b", "what_it_does": "Re-check the files"}])
    Path(prepared["report"]).write_text("full\n", encoding="utf-8")
    message, problems = handoff.render(prepared, CONTRACT, Path("."))
    assert message is None
    assert [p.split(":")[0] for p in problems] == ["decisions/0/relation"], problems
