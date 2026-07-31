#!/usr/bin/env python3
"""Validate the ADR set in docs/adr/ against the contract each ADR declares.

This script is a boundary validator: it holds no rules of its own. Every frontmatter
constraint lives in the schema file, which is the single authority. The checks
implemented here are the ones a per-file JSON Schema cannot express — cross-file id
uniqueness, id/filename agreement, supersession and amendment targets that must exist,
the citation an amendment owes its reader, the sections docs/adr/README.md requires for
a given status, and the non-restatement rule that same file states: a Decision section
cites an operative rule, it does not reproduce one. Frontmatter parsing is shared via
scripts/frontmatter_lib.py.

Two contract versions are readable. `.claude/rules/compatibility.md` requires a consumer
to select behavior on `contract_version` rather than infer it from shape, so each ADR is
validated against the contract it declares. An ADR still declaring `adr/1` therefore
fails on that contract's terms — detectably outdated rather than quietly non-conforming.

Declared dependencies: PyYAML, jsonschema. Both are required; the script exits with a
named error rather than degrading silently if either is missing.

Usage:  scripts/validate_adrs.py [adr_root]   (default: docs/adr)
Exit:   0 all ADRs valid, 1 validation failures, 2 cannot run
"""

from __future__ import annotations

import difflib
import json
import re
import sys
from pathlib import Path

from frontmatter_lib import REPO_ROOT, display, split_frontmatter
from cli import cannot_run

SCHEMA_BY_VERSION = {
    "adr/1": REPO_ROOT / "schemas" / "adr.v1.json",
    "adr/2": REPO_ROOT / "schemas" / "adr.v2.json",
}
RESERVED = {"README.md"}
SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# Sections docs/adr/README.md's format block requires. The Validation section is
# required only while a decision is proposed: it states what must hold before the
# decision binds, and an accepted ADR records what satisfied it instead.
REQUIRED_SECTIONS = ("## Context", "## Decision", "## Consequences")
PROPOSED_SECTION = "## Validation required before acceptance"

# The non-restatement rule, stated in docs/adr/README.md: an ADR holds the alternative
# rejected and the cost accepted, while the imperative an agent follows is held by one
# operative artifact. These are the artifacts that hold operative rules in this
# repository. The threshold and the Decision-only scope are that file's, not this
# script's — see docs/concepts/operative-rule.md for the term.
DECISION_SECTION = "## Decision"
RESTATEMENT_THRESHOLD = 0.65
MIN_STATEMENT = 40  # characters of non-path content: below this, a line carries no rule

PATH_TOKEN = re.compile(r"[\w./-]+\.(?:md|json|py)\b|\b[a-z_]+/(?:\*\*|[\w*/-]+)")

try:
    import yaml
except ImportError:
    cannot_run("cannot run: PyYAML is not installed (pip install pyyaml)")

try:
    from jsonschema import Draft202012Validator
except ImportError:
    cannot_run("cannot run: jsonschema is not installed (pip install jsonschema)")


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


def normalize(line: str) -> str:
    """Reduce a line to comparable prose: no list marker, table cell, or emphasis."""
    text = re.sub(r"^[-*]\s+|^\d+\.\s+", "", line.strip())
    text = text.strip("|").strip().replace("`", "").replace("*", "")
    return re.sub(r"\s+", " ", text).lower().strip()


def substance(line: str) -> str:
    """A normalized line minus its path citations.

    An ADR and a rule file naming the same path is not a restatement. Measuring length
    on the remainder keeps a bare citation below the threshold that admits a statement.
    """
    return re.sub(r"\s+", " ", PATH_TOKEN.sub(" ", line)).strip()


def decision_lines(body: str) -> list[str]:
    """The raw lines under the Decision heading, up to the next section."""
    lines = body.splitlines()
    start = next(
        (i for i, l in enumerate(lines) if l.startswith(DECISION_SECTION)), None
    )
    if start is None:
        return []
    out: list[str] = []
    for line in lines[start + 1 :]:
        if line.startswith("## "):
            break
        out.append(line)
    return out


def operative_lines() -> list[tuple[str, str]]:
    """Every statement in the artifacts that hold operative rules.

    CLAUDE.md is required: without it the check cannot run, and a check that silently
    covers nothing reports success on a defect.
    """
    claude_md = REPO_ROOT / "CLAUDE.md"
    if not claude_md.is_file():
        cannot_run(
            f"cannot run: {display(claude_md)} does not exist, so the non-restatement "
            f"check would pass vacuously"
        )
    sources = [claude_md]
    rules_dir = REPO_ROOT / ".claude" / "rules"
    if rules_dir.is_dir():
        sources.extend(sorted(rules_dir.glob("*.md")))

    lines: list[tuple[str, str]] = []
    for path in sources:
        for raw in path.read_text().splitlines():
            norm = normalize(raw)
            if len(substance(norm)) >= MIN_STATEMENT:
                lines.append((display(path), norm))
    return lines


def restatements(
    body: str, operative: list[tuple[str, str]]
) -> list[tuple[float, str, str, str]]:
    """Decision-section lines that reproduce an operative rule.

    A blockquoted line is exempt. docs/adr/README.md admits a marked quotation on the
    ground that a reader can see it and will not mistake it for a second authority.
    """
    found: list[tuple[float, str, str, str]] = []
    for raw in decision_lines(body):
        if raw.lstrip().startswith(">"):
            continue
        line = normalize(raw)
        sub = substance(line)
        if len(sub) < MIN_STATEMENT:
            continue
        # Score on substance, never on the path-bearing line. A shared file path is a
        # citation both artifacts are supposed to make, so letting it drive the ratio
        # reports a restatement where two lines agree only on where a rule lives. This is
        # what substance() was written for; measuring length on it and then comparing the
        # unstripped text left the intent stated and unimplemented. The reported line and
        # rule stay unstripped, so a reader sees the real text rather than the residue.
        score, src, rule = max(
            (
                (
                    difflib.SequenceMatcher(
                        None, sub, substance(r), autojunk=False
                    ).ratio(),
                    s,
                    r,
                )
                for s, r in operative
            ),
            default=(0.0, "", ""),
        )
        if score >= RESTATEMENT_THRESHOLD:
            found.append((score, src, line, rule))
    return found


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO_ROOT / "docs" / "adr"
    if not root.is_dir():
        cannot_run(f"cannot run: ADR root {root} does not exist")
    for version, path in SCHEMA_BY_VERSION.items():
        if not path.is_file():
            cannot_run(f"cannot run: schema {path} for contract {version} does not exist")

    validators = {
        version: Draft202012Validator(json.loads(path.read_text()))
        for version, path in SCHEMA_BY_VERSION.items()
    }

    adrs = sorted(p for p in root.glob("*.md") if p.name not in RESERVED)
    if not adrs:
        cannot_run(f"cannot run: no ADR files found under {root}")

    operative = operative_lines()

    failures: list[str] = []
    seen_ids: dict[str, str] = {}
    versions: dict[str, int] = {}
    statuses: dict[str, str] = {}  # id -> status
    bodies: dict[str, str] = {}  # id -> body
    supersessions: list[tuple[str, str]] = []  # (referrer path, target id)
    amendments: list[tuple[str, str, str]] = []  # (referrer path, amender id, target id)

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

        declared = data.get("contract_version")
        if declared not in validators:
            supported = ", ".join(sorted(validators))
            failures.append(
                f"{rel}: contract_version {declared!r} names no contract in "
                f"{display(REPO_ROOT / 'schemas')} — supported: {supported}"
            )
            continue
        validator = validators[declared]
        versions[declared] = versions.get(declared, 0) + 1

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
            statuses[aid] = data["status"]
            bodies[aid] = body

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

        for score, src, line, rule in restatements(body, operative):
            failures.append(
                f"{rel}: '{DECISION_SECTION}' restates {src} at {score:.2f} similarity "
                f"— cite the rule instead of repeating it, or mark the line as a "
                f"blockquote if the repetition is deliberate\n"
                f"      ADR:  {line[:84]}\n"
                f"      rule: {rule[:84]}"
            )

        if "superseded_by" in data:
            supersessions.append((rel, data["superseded_by"]))
        if "amends" in data:
            amendments.append((rel, aid, data["amends"]))

    for rel, target in supersessions:
        if target not in seen_ids:
            failures.append(f"{rel}: superseded_by '{target}' names no ADR in {display(root)}")

    # An amendment revises part of a live decision. Each condition below marks a
    # relation that would leave a reader with the wrong decision in hand.
    for rel, amender, target in amendments:
        if target == amender:
            failures.append(f"{rel}: amends '{target}' names itself")
            continue
        if target not in seen_ids:
            failures.append(f"{rel}: amends '{target}' names no ADR in {display(root)}")
            continue
        if statuses[target] == "superseded":
            failures.append(
                f"{rel}: amends '{target}', which is superseded — amend the ADR that "
                f"replaced it, or supersede it in turn"
            )
        citation = f"ADR-{amender}"
        if citation not in bodies[target]:
            failures.append(
                f"{seen_ids[target]}: is amended by {citation} and never cites it — a "
                f"reader of this decision cannot see the frontmatter that moved it"
            )

    schemas = ", ".join(display(SCHEMA_BY_VERSION[v]) for v in sorted(SCHEMA_BY_VERSION))
    declared = ", ".join(f"{v}: {n}" for v, n in sorted(versions.items()))
    print(f"ADRs checked: {len(adrs)}  contracts: {schemas}  declared: {declared or 'none'}")
    print(
        f"non-restatement: {len(operative)} operative statement(s) from "
        f"{display(REPO_ROOT / 'CLAUDE.md')} and {display(REPO_ROOT / '.claude' / 'rules')}"
        f", threshold {RESTATEMENT_THRESHOLD}"
    )
    if failures:
        print(f"FAILED: {len(failures)} problem(s)\n")
        for f in failures:
            print(f"  {f}")
        return 1
    print("all ADRs valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
