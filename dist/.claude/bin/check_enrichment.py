#!/usr/bin/env python3
"""Hold the enrichment pass to the fields it owns, by re-deriving what the expansion wrote.

The enrichment writes four fields and a body into a staged object and must change nothing else. A
tool grant cannot express that: a grant names tools, not files, and certainly not keys within a
file, so the restriction is prose until something checks it. This is that something, and it is why
the check exists before the pass it checks rather than after.

The method is re-derivation rather than a stored copy. Given the model the tree was expanded from,
the expansion is a function — the same input yields the same frontmatter every run — so what the
expansion wrote is recoverable at any time by running it again into a temporary tree and comparing.
A recorded baseline would be a second artifact to keep in step; a function needs nothing kept.

What it reports, per object: a field on the expansion's side that differs, a `kind: domain` gap that
was removed, and a body heading that was added or renamed. What it does not report is the four
fields and the body content, which are the enrichment's to write.

Declared dependencies: PyYAML.

Usage:  check_enrichment.py <model.json> <staging-root> <intake-id> <generated-by> <generated-at>
Exit:   0 the enrichment stayed inside its fields, 1 it did not, 2 cannot run
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from field_ownership import ENRICHMENT_FIELDS, SHARED_FIELD, closable, expansion_owns

HERE = Path(__file__).resolve().parent
CANNOT_RUN = 2
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
    return yaml.safe_load(match.group(1)), match.group(2)


def compare(expected: Path, actual: Path, relative: str) -> list[str]:
    """Every difference the enrichment was not permitted to make, in one object."""
    problems: list[str] = []
    before, before_body = split(expected)
    after, after_body = split(actual)

    for field in sorted(set(before) | set(after)):
        if not expansion_owns(field):
            continue
        if before.get(field) != after.get(field):
            problems.append(
                f"{relative}: `{field}` differs from what the expansion wrote. The enrichment "
                f"writes {', '.join(ENRICHMENT_FIELDS)} and the body, and reports a disagreement "
                f"with anything else as a finding rather than editing it"
            )

    kept = {json.dumps(gap, sort_keys=True) for gap in after.get(SHARED_FIELD) or []}
    for gap in before.get(SHARED_FIELD) or []:
        if closable(gap):
            continue
        if json.dumps(gap, sort_keys=True) not in kept:
            problems.append(
                f"{relative}: the `kind: domain` gap on `{gap['field']}` was removed. Only whoever "
                f"knows the domain closes one, and no pass of this pipeline may"
            )

    for gap in after.get(SHARED_FIELD) or []:
        if closable(gap) and gap.get("field") in ENRICHMENT_FIELDS and after.get(gap["field"]):
            problems.append(
                f"{relative}: `{gap['field']}` is written and its `authoring` gap is still open — "
                f"closing the gap is what records that the field was filled"
            )

    if HEADING.findall(before_body) != HEADING.findall(after_body):
        problems.append(
            f"{relative}: the body headings changed. The expansion places the two its node type "
            f"requires and the enrichment fills them; a third heading is one the contract refuses"
        )
    return problems


def main() -> int:
    if len(sys.argv) != 6:
        print("cannot run: expected <model.json> <staging-root> <intake-id> <by> <at>",
              file=sys.stderr)
        return CANNOT_RUN
    model, staging, intake_id, by, at = sys.argv[1:]
    root = Path(staging)
    if not Path(model).is_file() or not root.is_dir():
        print(f"cannot run: {model} or {staging} does not exist", file=sys.stderr)
        return CANNOT_RUN

    with tempfile.TemporaryDirectory() as holder:
        reference = Path(holder) / "expected"
        expansion = subprocess.run(
            [sys.executable, "-B", str(HERE / "expand_model.py"), model, str(reference),
             intake_id, by, at],
            capture_output=True, text=True,
        )
        if expansion.returncode != 0:
            print(f"cannot run: the expansion this compares against failed — {expansion.stderr}",
                  file=sys.stderr)
            return CANNOT_RUN

        problems: list[str] = []
        checked = 0
        for expected in sorted(reference.rglob("*.md")):
            relative = expected.relative_to(reference).as_posix()
            actual = root / relative
            if not actual.is_file():
                problems.append(f"{relative}: the expansion wrote it and it is gone")
                continue
            checked += 1
            problems += compare(expected, actual, relative)
        for actual in sorted(root.rglob("*.md")):
            relative = actual.relative_to(root).as_posix()
            if not (reference / relative).is_file():
                problems.append(
                    f"{relative}: nothing in the model expands to it. The enrichment writes into "
                    f"the objects it was given and creates none"
                )

    print(f"enrichment checked: {checked} object(s) against a re-derived expansion")
    if problems:
        print(f"FAILED: {len(problems)} change(s) outside the enrichment's fields\n")
        for problem in problems:
            print(f"  {problem}")
        return 1
    print("every object differs only in the fields the enrichment owns")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
