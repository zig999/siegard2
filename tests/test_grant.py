"""The grant is the person's words decided in advance, and a script answers what they let a stop do
(SPEC-011).

Each test builds a consumer repository under git, as `test_goal.py` does, arms a grant the way
`/siegard-grant` does, and asks `grant.py` as a session would. One test per bound the requirements
name, so a gate that stopped being held leaves its test red rather than every test green.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

import goal
from conftest import derive_plan
from test_goal import (SLUG, VERSION, commit, deliver, git, measure, project,  # noqa: F401
                       review)

REPO = Path(__file__).resolve().parent.parent
BIN = REPO / "src/claude/bin"
WORDS = "autorizo as portas do plano e os commits da rota; feche a iniciativa quando tudo estiver entregue."


def grant(*args: str, stdin: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(BIN / "grant.py"), *args],
                          input=stdin, capture_output=True, text=True)


def next_free_second(home: Path) -> None:
    """An ask is recorded once per second and never overwritten, so a test arming twice waits
    out a second whose ask is already recorded rather than meet that refusal."""
    sys.path.insert(0, str(BIN))
    import ask
    try:
        root = ask.telemetry_root(home)
    except Exception:
        return
    while (root / f"ask-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.md").exists():
        time.sleep(0.05)


def arm(project: dict, *flags: str, words: str = WORDS, slug: str | None = SLUG):
    named = ["--slug", slug] if slug else []
    next_free_second(project["home"])
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


def decide(project: dict, record: dict, tmp_path: Path,
           slug: str | None = None) -> subprocess.CompletedProcess:
    path = tmp_path / "record.json"
    path.write_text(json.dumps(record), encoding="utf-8")
    named = ["--slug", slug] if slug else []
    return grant("--decide", str(project["home"]), "--record", str(path), *named)


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


def ended_grants(project: dict) -> list[dict]:
    log = armed(project).parent / "grants-ended.jsonl"
    if not log.is_file():
        return []
    return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]


def test_arming_over_a_grant_armed_under_another_version_replaces_a_grant_that_stands(project):
    """«A change of the plugin's version ends no grant» (SPEC-011 R3): a grant armed under
    another version still stands, so arming over it replaces it."""
    assert arm(project, "--commits").returncode == 0
    old = record_of(project)
    armed(project).write_text(json.dumps({**old, "version": "0.0.1"}), encoding="utf-8")
    again = arm(project, "--doors", "plan-work")
    assert again.returncode == 0, again.stdout + again.stderr
    assert f"ended: the grant armed at {old['armed_at']} is replaced by this arming" in again.stdout
    assert record_of(project)["doors"] == ["plan-work"]
    [gone] = ended_grants(project)
    assert gone["ended"] == "replaced" and gone["version"] == "0.0.1"


def test_arming_over_a_grant_that_stands_replaces_it_and_says_what_it_held(project):
    """«An arming over a grant that still stands ends it in that log as `replaced`, says what it
    held» (SPEC-011 R3): no `--clear` first, the old grant kept in the ended log, the new one its own."""
    assert arm(project, "--commits", "--budget", "3").returncode == 0
    old = record_of(project)
    again = arm(project, "--doors", "plan-work", slug=None)
    assert again.returncode == 0, again.stdout + again.stderr
    assert f"ended: the grant armed at {old['armed_at']} is replaced by this arming — it covered " \
           f"{SLUG}" in again.stdout
    assert f"mark (grant sha256 {old['mark']})" in again.stdout and "budget 3, commits yes" in again.stdout
    new = record_of(project)
    assert new["doors"] == ["plan-work"] and new["slug"] is None and new["commits"] is False
    assert new["mark"] != old["mark"] and new["budget"] == 0
    [gone] = ended_grants(project)
    assert gone["ended"] == "replaced" and gone["reason"] == "replaced by a new arming"
    assert gone["mark"] == old["mark"] and gone["commits"] is True


def test_the_replacing_grant_budget_counts_only_its_own_mark(project):
    assert arm(project, "--budget", "1").returncode == 0
    first = record_of(project)["mark"]
    assert arm(project, "--budget", "2").returncode == 0
    held = record_of(project)
    assert held["mark"] != first and held["budget"] == 2


def test_a_refused_arming_leaves_a_standing_grant_in_place(project):
    assert arm(project, "--commits").returncode == 0
    old = record_of(project)
    refused = arm(project, "--doors", "close-plan")
    assert refused.returncode == 1 and "close-plan is outside" in refused.stdout
    nothing = arm(project, "--doors", "none")
    assert nothing.returncode == 1 and "no clause is named" in nothing.stdout
    assert record_of(project) == old and ended_grants(project) == []


def close_committed(project: dict) -> None:
    (project["home"] / "plans" / SLUG / "closure.md").write_text("closed\n", encoding="utf-8")
    commit(project["home"], "the closure", f"plans/{SLUG}/closure.md")


def test_arming_over_a_grant_whose_initiative_closed_ends_it_and_arms(project):
    assert arm(project, "--commits").returncode == 0
    close_committed(project)
    next_free_second(project["home"])
    words_only = grant("--arm", str(project["home"]), "--commits", "--words-file", "-",
                       stdin=WORDS)
    assert words_only.returncode == 0, words_only.stdout + words_only.stderr
    assert "holds a closure.md" in words_only.stdout
    assert [g["ended"] for g in ended_grants(project)] == ["ended"]


def test_a_refused_arming_leaves_a_grant_of_another_version_in_place(project):
    """Nothing is written on a refusal: the old record is moved only where the new one is armed."""
    assert arm(project, "--commits").returncode == 0
    old = {**record_of(project), "version": "0.0.1"}
    armed(project).write_text(json.dumps(old), encoding="utf-8")
    refused = arm(project, "--doors", "close-plan")
    assert refused.returncode == 1 and "close-plan is outside" in refused.stdout
    assert record_of(project) == old and ended_grants(project) == []


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
def test_an_invocation_recorded_empty_is_refused_whatever_flags_reach_the_script(project, flags):
    result = arm(project, *flags, words="   \n")
    assert result.returncode == 1 and "the invocation names nothing" in result.stdout
    assert not armed(project).exists()


# --------------------------------------- the invocation as the words, and the mark (R1, R10)

INVOCATION = "--budget 5 --commits --close\n"


def ask_files(project: dict) -> list[Path]:
    return sorted((project["home"] / "telemetry").glob("ask-*.md"))


def test_an_invocation_of_flags_alone_arms_and_is_recorded_as_typed(project):
    """«A grant is armed only by the person's own invocation of `/siegard-grant`, a skill closed
    to the model, whose arguments are the person's words.» (SPEC-011 R1)"""
    result = arm(project, "--budget", "5", "--commits", "--close", words=INVOCATION)
    assert result.returncode == 0, result.stdout + result.stderr
    held = record_of(project)
    assert (project["home"] / held["words"]["path"]).read_text(encoding="utf-8") == INVOCATION
    assert held["words"]["sha256"] == hashlib.sha256(INVOCATION.encode()).hexdigest()[:16]
    assert held["budget"] == 5 and held["commits"] is True and held["close"] is True


def test_an_invocation_that_names_nothing_arms_nothing_and_records_nothing(project):
    before = ask_files(project)
    result = arm(project, words="")
    assert result.returncode == 1
    assert "the invocation names nothing" in result.stdout
    assert "at least one of --doors, --budget, --commits or --close" in result.stdout
    assert not armed(project).exists() and ask_files(project) == before


def test_the_mark_is_the_words_digest_taken_with_the_instant_armed(project):
    assert arm(project, "--commits", words=INVOCATION).returncode == 0
    held = record_of(project)
    expected = hashlib.sha256(f"{held['words']['sha256']} {held['armed_at']}".encode()).hexdigest()
    assert held["mark"] == expected[:16] and held["mark"] != held["words"]["sha256"]
    printed = arm(project, "--commits", words=INVOCATION)
    assert printed.returncode == 0 and "replaced by this arming" in printed.stdout


def test_two_grants_armed_with_the_same_invocation_never_share_a_mark(project):
    first = arm(project, "--commits", words=INVOCATION)
    assert first.returncode == 0 and f"mark: (grant sha256 {record_of(project)['mark']})" in first.stdout
    one = record_of(project)
    assert "disarmed" in grant("--disarm", str(project["home"])).stdout
    import time
    time.sleep(1.1)
    assert arm(project, "--commits", words=INVOCATION).returncode == 0
    two = record_of(project)
    assert one["words"]["sha256"] == two["words"]["sha256"]
    assert one["mark"] != two["mark"]


def test_the_budget_counts_only_the_lines_its_own_mark_ends(project, tmp_path):
    """A judged line an earlier grant of the same invocation took, ending with that grant's mark
    or with the words' digest alone, is no line this grant took."""
    assert arm(project, "--doors", "plan-work", "--budget", "1", words=INVOCATION).returncode == 0
    held = record_of(project)
    log = project["home"] / "deliveries" / SLUG / "orchestration.md"
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(f"decided: /plan-work — keeps the route — the prescribed step (grant sha256 "
                   f"{held['words']['sha256']})\n", encoding="utf-8")
    commit(project["home"], f"deliver-scope {SLUG}: log", "deliveries")
    decision = with_recommended("/plan-work", "accepts", door("b", "/reconcile", "accepts"))
    assert "budget left 1" in decide(project, handoff(decision), tmp_path).stdout
    log.write_text(log.read_text(encoding="utf-8") + f"decided: /plan-work — keeps the route — "
                   f"the prescribed step (grant sha256 {held['mark']})\n", encoding="utf-8")
    commit(project["home"], f"deliver-scope {SLUG}: log", "deliveries")
    assert f"budget of judged doors for {SLUG} is spent" in decide(
        project, handoff(decision), tmp_path).stdout


def test_a_grant_recorded_before_the_mark_is_told_apart_by_its_words(project, tmp_path):
    assert arm(project, "--doors", "plan-work", "--budget", "1").returncode == 0
    held = record_of(project)
    held.pop("mark")
    armed(project).write_text(json.dumps(held), encoding="utf-8")
    decision = with_recommended("/plan-work", "accepts", door("b", "/reconcile", "accepts"))
    out = decide(project, handoff(decision), tmp_path).stdout
    assert f"(grant sha256 {held['words']['sha256']})" in out


def test_the_skill_records_the_invocation_as_typed_and_reads_on_no_argument():
    text = " ".join((REPO / "src/claude/skills/siegard-grant/SKILL.md").read_text("utf-8").split())
    assert "**The words the script records are the invocation's arguments as typed**" in text
    assert "never rebuilt from the flags the table read" in text
    assert "| **No argument** | the invocation holds nothing at all |" in text
    assert "bin/grant.py --read <project-root>` over the root `--here` resolves" in text
    assert "Never run `--arm` for it" in text
    assert "- Arm anything over an invocation with no argument." in text
    assert "<the person's words>" not in text


# ------------------------------------------------------------------------ what ends it (R3)


def test_a_plugin_version_change_ends_no_grant(project):
    """«A change of the plugin's version ends no grant: a grant holds under every version that
    reads its record, and its words, budget and mark carry over.» (SPEC-011 R3)"""
    assert arm(project, "--commits").returncode == 0
    held = record_of(project)
    held["version"] = "0.0.1"
    armed(project).write_text(json.dumps(held), encoding="utf-8")
    result = grant("--commit", str(project["home"]), "--file", "telemetry/x.json")
    assert "the grant ended" not in result.stdout, result.stdout
    assert record_of(project) == held
    assert not (armed(project).parent / "grants-ended.jsonl").exists()


def test_a_closure_ends_the_grant(project, tmp_path):
    assert arm(project, "--doors", "plan-work").returncode == 0
    close_committed(project)
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
    digest = record_of(project)["mark"]
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


def test_the_only_door_a_handoff_hands_is_taken_without_the_decider_and_spends_no_budget(
        project, tmp_path):
    assert arm(project, "--doors", "plan-work", "--budget", "1").returncode == 0
    out = decide(project, handoff(with_recommended("/plan-work", "accepts")), tmp_path).stdout
    digest = record_of(project)["mark"]
    lines = out.splitlines()
    assert "decision 1: take: a /plan-work" in lines
    assert ("  decided: /plan-work — precondition unmet — the handoff hands no other door and its "
            f"own check accepted (grant sha256 {digest})") in lines
    assert "judge:" not in out and "budget left" not in out
    assert goal.DOOR_LINE.match(lines[lines.index("decision 1: take: a /plan-work") + 1].strip())
    assert not goal.TAKEN_JUDGED.match(lines[lines.index("decision 1: take: a /plan-work") + 1])


@pytest.mark.parametrize("entry,answer,why", [
    ("/analyse", "accepts", "not in the grant's doors"),
    ("/plan-work", "not checked", "was not checked by `door.py --check`"),
    ("/plan-work", "refuses", "every door the handoff hands is excluded"),
])
def test_the_only_door_a_handoff_hands_is_not_taken_outside_the_list_or_unchecked(
        project, tmp_path, entry, answer, why):
    assert arm(project, "--doors", "plan-work").returncode == 0
    out = decide(project, handoff(with_recommended(entry, answer)), tmp_path).stdout
    assert "stop:" in out and why in out and "take:" not in out and "judge:" not in out


def test_the_only_door_with_no_entry_point_is_a_stop(project, tmp_path):
    assert arm(project, "--doors", "plan-work").returncode == 0
    decision = with_recommended("/plan-work", "accepts")
    del decision["recommended"]["entry"]
    out = decide(project, handoff(decision), tmp_path).stdout
    assert "stop:" in out and "with no entry point" in out and "take:" not in out


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


def test_a_certification_refused_again_is_judged_by_the_grant(project, tmp_path):
    """The one judged choice a goal answered whose retry a door reaches — a proof-only re-delivery
    after a certification refused again — is the grant's to judge: the recommended
    `/implement-task` the review's report hands, accepted by its check, beside ending the run."""
    assert arm(project, "--doors", "implement-task", "--budget", "1").returncode == 0
    end_the_run = {"reply_word": "b", "what_it_does": "ends the run on this stop", "check": {}}
    decision = with_recommended("/implement-task", "accepts", end_the_run)
    out = decide(project, handoff(decision), tmp_path).stdout
    assert "decision 1: judge: spawn the door decider over these doors, budget left 1" in out
    assert "door a: /implement-task" in out and "door b: no entry point" in out


def test_a_judged_choice_met_with_the_budget_spent_is_a_stop(project, tmp_path):
    assert arm(project, "--doors", "plan-work", "--budget", "1").returncode == 0
    log = project["home"] / "deliveries" / SLUG / "orchestration.md"
    log.parent.mkdir(parents=True, exist_ok=True)
    digest = record_of(project)["mark"]
    log.write_text(f"decided: /plan-work — keeps the route — the step the framework prescribes "
                   f"(grant sha256 {digest})\n", encoding="utf-8")
    commit(project["home"], f"deliver-scope {SLUG}: log", "deliveries")
    decision = with_recommended("/plan-work", "accepts", door("b", "/reconcile", "accepts"))
    out = decide(project, handoff(decision), tmp_path).stdout
    assert f"stop: the grant's budget of judged doors for {SLUG} is spent" in out


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


@pytest.mark.parametrize("slug", [SLUG, None])
def test_the_closings_own_commit_is_accepted_and_the_closure_lands_with_it(project, slug):
    """R3: an initiative holds its closure once HEAD holds it, so the closing's commit, asked of
    the gate after the marker is written, is still a commit of a covered initiative's paths."""
    one_task_plan(project)
    assert arm(project, "--commits", "--close", slug=slug).returncode == 0
    deliver(project)
    review(project)
    measure(project)
    close = grant("--close", str(project["home"]), "--slug", SLUG)
    assert close.stdout.splitlines()[0] == "accepts", close.stdout
    work = project["home"] / "plans" / SLUG
    (work / "closure.md").write_text("closed\n", encoding="utf-8")
    (work / "intake").mkdir(exist_ok=True)
    (work / "intake" / "close-ask.md").write_text(WORDS + "\n", encoding="utf-8")
    paths = [f"plans/{SLUG}/closure.md", f"plans/{SLUG}/intake/close-ask.md",
             f"plans/{SLUG}/plan.json"]
    result = commit_check(project, *paths)
    assert result.stdout.splitlines()[0] == "accepts", result.stdout
    assert armed(project).exists()
    commit(project["home"], "the closing", *paths[:2])
    after = commit_check(project, f"plans/{SLUG}/closure.md")
    assert after.stdout.splitlines()[0] == "refuses", after.stdout
    assert armed(project).exists() is (slug is None)


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
    assert "a stop's doors are answered when the handoff renders" in rules
    for line in ("`--render` prints the grant's answer on standard error",
                 "a `take:` line is taken", "a `judge:` line goes to `siegard:door-decider`",
                 "a `stop:` line is handed to the person",
                 "a `note:` line says a door lost its `entry`",
                 "`grant.py --commit <project-root> --file <path>...`",
                 "`grant.py --close <project-root> --slug <slug>`",
                 "Never run `grant.py --arm` outside `/siegard-grant`",
                 "a first line `refuses` stops it unless the person's own words in this session "
                 "name that commit or that closing"):
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
    assert "budget of judged doors for each initiative: 2" in out
    assert "commits: yes" in out and "close: no" in out
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


def test_the_budget_of_a_project_grant_counts_each_initiative_apart(project, tmp_path):
    """«The budget left is the grant's budget less the judged `decided:` lines the stopped
    initiative's log gained since the grant armed, each covered initiative counted apart»
    (SPEC-011 R5): a door taken in one initiative leaves another's budget whole, and a stop no
    `--slug` names draws on none."""
    other = "other-run"
    shutil.copytree(project["home"] / "plans" / SLUG, project["home"] / "plans" / other)
    commit(project["home"], "a second live initiative", "plans")
    assert arm(project, "--doors", "plan-work", "--budget", "1", slug=None).returncode == 0
    log = project["home"] / "deliveries" / SLUG / "orchestration.md"
    log.parent.mkdir(parents=True, exist_ok=True)
    digest = record_of(project)["mark"]
    log.write_text(f"decided: /plan-work — keeps the route — the prescribed step (grant sha256 "
                   f"{digest})\n", encoding="utf-8")
    commit(project["home"], f"deliver-scope {SLUG}: log", "deliveries")
    decision = handoff(with_recommended("/plan-work", "accepts", door("b", "/reconcile", "accepts")))
    assert f"budget of judged doors for {SLUG} is spent" in decide(
        project, decision, tmp_path, SLUG).stdout
    assert "budget left 1" in decide(project, decision, tmp_path, other).stdout
    assert "for an initiative no --slug names is spent" in decide(project, decision, tmp_path).stdout

def test_the_skill_states_the_defaults_the_script_applies_and_clears_through_the_script():
    text = " ".join((REPO / "src/claude/skills/siegard-grant/SKILL.md").read_text(
        encoding="utf-8").split())
    assert "all six, `analyse` among them" in text
    assert "zero: a choice between open doors stops until the person writes one" in text
    assert "Run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/grant.py --disarm <project-root>`" in text
    assert "With no grant armed it says so, and that is the report" in text
    assert "the grant covers every live initiative of the project" in text
    assert "**An invocation with no argument arms nothing.**" in text
    assert "A sentence is optional; the flags alone are a grant." in text
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


def test_a_judged_line_without_the_grants_mark_does_not_spend_its_budget(project, tmp_path):
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
    digest = record_of(project)["mark"]
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
    """«The same door over the same task is taken once in a run.» (SPEC-011 R10) The judged door
    is the grant's alone, and the goal's reference arms none."""
    doors = " ".join((REPO / "src/claude/skills/deliver-scope/references/doors.md").read_text(
        encoding="utf-8").split())
    goal_ref = " ".join((REPO / "src/claude/skills/deliver-scope/references/goal.md").read_text(
        encoding="utf-8").split())
    assert ("With a grant armed, run `bin/grant.py --decide <project-root> --latest <the "
            "stopping skill> --after <the log commit before it ran> --slug <slug>` first: `take:` "
            "prints a derived door's `decided:` line, `judge:` a judged door (below), `stop:` or no "
            "answer leaves the stop; the same-task rule binds them.") in doors
    assert "no `decided:` line of this run took over the same task" in doors
    assert "## A judged door, under a grant" in doors and "ending `(grant sha256 <mark>)`" in doors
    assert "A goal arms no judged door" in goal_ref and "## A judged choice" not in goal_ref


# ------------------------------------------------- the answer at the render of a stop (R9)

HANDOFF = BIN / "handoff.py"


def stop_record(project: dict, *, entry: bool = True, slug: str | None = SLUG) -> dict:
    """A plan-work stop as a session fills `--prepare`'s skeleton: `/implement-task` recommended
    and the other door `--prepare` printed beside it."""
    args = ["--prepare", "--skill", "plan-work", "--project", str(project["home"])]
    prepared = subprocess.run([sys.executable, "-B", str(HANDOFF), *args, *(["--slug", slug] if slug else [])],
                              capture_output=True, text=True, check=True)
    data = json.loads(prepared.stdout)
    one = data["decisions"][0]
    one.update(ask="Deliver the first task?", if_none="The plan waits.", relation="one-of",
               recommended={"reply_word": "a", "door": "Deliver it", "why": "The check accepts",
                            "reverses_if": "the task changes", **({"entry": "/implement-task"} if entry else {})},
               others=[{"reply_word": "b", "what_it_does": "Replan first", "entry": "/plan-work",
                        "check": {"answer": "accepts"}}])
    Path(data["report"]).write_text("full\n", encoding="utf-8")
    return data


def declare_no_standard(project: dict) -> None:
    """`standard: {app: null}`, as a project with no registry declares it, so that the doors'
    own checks have every input they take."""
    path = project["home"] / "siegard.json"
    declared = json.loads(path.read_text(encoding="utf-8"))
    path.write_text(json.dumps({**declared, "standard": {"app": None}}), encoding="utf-8")
    commit(project["home"], "declare that the project holds no standard")


def render_stop(project: dict, data: dict) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(HANDOFF), "--render", "-"],
                          input=json.dumps(data), capture_output=True, text=True,
                          cwd=project["home"])


def test_rendering_a_stop_under_a_grant_prints_what_the_grant_answers_on_standard_error(project):
    """«`--render` asks the grant over the doors of the decision it rendered and prints its answer
    on standard error» (SPEC-011 R9): the recommended door is accepted beside an open door, so the
    answer is `judge` with the budget left, and the message on standard output is the handoff."""
    declare_no_standard(project)
    assert arm(project, "--doors", "plan-work,implement-task", "--budget", "2").returncode == 0
    done = render_stop(project, stop_record(project))
    assert done.returncode == 0, done.stdout + done.stderr
    assert "decision 1: judge: spawn the door decider" in done.stderr
    assert "budget left 2" in done.stderr
    assert "door a: /implement-task" in done.stderr and "grant" not in done.stdout


def test_rendering_a_stop_with_no_grant_armed_prints_nothing_on_standard_error(project):
    declare_no_standard(project)
    done = render_stop(project, stop_record(project))
    assert done.returncode == 0, done.stdout + done.stderr
    assert done.stderr == ""


def test_a_recommended_door_with_no_entry_is_answered_stop_and_the_note_names_the_loss(project):
    """The recommended door lost its entry in the move: the answer is `stop`, and the note says
    which door of the skeleton the record no longer holds, so the record is rendered again."""
    declare_no_standard(project)
    assert arm(project, "--doors", "plan-work,implement-task", "--budget", "2").returncode == 0
    done = render_stop(project, stop_record(project, entry=False))
    assert done.returncode == 0, done.stdout + done.stderr
    assert "decision 1: stop: no recommended door is in the grant's doors" in done.stderr
    assert "note: decision 1: the recommended door carries no entry" in done.stderr
    assert "(the skeleton hands /implement-task beside the doors left)" in done.stderr


def test_the_note_names_a_recommended_door_without_entry_though_every_skeleton_door_is_kept(project):
    """The shape of two stops of the day before: the skeleton's doors stay under `others` and the
    recommended door is written beside them with no entry, so no door of the skeleton is absent
    and the note still says the recommended one cannot be answered."""
    declare_no_standard(project)
    assert arm(project, "--doors", "plan-work,implement-task", "--budget", "2").returncode == 0
    data = stop_record(project, entry=False)
    data["decisions"][0]["others"].append({"reply_word": "c", "what_it_does": "Deliver, kept as printed",
                                           "entry": "/implement-task", "check": {"answer": "accepts"}})
    done = render_stop(project, data)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "note: decision 1: the recommended door carries no entry" in done.stderr
    assert "skeleton hands" not in done.stderr


def test_a_grant_that_ended_at_the_render_adds_no_note(project):
    declare_no_standard(project)
    assert arm(project, "--doors", "plan-work,implement-task", "--budget", "2").returncode == 0
    close_committed(project)
    done = render_stop(project, stop_record(project, entry=False))
    assert "stop: the grant ended" in done.stderr and "note:" not in done.stderr


def test_rendering_a_stop_under_a_grant_of_another_version_is_answered_by_it(project):
    """The first stop after an update is answered by the grant armed before it."""
    declare_no_standard(project)
    assert arm(project, "--doors", "plan-work,implement-task", "--budget", "2").returncode == 0
    held = record_of(project)
    armed(project).write_text(json.dumps({**held, "version": "0.0.1"}), encoding="utf-8")
    done = render_stop(project, stop_record(project))
    assert done.returncode == 0, done.stdout + done.stderr
    assert "the grant ended" not in done.stderr and f"(sha256 {held['mark']})" in done.stderr
    assert armed(project).exists() and ended_grants(project) == []


def test_a_check_over_an_inferred_initiative_is_told_to_the_door_decider(project):
    declare_no_standard(project)
    assert arm(project, "--doors", "plan-work,implement-task", "--budget", "2",
               slug=None).returncode == 0
    data = stop_record(project, slug=None)
    data["decisions"][0]["recommended"].update(entry="/plan-work")
    data["decisions"][0]["others"][0].update(entry="/implement-task")
    done = render_stop(project, data)
    assert done.returncode == 0, done.stdout + done.stderr
    assert f"(its check ran over {SLUG}, which the record did not name)" in done.stderr


# ------------------------------------------------- obligations at the stop (R12, R13)

HOOKS = REPO / "src/claude/hooks"
TAKE_RECORD = {"ask": "what next?", "recommended": {"door": "runs /plan-work", "why": "w",
               "reverses_if": "r", "reply_word": "plan", "entry": "/plan-work",
               "check": {"answer": "accepts"}}, "others": [], "if_none": "nothing runs"}


def answer_printed(project: dict, decision: dict, tmp_path: Path) -> str:
    done = decide(project, handoff(decision), tmp_path)
    assert done.returncode == 0, done.stdout + done.stderr
    return done.stdout


def gate_dir(project: dict) -> Path:
    return project["home"] / ".git" / "siegard"


def post_tool(project: dict, tool: str, given: dict, output: str = "",
              session: str = "s1") -> subprocess.CompletedProcess:
    event = {"hook_event_name": "PostToolUse", "session_id": session,
             "cwd": str(project["home"]), "tool_name": tool, "tool_input": given,
             "tool_response": {"stdout": "", "stderr": output}}
    return subprocess.run([sys.executable, "-B", str(HOOKS / "after_tool.py")],
                          input=json.dumps(event), capture_output=True, text=True)


def rendered(project: dict, output: str, session: str = "s1") -> None:
    done = post_tool(project, "Bash", {"command": "python3 -B /p/bin/handoff.py --render r.json"},
                     output, session)
    assert done.returncode == 0 and done.stdout == "", done


def stop_hook(project: dict, message: str = "Done.", session: str = "s1",
              env: dict | None = None) -> subprocess.CompletedProcess:
    event = {"hook_event_name": "Stop", "session_id": session, "cwd": str(project["home"]),
             "stop_hook_active": False, "last_assistant_message": message}
    return subprocess.run([sys.executable, "-B", str(HOOKS / "goal_stop.py")],
                          input=json.dumps(event), capture_output=True, text=True,
                          env={**os.environ, **(env or {})})


def gate_events(project: dict) -> list[str]:
    path = gate_dir(project) / "grant-checks.jsonl"
    return [json.loads(line)["event"] for line in path.read_text(encoding="utf-8").splitlines()] \
        if path.is_file() else []


def test_a_renders_output_binds_one_obligation_per_take_and_judge_with_the_grants_mark(
        project, tmp_path):
    import grant as granting
    assert arm(project, "--doors", "plan-work,reconcile", "--budget", "2").returncode == 0
    digest = record_of(project)["mark"]
    took = granting.obligations_from(answer_printed(project, TAKE_RECORD, tmp_path))
    assert [(o["kind"], o["entry"], o["mark"]) for o in took] == [("take", "plan-work", digest)]
    assert took[0]["decided"].startswith("decided: /plan-work — precondition unmet")
    judged = granting.obligations_from(answer_printed(
        project, with_recommended("/plan-work", "accepts", door("b", "/reconcile", "accepts")),
        tmp_path))
    assert judged[0]["kind"] == "judge" and judged[0]["mark"] == digest
    assert [d["entry"] for d in judged[0]["doors"]] == ["/plan-work", "/reconcile"]
    stopped = answer_printed(project, with_recommended("/analyse", "accepts"), tmp_path)
    assert "stop:" in stopped and granting.obligations_from(stopped) == []


def test_a_take_left_uncarried_blocks_the_stop_once_and_the_next_stop_is_released(
        project, tmp_path):
    assert arm(project, "--doors", "plan-work").returncode == 0
    rendered(project, answer_printed(project, TAKE_RECORD, tmp_path))
    first = stop_hook(project, "O plano está pronto. Quer que eu siga?")
    held = json.loads(first.stdout)
    assert held["decision"] == "block"
    assert "decision 1: take: plan /plan-work" in held["reason"]
    assert "/siegard:plan-work" in held["reason"]
    second = stop_hook(project, "O plano está pronto. Quer que eu siga?")
    assert second.returncode == 0 and "block" not in second.stdout
    assert gate_events(project) == ["recorded", "blocked", "released"]


def test_the_doors_skill_carries_a_take_out_and_another_skill_does_not(project, tmp_path):
    assert arm(project, "--doors", "plan-work").returncode == 0
    rendered(project, answer_printed(project, TAKE_RECORD, tmp_path))
    post_tool(project, "Skill", {"skill": "siegard:review-change"})
    assert "block" in stop_hook(project).stdout
    rendered(project, answer_printed(project, TAKE_RECORD, tmp_path))
    post_tool(project, "Skill", {"skill": "siegard:plan-work", "args": "x"})
    done = stop_hook(project)
    assert done.returncode == 0 and "block" not in done.stdout
    assert "fulfilled" in gate_events(project)


def test_the_door_decider_carries_a_judge_out_and_another_agent_does_not(project, tmp_path):
    assert arm(project, "--doors", "plan-work,reconcile", "--budget", "2").returncode == 0
    judged = answer_printed(project, with_recommended(
        "/plan-work", "accepts", door("b", "/reconcile", "accepts")), tmp_path)
    rendered(project, judged)
    post_tool(project, "Agent", {"subagent_type": "siegard:task-implementer", "prompt": "p"})
    held = json.loads(stop_hook(project).stdout)
    assert held["decision"] == "block" and "siegard:door-decider" in held["reason"]
    assert f"(grant sha256 {record_of(project)['mark']})" in held["reason"]
    rendered(project, judged)
    post_tool(project, "Agent", {"subagent_type": "siegard:door-decider", "prompt": "p"})
    assert "block" not in stop_hook(project).stdout


def test_measure_logs_the_stop_and_never_blocks(project, tmp_path):
    assert arm(project, "--doors", "plan-work").returncode == 0
    rendered(project, answer_printed(project, TAKE_RECORD, tmp_path))
    done = stop_hook(project, env={"SIEGARD_GRANT_STOP": "measure"})
    assert done.returncode == 0 and "block" not in done.stdout
    assert gate_events(project) == ["recorded", "measured"]


DECISION_NAMING_A_DOOR = (
    "The plan is ready and its one task waits.\n\n"
    "- **Recommended** `deliver`: /implement-task over the late fee. It is the only task. "
    "It would change if you want the plan changed first.\n\nReply with the word.")


def test_an_unrendered_decision_naming_a_door_leaves_no_line_of_the_grants(project):
    """«a stop that hands a decision with no render printed since the session's last stop is read
    by the handoff check, from the session's turn record (SPEC-008 R15), and the grant logs no
    line of its own for it.» (SPEC-011 R13)"""
    assert arm(project, "--doors", "implement-task").returncode == 0
    done = stop_hook(project, DECISION_NAMING_A_DOOR)
    assert done.returncode == 0 and "block" not in done.stdout
    assert gate_events(project) == []


def test_every_line_of_the_grant_carries_the_mode_it_was_answered_under(project, tmp_path):
    """«Each recording, carrying out, block and release is one line of `grant-checks.jsonl`
    beside the grant, carrying the `mode` it was answered under.» (SPEC-011 R12)"""
    assert arm(project, "--doors", "plan-work").returncode == 0
    rendered(project, answer_printed(project, TAKE_RECORD, tmp_path))
    assert "block" in stop_hook(project).stdout
    assert "block" not in stop_hook(project).stdout
    rendered(project, answer_printed(project, TAKE_RECORD, tmp_path))
    stop_hook(project, env={"SIEGARD_GRANT_STOP": "measure"})
    path = gate_dir(project) / "grant-checks.jsonl"
    lines = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines()]
    assert [(x["event"], x["mode"]) for x in lines] == [
        ("recorded", "enforce"), ("blocked", "enforce"), ("released", "enforce"),
        ("recorded", "enforce"), ("measured", "measure")]


def test_a_stop_after_a_render_or_naming_no_door_is_not_blocked(project, tmp_path):
    assert arm(project, "--doors", "plan-work").returncode == 0
    stopped = answer_printed(project, with_recommended("/analyse", "accepts"), tmp_path)
    rendered(project, stopped)
    assert "block" not in stop_hook(project, DECISION_NAMING_A_DOOR).stdout
    assert "block" not in stop_hook(project, "The tests pass. Shall I push the branch?").stdout
    assert gate_events(project) == []


def test_no_grant_leaves_the_stop_alone_and_a_grant_of_another_version_holds_it(project,
                                                                                tmp_path):
    rendered(project, "grant: x (sha256 0123456789abcdef)\ndecision 1: take: plan /plan-work\n")
    assert "block" not in stop_hook(project, DECISION_NAMING_A_DOOR).stdout
    assert arm(project, "--doors", "plan-work").returncode == 0
    printed = answer_printed(project, TAKE_RECORD, tmp_path)
    held = record_of(project)
    held["version"] = "0.0.1"
    armed(project).write_text(json.dumps(held), encoding="utf-8")
    rendered(project, printed)
    assert "block" in stop_hook(project, DECISION_NAMING_A_DOOR).stdout
    assert gate_events(project) == ["recorded", "blocked"]


def test_another_sessions_obligation_is_not_this_sessions(project, tmp_path):
    assert arm(project, "--doors", "plan-work").returncode == 0
    rendered(project, answer_printed(project, TAKE_RECORD, tmp_path), session="other")
    assert "block" not in stop_hook(project, session="s1").stdout
    assert "block" in stop_hook(project, session="other").stdout


def test_a_stop_awaiting_background_work_is_not_read(project, tmp_path):
    assert arm(project, "--doors", "plan-work").returncode == 0
    rendered(project, answer_printed(project, TAKE_RECORD, tmp_path))
    event = {"hook_event_name": "Stop", "session_id": "s1", "cwd": str(project["home"]),
             "last_assistant_message": "waiting", "background_tasks": [{"id": "b"}]}
    done = subprocess.run([sys.executable, "-B", str(HOOKS / "goal_stop.py")],
                          input=json.dumps(event), capture_output=True, text=True)
    assert "block" not in done.stdout
    assert "block" in stop_hook(project).stdout


@pytest.mark.parametrize("stdin", ["", "not json", "[1]", json.dumps({"tool_name": "Bash"}),
                                   json.dumps({"hook_event_name": "PostToolUse",
                                               "tool_name": "Bash", "session_id": "s",
                                               "cwd": "/gone", "tool_input": {
                                                   "command": "handoff.py --render x"}})])
def test_the_post_tool_hook_never_fails_and_prints_nothing(stdin):
    done = subprocess.run([sys.executable, "-B", str(HOOKS / "after_tool.py")], input=stdin,
                          capture_output=True, text=True)
    assert done.returncode == 0 and done.stdout == "" and done.stderr == ""
