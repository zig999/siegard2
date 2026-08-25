"""`telemetry.py` counts how the work happened from disk, and says what it could not read.

The one shipped script that reads outside the project: the harness's session transcripts, in a
format this framework does not own. So the fixtures here are transcripts in that format, written
by hand from real ones — an assistant entry carrying a `tool_use` block, a user entry carrying its
`tool_result`, a `subagents/agent-<id>.meta.json` naming the tool use and a transcript beside it
with `usage` on every assistant message. If the harness changes the shape, these fixtures stop
describing it and the tests below keep passing; what they hold is that the script reads the shape
it was written against and refuses to invent where it cannot.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

REPO = Path(__file__).resolve().parent.parent
TELEMETRY = REPO / "src/claude/bin/telemetry.py"

SINCE = "2026-08-20T10:00:00Z"
UNTIL = "2026-08-20T12:00:00Z"
STAMP = "20260820T120000Z"


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(TELEMETRY), *map(str, args)],
                          capture_output=True, text=True)


def contract() -> Draft202012Validator:
    return Draft202012Validator(
        json.loads((REPO / "src/claude/schemas/telemetry.json").read_text(encoding="utf-8")))


def line(**entry) -> str:
    return json.dumps(entry) + "\n"


def assistant(stamp: str, *blocks: dict, session: str = "s1", **extra) -> str:
    return line(type="assistant", timestamp=stamp, sessionId=session, cwd="/consumer",
                version="2.1.0", message={"role": "assistant", "content": list(blocks)}, **extra)


def user_result(stamp: str, tool_use_id: str, text: str, raw: dict | None = None) -> str:
    return line(type="user", timestamp=stamp, sessionId="s1", cwd="/consumer",
                message={"role": "user", "content": [
                    {"type": "tool_result", "tool_use_id": tool_use_id, "content": text}]},
                toolUseResult=raw if raw is not None else {"stdout": text, "stderr": "",
                                                            "interrupted": False})


def human(stamp: str, text: str = "go on") -> str:
    return line(type="user", timestamp=stamp, sessionId="s1", cwd="/consumer",
                message={"role": "user", "content": text})


@pytest.fixture
def consumer(tmp_path: Path) -> dict:
    """A consumer project inside the window: one initiative with a BLOCKING task, one captured
    run, a decision log that gained one entry after `since`, and a telemetry root declared."""
    home = tmp_path / "consumer"
    home.mkdir()
    subprocess.run(["git", "init", "-q", str(home)], check=True)
    subprocess.run(["git", "-C", str(home), "config", "user.email", "t@example.com"], check=True)
    subprocess.run(["git", "-C", str(home), "config", "user.name", "t"], check=True)
    (home / "siegard.json").write_text(json.dumps({
        "specification_root": "specification", "targets": {"backend": "backend"},
        "work_root": "work", "delivery_root": "delivery", "telemetry_root": "telemetry",
    }), encoding="utf-8")
    (home / "backend").mkdir()
    spec_root = home / "specification"
    spec_root.mkdir()
    (spec_root / "decision-log.md").write_text(
        "---\nentries:\n- location: domain/x/a.md\n  field: attributes\n  unstated: u\n"
        "  decided: d\n  why: w\n---\n", encoding="utf-8")

    def commit(message: str, when: str) -> None:
        subprocess.run(["git", "-C", str(home), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(home), "-c", f"user.email=t@example.com",
                        "-c", "user.name=t", "commit", "-q", "-m", message, "--date", when],
                       check=True, env={"GIT_COMMITTER_DATE": when, "PATH": "/usr/bin:/bin",
                                        "HOME": str(tmp_path)})

    commit("before the window", "2026-08-20T09:00:00Z")

    (spec_root / "decision-log.md").write_text(
        "---\nentries:\n- location: domain/x/a.md\n  field: attributes\n  unstated: u\n"
        "  decided: d\n  why: w\n- location: domain/x/b.md\n  field: attributes\n"
        "  unstated: second\n  decided: e\n  why: v\n---\n", encoding="utf-8")
    task = home / "work/checkout/task/checkout/record-order.md"
    task.parent.mkdir(parents=True)
    task.write_text(
        "---\ntitle: t\nsummary: s\nobjective: o\ncriteria:\n- c\nimplements:\n- domain/x/a\n---\n"
        "## What it is\nProse.\n\n## Notes\n"
        "BLOCKING, from the specification — domain/x/a states the opposite of the scope.\n"
        "UNDERDETERMINED, from the specification — an empty order would satisfy every criterion.\n",
        encoding="utf-8")
    (home / "work/checkout/plan.json").write_text(json.dumps({
        "contract_version": "siegard-plan/3", "nodes": [
            {"id": "epic/checkout", "kind": "epic"},
            {"id": "task/checkout/record-order", "kind": "task"}], "edges": []}),
        encoding="utf-8")
    record = home / "delivery/checkout/implementation/checkout/record-order.md"
    record.parent.mkdir(parents=True)
    record.write_text("---\n---\n", encoding="utf-8")
    run_dir = home / "delivery/checkout/run/checkout-suite"
    run_dir.mkdir(parents=True)
    (run_dir / "run.json").write_text(json.dumps({
        "contract_version": "siegard-run/2", "run": "run/checkout-suite", "cwd": "/consumer",
        "timeout_seconds": 60, "outcome": "failed", "failed_step": "test",
        "steps": [
            {"name": "build", "command": "make", "outcome": "passed", "exit_code": 0,
             "output": "build.log", "started_at": "2026-08-20T10:30:00.000+00:00",
             "ended_at": "2026-08-20T10:30:12.500+00:00"},
            {"name": "test", "command": "make test", "outcome": "failed", "exit_code": 1,
             "output": "test.log", "started_at": "2026-08-20T10:30:12.600+00:00",
             "ended_at": "2026-08-20T10:31:00.000+00:00"}],
        "combined_output": "run.log"}), encoding="utf-8")
    commit("inside the window", "2026-08-20T11:00:00Z")

    transcripts = tmp_path / "transcripts"
    session = transcripts / "s1.jsonl"
    session.parent.mkdir()
    session.write_text(
        human("2026-08-20T09:30:00.000Z", "before the window")
        + human("2026-08-20T10:05:00.000Z")
        + assistant("2026-08-20T10:06:00.000Z", {
            "type": "tool_use", "id": "tu-plan", "name": "Bash",
            "input": {"command": "python3 -B /plugin/bin/plan.py --check work/checkout spec"}})
        + user_result("2026-08-20T10:06:05.000Z", "tu-plan",
                      "Exit code 1\nwork/checkout: 2 problem(s)\n")
        + assistant("2026-08-20T10:07:00.000Z", {
            "type": "tool_use", "id": "tu-ls", "name": "Bash", "input": {"command": "ls"}})
        + user_result("2026-08-20T10:07:01.000Z", "tu-ls", "a\nb\n")
        + assistant("2026-08-20T10:08:00.000Z", {
            "type": "tool_use", "id": "tu-agent-1", "name": "Agent",
            "input": {"subagent_type": "execution-contract-binder", "description": "Bind record-order",
                      "prompt": "secret prompt text"}})
        + user_result("2026-08-20T10:08:01.000Z", "tu-agent-1", "launched",
                      {"agentId": "a1", "resolvedModel": "claude-opus-5", "status": "async_launched"})
        + assistant("2026-08-20T10:20:00.000Z", {
            "type": "tool_use", "id": "tu-agent-2", "name": "Agent",
            "input": {"subagent_type": "execution-contract-binder", "description": "Bind record-order",
                      "prompt": "again"}})
        + assistant("2026-08-20T10:40:00.000Z", {
            "type": "tool_use", "id": "tu-deliver", "name": "Bash",
            "input": {"command": "cd x && python3 -B /plugin/bin/deliver.py d w t s"}})
        + user_result("2026-08-20T10:40:03.000Z", "tu-deliver", "sound.\n")
        + human("2026-08-20T13:00:00.000Z", "after the window"),
        encoding="utf-8")
    subagents = transcripts / "s1" / "subagents"
    subagents.mkdir(parents=True)
    (subagents / "agent-a1.meta.json").write_text(json.dumps({
        "agentType": "execution-contract-binder", "description": "Bind record-order",
        "toolUseId": "tu-agent-1", "spawnDepth": 1}), encoding="utf-8")
    (subagents / "agent-a1.jsonl").write_text(
        line(type="user", timestamp="2026-08-20T10:08:02.000Z", isSidechain=True, agentId="a1",
             message={"role": "user", "content": "the prompt"})
        + line(type="assistant", timestamp="2026-08-20T10:09:00.000Z", isSidechain=True,
               agentId="a1", message={"role": "assistant", "model": "claude-opus-5",
                                      "content": [{"type": "tool_use", "id": "x", "name": "Read",
                                                   "input": {}}],
                                      "usage": {"input_tokens": 10, "cache_creation_input_tokens": 100,
                                                "cache_read_input_tokens": 1000,
                                                "output_tokens": 50}})
        + line(type="assistant", timestamp="2026-08-20T10:12:30.000Z", isSidechain=True,
               agentId="a1", message={"role": "assistant", "model": "claude-opus-5",
                                      "content": [{"type": "text", "text": "done"}],
                                      "usage": {"input_tokens": 5, "cache_creation_input_tokens": 0,
                                                "cache_read_input_tokens": 2000,
                                                "output_tokens": 450}}),
        encoding="utf-8")
    return {"home": home, "transcripts": transcripts, "tmp": tmp_path}


def report_of(consumer: dict, *extra: str) -> tuple[subprocess.CompletedProcess, dict | None]:
    done = run(consumer["home"], "--since", SINCE, "--until", UNTIL,
               "--transcripts", consumer["transcripts"], *extra)
    destination = consumer["home"] / "telemetry" / f"{STAMP}.json"
    report = json.loads(destination.read_text(encoding="utf-8")) if destination.is_file() else None
    return done, report


# ------------------------------------------------------------------------ the report


def test_the_report_lands_at_the_stamp_and_satisfies_its_contract(consumer):
    done, report = report_of(consumer)
    assert done.returncode == 0, done.stdout + done.stderr
    assert report is not None
    assert [e.message for e in contract().iter_errors(report)] == []
    assert report["written_to"].endswith(f"telemetry/{STAMP}.json")
    assert report["window"] == {"since": "2026-08-20T10:00:00.000Z",
                                "until": "2026-08-20T12:00:00.000Z",
                                "since_resolved_from": "named"}
    assert f"report: {consumer['home'] / 'telemetry' / STAMP}.json" in done.stdout


def test_agents_are_summed_from_their_own_transcripts_and_repeats_are_marked(consumer):
    _, report = report_of(consumer)
    first, second = report["agents"]
    assert first["agent_type"] == "execution-contract-binder"
    assert first["agent_id"] == "a1"
    assert first["model"] == "claude-opus-5"
    assert first["usage"] == {"input_tokens": 15, "cache_creation_input_tokens": 100,
                              "cache_read_input_tokens": 3000, "output_tokens": 500}
    assert first["duration_seconds"] == 268.0
    assert first["messages"] == 2 and first["tool_calls"] == 1
    assert first["repeats_earlier"] is False
    # The second spawn has no meta file: null usage, a stated reason, and a repeat flag — the
    # mechanical half of the rework question, never the judgment.
    assert second["usage"] is None
    assert "names tool use tu-agent-2" in second["unavailable"]
    assert second["repeats_earlier"] is True
    totals = report["agent_totals"]
    assert totals["overall"]["invocations"] == 2
    assert totals["overall"]["with_transcript"] == 1
    assert totals["overall"]["usage"]["output_tokens"] == 500
    assert totals["by_type"]["execution-contract-binder"]["duration_seconds"] == 268.0


def test_no_prompt_text_leaves_the_transcripts(consumer):
    _, report = report_of(consumer)
    dumped = json.dumps(report)
    assert "secret prompt text" not in dumped
    assert "the prompt" not in dumped
    assert "before the window" not in dumped


def test_framework_commands_carry_exit_and_problem_counts_and_nothing_else_is_listed(consumer):
    _, report = report_of(consumer)
    assert [c["scripts"] for c in report["commands"]] == [["plan.py"], ["deliver.py"]]
    refused, sound = report["commands"]
    assert refused["exit_code"] == 1 and refused["exit_marker"] is True
    assert refused["problems"] == 2
    assert sound["exit_code"] is None and sound["exit_marker"] is False
    assert sound["problems"] is None and sound["unavailable"] is None


def test_the_window_bounds_every_transcript_count(consumer):
    _, report = report_of(consumer)
    [session] = report["harness"]["sessions"]
    assert session["human_turns_in_window"] == ["2026-08-20T10:05:00.000Z"]
    assert session["harness_versions"] == ["2.1.0"]
    assert session["working_directories"] == ["/consumer"]


def test_runs_are_read_from_the_record_with_a_duration_per_step(consumer):
    _, report = report_of(consumer)
    [captured] = report["runs"]
    assert captured["initiative"] == "checkout" and captured["run"] == "checkout-suite"
    assert captured["outcome"] == "failed" and captured["failed_step"] == "test"
    assert [s["duration_seconds"] for s in captured["steps"]] == [12.5, 47.4]
    assert captured["started_at"] == "2026-08-20T10:30:00.000+00:00"


def test_notes_are_quoted_as_the_validator_spells_them(consumer):
    _, report = report_of(consumer)
    classes = {(n["class"], n["node"]) for n in report["notes"]}
    assert classes == {("blocking", "task/checkout/record-order"),
                       ("underdetermined", "task/checkout/record-order")}
    blocking = next(n for n in report["notes"] if n["class"] == "blocking")
    assert blocking["text"].startswith("BLOCKING, from the specification —")


def test_decisions_added_are_diffed_against_the_commit_before_the_window(consumer):
    _, report = report_of(consumer)
    assert report["decisions"]["total_now"] == 2
    assert report["decisions"]["baseline"].startswith("commit ")
    assert [e["unstated"] for e in report["decisions"]["added"]] == ["second"]


def test_scope_counts_tasks_and_records_landed_in_the_window(consumer):
    _, report = report_of(consumer)
    [initiative] = report["scope"]["initiatives"]
    assert initiative == {
        "slug": "checkout", "live": True, "tasks": 1, "tasks_with_implementation_record": 1,
        "implementation_records_committed_in_window":
            ["delivery/checkout/implementation/checkout/record-order.md"]}
    [commit] = report["repository"]["commits"]
    assert commit["subject"] == "inside the window"
    assert "delivery_root" in commit["files_by_root"] and "work_root" in commit["files_by_root"]


def test_provenance_is_complete_when_every_source_was_read(consumer):
    _, report = report_of(consumer)
    assert [p for p in report["provenance"] if p["unavailable"]] == []
    assert report["framework"]["version"] is not None
    assert "plan.json" in report["framework"]["contracts"]
    assert {a["name"] for a in report["framework"]["agents"]} >= {"execution-contract-binder"}
    assert any(s["name"] == "siegard-telemetry" for s in report["framework"]["skills"])


# ----------------------------------------------------------------------- the refusals


def test_a_second_report_under_one_stamp_is_refused(consumer):
    first, _ = report_of(consumer)
    assert first.returncode == 0
    before = (consumer["home"] / "telemetry" / f"{STAMP}.json").read_bytes()
    second, _ = report_of(consumer)
    assert second.returncode == 1
    assert "already exists" in second.stdout
    assert (consumer["home"] / "telemetry" / f"{STAMP}.json").read_bytes() == before


def test_no_telemetry_root_is_a_stop_with_the_declaration_ready(consumer):
    declared = json.loads((consumer["home"] / "siegard.json").read_text(encoding="utf-8"))
    del declared["telemetry_root"]
    (consumer["home"] / "siegard.json").write_text(json.dumps(declared), encoding="utf-8")
    done, report = report_of(consumer)
    assert done.returncode == 1
    assert report is None
    assert "declares no telemetry_root" in done.stdout
    assert "/siegard-config" in done.stdout


def test_an_unreadable_transcript_root_is_a_reason_not_a_zero(consumer):
    done = run(consumer["home"], "--since", SINCE, "--until", UNTIL,
               "--transcripts", consumer["tmp"] / "nowhere")
    assert done.returncode == 0, done.stdout + done.stderr
    report = json.loads((consumer["home"] / "telemetry" / f"{STAMP}.json").read_text())
    assert report["harness"]["readable"] is False
    assert report["agents"] == [] and report["commands"] == []
    unavailable = {p["section"]: p["unavailable"] for p in report["provenance"]}
    assert "is not a directory" in unavailable["agents"]
    assert "is not a directory" in unavailable["commands"]
    assert unavailable["runs"] is None
    assert "agents — " in done.stdout and "is not a directory" in done.stdout


def test_since_last_continues_from_the_previous_report(consumer):
    first, _ = report_of(consumer)
    assert first.returncode == 0
    done = run(consumer["home"], "--since", "last", "--until", "2026-08-20T14:00:00Z",
               "--transcripts", consumer["transcripts"])
    assert done.returncode == 0, done.stdout + done.stderr
    report = json.loads((consumer["home"] / "telemetry" / "20260820T140000Z.json").read_text())
    assert report["window"]["since"] == "2026-08-20T12:00:00.000Z"
    assert report["window"]["since_resolved_from"].endswith(f"{STAMP}.json")
    [session] = report["harness"]["sessions"]
    assert session["human_turns_in_window"] == ["2026-08-20T13:00:00.000Z"]


def test_since_last_with_no_previous_report_cannot_run(consumer):
    done = run(consumer["home"], "--since", "last", "--transcripts", consumer["transcripts"])
    assert done.returncode == 2
    assert "names no report" in done.stderr


def test_a_window_that_does_not_open_before_it_closes_cannot_run(consumer):
    done = run(consumer["home"], "--since", UNTIL, "--until", SINCE,
               "--transcripts", consumer["transcripts"])
    assert done.returncode == 2
    assert "is not before" in done.stderr


# --------------------------------------------------------------------------- the probe


def test_the_probe_says_what_would_be_read_and_writes_nothing(consumer):
    done = run("--probe", consumer["home"], "--since", SINCE, "--until", UNTIL,
               "--transcripts", consumer["transcripts"])
    assert done.returncode == 0, done.stdout + done.stderr
    assert not (consumer["home"] / "telemetry").exists()
    assert f"transcripts: {consumer['transcripts']} — readable" in done.stdout
    assert "sessions overlapping the window: 1" in done.stdout
    assert "s1: " in done.stdout and "1 human turns" in done.stdout
    assert "no message text" in done.stdout
    assert f"would write: {consumer['home'] / 'telemetry' / STAMP}.json" in done.stdout


def test_the_probe_names_an_unreadable_transcript_root(consumer):
    done = run("--probe", consumer["home"], "--since", SINCE,
               "--transcripts", consumer["tmp"] / "nowhere")
    assert done.returncode == 0
    assert "unavailable:" in done.stdout and "is not a directory" in done.stdout


# ---------------------------------------------------------------- sibling directories


def test_a_session_opened_in_a_subdirectory_is_read_from_its_sibling_directory(consumer):
    """The harness names the transcript directory by the working directory the session opened
    in, so a session started in `<project>/backend` lands beside the project's own directory.
    A neighbouring project whose name merely extends this one's is not read: the test plants
    both, and only the one whose recorded cwd sits under the project is counted."""
    home = consumer["home"]
    transcripts = consumer["transcripts"]
    sibling = transcripts.parent / f"{transcripts.name}-backend"
    sibling.mkdir()
    (sibling / "s2.jsonl").write_text(
        line(type="user", timestamp="2026-08-20T10:50:00.000Z", sessionId="s2",
             cwd=str(home / "backend"), message={"role": "user", "content": "from the backend"}),
        encoding="utf-8")
    neighbour = transcripts.parent / f"{transcripts.name}-old"
    neighbour.mkdir()
    (neighbour / "s3.jsonl").write_text(
        line(type="user", timestamp="2026-08-20T10:51:00.000Z", sessionId="s3",
             cwd=str(home) + "-old", message={"role": "user", "content": "another project"}),
        encoding="utf-8")
    probe = run("--probe", home, "--since", SINCE, "--until", UNTIL, "--transcripts", transcripts)
    assert "sessions overlapping the window: 2" in probe.stdout
    assert f"s2: 1 entries, 1 human turns, working directories {home / 'backend'}, from sibling " \
           f"directory {sibling}" in probe.stdout
    assert "s3" not in probe.stdout
    done, report = report_of(consumer)
    assert done.returncode == 0, done.stdout + done.stderr
    assert [s["id"] for s in report["harness"]["sessions"]] == ["s1", "s2"]
    assert report["harness"]["transcript_roots"] == [str(transcripts), str(sibling)]
    assert "1 sibling directory read" in done.stdout
