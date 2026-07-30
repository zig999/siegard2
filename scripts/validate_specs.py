#!/usr/bin/env python3
"""Validate the specification set in specs/ against schemas/spec.v1.json.

This script is a boundary validator: it holds no rules of its own. Every frontmatter
constraint lives in the schema file, which is the single authority. The checks
implemented here are the ones a per-file JSON Schema cannot express — cross-file id
uniqueness, id/filename agreement, supersession targets that must exist, the sections a
specification requires for a given status, requirement ids that must be citable, and
concept links that must resolve. Frontmatter parsing is shared via
scripts/frontmatter_lib.py.

Two checks exist because a specification carries obligations an ADR does not:

- A requirement must be individually citable, so an impact artifact, a test, or an
  acceptance report can name the statement it satisfies or violates. Unnumbered prose
  is not citable, and a duplicate or skipped number breaks the citation silently.
- A term used normatively must resolve to the concept bundle, which CLAUDE.md makes the
  authority for framework vocabulary. A link to a concept that does not exist is
  vocabulary drift the moment it is written.

Declared dependencies: PyYAML, jsonschema. Both are required; the script exits with a
named error rather than degrading silently if either is missing.

Usage:  scripts/validate_specs.py [specs_root]   (default: specs)
Exit:   0 all specifications valid, 1 validation failures, 2 cannot run
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from frontmatter_lib import REPO_ROOT, display, split_frontmatter

SCHEMA_PATH = REPO_ROOT / "schemas" / "spec.v1.json"
RESERVED = {"README.md"}
SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# Sections every specification requires, whatever its status. Scope bounds what the
# document decides and what it leaves open; Definitions binds its vocabulary to the
# concept bundle; Requirements holds the citable normative statements.
REQUIRED_SECTIONS = ("## Scope", "## Definitions", "## Requirements")
# Required only while a specification is proposed, mirroring docs/adr/README.md: it
# states what must hold before the specification binds, and an accepted one records
# what satisfied it instead.
PROPOSED_SECTION = "## Validation required before acceptance"

SECTION_HEADING = re.compile(r"^## ", re.MULTILINE)
REQUIREMENT = re.compile(r"^- \*\*R(\d+)\*\*", re.MULTILINE)
MARKDOWN_LINK = re.compile(r"\]\(([^)\s]+)\)")

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


def section_body(body: str, heading: str) -> str:
    """Return the text under `heading`, up to the next `##` heading or end of file."""
    start = body.find(heading)
    if start == -1:
        return ""
    after = start + len(heading)
    match = SECTION_HEADING.search(body, after)
    return body[after : match.start()] if match else body[after:]


def check_requirements(body: str) -> list[str]:
    """Requirement ids must be present, unique, and sequential from R1.

    Sequential rather than merely unique: a gap means a requirement was deleted while
    something elsewhere may still cite it, and renumbering silently redirects that
    citation to a different statement.
    """
    found = [int(n) for n in REQUIREMENT.findall(section_body(body, "## Requirements"))]
    if not found:
        return [
            "the '## Requirements' section holds no requirement — "
            "each one is a line beginning '- **R<n>** '"
        ]
    problems: list[str] = []
    seen: set[int] = set()
    for position, number in enumerate(found, start=1):
        if number in seen:
            problems.append(f"requirement R{number} appears more than once")
        seen.add(number)
        if number != position:
            problems.append(
                f"requirement ids must be sequential from R1 in order of appearance: "
                f"position {position} holds R{number}"
            )
            break
    return problems


def check_concept_links(path: Path, body: str) -> list[str]:
    """Every link into the concept bundle must resolve to a file that exists."""
    problems: list[str] = []
    for target in MARKDOWN_LINK.findall(body):
        if "docs/concepts/" not in target:
            continue
        resolved = (path.parent / target.split("#", 1)[0]).resolve()
        if not resolved.is_file():
            problems.append(f"concept link '{target}' resolves to no file")
    return problems


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO_ROOT / "specs"
    if not root.is_dir():
        sys.exit(f"cannot run: specification root {root} does not exist")
    if not SCHEMA_PATH.is_file():
        sys.exit(f"cannot run: schema {SCHEMA_PATH} does not exist")

    validator = Draft202012Validator(json.loads(SCHEMA_PATH.read_text()))

    specs = sorted(p for p in root.glob("*.md") if p.name not in RESERVED)
    if not specs:
        sys.exit(f"cannot run: no specification files found under {root}")

    failures: list[str] = []
    seen_ids: dict[str, str] = {}
    supersessions: list[tuple[str, str]] = []  # (referrer path, target id)

    for path in specs:
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
        sid = data["id"]
        if sid in seen_ids:
            failures.append(f"{rel}: id '{sid}' already used by {seen_ids[sid]}")
        else:
            seen_ids[sid] = rel

        if stem_id != sid:
            failures.append(f"{rel}: filename must start with '{sid}-' to match id '{sid}'")
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

        if "## Requirements" in body:
            failures.extend(f"{rel}: {p}" for p in check_requirements(body))
        failures.extend(f"{rel}: {p}" for p in check_concept_links(path, body))

        if "superseded_by" in data:
            supersessions.append((rel, data["superseded_by"]))

    for rel, target in supersessions:
        if target not in seen_ids:
            failures.append(
                f"{rel}: superseded_by '{target}' names no specification in {display(root)}"
            )

    print(f"specifications checked: {len(specs)}  schema: {display(SCHEMA_PATH)}")
    if failures:
        print(f"FAILED: {len(failures)} problem(s)\n")
        for f in failures:
            print(f"  {f}")
        return 1
    print("all specifications valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
