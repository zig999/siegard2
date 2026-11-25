#!/usr/bin/env python3
"""Replay real stops of consumer sessions under a plugin tree, and read what the grant answered.

A stop is a session's last message before a person's turn. Each one is replayed from its own
session transcript: the consumer repository is cloned at the commit before the stop, its
`.git/siegard` state is copied up to the stop, the transcript is cut and every path in it is
rewritten to the clone, and the session is resumed with `claude -p --resume` under the plugin
tree of an arm, prompted by a background-task notification and nothing else. Two bench hooks run
beside the plugin's own: `intercept.py` records and denies every `Skill` and `Agent` call, so the
first act after a grant's answer is read without running a delivery; the guard below denies a
`Bash`, `Write` or `Edit` naming the real consumer, or `/tmp` outside the run's own directory, so
one run never reads another's scratch file.

Subcommands:
    points  --consumer <dir>... --since <iso> --out <points.json> [--live-grant] [--doors]
            every stop a person answered with a go-ahead or a "what now?", with the context it
            stood in and the grant live then
    build   <points.json> <index> <arm-dir> <run-dir> [--cut final|render|ask]
    run     <run-dir> <arm-dir> [--model <id>]
    batch   <points.json> <root> --arm <name>=<dir>... [--reps N] [--jobs N] [--only i,j]
    grade   <run-dir>
    table   <root>
    static  <root> [--bin <plugin-bin>]   re-ask the grant over each run's kept record, no model
    clean   <root>                         drop the clones and the cut transcripts of the runs
    guard   <log> <run-dir> <consumer>... [--allow <arm-dir>]
            the PreToolUse guard, read from standard input; the arm's own tree is never stray

No model runs in `points`, `grade`, `table`, `static` and `clean`. `run` and `batch` spend.
The workflow, what each outcome means and the limits of a replay: `docs/replay-stops.md`.
"""
from __future__ import annotations

import argparse
import collections
import contextlib
import functools
import io
import json
import os
import re
import shutil
import subprocess
import sys
import uuid
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INTERCEPT = REPO / "tests/fixtures/benchmarks/grant-gate/intercept.py"
PROJECTS = Path.home() / ".claude" / "projects"
CACHE = re.compile(r"/[^\s\"']*/\.claude/plugins/cache/[^/\s\"']+/siegard/\d+\.\d+\.\d+")
MODEL = "claude-sonnet-5-5"
SECONDS = 1500
ALLOWED = "Bash,Read,Glob,Grep,Skill,Agent"
NOTIFICATION = ("<task-notification><task-id>b7q2k1x9</task-id><status>completed</status>"
                "<summary>Background command \"git status --porcelain\" completed (exit code 0)"
                "</summary></task-notification>")
ROUTE_DOORS = ("plan-work", "implement-task", "review-change", "reconcile", "deliver-scope",
               "analyse")
DOOR = re.compile(r"/(" + "|".join(ROUTE_DOORS) + r")\b")
GO = re.compile(r"^\s*(sim|siga|segue|seguir|pode|vai|ok|certo|quero|1|2|3|planej|entreg|revis|"
                r"rod|continu|prossiga|yes|go|proceed|continue)", re.I)
STATUS = re.compile(r"(status|e agora|próximo passo|proximo passo|iniciativa|backlog|"
                    r"o que (falta|fazer)|oq fazer|qual a recomend|what now|next step)", re.I)
PERSON = re.compile(r"push|apag|delet|remov|comit|commit|encerr|fech|standard|autoriz|goal|"
                    r"desarm|close|authori", re.I)
ANSWER = re.compile(r"^(grant: |decision \d+: (take|judge|stop)|stop: |note: decision)")
DECISION = re.compile(r"^decision \d+: (\w+)")


def transcript_dir(consumer: Path) -> Path:
    return PROJECTS / ("-" + str(consumer).strip("/").replace("/", "-").replace(".", "-"))


def lines_of(path: Path) -> list[dict]:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return out


def text_of(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(x.get("text", "") for x in content
                        if isinstance(x, dict) and x.get("type") == "text")
    return ""


def result_text(block: dict) -> str:
    content = block.get("content")
    if isinstance(content, str):
        return content
    return " ".join(x.get("text", "") for x in content or [] if isinstance(x, dict))


def is_person(event: dict) -> str | None:
    """The person's own words in a transcript event, or None for anything the harness wrote."""
    if event.get("type") != "user" or event.get("isMeta") or event.get("isCompactSummary"):
        return None
    content = (event.get("message") or {}).get("content")
    if isinstance(content, list) and any(isinstance(x, dict) and x.get("type") == "tool_result"
                                         for x in content):
        return None
    words = text_of(content).strip()
    if not words or words.startswith(("<", "This session is being continued", "[Request interrupted",
                                      "Stop hook feedback")) or "SYSTEM NOTIFICATION" in words[:80]:
        return None
    return words


def reply_class(reply: str) -> str:
    if PERSON.search(reply):
        return "person-only"
    if len(reply) <= 70 and GO.match(reply) and "?" not in reply:
        return "go"
    if len(reply) <= 70 and STATUS.search(reply):
        return "status-q"
    return "content"


def stops(consumer: Path, since: str) -> list[dict]:
    """Every assistant message a person's turn followed, from the consumer's transcripts."""
    rows = []
    for path in sorted(transcript_dir(consumer).glob("*.jsonl")):
        events = lines_of(path)
        turns = [(at, e.get("timestamp", "")[:19], words) for at, e in enumerate(events)
                 if (words := is_person(e))]
        for (start, _, ask), (end, answered_at, reply) in zip(turns, turns[1:]):
            if answered_at < since:
                continue
            skills, last, rendered = [], None, False
            for e in events[start + 1:end]:
                if e.get("type") != "assistant":
                    continue
                for x in e["message"].get("content") or []:
                    if isinstance(x, dict) and x.get("type") == "tool_use":
                        given = x.get("input") or {}
                        if x.get("name") == "Skill":
                            skills.append(str(given.get("skill", "")).split(":")[-1])
                        command = str(given.get("command", ""))
                        rendered = rendered or ("handoff.py" in command and "--render" in command)
                said = text_of(e["message"].get("content")).strip()
                if said:
                    last = (e.get("timestamp", "")[:19], said)
            if last:
                rows.append({"project": consumer.name, "consumer": str(consumer),
                             "session": path.stem, "at": last[0], "skills": skills,
                             "ask": ask[:200], "doors": len(set(DOOR.findall(last[1]))),
                             "rendered": rendered, "reply": reply[:120],
                             "reply_class": reply_class(reply.strip())})
    return rows


def grant_at(consumer: Path, at: str) -> dict | None:
    """The grant armed in the consumer at that time, from its record and its ended log."""
    base = consumer / ".git/siegard"
    held = []
    if (base / "grants-ended.jsonl").is_file():
        held += [json.loads(line) for line in
                 (base / "grants-ended.jsonl").read_text(encoding="utf-8").splitlines() if line]
    if (base / "grant.json").is_file():
        held.append({**json.loads((base / "grant.json").read_text(encoding="utf-8")),
                     "ended_at": "9999"})
    found = [g for g in held if g.get("armed_at", "")[:19] <= at <= g.get("ended_at", "")[:19]]
    return found[0] if found else None


def plugin_version_at(consumer: Path, at: str) -> str | None:
    """The plugin version the consumer's session ran at that time, read from the plugin's cache
    paths its transcripts carry."""
    version = None
    for stamp, value in versions_seen(consumer):
        if stamp > at:
            break
        version = value
    return version


@functools.lru_cache(maxsize=None)
def versions_seen(consumer: Path) -> tuple[tuple[str, str], ...]:
    found = re.compile(r"siegard[/-](\d+\.\d+\.\d+)/")
    seen = []
    for path in transcript_dir(consumer).glob("*.jsonl"):
        for line in path.read_text(encoding="utf-8").splitlines():
            match = found.search(line)
            if match:
                try:
                    seen.append((json.loads(line).get("timestamp", "")[:19], match.group(1)))
                except ValueError:
                    continue
    return tuple(sorted(seen))


def points(consumers: list[Path], since: str, live_grant: bool, doors: bool) -> list[dict]:
    chosen = []
    for consumer in consumers:
        for row in stops(consumer, since):
            if row["reply_class"] not in ("go", "status-q") or (doors and not row["doors"]):
                continue
            grant = grant_at(consumer, row["at"])
            row["grant"] = grant
            row["grant_live"] = bool(grant) and grant.get("version") == plugin_version_at(
                consumer, row["at"])
            if live_grant and not row["grant_live"]:
                continue
            chosen.append(row)
    return chosen


def asked_at(events: list[dict], at: str) -> int:
    """The person's own message the turn ending at `at` answers: the last event before the stop's
    second that `is_person` reads as the person's words, never one the harness wrote."""
    found = None
    for index, e in enumerate(events):
        if e.get("timestamp", "")[:19] > at:
            break
        if not e.get("isSidechain") and is_person(e) is not None:
            found = index
    if found is None:
        raise SystemExit(f"no message of the person before {at}")
    return found


def cut_at(events: list[dict], at: str, mode: str) -> int:
    """Where the transcript is cut: `final`, at the last tool result before the stop's last
    message, so the session writes that message again; `render`, right after the tool result
    that printed a grant's `judge`; `ask`, right before the person's own message the turn
    answers, which the run then sends as its prompt, so a hook on that message meets it."""
    if mode == "ask":
        return asked_at(events, at) - 1
    if mode == "render":
        for index, e in enumerate(events):
            if e.get("timestamp", "").startswith(at[:16]) and e.get("type") == "user" \
                    and "spawn the door decider" in json.dumps(e):
                return index
        raise SystemExit(f"no render printing judge at {at}")
    final = None
    for index, e in enumerate(events):
        if e.get("timestamp", "")[:19] > at:
            break
        if e.get("type") == "assistant" and text_of(e["message"].get("content")).strip():
            final = index
    if final is None:
        raise SystemExit(f"no message at {at}")
    cut = final - 1
    while cut > 0 and not (events[cut].get("type") == "user" and "tool_result" in json.dumps(
            events[cut])):
        cut -= 1
    return cut


STRAY_TMP = re.compile(r"(?<![\w/.-])/tmp/(?!claude-)")


def rewrite(line: str, real: Path, clone: Path, tree: Path, old: str, new: str,
            scratch: Path | None = None) -> str:
    """One transcript line with the consumer, its parent, the plugin cache and the session id
    rewritten to the replay's own, and, given a scratch directory, every `/tmp/` path the real
    session wrote moved under it: a session reuses the paths its history holds, and the guard
    denies any outside the run."""
    if scratch is not None:
        line = STRAY_TMP.sub(f"{scratch}/", line)
    line = line.replace(str(real), str(clone)).replace(str(real.parent), str(clone.parent))
    return CACHE.sub(str(tree), line).replace(old, new)


RENDERING_SOURCE = REPO / "src/claude/hooks/turn.py"


def rendering_skills() -> tuple[str, ...]:
    """The skills whose run ends on a render, as the plugin's turn record reads them."""
    found = re.search(r"RENDERING = \(([^)]*)\)", RENDERING_SOURCE.read_text(encoding="utf-8"))
    return tuple(re.findall(r'"([\w-]+)"', found.group(1))) if found else ()


def route_at(events: list[dict], cut: int) -> float | None:
    """The instant of the last `Skill` call to a skill whose run ends on a render, in the turn the
    cut ends: the call happened before the cut, so the replayed session's `PostToolUse` hook never
    sees it, and the turn record is seeded with it instead."""
    rendering = rendering_skills()
    for event in reversed(events[:cut + 1]):
        content = (event.get("message") or {}).get("content")
        if event.get("type") == "user" and (is_person(event) or "<command-name>" in text_of(content)[:200]):
            return None
        if event.get("type") != "assistant" or not isinstance(content, list):
            continue
        for block in reversed(content):
            if isinstance(block, dict) and block.get("type") == "tool_use" \
                    and block.get("name") == "Skill":
                name = str((block.get("input") or {}).get("skill") or "").split(":")[-1].lstrip("/")
                if name in rendering:
                    stamp = event.get("timestamp", "").replace("Z", "+00:00")
                    return datetime.fromisoformat(stamp).timestamp() if stamp else None
    return None


def build(point: dict, tree: Path, run_dir: Path, mode: str) -> dict:
    real = Path(point["consumer"])
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True)
    (run_dir / "scratch").mkdir()
    clone = run_dir / real.name
    subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(real), str(clone)], check=True)
    source = transcript_dir(real) / f"{point['session']}.jsonl"
    raw = source.read_text(encoding="utf-8").splitlines()
    events = [json.loads(line) for line in raw]
    cut = cut_at(events, point["at"], mode)
    moment = events[cut + 1]["timestamp"][:19] if mode == "ask" else point["at"][:19]
    commit = subprocess.run(["git", "-C", str(real), "rev-list", "-1",
                             f"--before={moment}Z", "HEAD"],
                            capture_output=True, text=True, check=True).stdout.strip()
    subprocess.run(["git", "-C", str(clone), "checkout", "-q", commit], check=True)
    subprocess.run(["git", "-C", str(clone), "checkout", "-q", "-B", "main"], check=True)
    subprocess.run(["git", "-C", str(clone), "remote", "remove", "origin"], check=True)
    stamp = moment[:16].replace("-", "").replace(":", "")

    def later(_, names):
        return [n for n in names if n.endswith(".jsonl")
                or (re.match(r"\d{8}T\d{6}Z", n) and n[:13] > stamp)]

    shutil.copytree(real / ".git/siegard", clone / ".git/siegard", dirs_exist_ok=True,
                    ignore=later)
    (clone / ".git/siegard/goal.json").unlink(missing_ok=True)
    version = json.loads((tree / ".claude-plugin/plugin.json").read_text())["version"]
    grant = clone / ".git/siegard/grant.json"
    grant.unlink(missing_ok=True)
    if point.get("grant"):
        held = {k: v for k, v in point["grant"].items() if k not in ("ended", "reason", "ended_at")}
        grant.write_text(json.dumps({**held, "project_root": str(clone), "version": version},
                                    indent=2), encoding="utf-8")
    session = str(uuid.uuid4())
    out = [rewrite(line, real, clone, tree, point["session"], session, run_dir.resolve() / "scratch")
           for line in raw[:cut + 1]]
    where = transcript_dir(clone)
    where.mkdir(parents=True, exist_ok=True)
    (where / f"{session}.jsonl").write_text("\n".join(out) + "\n", encoding="utf-8")
    seeded = None if mode == "ask" else route_at(events, cut)
    if seeded is not None:
        record = clone / ".git/siegard/turn" / f"{session}.json"
        record.parent.mkdir(parents=True, exist_ok=True)
        record.write_text(json.dumps({"session_id": session, "route_at": seeded,
                                      "obligations": [], "blocked": []}), encoding="utf-8")
    meta = {"point": point, "clone": str(clone), "session": session, "commit": commit,
            "cut": cut, "mode": mode, "tree": str(tree), "transcript": str(where),
            "route_at": seeded}
    if mode == "ask":
        meta["prompt"] = rewrite(text_of(events[cut + 1]["message"].get("content")), real, clone,
                                 tree, point["session"], session, run_dir.resolve() / "scratch")
    (run_dir / "meta.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False),
                                       encoding="utf-8")
    return meta


def guard(log: Path, run_dir: Path, consumers: list[str], event: dict,
          allowed: tuple[str, ...] = ()) -> dict | None:
    """The guard's answer to a tool call: a denial where its input names a real consumer, or a
    path under `/tmp` outside the run's own directory and the arm's own tree."""
    given = json.dumps(event.get("tool_input") or {})
    named = [c for c in consumers if c in given]
    kept = (str(run_dir), *allowed)
    stray = [p for p in re.findall(r"/tmp/[\w./-]*", given)
             if not p.startswith(kept) and p not in ("/tmp", "/tmp/")]
    if not named and not stray:
        return None
    with log.open("a", encoding="utf-8") as out:
        out.write(json.dumps({"guard": event.get("tool_name"), "input": given[:300]}) + "\n")
    reason = ("This path is outside the project." if named else
              f"Write scratch files under {run_dir}/scratch, not elsewhere under /tmp.")
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                   "permissionDecisionReason": reason}}


def run(run_dir: Path, tree: Path, model: str) -> dict:
    meta = json.loads((run_dir / "meta.json").read_text(encoding="utf-8"))
    calls = run_dir / "calls.jsonl"
    calls.write_text("", encoding="utf-8")
    me = Path(__file__).resolve()
    consumer = meta["point"]["consumer"]
    settings = {"hooks": {"PreToolUse": [
        {"matcher": "Skill|Agent",
         "hooks": [{"type": "command", "command": f"python3 {INTERCEPT} {calls}"}]},
        {"matcher": "Bash|Write|Edit|MultiEdit|NotebookEdit",
         "hooks": [{"type": "command",
                    "command": f"python3 {me} guard {calls} {run_dir} {consumer} "
                               f"--allow {tree.resolve()}"}]}]}}
    (run_dir / "settings.json").write_text(json.dumps(settings), encoding="utf-8")
    env = {**os.environ, "TMPDIR": str(run_dir / "scratch")}
    with (run_dir / "stream.jsonl").open("w", encoding="utf-8") as out, \
            (run_dir / "stderr.txt").open("w", encoding="utf-8") as err:
        try:
            subprocess.run(["claude", "-p", meta.get("prompt") or NOTIFICATION,
                            "--resume", meta["session"],
                            "--model", model, "--plugin-dir", str(tree),
                            "--settings", str(run_dir / "settings.json"),
                            "--output-format", "stream-json", "--verbose",
                            "--allowedTools", ALLOWED], cwd=meta["clone"], stdin=subprocess.DEVNULL,
                           stdout=out, stderr=err, env=env, timeout=SECONDS)
        except subprocess.TimeoutExpired:
            err.write("timeout\n")
    return grade(run_dir)


def stream_facts(run_dir: Path) -> dict:
    renders, prepares, answers, final, cost, refused = 0, 0, [], "", None, False
    ids = set()
    for e in lines_of(run_dir / "stream.jsonl"):
        if e.get("type") == "assistant":
            for x in e["message"].get("content") or []:
                if x.get("type") == "tool_use":
                    command = str((x.get("input") or {}).get("command", ""))
                    if "handoff.py" in command and "--render" in command:
                        renders += 1
                        ids.add(x["id"])
                    prepares += "handoff.py" in command and "--prepare" in command
                if x.get("type") == "text" and x["text"].strip():
                    final = x["text"][:400]
        if e.get("type") == "user":
            for block in e["message"].get("content") or []:
                if isinstance(block, dict) and block.get("type") == "tool_result":
                    answers += [line[:260] for line in result_text(block).splitlines()
                                if ANSWER.match(line)]
        if e.get("type") == "result":
            cost = e.get("total_cost_usd")
            refused = "spend limit" in str(e.get("result", ""))
    return {"renders": renders, "prepares": prepares, "answers": answers, "final": final,
            "cost_usd": cost, "limit_hit": refused}


def outcome(facts: dict, blocks: list, calls: list) -> str:
    """What the stop came to: `took` where the grant answered take or judge and the session
    carried it out; `took-not-carried`; `stop`; `rendered-silent` where a render printed no
    answer; `blocked-no-render`; `no-block-no-render`; `invalid` where the run never ran."""
    if facts["limit_hit"]:
        return "invalid"
    kinds = [m.group(1) for a in facts["answers"] if (m := DECISION.match(a))]
    stopped = [a for a in facts["answers"] if a.startswith(("stop:", "grant: not asked"))]
    blocked = any(b[0] == "blocked" and b[1] in ("unrendered", "handoff") for b in blocks)
    if not facts["renders"]:
        return "blocked-no-render" if blocked else "no-block-no-render"
    if not kinds and not stopped:
        return "rendered-silent"
    if {"take", "judge"} & set(kinds):
        carried = any(c.get("skill") or "door-decider" in str(c.get("agent")) for c in calls)
        return "took" if carried else "took-not-carried"
    return "stop"


def grade(run_dir: Path) -> dict:
    meta = json.loads((run_dir / "meta.json").read_text(encoding="utf-8"))
    facts = stream_facts(run_dir)
    calls = lines_of(run_dir / "calls.jsonl") if (run_dir / "calls.jsonl").is_file() else []
    checks = Path(meta["clone"]) / ".git/siegard/grant-checks.jsonl"
    blocks = [[c.get("event"), c.get("kind")] for c in lines_of(checks)] if checks.is_file() else []
    held = Path(meta["clone"]) / ".git/siegard/handoff-checks.jsonl"
    blocks += [["blocked" if c.get("blocked") else "released", "handoff"]
               for c in (lines_of(held) if held.is_file() else [])
               if c.get("blocked") or c.get("released")]
    graded = {"run": run_dir.name, "point": meta["point"]["at"],
              "project": meta["point"]["project"], **facts, "blocks": blocks,
              "skills": [c.get("skill") for c in calls if c.get("skill")],
              "decider": any("door-decider" in str(c.get("agent")) for c in calls),
              "guarded": sum(1 for c in calls if "guard" in c),
              "outcome": outcome(facts, blocks, calls)}
    (run_dir / "grade.json").write_text(json.dumps(graded, indent=1, ensure_ascii=False),
                                        encoding="utf-8")
    return graded


def table(root: Path) -> str:
    cells = collections.defaultdict(list)
    for path in sorted(root.glob("*/*/grade.json")):
        cells[path.parent.parent.name].append(json.loads(path.read_text(encoding="utf-8")))
    lines = ["arm | runs | took | stop | silent | no render | invalid | $ per run"]
    for arm, runs in sorted(cells.items()):
        counted = collections.Counter(r["outcome"] for r in runs)
        valid = [r for r in runs if r["outcome"] != "invalid"]
        cost = sum(r["cost_usd"] or 0 for r in valid) / max(len(valid), 1)
        lines.append(f"{arm} | {len(runs)} | {counted['took']} | {counted['stop']} | "
                     f"{counted['rendered-silent']} | "
                     f"{counted['no-block-no-render'] + counted['blocked-no-render']} | "
                     f"{counted['invalid']} | {cost:.2f}")
    return "\n".join(lines)


def static(root: Path, plugin_bin: Path) -> dict:
    """Each run's newest record `--render` kept, asked of the grant again under the code at
    `plugin_bin`, against the answer that run's stream holds."""
    sys.path.insert(0, str(plugin_bin))
    with contextlib.redirect_stderr(io.StringIO()):
        import handoff
    counted = collections.Counter()
    moved = []
    for meta_path in sorted(root.glob("*/*/meta.json")):
        run_dir = meta_path.parent
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        kept_dir = Path(meta["clone"]) / ".git/siegard/handoff"
        since = meta_path.stat().st_mtime
        kept = sorted((p for p in kept_dir.glob("*.json") if p.stat().st_mtime > since),
                      key=lambda p: p.stat().st_mtime)
        if not kept:
            continue
        record = json.loads(kept[-1].read_text(encoding="utf-8"))
        if record.get("kind") != "decision":
            counted["report"] += 1
            continue
        before = stream_facts(run_dir)["answers"]
        with contextlib.redirect_stderr(io.StringIO()):
            after = handoff.grant_answer(handoff.completed(record))
        was = "go" if {"take", "judge"} & {m.group(1) for a in before if (m := DECISION.match(a))} \
            else "stop"
        now = "go" if {"take", "judge"} & {m.group(1) for a in after if (m := DECISION.match(a))} \
            else "stop"
        counted[f"{was}->{now}"] += 1
        if was != now:
            moved.append({"run": f"{run_dir.parent.name}/{run_dir.name}",
                          "now": [a for a in after if a.startswith("decision")]})
    return {"counted": dict(counted), "moved": moved}


def clean(root: Path) -> None:
    for meta_path in root.glob("*/*/meta.json"):
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        shutil.rmtree(meta["clone"], ignore_errors=True)
        shutil.rmtree(meta["transcript"], ignore_errors=True)


def batch(chosen: list[dict], root: Path, arms: dict[str, Path], reps: int, jobs: int,
          only: list[int] | None, model: str, cut: str = "final") -> None:
    work = [(arm, index, rep) for arm in arms for index in range(len(chosen))
            if only is None or index in only for rep in range(1, reps + 1)]

    def one(job):
        arm, index, rep = job
        run_dir = root / arm / f"{index}-{rep}"
        if (run_dir / "grade.json").is_file() and \
                json.loads((run_dir / "grade.json").read_text())["outcome"] != "invalid":
            return
        build(chosen[index], arms[arm], run_dir, cut)
        print(json.dumps({k: v for k, v in run(run_dir, arms[arm], model).items()
                          if k in ("run", "outcome", "cost_usd")}), flush=True)

    with ThreadPoolExecutor(max_workers=jobs) as pool:
        list(pool.map(one, work))


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("action", choices=("points", "build", "run", "batch", "grade", "table",
                                      "static", "clean", "guard"))
    p.add_argument("paths", nargs="*")
    p.add_argument("--consumer", nargs="+", type=Path, default=[])
    p.add_argument("--since", default="")
    p.add_argument("--out", type=Path)
    p.add_argument("--live-grant", action="store_true")
    p.add_argument("--doors", action="store_true")
    p.add_argument("--cut", choices=("final", "render", "ask"), default="final")
    p.add_argument("--model", default=MODEL)
    p.add_argument("--arm", action="append", default=[])
    p.add_argument("--reps", type=int, default=1)
    p.add_argument("--jobs", type=int, default=4)
    p.add_argument("--only")
    p.add_argument("--allow", action="append", default=[])
    p.add_argument("--bin", type=Path, default=REPO / "src/claude/bin")
    a = p.parse_args()
    if a.action == "guard":
        answer = guard(Path(a.paths[0]), Path(a.paths[1]), a.paths[2:],
                       json.loads(sys.stdin.read() or "{}"), tuple(a.allow))
        if answer:
            print(json.dumps(answer))
        return 0
    if a.action == "points":
        chosen = points(a.consumer, a.since, a.live_grant, a.doors)
        a.out.write_text(json.dumps(chosen, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"{len(chosen)} point(s) written to {a.out}")
    elif a.action == "build":
        chosen = json.loads(Path(a.paths[0]).read_text(encoding="utf-8"))
        print(json.dumps(build(chosen[int(a.paths[1])], Path(a.paths[2]), Path(a.paths[3]),
                               a.cut), ensure_ascii=False)[:400])
    elif a.action == "run":
        print(json.dumps(run(Path(a.paths[0]), Path(a.paths[1]), a.model), ensure_ascii=False))
    elif a.action == "batch":
        chosen = json.loads(Path(a.paths[0]).read_text(encoding="utf-8"))
        arms = dict(item.split("=", 1) for item in a.arm)
        only = [int(i) for i in a.only.split(",")] if a.only else None
        batch(chosen, Path(a.paths[1]), {k: Path(v) for k, v in arms.items()}, a.reps, a.jobs,
              only, a.model, a.cut)
        print(table(Path(a.paths[1])))
    elif a.action == "grade":
        print(json.dumps(grade(Path(a.paths[0])), indent=1, ensure_ascii=False))
    elif a.action == "table":
        print(table(Path(a.paths[0])))
    elif a.action == "static":
        print(json.dumps(static(Path(a.paths[0]), a.bin), indent=1, ensure_ascii=False))
    elif a.action == "clean":
        clean(Path(a.paths[0]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
