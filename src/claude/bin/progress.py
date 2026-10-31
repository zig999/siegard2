#!/usr/bin/env python3
"""Print one line saying where each live initiative stands, read from disk, for a status line.

A person watching a long run asks where it is; the answer is on disk the moment a record or a
log line lands, and a line the harness redraws on its own carries it without a model reading
anything. «The progress line is one line, printed by a script from disk and git alone, with no
model in it» (SPEC-009 R1). One segment per live initiative — a directory under `work_root`
without `closure.md` — joined by ` | `:

    <slug> · task <delivered>/<tasks> delivered · phase <phase> · last: <log line>

- **tasks** are the `task` nodes of `plan.json`, the plan's derived index; **delivered** are those
  holding an implementation record at the path the task computes to. «A count on the line is a
  count of records present at the paths their tasks compute to, and never a statement that they
  hold together» (SPEC-009 R2): whether they do is `deliver.py --check`'s to say, and
  `/siegard-progress` reads each task's state through `deliver.py --outstanding`.
- **phase** is the first that holds, in this order: `plan` — the work root holds no
  `plan.json`, or it names no task; `delivery` — a task holds no implementation record; `proof` —
  a task holds no proof record; `review` — a task is named by no record under `review/`;
  `reviewed` — every task is. It says which records are present, never what is owed: «a task
  delivered as the substrate alone holds no proof record, and the line reads `proof` over it»
  (SPEC-009 R3).
- **last** is the last line of `orchestration.md` at the initiative's delivery root, cut to a
  width; it is left out where the log does not exist.

«Outside a project that declares `siegard.json`, the line is empty» (SPEC-009 R4), and so it is
where nothing can be read — no `work_root`, no live initiative, a project file that does not parse:
a status line that fails is drawn as an error on every refresh, and it is no channel for a
refusal. The roots are read from `siegard.json` defensively, as `deliver.py` reads `targets`, and
never validated here — `project.py` is the file's reader, and a validation per redraw is the cost
this line exists not to pay; `/siegard-status` and `/siegard-progress` run it.

The working directory is the harness's: the JSON record a status line command receives on stdin
names it under `workspace.current_dir` or `cwd`, and a directory named as the one argument wins
over both.

Declared dependencies: PyYAML, read only where a review record exists.

Usage:  progress.py [<dir>]         print the progress line of the project holding <dir>, or of
                                    the directory the stdin record names, or of the working
                                    directory
        progress.py --help          print this text and stop
Exit:   0 always — the line, or nothing
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

BIN = Path(__file__).resolve().parent
sys.path.insert(0, str(BIN))

PROJECT_FILE = "siegard.json"
CLOSURE_FILE = "closure.md"
PLAN_FILE = "plan.json"
LOG_FILE = "orchestration.md"
GIT_TIMEOUT_SECONDS = 2
LAST_WIDTH = 80
SEPARATOR = " · "


def start_of(argv: list[str]) -> Path:
    if argv:
        return Path(argv[0])
    if not sys.stdin.isatty():
        try:
            record = json.loads(sys.stdin.read() or "{}")
        except (json.JSONDecodeError, UnicodeDecodeError):
            record = {}
        if isinstance(record, dict):
            workspace = record.get("workspace")
            for where in ((workspace or {}).get("current_dir") if isinstance(workspace, dict)
                          else None, record.get("cwd")):
                if isinstance(where, str) and where:
                    return Path(where)
    return Path.cwd()


def tasks_of(work: Path) -> list[str] | None:
    try:
        index = json.loads((work / PLAN_FILE).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None
    nodes = index.get("nodes") if isinstance(index, dict) else None
    if not isinstance(nodes, list):
        return None
    return [n["id"] for n in nodes if isinstance(n, dict) and n.get("kind") == "task"
            and isinstance(n.get("id"), str) and n["id"].startswith("task/")]


def reviewed_of(delivery: Path) -> set[str]:
    """Every task some record under `review/` names in its `tasks`."""
    records = sorted((delivery / "review").glob("*.md")) if (delivery / "review").is_dir() else []
    if not records:
        return set()
    import yaml
    loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
    named: set[str] = set()
    for record in records:
        try:
            text = record.read_text(encoding="utf-8")
            front = yaml.load(text.split("---", 2)[1], Loader=loader) if text.startswith("---") \
                else None
        except (OSError, IndexError, UnicodeDecodeError, yaml.YAMLError):
            continue
        if isinstance(front, dict) and isinstance(front.get("tasks"), list):
            named |= {t for t in front["tasks"] if isinstance(t, str)}
    return named


def last_line(delivery: Path) -> str | None:
    try:
        lines = [line.strip() for line in
                 (delivery / LOG_FILE).read_text(encoding="utf-8").splitlines() if line.strip()]
    except (OSError, UnicodeDecodeError):
        return None
    if not lines:
        return None
    line = lines[-1].removeprefix("- ")
    return line if len(line) <= LAST_WIDTH else line[:LAST_WIDTH - 1] + "…"


def segment(slug: str, work: Path, delivery: Path) -> str:
    parts = [slug]
    tasks = tasks_of(work)
    if not tasks:
        parts.append("phase plan")
    else:
        rest = [tid[len("task/"):] for tid in tasks]
        delivered = [r for r in rest if (delivery / "implementation" / f"{r}.md").is_file()]
        proven = [r for r in delivered if (delivery / "proof" / f"{r}.md").is_file()]
        parts.append(f"task {len(delivered)}/{len(tasks)} delivered")
        if len(delivered) < len(tasks):
            phase = "delivery"
        elif len(proven) < len(tasks):
            phase = "proof"
        elif set(tasks) - reviewed_of(delivery):
            phase = "review"
        else:
            phase = "reviewed"
        parts.append(f"phase {phase}")
    last = last_line(delivery)
    if last:
        parts.append(f"last: {last}")
    return SEPARATOR.join(parts)


def line_of(start: Path) -> str:
    from project import toplevel_of
    if not start.is_dir():
        return ""
    home = toplevel_of(start, timeout=GIT_TIMEOUT_SECONDS)
    try:
        declared = json.loads((home / PROJECT_FILE).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return ""
    if not isinstance(declared, dict):
        return ""
    work_root, delivery_root = declared.get("work_root"), declared.get("delivery_root")
    if not isinstance(work_root, str) or not (home / work_root).is_dir():
        return ""
    live = sorted(p for p in (home / work_root).iterdir()
                  if p.is_dir() and not (p / CLOSURE_FILE).is_file())
    if not isinstance(delivery_root, str):
        return ""
    return " | ".join(segment(p.name, p, home / delivery_root / p.name) for p in live)


def main() -> int:
    if "--help" in sys.argv[1:]:
        # The docstring is this script's one home of what it does and how it is called,
        # so `--help` prints that rather than a second copy of it that could drift.
        print(__doc__.strip())
        return 0
    try:
        line = line_of(start_of(sys.argv[1:2]))
    except Exception:
        line = ""
    if line:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
