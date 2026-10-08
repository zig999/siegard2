#!/usr/bin/env python3
"""Hold a clarified request to its contract: the sections, their order, and the mode's bound.

`/clarify-request` ends in one instruction written as sections. What makes that instruction
well-formed is decidable without a model, so it is decided here and not re-read by the skill: every
section is one `schemas/clarified-request.json` names, none is empty, they come in the canonical
order, nothing precedes the first, `MODE` and `TASK` are present, a mode that authorizes no change
carries a constraint bounding the whole project, and a mode that authorizes one carries none.
Whether the instruction preserves what the operator meant is not decidable here and is not checked.

A section opens with its name in capitals and a colon at the start of a line; text after the colon
is the section's first line. The instruction is held without a code fence around it. A leading
`- ` on a line is dropped. A line starting a section the contract does not name is refused rather
than read as content — a stray `NOTE:` is a section the executor would not know the meaning of.

Declared dependencies: jsonschema.

Usage:  clarify.py <file>    hold the instruction in <file> to the contract
        clarify.py -         hold the instruction read from standard input
        clarify.py --help    print this text and stop
Exit:   0 well-formed: nothing printed
        1 the instruction does not hold: one problem per line
        2 cannot run
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

CANNOT_RUN = 2
CONTRACT = Path(__file__).resolve().parent.parent / "schemas" / "clarified-request.json"
HEADER = re.compile(r"^([A-Z][A-Z_]*):[ \t]*(.*)$")


def parse(text: str) -> tuple[dict[str, list[str]], list[str]]:
    """The instruction as one array of lines per section, and the problems found reading it."""
    sections: dict[str, list[str]] = {}
    problems: list[str] = []
    current: str | None = None
    for number, raw in enumerate(text.splitlines(), 1):
        if not raw.strip():
            continue
        header = HEADER.match(raw)
        if header:
            current = header.group(1)
            if current in sections:
                problems.append(f"line {number}: section {current} appears twice")
            sections.setdefault(current, [])
            raw = header.group(2)
            if not raw.strip():
                continue
        elif current is None:
            problems.append(f"line {number}: text before the first section: {raw.strip()[:60]!r}")
            continue
        line = re.sub(r"^\s*-\s+", "", raw).strip()
        if line:
            sections[current].append(line)
    return sections, problems


def check(text: str, contract: dict) -> list[str]:
    sections, problems = parse(text)
    declared = list(contract["properties"])
    for name in sections:
        if name not in declared:
            problems.append(f"section {name} is not one the contract names")
    known = [name for name in sections if name in declared]
    if known != sorted(known, key=declared.index):
        problems.append("sections are out of the canonical order: " + ", ".join(declared))
    known_only = {name: lines for name, lines in sections.items() if name in declared}
    for error in sorted(Draft202012Validator(contract).iter_errors(known_only), key=str):
        where = "/".join(str(part) for part in error.absolute_path) or "(instruction)"
        problems.append(f"{where}: {error.message}")
    bound = contract["x-read-only-modes"]
    prefixes = tuple(bound["constraint-prefixes"])
    mode = known_only.get("MODE", [None])[0]
    bounding = [line for line in known_only.get("CONSTRAINTS", []) if line.startswith(prefixes)]
    if mode in bound["values"] and not bounding:
        problems.append(f"mode {mode} authorizes no change to the project's files and CONSTRAINTS carries no line "
                        f"beginning {' or '.join(repr(p) for p in prefixes)}")
    if mode and mode not in bound["values"] and bounding:
        problems.append(f"mode {mode} authorizes a change and CONSTRAINTS says {bounding[0]!r}")
    return problems


def main() -> int:
    args = sys.argv[1:]
    if "--help" in args:
        print(__doc__.strip())
        return 0
    if len(args) != 1:
        print("cannot run: expected <file> or -", file=sys.stderr)
        return CANNOT_RUN
    try:
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as broken:
        print(f"cannot run: {CONTRACT} is unreadable: {broken}", file=sys.stderr)
        return CANNOT_RUN
    try:
        text = sys.stdin.read() if args[0] == "-" else Path(args[0]).read_text(encoding="utf-8")
    except OSError as broken:
        print(f"cannot run: {broken}", file=sys.stderr)
        return CANNOT_RUN
    problems = check(text, contract)
    for problem in problems:
        print(problem)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
