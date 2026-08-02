#!/usr/bin/env python3
"""Hold the enrichment pass to the fields it owns, by comparing against what the analysis wrote.

The enrichment writes four fields and a body into an object and must change nothing else. A tool
grant cannot express that: a grant names tools, not files, and certainly not keys within a file, so
the restriction is prose until something checks it. This is that something, and it is why the check
exists before the pass it checks rather than after.

The method is a seal. `seal_analysis.py` records, per object, a digest of every field on the
analysis's side of the line, the `kind: domain` gaps verbatim, and the body headings. This
recomputes each digest and reports what moved.

**It used to re-derive instead, and could because a deterministic script wrote the objects.** Given
the same inputs that script yielded the same bytes, so "before" was a function nobody had to keep.
That stops holding the moment a producer writes by judgment: two runs of an analysis over one
request agree in meaning and not in bytes, and a re-derivation would report every such difference as
an enrichment that overstepped. A recorded baseline is what replaces the function, and it is written
by something other than the producer for the reason a producer's self-report is not a guarantee.

What it reports, per object: a field on the analysis's side that differs, a `kind: domain` gap that
was removed, an `authoring` gap left open beside the field it names, and a body heading added or
renamed. What it does not report is the four fields and the body content, which are the enrichment's
to write.

Declared dependencies: PyYAML.

Usage:  check_field_ownership.py <seal.json> <root>
Exit:   0 the enrichment stayed inside its fields, 1 it did not, 2 cannot run
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from field_ownership import ENRICHMENT_FIELDS, SHARED_FIELD, closable, digest, expansion_owns

CANNOT_RUN = 2
SEAL_CONTRACT = "analysis-seal/1"
HEADING = re.compile(r"^## (.+)$", re.MULTILINE)

try:
    import yaml
except ImportError:  # pragma: no cover - exercised by the environment, not the suite
    print("cannot run: PyYAML is not installed (pip install pyyaml)", file=sys.stderr)
    raise SystemExit(CANNOT_RUN)


def split(path: Path) -> tuple[dict, str]:
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", path.read_text(), re.S)
    if not match:
        raise ValueError(f"{path} carries no frontmatter fence")
    return yaml.safe_load(match.group(1)) or {}, match.group(2)


def compare(sealed: dict, data: dict, body: str, relative: str) -> list[str]:
    """Every difference the enrichment was not permitted to make, in one object."""
    problems: list[str] = []
    recorded = sealed["fields"]

    for field in sorted(set(recorded) | {f for f in data if expansion_owns(f)}):
        if not expansion_owns(field):
            continue
        if field not in data:
            problems.append(
                f"{relative}: `{field}` was written by the analysis and is gone. The enrichment "
                f"writes {', '.join(ENRICHMENT_FIELDS)} and the body, and removes nothing"
            )
        elif field not in recorded:
            problems.append(
                f"{relative}: `{field}` is not a field the analysis wrote. The enrichment writes "
                f"{', '.join(ENRICHMENT_FIELDS)} and the body, and adds no other"
            )
        elif digest(data[field]) != recorded[field]:
            problems.append(
                f"{relative}: `{field}` differs from what the analysis wrote. The enrichment "
                f"writes {', '.join(ENRICHMENT_FIELDS)} and the body, and reports a disagreement "
                f"with anything else as a finding rather than editing it"
            )

    kept = {json.dumps(gap, sort_keys=True) for gap in data.get(SHARED_FIELD) or []}
    for gap in sealed["domain_gaps"]:
        if json.dumps(gap, sort_keys=True) not in kept:
            problems.append(
                f"{relative}: the `kind: domain` gap on `{gap['field']}` was removed. Only whoever "
                f"knows the domain closes one, and no pass of this pipeline may"
            )

    for gap in data.get(SHARED_FIELD) or []:
        if closable(gap) and gap.get("field") in ENRICHMENT_FIELDS and data.get(gap["field"]):
            problems.append(
                f"{relative}: `{gap['field']}` is written and its `authoring` gap is still open — "
                f"closing the gap is what records that the field was filled"
            )

    if HEADING.findall(body) != sealed["headings"]:
        problems.append(
            f"{relative}: the body headings changed. The analysis places the two its node type "
            f"requires and the enrichment fills them; a third heading is one the contract refuses"
        )
    return problems


def main() -> int:
    if len(sys.argv) != 3:
        print("cannot run: expected <seal.json> <root>", file=sys.stderr)
        return CANNOT_RUN
    seal_path, root = Path(sys.argv[1]), Path(sys.argv[2])
    if not seal_path.is_file() or not root.is_dir():
        print(f"cannot run: {seal_path} or {root} does not exist", file=sys.stderr)
        return CANNOT_RUN

    try:
        seal = json.loads(seal_path.read_text())
    except json.JSONDecodeError as broken:
        print(f"cannot run: {seal_path} is not valid JSON — {broken}", file=sys.stderr)
        return CANNOT_RUN
    if seal.get("contract_version") != SEAL_CONTRACT:
        print(
            f"cannot run: {seal_path} declares {seal.get('contract_version')!r}; this reads "
            f"{SEAL_CONTRACT}",
            file=sys.stderr,
        )
        return CANNOT_RUN

    sealed = seal.get("objects") or {}
    problems: list[str] = []
    checked = 0
    for relative in sorted(sealed):
        path = root / relative
        if not path.is_file():
            problems.append(f"{relative}: the analysis wrote it and it is gone")
            continue
        checked += 1
        try:
            data, body = split(path)
        except ValueError as broken:
            problems.append(f"{relative}: {broken}")
            continue
        problems += compare(sealed[relative], data, body, relative)

    for path in sorted(root.rglob("*.md")):
        relative = path.relative_to(root).as_posix()
        if relative not in sealed:
            problems.append(
                f"{relative}: the seal does not name it. The enrichment writes into the objects it "
                f"was given and creates none"
            )

    print(f"enrichment checked: {checked} object(s) against the seal the analysis left")
    if problems:
        print(f"FAILED: {len(problems)} change(s) outside the enrichment's fields\n")
        for problem in problems:
            print(f"  {problem}")
        return 1
    print("every object differs only in the fields the enrichment owns")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
