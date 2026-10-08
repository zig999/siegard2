#!/usr/bin/env python3
"""Resolve the project file: every root and the standard a consumer declared, read from disk.

A value retyped per invocation is a value a session can forget or mistype — a registry can sit
unnamed across invocations that its own delivery root remembers, and a specification
root is no easier to retype correctly than a registry's path. `siegard.json` is where a project
declares each once: at the project's own root, in the consumer's own hands, written only by
`/siegard-config`. This script is the one reader — it finds the file, holds it to
`schemas/project.json`, and prints every field it declares, one per line. A skill never parses the
file itself, and an answer given in a session persists only by the file gaining it.

What the resolution means is the contract's business, stated once in the schema, and it is not one
rule: `standard` alone may be overridden by an invocation naming a different one — the report says
both existed and which won. `specification_root`, `targets`, `work_root`, `delivery_root` and
`telemetry_root` answer only from here; an invocation naming one of these instead has no effect, and where this
file does not declare one, that is the calling skill's stop to raise, never this script's to guess
around. This script prints only what stands; deciding that an absence is a stop belongs to
whichever skill needed the field.

One report precedes the fields: a root `CLAUDE.md` carrying the framework's rules. The rules
reach every session and every agent of a project that declares `siegard.json` through the
plugin's own hooks, and nothing is placed at the
project root for them; a root file carrying the rules' marker line is a second copy of what the
hooks already placed, loaded beside it in every session. This script prints one `rules:` line
naming that file and the version its marker states — a report, never a refusal, because the
fields below stand either way and removing a portion of a file a project may have added its own
rules to is a person's act. A root `CLAUDE.md` carrying no marker is the project's own and is
not reported.

A standard governs one target. Declared as an object keyed by target, each entry prints on its
own line — `standard <target>: <path>` or `standard <target>: declared none` — and the calling
skill reads the line for the target it was invoked over; a target the object lacks a line for is
an absence, and the skill's stop. Declared as a bare path, it prints as `standard: <path>` and is
refused here where `targets` holds more than one key: one registry answering for two stacks is
the wrong registry for one of them, and that error passes every structural check.

Tests are declared per target, in the scope parts a standard rule's scope uses, and print one
line per target — `tests <target>: <scope>; <scope>`. `reaches()` here is the one reading of those
parts for every script: a rule's scope and a declared test are matched by the same function, so
a path one of them reaches is never read differently by the other.

`toplevel_of()` here is the one answer to where a project's `siegard.json` sits, for every script
and for the plugin's hooks. A hook runs at the start of every session and every agent, and one that
fails stops them, so importing this module needs nothing beyond the standard library: jsonschema
is imported where the file is validated, and its absence is this script's `cannot run` there,
never a failure at import.

Declared dependencies: jsonschema.

Usage:  project.py <project-root>    resolve siegard.json for the tree holding <project-root> —
                                     the file sits at that directory's git toplevel, or at the
                                     directory itself where git does not hold it
        project.py --help            print this text and stop
Exit:   0 resolved: every field siegard.json declares, or no file at all, each said in one line
        1 the file does not hold together, or names a standard that does not exist
        2 cannot run
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

CANNOT_RUN = 2

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
PROJECT_CONTRACT = PLUGIN_ROOT / "schemas" / "project.json"
PROJECT_FILE = "siegard.json"
MANIFEST = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"

# The one home of the marker's shape: the rules file carries this line, this script reads it, and
# the distribution suite imports this pattern to pin the marker to the shipped version.
RULES_MARKER = re.compile(r"These rules ship with Siegard (\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?)")


def report_rules_copy(home: Path) -> None:
    """A root `CLAUDE.md` carrying the rules' marker line is a copy of what the plugin's hooks
    place in every session: the same rules loaded twice, and a copy the plugin's updates never
    reach. This script is the one thing every skill runs first, so the report lives here — a
    report, never a refusal, because the fields below stand either way, and removing the Siegard
    portion of a file a project may have appended its own rules to is a person's act, never this
    script's."""
    try:
        version = json.loads(MANIFEST.read_text(encoding="utf-8")).get("version")
    except (OSError, json.JSONDecodeError):
        # Not a shipped tree. The distribution suite guards the manifest where it is authored;
        # a second reporter here would fire only where that suite cannot run.
        return
    if not isinstance(version, str):
        return
    rules = home / "CLAUDE.md"
    if not rules.is_file():
        return
    try:
        text = rules.read_text(encoding="utf-8")
    except OSError:
        return
    found = RULES_MARKER.search(text)
    if found is None:
        return
    print(f"rules: {rules} carries the Siegard {found.group(1)} rules, and the plugin's hooks "
          f"place the {version} rules in every session and every agent of a project that declares "
          f"{PROJECT_FILE}; remove the "
          f"Siegard portion and keep anything the project added — a copy at the root is loaded "
          f"twice and updated never")


def reaches(scope, path: str) -> bool:
    """Whether one scope reaches one path spelled from the target source root. The scope is
    stated in parts rather than as a glob pattern deliberately: one tool's single star crosses a
    separator and another's double star means exactly one directory, and that difference would
    decide whether a finding is refused."""
    if not isinstance(scope, dict):
        return False
    under, suffix = scope.get("under"), scope.get("suffix")
    if not isinstance(under, str) or not isinstance(suffix, str):
        return False
    # `.` is the target root itself, the same thing it means to trace.py's `under()`, which reads
    # the other path vocabulary in this framework. Composed as a prefix it would be `./`, which no
    # stored path starts with, so a scope over the whole target would reach nothing at all.
    if under.strip("/") in ("", "."):
        return path.endswith(suffix) and (bool(scope.get("nested")) or "/" not in path)
    prefix = f"{under.rstrip('/')}/"
    if not path.startswith(prefix) or not path.endswith(suffix):
        return False
    return bool(scope.get("nested")) or "/" not in path[len(prefix):]


def spelled(scope: dict) -> str:
    """One scope as `project.py` prints it, in the parts it is declared in."""
    return (f"under {scope.get('under')}, suffix {scope.get('suffix')}"
            + (", nested" if scope.get("nested") else ""))


def toplevel_of(directory: Path, timeout: float | None = None) -> Path:
    """Where the project file sits: the directory's git toplevel, or the directory itself
    where git does not hold it — deterministic either way, because the directory is a named
    input and never the session's working directory. A caller that cannot wait names a
    `timeout`, and a git that does not answer within it raises `subprocess.TimeoutExpired`:
    not answering is not the same answer as not holding the directory."""
    try:
        probe = subprocess.run(["git", "-C", str(directory), "rev-parse", "--show-toplevel"],
                               capture_output=True, text=True, timeout=timeout)
    except OSError:
        # No git on this machine is the limit case of git not holding the directory, and the
        # answer is the same one: the directory itself.
        return directory
    if probe.returncode == 0 and probe.stdout.strip():
        return Path(probe.stdout.strip())
    return directory


def main() -> int:
    args = sys.argv[1:]
    if "--help" in args:
        # The docstring is this script's one home of what it does and how it is called,
        # so `--help` prints that rather than a second copy of it that could drift.
        print(__doc__.strip())
        return 0
    if len(args) != 1 or args[0].startswith("--"):
        print("cannot run: expected <project-root>", file=sys.stderr)
        return CANNOT_RUN
    directory = Path(args[0])
    if not directory.is_dir():
        print(f"cannot run: {directory} is not a directory", file=sys.stderr)
        return CANNOT_RUN
    if not PROJECT_CONTRACT.is_file():
        print(f"cannot run: {PROJECT_CONTRACT} is missing; nothing can be validated without it",
              file=sys.stderr)
        return CANNOT_RUN

    home = toplevel_of(directory)
    report_rules_copy(home)
    target = home / PROJECT_FILE
    if not target.is_file():
        print(f"no project file: {target} does not exist; every root and the standard are named "
              f"per invocation, or declared once through /siegard-config")
        return 0

    try:
        declared = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as broken:
        print(f"{target}: does not parse as JSON: {broken}")
        return 1

    try:
        schema = json.loads(PROJECT_CONTRACT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as broken:
        print(f"cannot run: {PROJECT_CONTRACT} does not parse: {broken}", file=sys.stderr)
        return CANNOT_RUN
    try:
        from jsonschema import Draft202012Validator
    except ImportError:  # pragma: no cover - exercised by the environment, not the suite
        print("cannot run: jsonschema is required (pip install jsonschema)", file=sys.stderr)
        return CANNOT_RUN
    problems = sorted(Draft202012Validator(schema).iter_errors(declared), key=str)
    if problems:
        for error in problems:
            where = ".".join(str(part) for part in error.absolute_path) or "top level"
            print(f"{target}: {where}: {error.message}")
        return 1

    # Every declared path is relative to this file's own directory, which is what the contract
    # says of each of them. An absolute one silently wins the join (`home / "/etc/x"` is
    # `/etc/x`) and points every later reader outside the project it declared.
    standard = declared.get("standard")
    standards = (sorted(standard.items()) if isinstance(standard, dict)
                 else [(None, standard)] if "standard" in declared else [])
    escaped = sorted(
        f"{where}: {value}"
        for where, value in [("specification_root", declared.get("specification_root")),
                             ("work_root", declared.get("work_root")),
                             ("delivery_root", declared.get("delivery_root")),
                             ("telemetry_root", declared.get("telemetry_root"))]
        + [("standard" if name is None else f"standard.{name}", path)
           for name, path in standards]
        + [(f"targets.{name}", path)
           for name, path in sorted(declared.get("targets", {}).items())]
        if isinstance(value, str) and Path(value).is_absolute())
    if escaped:
        for line in escaped:
            print(f"{target}: {line} is absolute; every declared path is read relative to this "
                  f"file's own directory")
        return 1

    # A key naming no target suppresses nothing, and the one surface that would say so is here:
    # trace.py reads `edits_freely` defensively and drops a key `targets` does not hold.
    unknown = sorted(set(declared.get("edits_freely") or []) - set(declared.get("targets", {})))
    if unknown:
        for name in unknown:
            print(f"{target}: edits_freely names {name}, which targets does not declare; the "
                  f"exemption it was written for is silently suppressing nothing")
        return 1

    # The same silent no-op again: a test scope keyed by a target nobody declared reaches no
    # file, and trace.py, which reads `tests` defensively, would count every test unsurveyed.
    unknown = sorted(set(declared.get("tests") or {}) - set(declared.get("targets", {})))
    if unknown:
        for name in unknown:
            print(f"{target}: tests names {name}, which targets does not declare; the scopes "
                  f"declared under it reach no file")
        return 1

    # A standard governs one target. As an object it is keyed by target, and a key `targets`
    # does not hold governs nothing — the same silent no-op `edits_freely` is refused for above.
    # As a bare path it governs the one target the project has; over two or more it would answer
    # for a stack it was never written against, and the wrong registry passes the structural
    # check (two npm packages hold the same manifest names) and fails only once a rule's content
    # is applied, so the refusal is here, where it is cheap, rather than in a review, where it is
    # a finding nobody asked for.
    targets = declared.get("targets", {})
    if isinstance(standard, dict):
        unknown = sorted(set(standard) - set(targets))
        if unknown:
            for name in unknown:
                print(f"{target}: standard names {name}, which targets does not declare; a "
                      f"registry keyed by a target nobody declared governs nothing")
            return 1
    elif isinstance(standard, str) and len(targets) > 1:
        names = ", ".join(sorted(targets))
        print(f"{target}: standard names one registry, {standard}, while targets declares "
              f"{len(targets)} ({names}); a standard governs one target, and one registry "
              f"answering for every target answers wrongly for all but one. Declare one per "
              f"target — ready to paste, with the registry each target follows, or null where "
              f"it follows none:\n\n  /siegard-config\n\n  Project root: {home}\n"
              + "".join(f"  Standard for {name}: <registry path, or null>\n"
                        for name in sorted(targets)))
        return 1

    for name, path in standards:
        label = "standard" if name is None else f"standard {name}"
        if path is None:
            print(f"{label}: declared none")
            continue
        resolved = home / path
        if not resolved.is_file():
            print(f"{target}: {label} names {resolved}, which does not exist; a declaration "
                  f"that outlived its registry is corrected in the file, never guessed around")
            return 1
        print(f"{label}: {resolved}")

    if "specification_root" in declared:
        print(f"specification_root: {home / declared['specification_root']}")
    for name, path in sorted(declared.get("targets", {}).items()):
        print(f"target {name}: {home / path}")
    if "work_root" in declared:
        print(f"work_root: {home / declared['work_root']}")
    if "delivery_root" in declared:
        print(f"delivery_root: {home / declared['delivery_root']}")
    if "telemetry_root" in declared:
        print(f"telemetry_root: {home / declared['telemetry_root']}")
    if declared.get("edits_freely"):
        print(f"edits_freely: {', '.join(sorted(declared['edits_freely']))}")
    for name, scopes in sorted((declared.get("tests") or {}).items()):
        print(f"tests {name}: {'; '.join(spelled(scope) for scope in scopes)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
