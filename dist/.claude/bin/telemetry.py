#!/usr/bin/env python3
"""Count how a stretch of work with this framework happened, from disk, and record the counts.

A telemetry report is a retrospective's raw material: which agents ran and what each cost, which
commands refused and how often, what the captured runs took, what stopped and what was decided.
Until this script existed that report was written from a session's own recall of the work — and
recall is the one source this framework declares non-authoritative. The token figures it produced
were plausible, and after the context had been compressed once they were guesses that read as
counts. Every figure this writes is read from a file, or is absent with the reason beside it.

**Where the numbers live.** The framework itself records the runs (`run/<slug>/run.json` under
each delivery root, with a clock on every step), the notes (`## Notes` on every plan node), the
decisions (`decision-log.md`) and the history (git). What it never recorded — which subagent was
spawned, when, by which skill, how many tokens it spent and how long it held the wall — the
harness records on its own, in the session transcripts under its projects directory: one
subdirectory per working directory, one `.jsonl` per session, and beside it a `subagents/`
directory holding one transcript and one `.meta.json` per agent spawned. That directory is the
harness's, in an internal format this framework neither owns nor documents, and it holds every
word of every conversation. Two rules follow. It is read only after `--probe` has said it can be,
and the read is announced by whoever invokes it. And what leaves it is counts, names, timestamps
and the command lines that invoked this framework's own scripts — never the text of a prompt, a
reply or a tool's result.

**The window is named, never remembered.** `--since` is an instant, or `last`, which continues
from the `until` of the newest report already in the telemetry root; `--until` defaults to now
and is recorded. Every transcript entry, run, commit and decision outside the window is outside
the report. A window inferred from when a session seemed to begin would be the recall this
replaces.

**A section that cannot be read is said, not filled.** Every section carries an entry in
`provenance` naming where it was read from or why it could not be. No source is estimated from
another: an agent whose transcript is missing has null usage and a reason, and the totals say how
many invocations they actually sum over.

**The stamp is the identity.** The report lands at `<telemetry_root>/<stamp>.json`, the stamp
being `until` in UTC to the second, and a stamp that already exists is a refusal — evidence is not
overwritten. The prose report `/siegard-telemetry` writes sits beside it under the same stem.

Declared dependencies: PyYAML, jsonschema (this script also imports spec.py and plan.py, its
siblings, for the node reading they already hold). It runs `project.py` for the roots rather than
reading `siegard.json` itself: that file has one reader.

Usage:  telemetry.py <project-root> --since <ISO-8601|last> [--until <ISO-8601>]
                     [--transcripts DIR]
            count the window and write <telemetry_root>/<stamp>.json
        telemetry.py --probe <project-root> --since <ISO-8601|last> [--until <ISO-8601>]
                     [--transcripts DIR]
            say what the full form would read — the transcript directory, whether it is
            readable, which sessions overlap the window, where the report would land — and
            write nothing
        telemetry.py --help    print this text and stop
Exit:   0 written, or probed
        1 the project declares no telemetry_root, or the stamp already has a report
        2 cannot run
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import NoReturn

try:
    import yaml
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover - exercised by the environment, not the suite
    print("cannot run: PyYAML and jsonschema are required (pip install pyyaml jsonschema)",
          file=sys.stderr)
    raise SystemExit(2)

import plan
import spec

CANNOT_RUN = 2
CONTRACT = "siegard-telemetry/1"
PLUGIN_ROOT = Path(__file__).resolve().parent.parent
TELEMETRY_CONTRACT = PLUGIN_ROOT / "schemas" / "telemetry.json"
PROJECT_PY = PLUGIN_ROOT / "bin" / "project.py"
MANIFEST = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
HARNESS_PROJECTS = Path.home() / ".claude" / "projects"

SCRIPTS = ("spec.py", "plan.py", "deliver.py", "trace.py", "project.py", "run.py", "terms.py",
           "telemetry.py")
SCRIPT_CALL = re.compile(r"bin/(" + "|".join(re.escape(s) for s in SCRIPTS) + r")\b")
EXIT_MARKER = re.compile(r"\AExit code (\d+)")
PROBLEMS = re.compile(r"\b(\d+) problem\(s\)")
FENCE = re.compile(r"\A---\n(.*?)\n---\n", re.S)
USAGE_KEYS = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens",
              "output_tokens")


def cannot_run(message: str) -> NoReturn:
    print(f"cannot run: {message}", file=sys.stderr)
    raise SystemExit(CANNOT_RUN)


# ------------------------------------------------------------------------------ time


def parse_instant(raw: str, flag: str) -> datetime:
    """An ISO-8601 instant, made timezone-aware. A naive one is read as UTC and said so below,
    rather than as the machine's locale, which would move the window between two machines."""
    text = raw.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        cannot_run(f"{flag} {raw!r} is not an ISO-8601 instant")
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def iso(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def stamp_of(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def instant_of(raw) -> datetime | None:
    """A transcript's or record's timestamp, or None where it carries none that parses."""
    if not isinstance(raw, str):
        return None
    text = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def seconds_between(first: str | None, last: str | None) -> float | None:
    a, b = instant_of(first), instant_of(last)
    if a is None or b is None:
        return None
    return round(max((b - a).total_seconds(), 0.0), 3)


# --------------------------------------------------------------------------- the roots


def resolve_roots(project_root: Path) -> dict[str, object]:
    """Every root `siegard.json` declares, read through `project.py` — the one reader. A refusal
    there is a refusal here, forwarded whole."""
    done = subprocess.run([sys.executable, "-B", str(PROJECT_PY), str(project_root)],
                          capture_output=True, text=True)
    if done.returncode != 0:
        sys.stdout.write(done.stdout)
        sys.stderr.write(done.stderr)
        raise SystemExit(done.returncode)
    roots: dict[str, object] = {"targets": {}}
    for line in done.stdout.splitlines():
        key, separator, value = line.partition(": ")
        if not separator:
            continue
        if key.startswith("target "):
            roots["targets"][key.split(" ", 1)[1]] = value
        elif key in ("specification_root", "work_root", "delivery_root", "telemetry_root"):
            roots[key] = value
    return roots


def git(home: Path, *args: str) -> subprocess.CompletedProcess | None:
    try:
        return subprocess.run(["git", "-C", str(home), *args], capture_output=True, text=True)
    except OSError:
        return None


def toplevel_of(directory: Path) -> Path:
    probe = git(directory, "rev-parse", "--show-toplevel")
    if probe is not None and probe.returncode == 0 and probe.stdout.strip():
        return Path(probe.stdout.strip())
    return directory


# ----------------------------------------------------------------------- the framework


def frontmatter_of(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError:
        return {}
    match = FENCE.match(text)
    if not match:
        return {}
    try:
        front = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return {}
    return front if isinstance(front, dict) else {}


def configured(paths: list[Path], name_of) -> list[dict]:
    rows = []
    for path in sorted(paths):
        front = frontmatter_of(path)
        rows.append({"name": name_of(path),
                     "effort": front.get("effort") if isinstance(front.get("effort"), str) else None,
                     "model": front.get("model") if isinstance(front.get("model"), str) else None})
    return rows


def framework_section() -> dict:
    version = None
    if MANIFEST.is_file():
        try:
            manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
            version = manifest.get("version") if isinstance(manifest.get("version"), str) else None
        except (OSError, json.JSONDecodeError):
            version = None
    contracts: dict[str, str] = {}
    for schema_path in sorted((PLUGIN_ROOT / "schemas").rglob("*.json")):
        try:
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        const = (schema.get("properties", {}).get("contract_version", {}) or {}).get("const")
        if isinstance(const, str):
            contracts[schema_path.relative_to(PLUGIN_ROOT / "schemas").as_posix()] = const
    return {
        "plugin_root": str(PLUGIN_ROOT),
        "version": version,
        "contracts": contracts,
        "agents": configured(list((PLUGIN_ROOT / "agents").glob("*.md")), lambda p: p.stem),
        "skills": configured(list((PLUGIN_ROOT / "skills").glob("*/SKILL.md")),
                             lambda p: p.parent.name),
    }


# ------------------------------------------------------------------------ the harness


def transcript_root_for(home: Path, override: str | None) -> Path:
    if override:
        return Path(override)
    return HARNESS_PROJECTS / re.sub(r"[^A-Za-z0-9]", "-", str(home))


def under(home: Path, cwd: str) -> bool:
    anchor = str(home).rstrip("/")
    return cwd == anchor or cwd.startswith(anchor + "/")


def session_files(root: Path, home: Path) -> list[tuple[Path, Path]]:
    """Every session transcript this project's work may sit in, as (transcript, its root).

    The harness names a transcript directory by the working directory the session opened in, so
    a session started in `<project>/backend` lands beside the project's directory under a longer
    name and the project's own directory never holds it. Those siblings are read too — any
    directory whose name extends this one's by a hyphen — but a name is only a prefix, and
    `<project>-old` extends it the same way: a sibling's session is included only where some
    `cwd` it recorded sits under this project's toplevel. The project's own directory is read
    whole, since a session there that recorded no `cwd` is still this project's."""
    files = [(path, root) for path in sorted(root.glob("*.jsonl"))]
    parent = root.parent
    if not parent.is_dir():
        return files
    for sibling in sorted(parent.iterdir()):
        if sibling == root or not sibling.is_dir() or not sibling.name.startswith(root.name + "-"):
            continue
        for path in sorted(sibling.glob("*.jsonl")):
            if any(isinstance(e.get("cwd"), str) and under(home, e["cwd"])
                   for e in entries_of(path)):
                files.append((path, sibling))
    return files


def probe_transcripts(root: Path) -> tuple[bool, str | None]:
    if not root.is_dir():
        return False, f"{root} is not a directory"
    if not os.access(root, os.R_OK | os.X_OK):
        return False, f"{root} is not readable"
    return True, None


def entries_of(path: Path):
    """Every JSON object in one transcript, in order; a line that does not parse is skipped.
    The format is the harness's, and a partial write at the tail of a live session is normal."""
    try:
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(entry, dict):
                    yield entry
    except OSError:
        return


def blocks_of(entry: dict) -> list[dict]:
    content = (entry.get("message") or {}).get("content")
    if isinstance(content, list):
        return [b for b in content if isinstance(b, dict)]
    return []


def text_of(block: dict) -> str:
    content = block.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(part.get("text", "") for part in content
                         if isinstance(part, dict) and isinstance(part.get("text"), str))
    return ""


def in_window(entry: dict, since: datetime, until: datetime) -> bool:
    moment = instant_of(entry.get("timestamp"))
    return moment is not None and since <= moment <= until


def is_human_turn(entry: dict) -> bool:
    if entry.get("type") != "user" or entry.get("isSidechain"):
        return False
    content = (entry.get("message") or {}).get("content")
    if isinstance(content, str):
        return bool(content.strip())
    blocks = blocks_of(entry)
    return bool(blocks) and not any(b.get("type") == "tool_result" for b in blocks)


def read_session(path: Path, since: datetime, until: datetime) -> tuple[dict, list, list]:
    """One session transcript: its summary row, the framework commands it issued inside the
    window, and the agents it spawned inside the window — the latter two still waiting for
    their results and their subagent transcripts."""
    session_id = path.stem
    first = last = None
    versions: set[str] = set()
    cwds: set[str] = set()
    human_turns: list[str] = []
    entries_in_window = 0
    commands: dict[str, dict] = {}
    agents: dict[str, dict] = {}
    results: dict[str, dict] = {}
    for entry in entries_of(path):
        stamp = entry.get("timestamp")
        if isinstance(stamp, str):
            first = stamp if first is None or stamp < first else first
            last = stamp if last is None or stamp > last else last
        if isinstance(entry.get("version"), str):
            versions.add(entry["version"])
        if isinstance(entry.get("cwd"), str):
            cwds.add(entry["cwd"])
        for block in blocks_of(entry):
            if block.get("type") == "tool_result" and isinstance(block.get("tool_use_id"), str):
                results[block["tool_use_id"]] = {"text": text_of(block),
                                                 "raw": entry.get("toolUseResult")}
        if not in_window(entry, since, until):
            continue
        entries_in_window += 1
        if is_human_turn(entry):
            human_turns.append(iso(instant_of(stamp)))
        if entry.get("type") != "assistant":
            continue
        for block in blocks_of(entry):
            if block.get("type") != "tool_use" or not isinstance(block.get("id"), str):
                continue
            payload = block.get("input") if isinstance(block.get("input"), dict) else {}
            if block.get("name") == "Bash":
                command = payload.get("command")
                if isinstance(command, str) and SCRIPT_CALL.search(command):
                    commands[block["id"]] = {
                        "session": session_id, "tool_use_id": block["id"],
                        "issued_at": iso(instant_of(stamp)),
                        "scripts": sorted(set(SCRIPT_CALL.findall(command))),
                        "command": command,
                    }
            elif block.get("name") == "Agent":
                agents[block["id"]] = {
                    "session": session_id, "tool_use_id": block["id"],
                    "agent_type": str(payload.get("subagent_type") or "general-purpose"),
                    "description": str(payload.get("description") or ""),
                    "invoked_at": iso(instant_of(stamp)),
                }
    for tool_use_id, command in commands.items():
        result = results.get(tool_use_id)
        command.update(exit_code=None, exit_marker=False, problems=None, interrupted=False,
                       unavailable=None)
        if result is None:
            command["unavailable"] = "the harness recorded no result for this command"
            continue
        marker = EXIT_MARKER.match(result["text"])
        if marker:
            command["exit_code"] = int(marker.group(1))
            command["exit_marker"] = True
        found = PROBLEMS.findall(result["text"])
        if found:
            command["problems"] = sum(int(n) for n in found)
        raw = result["raw"]
        if isinstance(raw, dict) and raw.get("interrupted") is True:
            command["interrupted"] = True
    for tool_use_id, agent in agents.items():
        raw = (results.get(tool_use_id) or {}).get("raw")
        agent["model"] = raw.get("resolvedModel") if isinstance(raw, dict) and isinstance(
            raw.get("resolvedModel"), str) else None
    summary = {
        "id": session_id, "path": str(path),
        "first_timestamp": first, "last_timestamp": last,
        "harness_versions": sorted(versions), "working_directories": sorted(cwds),
        "entries_in_window": entries_in_window, "human_turns_in_window": sorted(human_turns),
    }
    return summary, list(commands.values()), list(agents.values())


def subagent_metas(session_dir: Path) -> dict[str, tuple[str, Path]]:
    """tool_use_id -> (agent id, transcript path), from every `.meta.json` under a session's
    `subagents/` directory."""
    found: dict[str, tuple[str, Path]] = {}
    subagents = session_dir / "subagents"
    if not subagents.is_dir():
        return found
    for meta_path in sorted(subagents.glob("*.meta.json")):
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        tool_use_id = meta.get("toolUseId") if isinstance(meta, dict) else None
        if not isinstance(tool_use_id, str):
            continue
        transcript = meta_path.with_name(meta_path.name[:-len(".meta.json")] + ".jsonl")
        agent_id = meta_path.name[len("agent-"):-len(".meta.json")] \
            if meta_path.name.startswith("agent-") else meta_path.stem
        found[tool_use_id] = (agent_id, transcript)
    return found


def read_subagent(transcript: Path) -> dict:
    usage = dict.fromkeys(USAGE_KEYS, 0)
    first = last = None
    messages = tool_calls = 0
    model = None
    for entry in entries_of(transcript):
        stamp = entry.get("timestamp")
        if isinstance(stamp, str):
            first = stamp if first is None or stamp < first else first
            last = stamp if last is None or stamp > last else last
        if entry.get("type") != "assistant":
            continue
        message = entry.get("message") or {}
        messages += 1
        if isinstance(message.get("model"), str):
            model = message["model"]
        spent = message.get("usage")
        if isinstance(spent, dict):
            for key in USAGE_KEYS:
                value = spent.get(key)
                if isinstance(value, int) and value >= 0:
                    usage[key] += value
        tool_calls += sum(1 for b in blocks_of(entry) if b.get("type") == "tool_use")
    return {"model": model, "first_timestamp": first, "last_timestamp": last,
            "duration_seconds": seconds_between(first, last), "messages": messages,
            "tool_calls": tool_calls, "usage": usage}


def harness_section(root: Path, home: Path, since: datetime,
                    until: datetime) -> tuple[dict, list, list]:
    readable, reason = probe_transcripts(root)
    harness = {"transcript_root": str(root), "transcript_roots": [str(root)],
               "readable": readable, "reason": reason, "sessions": []}
    if not readable:
        return harness, [], []
    commands: list[dict] = []
    agents: list[dict] = []
    for path, root in session_files(root, home):
        summary, session_commands, session_agents = read_session(path, since, until)
        if summary["entries_in_window"] == 0:
            continue
        if str(root) not in harness["transcript_roots"]:
            harness["transcript_roots"].append(str(root))
        harness["sessions"].append(summary)
        commands.extend(session_commands)
        metas = subagent_metas(root / path.stem)
        for agent in session_agents:
            found = metas.get(agent["tool_use_id"])
            agent.update(agent_id=None, transcript=None, first_timestamp=None, last_timestamp=None,
                         duration_seconds=None, messages=None, tool_calls=None, usage=None,
                         unavailable=None)
            if found is None:
                agent["unavailable"] = (f"no subagents/*.meta.json under {root / path.stem} names "
                                        f"tool use {agent['tool_use_id']}")
            elif not found[1].is_file():
                agent["agent_id"] = found[0]
                agent["unavailable"] = f"{found[1]} does not exist"
            else:
                agent["agent_id"] = found[0]
                agent["transcript"] = str(found[1])
                read = read_subagent(found[1])
                agent["model"] = agent["model"] or read.pop("model")
                read.pop("model", None)
                agent.update(read)
            agents.append(agent)
    commands.sort(key=lambda c: (c["issued_at"], c["tool_use_id"]))
    agents.sort(key=lambda a: (a["invoked_at"], a["tool_use_id"]))
    seen: set[tuple[str, str]] = set()
    for agent in agents:
        key = (agent["agent_type"], agent["description"])
        agent["repeats_earlier"] = key in seen
        seen.add(key)
    return harness, commands, agents


def empty_total() -> dict:
    return {"invocations": 0, "with_transcript": 0, "duration_seconds": 0.0,
            "usage": dict.fromkeys(USAGE_KEYS, 0)}


def add_to(total: dict, agent: dict) -> None:
    total["invocations"] += 1
    if agent["usage"] is None:
        return
    total["with_transcript"] += 1
    total["duration_seconds"] = round(total["duration_seconds"]
                                      + (agent["duration_seconds"] or 0.0), 3)
    for key in USAGE_KEYS:
        total["usage"][key] += agent["usage"][key]


def totals_of(agents: list[dict]) -> dict:
    by_type: dict[str, dict] = {}
    overall = empty_total()
    for agent in agents:
        add_to(by_type.setdefault(agent["agent_type"], empty_total()), agent)
        add_to(overall, agent)
    return {"by_type": dict(sorted(by_type.items())), "overall": overall}


# --------------------------------------------------------------------------- the runs


def runs_section(delivery_root: Path | None, since: datetime, until: datetime) -> list[dict]:
    runs: list[dict] = []
    if delivery_root is None or not delivery_root.is_dir():
        return runs
    for record_path in sorted(delivery_root.glob("*/run/*/run.json")):
        try:
            record = json.loads(record_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(record, dict) or not isinstance(record.get("steps"), list):
            continue
        steps = [s for s in record["steps"] if isinstance(s, dict)]
        starts = [s.get("started_at") for s in steps if isinstance(s.get("started_at"), str)]
        ends = [s.get("ended_at") for s in steps if isinstance(s.get("ended_at"), str)]
        started = min(starts) if starts else None
        opened = instant_of(started)
        if opened is None or not (since <= opened <= until):
            continue
        runs.append({
            "initiative": record_path.parents[2].name,
            "run": record_path.parent.name,
            "path": str(record_path),
            "outcome": str(record.get("outcome")),
            "failed_step": record.get("failed_step") if isinstance(record.get("failed_step"), str)
            else None,
            "timeout_seconds": record.get("timeout_seconds")
            if isinstance(record.get("timeout_seconds"), int) else 0,
            "started_at": started,
            "ended_at": max(ends) if ends else None,
            "steps": [{
                "name": str(s.get("name")), "command": str(s.get("command")),
                "outcome": str(s.get("outcome")),
                "exit_code": s.get("exit_code") if isinstance(s.get("exit_code"), int) else None,
                "duration_seconds": seconds_between(s.get("started_at"), s.get("ended_at")),
            } for s in steps],
        })
    return runs


# --------------------------------------------------------------------- the repository


def root_of(path: str, roots: dict[str, object], home: Path) -> str:
    """Which declared root a committed path sits under, by name, or `other`."""
    absolute = (home / path).as_posix()
    named = [(k, roots[k]) for k in ("specification_root", "work_root", "delivery_root",
                                     "telemetry_root") if isinstance(roots.get(k), str)]
    named += [(f"target {name}", where) for name, where in sorted(roots["targets"].items())]
    for name, where in named:
        if absolute == where or absolute.startswith(where.rstrip("/") + "/"):
            return name
    return "other"


def repository_section(home: Path, roots: dict[str, object], since: datetime,
                       until: datetime) -> dict:
    listing = git(home, "log", f"--since={iso(since)}", f"--until={iso(until)}",
                  "--format=%H%x09%aI%x09%s")
    if listing is None:
        return {"commits": [], "uncommitted": [], "unavailable": "git is not installed"}
    if listing.returncode != 0:
        return {"commits": [], "uncommitted": [],
                "unavailable": f"git log refused: {listing.stderr.strip()}"}
    commits: list[dict] = []
    for line in listing.stdout.splitlines():
        parts = line.split("\t", 2)
        if len(parts) != 3:
            continue
        digest, when, subject = parts
        shown = git(home, "show", "--name-only", "--format=", digest)
        files_by_root: dict[str, list[str]] = {}
        for path in (shown.stdout.splitlines() if shown and shown.returncode == 0 else []):
            if path.strip():
                files_by_root.setdefault(root_of(path.strip(), roots, home), []).append(path.strip())
        commits.append({"hash": digest, "timestamp": when, "subject": subject,
                        "files_by_root": dict(sorted(files_by_root.items()))})
    status = git(home, "status", "--porcelain")
    uncommitted = [line[3:] for line in status.stdout.splitlines()] \
        if status and status.returncode == 0 else []
    return {"commits": commits, "uncommitted": uncommitted, "unavailable": None}


# ---------------------------------------------------------------------- the decisions


def entries_in(text: str) -> list[dict]:
    match = FENCE.match(text)
    if not match:
        return []
    try:
        front = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return []
    entries = front.get("entries") if isinstance(front, dict) else None
    return [e for e in entries if isinstance(e, dict)] if isinstance(entries, list) else []


def decisions_section(specification_root: Path | None, home: Path, since: datetime) -> dict:
    absent = {"log": None, "baseline": "no specification_root is declared", "total_now": None,
              "added": []}
    if specification_root is None:
        return absent
    log = specification_root / "decision-log.md"
    if not log.is_file():
        return {**absent, "baseline": f"{log} does not exist"}
    try:
        current = entries_in(log.read_text(encoding="utf-8-sig"))
    except OSError as broken:
        return {**absent, "log": str(log), "baseline": f"{log} cannot be read: {broken}"}
    try:
        relative = log.resolve().relative_to(home.resolve()).as_posix()
    except ValueError:
        return {"log": str(log), "baseline": f"{log} sits outside the git toplevel {home}; every "
                f"current entry is listed", "total_now": len(current), "added": current}
    before = git(home, "rev-list", "-1", f"--before={iso(since)}", "HEAD", "--", relative)
    if before is None or before.returncode != 0 or not before.stdout.strip():
        return {"log": str(log), "baseline": f"no commit before {iso(since)} holds {relative}; "
                f"every current entry is listed", "total_now": len(current), "added": current}
    digest = before.stdout.strip()
    shown = git(home, "show", f"{digest}:{relative}")
    baseline = entries_in(shown.stdout) if shown and shown.returncode == 0 else []
    seen = {json.dumps(e, sort_keys=True) for e in baseline}
    added = [e for e in current if json.dumps(e, sort_keys=True) not in seen]
    return {"log": str(log), "baseline": f"commit {digest}", "total_now": len(current),
            "added": added}


# -------------------------------------------------------------------- notes and scope


def initiatives_of(work_root: Path | None) -> list[Path]:
    if work_root is None or not work_root.is_dir():
        return []
    return sorted(p for p in work_root.iterdir() if p.is_dir())


def notes_section(work_root: Path | None) -> list[dict]:
    notes: list[dict] = []
    for initiative in initiatives_of(work_root):
        for path in sorted(initiative.rglob("*.md")):
            relative = path.relative_to(initiative)
            nid = plan.id_of(relative)
            if nid is None:
                continue
            front, body, problem = spec.parse_node(path)
            if problem is not None or front is None:
                continue
            if nid.startswith("task/"):
                text = plan.notes_of(body)
                for line in plan.blocking_notes_of(text):
                    notes.append({"initiative": initiative.name, "node": nid,
                                  "class": "blocking", "text": line})
                for line in plan.underdetermined_notes_of(text):
                    notes.append({"initiative": initiative.name, "node": nid,
                                  "class": "underdetermined", "text": line})
            elif nid.startswith("epic/"):
                for entry in spec.listed(front, "uncovered"):
                    if isinstance(entry, (dict, str)):
                        notes.append({"initiative": initiative.name, "node": nid,
                                      "class": "uncovered", "text": entry})
    return notes


def scope_section(work_root: Path | None, delivery_root: Path | None, home: Path,
                  commits: list[dict]) -> dict:
    committed: set[str] = set()
    for commit in commits:
        for paths in commit["files_by_root"].values():
            committed.update(paths)
    initiatives: list[dict] = []
    for initiative in initiatives_of(work_root):
        tasks = None
        graph = initiative / plan.PLAN_FILE
        if graph.is_file():
            try:
                nodes = json.loads(graph.read_text(encoding="utf-8")).get("nodes", [])
                tasks = sum(1 for n in nodes if isinstance(n, dict) and n.get("kind") == "task")
            except (OSError, json.JSONDecodeError, AttributeError):
                tasks = None
        records = None
        landed: list[str] = []
        if delivery_root is not None:
            implementation = delivery_root / initiative.name / "implementation"
            if implementation.is_dir():
                found = sorted(implementation.rglob("*.md"))
                records = len(found)
                for record in found:
                    try:
                        relative = record.resolve().relative_to(home.resolve()).as_posix()
                    except ValueError:
                        continue
                    if relative in committed:
                        landed.append(relative)
        initiatives.append({
            "slug": initiative.name,
            "live": not (initiative / plan.CLOSURE_FILE).is_file(),
            "tasks": tasks,
            "tasks_with_implementation_record": records,
            "implementation_records_committed_in_window": landed,
        })
    return {"initiatives": initiatives}


# --------------------------------------------------------------------------- the whole


def previous_until(telemetry_root: Path) -> tuple[datetime, str]:
    """`--since last`: the `until` of the newest report already there, and its path."""
    reports = sorted(telemetry_root.glob("*.json")) if telemetry_root.is_dir() else []
    for report_path in reversed(reports):
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        until = instant_of(((report.get("window") or {}) if isinstance(report, dict) else {})
                           .get("until"))
        if until is not None:
            return until, str(report_path)
    cannot_run(f"--since last names no report: {telemetry_root} holds none with a window; "
               f"name the instant this window opens at")


def provenance_of(roots: dict[str, object], harness: dict, repository: dict,
                  decisions: dict) -> list[dict]:
    def entry(section: str, source: str | None, unavailable: str | None) -> dict:
        return {"section": section, "source": source, "unavailable": unavailable}

    transcripts_ok = harness["readable"]
    transcript_source = harness["transcript_root"] if transcripts_ok else None
    transcript_reason = None if transcripts_ok else harness["reason"]
    rows = [
        entry("framework", str(PLUGIN_ROOT), None),
        entry("harness", transcript_source, transcript_reason),
        entry("agents", transcript_source, transcript_reason),
        entry("commands", transcript_source, transcript_reason),
    ]
    for key, section in (("delivery_root", "runs"), ("work_root", "notes"),
                         ("work_root", "scope")):
        where = roots.get(key)
        rows.append(entry(section, where if isinstance(where, str) else None,
                          None if isinstance(where, str) else f"siegard.json declares no {key}"))
    rows.append(entry("repository", None if repository["unavailable"] else "git",
                      repository["unavailable"]))
    rows.append(entry("decisions", decisions["log"],
                      None if decisions["log"] else decisions["baseline"]))
    return rows


def build(project_root: Path, since_raw: str, until_raw: str | None,
          transcripts: str | None) -> tuple[dict, Path, Path]:
    roots = resolve_roots(project_root)
    home = toplevel_of(project_root)
    telemetry_root = roots.get("telemetry_root")
    if not isinstance(telemetry_root, str):
        print(f"{home / 'siegard.json'}: declares no telemetry_root; a report needs a home the "
              f"project named, never one a session chose. Ready to paste:\n\n  /siegard-config\n\n"
              f"  Project root: {home}\n  telemetry_root: <directory, relative to the project "
              f"root>")
        raise SystemExit(1)
    telemetry_dir = Path(telemetry_root)
    until = parse_instant(until_raw, "--until") if until_raw else datetime.now(timezone.utc)
    if since_raw.strip() == "last":
        since, resolved_from = previous_until(telemetry_dir)
    else:
        since, resolved_from = parse_instant(since_raw, "--since"), "named"
    if since >= until:
        cannot_run(f"--since {iso(since)} is not before --until {iso(until)}")

    harness, commands, agents = harness_section(transcript_root_for(home, transcripts), home,
                                                since, until)
    delivery_root = Path(roots["delivery_root"]) if isinstance(roots.get("delivery_root"),
                                                               str) else None
    work_root = Path(roots["work_root"]) if isinstance(roots.get("work_root"), str) else None
    specification_root = Path(roots["specification_root"]) \
        if isinstance(roots.get("specification_root"), str) else None
    repository = repository_section(home, roots, since, until)
    decisions = decisions_section(specification_root, home, since)
    report = {
        "contract_version": CONTRACT,
        "project_root": str(home),
        "window": {"since": iso(since), "until": iso(until), "since_resolved_from": resolved_from},
        "generated_at": iso(datetime.now(timezone.utc)),
        "framework": framework_section(),
        "harness": harness,
        "agents": agents,
        "agent_totals": totals_of(agents),
        "commands": commands,
        "runs": runs_section(delivery_root, since, until),
        "repository": repository,
        "decisions": decisions,
        "notes": notes_section(work_root),
        "scope": scope_section(work_root, delivery_root, home, repository["commits"]),
        "provenance": provenance_of(roots, harness, repository, decisions),
    }
    return report, telemetry_dir, telemetry_dir / f"{stamp_of(until)}.json"


def receipt(report: dict, destination: Path) -> str:
    totals = report["agent_totals"]["overall"]
    lines = [
        f"window: {report['window']['since']} .. {report['window']['until']} "
        f"(since {report['window']['since_resolved_from']})",
        f"framework: {report['framework']['version'] or 'version unknown'} at "
        f"{report['framework']['plugin_root']}",
        f"transcripts: {report['harness']['transcript_root']} — "
        + ("readable" if report["harness"]["readable"] else f"unavailable: {report['harness']['reason']}")
        + f"; {len(report['harness']['sessions'])} session(s) overlap the window"
        + (f" ({len(report['harness']['transcript_roots']) - 1} sibling director"
           f"{'y' if len(report['harness']['transcript_roots']) == 2 else 'ies'} read)"
           if len(report["harness"]["transcript_roots"]) > 1 else ""),
        f"agents: {totals['invocations']} spawned, {totals['with_transcript']} with a transcript, "
        f"{totals['usage']['output_tokens']} output tokens, {totals['duration_seconds']}s",
        f"commands: {len(report['commands'])} invoking this framework's scripts, "
        f"{sum(1 for c in report['commands'] if c['exit_code'])} exiting non-zero",
        f"runs: {len(report['runs'])} captured",
        f"commits: {len(report['repository']['commits'])}; uncommitted: "
        f"{len(report['repository']['uncommitted'])}",
        f"decisions added: {len(report['decisions']['added'])} (baseline: "
        f"{report['decisions']['baseline']})",
        f"notes standing: {len(report['notes'])}",
    ]
    missing = [p for p in report["provenance"] if p["unavailable"]]
    lines.append("unavailable: " + ("; ".join(f"{p['section']} — {p['unavailable']}"
                                              for p in missing) if missing else "nothing"))
    lines.append(f"report: {destination}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(add_help=True, description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("project_root")
    parser.add_argument("--since", required=True, metavar="ISO-8601|last")
    parser.add_argument("--until", metavar="ISO-8601")
    parser.add_argument("--transcripts", metavar="DIR")
    parser.add_argument("--probe", action="store_true")
    args = parser.parse_args()

    project_root = Path(args.project_root)
    if not project_root.is_dir():
        cannot_run(f"{project_root} is not a directory")
    if not PROJECT_PY.is_file():
        cannot_run(f"{PROJECT_PY} is missing; the roots cannot be resolved without it")
    if not TELEMETRY_CONTRACT.is_file():
        cannot_run(f"{TELEMETRY_CONTRACT} is missing; nothing can be validated without it")

    if args.probe:
        roots = resolve_roots(project_root)
        home = toplevel_of(project_root)
        transcript_root = transcript_root_for(home, args.transcripts)
        readable, reason = probe_transcripts(transcript_root)
        until = parse_instant(args.until, "--until") if args.until else datetime.now(timezone.utc)
        telemetry_root = roots.get("telemetry_root")
        if args.since.strip() == "last":
            if not isinstance(telemetry_root, str):
                cannot_run("--since last needs a telemetry_root to read the previous report from")
            since, resolved_from = previous_until(Path(telemetry_root))
        else:
            since, resolved_from = parse_instant(args.since, "--since"), "named"
        print(f"window: {iso(since)} .. {iso(until)} (since {resolved_from})")
        print(f"telemetry_root: {telemetry_root if isinstance(telemetry_root, str) else 'not declared'}")
        print(f"transcripts: {transcript_root} — "
              + ("readable" if readable else f"unavailable: {reason}"))
        if readable:
            overlapping = []
            for path, root in session_files(transcript_root, home):
                summary, _, _ = read_session(path, since, until)
                if summary["entries_in_window"]:
                    overlapping.append((summary, root))
            print(f"sessions overlapping the window: {len(overlapping)}")
            for summary, root in overlapping:
                where = "" if root == transcript_root else f", from sibling directory {root}"
                print(f"  {summary['id']}: {summary['entries_in_window']} entries, "
                      f"{len(summary['human_turns_in_window'])} human turns, working "
                      f"directories {', '.join(summary['working_directories']) or 'unrecorded'}"
                      f"{where}")
        print("what leaves the transcripts: agent types, descriptions, token counts, timestamps, "
              "and the command lines that invoked this framework's scripts — no message text")
        if isinstance(telemetry_root, str):
            destination = Path(telemetry_root) / f"{stamp_of(until)}.json"
            print(f"would write: {destination}"
                  + (" — which already exists; this stamp is taken" if destination.exists() else ""))
        return 0

    report, telemetry_dir, destination = build(project_root, args.since, args.until,
                                               args.transcripts)
    if destination.exists():
        print(f"{destination} already exists; a second report under one stamp would overwrite the "
              f"evidence of the first — close this window at a later --until")
        return 1
    report["written_to"] = str(destination)
    schema = json.loads(TELEMETRY_CONTRACT.read_text(encoding="utf-8"))
    problems = sorted(Draft202012Validator(schema).iter_errors(report), key=str)
    if problems:
        # A report this script's own contract refuses is a defect here, not in the project; it
        # is refused before it lands so that nothing downstream reads a shape nobody validated.
        for error in problems:
            where = ".".join(str(p) for p in error.absolute_path) or "top level"
            print(f"cannot run: the report violates {TELEMETRY_CONTRACT.name} at {where}: "
                  f"{error.message}", file=sys.stderr)
        return CANNOT_RUN
    try:
        telemetry_dir.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                               encoding="utf-8")
    except OSError as broken:
        cannot_run(f"cannot write {destination}: {broken}")
    print(receipt(report, destination))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
