#!/usr/bin/env python3
"""Validate a Siegard concept bundle against schemas/concept.json.

This script is a boundary validator: it holds no rules of its own. Every constraint
lives in the schema file, which is the single authority. The checks implemented here
are the ones a JSON Schema cannot express — cross-file uniqueness, reserved filenames,
id/filename agreement, and whether a declared source still exists. Frontmatter parsing
is shared via bin/frontmatter_lib.py.

Declared dependencies: PyYAML, jsonschema. Both are required; the script exits with a
named error rather than degrading silently if either is missing.

Usage: bin/validate_concepts.py <bundle_root>
Exit: 0 all concepts valid, 1 validation failures, 2 cannot run
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path, PurePosixPath

from frontmatter_lib import INVOCATION_ROOT, PLUGIN_ROOT, display, split_frontmatter
from cli import cannot_run

SCHEMA_PATH = PLUGIN_ROOT / "schemas" / "concept.json"
RESERVED = {"index.md", "log.md"}
URI_SCHEME = re.compile(r"^[a-z][a-z0-9+.\-]*://")

try:
    import yaml
except ImportError:
    cannot_run("cannot run: PyYAML is not installed (pip install pyyaml)")

try:
    from jsonschema import Draft202012Validator
except ImportError:
    cannot_run("cannot run: jsonschema is not installed (pip install jsonschema)")


def check_sources(data: dict) -> list[str]:
    """Every source that is not an absolute URI must resolve to a file in this repository.

    The schema requires `resource` to be a repo-relative path or an absolute URI and cannot
    reach the filesystem, so this is the half a JSON Schema cannot hold.

    What it catches is provenance rot: a concept outliving the artifact that minted it.
    the decision that `projection` names the graph-derived artifact records the instance that
    demanded the check. the projection definition was sourced from an ADR that was later
    deleted, the dangling reference was replaced rather than reported, and the definition
    then drifted from what cited it while every file still validated on its own.

    It bounds the failure rather than closing it: a source that resolves says nothing about
    whether the definition still matches what the source decided.
    """
    problems: list[str] = []
    for index, source in enumerate(data.get("sources") or []):
        resource = source["resource"]
        if URI_SCHEME.match(resource):
            continue
        as_path = PurePosixPath(resource)
        if as_path.is_absolute() or ".." in as_path.parts:
            problems.append(
                f"sources.{index}.resource: '{resource}' must be a repo-relative path or an "
                f"absolute URI"
            )
            continue
        if not (INVOCATION_ROOT / resource).is_file():
            problems.append(
                f"sources.{index}.resource: '{resource}' resolves to no file — a source that "
                f"no longer exists is provenance nothing supports"
            )
    return problems


def concept_files(bundle: Path) -> list[Path]:
    return sorted(p for p in bundle.rglob("*.md") if p.name not in RESERVED)


def validate(bundle: Path) -> list[str]:
    """Check every concept in one bundle, returning every problem found."""
    validator = Draft202012Validator(json.loads(SCHEMA_PATH.read_text()))
    problems: list[str] = []
    seen_ids: dict[str, str] = {}

    for path in concept_files(bundle):
        rel = display(path)
        try:
            data, _body = split_frontmatter(path.read_text())
        except ValueError as exc:
            problems.append(f"{rel}: {exc}")
            continue
        except yaml.YAMLError as exc:
            problems.append(f"{rel}: frontmatter is not valid YAML: {exc}")
            continue

        errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
        for err in errors:
            where = ".".join(str(p) for p in err.path) or "(root)"
            problems.append(f"{rel}: {where}: {err.message}")
        if errors:
            continue

        # Constraints a per-file schema cannot express.
        cid = data["id"]
        if cid in seen_ids:
            problems.append(f"{rel}: id '{cid}' already used by {seen_ids[cid]}")
        else:
            seen_ids[cid] = rel

        expected_stem = cid.split(".", 1)[1]
        if path.stem != expected_stem:
            problems.append(f"{rel}: filename must be '{expected_stem}.md' to match id '{cid}'")

        problems.extend(f"{rel}: {problem}" for problem in check_sources(data))

    return problems


def main() -> int:
    if len(sys.argv) < 2:
        cannot_run("cannot run: name the concept bundle root; there is no default")
    bundle = Path(sys.argv[1])
    if not bundle.is_dir():
        cannot_run(f"cannot run: bundle root {bundle} does not exist")
    if not SCHEMA_PATH.is_file():
        cannot_run(f"cannot run: schema {SCHEMA_PATH} does not exist")

    concepts = concept_files(bundle)
    if not concepts:
        cannot_run(f"cannot run: no concept files found under {bundle}")

    failures = validate(bundle)

    print(f"concepts checked: {len(concepts)} schema: {display(SCHEMA_PATH)}")
    if failures:
        print(f"FAILED: {len(failures)} problem(s)\n")
        for f in failures:
            print(f" {f}")
        return 1
    print("all concepts valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
