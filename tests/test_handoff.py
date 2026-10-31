"""A handoff is rendered from its record, and a handoff written as free text is held to what the
text alone decides (SPEC-006 R8).

The fixtures under `fixtures/handoff/` are synthetic, written in the shapes the handoffs that
motivated R8 took — a Portuguese report that opens on the framework's own words and buries its
recommendation under pending items, hashes and measurements; an English one asking which door
without recommending any; a long status answer that hands nothing — and the shapes R8 asks for.
No consumer's text is copied. Each message fixture is named with what it is, and the expected
violations are the prefixes `--check` prints: `opening`, `length`, `decision`.
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


def rendered(data: dict) -> tuple[str | None, list[str]]:
    return handoff.render(data, CONTRACT, FIXTURES)


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
                                  "record-pt-status.json"])
def test_a_record_renders_and_what_it_renders_holds(name):
    message, problems = rendered(record(name))
    assert problems == [] and message
    assert handoff.violations(handoff.reading(message, CONTRACT), CONTRACT) == []


def test_the_rendering_opens_with_the_state_and_the_recommendation_first():
    message, _ = rendered(record("record-en-two-decisions.json"))
    assert message.startswith("The order screen is delivered")
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


def test_the_command_renders_from_a_file_and_from_standard_input():
    data = (FIXTURES / "record-en-two-decisions.json").read_text(encoding="utf-8")
    from_file = run("--render", str(FIXTURES / "record-en-two-decisions.json"), cwd=FIXTURES)
    from_stdin = run("--render", "-", stdin=data, cwd=FIXTURES)
    assert from_file.returncode == 0 and from_stdin.returncode == 0, from_file.stdout
    assert from_file.stdout == from_stdin.stdout == rendered(json.loads(data))[0]


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
    long = "word " * 90
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


def test_the_command_refuses_with_one_line_per_problem_and_exit_one(tmp_path):
    data = record("record-en-two-decisions.json")
    data["state"] = "The binder is done"
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
