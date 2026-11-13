"""The grant is the person's words decided in advance, and a script answers what they let a stop do
(SPEC-011).

Each test builds a consumer repository under git, as `test_goal.py` does, arms a grant the way
`/siegard-grant` does, and asks `grant.py` as a session would. One test per bound the requirements
name, so a gate that stopped being held leaves its test red rather than every test green.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from conftest import derive_plan
from test_goal import (SLUG, VERSION, commit, deliver, git, measure, project,  # noqa: F401
                       review)

REPO = Path(__file__).resolve().parent.parent
BIN = REPO / "src/claude/bin"
WORDS = "autorizo as portas do plano e os commits da rota; feche a iniciativa quando tudo estiver entregue."


def grant(*args: str, stdin: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(BIN / "grant.py"), *args],
                          input=stdin, capture_output=True, text=True)


def arm(project: dict, *flags: str, words: str = WORDS, slug: str | None = SLUG):
    named = ["--slug", slug] if slug else []
    return grant("--arm", str(project["home"]), *named, *flags, "--words-file", "-", stdin=words)


def armed(project: dict) -> Path:
    return project["home"] / ".git" / "siegard" / "grant.json"


def record_of(project: dict) -> dict:
    return json.loads(armed(project).read_text(encoding="utf-8"))


def handoff(*decisions: dict) -> dict:
    return {"contract_version": "handoff/1", "kind": "decision", "decisions": list(decisions),
            "report": "/tmp/report.md"}


def door(word: str, entry: str, answer: str, refused: list[str] | None = None) -> dict:
    check = {"answer": answer}
    if refused:
        check["refused"] = refused
    return {"reply_word": word, "what_it_does": f"runs {entry}", "entry": entry, "check": check}


def decide(project: dict, record: dict, tmp_path: Path) -> subprocess.CompletedProcess:
    path = tmp_path / "record.json"
    path.write_text(json.dumps(record), encoding="utf-8")
    return grant("--decide", str(project["home"]), "--record", str(path))


def with_recommended(entry: str, answer: str, *others: dict) -> dict:
    recommended = {"door": f"runs {entry}", "why": "w", "reverses_if": "r", "reply_word": "a",
                   "entry": entry, "check": {"answer": answer}}
    return {"ask": "what next?", "recommended": recommended, "others": list(others),
            "if_none": "nothing runs"}


# ------------------------------------------------------------------------- arming (R1, R2)


def test_arming_records_the_words_verbatim_under_their_digest(project):
    result = arm(project, "--doors", "plan-work,implement-task", "--budget", "2", "--commits")
    assert result.returncode == 0, result.stdout + result.stderr
    held = record_of(project)
    assert held["contract"] == "grant-armed/1" and held["slug"] == SLUG
    assert held["doors"] == ["plan-work", "implement-task"] and held["budget"] == 2
    assert held["commits"] is True and held["close"] is False
    assert held["version"] == VERSION and held["since"] == project["since"]
    words = project["home"] / held["words"]["path"]
    assert words.read_text(encoding="utf-8") == WORDS
    assert held["words"]["sha256"] == hashlib.sha256(WORDS.encode()).hexdigest()[:16]


def test_a_second_arming_is_refused_while_one_stands(project):
    assert arm(project, "--commits").returncode == 0
    again = arm(project, "--doors", "plan-work")
    assert again.returncode == 1
    assert "a grant is armed already in this project" in again.stdout


@pytest.mark.parametrize("flags,expected", [
    (("--doors", "close-plan"), "close-plan is outside `doors`"),
    (("--doors", "plan-work,reconcile,commit"), "commit is outside `doors`"),
    (("--doors", "none"), "no clause is named"),
    (("--doors", "none", "--budget", "2", "--commits"), "a budget of judged doors needs `doors`"),
])
def test_arming_refuses_what_the_requirements_leave_out(project, flags, expected):
    result = arm(project, *flags)
    assert result.returncode == 1, result.stdout
    assert expected in result.stdout
    assert not armed(project).exists()


def test_arming_over_an_initiative_that_is_not_live_is_refused(project):
    result = arm(project, "--commits", slug="nowhere")
    assert result.returncode == 1 and "names no live initiative" in result.stdout
    closed = project["home"] / "plans" / SLUG / "closure.md"
    closed.write_text("closed\n", encoding="utf-8")
    result = arm(project, "--commits")
    assert result.returncode == 1 and f"{SLUG} is closed" in result.stdout


@pytest.mark.parametrize("flags", [("--close",), ("--commits",), ("--doors", "plan-work")])
def test_a_grant_without_words_is_refused_whatever_it_grants(project, flags):
    result = arm(project, *flags, words="   \n")
    assert result.returncode == 1 and "the words are empty" in result.stdout
    assert not armed(project).exists()


# ------------------------------------------------------------------------ what ends it (R3)


def test_a_plugin_version_change_ends_the_grant_and_it_takes_nothing(project):
    assert arm(project, "--commits").returncode == 0
    held = record_of(project)
    held["version"] = "0.0.1"
    armed(project).write_text(json.dumps(held), encoding="utf-8")
    result = grant("--commit", str(project["home"]), "--file", "telemetry/x.json")
    assert result.returncode == 1 and "the grant ended" in result.stdout
    assert not armed(project).exists()
    ended = (armed(project).parent / "grants-ended.jsonl").read_text(encoding="utf-8")
    assert json.loads(ended.splitlines()[-1])["ended"] == "ended"


def test_a_closure_ends_the_grant(project, tmp_path):
    assert arm(project, "--doors", "plan-work").returncode == 0
    (project["home"] / "plans" / SLUG / "closure.md").write_text("closed\n", encoding="utf-8")
    result = decide(project, handoff(with_recommended("/plan-work", "accepts")), tmp_path)
    assert result.returncode == 1 and "holds a closure.md" in result.stdout
    assert not armed(project).exists()


def test_disarming_ends_the_grant_and_reading_says_so(project):
    assert arm(project, "--commits").returncode == 0
    assert "disarmed" in grant("--disarm", str(project["home"])).stdout
    assert not armed(project).exists()
    assert "no grant is armed" in grant("--read", str(project["home"])).stdout


# ------------------------------------------------------------------- decisions (R4, R5)


def test_a_decision_the_person_reserved_is_a_stop(project, tmp_path):
    assert arm(project, "--doors", "plan-work", "--budget", "3").returncode == 0
    reserved = {"ask": "who is right?", "settles": "what a node says", "others": [
        door("a", "/plan-work", "accepts"), door("b", "/reconcile", "accepts")],
        "if_none": "stays"}
    out = decide(project, handoff(reserved), tmp_path).stdout
    assert "decision 1: stop: the choice is the person's" in out


def test_the_one_door_left_after_a_refusal_is_taken_as_precondition_unmet(project, tmp_path):
    assert arm(project, "--doors", "implement-task,review-change").returncode == 0
    decision = with_recommended("/review-change", "accepts",
                                door("b", "/implement-task", "refuses",
                                     ["refused: the task waits on a dependency"]))
    out = decide(project, handoff(decision), tmp_path).stdout
    digest = record_of(project)["words"]["sha256"]
    lines = out.splitlines()
    assert "decision 1: take: a /review-change" in lines
    assert ("  decided: /review-change — precondition unmet — the other door was refused by its "
            f"own check: refused: the task waits on a dependency (grant sha256 {digest})") in lines


@pytest.mark.parametrize("entry,answer,why", [
    ("/analyse", "accepts", "not in the grant's doors"),
    ("/review-change", "not checked", "was not checked by `door.py --check`"),
])
def test_the_one_door_left_is_not_taken_outside_the_list_or_unchecked(project, tmp_path, entry,
                                                                      answer, why):
    assert arm(project, "--doors", "review-change").returncode == 0
    decision = with_recommended(entry, answer, door("b", "/plan-work", "refuses"))
    out = decide(project, handoff(decision), tmp_path).stdout
    assert "stop:" in out and why in out and "take:" not in out


def test_every_door_excluded_is_a_stop(project, tmp_path):
    assert arm(project, "--doors", "plan-work").returncode == 0
    decision = with_recommended("/plan-work", "refuses", door("b", "/reconcile", "refuses"))
    out = decide(project, handoff(decision), tmp_path).stdout
    assert "stop: every door the handoff hands is excluded" in out


def test_an_accepted_recommended_door_beside_an_open_one_is_judged_within_the_budget(project,
                                                                                    tmp_path):
    assert arm(project, "--doors", "plan-work", "--budget", "2").returncode == 0
    decision = with_recommended("/plan-work", "accepts", door("b", "/reconcile", "accepts"))
    out = decide(project, handoff(decision), tmp_path).stdout
    assert "decision 1: judge: spawn the door decider over these doors, budget left 2" in out
    assert "door a: /plan-work" in out and "door b: /reconcile" in out
    assert "report: /tmp/report.md" in out


def test_a_judged_choice_met_with_the_budget_spent_is_a_stop(project, tmp_path):
    assert arm(project, "--doors", "plan-work", "--budget", "1").returncode == 0
    log = project["home"] / "deliveries" / SLUG / "orchestration.md"
    log.parent.mkdir(parents=True, exist_ok=True)
    digest = record_of(project)["words"]["sha256"]
    log.write_text(f"decided: /plan-work — keeps the route — the step the framework prescribes "
                   f"(grant sha256 {digest})\n", encoding="utf-8")
    commit(project["home"], f"deliver-scope {SLUG}: log", "deliveries")
    decision = with_recommended("/plan-work", "accepts", door("b", "/reconcile", "accepts"))
    out = decide(project, handoff(decision), tmp_path).stdout
    assert "stop: the grant's budget of judged doors is spent" in out


def test_a_recommended_door_outside_the_list_is_a_stop(project, tmp_path):
    assert arm(project, "--doors", "plan-work", "--budget", "1").returncode == 0
    decision = with_recommended("/review-change", "accepts", door("b", "/plan-work", "accepts"))
    out = decide(project, handoff(decision), tmp_path).stdout
    assert "stop: no recommended door is in the grant's doors" in out


# ------------------------------------------------------------------- commit gate (R7, R8)


def commit_check(project: dict, *files: str) -> subprocess.CompletedProcess:
    args: list[str] = []
    for name in files:
        args += ["--file", name]
    return grant("--commit", str(project["home"]), *args)


def test_a_commit_of_paths_the_route_writes_is_accepted(project):
    deliver(project)
    assert arm(project, "--commits").returncode == 0
    result = commit_check(project, f"deliveries/{SLUG}/implementation/checkout/record-order.md",
                          "target/src/orders/place.ts", "telemetry/report.json")
    assert result.stdout.splitlines()[0] == "accepts", result.stdout
    assert result.returncode == 0
    assert "checked: 3 path(s)" in result.stdout


@pytest.mark.parametrize("name,why", [
    ("siegard.json", "the project file or a standard it declares"),
    ("CLAUDE.md", "CLAUDE.md, which only the person changes"),
    ("telemetry/.env", "names a file that holds credentials"),
    ("telemetry/id_rsa", "names a file that holds credentials"),
    ("../outside.txt", "is outside the project"),
    ("target/src/other.ts", "is no path the route writes"),
    (f"plans/{SLUG}/closure.md", "closes the initiative, and the grant holds no `close` clause"),
])
def test_a_commit_naming_a_bound_path_is_refused(project, name, why):
    deliver(project)
    assert arm(project, "--commits").returncode == 0
    result = commit_check(project, name)
    assert result.stdout.splitlines()[0] == "refuses", result.stdout
    assert why in result.stdout and result.returncode == 1


def test_a_commit_that_modifies_a_specification_file_head_holds_is_refused(project):
    deliver(project)
    assert arm(project, "--commits").returncode == 0
    held = next(path for path in (project["home"] / "specification").rglob("*.md")
                if not path.name.endswith(".log.md"))
    result = commit_check(project, held.relative_to(project["home"]).as_posix())
    assert result.stdout.splitlines()[0] == "refuses", result.stdout
    assert "a specification file HEAD already holds" in result.stdout


def test_a_commit_without_the_commits_clause_or_a_path_is_refused(project):
    deliver(project)
    assert arm(project, "--doors", "plan-work").returncode == 0
    result = commit_check(project, "telemetry/report.json")
    assert "the grant holds no `commits` clause" in result.stdout
    assert arm(project, "--commits").returncode == 1
    grant("--disarm", str(project["home"]))
    assert arm(project, "--commits").returncode == 0
    assert "no path is named" in commit_check(project).stdout


# ---------------------------------------------------------------------- close gate (R7)


def test_closing_needs_the_close_clause(project):
    assert arm(project, "--commits").returncode == 0
    out = grant("--close", str(project["home"]))
    assert out.stdout.splitlines()[0] == "refuses" and "holds no `close` clause" in out.stdout


def test_closing_is_refused_while_the_initiative_is_not_delivered_and_reviewed(project):
    assert arm(project, "--close").returncode == 0
    out = grant("--close", str(project["home"]))
    assert out.returncode == 1 and out.stdout.splitlines()[0] == "refuses"
    assert "refused: records" in out.stdout


def one_task_plan(project: dict) -> None:
    home = project["home"]
    work = home / "plans" / SLUG
    (work / "task/checkout/bill-order.md").unlink()
    epic = work / "epic/checkout.md"
    _, front, body = epic.read_text(encoding="utf-8").split("---\n", 2)
    data = yaml.safe_load(front)
    data["covers"] = ["domain/sales/order"]
    epic.write_text("---\n" + yaml.safe_dump(data, sort_keys=False) + "---\n" + body,
                    encoding="utf-8")
    derive_plan(work, home / "specification")
    project["since"] = commit(home, "the plan, one task")


def test_closing_is_refused_naming_the_task_still_undelivered(project):
    assert arm(project, "--close").returncode == 0
    deliver(project)
    review(project)
    measure(project)
    out = grant("--close", str(project["home"]))
    assert out.stdout.splitlines()[0] == "refuses", out.stdout
    assert "checkout/bill-order" in out.stdout


def test_closing_is_accepted_where_everything_is_delivered_proven_and_reviewed(project):
    one_task_plan(project)
    assert arm(project, "--close").returncode == 0
    deliver(project)
    review(project)
    measure(project)
    out = grant("--close", str(project["home"]))
    assert out.stdout.splitlines()[0] == "accepts", out.stdout
    assert out.returncode == 0
    for name in ("records", "review", "criteria", "delivery", "plan", "specification"):
        assert f"checked: {name}" in out.stdout


# ------------------------------------------------------------- adversarial paths (R7, R8)


@pytest.mark.parametrize("name", ["telemetry/../siegard.json", "./CLAUDE.md",
                                  f"deliveries/{SLUG}/../../siegard.json",
                                  "specification/../CLAUDE.md"])
def test_a_path_spelled_around_a_bound_is_refused_by_what_it_resolves_to(project, name):
    deliver(project)
    assert arm(project, "--commits").returncode == 0
    result = commit_check(project, name)
    assert result.stdout.splitlines()[0] == "refuses", result.stdout


def test_a_new_specification_file_no_record_names_is_refused_and_a_decision_log_is_not(project):
    deliver(project)
    assert arm(project, "--commits").returncode == 0
    fresh = commit_check(project, "specification/a-new-node.md")
    assert fresh.stdout.splitlines()[0] == "refuses" and "no path the route writes" in fresh.stdout
    held = next(path for path in (project["home"] / "specification").rglob("*.md")
                if not path.name.endswith(".log.md"))
    sidecar = held.with_name(held.stem + ".log.md").relative_to(project["home"]).as_posix()
    assert commit_check(project, sidecar).stdout.splitlines()[0] == "accepts"
    orphan = held.with_name("never-held.log.md").relative_to(project["home"]).as_posix()
    assert commit_check(project, orphan).stdout.splitlines()[0] == "refuses"


def test_one_refused_path_among_owned_ones_refuses_the_whole_commit(project):
    deliver(project)
    assert arm(project, "--commits").returncode == 0
    out = commit_check(project, "telemetry/report.json", "siegard.json")
    assert out.stdout.splitlines()[0] == "refuses" and "refused: siegard.json" in out.stdout
    assert "refused: telemetry/report.json" not in out.stdout


# ------------------------------------------------------------ the skill and the rule (R1)


def test_the_skill_is_closed_to_the_model_and_arms_only_through_the_script():
    """«A grant is armed only by the person's own invocation of `/siegard-grant`, a skill closed
    to the model, whose arguments are the person's words.» (SPEC-011 R1)"""
    import yaml
    text = (REPO / "src/claude/skills/siegard-grant/SKILL.md").read_text(encoding="utf-8")
    front = yaml.safe_load(text.split("---\n", 2)[1])
    assert front["disable-model-invocation"] is True
    assert "grant.py --arm" in text and "--words-file -" in text
    assert "Arm a grant but under an invocation of this skill" in " ".join(text.split())


def test_the_session_rules_send_a_stop_to_the_script_and_never_arm():
    rules = " ".join((REPO / "src/claude/hooks/rules.md").read_text(encoding="utf-8").split())
    assert "a stop's doors go to the script first" in rules
    for line in ("`bin/grant.py --decide <project-root> --record <record>`",
                 "`grant.py --commit <project-root> --file <path>...`",
                 "`grant.py --close <project-root>`",
                 "Never run `grant.py --arm` outside `/siegard-grant`"):
        assert line in rules
    others = [path for path in (REPO / "src/claude/skills").rglob("*.md")
              if path.parent.name != "siegard-grant" and "grant.py --arm" in path.read_text(
                  encoding="utf-8")]
    assert others == []


def test_a_record_handoff_prepare_wrote_is_read_by_decide_without_a_crash(project, tmp_path):
    deliver(project)
    assert arm(project, "--doors", "plan-work,implement-task,review-change,reconcile",
               "--budget", "2").returncode == 0
    prepared = subprocess.run(
        [sys.executable, "-B", str(BIN / "handoff.py"), "--prepare", "--skill", "implement-task",
         "--project", str(project["home"]), "--slug", SLUG, "--target", "app", "--language", "en"],
        capture_output=True, text=True)
    assert prepared.returncode == 0, prepared.stdout + prepared.stderr
    record = json.loads(prepared.stdout)
    out = decide(project, record, tmp_path)
    assert out.returncode == 0, out.stdout + out.stderr
    assert out.stdout.splitlines()[0].startswith("grant: ")
    assert "decision 1:" in out.stdout


# ------------------------------------------------- the project, until cleared (R1, R2, R3, R7)


def test_a_grant_without_a_slug_covers_every_live_initiative(project):
    result = arm(project, "--commits", slug=None)
    assert result.returncode == 0, result.stdout + result.stderr
    assert record_of(project)["slug"] is None


def test_a_grant_that_names_no_door_holds_all_six_and_none_holds_none(project):
    """«which is all six where the person names none» (SPEC-011 R2)"""
    assert arm(project, "--commits", slug=None).returncode == 0
    assert record_of(project)["doors"] == ["plan-work", "implement-task", "review-change",
                                           "reconcile", "deliver-scope", "analyse"]
    assert record_of(project)["budget"] == 0
    grant("--disarm", str(project["home"]))
    assert arm(project, "--commits", "--doors", "none", slug=None).returncode == 0
    assert record_of(project)["doors"] == []


def test_analyse_is_a_door_by_default_and_not_where_the_doors_are_narrowed(project, tmp_path):
    decision = with_recommended("/analyse", "accepts", door("b", "/plan-work", "refuses"))
    assert arm(project, "--budget", "1", slug=None).returncode == 0
    taken = decide(project, handoff(decision), tmp_path).stdout
    assert "decision 1: take: a /analyse" in taken
    assert "  decided: /analyse — precondition unmet" in taken
    grant("--disarm", str(project["home"]))
    assert arm(project, "--doors", "plan-work,implement-task", slug=None).returncode == 0
    assert "is not in the grant's doors" in decide(project, handoff(decision), tmp_path).stdout


def test_arming_prints_what_it_recorded_for_the_report_to_quote(project):
    out = arm(project, "--budget", "2", "--commits").stdout.splitlines()
    assert out[0].startswith("armed: ") and out[1].startswith("words: ")
    assert f"covers: {SLUG}" in out
    assert "doors: plan-work, implement-task, review-change, reconcile, deliver-scope, analyse" in out
    assert "budget of judged doors: 2" in out and "commits: yes" in out and "close: no" in out
    assert any(line.startswith("plugin: ") for line in out)


def test_a_target_taken_where_the_project_declares_several_is_said(project):
    declared = json.loads((project["home"] / "siegard.json").read_text(encoding="utf-8"))
    declared["targets"] = {"app": "target", "other": "target"}
    (project["home"] / "siegard.json").write_text(json.dumps(declared), encoding="utf-8")
    commit(project["home"], "a second target")
    out = arm(project, "--commits").stdout.splitlines()
    assert out[0] == ("target: app — decided: the first of app, other; a record's own target is "
                      "read where it names one")


def test_clearing_where_no_grant_is_armed_says_so_and_refuses_nothing(project):
    out = grant("--disarm", str(project["home"]))
    assert out.returncode == 0 and out.stdout.strip() == "no grant is armed in this project"


def test_disarming_a_project_grant_returns_the_project_to_no_grant(project, tmp_path):
    assert arm(project, "--doors", "plan-work", slug=None).returncode == 0
    assert "disarmed: every live initiative" in grant("--disarm", str(project["home"])).stdout
    assert not armed(project).exists()
    out = decide(project, handoff(with_recommended("/plan-work", "accepts")), tmp_path)
    assert out.returncode == 2 and "no grant is armed" in out.stderr


def test_a_closure_ends_a_grant_that_names_the_initiative_and_not_one_that_names_none(project):
    assert arm(project, "--commits", slug=None).returncode == 0
    (project["home"] / "plans" / SLUG / "closure.md").write_text("closed\n", encoding="utf-8")
    assert grant("--read", str(project["home"])).stdout.startswith("{")
    assert armed(project).exists()


def test_a_project_grant_commits_the_paths_of_any_live_initiative(project):
    deliver(project)
    assert arm(project, "--commits", slug=None).returncode == 0
    result = commit_check(project, f"deliveries/{SLUG}/implementation/checkout/record-order.md",
                          "target/src/orders/place.ts")
    assert result.stdout.splitlines()[0] == "accepts", result.stdout
    assert "every live initiative" in result.stdout
    refused = commit_check(project, "siegard.json")
    assert refused.stdout.splitlines()[0] == "refuses"


def test_a_project_grant_closes_only_the_initiative_it_is_asked_about(project):
    one_task_plan(project)
    assert arm(project, "--close", slug=None).returncode == 0
    deliver(project)
    review(project)
    measure(project)
    bare = grant("--close", str(project["home"]))
    assert bare.stdout.splitlines()[0] == "refuses" and "takes --slug" in bare.stdout
    other = grant("--close", str(project["home"]), "--slug", "elsewhere")
    assert "no live initiative the grant covers" in other.stdout
    done = grant("--close", str(project["home"]), "--slug", SLUG)
    assert done.stdout.splitlines()[0] == "accepts", done.stdout


def test_the_budget_of_a_project_grant_counts_the_judged_doors_of_every_log(project, tmp_path):
    assert arm(project, "--doors", "plan-work", "--budget", "1", slug=None).returncode == 0
    log = project["home"] / "deliveries" / SLUG / "orchestration.md"
    log.parent.mkdir(parents=True, exist_ok=True)
    digest = record_of(project)["words"]["sha256"]
    log.write_text(f"decided: /plan-work — keeps the route — the prescribed step (grant sha256 "
                   f"{digest})\n", encoding="utf-8")
    commit(project["home"], f"deliver-scope {SLUG}: log", "deliveries")
    decision = with_recommended("/plan-work", "accepts", door("b", "/reconcile", "accepts"))
    assert "the grant's budget of judged doors is spent" in decide(
        project, handoff(decision), tmp_path).stdout


def test_the_skill_states_the_defaults_the_script_applies_and_clears_through_the_script():
    text = " ".join((REPO / "src/claude/skills/siegard-grant/SKILL.md").read_text(
        encoding="utf-8").split())
    assert "all six, `analyse` among them" in text
    assert "zero: a choice between open doors stops until the person writes one" in text
    assert "Run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/grant.py --disarm <project-root>`" in text
    assert "With no grant armed it says so, and that is the report" in text
    assert "the grant covers every live initiative of the project" in text
    assert "The grant without words is no grant: ask for them and run nothing" in text
    assert "pick another where `WORDS` is one of their lines" in text
    assert "the script takes the first key `siegard.json` declares and says so" in text


def test_a_deliver_scope_handoff_record_is_read_by_decide_under_a_project_grant(project, tmp_path):
    deliver(project)
    assert arm(project, "--doors", "deliver-scope,plan-work,implement-task,review-change",
               "--budget", "2", slug=None).returncode == 0
    prepared = subprocess.run(
        [sys.executable, "-B", str(BIN / "handoff.py"), "--prepare", "--skill", "deliver-scope",
         "--project", str(project["home"]), "--slug", SLUG, "--target", "app", "--language", "en"],
        capture_output=True, text=True)
    assert prepared.returncode == 0, prepared.stdout + prepared.stderr
    out = decide(project, json.loads(prepared.stdout), tmp_path)
    assert out.returncode == 0 and out.stdout.splitlines()[0].startswith("grant: every live")


# --------------------------------------------------- where a run meets it (R9, R10)


def test_a_judged_line_the_goal_took_does_not_spend_the_grants_budget(project, tmp_path):
    assert arm(project, "--doors", "plan-work", "--budget", "1").returncode == 0
    log = project["home"] / "deliveries" / SLUG / "orchestration.md"
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text("decided: /plan-work — keeps the route — a goal's door, no grant's\n",
                   encoding="utf-8")
    commit(project["home"], f"deliver-scope {SLUG}: log", "deliveries")
    decision = with_recommended("/plan-work", "accepts", door("b", "/reconcile", "accepts"))
    assert "budget left 1" in decide(project, handoff(decision), tmp_path).stdout


def test_a_judge_answer_names_the_suffix_its_decided_line_ends_with(project, tmp_path):
    assert arm(project, "--doors", "plan-work", "--budget", "1").returncode == 0
    digest = record_of(project)["words"]["sha256"]
    decision = with_recommended("/plan-work", "accepts", door("b", "/reconcile", "accepts"))
    out = decide(project, handoff(decision), tmp_path).stdout
    assert f"end the deciding fact of the `decided:` line with `(grant sha256 {digest})`" in out


def kept(project: dict, skill: str, stamp: str, record: dict, age: int = 0) -> Path:
    base = project["home"] / ".git" / "siegard" / "handoff"
    base.mkdir(parents=True, exist_ok=True)
    path = base / f"{stamp}-{skill}.json"
    path.write_text(json.dumps(record), encoding="utf-8")
    if age:
        import os
        moved = path.stat().st_mtime - age
        os.utime(path, (moved, moved))
    return path


def test_latest_answers_over_the_newest_record_kept_for_the_skill_after_the_commit(project):
    assert arm(project, "--doors", "plan-work,reconcile", "--budget", "1").returncode == 0
    marker = commit(project["home"], "the log before the invocation")
    reserved = {"ask": "who is right?", "settles": "what a node says", "others": [
        door("a", "/plan-work", "accepts")], "if_none": "stays"}
    kept(project, "implement-task", "20261113T100000Z", handoff(reserved))
    kept(project, "implement-task", "20261113T110000Z",
         handoff(with_recommended("/reconcile", "accepts", door("b", "/plan-work", "refuses"))))
    kept(project, "review-change", "20261113T120000Z", handoff(reserved))
    out = grant("--decide", str(project["home"]), "--latest", "implement-task", "--after",
                marker).stdout
    assert "decision 1: take: a /reconcile" in out
    other = grant("--decide", str(project["home"]), "--latest", "review-change", "--after",
                  marker).stdout
    assert "stop: the choice is the person's" in other


def test_a_record_an_earlier_stop_left_is_never_answered_over(project):
    """«so that a run never answers over the report of an earlier stop» (SPEC-011 R9)"""
    assert arm(project, "--doors", "plan-work,reconcile", "--budget", "1").returncode == 0
    kept(project, "implement-task", "20261113T090000Z",
         handoff(with_recommended("/reconcile", "accepts", door("b", "/plan-work", "refuses"))),
         age=3600)
    import time
    time.sleep(1.1)
    marker = commit(project["home"], "the log before the invocation")
    out = grant("--decide", str(project["home"]), "--latest", "implement-task", "--after", marker)
    assert out.returncode == 2 and "was kept under" in out.stderr and "after" in out.stderr


def test_latest_needs_a_skill_a_commit_and_a_commit_that_exists(project):
    assert arm(project, "--doors", "plan-work").returncode == 0
    bare = grant("--decide", str(project["home"]), "--latest", "implement-task")
    assert bare.returncode == 2 and "with --after <commit>" in bare.stderr
    both = grant("--decide", str(project["home"]), "--latest", "x", "--after", "y", "--record", "z")
    assert both.returncode == 2 and "--record <file>, or --latest" in both.stderr
    nowhere = grant("--decide", str(project["home"]), "--latest", "implement-task", "--after",
                    "0000000")
    assert nowhere.returncode == 2 and "--after names no commit" in nowhere.stderr


def test_a_stop_a_grant_cannot_answer_stays_the_stop_it_was_under_a_goal_too(project, tmp_path):
    """«a `stop` leaves the stop as it was» (SPEC-011 R10): a decision the person reserved, a door
    outside the list and an unchecked door are each `stop`, so a run reading them ends as before."""
    assert arm(project, "--doors", "plan-work").returncode == 0
    reserved = {"ask": "who is right?", "settles": "what a node says",
                "others": [door("a", "/plan-work", "accepts")], "if_none": "stays"}
    outside = with_recommended("/review-change", "accepts", door("b", "/plan-work", "refuses"))
    unchecked = with_recommended("/plan-work", "not checked", door("b", "/reconcile", "refuses"))
    out = decide(project, handoff(reserved, outside, unchecked), tmp_path).stdout
    assert out.count("stop:") == 3 and "take:" not in out and "judge:" not in out


def test_deliver_scope_asks_the_grant_where_it_answers_a_stop_and_binds_the_same_task_rule():
    """«The same door over the same task is taken once in a run.» (SPEC-011 R10)"""
    doors = " ".join((REPO / "src/claude/skills/deliver-scope/references/doors.md").read_text(
        encoding="utf-8").split())
    goal_ref = " ".join((REPO / "src/claude/skills/deliver-scope/references/goal.md").read_text(
        encoding="utf-8").split())
    assert ("With a grant armed, run `bin/grant.py --decide <project-root> --latest <the "
            "stopping skill> --after <the log commit before it ran>` first: `take:` prints a "
            "derived door's `decided:` line, `judge:` a judged door, `stop:` or no answer leaves "
            "the stop; the same-task rule binds them.") in doors
    assert "no `decided:` line of this run took over the same task" in doors
    assert "A grant's `judge:` brings its own budget; its line ends `(grant sha256 …)`, no goal's." \
        in goal_ref
