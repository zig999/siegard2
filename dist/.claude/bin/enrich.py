#!/usr/bin/env python3
"""Hold an enriched prompt to its contract: the sections, their order, their provenance and its fields.

`/enrich-request` ends in one prompt written as sections. What makes that prompt well-formed is
decidable without a model, so it is decided here and not re-read by the skill: every section is one
`schemas/enriched-prompt.json` names, none is empty, they come in the canonical order, nothing
precedes the first, every required section is present, a line of a justified section carries a
statement and its reason, and every bracketed field is a readable one. Whether the additions are
worth keeping and whether the prompt preserves what the person meant is not decidable here and is
not checked.

Sections are read as `bin/clarify.py` reads them, through its `parse`.

What no mechanism decides is reported and refused on nothing: after `ok`, one line counts the
additions and names the longest, one counts the bracketed fields and the sections holding them, so a
reader can open the far end of the distribution.

Declared dependencies: jsonschema.

Usage:  enrich.py <file>    hold the prompt in <file> to the contract
        enrich.py -         hold the prompt read from standard input
        enrich.py --help    print this text and stop
Exit:   0 well-formed: `ok`, then the two report lines
        1 the prompt does not hold: one problem per line
        2 cannot run
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

import clarify

CANNOT_RUN = 2
CONTRACT = Path(__file__).resolve().parent.parent / "schemas" / "enriched-prompt.json"


def check(text: str, contract: dict) -> list[str]:
    sections, problems = clarify.parse(text)
    declared = list(contract["properties"])
    for name in sections:
        if name not in declared:
            problems.append(f"section {name} is not one the contract names")
    known = [name for name in sections if name in declared]
    if known != sorted(known, key=declared.index):
        problems.append("sections are out of the canonical order: " + ", ".join(declared))
    known_only = {name: lines for name, lines in sections.items() if name in declared}
    for error in sorted(Draft202012Validator(contract).iter_errors(known_only), key=str):
        where = "/".join(str(part) for part in error.absolute_path) or "(prompt)"
        problems.append(f"{where}: {error.message}")
    justified = contract["x-justified-sections"]
    separator = justified["separator"]
    for name in justified["values"]:
        for line in known_only.get(name, []):
            statement, _, reason = line.partition(separator)
            if not reason.strip() or not statement.strip():
                problems.append(f"{name}: a line is a statement, {separator.strip()!r}, and its reason: {line[:60]!r}")
    field = re.compile(contract["x-field"]["pattern"])
    for name, lines in known_only.items():
        for line in lines:
            rest = field.sub("", line)
            if "[" in rest or "]" in rest:
                problems.append(f"{name}: a bracket that is not one readable field: {line[:60]!r}")
    return problems


def report(text: str, contract: dict) -> list[str]:
    """Two lines: the additions and the longest one; the fields and where they stand."""
    sections = clarify.parse(text)[0]
    additions = sections.get("ADDITIONS", [])
    longest = max(additions, key=len)[:80] if additions else "-"
    field = re.compile(contract["x-field"]["pattern"])
    holding = {name: sum(len(field.findall(line)) for line in lines) for name, lines in sections.items()}
    holding = {name: count for name, count in holding.items() if count}
    where = ", ".join(f"{name} {count}" for name, count in holding.items()) or "-"
    return [f"additions: {len(additions)}; longest: {longest}", f"fields: {sum(holding.values())}; in: {where}"]


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
    if problems:
        return 1
    print("ok")
    for line in report(text, contract):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
