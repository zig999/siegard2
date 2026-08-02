#!/usr/bin/env python3
"""Record what the analysis wrote, so the pass that comes next can be held to its own fields.

The enrichment writes four fields and a body into an object and must change nothing else. A tool
grant cannot express that — a grant names tools, not files, and certainly not keys within a file —
so the restriction is prose until something compares the object against what it looked like before.

**Why a record and not a re-derivation.** While a deterministic script wrote the objects, "before"
was recoverable at any time by running that script again: the same input yielded the same bytes, and
nothing had to be kept. A producer that writes by judgment offers no such function. So `before` is
recorded once, immediately, and by something other than the producer — a guarantee a producer
self-reports is not a guarantee, and a seal the analysis wrote about itself would be one.

It writes and never verifies. `check_enrichment.py` is what compares, and the two are separate
commands on purpose: a check that could also refresh the baseline it compares against would report
success on the very change it exists to catch.

What is sealed is the analysis's side of the line `field_ownership` declares, and nothing else. The
four fields the enrichment owns are absent by construction — sealing them would record a value
nobody had written and report every legitimate enrichment as a change.

Declared dependencies: PyYAML.

Usage:  seal_analysis.py <root> <seal.json>
Exit:   0 the seal was written, 1 the tree could not be read, 2 cannot run
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from field_ownership import SHARED_FIELD, closable, digest, expansion_owns

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
        raise ValueError("carries no frontmatter fence")
    return yaml.safe_load(match.group(1)) or {}, match.group(2)


def seal_of(data: dict, body: str) -> dict:
    """One object's side of the line: a digest per owned field, its domain gaps, its headings."""
    return {
        "fields": {
            field: digest(value) for field, value in sorted(data.items()) if expansion_owns(field)
        },
        # Verbatim, because a removed gap is reported by the field it named and a digest names
        # nothing a reader can open.
        "domain_gaps": [gap for gap in data.get(SHARED_FIELD) or [] if not closable(gap)],
        "headings": HEADING.findall(body),
    }


def main() -> int:
    if len(sys.argv) != 3:
        print("cannot run: expected <root> <seal.json>", file=sys.stderr)
        return CANNOT_RUN
    root, destination = Path(sys.argv[1]), Path(sys.argv[2])
    if not root.is_dir():
        print(f"cannot run: {root} is not a directory", file=sys.stderr)
        return CANNOT_RUN

    objects = sorted(root.rglob("*.md"))
    if not objects:
        print(f"cannot run: {root} holds no object to seal", file=sys.stderr)
        return CANNOT_RUN

    sealed: dict[str, dict] = {}
    problems: list[str] = []
    for path in objects:
        relative = path.relative_to(root).as_posix()
        try:
            data, body = split(path)
        except ValueError as broken:
            problems.append(f"{relative}: {broken}")
            continue
        sealed[relative] = seal_of(data, body)

    if problems:
        print(f"FAILED: {len(problems)} object(s) could not be read\n")
        for problem in problems:
            print(f"  {problem}")
        return 1

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(
            {
                "contract_version": SEAL_CONTRACT,
                "producer": "seal-analysis",
                "consumer": "check-enrichment",
                "objects": sealed,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n"
    )
    fields = sum(len(entry["fields"]) for entry in sealed.values())
    print(f"sealed {len(sealed)} object(s), {fields} field(s), into {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
