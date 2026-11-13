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
    ((), "no clause is named"),
    (("--budget", "2", "--commits"), "a budget of judged doors needs `doors`"),
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


def test_close_is_the_persons_reason_and_empty_words_are_refused(project):
    result = arm(project, "--close", words="   \n")
    assert result.returncode == 1 and "the words are empty" in result.stdout


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
    assert ("decision 1: take: a /review-change — precondition unmet — refused: the task waits "
            f"on a dependency (grant sha256 {digest})") in out


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
    log.write_text("decided: /plan-work — keeps the route — the step the framework prescribes\n",
                   encoding="utf-8")
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


def test_analyse_is_a_door_only_where_the_person_writes_it(project, tmp_path):
    assert arm(project, "--doors", "plan-work", slug=None).returncode == 0
    decision = with_recommended("/analyse", "accepts", door("b", "/plan-work", "refuses"))
    assert "is not in the grant's doors" in decide(project, handoff(decision), tmp_path).stdout
    grant("--disarm", str(project["home"]))
    assert arm(project, "--doors", "plan-work,analyse", slug=None).returncode == 0
    taken = decide(project, handoff(decision), tmp_path).stdout
    assert "take: a /analyse — precondition unmet" in taken


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
    log.write_text("decided: /plan-work — keeps the route — the prescribed step\n", encoding="utf-8")
    commit(project["home"], f"deliver-scope {SLUG}: log", "deliveries")
    decision = with_recommended("/plan-work", "accepts", door("b", "/reconcile", "accepts"))
    assert "the grant's budget of judged doors is spent" in decide(
        project, handoff(decision), tmp_path).stdout


def test_the_skill_clears_a_grant_through_the_script_and_arms_nothing_then():
    text = " ".join((REPO / "src/claude/skills/siegard-grant/SKILL.md").read_text(
        encoding="utf-8").split())
    assert "Where the arguments hold `--clear`, nothing is armed" in text
    assert "grant.py --disarm <project-root>" in text
    assert "none: the grant covers every live initiative of the project" in text
    assert "`analyse` only where the person writes it" in text


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
