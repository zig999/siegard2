"""`tools/replay_stops.py` reads stops, cuts transcripts and grades runs the same way every time.

No model runs here: the parts of the replay that decide which stops are read, where a transcript
is cut, what the guard denies and what a run came to are held over small fixtures.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("replay_stops", REPO / "tools/replay_stops.py")
replay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(replay)


def test_a_reply_is_read_as_go_status_person_only_or_content():
    assert replay.reply_class("Siga") == "go"
    assert replay.reply_class("pode seguir com o recomendado") == "go"
    assert replay.reply_class("Próximo passo?") == "status-q"
    assert replay.reply_class("pode comitar tudo") == "person-only"
    assert replay.reply_class("Siga?") == "content"
    assert replay.reply_class("Mova este arquivo para a pasta de escopos e diga por que ele ficou fora da rota de entrega") \
        == "content"


def test_only_the_person_s_own_words_are_a_turn():
    said = {"type": "user", "message": {"content": "Siga"}}
    assert replay.is_person(said) == "Siga"
    for harness in ({**said, "isMeta": True}, {**said, "isCompactSummary": True},
                    {"type": "user", "message": {"content": "<task-notification>x"}},
                    {"type": "user", "message": {"content": "Stop hook feedback: x"}},
                    {"type": "user", "message": {"content": [{"type": "tool_result",
                                                              "content": "ok"}]}}):
        assert replay.is_person(harness) is None


def guarded(tmp_path: Path, given: dict) -> dict | None:
    return replay.guard(tmp_path / "log.jsonl", Path("/tmp/root/arm/3-1"), ["/home/x/sales/inv"],
                        {"tool_name": "Bash", "tool_input": given})


def test_the_guard_denies_the_real_consumer_and_stray_scratch_and_allows_the_run_s_own(tmp_path):
    assert guarded(tmp_path, {"command": "git -C /home/x/sales/inv status"})[
        "hookSpecificOutput"]["permissionDecision"] == "deny"
    stray = guarded(tmp_path, {"command": "cat > /tmp/rec.json"})
    assert "/tmp/root/arm/3-1/scratch" in stray["hookSpecificOutput"]["permissionDecisionReason"]
    assert guarded(tmp_path, {"command": "cat > /tmp/root/arm/3-1/scratch/rec.json"}) is None
    assert guarded(tmp_path, {"command": "ls src"}) is None
    assert len((tmp_path / "log.jsonl").read_text().splitlines()) == 2


def test_the_guard_never_denies_the_arm_s_own_tree_under_tmp(tmp_path):
    use = {"command": "python3 -B /tmp/arms/B/bin/handoff.py --prepare"}
    assert guarded(tmp_path, use) is not None
    assert replay.guard(tmp_path / "log.jsonl", Path("/tmp/root/arm/3-1"), ["/home/x/sales/inv"],
                        {"tool_name": "Bash", "tool_input": use}, ("/tmp/arms/B",)) is None

def event(kind: str, at: str, **content) -> dict:
    return {"type": kind, "timestamp": at, "message": {"content": content.get("content", "")}}


def test_the_final_cut_lands_on_the_last_tool_result_before_the_stop_s_message():
    events = [
        event("user", "2026-11-21T10:00:00", content="Siga"),
        event("assistant", "2026-11-21T10:00:05", content=[{"type": "tool_use", "id": "a"}]),
        event("user", "2026-11-21T10:00:06", content=[{"type": "tool_result", "tool_use_id": "a"}]),
        event("assistant", "2026-11-21T10:00:09", content=[{"type": "text", "text": "Done. Next?"}]),
        event("user", "2026-11-21T10:05:00", content="Siga"),
    ]
    assert replay.cut_at(events, "2026-11-21T10:00:09", "final") == 2


def test_a_transcript_line_is_rewritten_to_the_clone_the_tree_and_the_new_session():
    line = ('{"cwd":"/home/x/sales/inv","p":"/home/x/sales/other","s":"old-id",'
            '"c":"/home/x/.claude/plugins/cache/gen/siegard/5.133.0/bin/handoff.py"}')
    out = replay.rewrite(line, Path("/home/x/sales/inv"), Path("/tmp/r/inv"), Path("/arm"),
                         "old-id", "new-id")
    assert json.loads(out) == {"cwd": "/tmp/r/inv", "p": "/tmp/r/other", "s": "new-id",
                               "c": "/arm/bin/handoff.py"}


def test_a_real_tmp_path_in_the_history_is_moved_under_the_run_s_scratch():
    line = '{"c":"python3 /tmp/pd/record.json","t":"/tmp/claude-1000/x/tasks/a.output","h":"/home/x/tmp/keep"}'
    out = replay.rewrite(line, Path("/home/x/sales/inv"), Path("/tmp/r/inv"), Path("/arm"),
                         "old-id", "new-id", Path("/tmp/r/run/scratch"))
    assert json.loads(out) == {"c": "python3 /tmp/r/run/scratch/pd/record.json",
                               "t": "/tmp/claude-1000/x/tasks/a.output",
                               "h": "/home/x/tmp/keep"}


def git(cwd: Path, *args: str, when: str | None = None) -> str:
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    if when:
        env.update(GIT_AUTHOR_DATE=when, GIT_COMMITTER_DATE=when)
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True,
                          check=True, env=env).stdout.strip()


def test_a_clone_is_cut_at_the_stop_s_second_and_holds_no_goal_armed_later(tmp_path, monkeypatch):
    real = tmp_path / "sales" / "inv"
    real.mkdir(parents=True)
    git(real, "init", "-q", "-b", "main")
    (real / "a").write_text("a")
    git(real, "add", "a")
    git(real, "commit", "-q", "-m", "a", when="2026-11-21T10:00:05Z")
    (real / "b").write_text("b")
    git(real, "add", "b")
    git(real, "commit", "-q", "-m", "b", when="2026-11-21T10:00:08Z")
    wanted = git(real, "rev-parse", "HEAD")
    (real / "c").write_text("c")
    git(real, "add", "c")
    git(real, "commit", "-q", "-m", "c", when="2026-11-21T10:30:00Z")
    (real / ".git/siegard").mkdir()
    (real / ".git/siegard/goal.json").write_text("{}")
    (real / ".git/siegard/keep.json").write_text("{}")
    monkeypatch.setattr(replay, "PROJECTS", tmp_path / "projects")
    events = [
        event("user", "2026-11-21T10:00:00", content="Siga"),
        event("assistant", "2026-11-21T10:00:05", content=[{"type": "tool_use", "id": "a",
                                                            "input": {"command": "cat /tmp/pd/r"}}]),
        event("user", "2026-11-21T10:00:06", content=[{"type": "tool_result", "tool_use_id": "a"}]),
        event("assistant", "2026-11-21T10:00:09", content=[{"type": "text", "text": "Done. Next?"}]),
    ]
    source = replay.transcript_dir(real)
    source.mkdir(parents=True)
    (source / "old.jsonl").write_text("\n".join(json.dumps(e) for e in events), encoding="utf-8")
    tree = tmp_path / "arm" / ".claude-plugin"
    tree.mkdir(parents=True)
    (tree / "plugin.json").write_text(json.dumps({"version": "9.9.9"}))
    point = {"consumer": str(real), "session": "old", "at": "2026-11-21T10:00:09", "grant": None}
    meta = replay.build(point, tmp_path / "arm", tmp_path / "run", "final")
    clone = Path(meta["clone"])
    assert git(clone, "rev-parse", "HEAD") == wanted
    assert not (clone / ".git/siegard/goal.json").exists()
    assert (clone / ".git/siegard/keep.json").exists()
    written = (Path(meta["transcript"]) / f"{meta['session']}.jsonl").read_text(encoding="utf-8")
    assert "/tmp/pd/" not in written
    assert f"{(tmp_path / 'run').resolve()}/scratch/pd/r" in written


def test_the_turn_record_is_seeded_from_the_last_rendering_skill_of_the_cut_turn():
    skill = lambda name: [{"type": "tool_use", "id": name, "name": "Skill",
                           "input": {"skill": name}}]
    events = [
        event("assistant", "2026-11-21T09:59:00Z", content=skill("siegard:review-change")),
        event("user", "2026-11-21T10:00:00Z", content="Siga"),
        event("assistant", "2026-11-21T10:00:05Z", content=skill("siegard:siegard-progress")),
        event("assistant", "2026-11-21T10:00:07Z", content=skill("siegard:plan-work")),
        event("user", "2026-11-21T10:00:08Z", content=[{"type": "tool_result", "tool_use_id": "p"}]),
        event("assistant", "2026-11-21T10:00:09Z", content=[{"type": "text", "text": "Done."}]),
    ]
    from datetime import datetime
    assert replay.route_at(events, 4) == datetime.fromisoformat("2026-11-21T10:00:07+00:00").timestamp()
    assert replay.route_at(events[:3], 2) is None, "a route of an earlier turn is not this turn's"
    assert "plan-work" in replay.rendering_skills()
    assert "siegard-progress" not in replay.rendering_skills()

def facts(**given) -> dict:
    return {"renders": 1, "answers": [], "limit_hit": False, **given}


def test_a_stop_the_handoff_check_blocked_that_still_did_not_render_is_blocked_no_render():
    assert replay.outcome(facts(renders=0), [["blocked", "handoff"], ["released", "handoff"]],
                          []) == "blocked-no-render"
    assert replay.outcome(facts(renders=0), [["released", "handoff"]], []) == "no-block-no-render"


def test_a_run_s_outcome_is_read_from_its_renders_its_answers_and_its_calls():
    took = facts(answers=["decision 1: judge: spawn the door decider"])
    assert replay.outcome(took, [], [{"agent": "siegard:door-decider"}]) == "took"
    assert replay.outcome(took, [], []) == "took-not-carried"
    assert replay.outcome(facts(answers=["decision 1: stop: the choice is the person's"]), [],
                          []) == "stop"
    assert replay.outcome(facts(), [], []) == "rendered-silent"
    assert replay.outcome(facts(renders=0), [["blocked", "unrendered"]], []) == "blocked-no-render"
    assert replay.outcome(facts(renders=0), [], []) == "no-block-no-render"
    assert replay.outcome(facts(limit_hit=True), [], []) == "invalid"


def test_the_grant_of_a_stop_is_the_one_armed_at_its_time(tmp_path):
    base = tmp_path / ".git/siegard"
    base.mkdir(parents=True)
    (base / "grants-ended.jsonl").write_text(json.dumps(
        {"mark": "old", "armed_at": "2026-11-19T10:00:00Z", "ended_at": "2026-11-20T10:00:00Z"})
        + "\n")
    (base / "grant.json").write_text(json.dumps({"mark": "new",
                                                 "armed_at": "2026-11-20T12:00:00Z"}))
    assert replay.grant_at(tmp_path, "2026-11-19T12:00:00")["mark"] == "old"
    assert replay.grant_at(tmp_path, "2026-11-20T11:00:00") is None
    assert replay.grant_at(tmp_path, "2026-11-21T09:00:00")["mark"] == "new"
