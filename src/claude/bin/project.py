#!/usr/bin/env python3
"""Resolve the project file: which standard a consumer declared, read from disk.

Three skills take the project's standard as an optional input, and a value retyped per
invocation is a value a session can forget or mistype — one consumer's registry sat unnamed
across invocations that its own delivery root remembered. `siegard.json` is where a project
declares it once: at the git toplevel of the target source root, beside the tree it speaks
for, in the consumer's own hands. This script is the one reader — it finds the file, holds it
to `schemas/project.json`, and prints what was declared. A skill never parses the file itself,
and an answer given in a session persists only by the file gaining it.

What the resolution means is the contract's business, stated once in the schema: a standard
named in the invocation wins over the file, `null` declares the narrow path deliberately, and
an absent file declares nothing — the skill's stop, never this script's, which is why absence
exits 0: it is a fact to report, not a defect to refuse.

Declared dependencies: jsonschema.

Usage:  project.py <directory>     resolve siegard.json for the tree holding <directory> —
                                   the file sits at the directory's git toplevel, or at the
                                   directory itself where git does not hold it
Exit:   0 resolved: a declared standard, a declared none, or no file, each said in one line
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
    probe = subprocess.run(["git", "-C", str(directory), "rev-parse", "--show-toplevel"],
                           capture_output=True, text=True)
    if probe.returncode == 0 and probe.stdout.strip():
        return Path(probe.stdout.strip())
    return directory


def main() -> int:
    args = sys.argv[1:]
    if len(args) != 1 or args[0].startswith("--"):
        print("cannot run: expected <directory>", file=sys.stderr)
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
        print(f"no project file: {target} does not exist; a standard is named per invocation, "
              f"or declared once by creating the file")
        return 0

    try:
        declared = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as broken:
        print(f"{target}: does not parse as JSON: {broken}")
        return 1

    schema = json.loads(PROJECT_CONTRACT.read_text(encoding="utf-8"))
    problems = sorted(Draft202012Validator(schema).iter_errors(declared), key=str)
    if problems:
        for error in problems:
            where = ".".join(str(part) for part in error.absolute_path) or "top level"
            print(f"{target}: {where}: {error.message}")
        return 1

    standard = declared["standard"]
    if standard is None:
        print("standard: declared none")
        return 0
    resolved = home / standard
    if not resolved.is_file():
        print(f"{target}: names {resolved}, which does not exist; a declaration that outlived "
              f"its registry is corrected in the file, never guessed around")
        return 1
    print(f"standard: {resolved}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
