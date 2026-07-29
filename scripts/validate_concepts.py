#!/usr/bin/env python3
"""Validate a Siegard concept bundle against schemas/concept.v1.json.

This script is a boundary validator: it holds no rules of its own. Every constraint
lives in the schema file, which is the single authority. The checks implemented here
are the ones a JSON Schema cannot express — cross-file uniqueness, reserved filenames,
and id/filename agreement.

Declared dependencies: PyYAML, jsonschema. Both are required; the script exits with a
named error rather than degrading silently if either is missing.

Usage:  scripts/validate_concepts.py [bundle_root]   (default: docs/concepts)
Exit:   0 all concepts valid, 1 validation failures, 2 cannot run
"""

from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
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


def normalize(value):
    """Render YAML native timestamps as the canonical strings the schema expects.

    YAML resolves an unquoted `2026-07-29T16:33:28Z` to a datetime and an unquoted
    `2026-07-29` to a date. OKF's own example frontmatter is unquoted, so rejecting
    those would reject the form the spec documents. Normalizing here accepts both the
    quoted and unquoted forms while leaving the schema's pattern constraint meaningful.
    """
    if isinstance(value, dt.datetime):
        return value.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if isinstance(value, dt.date):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, dict):
        return {k: normalize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [normalize(v) for v in value]
    return value


def display(path: Path) -> str:
    """Repo-relative path when the file lives in the repo, absolute otherwise.

    The bundle root is a CLI argument, so it can legitimately point outside the repo.
    """
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def split_frontmatter(text: str, path: Path) -> dict:
    """Return the YAML frontmatter block as a dict, or raise ValueError."""
    if not text.startswith("---\n"):
        raise ValueError("file does not begin with a '---' frontmatter fence")
    end = text.find("\n---\n", 3)
    if end == -1:
        raise ValueError("frontmatter fence is never closed")
    block = text[4 : end + 1]
    data = yaml.safe_load(block)
    if not isinstance(data, dict):
        raise ValueError(f"frontmatter is {type(data).__name__}, expected a mapping")
    if not text[end + 5 :].strip():
        raise ValueError("concept has frontmatter but no body")
    return normalize(data)


def main() -> int:
    import json

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
            data = split_frontmatter(path.read_text(), path)
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
