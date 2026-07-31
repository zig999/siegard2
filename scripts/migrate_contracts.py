#!/usr/bin/env python3
"""Executable migration paths between contract versions.

`.claude/rules/compatibility.md` requires a breaking change to "define the supported
migration path" and to "add a compatibility or migration test that fails against the old
behavior". The registry is empty: no contract in this repository carries a second version. The machinery
stays because the first real bump needs it, and because check_contract_versions.py fails a bump
that registers no path.

A migration here is a function, not a description, for the reason this repository applies
everywhere else: a path that is only written down is a path nobody has run. Registering one
is also what makes the coverage check in scripts/check_contract_versions.py possible — two
version files of the same contract with no migration between them is a bump that left its
consumers with no way forward, and that is now a validation failure rather than a discovery.

A migration transforms one instance document. It does not touch files, does not guess, and
raises on an input it was not given: an instance that does not declare the version being
migrated *from* is a caller error, and repairing it silently would hide which contract the
document actually came from.

Declared dependencies: none beyond the standard library.

Usage:  scripts/migrate_contracts.py <contract-from> <contract-to> <file.json|->
Exit:   0 migrated to stdout, 1 no path or the input does not match, 2 cannot run
"""

from __future__ import annotations

import json
import sys
from typing import Callable
import generator_lib  # noqa: F401  (puts src/claude/bin on the import path)
from cli import cannot_run


class MigrationError(Exception):
    """A migration was asked for something it cannot do."""


# Keyed by (from, to). A key here is the claim that a document can cross that boundary; the
# coverage check in check_contract_versions.py fails when a boundary exists and a key does not.
MIGRATIONS: dict[tuple[str, str], Callable[[dict], dict]] = {}


def migrate(doc: dict, source: str, target: str) -> dict:
    """Apply the registered path from `source` to `target`, one step at a time."""
    declared = doc.get("contract_version")
    if declared != source:
        raise MigrationError(
            f"instance declares contract_version {declared!r}, not {source!r} — a migration does "
            f"not guess which contract a document came from"
        )
    name, start = source.rsplit("/", 1)
    end_name, end = target.rsplit("/", 1)
    if name != end_name:
        raise MigrationError(f"cannot migrate across contracts: {source!r} to {target!r}")
    if int(end) < int(start):
        raise MigrationError(f"no downgrade path: {source!r} to {target!r}")

    current = doc
    for step in range(int(start), int(end)):
        hop = (f"{name}/{step}", f"{name}/{step + 1}")
        if hop not in MIGRATIONS:
            raise MigrationError(f"no migration registered for {hop[0]} to {hop[1]}")
        current = MIGRATIONS[hop](current)
    return current


def main() -> int:
    if len(sys.argv) != 4:
        cannot_run(
            "cannot run: usage: migrate_contracts.py <contract-from> <contract-to> <file.json|->"
        )
    source, target, path = sys.argv[1:]
    try:
        text = sys.stdin.read() if path == "-" else open(path).read()
        doc = json.loads(text)
    except (OSError, json.JSONDecodeError) as exc:
        cannot_run(f"cannot run: {exc}")

    try:
        print(json.dumps(migrate(doc, source, target), indent=2))
    except MigrationError as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
