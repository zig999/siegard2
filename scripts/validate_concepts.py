#!/usr/bin/env python3
"""Validate a Siegard concept bundle against schemas/concept.v1.json.

This script is a boundary validator: it holds no rules of its own. Every constraint
lives in the schema file, which is the single authority. The checks implemented here
are the ones a JSON Schema cannot express — cross-file uniqueness, reserved filenames,
and id/filename agreement. Frontmatter parsing is shared via scripts/frontmatter_lib.py.

Declared dependencies: PyYAML, jsonschema. Both are required; the script exits with a
named error rather than degrading silently if either is missing.

Usage:  scripts/validate_concepts.py [bundle_root]   (default: docs/concepts)
Exit:   0 all concepts valid, 1 validation failures, 2 cannot run
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from frontmatter_lib import REPO_ROOT, display, split_frontmatter

SCHEMA_PATH = REPO_ROOT / "schemas" / "concept.v1.json"
RESERVED = {"index.md", "log.md"}

try:
    import yaml
except ImportError:
    sys.exit("cannot run: PyYAML is not installed (pip install pyyaml)")

try:
    from jsonschema import Draft202012Validator
except ImportError:
    sys.exit("cannot run: jsonschema is not installed (pip install jsonschema)")


def main() -> int:
    bundle = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO_ROOT / "docs" / "concepts"
    if not bundle.is_dir():
        sys.exit(f"cannot run: bundle root {bundle} does not exist")
    if not SCHEMA_PATH.is_file():
        sys.exit(f"cannot run: schema {SCHEMA_PATH} does not exist")

    validator = Draft202012Validator(json.loads(SCHEMA_PATH.read_text()))

    concepts = sorted(p for p in bundle.rglob("*.md") if p.name not in RESERVED)
    if not concepts:
        sys.exit(f"cannot run: no concept files found under {bundle}")

    failures: list[str] = []
    seen_ids: dict[str, str] = {}

    for path in concepts:
        rel = display(path)
        try:
            data, _body = split_frontmatter(path.read_text())
        except ValueError as exc:
            failures.append(f"{rel}: {exc}")
            continue
        except yaml.YAMLError as exc:
            failures.append(f"{rel}: frontmatter is not valid YAML: {exc}")
            continue

        errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
        for err in errors:
            where = ".".join(str(p) for p in err.path) or "(root)"
            failures.append(f"{rel}: {where}: {err.message}")
        if errors:
            continue

        # Constraints a per-file schema cannot express.
        cid = data["id"]
        if cid in seen_ids:
            failures.append(f"{rel}: id '{cid}' already used by {seen_ids[cid]}")
        else:
            seen_ids[cid] = rel

        expected_stem = cid.split(".", 1)[1]
        if path.stem != expected_stem:
            failures.append(f"{rel}: filename must be '{expected_stem}.md' to match id '{cid}'")

    print(f"concepts checked: {len(concepts)}  schema: {display(SCHEMA_PATH)}")
    if failures:
        print(f"FAILED: {len(failures)} problem(s)\n")
        for f in failures:
            print(f"  {f}")
        return 1
    print("all concepts valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
