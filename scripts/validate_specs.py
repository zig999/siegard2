#!/usr/bin/env python3
"""Validate the specification set in foundation/ against schemas/spec.json.

This script is a boundary validator: it holds no rules of its own. Every frontmatter
constraint lives in the schema file, which is the single authority. The checks
implemented here are the ones a per-file JSON Schema cannot express — cross-file id
uniqueness, id/filename agreement, the sections a specification requires for a given
status, requirement ids that must be citable, concept links that must resolve, and the
acceptance order the set declares about itself.
Frontmatter parsing is shared via scripts/frontmatter_lib.py.

Three checks exist because a specification carries obligations an ADR does not:

- A requirement must be individually citable, so an impact artifact, a test, or an
  acceptance report can name the statement it satisfies or violates. Unnumbered prose
  is not citable, and a duplicate or skipped number breaks the citation silently.
- A term used normatively must resolve to the concept bundle, which CLAUDE.md makes the
  authority for framework vocabulary. A link to a concept that does not exist is
  vocabulary drift the moment it is written, and a link whose label names one concept
  while pointing at another is the same drift with the evidence hidden: it resolves, so
  a check that only follows the path reports nothing.
- A specification cites other specifications normatively, and foundation/README.md states an
  acceptance rule over those citations: no specification is accepted before the one it
  depends on. That rule was prose nothing checked. The dependency edges are derived from
  the acceptance conditions the documents already write — an unresolved reference, a
  prerequisite marked met while its target is not accepted, an accepted specification
  still carrying an unmet prerequisite, and a cycle are each reported.

What this last check does not do is worth stating, because a reader could mistake its
green run for more than it is. It derives edges only from the "## Validation required
before acceptance" section, in the form the set already uses ("`foundation/NNNN` is
accepted"). An accepted specification replaces that section with what satisfied it, so
the prerequisite disappears from the text on acceptance and this script cannot audit a
promotion after the fact. What it catches is the drift while a document is still
proposed, and a promotion that leaves the claim behind.

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

from generator_lib import REPO_ROOT, display
from frontmatter_lib import split_frontmatter
from cli import cannot_run

SCHEMA_PATH = REPO_ROOT / "schemas" / "spec.json"
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
MARKDOWN_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")

# A citation of another specification, in the two forms the set uses: the bare
# `foundation/0004`, and the full `foundation/0004-generation-and-reproducibility.md`.
SPEC_REFERENCE = re.compile(r"foundation/(\d{4})(-[a-z0-9-]+\.md)?")
# A numbered item in an acceptance-condition list, with its continuation lines.
LIST_ITEM = re.compile(r"^\d+\. ", re.MULTILINE)
# The phrase the set uses for "this document cannot be accepted until that one is".
PREREQUISITE_PHRASE = "is accepted"
# How a met condition is marked, per the convention foundation/0009 established.
MET_MARKER = "**Met**"

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


def singular(word: str) -> str:
    """Strip the plural from one word, so a term matches its inflected form.

    A specification writes `artifact classes` where the concept is titled `artifact
    class`. That is the same term, and a check that called it a mismatch would be
    rejecting correct English rather than finding a defect.
    """
    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "y"
    if word.endswith(("ses", "xes", "ches", "shes")):
        return word[:-2]
    if word.endswith("s") and not word.endswith("ss") and len(word) > 3:
        return word[:-1]
    return word


def term_words(text: str) -> list[str]:
    """The words of a term, lowercased, unpunctuated, and singular.

    Punctuation goes because a link label is written both as prose and as the concept's
    file slug — `[change request]` and `[change-request]` name the same concept.
    """
    return [singular(word) for word in re.sub(r"[^a-z0-9]+", " ", text.lower()).split()]


def label_names(label: str, title: str) -> bool:
    """Whether a link label names the concept it points at.

    A shortened label is accepted only when it keeps the head noun — `[track]` for
    `generation track` — because English puts the head last and the qualifier is what a
    reader drops once the full term is in scope. A leading fragment is not accepted:
    `[knowledge]` for `knowledge base` is indistinguishable from a link that landed on
    the wrong file, which is the defect this check exists to catch.
    """
    got, want = term_words(label), term_words(title)
    if not got or not want:
        return False
    return got == want or (len(got) < len(want) and want[-len(got) :] == got)


def concept_title(path: Path) -> str | None:
    """The `title` a concept declares, or None where the file cannot supply one.

    A concept whose frontmatter is unreadable is `validate_concepts.py`'s failure to
    report, not this validator's; returning None here keeps one defect from being named
    twice in two different vocabularies.
    """
    try:
        data, _ = split_frontmatter(path.read_text())
    except (ValueError, yaml.YAMLError):
        return None
    title = data.get("title")
    return title if isinstance(title, str) else None


def check_concept_links(path: Path, body: str) -> list[str]:
    """Every link into the concept bundle must resolve, and must be labelled with the
    concept it resolves to."""
    problems: list[str] = []
    for label, target in MARKDOWN_LINK.findall(body):
        if "docs/concepts/" not in target:
            continue
        resolved = (path.parent / target.split("#", 1)[0]).resolve()
        if not resolved.is_file():
            problems.append(f"concept link '{target}' resolves to no file")
            continue
        title = concept_title(resolved)
        if title is not None and not label_names(label, title):
            problems.append(
                f"concept link '[{label}]({target})' is labelled '{label}' but points at "
                f"the concept titled '{title}' — the link resolves, so nothing else "
                f"catches it"
            )
    return problems


def check_spec_references(body: str, filenames: dict[str, str]) -> list[str]:
    """Every `foundation/NNNN` citation must name a specification that exists, by its real name.

    Both halves matter. An id nothing holds is a normative citation pointing at nothing,
    which is the failure ADR-0010 recorded for a deleted concept source. A filename that
    disagrees with the id is the same defect after a rename: the reference still looks
    right, and following it lands on nothing.
    """
    problems: list[str] = []
    for sid, filename in dict.fromkeys(SPEC_REFERENCE.findall(body)):
        if sid not in filenames:
            problems.append(f"reference 'foundation/{sid}' names no specification")
            continue
        if filename and filenames[sid] != f"{sid}{filename}":
            problems.append(
                f"reference 'foundation/{sid}{filename}' names a file that does not exist — "
                f"specification {sid} is '{filenames[sid]}'"
            )
    return problems


def acceptance_prerequisites(body: str) -> list[tuple[str, bool]]:
    """The specifications this one says must be accepted first, and whether it claims each is.

    Derived rather than declared. Every document already writes these as acceptance
    conditions, and adding a frontmatter field for them would put the same relation in
    two places — the drift this repository rejects everywhere else.
    """
    section = section_body(body, PROPOSED_SECTION)
    if not section:
        return []
    found: list[tuple[str, bool]] = []
    starts = [m.start() for m in LIST_ITEM.finditer(section)]
    for position, start in enumerate(starts):
        end = starts[position + 1] if position + 1 < len(starts) else len(section)
        item = section[start:end]
        if PREREQUISITE_PHRASE not in item:
            continue
        met = MET_MARKER in item
        for sid, _ in SPEC_REFERENCE.findall(item):
            found.append((sid, met))
    return found


def find_cycle(edges: dict[str, set[str]]) -> list[str] | None:
    """One cycle in the prerequisite graph, as the path that closes it, or None.

    A cycle is not a style problem: two specifications each waiting on the other can
    never be accepted, and neither document says so on its own page.
    """
    colour: dict[str, int] = {}  # 0 = on the current path, 1 = finished
    path: list[str] = []

    def walk(node: str) -> list[str] | None:
        colour[node] = 0
        path.append(node)
        for target in sorted(edges.get(node, ())):
            if colour.get(target) == 0:
                return path[path.index(target) :] + [target]
            if target not in colour:
                found = walk(target)
                if found:
                    return found
        path.pop()
        colour[node] = 1
        return None

    for node in sorted(edges):
        if node not in colour:
            found = walk(node)
            if found:
                return found
    return None


def check_acceptance_order(
    prerequisites: dict[str, list[tuple[str, bool]]],
    statuses: dict[str, str],
    paths: dict[str, str],
) -> list[str]:
    """The acceptance rule foundation/README.md states, over the derived prerequisite graph."""
    problems: list[str] = []
    edges: dict[str, set[str]] = {}
    for sid, entries in prerequisites.items():
        for target, met in entries:
            if target == sid:
                problems.append(
                    f"{paths[sid]}: acceptance condition requires specification {sid} — "
                    f"itself — to be accepted first"
                )
                continue
            if target not in statuses:
                continue  # check_spec_references already named it
            edges.setdefault(sid, set()).add(target)
            if met and statuses[target] != "accepted":
                problems.append(
                    f"{paths[sid]}: an acceptance condition is marked '{MET_MARKER}' on "
                    f"specification {target} being accepted, but {target} is "
                    f"'{statuses[target]}'"
                )
            if statuses[sid] == "accepted" and statuses[target] != "accepted":
                problems.append(
                    f"{paths[sid]}: accepted, but it still carries an unmet acceptance "
                    f"condition on specification {target}, which is "
                    f"'{statuses[target]}' — foundation/README.md forbids accepting a "
                    f"specification before the one it depends on"
                )

    cycle = find_cycle(edges)
    if cycle:
        problems.append(
            "acceptance prerequisites form a cycle, so none of these can ever be "
            "accepted: " + " → ".join(cycle)
        )
    return problems


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO_ROOT / "foundation"
    if not root.is_dir():
        cannot_run(f"cannot run: specification root {root} does not exist")
    if not SCHEMA_PATH.is_file():
        cannot_run(f"cannot run: schema {SCHEMA_PATH} does not exist")

    validator = Draft202012Validator(json.loads(SCHEMA_PATH.read_text()))

    specs = sorted(p for p in root.glob("*.md") if p.name not in RESERVED)
    if not specs:
        cannot_run(f"cannot run: no specification files found under {root}")

    failures: list[str] = []
    seen_ids: dict[str, str] = {}
    # Collected across the loop because a cross-file check cannot run until every file
    # has been read: a reference is only unresolved once the whole set is known.
    bodies: dict[str, str] = {}
    filenames: dict[str, str] = {}
    statuses: dict[str, str] = {}
    prerequisites: dict[str, list[tuple[str, bool]]] = {}

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

        bodies[sid] = body
        filenames[sid] = path.name
        statuses[sid] = data["status"]
        prerequisites[sid] = acceptance_prerequisites(body)

    # Cross-file, so they run once the whole set is known rather than per file.
    for sid, body in sorted(bodies.items()):
        failures.extend(f"{seen_ids[sid]}: {p}" for p in check_spec_references(body, filenames))
    failures.extend(check_acceptance_order(prerequisites, statuses, seen_ids))

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
