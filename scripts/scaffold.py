#!/usr/bin/env python3
"""Expand a scaffold in templates/ into a conforming skeleton.

A [scaffold](../docs/concepts/scaffold.md) is a generator for an artifact *this repository
authors* — a specification, an ADR, a concept, a knowledge object, a component. It is not a
template in the sense of `foundation/0011`: a template expands structured domain knowledge into an
artifact class from the closed vocabulary of `foundation/0004` R8, holds byte identity, and ships
inside a target pack. None of that applies here, and using one word for both is the collision
`docs/adr/0010-projection-names-the-graph-derived-artifact.md` exists to prevent.

Two rules the two mechanisms do share, and both are enforced below.

**Output is validated before it is written.** A scaffold that produced a non-conforming skeleton
would put the author in the worst position: a file that looks finished and fails the validator
later, with no indication which part was the scaffold's fault.

**Nothing is minted.** A timestamp, an identifier, and a version come from the caller and are
never invented — `foundation/0011` R5 states it for templates, and a scaffold that invented one would
make the artifact irreproducible in the same way. Every placeholder is required for the same
reason: a default filled in silently is a decision nobody made.

Placeholders are `{{name}}`, and the required set is read from the template itself rather than
declared beside it. Two records of one fact drift, and the template is the one that cannot be
wrong about what it contains.

Declared dependencies: PyYAML, jsonschema.

Usage:
  scaffold.py --kind KIND --set name=value [--set ...] [--out PATH]
  scaffold.py --list
Exit: 0 written or printed, 1 the result does not conform, 2 cannot run
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from generator_lib import REPO_ROOT
from cli import cannot_run
from frontmatter_lib import split_frontmatter

# Both trees, in the order a name is looked up. `src/claude/` holds the scaffolds and
# contracts a consumer receives; the bare directories hold the ones that only ever describe
# this repository's own artifacts. Scaffolding spans the two because the generator is the
# thing that authors on both sides — it writes this repository's specifications and it is
# what a consumer's `concept.md` was written for.
SHIPPED_ROOT = REPO_ROOT / "src" / "claude"
TEMPLATE_ROOTS = (SHIPPED_ROOT / "templates", REPO_ROOT / "templates")
SCHEMA_ROOTS = (SHIPPED_ROOT / "schemas", REPO_ROOT / "schemas")


def _first(roots, name: str) -> Path:
    """The first tree holding `name`, or the shipped path so the error names one place."""
    for root in roots:
        candidate = root / name
        if candidate.is_file():
            return candidate
    return roots[0] / name
PLACEHOLDER = re.compile(r"\{\{([a-z0-9_]+)\}\}")

# Which contract validates each kind's output. The mapping is explicit rather than derived from
# the filename: `knowledge-object-rule` and `knowledge-object-definition` are two scaffolds over
# one contract, because `foundation/0003` gives each node type its own required fields and its own
# body sections, and one skeleton for six types would be a skeleton for none of them.
SCHEMA_BY_KIND = {
    "specification": "spec.json",
    "adr": "adr.json",
    "concept": "concept.json",
    "knowledge-object-definition": "knowledge-object.json",
    "knowledge-object-rule": "knowledge-object.json",
    "knowledge-object-lifecycle": "knowledge-object.json",
    "knowledge-object-interface": "knowledge-object.json",
    "knowledge-object-boundary": "knowledge-object.json",
    "knowledge-object-process": "knowledge-object.json",
    "knowledge-decision": "knowledge-decision.json",
    "skill": "skill.json",
    "agent": "agent.json",
    "pack-declaration": "pack-declaration.json",
    "specification-delta": "specification-delta.json",
    "validation-evidence": "validation-evidence.json",
}

# Kinds whose artifact is a JSON document rather than markdown with frontmatter. The distinction
# is the artifact's own form, not a property of scaffolding: a specification is a file with
# frontmatter and a specification delta is a JSON object, and validating either against its
# contract means parsing it the way its consumer will.
JSON_KINDS = frozenset({"pack-declaration", "specification-delta", "validation-evidence"})

try:
    import yaml
except ImportError:
    cannot_run("cannot run: PyYAML is not installed (pip install pyyaml)")

try:
    from jsonschema import Draft202012Validator
except ImportError:
    cannot_run("cannot run: jsonschema is not installed (pip install jsonschema)")


def template_path(kind: str) -> Path:
    return _first(TEMPLATE_ROOTS, f"{kind}.md")


def placeholders(text: str) -> list[str]:
    """Every placeholder the template uses, in first-appearance order."""
    seen: list[str] = []
    for name in PLACEHOLDER.findall(text):
        if name not in seen:
            seen.append(name)
    return seen


def expand(kind: str, values: dict[str, str]) -> tuple[str, list[str]]:
    """Substitute `values` into the template, returning the text and any problems."""
    path = template_path(kind)
    if not path.is_file():
        cannot_run(f"cannot run: no scaffold for kind '{kind}' at {path}")
    text = path.read_text()

    required = placeholders(text)
    missing = [name for name in required if name not in values]
    extra = [name for name in values if name not in required]
    problems = []
    if missing:
        problems.append(
            f"missing value(s) for {', '.join(missing)} — a scaffold fills in no default, "
            f"because a value nobody supplied is a decision nobody made"
        )
    if extra:
        problems.append(f"{kind} uses no placeholder named {', '.join(sorted(extra))}")
    if problems:
        return text, problems

    for name, value in values.items():
        text = text.replace(f"{{{{{name}}}}}", value)
    return text, []


def conforms(kind: str, text: str) -> list[str]:
    """Validate the produced artifact against the contract its kind names."""
    schema_path = _first(SCHEMA_ROOTS, SCHEMA_BY_KIND[kind])
    if not schema_path.is_file():
        cannot_run(f"cannot run: schema {schema_path} does not exist")
    if kind in JSON_KINDS:
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            return [f"the expanded scaffold is not valid JSON: {exc}"]
    else:
        try:
            data, _body = split_frontmatter(text)
        except (ValueError, yaml.YAMLError) as exc:
            return [f"the expanded scaffold is not a valid artifact: {exc}"]

    validator = Draft202012Validator(json.loads(schema_path.read_text()))
    return [
        f"{'.'.join(str(p) for p in err.path) or '(root)'}: {err.message}"
        for err in sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    ]


def main() -> int:
    parser = argparse.ArgumentParser(prog="scaffold.py", add_help=True)
    parser.add_argument("--kind", choices=sorted(SCHEMA_BY_KIND))
    parser.add_argument("--set", action="append", default=[], metavar="name=value")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()

    if args.list:
        for kind in sorted(SCHEMA_BY_KIND):
            path = template_path(kind)
            names = ", ".join(placeholders(path.read_text())) if path.is_file() else "(no template)"
            print(f"{kind}\n  schema: {SCHEMA_BY_KIND[kind]}\n  placeholders: {names}")
        return 0

    if not args.kind:
        cannot_run("cannot run: --kind is required (or --list to see them)")

    values: dict[str, str] = {}
    for pair in args.set:
        name, sep, value = pair.partition("=")
        if not sep:
            cannot_run(f"cannot run: --set expects name=value, got {pair!r}")
        values[name] = value

    text, problems = expand(args.kind, values)
    problems.extend(conforms(args.kind, text) if not problems else [])

    if problems:
        print(f"FAILED: {len(problems)} problem(s)\n", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        return 1

    if args.out:
        if args.out.exists():
            print(f"refused: {args.out} already exists", file=sys.stderr)
            return 1
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text)
        print(f"wrote {args.out} from the {args.kind} scaffold")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
