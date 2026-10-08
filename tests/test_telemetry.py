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

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator

REPO = Path(__file__).resolve().parent.parent
TELEMETRY = REPO / "src/claude/bin/telemetry.py"

SINCE = "2026-08-20T10:00:00Z"
UNTIL = "2026-08-20T12:00:00Z"
STAMP = "20260820T120000Z"


def run(*args: str, home: Path | None = None) -> subprocess.CompletedProcess:
    env = dict(os.environ, HOME=str(home)) if home is not None else None
    return subprocess.run([sys.executable, "-B", str(TELEMETRY), *map(str, args)],
                          capture_output=True, text=True, env=env)


def contract() -> Draft202012Validator:
    return Draft202012Validator(
        json.loads((REPO / "src/claude/schemas/telemetry.json").read_text(encoding="utf-8")))


def line(**entry) -> str:
    return json.dumps(entry) + "\n"


def assistant(stamp: str, *blocks: dict, session: str = "s1", usage: dict | None = None,
             **extra) -> str:
    message = {"role": "assistant", "content": list(blocks)}
    if usage is not None:
        message["usage"] = usage
    return line(type="assistant", timestamp=stamp, sessionId=session, cwd="/consumer",
                version="2.1.0", message=message, **extra)


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
    (spec_root / "domain/x").mkdir(parents=True)
    (spec_root / "domain/x/a.log.md").write_text(
        "---\nentries:\n- field: attributes\n  unstated: u\n  decided: d\n  why: w\n---\n",
        encoding="utf-8")

    def commit(message: str, when: str) -> None:
        subprocess.run(["git", "-C", str(home), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(home), "-c", f"user.email=t@example.com",
                        "-c", "user.name=t", "commit", "-q", "-m", message, "--date", when],
                       check=True, env={"GIT_COMMITTER_DATE": when, "PATH": "/usr/bin:/bin",
                                        "HOME": str(tmp_path)})

    commit("before the window", "2026-08-20T09:00:00Z")

    (spec_root / "domain/x/b.log.md").write_text(
        "---\nentries:\n- field: attributes\n  unstated: second\n  decided: e\n  why: v\n---\n",
        encoding="utf-8")
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
            "type": "tool_use", "id": "tu-ls", "name": "Bash", "input": {"command": "ls"}},
            usage={"input_tokens": 20, "cache_creation_input_tokens": 0,
                   "cache_read_input_tokens": 0, "output_tokens": 5})
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
            "input": {"command": "cd x && python3 -B /plugin/bin/deliver.py d w t s"}},
            usage={"input_tokens": 30, "cache_creation_input_tokens": 0,
                   "cache_read_input_tokens": 0, "output_tokens": 8})
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
    # The second spawn has no meta file: null usage and a stated reason. It shares the first's
    # description and not its prompt, and a description is free text: not a repeat.
    assert second["usage"] is None
    assert "names tool use tu-agent-2" in second["unavailable"]
    assert second["repeats_earlier"] is False
    totals = report["agent_totals"]
    assert totals["overall"]["invocations"] == 2
    assert totals["overall"]["repeats"] == 0
    assert totals["overall"]["with_transcript"] == 1
    assert totals["overall"]["usage"]["output_tokens"] == 500
    assert totals["by_type"]["execution-contract-binder"]["duration_seconds"] == 268.0


def test_a_repeat_is_the_same_prompt_handed_to_the_same_agent_type(consumer):
    """A re-run hands the same prompt again, under whatever description the session composes
    for it; the description is free text and decides nothing. Each row carries the prompt's
    digest — never its text — and the totals count the rows handed a prompt already handed."""
    session = consumer["transcripts"] / "s1.jsonl"
    session.write_text(session.read_text(encoding="utf-8")
                       + assistant("2026-08-20T10:45:00.000Z", {
                           "type": "tool_use", "id": "tu-agent-3", "name": "Agent",
                           "input": {"subagent_type": "execution-contract-binder",
                                     "description": "Bind record-order (round 2)",
                                     "prompt": "secret prompt text"}})
                       + assistant("2026-08-20T10:46:00.000Z", {
                           "type": "tool_use", "id": "tu-agent-4", "name": "Agent",
                           "input": {"subagent_type": "test-author",
                                     "description": "Bind record-order",
                                     "prompt": "secret prompt text"}}),
                       encoding="utf-8")
    done, report = report_of(consumer)
    assert done.returncode == 0, done.stdout + done.stderr
    assert [e.message for e in contract().iter_errors(report)] == []
    rows = {a["tool_use_id"]: a for a in report["agents"]}
    digest = hashlib.sha256("secret prompt text".encode("utf-8")).hexdigest()
    assert rows["tu-agent-1"]["prompt_sha256"] == digest
    assert rows["tu-agent-3"]["prompt_sha256"] == digest
    assert rows["tu-agent-2"]["prompt_sha256"] == hashlib.sha256(b"again").hexdigest()
    assert [rows[k]["repeats_earlier"] for k in ("tu-agent-1", "tu-agent-2", "tu-agent-3",
                                                 "tu-agent-4")] == [False, False, True, False], \
        "the same prompt again under another description repeats; the same prompt under " \
        "another agent type does not"
    totals = report["agent_totals"]
    assert totals["by_type"]["execution-contract-binder"]["repeats"] == 1
    assert totals["by_type"]["test-author"]["repeats"] == 0
    assert totals["overall"]["repeats"] == 1
    assert "1 repeating an earlier prompt" in done.stdout
    assert "secret prompt text" not in json.dumps(report)


def test_an_agent_spawned_by_an_agent_is_a_row_of_its_own_under_its_parent(consumer):
    """A skill invoked inside a spawned context — a fork the session launched to run
    `/implement-task` in the background — spawns this framework's agents from there, and the
    harness writes their transcripts beside the fork's, one depth further down. A report that
    read only the session's own spawns would carry the fork and miss what it spawned: the
    named agents' cost would be nowhere, not folded into the fork's row, and `agent_totals`
    would be a floor with `provenance` saying nothing. Each depth is read from the transcript
    above it, and every row's usage is its own turns alone, so the rows sum without overlap."""
    session = consumer["transcripts"] / "s1.jsonl"
    session.write_text(session.read_text(encoding="utf-8") + assistant(
        "2026-08-20T10:30:00.000Z", {
            "type": "tool_use", "id": "tu-fork", "name": "Agent",
            "input": {"subagent_type": "fork", "description": "Deliver record-order",
                      "prompt": "run /implement-task"}})
        + user_result("2026-08-20T10:30:01.000Z", "tu-fork", "launched",
                      {"agentId": "f1", "status": "async_launched"}), encoding="utf-8")
    subagents = consumer["transcripts"] / "s1" / "subagents"
    (subagents / "agent-f1.meta.json").write_text(json.dumps({
        "agentType": "fork", "isFork": True, "description": "Deliver record-order",
        "toolUseId": "tu-fork", "spawnDepth": 1}), encoding="utf-8")
    spend = {"input_tokens": 1, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0,
             "output_tokens": 7}
    (subagents / "agent-f1.jsonl").write_text(
        # A fork opens with a copy of the context it was forked from — here the session's own
        # spawn of a1 — which is the session's spawn and never a second row under the fork.
        line(type="assistant", timestamp="2026-08-20T10:08:00.000Z", agentId="f1",
             message={"role": "assistant", "content": [{
                 "type": "tool_use", "id": "tu-agent-1", "name": "Agent",
                 "input": {"subagent_type": "execution-contract-binder",
                           "description": "Bind record-order"}}]})
        + line(type="assistant", timestamp="2026-08-20T10:31:00.000Z", agentId="f1",
             message={"role": "assistant", "model": "claude-opus-5", "usage": spend,
                      "content": [{"type": "tool_use", "id": "tu-nested", "name": "Agent",
                                   "input": {"subagent_type": "siegard:task-implementer",
                                             "description": "Implement record-order",
                                             "prompt": "nested prompt text"}}]})
        + line(type="user", timestamp="2026-08-20T10:31:01.000Z", agentId="f1",
               message={"role": "user", "content": [
                   {"type": "tool_result", "tool_use_id": "tu-nested", "content": "done"}]},
               toolUseResult={"agentId": "n1", "resolvedModel": "claude-sonnet-5"})
        + line(type="assistant", timestamp="2026-08-20T10:45:00.000Z", agentId="f1",
               message={"role": "assistant", "model": "claude-opus-5", "usage": spend,
                        "content": [{"type": "text", "text": "delivered"}]}),
        encoding="utf-8")
    (subagents / "agent-n1.meta.json").write_text(json.dumps({
        "agentType": "siegard:task-implementer", "description": "Implement record-order",
        "toolUseId": "tu-nested", "parentAgentId": "f1", "spawnDepth": 2}), encoding="utf-8")
    (subagents / "agent-n1.jsonl").write_text(
        line(type="assistant", timestamp="2026-08-20T10:32:00.000Z", agentId="n1",
             message={"role": "assistant", "model": "claude-sonnet-5",
                      "content": [{"type": "text", "text": "written"}],
                      "usage": {"input_tokens": 3, "cache_creation_input_tokens": 0,
                                "cache_read_input_tokens": 0, "output_tokens": 300}}),
        encoding="utf-8")
    done, report = report_of(consumer)
    assert [e.message for e in contract().iter_errors(report)] == []
    by_id = {a["agent_id"]: a for a in report["agents"]}
    fork, nested = by_id["f1"], by_id["n1"]
    assert fork["spawn_depth"] == 1 and fork["parent_agent_id"] is None
    assert nested["spawn_depth"] == 2 and nested["parent_agent_id"] == "f1"
    assert nested["session"] == "s1" and nested["invoked_at"] == "2026-08-20T10:31:00.000Z"
    assert nested["agent_type"] == "task-implementer"
    assert nested["model"] == "claude-sonnet-5"
    assert nested["usage"]["output_tokens"] == 300
    assert fork["usage"]["output_tokens"] == 14, "a parent's row is its own turns alone"
    assert by_id["a1"]["spawn_depth"] == 1 and by_id["a1"]["parent_agent_id"] is None
    assert [a["tool_use_id"] for a in report["agents"]].count("tu-agent-1") == 1
    totals = report["agent_totals"]
    assert totals["overall"]["invocations"] == 4
    assert totals["overall"]["usage"]["output_tokens"] == 500 + 14 + 300
    assert totals["by_type"]["task-implementer"]["usage"]["output_tokens"] == 300
    assert totals["by_type"]["fork"]["usage"]["output_tokens"] == 14
    assert "agents: 4 spawned (1 of them by another agent)" in done.stdout
    assert "nested prompt text" not in json.dumps(report)


def test_an_agent_without_a_transcript_says_its_spawns_are_uncounted(consumer):
    _, report = report_of(consumer)
    _, second = report["agents"]
    assert second["usage"] is None
    assert "whatever this agent spawned is uncounted" in second["unavailable"]


def test_a_framework_script_is_recognised_by_its_file_name_however_its_path_is_spelled():
    """The skills spell an invocation `${CLAUDE_PLUGIN_ROOT}/bin/<script>.py`, and a session
    that shortens it — `B=<plugin>/bin; python3 -B $B/deliver.py` — has still invoked the
    script. A match anchored on the literal `bin/` segment drops that form, and the commands
    section becomes a floor nothing in `provenance` announces."""
    import telemetry
    call = telemetry.SCRIPT_CALL
    assert call.findall("B=/p/bin; python3 -B $B/deliver.py d w t s") == ["deliver.py"]
    assert call.findall("python3 -B /plugin/bin/plan.py --check w s") == ["plan.py"]
    assert call.findall("cd t && python3 -B ./trace.py --check .") == ["trace.py"]
    assert call.findall("python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/run.py x") == ["run.py"]
    assert call.findall("python3 my-deliver.py; cat deliver.pyc; ls bin/") == []


def test_a_scoped_spawn_normalizes_to_the_plugin_agents_bare_name():
    """Skills spawn this framework's own agents by their plugin-scoped name
    (`siegard:execution-contract-binder`), never the bare form a consumer's own
    `.claude/agents/` could shadow — so the harness records that scoped string as
    `subagent_type`, and a report keyed on it would split one agent into two `by_type`
    buckets depending on which spelling a session happened to use. The namespace to strip is
    read from `plugin.json`'s own `name`, never restated as a literal here."""
    import telemetry
    assert telemetry.agent_type_of({"subagent_type": "siegard:execution-contract-binder"}) \
        == "execution-contract-binder"
    assert telemetry.agent_type_of({"subagent_type": "execution-contract-binder"}) \
        == "execution-contract-binder"
    # A different plugin's own namespace is never this framework's to strip.
    assert telemetry.agent_type_of({"subagent_type": "other-plugin:reviewer"}) \
        == "other-plugin:reviewer"
    assert telemetry.agent_type_of({}) == "general-purpose"


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
    logs = {entry["path"]: entry["baseline"] for entry in report["decisions"]["log"]}
    assert logs["specification/domain/x/a.log.md"].startswith("commit ")
    assert logs["specification/domain/x/b.log.md"].startswith("no commit before")
    assert report["decisions"]["baseline"].startswith("2 log(s) read, 1 with a commit before")
    assert [e["unstated"] for e in report["decisions"]["added"]] == ["second"]
    assert [e["node"] for e in report["decisions"]["added"]] == ["domain/x/b"], \
        "each added entry names the node its log sits beside; the file never carries it"


def test_a_retirement_is_listed_apart_and_never_followed_as_a_decision(consumer):
    """A retirement says where an earlier decision went when its node left; it decides nothing,
    so it is neither counted with the decisions nor followed to a field that is gone."""
    log = consumer["home"] / "specification" / "domain/x/b.log.md"
    closing = "---\n"
    text = log.read_text(encoding="utf-8")
    assert text.endswith(closing)
    log.write_text(text[:-len(closing)] + "- field: attributes\n"
                   "  retired: held nowhere; the element left the specification\n" + closing,
                   encoding="utf-8")
    home = consumer["home"]
    subprocess.run(["git", "-C", str(home), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(home), "-c", "user.email=t@example.com", "-c", "user.name=t",
                    "commit", "-q", "-m", "retire", "--date", "2026-08-20T11:30:00Z"], check=True,
                   env={"GIT_COMMITTER_DATE": "2026-08-20T11:30:00Z", "PATH": "/usr/bin:/bin",
                        "HOME": str(consumer["tmp"])})
    done, report = report_of(consumer)
    assert done.returncode == 0, done.stdout + done.stderr
    assert report["contract_version"] == "siegard-telemetry/12"
    assert [e.get("unstated") for e in report["decisions"]["added"]] == ["second"]
    assert [e["retired"] for e in report["decisions"]["retired"]] == [
        "held nowhere; the element left the specification"]
    assert "1 location(s) retired" in done.stdout


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


def test_since_last_reads_the_window_of_a_report_under_an_earlier_contract(consumer):
    """`last` is the `until` of the newest report on disk, whatever contract it was written
    under: an earlier report is read for its window and never held to the current schema."""
    telemetry = consumer["home"] / "telemetry"
    telemetry.mkdir()
    (telemetry / "20260820T110000Z.json").write_text(json.dumps({
        "contract_version": "siegard-telemetry/11",
        "window": {"since": "2026-08-20T10:00:00.000Z", "until": "2026-08-20T11:00:00.000Z",
                   "since_resolved_from": "named"}}), encoding="utf-8")
    done = run(consumer["home"], "--since", "last", "--until", UNTIL,
               "--transcripts", consumer["transcripts"])
    assert done.returncode == 0, done.stdout + done.stderr
    report = json.loads((telemetry / f"{STAMP}.json").read_text(encoding="utf-8"))
    assert report["window"]["since"] == "2026-08-20T11:00:00.000Z"
    assert report["window"]["since_resolved_from"].endswith("20260820T110000Z.json")


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


def test_a_transcript_whose_entries_carry_other_keys_is_unreadable_not_zero(consumer):
    """A harness that renamed the keys this reader counts leaves files that parse cleanly and
    count as nothing; the probe says so rather than letting the report read zero sessions as
    complete."""
    renamed = consumer["tmp"] / "renamed"
    renamed.mkdir()
    (renamed / "s9.jsonl").write_text(
        line(kind="user", time="2026-08-20T10:05:00.000Z", sessionId="s9", cwd="/consumer",
             body={"role": "user", "content": "go on"}), encoding="utf-8")
    probe = run("--probe", consumer["home"], "--since", SINCE, "--until", UNTIL,
                "--transcripts", renamed)
    assert "no entry carries the keys this reader counts: type, timestamp, message" in probe.stdout
    done = run(consumer["home"], "--since", SINCE, "--until", UNTIL, "--transcripts", renamed)
    assert done.returncode == 0, done.stdout + done.stderr
    report = json.loads((consumer["home"] / "telemetry" / f"{STAMP}.json").read_text())
    assert report["harness"]["readable"] is False
    unavailable = {p["section"]: p["unavailable"] for p in report["provenance"]}
    assert "no entry carries the keys" in unavailable["agents"]


def test_the_probe_announces_a_worktree_sited_outside_the_tree(consumer):
    """A session opened in a worktree outside the project's own tree — the parallel-frontier
    route's `../wt-<task>` — transcribes under a harness directory the probe never lists, so the
    probe announces such worktrees with the `--transcripts` door. A worktree inside the tree is
    not announced: its sessions record a cwd under the toplevel, which the sibling reading
    already reaches."""
    home = consumer["home"]
    before = run("--probe", home, "--since", SINCE, "--until", UNTIL,
                 "--transcripts", consumer["transcripts"])
    assert "worktree outside this tree" not in before.stdout
    outside = consumer["tmp"] / "wt-record-order"
    subprocess.run(["git", "-C", str(home), "worktree", "add", str(outside)],
                   check=True, capture_output=True)
    inside = home / ".claude" / "worktrees" / "wt-inside"
    subprocess.run(["git", "-C", str(home), "worktree", "add", str(inside)],
                   check=True, capture_output=True)
    done = run("--probe", home, "--since", SINCE, "--until", UNTIL,
               "--transcripts", consumer["transcripts"])
    assert done.returncode == 0, done.stdout + done.stderr
    assert f"worktree outside this tree: {outside}" in done.stdout
    assert "point --transcripts at it for that slice" in done.stdout
    assert str(inside) not in done.stdout


def linked_worktree(consumer: dict) -> Path:
    home = consumer["home"]
    worktree = home / ".claude" / "worktrees" / "x"
    subprocess.run(["git", "-C", str(home), "worktree", "add", str(worktree)],
                   check=True, capture_output=True)
    return worktree


def test_the_transcript_directory_is_keyed_by_the_main_tree_from_inside_a_worktree(consumer):
    """The harness keeps a session that entered a linked worktree under the main tree's
    directory, so the directory a report reads is derived from the main toplevel whichever tree
    it is run from; outside any repository the directory itself is the key."""
    import telemetry
    home = consumer["home"]
    worktree = linked_worktree(consumer)
    assert telemetry.main_toplevel_of(worktree) == home
    assert telemetry.main_toplevel_of(home) == home
    assert telemetry.worktree_of(telemetry.toplevel_of(worktree), home) == str(worktree)
    assert telemetry.worktree_of(home, home) is None
    assert telemetry.transcript_root_for(home, None) == telemetry.transcript_root_for(
        telemetry.main_toplevel_of(worktree), None)
    plain = consumer["tmp"] / "plain"
    plain.mkdir()
    assert telemetry.main_toplevel_of(plain) == plain
    assert telemetry.worktree_of(telemetry.toplevel_of(plain), telemetry.main_toplevel_of(plain)) \
        is None


def test_a_report_from_a_worktree_reads_only_the_sessions_that_reached_it(consumer):
    """Under the main tree's harness directory sit the main tree's sessions and every linked
    worktree's. A report run inside a worktree admits a session only where one of its working
    directories reaches the worktree, and names the worktree; the main tree's report reads them
    all and names none. The harness directory is the one `HOME` resolves to, so the fixture
    plants it under a home of its own and the script is run with `--transcripts` unset."""
    import telemetry
    home = consumer["home"]
    worktree = linked_worktree(consumer)
    fake_home = consumer["tmp"] / "fakehome"
    projects = fake_home / ".claude" / "projects"
    encoded = projects / telemetry.transcript_root_for(home, None).name
    encoded.mkdir(parents=True)
    (encoded / "w1.jsonl").write_text(
        line(type="user", timestamp="2026-08-20T10:50:00.000Z", sessionId="w1", cwd=str(home),
             message={"role": "user", "content": "opened in the main tree"})
        + line(type="user", timestamp="2026-08-20T10:51:00.000Z", sessionId="w1",
               cwd=str(worktree), message={"role": "user", "content": "entered the worktree"}),
        encoding="utf-8")
    (encoded / "m1.jsonl").write_text(
        line(type="user", timestamp="2026-08-20T10:52:00.000Z", sessionId="m1", cwd=str(home),
             message={"role": "user", "content": "stayed in the main tree"}),
        encoding="utf-8")

    probe = run("--probe", worktree, "--since", SINCE, "--until", UNTIL, home=fake_home)
    assert probe.returncode == 0, probe.stdout + probe.stderr
    assert f"transcripts: {encoded} — readable" in probe.stdout
    assert f"worktree: {worktree}" in probe.stdout
    assert "worktree outside this tree" not in probe.stdout
    assert "sessions overlapping the window: 1" in probe.stdout and "w1: " in probe.stdout

    done = run(worktree, "--since", SINCE, "--until", UNTIL, home=fake_home)
    assert done.returncode == 0, done.stdout + done.stderr
    report = json.loads((worktree / "telemetry" / f"{STAMP}.json").read_text(encoding="utf-8"))
    assert [e.message for e in contract().iter_errors(report)] == []
    assert report["harness"]["transcript_root"] == str(encoded)
    assert report["harness"]["worktree"] == str(worktree)
    assert [s["id"] for s in report["harness"]["sessions"]] == ["w1"]

    done = run(home, "--since", SINCE, "--until", UNTIL, home=fake_home)
    assert done.returncode == 0, done.stdout + done.stderr
    report = json.loads((home / "telemetry" / f"{STAMP}.json").read_text(encoding="utf-8"))
    assert report["harness"]["worktree"] is None
    assert [s["id"] for s in report["harness"]["sessions"]] == ["m1", "w1"]


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
    assert report["harness"]["worktree"] is None
    assert "1 sibling directory read" in done.stdout


def test_session_usage_sums_only_its_own_turns_inside_the_window(consumer):
    """The tokens the main session's own turns spent, distinct from what its subagents spent —
    the half `agent_totals` alone never carried."""
    _, report = report_of(consumer)
    sessions = report["harness"]["sessions"]
    assert len(sessions) == 1
    assert sessions[0]["usage"] == {"input_tokens": 50, "cache_creation_input_tokens": 0,
                                    "cache_read_input_tokens": 0, "output_tokens": 13}


def split(stamp: str, message_id: str, blocks: list[dict], final_output: int,
          **extra) -> str:
    """One assistant message as the harness transcribes it: one entry per content block, every
    entry carrying the message's usage, `output_tokens` reaching its final value on the last."""
    written = ""
    for at, block in enumerate(blocks):
        last = at == len(blocks) - 1
        written += line(type="assistant", timestamp=stamp, message={
            "id": message_id, "role": "assistant", "model": "claude-opus-5", "content": [block],
            "usage": {"input_tokens": 7, "cache_creation_input_tokens": 100,
                      "cache_read_input_tokens": 1000,
                      "output_tokens": final_output if last else 1}}, **extra)
    return written


def test_a_message_transcribed_as_several_entries_is_counted_once(consumer):
    session = consumer["transcripts"] / "s1.jsonl"
    session.write_text(session.read_text(encoding="utf-8")
                       + split("2026-08-20T10:50:00.000Z", "m-split",
                               [{"type": "thinking", "thinking": ""},
                                {"type": "text", "text": "t"},
                                {"type": "tool_use", "id": "tu-x", "name": "Read", "input": {}}],
                               40, sessionId="s1", cwd="/consumer", version="2.1.0"),
                       encoding="utf-8")
    agent = consumer["transcripts"] / "s1" / "subagents" / "agent-a1.jsonl"
    agent.write_text(agent.read_text(encoding="utf-8")
                     + split("2026-08-20T10:12:40.000Z", "m-agent",
                             [{"type": "text", "text": "a"}, {"type": "text", "text": "b"}],
                             60, isSidechain=True, agentId="a1"),
                     encoding="utf-8")
    _, report = report_of(consumer)
    assert report["contract_version"] == "siegard-telemetry/12"
    assert report["harness"]["sessions"][0]["usage"] == {
        "input_tokens": 57, "cache_creation_input_tokens": 100,
        "cache_read_input_tokens": 1000, "output_tokens": 53}
    row = next(a for a in report["agents"] if a["tool_use_id"] == "tu-agent-1")
    assert row["usage"] == {"input_tokens": 22, "cache_creation_input_tokens": 200,
                            "cache_read_input_tokens": 4000, "output_tokens": 560}
    assert row["messages"] == 3


def test_distinct_messages_are_each_counted(consumer):
    session = consumer["transcripts"] / "s1.jsonl"
    extra = "".join(split(f"2026-08-20T10:5{n}:00.000Z", f"m-{n}",
                          [{"type": "text", "text": "t"}], 40,
                          sessionId="s1", cwd="/consumer", version="2.1.0") for n in range(3))
    session.write_text(session.read_text(encoding="utf-8") + extra, encoding="utf-8")
    _, report = report_of(consumer)
    assert report["harness"]["sessions"][0]["usage"] == {
        "input_tokens": 50 + 21, "cache_creation_input_tokens": 300,
        "cache_read_input_tokens": 3000, "output_tokens": 13 + 120}


def test_the_receipt_prints_session_tokens_separately_from_agent_tokens(consumer):
    done, _ = report_of(consumer)
    assert "sessions: 1 orchestrating, 13 output tokens" in done.stdout
    assert "500 output tokens" in done.stdout, "the agents line should be unaffected"


# ------------------------------------------------ decisions followed to their nodes


def committed(home: Path, message: str, when: str) -> None:
    subprocess.run(["git", "-C", str(home), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(home), "-c", "user.email=t@example.com", "-c", "user.name=t",
                    "commit", "-q", "-m", message, "--date", when], check=True,
                   env={"GIT_COMMITTER_DATE": when, "PATH": "/usr/bin:/bin",
                        "HOME": str(home.parent)})


def node_at(home: Path, rel: str, attributes: list[dict]) -> None:
    path = home / "specification" / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("---\n" + yaml.safe_dump({"type": "value-object", "attributes": attributes},
                                                sort_keys=False) + "---\n## Description\nProse.\n",
                    encoding="utf-8")


def decided(home: Path, node: str, unstated: str, value: str, field: str = "attributes") -> None:
    """Append one decided entry to the log beside `node`, the way `spec.py --decide` lays it out:
    one block per entry, every scalar on one line, no body."""
    log = home / "specification" / f"{node}.log.md"
    block = yaml.safe_dump([{"field": field, "unstated": unstated, "decided": value,
                             "why": "money is decimal"}], sort_keys=False, width=float("inf"))
    if log.is_file():
        text = log.read_text(encoding="utf-8")
        log.write_text(text[:-len("---\n")] + block + "---\n", encoding="utf-8")
    else:
        log.write_text(f"---\nentries:\n{block}---\n", encoding="utf-8")


def test_a_decision_is_followed_to_the_field_it_filled(consumer):
    """The log records what the framework decided on the human's behalf; nothing recorded whether
    anyone read it. The node the decision located records what stands — so the outcome is read
    there: the field as the landing commit wrote it against the field today, never the log's
    paraphrase — and every later commit that changed it, with its route."""
    home = consumer["home"]
    node_at(home, "domain/x/c.md", [{"name": "total", "type": "decimal", "required": True}])
    decided(home, "domain/x/c", "whether the total is decimal", "total is carried as decimal")
    node_at(home, "domain/x/d.md", [{"name": "code", "type": "string", "required": True}])
    decided(home, "domain/x/d", "whether a code is a string", "code is carried as a string")
    committed(home, "deliver-scope pricing: plan", "2026-08-20T11:10:00Z")
    node_at(home, "domain/x/c.md", [{"name": "total", "type": "integer", "required": True}])
    committed(home, "deliver-scope corrective-increment-total: plan", "2026-08-20T11:30:00Z")

    _, report = report_of(consumer)
    by = {e["unstated"]: e["outcome"] for e in report["decisions"]["added"]}
    revised = by["whether the total is decimal"]
    assert revised["state"] == "revised", revised
    assert revised["landed"]["commit"] and revised["landed"]["at"].startswith("2026-08-20T11:10")
    assert [r["route"] for r in revised["revised_by"]] == ["corrective"]
    assert "corrective-increment" in revised["revised_by"][0]["subject"]
    assert 0 < revised["days_to_first_revision"] < 0.02
    assert revised["value_now"][0]["type"] == "integer"
    assert by["whether a code is a string"]["state"] == "stands"
    # the fixture's own second decision locates a node that never existed
    assert by["second"]["state"] == "unreadable"
    tally = report["decisions"]["outcomes"]
    assert tally["states"]["revised"] == 1 and tally["states"]["stands"] == 1
    assert tally["first_revision_by_route"]["corrective"] == 1
    assert "a person routing the correction" in tally["route_meanings"]["corrective"]
    assert "the framework re-authoring the field" in tally["route_meanings"]["framework"]
    assert "rests on the slug's words" in tally["route_meanings"]["corrective"]


def test_a_delivery_naming_no_correction_is_the_framework_revising_itself(consumer):
    home = consumer["home"]
    node_at(home, "domain/x/c.md", [{"name": "total", "type": "decimal", "required": True}])
    decided(home, "domain/x/c", "whether the total is decimal", "total is carried as decimal")
    committed(home, "deliver-scope pricing: plan", "2026-08-20T11:10:00Z")
    node_at(home, "domain/x/c.md", [{"name": "total", "type": "money", "required": True}])
    committed(home, "deliver-scope invoicing: plan", "2026-08-20T11:40:00Z")
    _, report = report_of(consumer)
    outcome = next(e["outcome"] for e in report["decisions"]["added"]
                   if e["unstated"] == "whether the total is decimal")
    assert outcome["state"] == "revised" and outcome["revised_by"][0]["route"] == "framework"
    assert report["decisions"]["outcomes"]["first_revision_by_route"] == {
        "corrective": 0, "framework": 1, "hand-edit": 0}


def test_a_commit_no_skill_wrote_is_a_hand_edit(consumer):
    home = consumer["home"]
    node_at(home, "domain/x/c.md", [{"name": "total", "type": "decimal", "required": True}])
    decided(home, "domain/x/c", "whether the total is decimal", "total is carried as decimal")
    committed(home, "deliver-scope pricing: plan", "2026-08-20T11:10:00Z")
    node_at(home, "domain/x/c.md", [{"name": "total", "type": "integer", "required": True}])
    committed(home, "total must be an integer, finance said so", "2026-08-20T11:50:00Z")
    _, report = report_of(consumer)
    outcome = next(e["outcome"] for e in report["decisions"]["added"]
                   if e["unstated"] == "whether the total is decimal")
    assert outcome["revised_by"][0]["route"] == "hand-edit"


def test_only_the_subject_a_shipped_skill_writes_is_a_framework_route():
    """`/deliver-scope` is the one entry point that commits; a subject opened by any other
    skill's name is a convention nothing ships, and reads as what it is — a person's commit."""
    import telemetry
    assert telemetry.route_of("deliver-scope pricing: deliver task/x/total") == "framework"
    assert telemetry.route_of("deliver-scope hotfix-total: review") == "corrective"
    assert telemetry.route_of("plan-work: corrective increment over the total") == "hand-edit"
    assert telemetry.route_of("analyse: re-decide the total") == "hand-edit"


def test_a_decision_committed_after_the_window_closes_is_not_counted(consumer):
    """The log is read as it stood at the last commit at or before `--until`, not as the working
    tree holds it now, and a revision committed after the close is not one the window saw."""
    home = consumer["home"]
    node_at(home, "domain/x/c.md", [{"name": "total", "type": "decimal", "required": True}])
    decided(home, "domain/x/c", "whether the total is decimal", "total is carried as decimal")
    committed(home, "deliver-scope pricing: plan", "2026-08-20T11:10:00Z")
    node_at(home, "domain/x/c.md", [{"name": "total", "type": "integer", "required": True}])
    committed(home, "total must be an integer", "2026-08-20T11:50:00Z")
    decided(home, "domain/x/c", "whether the code is a string", "code is a string")
    committed(home, "a later decision", "2026-08-20T11:55:00Z")

    early = run(home, "--since", SINCE, "--until", "2026-08-20T11:05:00Z",
                "--transcripts", consumer["transcripts"])
    assert early.returncode == 0, early.stdout + early.stderr
    report = json.loads((home / "telemetry" / "20260820T110500Z.json").read_text())
    assert [e["unstated"] for e in report["decisions"]["added"]] == ["second"]
    assert report["decisions"]["total_now"] == 2

    middle = run(home, "--since", SINCE, "--until", "2026-08-20T11:30:00Z",
                 "--transcripts", consumer["transcripts"])
    assert middle.returncode == 0, middle.stdout + middle.stderr
    report = json.loads((home / "telemetry" / "20260820T113000Z.json").read_text())
    by = {e["unstated"]: e["outcome"] for e in report["decisions"]["added"]}
    assert "whether the code is a string" not in by
    assert by["whether the total is decimal"]["state"] == "stands"
    assert by["whether the total is decimal"]["revised_by"] == []


def test_a_decision_lands_on_the_exact_commit_without_a_text_search(consumer):
    """A /7 report found an entry's landing by searching the log's history for sixty characters
    of its text, and found nothing for an entry whose text wrapped across lines. The landing is
    now the first commit of the node's own log whose entries contain the entry."""
    home = consumer["home"]
    node_at(home, "domain/x/c.md", [{"name": "total", "type": "decimal", "required": True}])
    decided(home, "domain/x/c", "whether the total,\nwhich the material shows in two currencies,\n"
            "is carried as one decimal or as a money value with its own currency", "decimal")
    committed(home, "deliver-scope pricing: plan", "2026-08-20T11:10:00Z")
    _, report = report_of(consumer)
    outcome = next(e["outcome"] for e in report["decisions"]["added"]
                   if e["node"] == "domain/x/c")
    assert outcome["state"] == "stands", outcome
    assert outcome["landed"]["at"].startswith("2026-08-20T11:10")


def test_a_log_that_moved_with_its_node_is_followed(consumer):
    """A log moves with its node and no entry records the move; following the one path through
    its renames is what finds the landing commit under the node's old name."""
    home = consumer["home"]
    node_at(home, "domain/x/c.md", [{"name": "total", "type": "decimal", "required": True}])
    decided(home, "domain/x/c", "whether the total is decimal", "total is carried as decimal")
    committed(home, "deliver-scope pricing: plan", "2026-08-20T11:10:00Z")
    for name in ("c.md", "c.log.md"):
        subprocess.run(["git", "-C", str(home), "mv", f"specification/domain/x/{name}",
                        f"specification/domain/x/{name.replace('c.', 'charge.', 1)}"],
                       check=True)
    committed(home, "analyse: rename c to charge", "2026-08-20T11:20:00Z")
    _, report = report_of(consumer)
    outcome = next(e["outcome"] for e in report["decisions"]["added"]
                   if e["node"] == "domain/x/charge")
    assert outcome["state"] == "stands", outcome
    assert outcome["landed"]["at"].startswith("2026-08-20T11:10")


def test_a_field_spelled_through_a_list_by_name_is_read_to_the_item(consumer):
    """`attributes.total.type` is how a log entry names an attribute's type (SPEC-002 names list
    items by `name`); a reader that only indexed lists by number called every such decision
    `unreadable`, and the outcome metric R10 promises stopped at the list."""
    home = consumer["home"]
    node_at(home, "domain/x/c.md", [{"name": "total", "type": "decimal", "required": True},
                                    {"name": "code", "type": "string", "required": True}])
    decided(home, "domain/x/c", "whether the total is decimal", "decimal",
            field="attributes.total.type")
    committed(home, "deliver-scope pricing: plan", "2026-08-20T11:10:00Z")
    _, report = report_of(consumer)
    outcome = next(e["outcome"] for e in report["decisions"]["added"]
                   if e["node"] == "domain/x/c")
    assert outcome["state"] == "stands" and outcome["value_now"] == "decimal", outcome
    node_at(home, "domain/x/c.md", [{"name": "total", "type": "integer", "required": True},
                                    {"name": "code", "type": "string", "required": True}])
    committed(home, "total must be an integer", "2026-08-20T11:50:00Z")
    (home / "telemetry" / f"{STAMP}.json").unlink()
    _, report = report_of(consumer)
    outcome = next(e["outcome"] for e in report["decisions"]["added"]
                   if e["node"] == "domain/x/c")
    assert outcome["state"] == "revised" and outcome["value_now"] == "integer", outcome
    import telemetry
    assert telemetry.field_of({"attributes": [{"name": "a"}, {"name": "a"}]},
                              "attributes.a") == (False, None), "two items under one name"
    assert telemetry.field_of({"attributes": [{"name": "a"}]}, "attributes.b") == (False, None)
    answers = {"answers": [{"operation": "send-message", "accepted": "the turn"},
                           {"operation": "list", "accepted": "the page"}]}
    assert telemetry.field_of(answers, "answers.send-message.accepted") == (True, "the turn"), \
        "a contract keys each answer by its operation, and a log entry spells it that way"
    assert telemetry.field_of(answers, "answers.1.accepted") == (True, "the page")


def test_an_entry_in_no_commit_yet_is_unlocated(consumer):
    home = consumer["home"]
    node_at(home, "domain/x/c.md", [{"name": "total", "type": "decimal", "required": True}])
    decided(home, "domain/x/c", "whether the total is decimal", "total is carried as decimal")
    _, report = report_of(consumer)
    outcome = next(e["outcome"] for e in report["decisions"]["added"]
                   if e["node"] == "domain/x/c")
    assert outcome["state"] == "unlocated" and outcome["landed"] is None
    assert "working tree only" in report["decisions"]["outcomes"]["state_meanings"]["unlocated"]


# ------------------------------------------- the session's cost by the skill it ran


def test_session_turns_are_attributed_to_the_skill_they_ran_under(consumer):
    """A Skill call names what the session runs from there to the next one; the person's own turns
    inside the span count toward it, so every figure is a ceiling per skill, said as one. The
    plugin's own namespace is stripped so `siegard:plan-work` and `plan-work` are one row."""
    second = consumer["transcripts"] / "s2.jsonl"
    second.write_text(
        human("2026-08-20T10:05:00.000Z")
        + assistant("2026-08-20T10:05:30.000Z", {"type": "text", "text": "reading"}, session="s2",
                    usage={"input_tokens": 1, "cache_creation_input_tokens": 0,
                           "cache_read_input_tokens": 0, "output_tokens": 3})
        + assistant("2026-08-20T10:06:00.000Z", {"type": "tool_use", "id": "sk-1", "name": "Skill",
                                                  "input": {"skill": "siegard:plan-work"}},
                    session="s2", usage={"input_tokens": 1, "cache_creation_input_tokens": 0,
                                         "cache_read_input_tokens": 0, "output_tokens": 5})
        + assistant("2026-08-20T10:07:00.000Z", {"type": "text", "text": "planning"}, session="s2",
                    usage={"input_tokens": 1, "cache_creation_input_tokens": 0,
                           "cache_read_input_tokens": 0, "output_tokens": 7})
        + assistant("2026-08-20T10:08:00.000Z", {"type": "tool_use", "id": "sk-2", "name": "Skill",
                                                  "input": {"skill": "review-change"}},
                    session="s2", usage={"input_tokens": 1, "cache_creation_input_tokens": 0,
                                         "cache_read_input_tokens": 0, "output_tokens": 11}),
        encoding="utf-8")
    _, report = report_of(consumer)
    s2 = next(s for s in report["harness"]["sessions"] if s["id"] == "s2")
    assert s2["by_skill"]["none"]["turns"] == 1 and s2["by_skill"]["none"]["usage"]["output_tokens"] == 3
    assert s2["by_skill"]["plan-work"]["turns"] == 2
    assert s2["by_skill"]["plan-work"]["usage"]["output_tokens"] == 12
    assert s2["by_skill"]["review-change"]["usage"]["output_tokens"] == 11
    totals = report["harness"]["skill_totals"]
    assert totals["plan-work"]["sessions"] == 1 and totals["plan-work"]["usage"]["output_tokens"] == 12
    assert sum(t["usage"]["output_tokens"] for t in totals.values()) == \
        sum(s["usage"]["output_tokens"] for s in report["harness"]["sessions"])


# ----------------------------------------------------------------- compactions


def compacted(stamp: str, trigger: str = "auto", pre: int = 970714, post: int = 13469) -> str:
    """A compaction as the harness records it: a system entry marking the boundary, with the
    context's size either side."""
    return line(type="system", subtype="compact_boundary", timestamp=stamp, sessionId="s4",
                cwd="/consumer", content="Conversation compacted",
                compactMetadata={"trigger": trigger, "preTokens": pre, "postTokens": post})


def test_a_compaction_is_counted_under_the_skill_it_fell_in(consumer):
    (consumer["transcripts"] / "s4.jsonl").write_text(
        human("2026-08-20T10:05:00.000Z")
        + compacted("2026-08-20T10:05:30.000Z", trigger="manual", pre=500, post=40)
        + assistant("2026-08-20T10:06:00.000Z", {"type": "tool_use", "id": "sk-4", "name": "Skill",
                                                  "input": {"skill": "siegard:review-change"}},
                    session="s4", usage={"input_tokens": 1, "cache_creation_input_tokens": 0,
                                         "cache_read_input_tokens": 0, "output_tokens": 1})
        + compacted("2026-08-20T10:30:00.000Z")
        + compacted("2026-08-20T13:30:00.000Z"),
        encoding="utf-8")
    _, report = report_of(consumer)
    assert not list(contract().iter_errors(report))
    s4 = next(s for s in report["harness"]["sessions"] if s["id"] == "s4")
    assert s4["compactions"] == [
        {"trigger": "manual", "pre_tokens": 500, "post_tokens": 40,
         "at": "2026-08-20T10:05:30.000Z", "skill": "none"},
        {"trigger": "auto", "pre_tokens": 970714, "post_tokens": 13469,
         "at": "2026-08-20T10:30:00.000Z", "skill": "review-change"}]
    totals = report["harness"]["skill_totals"]
    assert totals["review-change"]["compactions"] == 1
    assert totals["none"]["compactions"] == 1
    s1 = next(s for s in report["harness"]["sessions"] if s["id"] == "s1")
    assert s1["compactions"] == []


def test_an_agent_s_own_compactions_are_counted_on_its_row(consumer):
    transcript = consumer["transcripts"] / "s1" / "subagents" / "agent-a1.jsonl"
    transcript.write_text(transcript.read_text(encoding="utf-8")
                          + compacted("2026-08-20T10:12:40.000Z"), encoding="utf-8")
    _, report = report_of(consumer)
    rows = {a["tool_use_id"]: a for a in report["agents"]}
    assert rows["tu-agent-1"]["compactions"] == 1
    assert rows["tu-agent-2"]["compactions"] is None


# ----------------------------------------------- what counts as a person typing


def test_a_user_role_entry_the_harness_wrote_is_not_a_human_turn(consumer):
    """A background task's notice, a local command's echo and an injected reminder all land in
    the user role. Counted as they land, they outnumber the person; a paste a person made stays,
    because the pasting was theirs."""
    (consumer["transcripts"] / "s3.jsonl").write_text(
        human("2026-08-20T10:10:00.000Z", "<task-notification><task-id>x</task-id><status>done"
                                          "</status></task-notification>")
        + human("2026-08-20T10:11:00.000Z", "[SYSTEM NOTIFICATION - NOT USER INPUT]\n"
                                            "<task-notification><task-id>y</task-id></task-notification>")
        + human("2026-08-20T10:12:00.000Z", "<local-command-caveat>Caveat.</local-command-caveat>"
                                            "<command-name>/model</command-name>"
                                            "<command-message>model</command-message>"
                                            "<local-command-stdout>Set model</local-command-stdout>")
        + human("2026-08-20T10:13:00.000Z", "<system-reminder>ignore this</system-reminder>")
        + human("2026-08-20T10:14:00.000Z", "<pasted_content id=\"1\">a document</pasted_content>")
        + human("2026-08-20T10:15:00.000Z", "<system-reminder>context</system-reminder>\nand my question")
        + assistant("2026-08-20T10:16:00.000Z", {"type": "text", "text": "ok"}, session="s3",
                    usage={"input_tokens": 1, "cache_creation_input_tokens": 0,
                           "cache_read_input_tokens": 0, "output_tokens": 1}),
        encoding="utf-8")
    _, report = report_of(consumer)
    s3 = next(s for s in report["harness"]["sessions"] if s["id"] == "s3")
    assert s3["human_turns_in_window"] == ["2026-08-20T10:14:00.000Z", "2026-08-20T10:15:00.000Z"]


def test_the_skill_template_names_the_contract_the_script_writes():
    """The report the skill writes carries the version the JSON beside it was written under; a
    template naming another is a report claiming a contract its record does not hold."""
    import telemetry
    text = (REPO / "src/claude/skills/siegard-telemetry/SKILL.md").read_text(encoding="utf-8")
    assert f"contract_version: {telemetry.CONTRACT}\n" in text


def test_a_window_opening_before_the_log_s_history_follows_every_entry(consumer):
    """With no commit before `since` holding the log, every current entry is one the window
    added, and each is still followed to the field it filled — the report keeps its contract."""
    done = run(consumer["home"], "--since", "2026-08-19T00:00:00Z", "--until", UNTIL,
               "--transcripts", consumer["transcripts"])
    assert done.returncode == 0, done.stdout + done.stderr
    report = json.loads((consumer["home"] / "telemetry" / f"{STAMP}.json").read_text(encoding="utf-8"))
    assert not list(contract().iter_errors(report))
    decisions = report["decisions"]
    assert decisions["baseline"].startswith("2 log(s) read, 0 with a commit before")
    assert all(entry["baseline"].startswith("no commit before") for entry in decisions["log"])
    assert len(decisions["added"]) == 2
    assert all("outcome" in entry for entry in decisions["added"])
    assert sum(decisions["outcomes"]["states"].values()) == 2


# ------------------------------------------------------------------- the recommendations


def commit_at(consumer: dict, message: str, when: str) -> str:
    home = consumer["home"]
    subprocess.run(["git", "-C", str(home), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(home), "-c", "user.email=t@example.com", "-c", "user.name=t",
                    "commit", "-q", "-m", message, "--date", when], check=True,
                   env={"GIT_COMMITTER_DATE": when, "PATH": "/usr/bin:/bin",
                        "HOME": str(consumer["tmp"])})
    return subprocess.run(["git", "-C", str(home), "rev-parse", "HEAD"], capture_output=True,
                          text=True, check=True).stdout.strip()


def test_a_recommendation_line_is_counted_with_what_landed_it_and_what_followed(consumer):
    log = consumer["home"] / "delivery/checkout/orchestration.md"
    log.write_text(
        "deliver-scope checkout: deliver task/checkout/record-order — stopped.\n"
        "recommended: /plan-work over checkout — precondition unmet — siegard-reconcile/ holds "
        "no record with `remainder: testable` for domain/x/a\n"
        "- `recommended: /analyse over domain/x/a — rule violated — intake/proof.md`\n"
        "recommended: the second door because I prefer it\n", encoding="utf-8")
    landed = commit_at(consumer, "deliver-scope checkout: log", "2026-08-20T11:10:00Z")
    (consumer["home"] / "work/checkout/task/checkout/record-order.md").write_text(
        "---\ntitle: t\nsummary: s\nobjective: o\ncriteria:\n- c\nimplements:\n- domain/x/a\n---\n"
        "## What it is\nRe-planned.\n", encoding="utf-8")
    followed = commit_at(consumer, "deliver-scope checkout: plan", "2026-08-20T11:20:00Z")
    done, report = report_of(consumer)
    assert done.returncode == 0, done.stdout + done.stderr
    assert [e.message for e in contract().iter_errors(report)] == []
    recommendations = report["recommendations"]
    assert recommendations["emitted"] == 2
    assert recommendations["by_criterion"] == {"precondition unmet": 1, "rule violated": 1,
                                               "already done": 0, "reading paid twice": 0}
    first, second = recommendations["lines"]
    assert (first["slug"], first["line"], first["door"]) == ("checkout", 2, "/plan-work over checkout")
    assert first["landed_in"] == landed
    assert first["next_commit"]["hash"] == followed
    assert first["next_commit"]["subject"] == "deliver-scope checkout: plan"
    assert second["criterion"] == "rule violated" and second["fact"] == "intake/proof.md"
    assert [m["line"] for m in recommendations["malformed"]] == [4]
    assert "recommendations: 2 recorded, 1 line(s) that do not parse" in done.stdout


def test_a_recommendation_no_commit_holds_yet_is_counted_with_no_follower(consumer):
    (consumer["home"] / "delivery/checkout/orchestration.md").write_text(
        "recommended: /reconcile over the remainder — reading paid twice — the bind's receipt\n",
        encoding="utf-8")
    _, report = report_of(consumer)
    (line_,) = report["recommendations"]["lines"]
    assert line_["landed_in"] is None and line_["next_commit"] is None


def test_a_recommendation_landed_outside_the_window_is_not_counted(consumer):
    (consumer["home"] / "delivery/checkout/orchestration.md").write_text(
        "recommended: /reconcile over the remainder — reading paid twice — the bind's receipt\n",
        encoding="utf-8")
    commit_at(consumer, "deliver-scope checkout: log", "2026-08-20T12:30:00Z")
    _, report = report_of(consumer)
    assert report["recommendations"]["emitted"] == 0


def test_no_orchestration_log_is_zero_recommendations_and_the_survey_root_is_never_read(consumer):
    survey = consumer["home"] / "siegard-survey/adopt/orchestration.md"
    survey.parent.mkdir(parents=True)
    survey.write_text("recommended: /reconcile — already done — a note\n", encoding="utf-8")
    _, report = report_of(consumer)
    assert report["recommendations"] == {"emitted": 0, "by_criterion": {
        "precondition unmet": 0, "rule violated": 0, "already done": 0, "reading paid twice": 0},
        "lines": [], "malformed": []}


# ------------------------------------------------------------------------ the handoffs


def spoken(stamp: str, text: str, session: str = "s1") -> str:
    return assistant(stamp, {"type": "text", "text": text}, session=session,
                     usage={"input_tokens": 1, "cache_creation_input_tokens": 0,
                            "cache_read_input_tokens": 0, "output_tokens": 1})


def test_a_confirmation_is_a_class_with_its_wait_and_whether_it_was_asked_for(consumer):
    """What a handoff costs the person is a turn whose whole content is permission. Each one
    leaves the transcript as a class, the skill it answered under, the seconds it waited and
    whether the message it answered asked anything — and never as the words typed."""
    (consumer["transcripts"] / "s4.jsonl").write_text(
        spoken("2026-08-20T10:30:00.000Z", "Delivered.\n\nShall I commit it?", session="s4")
        + human("2026-08-20T10:32:00.000Z", "pode comitar")
        + spoken("2026-08-20T10:40:00.000Z", "Done. The plan holds.", session="s4")
        + human("2026-08-20T10:41:30.000Z", "sim")
        + spoken("2026-08-20T10:45:00.000Z", "Two doors: /plan-work, or /reconcile.\n\nWhich?",
                 session="s4")
        + human("2026-08-20T10:46:00.000Z", "2")
        + human("2026-08-20T10:47:00.000Z", "qual status?")
        + human("2026-08-20T10:48:00.000Z", "can you go ahead and explain the second door?")
        + human("2026-08-20T10:49:00.000Z", "x" * 61 + " go on"),
        encoding="utf-8")
    done, report = report_of(consumer)
    assert done.returncode == 0, done.stdout + done.stderr
    assert [e.message for e in contract().iter_errors(report)] == []
    s4 = next(s for s in report["harness"]["sessions"] if s["id"] == "s4")
    assert [(c["class"], c["after_question"], c["wait_seconds"]) for c in s4["confirmations"]] == [
        ("commit_authorization", True, 120.0), ("go_ahead", False, 90.0),
        ("choice_by_label", True, 60.0)]
    assert s4["short_turns"] == 5, "both questions are short and unclassified; the long turn is not short"
    handoffs = report["handoffs"]
    assert handoffs["human_turns"] == 6 + 1, "s4's six and the fixture's own `go on`"
    assert handoffs["confirmations"] == 4 and handoffs["unclassified_short"] == 2
    assert handoffs["by_class"]["commit_authorization"] == {
        "count": 1, "unasked": 0, "wait_seconds_total": 120.0, "wait_seconds_max": 120.0}
    assert handoffs["by_class"]["go_ahead"]["count"] == 2
    assert handoffs["by_class"]["go_ahead"]["unasked"] == 2
    assert handoffs["by_class"]["go_ahead"]["wait_seconds_max"] == 90.0
    dumped = json.dumps(report)
    assert "pode comitar" not in dumped and "qual status" not in dumped
    assert "handoffs: 4 confirmation(s) typed over 0 Skill call(s)" in done.stdout


def test_a_confirmation_is_attributed_to_the_skill_the_session_was_running(consumer):
    """A go-ahead typed while a skill's span is open is that skill's stop the person paid for;
    the Skill calls beside it are the denominator."""
    (consumer["transcripts"] / "s5.jsonl").write_text(
        assistant("2026-08-20T10:30:00.000Z", {
            "type": "tool_use", "id": "tu-skill", "name": "Skill",
            "input": {"skill": "siegard:implement-task", "args": "task/checkout/record-order"}},
            session="s5")
        + user_result("2026-08-20T10:30:01.000Z", "tu-skill", "loaded")
        + spoken("2026-08-20T10:50:00.000Z", "The delivery is written; the tree is yours.",
                 session="s5")
        + human("2026-08-20T10:51:00.000Z", "comite e siga"),
        encoding="utf-8")
    _, report = report_of(consumer)
    s5 = next(s for s in report["harness"]["sessions"] if s["id"] == "s5")
    assert s5["skill_calls"] == {"implement-task": 1}
    assert [c["skill"] for c in s5["confirmations"]] == ["implement-task"]
    assert report["handoffs"]["by_skill"]["implement-task"] == {"calls": 1, "confirmations": 1}
    assert report["handoffs"]["skill_calls"] == 1


def test_the_classifier_reads_a_commit_word_first_and_a_question_never(consumer):
    import telemetry
    assert telemetry.confirmation_class("go ahead and commit") == "commit_authorization"
    assert telemetry.confirmation_class("pode seguir") == "go_ahead"
    assert telemetry.confirmation_class("opção b") == "choice_by_label"
    assert telemetry.confirmation_class("pode seguir?") is None
    assert telemetry.confirmation_class("sim, mas antes troque o nome do campo para x") is None
    assert telemetry.asks("Done.\n\nShall I commit?") is True
    assert telemetry.asks("Is it done? Yes.\n\nThe tree is yours.") is False


def test_the_handoffs_section_names_the_transcripts_as_its_source(consumer):
    _, report = report_of(consumer)
    row = next(p for p in report["provenance"] if p["section"] == "handoffs")
    assert row["source"] == str(consumer["transcripts"]) and row["unavailable"] is None
    done = run(consumer["home"], "--since", SINCE, "--until", UNTIL, "--transcripts",
               consumer["tmp"] / "nowhere")
    report = json.loads((consumer["home"] / "telemetry" / f"{STAMP}.json").read_text(encoding="utf-8")) \
        if done.returncode == 0 else None
    assert report is None or report["handoffs"]["confirmations"] == 0


# ------------------------------------------------------------- commits inside a span


def git_call(stamp: str, tool_use_id: str, command: str, session: str) -> str:
    return assistant(stamp, {"type": "tool_use", "id": tool_use_id, "name": "Bash",
                             "input": {"command": command}}, session=session,
                     usage={"input_tokens": 1, "cache_creation_input_tokens": 0,
                            "cache_read_input_tokens": 0, "output_tokens": 1})


def skill_call(stamp: str, tool_use_id: str, skill: str, session: str) -> str:
    return assistant(stamp, {"type": "tool_use", "id": tool_use_id, "name": "Skill",
                             "input": {"skill": skill, "args": "x"}}, session=session)


def test_a_commit_inside_a_skill_span_is_counted_with_what_authorized_it(consumer):
    """A commit the session ran after a Skill call and before the person's next turn is the
    session's own act. Each leaves as the skill it fell under, whether it named a pathspec,
    whether it pushed, and the strongest authorization the session could read: a typed commit
    word, an armed loop, a word only in a continuation summary, or nothing."""
    (consumer["transcripts"] / "s6.jsonl").write_text(
        skill_call("2026-08-20T10:30:00.000Z", "tu-s1", "siegard:implement-task", "s6")
        + git_call("2026-08-20T10:31:00.000Z", "tu-g1",
                   "git add -A && git commit -m 'implement-task: x'", "s6")
        + human("2026-08-20T10:32:00.000Z", "ok, pode comitar os próximos também")
        + skill_call("2026-08-20T10:33:00.000Z", "tu-s2", "siegard:review-change", "s6")
        + git_call("2026-08-20T10:34:00.000Z", "tu-g2",
                   "git add -- delivery && git commit -m 'review-change: y' && git push", "s6")
        + human("2026-08-20T10:35:00.000Z", "e agora?")
        + git_call("2026-08-20T10:36:00.000Z", "tu-g3", "git commit -a -m 'after a turn'", "s6"),
        encoding="utf-8")
    (consumer["transcripts"] / "s7.jsonl").write_text(
        human("2026-08-20T10:40:00.000Z", "This session is being continued from a previous "
                                          "conversation. Summary: run the route, committing "
                                          "between steps.")
        + skill_call("2026-08-20T10:41:00.000Z", "tu-s3", "siegard:plan-work", "s7")
        + git_call("2026-08-20T10:42:00.000Z", "tu-g4", "git -C /x commit -m 'plan' -- work",
                   "s7"),
        encoding="utf-8")
    (consumer["transcripts"] / "s8.jsonl").write_text(
        human("2026-08-20T10:50:00.000Z", "/loop 5m continue the delivery loop")
        + skill_call("2026-08-20T10:51:00.000Z", "tu-s4", "siegard:reconcile", "s8")
        + git_call("2026-08-20T10:52:00.000Z", "tu-g5", "git commit -m 'reconcile' -- siegard-reconcile",
                   "s8"),
        encoding="utf-8")
    done, report = report_of(consumer)
    assert done.returncode == 0, done.stdout + done.stderr
    assert [e.message for e in contract().iter_errors(report)] == []
    s6 = next(s for s in report["harness"]["sessions"] if s["id"] == "s6")
    assert [(c["skill"], c["authorized_by"], c["pathspec"], c["push"]) for c in s6["commits"]] == [
        ("implement-task", "none", False, False), ("review-change", "typed", True, True)], \
        "the third commit came after a human turn and is not the session's own act in a span"
    in_span = report["handoffs"]["in_span_commits"]
    assert in_span["count"] == 4
    assert in_span["by_authorization"] == {"typed": 1, "loop": 1, "summary": 1, "none": 1}
    assert in_span["by_skill"] == {"implement-task": 1, "plan-work": 1, "reconcile": 1,
                                   "review-change": 1}
    assert in_span["pathspec"] == 3 and in_span["push"] == 1
    assert "git add -A" not in json.dumps(report)
    assert "commits inside a skill's span: 4 — typed 1, loop 1, summary 1, none 1; 3 pathspec-scoped, 1 pushed" in done.stdout


def test_pathspec_scoping_is_read_from_the_command_alone():
    import telemetry
    assert telemetry.pathspec_scoped("git add -A -- work && git commit -m x") is True
    assert telemetry.pathspec_scoped("git add -A && git commit -m x") is False
    assert telemetry.pathspec_scoped("git add . && git commit -m x") is False
    assert telemetry.pathspec_scoped("git commit -a -m x") is False
    assert telemetry.pathspec_scoped("git add work/a.md && git commit -m x") is True


def test_a_note_in_a_closed_plan_is_marked_not_live(consumer):
    """A note in a closed plan is what a person closed over, not the state the window's work ran
    under; the record carries the marker so a report can list the two apart."""
    _, report = report_of(consumer)
    assert all(note["live"] is True for note in report["notes"])
    (consumer["home"] / "work/checkout/closure.md").write_text("Closed.\n", encoding="utf-8")
    (consumer["home"] / "telemetry" / f"{STAMP}.json").unlink()
    _, report = report_of(consumer)
    assert report["notes"] and all(note["live"] is False for note in report["notes"])
    assert [e.message for e in contract().iter_errors(report)] == []
