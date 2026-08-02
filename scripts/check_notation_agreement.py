#!/usr/bin/env python3
"""Hold every knowledge profile to the one declaration of the storage notation.

A knowledge profile decides which kinds exist and what each requires of its own content. What it does
*not* decide is the envelope: `id`, `title`, `origin`, `gaps`, `sources` and the rest are the same
fields whatever the profile, and they are what makes a file readable by anything that reads the base
at all.

Three profiles shipped when this was written, agreeing on that envelope by coincidence of authorship.
Measured then: two of them differed, once annotations were stripped, in exactly four places — the
`contract_version` const, the `required` list, `$defs.attribute`, and the `rule` conditional. Every one
carried **completeness** rather than vocabulary. The other thirty-odd properties and the shared `$defs`
were the same assertions written down more than once.

Written more than once is one fact with several homes, and the drift would be invisible: each file
keeps validating while they disagree about a field. So `schemas/knowledge-notation.json` states the
envelope once and this holds every profile to it — which is what let two of the three be retired
without the envelope going with them.

**Why not `$ref`.** Composing the envelope across files is what JSON Schema references are for, and
it is not available here. The shipped scripts load a schema standalone — `Draft202012Validator(
json.loads(path.read_text()))` — under jsonschema 4.10, which resolves an unknown remote `$ref` by
fetching it. A consumer's boundary validator must not reach the network to decide whether an object
is valid, and `referencing` is not a dependency this distribution declares. So the envelope is
copied into each profile and this check is what makes the copy safe, exactly as
`schemas/contract-versions.json` makes a constraint digest safe without a second schema file.

Annotations are stripped before comparing, by `check_contract_versions.strip_annotations`. A profile
may word a description for its own readers; only the assertions have to agree.

Declared dependencies: none beyond the standard library.

Usage:  check_notation_agreement.py
Exit:   0 every profile carries the declared envelope, 1 one does not, 2 cannot run
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from check_contract_versions import strip_annotations
from cli import cannot_run

REPO_ROOT = Path(__file__).resolve().parent.parent
NOTATION = REPO_ROOT / "schemas" / "knowledge-notation.json"
SHIPPED_SCHEMAS = REPO_ROOT / "src" / "claude" / "schemas"

# The profiles this holds. Named rather than discovered: a schema in that directory is a contract
# over some artifact, and most of them — an impact analysis, an enrichment result — are not written
# in the notation at all. Discovery would have to guess which, and a wrong guess reports a false
# disagreement over a file that was never a profile.
#
# One entry today. It was three, and two were retired with the vocabulary they spelled — which is
# exactly when this check earned its keep: the envelope survived the retirement because it was
# stated somewhere other than in the files that went.
PROFILES = ("domain-object.json",)


def canonical(node) -> str:
    return json.dumps(strip_annotations(node), sort_keys=True, ensure_ascii=False)


def disagreements(profile: dict, envelope: dict, name: str) -> list[str]:
    """Every place this profile departs from the declared envelope."""
    problems: list[str] = []

    for keyword in ("type", "additionalProperties"):
        if profile.get(keyword) != envelope[keyword]:
            problems.append(
                f"{name}: `{keyword}` is {profile.get(keyword)!r} and the notation declares "
                f"{envelope[keyword]!r}"
            )

    declared = profile.get("properties") or {}
    for field, shape in envelope["properties"].items():
        if field not in declared:
            problems.append(
                f"{name}: the envelope field `{field}` is absent. A profile chooses its types and "
                f"its content, never which envelope a file carries"
            )
            continue
        if canonical(declared[field]) != canonical(shape):
            problems.append(
                f"{name}: `{field}` asserts something the notation does not. Word the description "
                f"as this profile needs; change the assertions in schemas/knowledge-notation.json "
                f"and let every profile follow"
            )

    for field in envelope["required_keys"]:
        if field not in declared:
            problems.append(
                f"{name}: `{field}` is absent, and the notation requires every profile to define "
                f"one of its own"
            )

    shared = profile.get("$defs") or {}
    for name_, shape in envelope["$defs"].items():
        if name_ not in shared:
            problems.append(f"{name}: `$defs.{name_}` is absent, and the envelope references it")
        elif canonical(shared[name_]) != canonical(shape):
            problems.append(
                f"{name}: `$defs.{name_}` asserts something the notation does not"
            )

    return problems


def main() -> int:
    if not NOTATION.is_file():
        cannot_run(f"cannot run: {NOTATION.relative_to(REPO_ROOT)} does not exist")
    try:
        envelope = json.loads(NOTATION.read_text())["envelope"]
    except (json.JSONDecodeError, KeyError) as exc:
        cannot_run(f"cannot run: {NOTATION.name} does not declare an envelope — {exc}")

    problems: list[str] = []
    checked = 0
    for filename in PROFILES:
        path = SHIPPED_SCHEMAS / filename
        if not path.is_file():
            # A profile named here and absent is a rename or a removal that did not reach this
            # list. Reported rather than skipped: a check that quietly stops checking is the
            # failure this file exists to prevent.
            problems.append(
                f"{filename}: named as a profile and not found under src/claude/schemas/. Either "
                f"it was removed and PROFILES still names it, or it moved"
            )
            continue
        checked += 1
        problems += disagreements(json.loads(path.read_text()), envelope, filename)

    print(
        f"notation agreement checked: {checked} profile(s) against "
        f"{len(envelope['properties'])} envelope field(s)  "
        f"declaration: schemas/{NOTATION.name}"
    )
    if problems:
        print(f"FAILED: {len(problems)} disagreement(s)\n")
        for problem in problems:
            print(f"  {problem}")
        return 1
    print("every profile carries the envelope the notation declares")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
