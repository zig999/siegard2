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

The line is set by the person, never by a session on its own: `/siegard-config`, which only a
person invokes, runs `--install`. «The status line is set only where the person asks for it, in
the project's `.claude/settings.local.json`, as the command `python3 -B` over the absolute path of
the `bin/progress.py` that wrote it» (SPEC-009 R5). The local settings file is the one Claude Code
keeps out of version control, and the path is this machine's: committed to the shared settings, it
would name a file no other machine holds. The entry is merged, never the file replaced — every
other key stands — and an existing `statusLine` this script did not write is refused, never
overwritten; one it did write, from any plugin version, is replaced. `--uninstall` removes the
entry only where this script wrote it.

The plugin's cache directory is named by version, so the path the entry holds is one version's
and a later version leaves it pointing at the earlier one. «Where the plugin version loaded for the
project is not the one the line runs from, the line says so, naming both, and names the re-run
that moves it» (SPEC-009 R6): the loaded version is read from Claude Code's own record of installed
plugins — `installed_plugins.json` under `$CLAUDE_CONFIG_DIR`, or `~/.claude` — taking the entry
installed for the project before one installed for the user, and a record that is absent, does not
parse or names no entry adds nothing to the line.

Declared dependencies: PyYAML, read only where a review record exists.

Usage:  progress.py [<dir>]         print the progress line of the project holding <dir>, or of
                                    the directory the stdin record names, or of the working
                                    directory
        progress.py --install <project-root>
                                    merge the status line entry naming this script into
                                    <project-root>/.claude/settings.local.json
        progress.py --uninstall <project-root>
                                    remove that entry, where this script wrote it
        progress.py --help          print this text and stop
Exit:   0 always for the line — the line, or nothing; 0 when --install or --uninstall wrote or
        found nothing to change, 1 when it refused, 2 when it cannot run
"""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

BIN = Path(__file__).resolve().parent
sys.path.insert(0, str(BIN))

PROJECT_FILE = "siegard.json"
CLOSURE_FILE = "closure.md"
PLAN_FILE = "plan.json"
LOG_FILE = "orchestration.md"
SETTINGS_FILE = ".claude/settings.local.json"
MANIFEST = BIN.parent / ".claude-plugin" / "plugin.json"
INSTALLED_PLUGINS = Path("plugins") / "installed_plugins.json"
SCOPES = ("local", "project", "user")
GIT_TIMEOUT_SECONDS = 2
LAST_WIDTH = 80
SEPARATOR = " · "
REFUSED = 1
CANNOT_RUN = 2


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
    line = " | ".join(segment(p.name, p, home / delivery_root / p.name) for p in live)
    moved = version_moved(home) if line else None
    return f"{line} | {moved}" if moved else line


def manifest() -> dict:
    try:
        held = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return {}
    return held if isinstance(held, dict) else {}


def version_moved(home: Path) -> str | None:
    """The note naming both versions where the plugin loaded for `home` is not this one, or None."""
    own = manifest()
    name, version = own.get("name"), own.get("version")
    if not isinstance(name, str) or not isinstance(version, str):
        return None
    config = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")
    try:
        record = json.loads((config / INSTALLED_PLUGINS).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None
    plugins = record.get("plugins") if isinstance(record, dict) else None
    if not isinstance(plugins, dict):
        return None
    entries = [e for key, held in plugins.items() if isinstance(key, str)
               and key.startswith(f"{name}@") and isinstance(held, list)
               for e in held if isinstance(e, dict) and isinstance(e.get("installPath"), str)]
    for scope in SCOPES:
        loaded = next((e for e in entries if e.get("scope") == scope
                       and (scope == "user" or e.get("projectPath") == str(home))), None)
        if loaded is None:
            continue
        if Path(loaded["installPath"]).resolve() == BIN.parent:
            return None
        other = loaded.get("version") if isinstance(loaded.get("version"), str) else "another"
        return (f"progress.py {version}, plugin {other} loaded: re-run the status line step of "
                f"/siegard-config")
    return None


def entry_of(script: Path) -> dict:
    return {"type": "command", "command": f"python3 -B {shlex.quote(str(script))}"}


def written_here(entry: object) -> bool:
    """Whether a `statusLine` value is one `--install` writes, from any plugin version."""
    if not isinstance(entry, dict) or not isinstance(entry.get("command"), str):
        return False
    try:
        words = shlex.split(entry["command"])
    except ValueError:
        return False
    return (len(words) == 3 and words[:2] == ["python3", "-B"]
            and Path(words[2]).parts[-2:] == ("bin", "progress.py"))


def merged(held: dict | None, script: Path) -> tuple[dict | None, str]:
    """The settings `held` with this script's status line merged in, and what the merge did.

    None in place of the settings is a refusal, and the text says why: a `statusLine` this
    script did not write is the person's, and replacing it would be deciding for them."""
    settings = dict(held or {})
    wanted = entry_of(script)
    present = settings.get("statusLine")
    if present == wanted:
        return settings, "unchanged"
    if present is not None and not written_here(present):
        return None, (f"{SETTINGS_FILE} already sets statusLine to {json.dumps(present)}, which "
                      f"this script did not write; remove it there first to replace it")
    settings["statusLine"] = wanted
    return settings, "replaced" if present is not None else "added"


def removed(held: dict | None) -> tuple[dict | None, str]:
    """The settings `held` without this script's status line, and what the removal did."""
    settings = dict(held or {})
    present = settings.get("statusLine")
    if present is None:
        return settings, "unchanged"
    if not written_here(present):
        return None, (f"{SETTINGS_FILE} sets statusLine to {json.dumps(present)}, which this "
                      f"script did not write; it is left as it stands")
    del settings["statusLine"]
    return settings, "removed"


def settings_change(argv: list[str]) -> int:
    install = argv[0] == "--install"
    if len(argv) != 2:
        print(f"cannot run: expected {argv[0]} <project-root>", file=sys.stderr)
        return CANNOT_RUN
    root = Path(argv[1]).resolve()
    if not (root / PROJECT_FILE).is_file():
        print(f"cannot run: {root} holds no {PROJECT_FILE}, and outside one the line is empty",
              file=sys.stderr)
        return CANNOT_RUN
    path = root / SETTINGS_FILE
    held = None
    if path.exists():
        try:
            held = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError) as broken:
            print(f"cannot run: {path} does not parse ({broken}); it is never rewritten over",
                  file=sys.stderr)
            return CANNOT_RUN
        if not isinstance(held, dict):
            print(f"cannot run: {path} holds no JSON object", file=sys.stderr)
            return CANNOT_RUN
    result, done = merged(held, BIN / "progress.py") if install else removed(held)
    if result is None:
        print(f"refused: {done}")
        return REFUSED
    if done != "unchanged":
        path.parent.mkdir(parents=True, exist_ok=True)
        staged = path.with_name(path.name + ".tmp")
        staged.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")
        os.replace(staged, path)
    print(f"{done}: statusLine in {path}")
    if install:
        print(f"  {json.dumps(result['statusLine'])}")
        print(f"  plugin {manifest().get('version', 'unknown')}: a plugin update moves this path; "
              f"run this again after one")
        print(f"  removed by: python3 -B {shlex.quote(str(BIN / 'progress.py'))} --uninstall "
              f"{shlex.quote(str(root))}")
    try:
        ignored = subprocess.run(["git", "-C", str(root), "check-ignore", "-q", SETTINGS_FILE],
                                 capture_output=True, timeout=GIT_TIMEOUT_SECONDS).returncode
    except (OSError, subprocess.TimeoutExpired):
        ignored = None
    if install and ignored == 1:
        print(f"  git does not ignore {SETTINGS_FILE}: it names a path on this machine and no "
              f"other, so it belongs in .gitignore and never in a commit")
    return 0


def main() -> int:
    if "--help" in sys.argv[1:]:
        # The docstring is this script's one home of what it does and how it is called,
        # so `--help` prints that rather than a second copy of it that could drift.
        print(__doc__.strip())
        return 0
    if sys.argv[1:2] in (["--install"], ["--uninstall"]):
        return settings_change(sys.argv[1:])
    try:
        line = line_of(start_of(sys.argv[1:2]))
    except Exception:
        line = ""
    if line:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
