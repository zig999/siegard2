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
and the read is announced by whoever invokes it. And what leaves it is counts, names, timestamps,
a digest of each agent's prompt and the command lines that invoked this framework's own scripts
— never the text of a prompt, a reply or a tool's result. The harness keys that directory by the
main tree: a session that enters a linked worktree under the project keeps transcribing under
the main tree's directory, so the directory is derived from the main toplevel — the parent of
`git rev-parse --git-common-dir` — whichever tree the report is run from. Run inside a linked
worktree, the report names it in `harness.worktree` and admits a session only where one of its
recorded working directories reaches that worktree; otherwise the main tree's sessions and every
other worktree's would be counted as the worktree's. One directory the probe cannot promise: a
session opened in a git worktree sited outside the main tree — the parallel-frontier route's
`../wt-<task>` — transcribes under a harness directory this probe never lists. Where
`git worktree list` names such worktrees at probe time, the probe says so and `--transcripts
DIR` is the door; a worktree already removed left nothing to announce, so the receipt is honest
only about what still exists.

**A repeat is the same prompt handed to the same agent type.** Each spawn carries the SHA-256 of
its prompt's UTF-8 bytes — a digest, never the text — and `repeats_earlier` is true where an
earlier spawn in the window carried the same digest under the same type; `agent_totals` sums the
repeats per type and overall. A description is free text the spawning session composes, and two
spawns of one prompt under two descriptions are one prompt handed twice.

**The window is named, never remembered.** `--since` is an instant, or `last`, which continues
from the `until` of the newest report already in the telemetry root; `--until` defaults to now
and is recorded. Every transcript entry, run, commit and decision outside the window is outside
the report. A window inferred from when a session seemed to begin would be the recall this
replaces.

**A decision is followed to the node it filled.** The log records what the framework decided on
the human's behalf; nothing records whether anyone read it afterwards, and «the disclosed
decisions later revised are reported by the telemetry — counted beside those that stand, each
revised one named with the route that revised it and how long after — so the trade that removed
the stop stays measured rather than assumed» (SPEC-001 R10).
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

**A recommendation is counted from the log that recorded it.** An orchestrating entry point that
relays a report naming one door over the others writes it to the run's `orchestration.md` as one
line, «`recommended: <door> — <criterion> — <deciding fact>`» (SPEC-006 R5). Every such line under
the delivery root is read, with the commit that landed it and the first commit after it touching
that initiative's delivery or work root. Which door was then taken is never computed: the commit
that followed is the evidence, and reading it is a person's. Each line is `derived` or `judged`
by the criterion it names — a fact on disk decided it, or a rung of the ladder where none did —
because the two are read apart: a judged recommendation the person read as not taken is the
reading that narrows the grant back to derived ones.

**A question is counted, never read.** A human turn in the window holding a question mark is a
question the person put to the session, with the skill it ran and the seconds since the
assistant's last entry, and nothing of its text. Which of them asked for the recommendation a
handoff withheld is a person's reading of the transcript, never this script's: a word list for
that request, in any language, would be a classifier nobody measured. The count is the baseline
a reading of handoffs is set beside, and it decides nothing.

**A confirmation is counted, never quoted.** A handoff costs the person a turn whose whole
content is permission: "commit", "go on", "2". Each human turn inside the window is read once, in
the session's own context, and leaves as a class and nothing else — `commit_authorization` where
a short turn names a commit or a push, `go_ahead` where it is one of the go-ahead words this
script lists, `choice_by_label` where it is a bare label picking one offered door — with the
skill the session was running, the seconds since the assistant's last entry, and whether that
entry's closing paragraph asked anything. A confirmation after a message that asked nothing is
a turn the framework's own stop cost; one after a question is a turn a person was asked for. The
word list is this script's and is finite: a short turn it does not match is counted under
`unclassified_short`, so what the classifier reaches is read beside what it does not, and a
longer turn is a message, never a confirmation. `handoffs` sums these across sessions, beside
the Skill calls the sessions made, which is the denominator a confirmation count is read per.

**A commit the session made inside a skill's span is counted with what authorized it.** A `git
commit` or `git push` the session ran after a Skill call and before the person's next turn is
the session's own act — the skill refused it, the person did not type for it just then — and
each is recorded with the skill whose span it fell in, whether the command carried a pathspec,
whether it pushed, and what the session had to go on: `typed`, a commit word in a message the
person typed earlier in this session; `loop`, an autonomous loop the person armed; `summary`,
a commit word only in the continuation summary the harness wrote after a compaction; `none`.
The classification is the same word match the confirmations use, read over the whole session;
what it does not read is whether the person meant it, which the rules state and this counts.

**A section that cannot be read is said, not filled.**

Every section carries an entry in
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
import hashlib
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

import deliver
import plan
import spec

CANNOT_RUN = 2
CONTRACT = "siegard-telemetry/13"
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

CONFIRMATION_CLASSES = ("commit_authorization", "go_ahead", "choice_by_label")
SHORT_TURN = 60
COMMIT_WORDS = re.compile(r"\b(?:commit\w*|comit\w*|push\w*)\b", re.I)
GO_AHEAD = re.compile(
    r"^(?:sim|ok|okay|yes|yep|go|go on|go ahead|proceed|continue|continua\w*|prossiga|prosseguir"
    r"|segue|siga|vai|bora|manda|pode(?: \w+){0,2}|faça|faz|isso|certo|beleza|perfeito|concordo"
    r"|de acordo|aprovado|pode ser)[\s.!]*$", re.I)
CHOICE = re.compile(r"^(?:op[çc][ãa]o|option)?\s*[1-9a-d][).]?[\s.!]*$", re.I)
GIT_COMMIT = re.compile(r"\bgit\s+(?:-C\s+\S+\s+)?(?:-c\s+\S+\s+)*(commit|push)\b")
GIT_SWEEP = re.compile(r"\bgit\s+(?:-C\s+\S+\s+)?add\s+(?:-A|--all|-a|\.)(?:\s|$)|\bgit\s+(?:-C\s+\S+\s+)?commit\s+(?:\S+\s+)*-a\b")
CONTINUATION = "This session is being continued"
LOOP_MARKS = ("<<autonomous-loop", "/loop")
AUTHORIZATIONS = ("typed", "loop", "summary", "none")


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


def main_toplevel_of(directory: Path) -> Path:
    """The main tree's toplevel — the parent of the repository's common `.git` directory — which
    is the toplevel itself outside a linked worktree, and `toplevel_of` where git answers nothing."""
    probe = git(directory, "rev-parse", "--path-format=absolute", "--git-common-dir")
    if probe is not None and probe.returncode == 0 and probe.stdout.strip():
        return Path(probe.stdout.strip()).parent
    return toplevel_of(directory)


def worktree_of(home: Path, main: Path) -> str | None:
    """The linked worktree the report runs inside, or null where `home` is the main tree."""
    return str(home) if home != main else None


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
        front = spec.load_yaml(match.group(1))
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


def transcript_root_for(main: Path, override: str | None) -> Path:
    """The harness directory for the project, keyed by the main tree's toplevel."""
    if override:
        return Path(override)
    return HARNESS_PROJECTS / re.sub(r"[^A-Za-z0-9]", "-", str(main))


def under(home: Path, cwd: str) -> bool:
    anchor = str(home).rstrip("/")
    return cwd == anchor or cwd.startswith(anchor + "/")


def session_files(root: Path, main: Path, worktree: str | None) -> list[tuple[Path, Path]]:
    """Every session transcript this project's work may sit in, as (transcript, its root).

    The harness names a transcript directory by the working directory the session opened in, so
    a session started in `<project>/backend` lands beside the project's directory under a longer
    name and the project's own directory never holds it. Those siblings are read too — any
    directory whose name extends this one's by a hyphen — but a name is only a prefix, and
    `<project>-old` extends it the same way: a sibling's session is included only where some
    `cwd` it recorded sits under the main tree's toplevel. The project's own directory is read
    whole, since a session there that recorded no `cwd` is still this project's.

    Inside a linked worktree the anchor is the worktree, and the project's own directory is read
    under the same rule as a sibling: a session is the worktree's only where some `cwd` it
    recorded sits under the worktree, since the main tree's directory holds the main tree's
    sessions and every worktree's alike."""
    anchor = Path(worktree) if worktree is not None else main

    def reaches(path: Path) -> bool:
        return any(isinstance(e.get("cwd"), str) and under(anchor, e["cwd"])
                   for e in entries_of(path))

    files = [(path, root) for path in sorted(root.glob("*.jsonl"))
             if worktree is None or reaches(path)]
    parent = root.parent
    if not parent.is_dir():
        return files
    for sibling in sorted(parent.iterdir()):
        if sibling == root or not sibling.is_dir() or not sibling.name.startswith(root.name + "-"):
            continue
        for path in sorted(sibling.glob("*.jsonl")):
            if reaches(path):
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


def human_text_of(entry: dict) -> str | None:
    """What a person typed in a user-role entry, or None where the entry is not a person's. The
    harness writes in that role too — a background task's completion notice, a local command's
    echo, a reminder it injects — and counted as they land, those can outnumber the person many
    times over. What remains after those blocks are removed is what a person wrote; a paste a
    person made stays, because the pasting was theirs. The text is read here and classified
    here; nothing of it leaves the session's context."""
    if entry.get("type") != "user" or entry.get("isSidechain"):
        return None
    content = (entry.get("message") or {}).get("content")
    if isinstance(content, str):
        text = content
    else:
        blocks = blocks_of(entry)
        if not blocks or any(b.get("type") == "tool_result" for b in blocks):
            return None
        text = " ".join(text_of(b) for b in blocks if b.get("type") == "text")
    text = HARNESS_LINE.sub("", HARNESS_BLOCK.sub("", text)).strip()
    return text or None


def is_human_turn(entry: dict) -> bool:
    return human_text_of(entry) is not None


def confirmation_class(text: str) -> str | None:
    """Which confirmation a short human turn is, or None where it is not one. A turn that asks
    something is never a confirmation, whatever words it uses; a commit word is read first, so
    "go ahead and commit" is a commit authorization and not a go-ahead."""
    if len(text) > SHORT_TURN or text.endswith("?"):
        return None
    if COMMIT_WORDS.search(text):
        return "commit_authorization"
    if GO_AHEAD.match(text):
        return "go_ahead"
    if CHOICE.match(text):
        return "choice_by_label"
    return None


def asks(text: str) -> bool:
    """Whether the assistant's message closed on a question: its final paragraph holds one."""
    return "?" in text.strip().rsplit("\n\n", 1)[-1]


def pathspec_scoped(command: str) -> bool:
    """Whether a commit command names what it commits. A ` -- ` separator anywhere in the
    command is a pathspec; `git add -A`, `--all`, `-a`, `.` or `git commit -a` without one is a
    sweep. A command with neither names its paths some other way and is read as scoped."""
    if " -- " in command:
        return True
    return GIT_SWEEP.search(command) is None


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
    skill_calls: dict[str, int] = {}
    confirmations: list[dict] = []
    questions: list[dict] = []
    short_turns = 0
    last_assistant_at: str | None = None
    last_assistant_text: str = ""
    in_span_commits: list[dict] = []
    turns_since_skill = 0
    commit_word_typed = commit_word_in_summary = loop_armed = False
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
        if entry.get("type") == "assistant" and not entry.get("isSidechain"):
            # What the person answers to: the assistant's last entry, and the last text it wrote.
            last_assistant_at = stamp if isinstance(stamp, str) else last_assistant_at
            spoken = "\n".join(b.get("text", "") for b in blocks_of(entry)
                               if b.get("type") == "text" and isinstance(b.get("text"), str))
            if spoken.strip():
                last_assistant_text = spoken
        if not in_window(entry, since, until):
            continue
        entries_in_window += 1
        typed = human_text_of(entry)
        if typed is not None:
            human_turns.append(iso(instant_of(stamp)))
            turns_since_skill += 1
            if typed.startswith(CONTINUATION):
                commit_word_in_summary = commit_word_in_summary or bool(COMMIT_WORDS.search(typed))
            else:
                commit_word_typed = commit_word_typed or bool(COMMIT_WORDS.search(typed))
                loop_armed = loop_armed or any(mark in typed for mark in LOOP_MARKS)
            if len(typed) <= SHORT_TURN:
                short_turns += 1
            if "?" in typed and not typed.startswith(CONTINUATION):
                questions.append({
                    "at": iso(instant_of(stamp)), "skill": skill or "none",
                    "wait_seconds": seconds_between(last_assistant_at, stamp)
                    if last_assistant_at is not None else None})
            kind = confirmation_class(typed)
            if kind is not None:
                confirmations.append({
                    "at": iso(instant_of(stamp)), "class": kind, "skill": skill or "none",
                    "after_question": asks(last_assistant_text),
                    "wait_seconds": seconds_between(last_assistant_at, stamp)
                    if last_assistant_at is not None else None})
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
                    skill_calls[named] = skill_calls.get(named, 0) + 1
                    turns_since_skill = 0
        spent.add(entry, skill)
        for block in blocks_of(entry):
            if block.get("type") != "tool_use" or not isinstance(block.get("id"), str):
                continue
            payload = block.get("input") if isinstance(block.get("input"), dict) else {}
            if block.get("name") == "Bash":
                command = payload.get("command")
                if isinstance(command, str) and skill and turns_since_skill == 0 \
                        and GIT_COMMIT.search(command):
                    in_span_commits.append({
                        "at": iso(instant_of(stamp)), "skill": skill,
                        "push": "push" in {m.group(1) for m in GIT_COMMIT.finditer(command)},
                        "pathspec": pathspec_scoped(command),
                        "authorized_by": "typed" if commit_word_typed else "loop" if loop_armed
                        else "summary" if commit_word_in_summary else "none"})
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
        "skill_calls": dict(sorted(skill_calls.items())), "short_turns": short_turns,
        "confirmations": confirmations, "questions": questions, "commits": in_span_commits,
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


def prompt_digest_of(payload: dict) -> str:
    """SHA-256, hex, of the prompt's UTF-8 bytes — the empty string's where the tool use carried
    none. A digest is what leaves the transcript; the prompt's text never does."""
    prompt = payload.get("prompt")
    return hashlib.sha256((prompt if isinstance(prompt, str) else "").encode("utf-8")).hexdigest()


def spawn_of(block: dict, payload: dict, session_id: str, stamp: str | None) -> dict:
    return {
        "session": session_id, "tool_use_id": block["id"],
        "agent_type": agent_type_of(payload),
        "description": str(payload.get("description") or ""),
        "prompt_sha256": prompt_digest_of(payload),
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


def harness_section(root: Path, main: Path, worktree: str | None, since: datetime,
                    until: datetime) -> tuple[dict, list, list]:
    readable, reason = probe_transcripts(root)
    harness = {"transcript_root": str(root), "transcript_roots": [str(root)],
               "worktree": worktree, "readable": readable, "reason": reason, "sessions": [],
               "skill_totals": {}}
    if not readable:
        return harness, [], []
    commands: list[dict] = []
    agents: list[dict] = []
    for path, root in session_files(root, main, worktree):
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
        key = (agent["agent_type"], agent["prompt_sha256"])
        agent["repeats_earlier"] = key in seen
        seen.add(key)
    return harness, commands, agents


def empty_total() -> dict:
    return {"invocations": 0, "repeats": 0, "with_transcript": 0, "duration_seconds": 0.0,
            "usage": dict.fromkeys(USAGE_KEYS, 0)}


def add_to(total: dict, agent: dict) -> None:
    total["invocations"] += 1
    if agent["repeats_earlier"]:
        total["repeats"] += 1
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
        front = spec.load_yaml(match.group(1))
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
    """The value a dotted field path reaches in a node's frontmatter, and whether it reached.

    A list of mappings is addressed by index or by the one item whose `name` is the part — the
    way a node names an attribute, a relationship or an operation, and the way a log entry's
    `field` spells `attributes.<name>.type` — or whose `operation` is, the way a contract keys
    each of its `answers` and a log entry spells `answers.<operation>.accepted`. No item or two
    items under that name is a path that does not reach."""
    current = front
    for part in dotted.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, list) and part.isdigit() and int(part) < len(current):
            current = current[int(part)]
        elif isinstance(current, list):
            named = [item for item in current
                     if isinstance(item, dict) and part in (item.get("name"),
                                                            item.get("operation"))]
            if len(named) != 1:
                return False, None
            current = named[0]
        else:
            return False, None
    return True, current


def field_in_text(text: str, dotted: str) -> tuple[bool, object]:
    match = FENCE.match(text or "")
    if not match:
        return False, None
    try:
        front = spec.load_yaml(match.group(1))
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
    """Every classified note under the work root, each marked `live`: a note in a closed plan is
    what that plan left standing, not the state the window's work ran under, and the two are
    told apart by the same marker `scope` reads."""
    notes: list[dict] = []
    for initiative in initiatives_of(work_root):
        live = not (initiative / plan.CLOSURE_FILE).is_file()
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
                                  "class": "blocking", "text": line, "live": live})
                for line in plan.underdetermined_notes_of(text):
                    notes.append({"initiative": initiative.name, "node": nid,
                                  "class": "underdetermined", "text": line, "live": live})
            elif nid.startswith("epic/"):
                for entry in spec.listed(front, "uncovered"):
                    if isinstance(entry, (dict, str)):
                        notes.append({"initiative": initiative.name, "node": nid,
                                      "class": "uncovered", "text": entry, "live": live})
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


# ------------------------------------------------------------------- the recommendations


DERIVED = ("precondition unmet", "rule violated", "already done", "reading paid twice")
JUDGED = ("keeps the route", "serves the stated goal", "can be undone", "costs less")
CRITERIA = DERIVED + JUDGED
RECOMMENDED = re.compile(r"^recommended: (?P<door>.+?) — (?P<criterion>"
                         + "|".join(CRITERIA) + r") — (?P<fact>.+)$")
UNCOMMITTED = "0" * 40


def landing_of(home: Path, log: Path) -> dict[int, tuple[str, datetime] | None]:
    """Line number -> (commit, author time) of the commit that wrote it; None for a line no
    commit holds yet."""
    blame = git(home, "blame", "--line-porcelain", "--", str(log))
    if blame is None or blame.returncode != 0:
        return {}
    landed: dict[int, tuple[str, datetime] | None] = {}
    digest, line_number, when = None, None, None
    for raw in blame.stdout.splitlines():
        if raw.startswith("\t"):
            if line_number is not None:
                landed[line_number] = None if digest == UNCOMMITTED or when is None \
                    else (digest, when)
            digest, line_number, when = None, None, None
            continue
        head = raw.split(" ")
        if digest is None and len(head) >= 3 and len(head[0]) == 40:
            digest, line_number = head[0], int(head[2])
        elif head[0] == "author-time" and len(head) == 2:
            when = datetime.fromtimestamp(int(head[1]), timezone.utc)
    return landed


def next_commit_after(home: Path, digest: str, paths: list[Path], until: datetime) -> dict | None:
    listing = git(home, "log", "--reverse", f"--until={iso(until)}", "--format=%H%x09%aI%x09%s",
                  f"{digest}..HEAD", "--", *(str(p) for p in paths))
    if listing is None or listing.returncode != 0:
        return None
    for line in listing.stdout.splitlines():
        parts = line.split("\t", 2)
        if len(parts) == 3:
            return {"hash": parts[0], "timestamp": parts[1], "subject": parts[2]}
    return None


def recommendations_section(delivery_root: Path | None, work_root: Path | None, home: Path,
                            since: datetime, until: datetime) -> dict:
    lines: list[dict] = []
    malformed: list[dict] = []
    logs = sorted(delivery_root.glob(f"*/{deliver.ORCHESTRATION_FILE}")) \
        if delivery_root is not None and delivery_root.is_dir() else []
    for log in logs:
        slug = log.parent.name
        try:
            text = log.read_text(encoding="utf-8")
        except OSError:
            continue
        landed = landing_of(home, log)
        roots = [log.parent] + ([work_root / slug] if work_root is not None else [])
        for number, raw in enumerate(text.splitlines(), start=1):
            line = raw.strip()
            if line.startswith("- "):
                line = line[2:].strip()
            line = line.strip("`").strip()
            if not line.startswith("recommended:"):
                continue
            landing = landed.get(number)
            if landing is not None and not (since <= landing[1] <= until):
                continue
            where = {"slug": slug, "log": str(log), "line": number}
            match = RECOMMENDED.match(line)
            if match is None:
                malformed.append({**where, "text": line})
                continue
            lines.append({**where, "door": match.group("door"),
                          "criterion": match.group("criterion"),
                          "kind": "derived" if match.group("criterion") in DERIVED else "judged",
                          "fact": match.group("fact"),
                          "landed_in": landing[0] if landing else None,
                          "next_commit": next_commit_after(home, landing[0], roots, until)
                          if landing else None})
    by_criterion = {criterion: sum(1 for l in lines if l["criterion"] == criterion)
                    for criterion in CRITERIA}
    by_kind = {kind: sum(1 for l in lines if l["kind"] == kind) for kind in ("derived", "judged")}
    return {"emitted": len(lines), "by_criterion": by_criterion, "by_kind": by_kind,
            "lines": lines, "malformed": malformed}


# ------------------------------------------------------------------------- the handoffs


def handoffs_section(harness: dict) -> dict:
    """Every confirmation the sessions' human turns were, summed across sessions and set beside
    the Skill calls the sessions made. Nothing here is a judgment: a class is a word match, a
    wait is two timestamps apart, and `after_question` is a question mark in the paragraph the
    person answered to."""
    by_class = {name: {"count": 0, "unasked": 0, "wait_seconds_total": 0.0,
                       "wait_seconds_max": None} for name in CONFIRMATION_CLASSES}
    by_skill: dict[str, dict] = {}
    lines: list[dict] = []
    skill_calls = human_turns = short_turns = 0
    asked: dict[str, int] = {}
    for session in harness["sessions"]:
        for question in session["questions"]:
            asked[question["skill"]] = asked.get(question["skill"], 0) + 1
        human_turns += len(session["human_turns_in_window"])
        short_turns += session["short_turns"]
        for name, count in session["skill_calls"].items():
            by_skill.setdefault(name, {"calls": 0, "confirmations": 0})["calls"] += count
            skill_calls += count
        for confirmation in session["confirmations"]:
            lines.append({"session": session["id"], **confirmation})
            tally = by_class[confirmation["class"]]
            tally["count"] += 1
            if not confirmation["after_question"]:
                tally["unasked"] += 1
            wait = confirmation["wait_seconds"]
            if wait is not None:
                tally["wait_seconds_total"] = round(tally["wait_seconds_total"] + wait, 3)
                if tally["wait_seconds_max"] is None or wait > tally["wait_seconds_max"]:
                    tally["wait_seconds_max"] = wait
            by_skill.setdefault(confirmation["skill"],
                                {"calls": 0, "confirmations": 0})["confirmations"] += 1
    lines.sort(key=lambda c: (c["at"], c["session"]))
    confirmations = sum(t["count"] for t in by_class.values())
    commits = [{"session": s["id"], **c} for s in harness["sessions"] for c in s["commits"]]
    commits.sort(key=lambda c: (c["at"], c["session"]))
    in_span = {"count": len(commits),
               "by_authorization": {name: sum(1 for c in commits if c["authorized_by"] == name)
                                    for name in AUTHORIZATIONS},
               "by_skill": {name: sum(1 for c in commits if c["skill"] == name)
                            for name in sorted({c["skill"] for c in commits})},
               "pathspec": sum(1 for c in commits if c["pathspec"]),
               "push": sum(1 for c in commits if c["push"]),
               "lines": commits}
    return {"skill_calls": skill_calls, "human_turns": human_turns, "short_turns": short_turns,
            "confirmations": confirmations, "unclassified_short": short_turns - confirmations,
            "by_class": by_class, "by_skill": dict(sorted(by_skill.items())), "lines": lines,
            "questions": {"count": sum(asked.values()), "by_skill": dict(sorted(asked.items()))},
            "in_span_commits": in_span}


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
        entry("handoffs", transcript_source, transcript_reason),
    ]
    for key, section in (("delivery_root", "runs"), ("work_root", "notes"),
                         ("work_root", "scope"), ("delivery_root", "recommendations")):
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

    main = main_toplevel_of(project_root)
    harness, commands, agents = harness_section(transcript_root_for(main, transcripts), main,
                                                worktree_of(home, main), since, until)
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
        "recommendations": recommendations_section(delivery_root, work_root, home, since, until),
        "handoffs": handoffs_section(harness),
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
        f"{totals['repeats']} repeating an earlier prompt, "
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
        f"recommendations: {report['recommendations']['emitted']} recorded"
        + (f" ({report['recommendations']['by_kind']['derived']} derived, "
           f"{report['recommendations']['by_kind']['judged']} judged)"
           if report['recommendations']['emitted'] else "")
        + (f", {len(report['recommendations']['malformed'])} line(s) that do not parse"
           if report['recommendations']['malformed'] else ""),
        f"handoffs: {report['handoffs']['confirmations']} confirmation(s) typed over "
        f"{report['handoffs']['skill_calls']} Skill call(s) — "
        + ", ".join(f"{name} {tally['count']} ({tally['unasked']} after no question, "
                    f"{tally['wait_seconds_total']}s waited)"
                    for name, tally in report["handoffs"]["by_class"].items())
        + f"; {report['handoffs']['questions']['count']} question(s) asked"
        + f"; {report['handoffs']['unclassified_short']} short turn(s) unclassified",
        f"commits inside a skill's span: {report['handoffs']['in_span_commits']['count']} — "
        + ", ".join(f"{name} {n}" for name, n in
                    report["handoffs"]["in_span_commits"]["by_authorization"].items())
        + f"; {report['handoffs']['in_span_commits']['pathspec']} pathspec-scoped, "
        f"{report['handoffs']['in_span_commits']['push']} pushed",
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
        main = main_toplevel_of(project_root)
        worktree = worktree_of(home, main)
        transcript_root = transcript_root_for(main, args.transcripts)
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
        if worktree is not None:
            print(f"worktree: {worktree} — only the sessions whose working directories reach it "
                  f"are read; the main tree is {main}")
        worktrees = git(main, "worktree", "list", "--porcelain")
        if worktrees is not None and worktrees.returncode == 0:
            for line in worktrees.stdout.splitlines():
                if not line.startswith("worktree "):
                    continue
                path = line[len("worktree "):]
                if path and not under(main, path):
                    print(f"worktree outside this tree: {path} — sessions opened there "
                          f"transcribe under another harness directory this probe does not read; "
                          f"point --transcripts at it for that slice")
        if readable:
            overlapping = []
            for path, root in session_files(transcript_root, main, worktree):
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
        print("what leaves the transcripts: agent types, descriptions, a digest of each agent's "
              "prompt, token counts, timestamps, the class of each short confirmation a person "
              "typed, and the command lines that invoked this framework's scripts — no message "
              "text")
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
