#!/usr/bin/env python3
"""Resolve the project file: every root and the standard a consumer declared, read from disk.

A value retyped per invocation is a value a session can forget or mistype — one consumer's
registry sat unnamed across invocations that its own delivery root remembered, and a specification
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

A standard governs one target. Declared as an object keyed by target, each entry prints on its
own line — `standard <target>: <path>` or `standard <target>: declared none` — and the calling
skill reads the line for the target it was invoked over; a target the object lacks a line for is
an absence, and the skill's stop. Declared as a bare path, it prints as `standard: <path>` and is
refused here where `targets` holds more than one key: one registry answering for two stacks is
the wrong registry for one of them, and that error passes every structural check.

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
import subprocess
import sys
from pathlib import Path

CANNOT_RUN = 2

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover - exercised by the environment, not the suite
    print("cannot run: jsonschema is required (pip install jsonschema)", file=sys.stderr)
    raise SystemExit(CANNOT_RUN)

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
PROJECT_CONTRACT = PLUGIN_ROOT / "schemas" / "project.json"
PROJECT_FILE = "siegard.json"


def toplevel_of(directory: Path) -> Path:
    """Where the project file sits: the directory's git toplevel, or the directory itself
    where git does not hold it — deterministic either way, because the directory is a named
    input and never the session's working directory."""
    try:
        probe = subprocess.run(["git", "-C", str(directory), "rev-parse", "--show-toplevel"],
                               capture_output=True, text=True)
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
