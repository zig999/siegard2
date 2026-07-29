#!/usr/bin/env python3
"""Validate the ADR set in docs/adr/ against schemas/adr.v1.json.

This script is a boundary validator: it holds no rules of its own. Every frontmatter
constraint lives in the schema file, which is the single authority. The checks
implemented here are the ones a per-file JSON Schema cannot express — cross-file id
uniqueness, id/filename agreement, supersession targets that must exist, and the
sections docs/adr/README.md requires for a given status. Frontmatter parsing is shared
via scripts/frontmatter_lib.py.

Declared dependencies: PyYAML, jsonschema. Both are required; the script exits with a
named error rather than degrading silently if either is missing.

Usage:  scripts/validate_adrs.py [adr_root]   (default: docs/adr)
Exit:   0 all ADRs valid, 1 validation failures, 2 cannot run
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from frontmatter_lib import REPO_ROOT, display, split_frontmatter

SCHEMA_PATH = REPO_ROOT / "schemas" / "adr.v1.json"
RESERVED = {"README.md"}
SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# Sections docs/adr/README.md's format block requires. The Validation section is
# required only while a decision is proposed: it states what must hold before the
# decision binds, and an accepted ADR records what satisfied it instead.
REQUIRED_SECTIONS = ("## Context", "## Decision", "## Consequences")
PROPOSED_SECTION = "## Validation required before acceptance"

try:
    import yaml
except ImportError:
    sys.exit("cannot run: PyYAML is not installed (pip install pyyaml)")

try:
    from jsonschema import Draft202012Validator
except ImportError:
    sys.exit("cannot run: jsonschema is not installed (pip install jsonschema)")


def unquoted_id_hint(data: dict, stem_id: str) -> str | None:
    """Explain the YAML trap behind an id that did not arrive as a string.

    `id: 0010` resolves to octal 8 and `id: 0012` to 10, while `id: 0008` resolves to
    a string because 8 is not an octal digit. The schema's type error alone would send
    a reader looking for a value they never wrote.
    """
    raw = data.get("id")
    if raw is None or isinstance(raw, str):
        return None
    return (
        f"id: must be a quoted string. YAML resolved it to {raw!r} "
        f"({type(raw).__name__}) because leading-zero digits are read as octal — "
        f'write id: "{stem_id}"'
    )


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO_ROOT / "docs" / "adr"
    if not root.is_dir():
        sys.exit(f"cannot run: ADR root {root} does not exist")
    if not SCHEMA_PATH.is_file():
        sys.exit(f"cannot run: schema {SCHEMA_PATH} does not exist")

    validator = Draft202012Validator(json.loads(SCHEMA_PATH.read_text()))

    adrs = sorted(p for p in root.glob("*.md") if p.name not in RESERVED)
    if not adrs:
        sys.exit(f"cannot run: no ADR files found under {root}")

    failures: list[str] = []
    seen_ids: dict[str, str] = {}
    supersessions: list[tuple[str, str]] = []  # (referrer path, target id)

    for path in adrs:
        rel = display(path)
        try:
            data, body = split_frontmatter(path.read_text())
        except ValueError as exc:
            failures.append(f"{rel}: {exc}")
            continue
        except yaml.YAMLError as exc:
            failures.append(f"{rel}: frontmatter is not valid YAML: {exc}")
            continue

        stem_id, _, slug = path.stem.partition("-")

        hint = unquoted_id_hint(data, stem_id)
        if hint:
            failures.append(f"{rel}: {hint}")

        errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
        if hint:
            # The hint already explains the id, so the schema's type error on the
            # same field would only repeat it in less useful words.
            errors = [e for e in errors if list(e.path) != ["id"]]
        for err in errors:
            where = ".".join(str(p) for p in err.path) or "(root)"
            failures.append(f"{rel}: {where}: {err.message}")
        if errors or hint:
            continue

        # Constraints a per-file schema cannot express.
        aid = data["id"]
        if aid in seen_ids:
            failures.append(f"{rel}: id '{aid}' already used by {seen_ids[aid]}")
        else:
            seen_ids[aid] = rel

        if stem_id != aid:
            failures.append(f"{rel}: filename must start with '{aid}-' to match id '{aid}'")
        if not slug or not SLUG.match(slug):
            failures.append(f"{rel}: filename needs a kebab-case title after the id")

        for section in REQUIRED_SECTIONS:
            if section not in body:
                failures.append(f"{rel}: body is missing the '{section}' section")
        if data["status"] == "proposed" and PROPOSED_SECTION not in body:
            failures.append(
                f"{rel}: status is proposed, so the body needs the "
                f"'{PROPOSED_SECTION}' section stating what must hold before it binds"
            )

        if "superseded_by" in data:
            supersessions.append((rel, data["superseded_by"]))

    for rel, target in supersessions:
        if target not in seen_ids:
            failures.append(f"{rel}: superseded_by '{target}' names no ADR in {display(root)}")

    print(f"ADRs checked: {len(adrs)}  schema: {display(SCHEMA_PATH)}")
    if failures:
        print(f"FAILED: {len(failures)} problem(s)\n")
        for f in failures:
            print(f"  {f}")
        return 1
    print("all ADRs valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
