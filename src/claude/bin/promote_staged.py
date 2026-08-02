#!/usr/bin/env python3
"""Move an enriched staged object into the knowledge base, validating before it writes.

The boundary between staging and the base is a contract change, not a directory change. A staged
object declares `staged-knowledge-object/1`, which does not require the retrieval question, the
summary, or the declared out-of-scope, because the pass that supplies them has not run. A knowledge
object requires all three. So promotion validates the file against the base's contract with its
version line substituted, and writes only where that passes.

That is a transformation rather than a repair. The staged file is *valid in its own contract*, and
this turns it into the next one — the same shape as a migration hop, and the reason an artifact
failing at a boundary is rejected does not reach it: nothing here is failing.

What it refuses is as important as what it moves. An object whose `kind: domain` gaps are still open
is refused unless the caller says otherwise, and the default is refusal: a gap the domain has not
closed is a fact the base would be asserting it has, and admitting it silently is how a list of gaps
becomes a list nobody reads. The caller can promote one anyway, and then the base holds an object
that says which fact it lacks — which the contract admits by name, and which is the whole reason an
object carries its gaps. Either way the decision is recorded rather than defaulted.

Declared dependencies: PyYAML, jsonschema.

Usage:  promote_staged.py <staging-root> <knowledge-root> [--with-open-domain-gaps]
Exit:   0 every object promoted, 1 one or more were refused, 2 cannot run
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
BASE_CONTRACT = "knowledge-object/4"
STAGED_CONTRACT = "staged-knowledge-object/1"
CANNOT_RUN = 2

try:
    import yaml
except ImportError:  # pragma: no cover - exercised by the environment, not the suite
    print("cannot run: PyYAML is not installed (pip install pyyaml)", file=sys.stderr)
    raise SystemExit(CANNOT_RUN)

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover
    print("cannot run: jsonschema is not installed (pip install jsonschema)", file=sys.stderr)
    raise SystemExit(CANNOT_RUN)


def split(text: str) -> tuple[dict, str]:
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not match:
        raise ValueError("carries no frontmatter fence")
    return yaml.safe_load(match.group(1)), match.group(2)


def promoted_text(text: str) -> str:
    """The same file with its contract line rewritten, and nothing else touched.

    Rewritten in the text rather than re-rendered from the parsed mapping. A round trip through YAML
    would reformat the whole file — reordering nothing but requoting and rewrapping enough that a
    reviewer reading the promotion diff would see the object rewritten rather than moved.
    """
    return text.replace(f"contract_version: {STAGED_CONTRACT}", f"contract_version: {BASE_CONTRACT}", 1)


def refusals(data: dict, validator: Draft202012Validator, relative: str, allow_gaps: bool) -> list[str]:
    """Why this object may not be promoted, or nothing."""
    problems = [
        f"{relative}: {error.message}"
        for error in sorted(validator.iter_errors(data), key=str)
    ]
    if not allow_gaps:
        for gap in data.get("gaps") or []:
            if gap.get("kind") == "domain":
                problems.append(
                    f"{relative}: the `kind: domain` gap on `{gap['field']}` is open — "
                    f"{gap.get('why', 'the domain has not stated it')}. Promote it anyway with "
                    f"--with-open-domain-gaps, which records the decision rather than defaulting it"
                )
    return problems


def main() -> int:
    arguments = [a for a in sys.argv[1:] if not a.startswith("--")]
    allow_gaps = "--with-open-domain-gaps" in sys.argv[1:]
    if len(arguments) != 2:
        print("cannot run: expected <staging-root> <knowledge-root>", file=sys.stderr)
        return CANNOT_RUN
    staging, knowledge = Path(arguments[0]), Path(arguments[1])
    if not staging.is_dir():
        print(f"cannot run: {staging} is not a directory", file=sys.stderr)
        return CANNOT_RUN

    contract = PLUGIN_ROOT / "schemas" / "knowledge-object.json"
    if not contract.is_file():
        print(f"cannot run: {contract} is missing", file=sys.stderr)
        return CANNOT_RUN
    validator = Draft202012Validator(json.loads(contract.read_text()))

    staged = sorted(staging.rglob("*.md"))
    if not staged:
        print(f"cannot run: {staging} holds no staged object", file=sys.stderr)
        return CANNOT_RUN

    problems: list[str] = []
    promotable: list[tuple[Path, Path, str]] = []
    for source in staged:
        relative = source.relative_to(staging).as_posix()
        try:
            text = promoted_text(source.read_text())
            data, _body = split(text)
        except ValueError as broken:
            problems.append(f"{relative}: {broken}")
            continue
        found = refusals(data, validator, relative, allow_gaps)
        if found:
            problems.extend(found)
            continue
        promotable.append((source, knowledge / relative, text))

    # Nothing is written while anything is refused. A partial promotion would leave a base holding
    # some of a run's objects and a staging tree holding the rest, with the edges between them
    # resolving to whichever half the reader looked at.
    if problems:
        print(f"staged objects checked: {len(staged)}  contract: {BASE_CONTRACT}")
        print(f"REFUSED: {len(problems)} problem(s), and nothing was promoted\n")
        for problem in problems:
            print(f"  {problem}")
        return 1

    for source, target, text in promotable:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
        source.unlink()
    for directory in sorted(staging.rglob("*"), reverse=True):
        if directory.is_dir() and not any(directory.iterdir()):
            directory.rmdir()

    print(f"promoted {len(promotable)} object(s) into {knowledge}  contract: {BASE_CONTRACT}")
    if allow_gaps:
        open_gaps = sum(
            1 for _s, target, _t in promotable
            for gap in (split(target.read_text())[0].get("gaps") or [])
            if gap.get("kind") == "domain"
        )
        if open_gaps:
            print(f"{open_gaps} open domain gap(s) were promoted by request: the base now records "
                  f"what it does not hold, and each names what the domain would have to state")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
