#!/usr/bin/env python3
"""Reject a foundation document that claims a tree is empty while it is not.

Six specifications drifted the same way. Each opened its **Provenance** with an existence claim
about this repository — "No hook exists", "No generator exists", "No pack exists, and no fixture
exercises one" — and each stayed said after the thing was built. Every individual document still
validated, because nothing compares prose against the filesystem, and a reader who trusted the
paragraph got a false picture of what binds and what is owed.

That is the failure this script exists to catch, and the shape of the catch matters. A general
prose-contradiction checker is not decidable, so this does not attempt one. What it decides is
narrow and total: a small closed set of *phrases that assert emptiness*, each paired with a
predicate over a path the repository holds. A document may say a tree is empty only while it is.

The direction is deliberate. Claiming emptiness while something exists is the drift that happened
and is reported. Claiming existence while nothing exists is not checked here: a specification
naming a mechanism it needs is how a requirement is written before the mechanism arrives, and
`foundation/0007` R1 is the standing example.

Adding a subject is adding a row. Where a document needs to say something about this repository
that no row covers, the answer is usually that the statement belongs in **Outstanding evidence**
per requirement rather than in a Provenance summary — which is what the six corrections did.

Declared dependencies: none beyond the standard library.

Usage:  scripts/check_existence_claims.py [ROOT]   (default: foundation/)
Exit:   0 every claim holds, 1 a claim is contradicted, 2 cannot run
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from cli import cannot_run

REPO_ROOT = Path(__file__).resolve().parent.parent


def nonempty(*patterns: str):
    """A predicate that is true when any pattern matches at least one file."""

    def present() -> list[str]:
        found: list[str] = []
        for pattern in patterns:
            found.extend(
                str(p.relative_to(REPO_ROOT)) for p in sorted(REPO_ROOT.glob(pattern)) if p.is_file()
            )
        return found

    return present


# Each subject pairs the phrases that assert its emptiness with what would contradict them. A
# phrase is matched case-insensitively against the whole document, so a claim moved out of
# Provenance is still caught.
SUBJECTS: dict[str, dict] = {
    "generator": {
        "phrases": ["no generator exists", "no generator has been built"],
        "evidence": nonempty("scripts/generate_dist.py"),
    },
    # Four subjects were dropped rather than kept unsatisfiable, and the same sentence covers all
    # four: a subject whose evidence path can never be satisfied is a branch that reports nothing
    # while looking like a check.
    #
    # `template` and `pack` went when `fixtures/` did — both looked under `fixtures/pack-*/`. Then
    # `context resolution` went with `src/claude/bin/resolve_context.py`, removed with the
    # generation path, and `hook` went with `src/claude/hooks/`, which held no hook and was
    # removed under `foundation/0005` R2. Each claim they guarded — "no template exists", "no pack
    # exists", "context resolution does not exist", "no hook exists" — is true today, so the guard
    # has nothing to catch.
    #
    # Each returns with the artifact that makes its claim falsifiable again: the first template or
    # pack that ships from `src/claude/`, the first context resolver, the first hook.
    "capability declaration": {
        "phrases": ["no declaration format is enforced anywhere today"],
        "evidence": nonempty("schemas/capability-declaration.json"),
    },
}


def problems_for(path: Path, text: str) -> list[str]:
    lowered = text.lower()
    try:
        rel = path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        # A caller checking a copy outside the repository — a test does exactly this.
        rel = path.as_posix()
    found: list[str] = []
    for subject, spec in SUBJECTS.items():
        for phrase in spec["phrases"]:
            index = lowered.find(phrase)
            if index < 0:
                continue
            evidence = spec["evidence"]()
            if not evidence:
                continue
            line = text[:index].count("\n") + 1
            shown = ", ".join(evidence[:3]) + (" …" if len(evidence) > 3 else "")
            found.append(
                f"{rel}:{line}: claims {subject!r} is absent — {phrase!r} — while the repository "
                f"holds {shown}. State what is unexercised per requirement in Outstanding "
                f"evidence rather than as an existence claim that goes stale."
            )
    return found


def main() -> int:
    args = sys.argv[1:]
    if len(args) > 1:
        cannot_run(f"cannot run: unexpected arguments {args}; usage: check_existence_claims.py [ROOT]")
    root = Path(args[0]) if args else REPO_ROOT / "foundation"
    if not root.is_dir():
        cannot_run(f"cannot run: {root} does not exist")

    documents = sorted(p for p in root.glob("*.md"))
    if not documents:
        cannot_run(f"cannot run: {root} holds no document to check")

    problems: list[str] = []
    for path in documents:
        problems.extend(problems_for(path, path.read_text()))

    print(
        f"existence claims checked: {len(documents)} document(s), {len(SUBJECTS)} subject(s)  "
        f"root: {root.relative_to(REPO_ROOT).as_posix()}"
    )
    if problems:
        print(f"FAILED: {len(problems)} problem(s)\n")
        for problem in problems:
            print(f"  {problem}")
        return 1
    print("no document claims a tree is empty while it is not")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
