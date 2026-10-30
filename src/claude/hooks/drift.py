#!/usr/bin/env python3
"""Places the drift a project is carrying into the session that is starting.

Detection already exists and is mechanical: `bin/trace.py --check` recomputes every binding's
digests and says which have moved. What it never had was a trigger. It runs when a person invokes
`/siegard-status` or `/reconcile`, so a tree accumulates drift between the moments somebody
thinks to look, and the reading that would have caught it is the reading nobody ran. A count
placed at the start of the session is the trigger: the session, and every agent that later edits
in it, begins holding what the tree already owes.

The same trigger carries the other thing the trace owes and no drift report shows: nodes a
refused certification left decided by a reading or a step, with the assertion that would let a
test decide them named. `trace.py --owed` is the one reader of that corpus, and the count here is
its own, never recounted.

A tally and never a listing. What a reader acts on is the number per class and the door it opens;
the lines themselves are the drift report's to print, and a hook that pasted them would spend a
session's opening context on a report nobody asked for — and would be switched off for it.

`SessionStart` alone. A subagent spawned mid-session inherits a context whose opening already
carries this, and paying for it again per spawn buys nothing the session does not hold.

This never fails a session. Every path out of here exits 0. A `SessionStart` hook cannot stop a
session, but one that exits non-zero is rendered as a hook error at the start of every session of
every project holding the plugin, Siegard or not, and the session itself is never told what it
said. Most paths print nothing: a project with no `siegard.json`, a tree git does not hold, a
trace that does not parse — an unreadable trace is the drift report's to refuse properly, with
its reason, where somebody asked it the question.

One silence would mislead, and it is said instead: a project that declares `siegard.json`, on a
machine whose `python3` lacks the validators. There no count is taken, and a session starting
with no count reads as a session starting with no drift. It is said once, in one line, on both
channels — to the person as a `systemMessage`, to the session as context — and only where the
project is declared, because the plugin's scripts are no other project's to run.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import subprocess
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
EVENT = "SessionStart"
GIT_TIMEOUT_SECONDS = 10
VALIDATORS = {"yaml": "PyYAML", "jsonschema": "jsonschema"}


def declares_a_project(root: Path) -> bool:
    """Whether the session starts inside a project that declares `siegard.json`, decided by the
    standard library alone, because this is the question asked where the validators may be
    missing and `bin/project.py`'s own reading of the file needs one of them."""
    sys.path.insert(0, str(PLUGIN_ROOT / "bin"))
    from project import PROJECT_FILE, toplevel_of
    return (toplevel_of(root, timeout=GIT_TIMEOUT_SECONDS) / PROJECT_FILE).is_file()


def missing_validators() -> list[str]:
    """The validators `bin/trace.py` cannot run without, as their packages are named, where its
    import refuses; nothing where it imports. The refusal is the script's own, and only the names
    are read here, so the line says what to install rather than that something is missing."""
    sys.path.insert(0, str(PLUGIN_ROOT / "bin"))
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            import trace
    except SystemExit:
        return [package for module, package in VALIDATORS.items()
                if importlib.util.find_spec(module) is None] or list(VALIDATORS.values())
    return []


def unchecked(missing: list[str]) -> dict:
    lacks = " and ".join(missing)
    install = " ".join(name.lower() for name in missing)
    said = (f"Siegard did not count the drift this project carries: the plugin's scripts need "
            f"{lacks}, which the `python3` its hooks run lacks (pip install {install}).")
    return {"systemMessage": said,
            "hookSpecificOutput": {"hookEventName": EVENT, "additionalContext": said}}


def targets_of(root: Path) -> list[Path]:
    """Every target source root the project declares, read from the one reader of `siegard.json`.

    `bin/project.py` is that reader and this does not become a second one: the file's fields are
    taken off its printed lines, exactly the way every skill takes them. A project file that does
    not hold together prints its problems there and no target line here, which is the right
    silence — a receipt computed over a root nobody validated would be a number about the wrong
    tree."""
    try:
        probe = subprocess.run([sys.executable, "-B", str(PLUGIN_ROOT / "bin" / "project.py"),
                                str(root)], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return []
    if probe.returncode != 0:
        return []
    found = []
    for line in probe.stdout.splitlines():
        if line.startswith("target ") and ": " in line:
            found.append(Path(line.split(": ", 1)[1].strip()))
    return found


def receipt(root: Path) -> str:
    """What this session is starting on top of, in as few lines as it can be said in.

    One block per trace file rather than per target: a trace is one file per git toplevel, so two
    targets under one toplevel read the same file, and printing it twice would report one tree's
    drift as two trees' worth."""
    sys.path.insert(0, str(PLUGIN_ROOT / "bin"))
    import trace  # the drift is computed by the script that owns it, never recounted here

    lines: list[str] = []
    seen: set[Path] = set()
    for target in targets_of(root):
        try:
            where = trace.trace_path(target)
        except Exception:
            continue
        if where in seen:
            continue
        seen.add(where)
        counted = trace.tally_of(target)
        if counted is None:
            continue
        counts, held, drifted = counted
        total = sum(counts.values())
        if not total and not held:
            continue
        said = ", ".join(f"{counts[cls]} {cls}" for cls in counts if counts[cls])
        lines.append(f"- {where}: {total} drift finding(s) — {said}"
                     + (f"; {held} suppressed under a freely-edited target" if held else ""))
        if drifted:
            lines.append(f"  {len(drifted)} file(s) carry `code` drift, which /reconcile is what "
                         f"answers; /siegard-status lists them and hands the invocation ready")
        if counts[trace.MOVED]:
            lines.append(f"  {counts[trace.MOVED]} binding(s) carry `moved` drift: `/reconcile` "
                         f"over the bound files re-reads them against the node as it stands; a "
                         f"delivery of a task implementing the node restamps only the files its "
                         f"record names")
    for target in targets_of(root):
        try:
            if trace.tally_of(target) is None:
                continue
            reading, problems = trace.owed_reading(target)
        except (Exception, SystemExit):
            continue
        if reading is None or problems:
            continue
        owed = len(reading["testable_nodes"])
        if owed:
            lines.append(f"- {target}: {owed} node(s) a finite test would decide are still "
                         f"decided by a reading or a step — each with the assertion that closes "
                         f"it named; `bin/trace.py --owed {target}` lists them and hands the "
                         f"proof increment that writes those tests")
    if not lines:
        return ""
    return ("This project is carrying what the trace owes, counted at the start of this session "
            "by `bin/trace.py`:\n\n" + "\n".join(lines) + "\n\nA count, not a stop: nothing here "
            "is owed before other work, and none of it is repaired by editing the trace. Where a "
            "reading is wanted, /siegard-status prints the findings and their routes.")


def main() -> int:
    try:
        record = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        record = {}
    if not isinstance(record, dict):
        record = {}
    if record.get("hook_event_name") not in (EVENT, None):
        return 0
    where = record.get("cwd")
    root = Path(where) if isinstance(where, str) and where else Path.cwd()
    try:
        if not root.is_dir() or not declares_a_project(root):
            return 0
        missing = missing_validators()
        if missing:
            print(json.dumps(unchecked(missing)))
            return 0
        said = receipt(root)
    except (Exception, SystemExit):
        return 0
    if not said:
        return 0
    print(json.dumps({"hookSpecificOutput": {"hookEventName": EVENT,
                                             "additionalContext": said}}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
