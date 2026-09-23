#!/usr/bin/env python3
"""Places the drift a project is carrying into the session that is starting.

Detection already exists and is mechanical: `bin/trace.py --check` recomputes every binding's
digests and says which have moved. What it never had was a trigger. It runs when a person invokes
`/siegard-status` or `/reconcile`, so a tree accumulates drift between the moments somebody
thinks to look, and the reading that would have caught it is the reading nobody ran. A count
placed at the start of the session is the trigger: the session, and every agent that later edits
in it, begins holding what the tree already owes.

A tally and never a listing. What a reader acts on is the number per class and the door it opens;
the lines themselves are the drift report's to print, and a hook that pasted them would spend a
session's opening context on a report nobody asked for — and would be switched off for it.

`SessionStart` alone. A subagent spawned mid-session inherits a context whose opening already
carries this, and paying for it again per spawn buys nothing the session does not hold.

This never fails a session. Every path out of here exits 0 and most print nothing: a project with
no `siegard.json`, a tree git does not hold, a trace that does not parse, a machine missing the
validators. A hook that exited non-zero would stop every session of every project holding the
plugin, and an unreadable trace is the drift report's to refuse properly, with its reason, where
somebody asked it the question.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
EVENT = "SessionStart"


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
    if not lines:
        return ""
    return ("This project is carrying trace drift, counted at the start of this session by "
            "`bin/trace.py`:\n\n" + "\n".join(lines) + "\n\nA count, not a stop: nothing here is "
            "owed before other work, and none of it is repaired by editing the trace. Where a "
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
        if not root.is_dir():
            return 0
        said = receipt(root)
    except Exception:
        return 0
    if not said:
        return 0
    print(json.dumps({"hookSpecificOutput": {"hookEventName": EVENT,
                                             "additionalContext": said}}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
