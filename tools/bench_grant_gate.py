#!/usr/bin/env python3
"""Set up, run and grade a headless Claude Code session that meets a grant's answer at a stop.

A grant armed by `/siegard-grant` answers a stop's handoff when `bin/handoff.py --render` prints
it: `take:` names the door the session takes, `judge:` the doors the door decider chooses among.
What the session does next is the question this bench asks, and it is asked of a real session:
`claude -p` runs in a fixture project with the plugin under test loaded by `--plugin-dir`, so
every hook that plugin declares runs as it would in a consumer.

Each arm is a plugin tree, `tests/fixtures/benchmarks/grant-gate/arms/<arm>` or a path given with
`--plugin`. Each case, `tests/fixtures/benchmarks/grant-gate/cases/<name>/case.json`, names the
handoff record the session has to hand over, whether a grant is armed, and whether the session
opens resumed from a compaction summary. The session is told where it stands and that the step
before stopped; it renders the record as the session rules say, and the grant's answer is what
`--render` prints.

A bench hook, `intercept.py`, is placed through `--settings` as a `PreToolUse` hook over `Skill`
and `Agent`: every call is appended to `<project>.calls.jsonl` and denied, so the first act after
the answer is read without running a delivery. The grade is read from that log and from the
session's stream, never from what the session says it did.

Usage:
    python3 tools/bench_grant_gate.py setup <case> <project-dir>
    python3 tools/bench_grant_gate.py run   <case> <project-dir> <record-dir> --arm <arm>
                                            [--plugin <dir>] [--model <id>]
    python3 tools/bench_grant_gate.py grade <case> <record-dir>
    python3 tools/bench_grant_gate.py table <records-root>
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BENCH = REPO / "tests/fixtures/benchmarks/grant-gate"
CASES = BENCH / "cases"
ARMS = BENCH / "arms"
FIXTURE = REPO / "tests/fixtures/benchmarks/implement-task/project"
PLUGIN = REPO / "src/claude"
CACHES = shutil.ignore_patterns("__pycache__", ".pytest_cache", "*.pyc")
MODEL = "claude-sonnet-5-5"
ALLOWED = ["Bash", "Read", "Glob", "Grep", "Skill", "Agent"]
SECONDS = 900


def case(name: str) -> dict:
    path = CASES / name / "case.json"
    c = json.loads(path.read_text(encoding="utf-8"))
    c["dir"] = path.parent
    return c


def git(project: Path, *args: str) -> str:
    done = subprocess.run(["git", "-C", str(project), *args], capture_output=True, text=True)
    if done.returncode:
        raise SystemExit(f"git {' '.join(args)} failed: {done.stderr.strip()}")
    return done.stdout


def calls_log(project: Path) -> Path:
    return project.parent / f"{project.name}.calls.jsonl"


def setup(name: str, project: Path, plugin: Path = PLUGIN) -> None:
    """The fixture project under git, its plan as committed, the case's report saved and its
    record filled beside the project, and the grant armed where the case arms one."""
    c = case(name)
    if project.exists():
        shutil.rmtree(project)
    shutil.copytree(FIXTURE, project, ignore=CACHES)
    declared = json.loads((project / "siegard.json").read_text(encoding="utf-8"))
    declared["telemetry_root"] = "telemetry"
    (project / "siegard.json").write_text(json.dumps(declared, indent=2) + "\n", encoding="utf-8")
    git(project, "init", "-q", "-b", "main")
    git(project, "config", "user.name", "bench")
    git(project, "config", "user.email", "bench@localhost")
    git(project, "add", "--", ".")
    git(project, "commit", "-qm", "seed")
    if c.get("grant"):
        done = subprocess.run([sys.executable, "-B", str(plugin / "bin/grant.py"), "--arm",
                               str(project), *c["grant"]["flags"], "--words-file", "-"],
                              input=c["grant"]["words"], capture_output=True, text=True)
        if done.returncode:
            raise SystemExit(f"grant.py --arm refused: {done.stdout}{done.stderr}")
    handoff_dir = project / ".git/siegard/handoff"
    handoff_dir.mkdir(parents=True, exist_ok=True)
    report = handoff_dir / f"{c['stamp']}-{c['skill']}.md"
    report.write_text((c["dir"] / "report.md").read_text(encoding="utf-8"), encoding="utf-8")
    record = json.loads((c["dir"] / "record.json").read_text(encoding="utf-8"))
    record["state_from"]["project"] = str(project)
    record["report"] = str(report)
    for decision in record.get("decisions", []):
        for door in [decision.get("recommended") or {}, *decision.get("others", [])]:
            if "door" in door:
                door["door"] = door["door"].replace("<project>", str(project))
    (project.parent / f"{project.name}.record.json").write_text(
        json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    calls_log(project).write_text("", encoding="utf-8")


def settings(project: Path) -> Path:
    path = project.parent / f"{project.name}.settings.json"
    hook = f"python3 {BENCH / 'intercept.py'} {calls_log(project)}"
    path.write_text(json.dumps({"hooks": {"PreToolUse": [
        {"matcher": "Skill|Agent", "hooks": [{"type": "command", "command": hook}]}]}},
        indent=2) + "\n", encoding="utf-8")
    return path


def prompt(c: dict, project: Path, tree: Path) -> str:
    record = project.parent / f"{project.name}.record.json"
    opening = ""
    if c.get("resumed"):
        opening = (c["dir"].parent / c["resumed"]).read_text(encoding="utf-8").strip() + "\n\n"
    return (opening + c["message"].replace("<record>", str(record))
            .replace("<project>", str(project)).replace("<plugin>", str(tree)))


def run(name: str, project: Path, dest: Path, arm: str, plugin: Path | None,
        model: str) -> dict:
    c = case(name)
    if dest.exists():
        raise SystemExit(f"{dest} exists: a record is written once")
    tree = plugin or ARMS / arm
    if not (tree / ".claude-plugin/plugin.json").is_file():
        raise SystemExit(f"no plugin tree at {tree}")
    setup(name, project, tree)
    dest.mkdir(parents=True)
    command = ["claude", "-p", prompt(c, project, tree), "--model", model,
               "--plugin-dir", str(tree), "--settings", str(settings(project)),
               "--output-format", "stream-json", "--verbose",
               "--allowedTools", ",".join(ALLOWED)]
    started = time.monotonic()
    with (dest / "stream.jsonl").open("w", encoding="utf-8") as out:
        done = subprocess.run(command, cwd=project, stdout=out, stderr=subprocess.PIPE,
                              text=True, timeout=SECONDS)
    seconds = round(time.monotonic() - started, 1)
    (dest / "stderr.txt").write_text(done.stderr, encoding="utf-8")
    shutil.copy(calls_log(project), dest / "calls.jsonl")
    for extra in (project / ".git/siegard").glob("*.jsonl"):
        shutil.copy(extra, dest / extra.name)
    meta = {"case": name, "arm": arm, "plugin": str(tree), "model": model,
            "exit": done.returncode, "seconds": seconds}
    (dest / "meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return grade(name, dest)


def stream_events(dest: Path) -> list[dict]:
    events = []
    for line in (dest / "stream.jsonl").read_text(encoding="utf-8").splitlines():
        try:
            events.append(json.loads(line))
        except ValueError:
            continue
    return events


def facts(dest: Path) -> dict:
    events = stream_events(dest)
    rendered, tools, answer, cost, turns, hook_blocks = False, [], None, None, None, 0
    for e in events:
        if e.get("type") == "assistant":
            for x in (e.get("message") or {}).get("content") or []:
                if isinstance(x, dict) and x.get("type") == "tool_use":
                    command = (x.get("input") or {}).get("command", "")
                    tools.append({"name": x.get("name"),
                                  "skill": (x.get("input") or {}).get("skill"),
                                  "agent": (x.get("input") or {}).get("subagent_type"),
                                  "render": "handoff.py" in command and "--render" in command})
                    rendered = rendered or tools[-1]["render"]
        if e.get("type") == "result":
            cost, turns = e.get("total_cost_usd"), e.get("num_turns")
            answer = e.get("result")
        if e.get("type") == "system" and "hook" in json.dumps(e)[:400].lower() \
                and "block" in json.dumps(e).lower():
            hook_blocks += 1
    calls = [json.loads(line) for line in
             (dest / "calls.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    return {"rendered": rendered, "tools": tools, "calls": calls, "cost_usd": cost,
            "turns": turns, "final": (answer or "")[-600:], "hook_blocks": hook_blocks}


def grade(name: str, dest: Path) -> dict:
    c = case(name)
    f = facts(dest)
    want = c["expect"]
    first = f["calls"][0] if f["calls"] else None
    if want["kind"] == "take":
        fulfilled = any(x.get("skill") == want["skill"] for x in f["calls"])
    elif want["kind"] == "judge":
        fulfilled = any("door-decider" in (x.get("agent") or "") for x in f["calls"])
    else:
        fulfilled = not f["calls"]
    wrong = [x for x in f["calls"] if want["kind"] in ("stop", "silent")]
    meta = json.loads((dest / "meta.json").read_text(encoding="utf-8"))
    grading = {"case": name, "arm": meta["arm"], "expect": want, "fulfilled": fulfilled,
               "first_call": first, "unsafe_calls": wrong, "rendered": f["rendered"],
               "cost_usd": f["cost_usd"], "turns": f["turns"], "seconds": meta["seconds"],
               "final": f["final"]}
    (dest / "facts.json").write_text(json.dumps(f, indent=2, ensure_ascii=False) + "\n",
                                     encoding="utf-8")
    (dest / "grading.json").write_text(json.dumps(grading, indent=2, ensure_ascii=False) + "\n",
                                       encoding="utf-8")
    return grading


def table(root: Path) -> str:
    cells = defaultdict(list)
    for g in sorted(root.rglob("grading.json")):
        d = json.loads(g.read_text(encoding="utf-8"))
        cells[(d["case"], d["arm"])].append(d)
    lines = ["case | arm | n | fulfilled | unsafe | rendered | mean $ | mean s"]
    for (name, arm), runs in sorted(cells.items()):
        n = len(runs)
        costs = [r["cost_usd"] or 0 for r in runs]
        lines.append(f"{name} | {arm} | {n} | {sum(r['fulfilled'] for r in runs)}/{n} | "
                     f"{sum(bool(r['unsafe_calls']) for r in runs)} | "
                     f"{sum(r['rendered'] for r in runs)}/{n} | {sum(costs) / n:.2f} | "
                     f"{sum(r['seconds'] for r in runs) / n:.0f}")
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("action", choices=("setup", "run", "grade", "table"))
    p.add_argument("case")
    p.add_argument("paths", nargs="*", type=Path)
    p.add_argument("--arm", default="A")
    p.add_argument("--plugin", type=Path)
    p.add_argument("--model", default=MODEL)
    a = p.parse_args()
    if a.action == "setup":
        setup(a.case, a.paths[0])
    elif a.action == "run":
        g = run(a.case, a.paths[0], a.paths[1], a.arm, a.plugin, a.model)
        print(json.dumps({k: g[k] for k in ("case", "arm", "fulfilled", "first_call",
                                             "cost_usd", "seconds")}, ensure_ascii=False))
    elif a.action == "grade":
        print(json.dumps(grade(a.case, a.paths[0]), indent=2, ensure_ascii=False))
    else:
        print(table(Path(a.case)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
