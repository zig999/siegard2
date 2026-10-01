#!/usr/bin/env python3
"""Count how a stretch of work with this framework happened, from disk, and record the counts.

A telemetry report is a retrospective's raw material: which agents ran and what each cost, which
commands refused and how often, what the captured runs took, what stopped and what was decided.
A report written from a session's own recall of the work would rest on the one source this
framework declares non-authoritative: recalled token figures are plausible, and after a context
compression they are guesses that read as
counts. Every figure this writes is read from a file, or is absent with the reason beside it.

**Where the numbers live.** The framework itself records the runs (`run/<slug>/run.json` under
each delivery root, with a clock on every step), the notes (`## Notes` on every plan node), the
decisions (`<slug>.log.md` beside each node) and the history (git). What it never records — which subagent was
spawned, when, by which skill, how many tokens it spent and how long it held the wall — the
harness records on its own, in the session transcripts under its projects directory: one
subdirectory per working directory, one `.jsonl` per session, and beside it a `subagents/`
directory holding one transcript and one `.meta.json` per agent spawned — at every depth, so an
agent an agent spawned lands there too, and is found by reading its parent's transcript for the
spawn the way the session's is read. That directory is the
harness's, in an internal format this framework neither owns nor documents, and it holds every
word of every conversation. Two rules follow. It is read only after `--probe` has said it can be,
and the read is announced by whoever invokes it. And what leaves it is counts, names, timestamps
and the command lines that invoked this framework's own scripts — never the text of a prompt, a
reply or a tool's result. One directory the probe cannot promise: a session opened in a git
worktree sited outside this project's own tree — the parallel-frontier route's `../wt-<task>` —
transcribes under a harness directory this probe never lists. Where `git worktree list` names
such worktrees at probe time, the probe says so and `--transcripts DIR` is the door; a worktree
already removed left nothing to announce, so the receipt is honest only about what still exists.

**The window is named, never remembered.** `--since` is an instant, or `last`, which continues
from the `until` of the newest report already in the telemetry root; `--until` defaults to now
and is recorded. Every transcript entry, run, commit and decision outside the window is outside
the report. A window inferred from when a session seemed to begin would be the recall this
replaces.

**A decision is followed to the node it filled.** The log records what the framework decided on
the human's behalf; nothing records whether anyone read it afterwards, and «the share of
disclosed decisions later revised, by which route and how long after, is reported by the
telemetry, so the trade that removed the stop stays measured rather than assumed» (SPEC-001 R10).
So every decision the window added carries its `outcome`: the commit that landed it, whether the
field it filled reads today as that commit wrote it, and — where it does not — every later commit
that changed the field, with its route read off the one subject a skill writes: `/deliver-scope`
is the only entry point that commits, and every other commit is a person's. Only a corrective
increment or a hand edit is a person disagreeing; a delivery that re-authors the field without
naming a correction is the framework revising itself, and the tally keeps the two apart. The comparison is field against field, never
the log's `decided` text against the field: the log paraphrases.

**The session's own cost is attributed to the skill it was running.** A `Skill` call in the
transcript names what the session runs from there to the next such call, and every turn's usage
in that span is that skill's — a ceiling per skill, since the person's own turns land in the span
too, said as one. `harness.skill_totals` sums it across sessions; a report that read
`agent_totals` alone would miss this half, and one that read the session total alone could not say
which skill spent it.

**A message is counted once.** The harness writes an assistant message received in several
content blocks as several transcript entries, each carrying the message's whole `usage`. Every
count here is per message, grouped by `message.id`, each figure the largest any of its entries
states — so a session's or an agent's usage is what the API calls cost, not that cost times the
blocks each call returned.

**A compaction is counted where it falls.** The harness records one in the transcript each time
it replaces a context with a summary of it — in a session under the skill whose span it falls in,
and in an agent's own transcript as a count. Past one, what the context holds of its earlier
reading is a paraphrase; an invocation that reaches one has outgrown its window, and whether a
skill's invocations do is a count this reads rather than an impression.

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
CONTRACT = "siegard-telemetry/8"
STANDS, REVISED, NODE_GONE, UNREADABLE, UNLOCATED = ("stands", "revised", "node-gone",
                                                     "unreadable", "unlocated")
OUTCOME_STATES = {
    STANDS: "the field the decision filled reads today as it read in the commit that landed it",
    REVISED: "the field changed after the decision landed; `revised_by` says by which commits and "
             "which route, and only `corrective` and `hand-edit` are a person disagreeing",
    NODE_GONE: "the node the decision located is no longer in the specification",
    UNREADABLE: "the located field could not be read at the landing commit — the log names a "
                "field the node did not hold when the entry was written",
    UNLOCATED: "no commit of the node's log contains this entry: it stands in the working tree "
               "only, or the log was rewritten rather than appended to",
}
CORRECTIVE, FRAMEWORK, HAND_EDIT = "corrective", "framework", "hand-edit"
ROUTES = {
    CORRECTIVE: "a /deliver-scope commit whose slug names a correction — corrective, hotfix, fix, "
                "abandon or revert — read as behavior contradicting the decision and a person "
                "routing the correction; the reading rests on the slug's words",
    FRAMEWORK: "a /deliver-scope commit whose slug names no correction — the framework "
               "re-authoring the field",
    HAND_EDIT: "a commit no framework skill wrote — a person changed the artifact directly",
}
ROUTE_PREFIX = re.compile(r"^deliver-scope [^\s:]+:")
CORRECTION_WORDS = re.compile(r"corrective|hotfix|\bfix\b|abandon|revert", re.I)
PLUGIN_ROOT = Path(__file__).resolve().parent.parent
TELEMETRY_CONTRACT = PLUGIN_ROOT / "schemas" / "telemetry.json"
PROJECT_PY = PLUGIN_ROOT / "bin" / "project.py"
MANIFEST = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
HARNESS_PROJECTS = Path.home() / ".claude" / "projects"


def plugin_namespace() -> str | None:
    """The prefix the harness gives this plugin's own subagents, read from `plugin.json`'s own
    `name` rather than restated: a scoped spawn (`siegard:codebase-surveyor`) and a bare one
    (`codebase-surveyor`) count as the same agent type, which `framework.agents` names bare."""
    if not MANIFEST.is_file():
        return None
    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    name = manifest.get("name")
    return name if isinstance(name, str) and name else None


def agent_type_of(payload: dict) -> str:
    raw = payload.get("subagent_type")
    if not isinstance(raw, str) or not raw:
        return "general-purpose"
    namespace = plugin_namespace()
    if namespace and raw.startswith(f"{namespace}:"):
        return raw[len(namespace) + 1:]
    return raw

SCRIPTS = ("spec.py", "plan.py", "deliver.py", "trace.py", "project.py", "run.py", "telemetry.py")
SCRIPT_CALL = re.compile(r"(?:^|[\s/])(" + "|".join(re.escape(s) for s in SCRIPTS) + r")\b")
EXIT_MARKER = re.compile(r"\AExit code (\d+)")
PROBLEMS = re.compile(r"\b(\d+) problem\(s\)")
FENCE = re.compile(r"\A---\n(.*?)\n---\n", re.S)
USAGE_KEYS = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens",
              "output_tokens")


class MessageUsage:
    """The usage of a transcript's assistant messages, one count per message.

    The harness writes a message it received in several content blocks as several transcript
    entries, and every one of them carries the message's `usage`: the input and cache figures
    repeated, `output_tokens` growing to its final value on the last. Summed per entry, one API
    call is counted once per block. So entries are grouped by `message.id`, each key keeps its
    largest value across the group, and the message is attributed to the skill named at its last
    entry. An entry carrying no message id is its own message."""

    def __init__(self) -> None:
        self.messages: dict[str, dict] = {}

    def add(self, entry: dict, skill: str | None = None) -> None:
        message = entry.get("message") or {}
        key = message.get("id") if isinstance(message.get("id"), str) \
            else f"entry:{len(self.messages)}"
        held = self.messages.setdefault(key, {"usage": dict.fromkeys(USAGE_KEYS, 0),
                                              "skill": skill})
        held["skill"] = skill
        spent = message.get("usage")
        if isinstance(spent, dict):
            for name in USAGE_KEYS:
                value = spent.get(name)
                if isinstance(value, int) and value >= 0 and value > held["usage"][name]:
                    held["usage"][name] = value

    def total(self) -> dict:
        usage = dict.fromkeys(USAGE_KEYS, 0)
        for held in self.messages.values():
            for name in USAGE_KEYS:
                usage[name] += held["usage"][name]
        return usage

    def by_skill(self) -> dict[str, dict]:
        shares: dict[str, dict] = {}
        for held in self.messages.values():
            share = shares.setdefault(held["skill"] or "none",
                                      {"turns": 0, "usage": dict.fromkeys(USAGE_KEYS, 0)})
            share["turns"] += 1
            for name in USAGE_KEYS:
                share["usage"][name] += held["usage"][name]
        return shares


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


TRANSCRIPT_KEYS = ("type", "timestamp", "message")


def probe_transcripts(root: Path) -> tuple[bool, str | None]:
    """Whether the root can be read, and whether what it holds is the shape this reader counts.
    The format is the harness's and undocumented: a transcript whose entries carry other keys
    parses cleanly and counts as nothing, and a report over it would read as zero sessions and
    complete. So the newest transcript must hold at least one entry carrying every key the
    counting reads; a root holding no transcript at all is an honest zero."""
    if not root.is_dir():
        return False, f"{root} is not a directory"
    if not os.access(root, os.R_OK | os.X_OK):
        return False, f"{root} is not readable"
    try:
        newest = max(root.rglob("*.jsonl"), key=lambda path: path.stat().st_mtime, default=None)
    except OSError as broken:
        return False, f"{root} cannot be listed: {broken}"
    if newest is None:
        return True, None
    if not any(all(key in entry for key in TRANSCRIPT_KEYS) for entry in entries_of(newest)):
        return False, (f"{newest}: no entry carries the keys this reader counts: "
                       f"{', '.join(TRANSCRIPT_KEYS)}")
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


HARNESS_BLOCK = re.compile(
    r"<(task-notification|system-reminder|local-command-caveat|local-command-stdout|command-name|"
    r"command-message|command-args)\b[^>]*>.*?</\1>", re.S)
HARNESS_LINE = re.compile(r"^\s*\[SYSTEM NOTIFICATION[^\n]*$", re.M)


def is_human_turn(entry: dict) -> bool:
    """Whether a user-role entry is a person typing. The harness writes in that role too — a
    background task's completion notice, a local command's echo, a reminder it injects — and
    counted as they land, those can outnumber the person many times over. What remains after those blocks are removed is what a person wrote; a paste a person made stays,
    because the pasting was theirs."""
    if entry.get("type") != "user" or entry.get("isSidechain"):
        return False
    content = (entry.get("message") or {}).get("content")
    if isinstance(content, str):
        text = content
    else:
        blocks = blocks_of(entry)
        if not blocks or any(b.get("type") == "tool_result" for b in blocks):
            return False
        text = " ".join(text_of(b) for b in blocks if b.get("type") == "text")
    text = HARNESS_LINE.sub("", HARNESS_BLOCK.sub("", text))
    return bool(text.strip())


def read_session(path: Path, since: datetime, until: datetime) -> tuple[dict, list, list]:
    """One session transcript: its summary row — including the tokens its own turns spent inside
    the window, the half of a run's cost `agent_totals` alone never carried — the framework
    commands it issued inside the window, and the agents it spawned inside the window — the
    latter two still waiting for their results and their subagent transcripts."""
    session_id = path.stem
    first = last = None
    versions: set[str] = set()
    cwds: set[str] = set()
    human_turns: list[str] = []
    entries_in_window = 0
    commands: dict[str, dict] = {}
    agents: dict[str, dict] = {}
    results: dict[str, dict] = {}
    spent = MessageUsage()
    namespace = plugin_namespace()
    skill: str | None = None
    compactions: list[dict] = []
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
        if is_compaction(entry):
            compactions.append(dict(compaction_of(entry), at=iso(instant_of(stamp)),
                                    skill=skill or "none"))
        if entry.get("type") != "assistant":
            continue
        for block in blocks_of(entry):
            # A Skill call names the skill the session runs from here to the next one; the
            # turn that launched it is already that skill's.
            if block.get("type") == "tool_use" and block.get("name") == "Skill":
                named = (block.get("input") or {}).get("skill") if isinstance(block.get("input"),
                                                                             dict) else None
                if isinstance(named, str) and named:
                    if namespace and named.startswith(f"{namespace}:"):
                        named = named[len(namespace) + 1:]
                    skill = named
        spent.add(entry, skill)
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
                agents[block["id"]] = spawn_of(block, payload, session_id, stamp)
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
        agent["model"] = resolved_model_of(results.get(tool_use_id))
    summary = {
        "id": session_id, "path": str(path),
        "first_timestamp": first, "last_timestamp": last,
        "harness_versions": sorted(versions), "working_directories": sorted(cwds),
        "entries_in_window": entries_in_window, "human_turns_in_window": sorted(human_turns),
        "usage": spent.total(), "by_skill": spent.by_skill(), "compactions": compactions,
    }
    return summary, list(commands.values()), list(agents.values())


def is_compaction(entry: dict) -> bool:
    return entry.get("type") == "system" and entry.get("subtype") == "compact_boundary"


def compaction_of(entry: dict) -> dict:
    """What the harness recorded about one compaction: its cause and the context's size either
    side of it, each null where the entry does not carry it."""
    meta = entry.get("compactMetadata") if isinstance(entry.get("compactMetadata"), dict) else {}

    def count(key: str) -> int | None:
        value = meta.get(key)
        return value if isinstance(value, int) and value >= 0 else None

    trigger = meta.get("trigger")
    return {"trigger": trigger if isinstance(trigger, str) else None,
            "pre_tokens": count("preTokens"), "post_tokens": count("postTokens")}


def spawn_of(block: dict, payload: dict, session_id: str, stamp: str | None) -> dict:
    return {
        "session": session_id, "tool_use_id": block["id"],
        "agent_type": agent_type_of(payload),
        "description": str(payload.get("description") or ""),
        "invoked_at": iso(instant_of(stamp)),
    }


def resolved_model_of(result: dict | None) -> str | None:
    raw = (result or {}).get("raw")
    if isinstance(raw, dict) and isinstance(raw.get("resolvedModel"), str):
        return raw["resolvedModel"]
    return None


def spawns_in(transcript: Path, session_id: str, since: datetime, until: datetime) -> list[dict]:
    """Every `Agent` tool use an agent's own transcript holds inside the window — what it
    spawned, in the same shape a session's spawns take. A fork's transcript opens with a copy
    of the context it was forked from, spawns included, so the caller attributes a tool use to
    the first transcript it was read from and never twice."""
    agents: dict[str, dict] = {}
    for entry in entries_of(transcript):
        for block in blocks_of(entry):
            if block.get("type") == "tool_result" and block.get("tool_use_id") in agents:
                agents[block["tool_use_id"]]["model"] = resolved_model_of(
                    {"raw": entry.get("toolUseResult")})
        if entry.get("type") != "assistant" or not in_window(entry, since, until):
            continue
        for block in blocks_of(entry):
            if block.get("type") != "tool_use" or block.get("name") != "Agent" \
                    or not isinstance(block.get("id"), str):
                continue
            payload = block.get("input") if isinstance(block.get("input"), dict) else {}
            agents[block["id"]] = dict(spawn_of(block, payload, session_id, entry.get("timestamp")),
                                       model=None)
    return list(agents.values())


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
    spent = MessageUsage()
    first = last = None
    tool_calls = compactions = 0
    model = None
    for entry in entries_of(transcript):
        stamp = entry.get("timestamp")
        if isinstance(stamp, str):
            first = stamp if first is None or stamp < first else first
            last = stamp if last is None or stamp > last else last
        if is_compaction(entry):
            compactions += 1
        if entry.get("type") != "assistant":
            continue
        message = entry.get("message") or {}
        if isinstance(message.get("model"), str):
            model = message["model"]
        spent.add(entry)
        tool_calls += sum(1 for b in blocks_of(entry) if b.get("type") == "tool_use")
    return {"model": model, "first_timestamp": first, "last_timestamp": last,
            "duration_seconds": seconds_between(first, last), "messages": len(spent.messages),
            "tool_calls": tool_calls, "compactions": compactions, "usage": spent.total()}


def harness_section(root: Path, home: Path, since: datetime,
                    until: datetime) -> tuple[dict, list, list]:
    readable, reason = probe_transcripts(root)
    harness = {"transcript_root": str(root), "transcript_roots": [str(root)],
               "readable": readable, "reason": reason, "sessions": [], "skill_totals": {}}
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
        pending = [dict(agent, spawn_depth=1, parent_agent_id=None) for agent in session_agents]
        seen = {agent["tool_use_id"] for agent in pending}
        while pending:
            agent = pending.pop(0)
            found = metas.get(agent["tool_use_id"])
            agent.update(agent_id=None, transcript=None, first_timestamp=None, last_timestamp=None,
                         duration_seconds=None, messages=None, tool_calls=None, compactions=None,
                         usage=None, unavailable=None)
            if found is None:
                agent["unavailable"] = (f"no subagents/*.meta.json under {root / path.stem} names "
                                        f"tool use {agent['tool_use_id']}; whatever this agent "
                                        f"spawned is uncounted")
            elif not found[1].is_file():
                agent["agent_id"] = found[0]
                agent["unavailable"] = (f"{found[1]} does not exist; whatever this agent spawned "
                                        f"is uncounted")
            else:
                agent["agent_id"] = found[0]
                agent["transcript"] = str(found[1])
                read = read_subagent(found[1])
                agent["model"] = agent["model"] or read.pop("model")
                read.pop("model", None)
                agent.update(read)
                for child in spawns_in(found[1], summary["id"], since, until):
                    if child["tool_use_id"] in seen:
                        continue
                    seen.add(child["tool_use_id"])
                    pending.append(dict(child, spawn_depth=agent["spawn_depth"] + 1,
                                        parent_agent_id=found[0]))
            agents.append(agent)
    # The session side of the cost, by the skill the session was running. A session's own turns
    # are half of what a stretch of work costs, and which skill each half belongs to is what a
    # reader needs before shortening anything.
    totals: dict[str, dict] = {}
    for summary in harness["sessions"]:
        for name, share in summary["by_skill"].items():
            into = totals.setdefault(name, {"turns": 0, "sessions": 0, "compactions": 0,
                                            "usage": dict.fromkeys(USAGE_KEYS, 0)})
            into["turns"] += share["turns"]
            into["sessions"] += 1
            for key in USAGE_KEYS:
                into["usage"][key] += share["usage"][key]
        for compaction in summary["compactions"]:
            totals.setdefault(compaction["skill"], {"turns": 0, "sessions": 0, "compactions": 0,
                                                    "usage": dict.fromkeys(USAGE_KEYS, 0)})
            totals[compaction["skill"]]["compactions"] += 1
    harness["skill_totals"] = dict(sorted(totals.items()))
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


def closing_commit(home: Path, until: datetime) -> tuple[bool, str | None]:
    """The commit a window closing at `until` reads the repository at: (False, None) where the
    last commit is at or before `until` and the working tree is what stands at the close;
    (True, <commit>) where later commits exist, the commit being the last at or before `until`
    — None where the window closes before the first commit."""
    head = git(home, "rev-parse", "--verify", "-q", "HEAD")
    if head is None or head.returncode != 0 or not head.stdout.strip():
        return False, None
    cut = git(home, "rev-list", "-1", f"--before={iso(until)}", "HEAD")
    digest = cut.stdout.strip() if cut and cut.returncode == 0 else ""
    if digest == head.stdout.strip():
        return False, None
    return True, digest or None


LOG_SUFFIX = ".log.md"


def is_log(relative: str) -> bool:
    """Whether a specification-relative path is a node's decision log, `<slug>.log.md` — read
    by the same classifier the validator uses, so what telemetry counts is what validates."""
    placed = spec.classify(Path(relative))
    return placed is not None and placed[0] == "log"


def logs_in_tree(specification_root: Path) -> list[str]:
    return sorted(p.relative_to(specification_root).as_posix()
                  for p in specification_root.rglob(f"*{LOG_SUFFIX}")
                  if is_log(p.relative_to(specification_root).as_posix()))


def logs_at(home: Path, commit: str, spec_relative: str) -> list[str]:
    """Every decision log the specification held at `commit`, specification-relative."""
    scope = [] if spec_relative == "." else [spec_relative]
    listed = git(home, "ls-tree", "-r", "--name-only", commit, "--", *scope)
    if listed is None or listed.returncode != 0:
        return []
    prefix = "" if spec_relative == "." else spec_relative + "/"
    found = []
    for line in listed.stdout.splitlines():
        if not line.endswith(LOG_SUFFIX) or not line.startswith(prefix):
            continue
        relative = line[len(prefix):]
        if is_log(relative):
            found.append(relative)
    return sorted(found)


def node_of(log_relative: str) -> str:
    """The identity of the node a decision log sits beside, from the log's own path."""
    return log_relative[:-len(LOG_SUFFIX)]


def decisions_section(specification_root: Path | None, home: Path, since: datetime,
                      until: datetime) -> dict:
    """What the decision logs gained inside the window — one log beside each node, read one by
    one against its own baseline. A window closing before the last commit reads every log as it
    stood at the last commit at or before `until`, and follows each decision only that far: a
    decision committed after the close is outside the window, and so is a revision."""
    absent = {"log": None, "baseline": "no specification_root is declared", "total_now": None,
              "added": [], "retired": [], "outcomes": outcomes_of([])}
    if specification_root is None:
        return absent
    bounded, cut = closing_commit(home, until)
    try:
        spec_relative = specification_root.resolve().relative_to(home.resolve()).as_posix()
    except ValueError:
        spec_relative = None
    logs: list[dict] = []
    current_all: list[dict] = []
    added_all: list[dict] = []

    def repo_path(relative: str) -> str:
        return relative if spec_relative in (None, ".") else f"{spec_relative}/{relative}"

    if spec_relative is None:
        for relative in logs_in_tree(specification_root):
            try:
                current = entries_in((specification_root / relative).read_text(encoding="utf-8-sig"))
            except OSError as broken:
                logs.append({"path": relative, "baseline": f"cannot be read: {broken}"})
                continue
            logs.append({"path": relative, "baseline": f"sits outside the git toplevel {home}; "
                         f"every current entry is listed"})
            for entry in current:
                entry["node"] = node_of(relative)
            current_all += current
            added_all += current
        decided, retired = apart_from_retirements(added_all)
        return {"log": logs, "baseline": f"{len(logs)} log(s) read outside git; every current "
                f"entry is listed", "total_now": len(current_all), "added": decided,
                "retired": retired, "outcomes": outcomes_of(decided)}
    if bounded:
        if cut is None:
            return {"log": [], "baseline": f"no commit is at or before {iso(until)}; the window "
                    f"closes before the specification's history begins", "total_now": 0,
                    "added": [], "retired": [], "outcomes": outcomes_of([])}
        paths = logs_at(home, cut, spec_relative)
    else:
        paths = logs_in_tree(specification_root)
    upto = cut if bounded else None
    with_baseline = 0
    for relative in paths:
        at_repo = repo_path(relative)
        if bounded:
            held = git(home, "show", f"{cut}:{at_repo}")
            current = entries_in(held.stdout) if held and held.returncode == 0 else []
        else:
            try:
                current = entries_in((specification_root / relative).read_text(encoding="utf-8-sig"))
            except OSError as broken:
                logs.append({"path": at_repo, "baseline": f"cannot be read: {broken}"})
                continue
        before = git(home, "rev-list", "-1", f"--before={iso(since)}", "HEAD", "--", at_repo)
        if before is None or before.returncode != 0 or not before.stdout.strip():
            baseline_said = (f"no commit before {iso(since)} holds {at_repo}; every current "
                             f"entry is listed")
            added = list(current)
        else:
            digest = before.stdout.strip()
            baseline_said = f"commit {digest}"
            with_baseline += 1
            shown = git(home, "show", f"{digest}:{at_repo}")
            baseline = entries_in(shown.stdout) if shown and shown.returncode == 0 else []
            seen = {json.dumps(e, sort_keys=True) for e in baseline}
            added = [e for e in current if json.dumps(e, sort_keys=True) not in seen]
        logs.append({"path": at_repo, "baseline": baseline_said})
        for entry in added:
            entry["node"] = node_of(relative)
        current_all += current
        added_all += added
    added, retired = apart_from_retirements(added_all)
    for entry in added:
        entry["outcome"] = outcome_of(entry, home, spec_relative, specification_root, upto)
    return {"log": logs,
            "baseline": f"{len(logs)} log(s) read, {with_baseline} with a commit before "
                        f"{iso(since)}; each log's own baseline is under `log`",
            "total_now": len(current_all), "added": added, "retired": retired,
            "outcomes": outcomes_of(added)}


def apart_from_retirements(entries: list[dict]) -> tuple[list[dict], list[dict]]:
    """The entries that record a decision or a reading, and the ones that retire a field.

    A retirement decides nothing: it says where an earlier decision went when its node or field
    left the specification. Followed to its field like a decision, it would read as a decision
    whose node is gone — the opposite of what it records."""
    return ([e for e in entries if "retired" not in e], [e for e in entries if "retired" in e])


def route_of(subject: str) -> str:
    """Which route a commit that changed a decided field came through, read off the one subject a
    shipped skill writes: `/deliver-scope` is the only entry point that commits, every commit it
    makes opens `deliver-scope <slug>:`, and a subject with no such opening is a person's.
    Authorship separates nothing here — every commit a skill makes is made under the human's
    identity. Whether a deliver-scope commit is corrective rests on its slug's words, which the
    human's ask chose: a heuristic, and `route_meanings` says so beside every count."""
    if not ROUTE_PREFIX.match(subject or ""):
        return HAND_EDIT
    return CORRECTIVE if CORRECTION_WORDS.search(subject) else FRAMEWORK


def field_of(front: object, dotted: str) -> tuple[bool, object]:
    """The value a dotted field path reaches in a node's frontmatter, and whether it reached."""
    current = front
    for part in dotted.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, list) and part.isdigit() and int(part) < len(current):
            current = current[int(part)]
        else:
            return False, None
    return True, current


def field_in_text(text: str, dotted: str) -> tuple[bool, object]:
    match = FENCE.match(text or "")
    if not match:
        return False, None
    try:
        front = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return False, None
    return field_of(front, dotted)


def flat(value: object) -> str:
    return re.sub(r"\s+", " ", json.dumps(value, sort_keys=True, ensure_ascii=False)
                  if isinstance(value, (dict, list)) else str(value)).strip()


def outcome_of(entry: dict, home: Path, spec_relative: str, specification_root: Path,
               upto: str | None = None) -> dict:
    """What became of one decision the framework made on the human's behalf, read from the node
    it sits beside rather than from the log: the log records what was decided, and the node
    records what stands. The comparison is the field as the landing commit wrote it against the
    field today — never the log's `decided` text against the field, because the log paraphrases
    and the paraphrase is not the value.

    The landing commit is exact: the first commit of the node's own log whose entries contain
    this one, read by following the log through its renames — a log moves with its node, one
    path at a time, so `--follow` on that one path is the whole of what a rename needs. The
    route of every later commit over the node is read off the subject the skills write, and the
    states are printed with their meaning beside them, because the one reading that matters —
    was this a person disagreeing, or the framework re-deciding itself — is not a count.

    `upto` is the commit a window closing before the last commit reads at: "today" is then that
    commit, the node is read there rather than in the working tree, and no later commit is a
    revision the window saw."""
    tip = upto or "HEAD"
    node = str(entry.get("node") or "")
    at_repo = (lambda rel: rel if spec_relative in (None, ".") else f"{spec_relative}/{rel}")
    log_relative = at_repo(f"{node}{LOG_SUFFIX}")
    node_relative = at_repo(f"{node}.md")
    field = str(entry.get("field") or "")
    wanted = json.dumps({k: v for k, v in entry.items() if k not in ("node", "outcome")},
                        sort_keys=True)
    # `--follow` walks newest to oldest and does not combine with `--reverse`; the history is
    # collected as git emits it and read oldest first here.
    listing = git(home, "log", "--follow", "--format=%H%x09%aI", "--name-only", tip, "--",
                  log_relative)
    history: list[tuple[str, str, str]] = []
    if listing is not None and listing.returncode == 0:
        commit = at = None
        for line in listing.stdout.splitlines():
            if "\t" in line and len(line.split("\t", 1)[0]) == 40:
                commit, at = line.split("\t", 1)
                continue
            if line.strip() and commit is not None:
                history.append((commit, at, line.strip()))
                commit = None
    landed = None
    node_then = node_relative
    for commit, at, path_then in reversed(history):
        shown = git(home, "show", f"{commit}:{path_then}")
        held = entries_in(shown.stdout) if shown and shown.returncode == 0 else []
        if wanted in {json.dumps(e, sort_keys=True) for e in held}:
            landed = {"commit": commit, "at": at}
            node_then = path_then[:-len(LOG_SUFFIX)] + ".md"
            break
    if landed is None:
        return {"landed": None, "state": UNLOCATED, "value_now": None, "revised_by": [],
                "days_to_first_revision": None}
    commit, at = landed["commit"], landed["at"]
    shown = git(home, "show", f"{commit}:{node_then}")
    if shown is None or shown.returncode != 0:
        return {"landed": landed, "state": UNREADABLE, "value_now": None, "revised_by": [],
                "days_to_first_revision": None}
    held, value_landed = field_in_text(shown.stdout, field)
    if not held:
        return {"landed": landed, "state": UNREADABLE, "value_now": None, "revised_by": [],
                "days_to_first_revision": None}
    if upto is not None:
        standing = git(home, "show", f"{upto}:{node_relative}")
        if standing is None or standing.returncode != 0:
            return {"landed": landed, "state": NODE_GONE, "value_now": None, "revised_by": [],
                    "days_to_first_revision": None}
        held_now, value_now = field_in_text(standing.stdout, field)
    else:
        now_path = specification_root / f"{node}.md"
        if not now_path.is_file():
            return {"landed": landed, "state": NODE_GONE, "value_now": None, "revised_by": [],
                    "days_to_first_revision": None}
        try:
            held_now, value_now = field_in_text(now_path.read_text(encoding="utf-8-sig"), field)
        except OSError:
            held_now, value_now = False, None
    revised_by: list[dict] = []
    later = git(home, "log", "--reverse", "--format=%H%x09%aI%x09%s", f"{commit}..{tip}", "--",
                node_relative)
    previous = flat(value_landed)
    for line in (later.stdout.splitlines() if later and later.returncode == 0 else []):
        parts = line.split("\t", 2)
        if len(parts) != 3:
            continue
        at_commit = git(home, "show", f"{parts[0]}:{node_relative}")
        held_then, value_then = field_in_text(at_commit.stdout if at_commit else "", field)
        current = flat(value_then) if held_then else "<field-missing>"
        if current != previous:
            revised_by.append({"commit": parts[0], "at": parts[1], "subject": parts[2],
                               "route": route_of(parts[2])})
            previous = current
    state = STANDS if held_now and flat(value_now) == flat(value_landed) else REVISED
    if state == REVISED and not revised_by and upto is None:
        # The tree differs from every commit: an uncommitted edit stands on the field.
        revised_by.append({"commit": None, "at": None, "subject": "(uncommitted)",
                           "route": HAND_EDIT})
    days = None
    if revised_by and revised_by[0]["at"]:
        days = seconds_between(at, revised_by[0]["at"])
        days = round(days / 86400, 2) if days is not None else None
    return {"landed": landed, "state": state, "value_now": value_now if held_now else None,
            "revised_by": revised_by, "days_to_first_revision": days}


def outcomes_of(added: list[dict]) -> dict:
    """The tally beside the entries: how many decisions stand, how many were revised and by which
    route. Counts and the vocabulary — never a share: what a reader acts on is the list of the
    revised ones, each with its commit, and the one line that says which routes are a person
    disagreeing."""
    states = {state: 0 for state in OUTCOME_STATES}
    routes = {route: 0 for route in ROUTES}
    for entry in added:
        outcome = entry.get("outcome") or {}
        states[outcome.get("state", UNLOCATED)] += 1
        if outcome.get("state") == REVISED and outcome.get("revised_by"):
            routes[outcome["revised_by"][0]["route"]] += 1
    return {"states": states, "first_revision_by_route": routes,
            "state_meanings": OUTCOME_STATES, "route_meanings": ROUTES}


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
    logs = decisions["log"]
    rows.append(entry("decisions",
                      f"{len(logs)} decision log(s) beside the specification's nodes"
                      if isinstance(logs, list) else None,
                      None if isinstance(logs, list) else decisions["baseline"]))
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
    decisions = decisions_section(specification_root, home, since, until)
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
    session_usage = dict.fromkeys(USAGE_KEYS, 0)
    for session in report["harness"]["sessions"]:
        for key in USAGE_KEYS:
            session_usage[key] += session["usage"][key]
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
        f"agents: {totals['invocations']} spawned "
        f"({sum(1 for a in report['agents'] if a['parent_agent_id'])} of them by another agent), "
        f"{totals['with_transcript']} with a transcript, "
        f"{totals['usage']['output_tokens']} output tokens, {totals['duration_seconds']}s",
        f"sessions: {len(report['harness']['sessions'])} orchestrating, "
        f"{session_usage['output_tokens']} output tokens — never a subagent's, which the line "
        f"above already carries",
        f"commands: {len(report['commands'])} invoking this framework's scripts, "
        f"{sum(1 for c in report['commands'] if c['exit_code'])} exiting non-zero",
        f"runs: {len(report['runs'])} captured",
        f"commits: {len(report['repository']['commits'])}; uncommitted: "
        f"{len(report['repository']['uncommitted'])}",
        f"decisions added: {len(report['decisions']['added'])}"
        + (f", {len(report['decisions']['retired'])} location(s) retired"
           if report['decisions'].get('retired') else "")
        + f" (baseline: {report['decisions']['baseline']})",
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
        worktrees = git(home, "worktree", "list", "--porcelain")
        if worktrees is not None and worktrees.returncode == 0:
            for line in worktrees.stdout.splitlines():
                if not line.startswith("worktree "):
                    continue
                path = line[len("worktree "):]
                if path and not under(home, path):
                    print(f"worktree outside this tree: {path} — sessions opened there "
                          f"transcribe under another harness directory this probe does not read; "
                          f"point --transcripts at it for that slice")
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
