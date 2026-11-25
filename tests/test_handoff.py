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
import yaml

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


COMPOSED = {name for name in MESSAGES if name != "pt-long-status-answer.md"}


@pytest.mark.parametrize("name", sorted(MESSAGES))
def test_the_command_exits_on_what_the_functions_return_and_refuses_a_composed_decision(name):
    """The functions the Stop hooks read are unchanged; the command adds one refusal: «Where text
    given to `--check` hands a decision and carries no line `--render` writes for one — the line
    that opens with the words the schema holds for what stays if no door is taken — `--check`
    refuses it as composed and names `--render`» (SPEC-006 R8). Every decision fixture is free
    text a session wrote, so each is refused as composed; the status answer hands none."""
    done = run("--check", str(FIXTURES / name))
    expected = MESSAGES[name] | ({"composed"} if name in COMPOSED else set())
    assert done.returncode == (1 if expected else 0), done.stdout + done.stderr
    assert kinds(done.stdout.splitlines()) == expected
    assert done.stderr == ""
    if name in COMPOSED:
        assert "--render" in done.stdout.splitlines()[-1]


@pytest.mark.parametrize("name", ["record-en-independent-doors.json", "record-en-two-decisions.json",
                                  "record-pt-own-decision.json", "record-pt-path-in-order.json",
                                  "record-pt-route-steps.json"])
def test_a_decision_render_printed_is_not_refused_as_composed(name):
    data = record(name)
    message, problems = rendered(data)
    assert problems == [], problems
    assert handoff.rendered(message, CONTRACT)
    done = run("--check", "-", stdin=message)
    assert "composed" not in kinds(done.stdout.splitlines()), done.stdout


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
    chosen = kept["decisions"][0]["recommended"]
    assert chosen["entry"] == "/plan-work" and chosen["check"]["answer"] == "not checked"
    del chosen["entry"], chosen["check"]
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


def own_choice(settles_by=None) -> dict:
    data = copy.deepcopy(record("record-en-two-decisions.json"))
    decision = data["decisions"][0]
    decision.pop("recommended")
    decision["settles"] = "The first assumes the rule holds, the second that it does not."
    if settles_by is not None:
        decision["settles_by"] = settles_by
    decision["relation"] = "one-of"
    decision["others"].insert(0, {"reply_word": "z", "what_it_does": "Refuse it"})
    return data


def test_a_choice_left_to_the_person_without_its_class_is_refused_and_told_to_recommend():
    """«No recommendation is made over a scope and a specification that contradict, over two
    readings of one piece of evidence, or over whether a finding matters or what route it
    deserves.» (SPEC-006 R3) Any other choice is recommended, so `settles` names which it is."""
    for given in (None, "cost"):
        message, problems = rendered(own_choice(given))
        assert message is None
        said = [p for p in problems if p.startswith("decisions/0/settles_by:")]
        assert len(said) == 1 and len(problems) == 1, problems
        for value in CONTRACT["$defs"]["decision"]["properties"]["settles_by"]["enum"]:
            assert value in said[0]
        assert "recommend its door as a judgment" in said[0]


@pytest.mark.parametrize("value", ["contradiction", "two-readings", "all-excluded"])
def test_a_choice_left_to_the_person_under_one_of_the_four_renders(value):
    message, problems = rendered(own_choice(value))
    assert message is not None, problems


def review_record(at: Path, findings: list) -> Path:
    path = at / "review" / "first.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("---\n" + yaml.safe_dump({"target": "app", "title": "Review", "findings": findings})
                    + "---\n\nBody.\n", encoding="utf-8")
    return path


def test_a_finding_s_worth_naming_no_finding_is_refused_and_told_to_recommend():
    """«A choice left to the person as `finding-worth` names in `finding` the review record that
    holds the finding, and `--render` refuses it where that record holds no finding» (SPEC-006 R3)."""
    message, problems = rendered(own_choice("finding-worth"))
    assert message is None
    said = [p for p in problems if p.startswith("decisions/0/finding:")]
    assert len(said) == 1, problems
    assert "review record" in said[0] and "recommend" in said[0]
    assert said[0].index("two-readings") < said[0].index("recommend its door"), said[0]


def test_a_finding_s_worth_naming_a_review_record_with_findings_renders(tmp_path):
    choice = own_choice("finding-worth")
    named = str(review_record(tmp_path, [{"where": "a", "kind": "unstated"}]))
    choice["decisions"][0]["finding"] = named
    message, problems = rendered(choice)
    assert message is not None, problems
    assert f"(`{named}`)" in message, message


def test_a_finding_s_worth_naming_a_record_from_the_project_root_renders(tmp_path):
    review_record(tmp_path / "deliveries" / "s", [{"where": "a", "kind": "unstated"}])
    choice = own_choice("finding-worth")
    choice["state_from"] = {"script": "progress.py", "project": str(tmp_path)}
    choice["decisions"][0]["finding"] = "deliveries/s/review/first.md"
    message, problems = rendered(choice, state_of=lambda source, language, contract: choice["state"])
    assert message is not None, problems


def test_a_finding_s_worth_naming_a_file_with_no_frontmatter_is_refused(tmp_path):
    plain = tmp_path / "plain.md"
    plain.write_text("findings: one\n", encoding="utf-8")
    choice = own_choice("finding-worth")
    choice["decisions"][0]["finding"] = str(plain)
    message, problems = rendered(choice)
    assert message is None and any("holds no finding" in p for p in problems), problems


def test_a_finding_named_beside_another_class_is_not_shown(tmp_path):
    choice = own_choice("two-readings")
    choice["decisions"][0]["finding"] = str(tmp_path / "unchecked.md")
    message, problems = rendered(choice)
    assert message is not None and "unchecked.md" not in message, problems


def test_a_finding_s_worth_naming_a_record_without_findings_or_no_file_is_refused(tmp_path):
    for named in (str(review_record(tmp_path, [])), str(tmp_path / "review" / "absent.md")):
        choice = own_choice("finding-worth")
        choice["decisions"][0]["finding"] = named
        message, problems = rendered(choice)
        assert message is None and any(p.startswith("decisions/0/finding:") for p in problems), problems


def test_a_recommendation_never_carries_the_class_of_a_choice_left_to_the_person():
    problems = refusal(lambda d: d["decisions"][0].update(settles_by="contradiction"))
    assert any(p.startswith("decisions/0") for p in problems)


def test_the_note_asks_for_the_slug_a_recommended_door_went_unchecked_without():
    data = {"decisions": [
        {"recommended": {"entry": "/plan-work", "check": {
            "answer": "not checked", "why": f"/plan-work {handoff.UNNAMED_SLUG}"}}},
        {"recommended": {"entry": "/reconcile", "check": {
            "answer": "not checked", "why": "no script decides it"}}},
        {"recommended": {"entry": "/plan-work", "check": {"answer": "accepts"}}}]}
    assert handoff.unslugged_recommendations(data) == [
        "note: decision 1: the recommended door /plan-work was not checked because it takes a "
        "slug and none was named — carry `--slug <slug>` in the decision's `invocation` and "
        "render again"]


def test_with_two_live_initiatives_the_unchecked_door_is_noted_under_a_grant(project, monkeypatch):
    make_second_initiative(project)
    prepared = prepared_for_plan_work(project)
    done = handoff.completed(prepared)
    import grant
    monkeypatch.setattr(grant, "decide", lambda *_: (
        ["grant: every live initiative (sha256 0000000000000000)",
         "decision 1: stop: the one door left was not checked by `door.py --check`"], 0))
    lines = handoff.grant_answer(done)
    assert any(line.startswith("note: decision 1: the recommended door /plan-work was not "
                               "checked") for line in lines)


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
        decision["settles_by"] = "two-readings"
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


def two_targets(home: Path) -> None:
    from test_door import declare
    (home / "web").mkdir()
    (home / "web/.keep").write_text("", encoding="utf-8")
    declare(home, targets={"app": "target", "web": "web"}, standard={"app": None, "web": None})
    commit(home)


def refused_of(prepared: dict, entry: str) -> list[str]:
    return doors_of(prepared)[entry].get("refused", [])


def test_a_door_is_checked_over_the_target_the_armed_goal_names(project):
    """«A door that takes a target and is checked with none named is checked over the target the
    armed goal names, where the check runs over that goal's own initiative» (SPEC-006 R9)"""
    two_targets(project)
    arm(project)
    prepared = prepare(project, "analyse", "--slug", SLUG)
    check = doors_of(prepared)["/plan-work"]
    assert not any("no target named" in line for line in check.get("refused", [])), check


def test_with_no_goal_armed_a_project_of_two_targets_still_refuses_for_want_of_one(project):
    two_targets(project)
    prepared = prepare(project, "analyse", "--slug", SLUG)
    assert any("no target named" in line for line in refused_of(prepared, "/plan-work"))


def test_a_goal_over_another_initiative_names_no_target_for_this_one(project):
    two_targets(project)
    arm(project)
    prepared = prepare(project, "analyse", "--slug", "another-initiative")
    assert any("no target named" in line for line in refused_of(prepared, "/plan-work"))


def test_a_target_named_wins_over_the_goal_s(project):
    two_targets(project)
    arm(project)
    prepared = prepare(project, "analyse", "--slug", SLUG, "--target", "web")
    assert not any("no target named" in line for line in refused_of(prepared, "/plan-work"))


def test_render_checks_the_recommended_door_over_the_armed_goal_s_target(project):
    two_targets(project)
    arm(project)
    record = {"entry": "/plan-work"}
    done = handoff.completed({"kind": "decision", "state_from": {"script": "goal.py",
                                                                  "project": str(project)},
                              "decisions": [{"invocation": f"/siegard:plan-work --slug {SLUG}",
                                             "recommended": record, "others": []}]})
    check = done["decisions"][0]["recommended"]["check"]
    assert not any("no target named" in line for line in check.get("refused", [])), check


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


def arm_grant(home: Path) -> None:
    done = subprocess.run([sys.executable, "-B", str(REPO / "src/claude/bin/grant.py"), "--arm",
                           str(home), "--budget", "2", "--words-file", "-"],
                          input="siga a recomendação", capture_output=True, text=True)
    assert done.returncode == 0, done.stdout + done.stderr


def test_a_status_with_no_grant_standing_prepares_a_report(project):
    """«`--prepare --skill siegard-status` hands its doors only where a grant stands, and prints
    kind `report` where none does» (SPEC-006 R11)."""
    prepared = prepare(project, "siegard-status")
    assert prepared["kind"] == "report" and "decisions" not in prepared


def test_a_status_under_a_standing_grant_prepares_its_doors(project):
    arm_grant(project)
    prepared = prepare(project, "siegard-status", "--slug", SLUG)
    assert prepared["kind"] == "decision"
    assert list(doors_of(prepared)) == ["/reconcile"]


def test_a_status_decision_under_a_grant_renders_with_the_grant_s_answer(project):
    arm_grant(project)
    prepared = prepare(project, "siegard-status", "--slug", SLUG)
    one = prepared["decisions"][0]
    one.update(ask="Deliver the next task now?", if_none="Nothing runs.", relation="one-of",
               invocation=f"/implement-task --slug {SLUG}")
    one["recommended"] = {"reply_word": "a", "door": "Deliver it", "entry": "/implement-task",
                          "why": "It is the one task ready", "reverses_if": "you want a review first"}
    for door in one["others"]:
        door.update(reply_word="b", what_it_does="Reread the links")
    Path(prepared["report"]).write_text("full\n", encoding="utf-8")
    done = run("--render", "-", stdin=json.dumps(prepared))
    assert done.returncode == 0, done.stdout + done.stderr
    assert "grant: every live initiative" in done.stderr
    assert "decision 1: judge: spawn the door decider over these doors, budget left 2" \
        in done.stderr, done.stderr


def report_of(project: Path, skill: str, body: str) -> dict:
    """The skeleton `--prepare` printed for `skill`, rewritten by hand as kind `report` with
    `body`, its full report written."""
    prepared = prepare(project, skill, "--slug", SLUG)
    prepared.pop("decisions", None)
    prepared.update(kind="report", body=body)
    Path(prepared["report"]).write_text("full\n", encoding="utf-8")
    return prepared


SUGGESTING = ("Both tasks are delivered and the suite passed. I suggest reviewing the delivery "
              "next. It would change if you want the stale links reread first.")


def test_a_report_recommending_a_next_step_under_a_standing_grant_is_refused(project):
    """«Where a grant covering the record's initiative stands, `--render` refuses kind `report`
    from a skill whose report hands doors when its body recommends, so the step is handed as a
    decision the grant answers» (SPEC-006 R11)."""
    arm_grant(project)
    done = run("--render", "-", stdin=json.dumps(report_of(project, "implement-task", SUGGESTING)))
    assert done.returncode == 1, done.stdout + done.stderr
    assert "kind: " in done.stdout and "SPEC-006 R11" in done.stdout, done.stdout
    assert "--prepare" in done.stdout and "settles_by" in done.stdout, done.stdout


def test_the_step_handed_as_a_choice_left_to_the_person_under_a_grant_renders_with_its_stop(project):
    """The refused report's step re-rendered as the person's own choice — a finding's worth —
    renders, and the grant stops on it: the refusal never makes the framework decide one of the
    three questions."""
    arm_grant(project)
    prepared = prepare(project, "implement-task", "--slug", SLUG)
    one = prepared["decisions"][0]
    one.update(ask="Does the finding on the price list deserve a correction?",
               if_none="The finding stays recorded.", relation="one-of",
               settles="Correcting assumes the list is wrong; leaving it assumes the node allows it.",
               settles_by="finding-worth",
               finding=str(review_record(project / "deliveries" / SLUG, [{"where": "a", "kind": "unstated"}])))
    for word, door in zip("ab", one["others"]):
        door.update(reply_word=word, what_it_does="Take this step")
    Path(prepared["report"]).write_text("full\n", encoding="utf-8")
    done = run("--render", "-", stdin=json.dumps(prepared))
    assert done.returncode == 0, done.stdout + done.stderr
    assert "decision 1: stop: the choice is the person's" in done.stderr, done.stderr


def test_a_status_report_recommending_nothing_renders_under_a_standing_grant(project):
    arm_grant(project)
    body = "Every initiative is delivered and reviewed. Nothing waits on you."
    done = run("--render", "-", stdin=json.dumps(report_of(project, "siegard-status", body)))
    assert done.returncode == 0, done.stdout + done.stderr


def test_prepare_says_so_where_a_grant_covers_the_initiative(project):
    done = run("--prepare", "--skill", "implement-task", "--project", str(project), "--slug", SLUG)
    assert "never `report`" not in done.stderr, done.stderr
    arm_grant(project)
    done = run("--prepare", "--skill", "implement-task", "--project", str(project), "--slug", SLUG)
    assert done.returncode == 0, done.stderr
    assert "limits: a grant covers this initiative" in done.stderr, done.stderr
    done = run("--prepare", "--skill", "siegard-goal", "--project", str(project))
    assert "limits: a grant covers this initiative" not in done.stderr, done.stderr


def test_a_report_recommending_over_an_initiative_the_grant_does_not_name_renders(project):
    arm_grant(project)
    import grant
    path = grant.grant_path(project)
    held = json.loads(path.read_text(encoding="utf-8"))
    held["slug"] = "another-initiative"
    path.write_text(json.dumps(held), encoding="utf-8")
    assert grant.standing(project)[3] is None
    assert handoff.grant_covers(project, "another-initiative")
    done = run("--render", "-", stdin=json.dumps(report_of(project, "implement-task", SUGGESTING)))
    assert done.returncode == 0, done.stdout + done.stderr


def test_a_report_recommending_with_no_state_source_renders_under_a_grant(project):
    arm_grant(project)
    prepared = report_of(project, "implement-task", SUGGESTING)
    prepared.pop("state_from")
    done = run("--render", "-", stdin=json.dumps(prepared))
    assert done.returncode == 0, done.stdout + done.stderr


def test_a_report_recommending_a_next_step_with_no_grant_renders(project):
    done = run("--render", "-", stdin=json.dumps(report_of(project, "implement-task", SUGGESTING)))
    assert done.returncode == 0, done.stdout + done.stderr


def test_a_report_recommending_nothing_under_a_standing_grant_renders(project):
    arm_grant(project)
    body = "Both tasks are delivered and the suite passed. Nothing waits on you."
    done = run("--render", "-", stdin=json.dumps(report_of(project, "plan-work", body)))
    assert done.returncode == 0, done.stdout + done.stderr


def test_a_report_of_a_skill_handing_no_door_renders_under_a_standing_grant(project):
    arm_grant(project)
    prepared = prepare(project, "siegard-goal")
    prepared["body"] = SUGGESTING
    Path(prepared["report"]).write_text("full\n", encoding="utf-8")
    done = run("--render", "-", stdin=json.dumps(prepared))
    assert done.returncode == 0, done.stdout + done.stderr


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
    """Every door a skill's report hands has a check since `/analyse` gained one (SPEC-006 R9);
    an entry point no script decides, such as `/survey`, is still never marked accepted."""
    unchecked = handoff.check_door("survey", project, SLUG, None, [])
    assert unchecked["answer"] == "not checked" and unchecked["why"]
    doors = doors_of(prepare(project, "reconcile", "--slug", SLUG))
    assert doors["/analyse"]["answer"] == "accepts"
    assert doors["/plan-work"]["answer"] == "accepts"


def test_a_skill_whose_report_hands_no_door_prepares_a_report(project):
    prepared = prepare(project, "siegard-goal")
    assert prepared["kind"] == "report" and "decisions" not in prepared


def test_the_goal_report_followed_by_its_line_to_paste_passes_the_check(project):
    """SPEC-008 R6: the line that arms through the framework follows the rendered report, fenced,
    and the handoff stays within what `--check` decides; the condition is in the full report."""
    prepared = prepare(project, "siegard-goal", "--language", "pt-BR")
    Path(prepared["report"]).write_text("full\n", encoding="utf-8")
    prepared["body"] = ("O goal leva o escopo do começo ao fim, faz um commit por passo e termina "
                        "quando o estado lido do disco disser que acabou ou que parou para você.")
    message, problems = handoff.render(prepared, CONTRACT, project)
    assert problems == [], problems
    text = (message + "\n```\n/siegard:siegard-goal --arm /p --slug s --target backend "
            "--objective-file /p/siegard/telemetry/goal-20261114T103247Z-s.md\n```\n")
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
    assert doors_of(prepared)["/analyse"]["answer"] == "refuses"


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



def test_prepare_prints_the_limits_beside_the_skeleton_on_standard_error(project):
    """«Beside the skeleton, on standard error, it prints the limits `--render` holds a record to
    — the ceilings of the state, of each decision's block and of the message, what a decision
    carries, the words in the record's language a body that recommends says the reversing fact
    after, that the record holds the skeleton's fields and no other, and the closed list's terms,
    phrases and pattern names» (SPEC-006 R10)."""
    done = run("--prepare", "--skill", "implement-task", "--project", str(project), "--slug", SLUG,
               "--language", "pt-BR")
    assert done.returncode == 0, done.stdout + done.stderr
    json.loads(done.stdout)
    lines = done.stderr.splitlines()
    assert lines and all(line.startswith(("limits: ", "next: ")) for line in lines)
    assert CONTRACT["x-labels"]["pt-BR"]["reverses_if"] in done.stderr
    assert "no other" in done.stderr
    ceilings, jargon = CONTRACT["x-ceilings"], CONTRACT["x-jargon"]
    for key in ("state", "block", "message"):
        assert str(ceilings[key]) in done.stderr
    for field in ("recommended", "settles", "settles_by", "relation", "reverses_if"):
        assert field in done.stderr
    for word in (*jargon["terms"], *jargon["english_terms"], *jargon["phrases"],
                 *jargon["patterns"]):
        assert word in done.stderr, word


def test_prepare_prints_the_invocations_that_follow_ready_to_paste(project):
    """«after them the two invocations that follow, ready to paste: `--save-report` over the
    skeleton's report path, the report read from standard input, and `--render` over the filled
    record» (SPEC-006 R10)."""
    done = run("--prepare", "--skill", "implement-task", "--project", str(project), "--slug", SLUG)
    assert done.returncode == 0, done.stdout + done.stderr
    record = json.loads(done.stdout)
    after = done.stderr.splitlines()
    nexts = [line for line in after if line.startswith("next: ")]
    assert len(nexts) == 2 and after[-2:] == nexts
    assert f"--save-report {record['report']}" in nexts[0]
    assert "--render" in nexts[1]
    assert all(str(SCRIPT) in line or "handoff.py" in line for line in nexts)


# ------------------------------------------------------- --render writes the check of each door


def filled(project: Path, skill: str, recommended: dict, **decision) -> tuple[dict, Path]:
    """A skeleton filled the way a session fills it, the recommended door written whole and the
    other doors left as `--prepare` printed them, with the report saved where it names."""
    prepared = prepare(project, skill, "--slug", SLUG)
    one = prepared["decisions"][0]
    one.update(ask="Which step comes next?", if_none="The work waits.", relation="one-of",
               recommended={"reply_word": "a", "why": "The check accepts the tree as it stands",
                            "reverses_if": "a file under the delivery changes first",
                            **recommended}, **decision)
    for number, other in enumerate(one["others"]):
        other.update(reply_word=f"x{number}", what_it_does="Another way, leaving this one open")
    Path(prepared["report"]).write_text("full\n", encoding="utf-8")
    return prepared, Path(prepared["report"])


def render_kept(project: Path, prepared: dict) -> tuple[subprocess.CompletedProcess, dict]:
    done = run("--render", "-", stdin=json.dumps(prepared), cwd=project)
    kept = Path(prepared["report"]).with_suffix(".json")
    return done, json.loads(kept.read_text(encoding="utf-8")) if kept.is_file() else {}


def drop(prepared: dict, entry: str) -> None:
    prepared["decisions"][0]["others"] = [door for door in prepared["decisions"][0]["others"]
                                          if door["entry"] != entry]


def test_a_recommended_door_that_lost_its_entry_takes_the_one_its_invocation_opens_with(project):
    """«`--render` writes the `entry` and the `check` of the door a record recommends, from the
    entry the door carries or the one its invocation opens with» (SPEC-006 R9)"""
    prepared, _ = filled(project, "implement-task", {"door": "Review it now"},
                         invocation=f"/review-change {project} --slug {SLUG}")
    drop(prepared, "/review-change")
    done, kept = render_kept(project, prepared)
    assert done.returncode == 0, done.stdout
    chosen = kept["decisions"][0]["recommended"]
    assert chosen["entry"] == "/review-change" and chosen["check"]["answer"] == "accepts"
    assert "entry" not in prepared["decisions"][0]["recommended"], "the record came without one"


def test_a_recommended_door_with_no_entry_and_no_invocation_is_kept_as_it_came(project):
    prepared, _ = filled(project, "implement-task", {"door": "Pick the review name yourself"})
    drop(prepared, "/review-change")
    done, kept = render_kept(project, prepared)
    assert done.returncode == 0, done.stdout
    assert "entry" not in kept["decisions"][0]["recommended"]
    assert "check" not in kept["decisions"][0]["recommended"]


def test_the_check_a_recommended_door_carries_is_run_again_when_the_record_is_rendered(project):
    """The tree moved between `--prepare` and `--render`: the check the record carries said
    `accepts`, and the check run now refuses, so the record is refused as `--prepare`'s would be."""
    prepared, _ = filled(project, "implement-task", {"door": "Review it now"})
    review = next(door for door in prepared["decisions"][0]["others"]
                  if door["entry"] == "/review-change")
    assert review["check"]["answer"] == "accepts"
    drop(prepared, "/review-change")
    prepared["decisions"][0]["recommended"].update(entry="/review-change", check=review["check"])
    (project / "deliveries" / SLUG / "run").mkdir()
    (project / "deliveries" / SLUG / "run/x.log").write_text("x\n", encoding="utf-8")
    done, kept = render_kept(project, prepared)
    assert done.returncode == 1 and "refused by its own entry point" in done.stdout
    assert kept == {}, "a refused record is not kept"


def test_a_door_of_others_with_an_entry_and_no_check_gets_its_check(project):
    prepared, _ = filled(project, "implement-task", {"door": "Review it now",
                                                     "entry": "/review-change"})
    drop(prepared, "/review-change")
    for other in prepared["decisions"][0]["others"]:
        other.pop("check")
    done, kept = render_kept(project, prepared)
    assert done.returncode == 0, done.stdout
    answers = {door["entry"]: door["check"]["answer"] for door in kept["decisions"][0]["others"]}
    assert answers == {"/reconcile": "not checked"}


def make_second_initiative(project: Path) -> None:
    work = project / json.loads((project / "siegard.json").read_text())["work_root"]
    (work / "another-initiative").mkdir()
    (work / "another-initiative" / "intake.md").write_text("x\n", encoding="utf-8")


def prepared_for_plan_work(project: Path, **decision) -> dict:
    """A decision recommending `/plan-work` whose `state_from` names no slug, as `--prepare`
    wrote it where the skill named none."""
    prepared = prepare(project, "analyse")
    assert "slug" not in prepared["state_from"]
    one = prepared["decisions"][0]
    one.update(ask="Plan the correction next?", if_none="The code stays as it is.",
               relation="one-of", **decision)
    one["recommended"] = {"reply_word": "a", "door": "Plan it", "entry": "/plan-work",
                          "why": "The specification changed and the code did not",
                          "reverses_if": "you want to read the specification first"}
    one["others"] = [{"reply_word": "b", "what_it_does": "Leave it", "entry": "/reconcile",
                      "check": {"answer": "not checked", "why": "no script decides it"}}]
    Path(prepared["report"]).write_text("full\n", encoding="utf-8")
    return prepared


def test_a_door_that_needs_a_slug_is_checked_over_the_one_live_initiative_and_says_so(project):
    prepared = prepared_for_plan_work(project)
    done, kept = render_kept(project, prepared)
    assert done.returncode == 0, done.stdout
    check = kept["decisions"][0]["recommended"]["check"]
    assert check["answer"] == "accepts" and check["inferred_slug"] == SLUG


def test_a_slug_the_record_names_is_never_marked_inferred(project):
    prepared = prepared_for_plan_work(project, invocation=f"/plan-work {project} --slug {SLUG}")
    done, kept = render_kept(project, prepared)
    assert done.returncode == 0, done.stdout
    check = kept["decisions"][0]["recommended"]["check"]
    assert check["answer"] == "accepts" and "inferred_slug" not in check


def test_with_two_live_initiatives_no_slug_is_inferred_and_the_door_stays_unchecked(project):
    make_second_initiative(project)
    prepared = prepared_for_plan_work(project)
    done, kept = render_kept(project, prepared)
    assert done.returncode == 0, done.stdout
    check = kept["decisions"][0]["recommended"]["check"]
    assert check["answer"] == "not checked" and "inferred_slug" not in check


def test_a_door_that_takes_no_slug_is_not_given_an_inferred_one(project):
    prepared, _ = filled(project, "plan-work", {"door": "Deliver it", "entry": "/implement-task"})
    drop(prepared, "/implement-task")
    prepared["state_from"].pop("slug", None)
    done, kept = render_kept(project, prepared)
    assert "inferred_slug" not in kept["decisions"][0]["recommended"]["check"]


def test_an_invocation_naming_the_plugin_gives_the_recommended_door_its_entry(project):
    prepared = prepared_for_plan_work(project, invocation=f"/siegard:plan-work {project} --slug {SLUG}")
    prepared["decisions"][0]["recommended"].pop("entry")
    done = handoff.completed(prepared)
    chosen = done["decisions"][0]["recommended"]
    assert chosen["entry"] == "/plan-work" and chosen["check"]["answer"] == "accepts"


def test_a_recommended_door_naming_one_door_of_the_route_in_its_words_takes_it():
    assert handoff.named_door({"door": "Run /siegard:review-change over it", "why": "x"}) \
        == "/review-change"
    assert handoff.named_door({"door": "Plan it", "why": "/plan-work reads the scope"}) \
        == "/plan-work"
    assert handoff.named_door({"door": "Plan with /plan-work or /reconcile first"}) is None
    assert handoff.named_door({"door": "Move src/plan-work to /tmp"}) is None
    assert handoff.named_door({"door": "Write the change request"}) is None


RECONCILE_OUTPUT = """trace: x
reconcile set over target backend (backend), spelled from the target source root — one /reconcile invocation reads it whole:
  src/a.ts  (code)
  src/b.ts  (moved: rules/x)
  2 file(s)
  free slug: reconcile-20261121-backend
left to a delivery — a live task not yet delivered implements the node:
  src/c.ts  (rules/y)
"""


def test_the_reconcile_set_is_read_from_what_trace_prints(monkeypatch, tmp_path):
    import door
    monkeypatch.setattr(door, "script", lambda *_: (0, RECONCILE_OUTPUT))
    assert handoff.reconcile_set(tmp_path, tmp_path) == (["src/a.ts", "src/b.ts"],
                                                          "reconcile-20261121-backend")
    monkeypatch.setattr(door, "script", lambda *_: (0, "reconcile set over target backend (b):\n"
                                                       "  nothing: no drift this target holds"))
    assert handoff.reconcile_set(tmp_path, tmp_path) == ([], None)
    monkeypatch.setattr(door, "script", lambda *_: (1, "no trace file"))
    assert handoff.reconcile_set(tmp_path, tmp_path) is None


def test_a_reconcile_door_is_checked_over_the_set_and_slug_its_trace_prints(monkeypatch, tmp_path):
    import door
    (tmp_path / "siegard.json").write_text(json.dumps({"targets": {"backend": "backend"}}))
    asked = {}

    class Said:
        def lines(self, _):
            return ["accepts", "checked: the record is free"]

    def check(name, project, args):
        asked.update(args)
        return Said()

    monkeypatch.setattr(door, "check", check)
    monkeypatch.setattr(handoff, "reconcile_set", lambda *_: (["src/a.ts"], "reconcile-x"))
    got = handoff.check_door("reconcile", tmp_path, None, None, [])
    assert got["answer"] == "accepts" and "reconcile-x" in got["why"]
    assert asked["file"] == ["src/a.ts"] and asked["slug"] == "reconcile-x" \
        and asked["target"] == "backend"
    monkeypatch.setattr(handoff, "reconcile_set", lambda *_: ([], None))
    assert handoff.check_door("reconcile", tmp_path, None, None, [])["answer"] == "refuses"
    monkeypatch.setattr(handoff, "reconcile_set", lambda *_: None)
    assert handoff.check_door("reconcile", tmp_path, None, None, [])["answer"] == "not checked"


def test_a_reconcile_door_with_several_targets_and_none_named_is_not_checked(monkeypatch, tmp_path):
    (tmp_path / "siegard.json").write_text(json.dumps({"targets": {"a": "a", "b": "b"}}))
    monkeypatch.setattr(handoff, "goal_target", lambda *_: None)
    got = handoff.check_door("reconcile", tmp_path, None, None, [])
    assert got["answer"] == "not checked" and "no target was named" in got["why"]


def test_a_record_naming_no_project_directory_is_rendered_as_it_came(tmp_path):
    data = record("record-en-two-decisions.json")
    data["state"] = CONTRACT["x-labels"]["en"]["quiet"]
    data["state_from"] = {"script": "progress.py", "project": str(tmp_path / "absent")}
    assert handoff.completed(data) is data


def test_a_check_that_cannot_run_is_not_checked_and_never_breaks_the_render():
    def broken(*_):
        raise RuntimeError("no registry")
    check = handoff.check_as_it_stands("/review-change", Path("."), {}, "", broken)
    assert check["answer"] == "not checked" and "no registry" in check["why"]


def test_the_specification_states_what_render_writes_for_a_door():
    text = (REPO / "specs/handoff.md").read_text(encoding="utf-8")
    r9 = re.search(r"^- \*\*R9\*\* — (.*)$", text, re.M).group(1)
    for words in ("`--render` writes the `entry` and the `check` of the door a record recommends",
                  "`inferred_slug`"):
        assert words in r9, words


# ------------------------------------------------------------ routing a request (SPEC-011 R14)


def recorded_ask(home: Path) -> Path:
    path = home / "telemetry" / "ask-20261125T000000Z.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("adicione o desconto por fidelidade ao pedido\n", encoding="utf-8")
    return path


def route(home: Path, *extra: str) -> subprocess.CompletedProcess:
    return run("--prepare", "--route", "--project", str(home), *extra)


def test_a_routing_skeleton_hands_analyse_and_plan_work_each_checked(project):
    """«whose doors are `/analyse` and `/plan-work`, each checked by `door.py --check` as the tree
    stands and never over an initiative the record does not name; the record is kept under a
    report whose name no skill's report carries» (SPEC-011 R14)"""
    ask = recorded_ask(project)
    done = route(project, "--slug", "loyalty-discount", "--ask", str(ask), "--language", "pt-BR")
    assert done.returncode == 0, done.stdout + done.stderr
    prepared = json.loads(done.stdout)
    assert prepared["kind"] == "decision" and prepared["language"] == "pt-BR"
    assert prepared["report"].endswith("-route.md")
    assert handoff.is_routing(prepared)
    checks = doors_of(prepared)
    assert list(checks) == ["/analyse", "/plan-work"]
    assert checks["/analyse"]["answer"] == "accepts"
    assert checks["/plan-work"]["answer"] == "accepts"
    assert prepared["state_from"].get("slug") == "loyalty-discount"
    assert str(ask) in prepared["decisions"][0]["ask"]


def test_a_routing_door_refused_for_want_of_a_target_is_not_checked(project):
    """«nor refused for want of a target it does not name: such a door is not checked» (SPEC-006
    R9): in a project of two targets the request names none yet, and a refusal the record's own
    inputs produced would hand the grant `/analyse` as the one route left."""
    two_targets(project)
    prepared = json.loads(route(project, "--slug", "loyalty-discount", "--ask",
                                str(recorded_ask(project))).stdout)
    checks = doors_of(prepared)
    assert checks["/analyse"]["answer"] == "accepts"
    assert checks["/plan-work"] == {"answer": "not checked",
                                    "why": f"/plan-work {handoff.UNNAMED_TARGET}"}
    one = prepared["decisions"][0]
    one["recommended"] = {"reply_word": "p", "door": "Plan it", "entry": "/plan-work",
                          "why": "w", "reverses_if": "r"}
    one["others"] = [door for door in one["others"] if door["entry"] != "/plan-work"]
    rendered = handoff.completed(prepared)["decisions"][0]["recommended"]["check"]
    assert rendered["answer"] == "not checked", rendered
    stop = handoff.completed({**prepared, "report": prepared["report"].replace("-route", "-plan-work")})
    assert stop["decisions"][0]["recommended"]["check"]["answer"] == "refuses"


def test_a_routing_skeleton_refuses_a_slug_an_initiative_holds(project):
    done = route(project, "--slug", SLUG, "--ask", str(recorded_ask(project)))
    assert done.returncode == 1 and "a route opens a new initiative" in done.stdout


def test_a_routing_skeleton_refuses_a_request_not_recorded(project):
    done = route(project, "--slug", "loyalty-discount", "--ask", str(project / "nowhere.md"))
    assert done.returncode == 1 and "is no recorded ask" in done.stdout


@pytest.mark.parametrize("extra", [("--ask", "x.md"), ("--slug", "x"),
                                   ("--slug", "x", "--ask", "x.md", "--skill", "analyse")])
def test_a_routing_skeleton_cannot_run_without_its_inputs_or_beside_a_skill(project, extra):
    assert route(project, *extra).returncode == 2


def test_a_routing_record_never_checks_a_door_over_the_live_initiative(project):
    """«save in a routing record `--prepare --route` wrote (SPEC-011 R14), whose doors are never
    checked over an initiative it does not name» (SPEC-006 R9): with no slug left in the record,
    the `/plan-work` door goes unchecked rather than checked over the live one."""
    ask = recorded_ask(project)
    prepared = json.loads(route(project, "--slug", "loyalty-discount", "--ask", str(ask)).stdout)
    prepared["state_from"].pop("slug")
    one = prepared["decisions"][0]
    one["recommended"] = {"reply_word": "p", "door": "Plan it", "entry": "/plan-work",
                          "why": "w", "reverses_if": "r"}
    one["others"] = [door for door in one["others"] if door["entry"] != "/plan-work"]
    done = handoff.completed(prepared)
    check = done["decisions"][0]["recommended"]["check"]
    assert check["answer"] == "not checked" and "inferred_slug" not in check
    stop = handoff.completed({**prepared, "report": prepared["report"].replace("-route", "-plan-work")})
    assert stop["decisions"][0]["recommended"]["check"].get("inferred_slug") == SLUG


def test_a_status_over_an_initiative_the_grant_does_not_name_prepares_a_report(project):
    """«`--prepare --skill siegard-status` hands its doors only where such a grant stands»
    (SPEC-006 R11): a grant naming another initiative covers none of this one."""
    arm_grant(project)
    import grant
    path = grant.grant_path(project)
    held = json.loads(path.read_text(encoding="utf-8"))
    held["slug"] = "another-initiative"
    path.write_text(json.dumps(held), encoding="utf-8")
    prepared = prepare(project, "siegard-status", "--slug", SLUG)
    assert prepared["kind"] == "report" and "decisions" not in prepared


def test_prepare_and_render_read_one_initiative_under_a_goal(project):
    """`--prepare` and `--render` read the record's initiative from the same `state_from`: under a
    goal on the initiative the grant covers, a skeleton prepared naming another initiative still
    hands its doors, and the grant answers the other initiative's invocation with its stop."""
    arm_grant(project)
    import grant
    held = json.loads(grant.grant_path(project).read_text(encoding="utf-8"))
    held["slug"] = SLUG
    grant.grant_path(project).write_text(json.dumps(held), encoding="utf-8")
    arm(project)
    done = run("--prepare", "--skill", "plan-work", "--project", str(project), "--slug", "elsewhere")
    assert done.returncode == 0, done.stderr
    prepared = json.loads(done.stdout)
    assert prepared["state_from"] == {"script": "goal.py", "project": str(project)}
    assert prepared["kind"] == "decision"
    assert "limits: a grant covers this initiative" in done.stderr, done.stderr
    one = prepared["decisions"][0]
    one.update(ask="Deliver the next task?", if_none="Nothing runs.",
               invocation="/implement-task /x --target app --slug elsewhere")
    one["recommended"] = {"reply_word": "a", "door": "Deliver it", "entry": "/implement-task",
                          "why": "It is the one task ready", "reverses_if": "you want a review first",
                          "check": {"answer": "accepts", "refused": []}}
    one["others"] = []
    lines = handoff.grant_answer(prepared)
    assert f"decision 1: stop: the grant covers {SLUG}, not elsewhere" in lines, lines
