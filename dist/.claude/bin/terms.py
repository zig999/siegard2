#!/usr/bin/env python3
"""Print what this framework's terms mean, straight from the contracts that define them.

Every term below is already defined, once, in a schema this framework ships — almost always in the
`description` of the field that carries it. The problem this solves is not that the definitions are
missing; it is that they sit in files only an agent opens, while the same words come back at a human
in the validators' refusals: `a bound node passed over in silence`, `base pin ... is not the base as
it stands`, `a covered node reaches a task or a stated why`. Three terms in one line, each defined in
a schema nobody reading that line has open.

**This script holds pointers, never text.** A term maps to a file and a JSON pointer, and what gets
printed is read out of the schema at that pointer. Nothing here paraphrases a definition, and there is
no copy to drift: a schema whose wording changes changes this output in the same commit, because the
output was never anywhere else. That is the same rule `graph.py --gaps` follows — report from the
source, never maintain a second answer beside it.

**A pointer that stops resolving is a refusal, not a stale entry.** Move a definition and this exits
2 naming the term and the pointer that broke. A glossary that silently omitted the term it could no
longer find would be worse than no glossary: it would read as complete.

**What has no definition is named, not omitted.** A word this framework uses normatively and defines
nowhere is listed under `no definition holds these`, with what it collides with. That list is a gap in
the sense the base uses the word — an absence declared where a reader will look for it, rather than an
absence a reader discovers. Closing an entry means writing the definition into a contract and moving
the term into the table above it; it does not mean writing a definition here.

**One term, one entry, even where the word has two senses.** Where a word means two different things
in two roots — `covers` over base nodes and `covers` over a criterion, `base` the knowledge root and
`base` the pin field — each sense is its own row, named apart. A single row for a word with two
meanings is the collision left in place with a definition on top of it.

Declared dependencies: none beyond the standard library.

Usage:  terms.py                 every term, alphabetically
        terms.py <term> [...]    only the terms named
Exit:   0 printed
        1 a term was named that no contract defines
        2 cannot run
"""

from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path

SCHEMAS = Path(__file__).resolve().parent.parent / "schemas"

# term -> (schema file, JSON pointer to the object whose `description` is the definition). The
# empty pointer is the schema itself, whose own description defines what one of its nodes is.
# Never a definition. Add a term by pointing at where a contract already states it; where no
# contract states it, the term belongs in OPEN below until one does.
TERMS: dict[str, tuple[str, str]] = {
    "base (the pin on a task)": ("plan-node.json", "/properties/base"),
    "base node": ("node.json", ""),
    "binding": ("plan-node.json", "/properties/nodes"),
    "cause": ("delivery-node.json", "/$defs/finding/properties/cause"),
    "covers (an epic over base nodes)": ("plan-node.json", "/properties/covers"),
    "covers (a test over a criterion)":
        ("delivery-node.json", "/$defs/coverageEntry/properties/state"),
    "criteria": ("plan-node.json", "/properties/criteria"),
    "ddd": ("node.json", "/properties/ddd"),
    "decided_by": ("standard.json", "/$defs/rule/properties/decided_by"),
    "delivery node": ("delivery-node.json", ""),
    "delivery.json": ("delivery.json", ""),
    "gap": ("node.json", "/properties/gaps"),
    "gap.field": ("node.json", "/$defs/gap/properties/field"),
    "graph.json": ("graph.json", ""),
    "objective": ("plan-node.json", "/properties/objective"),
    "pin": ("plan-node.json", "/$defs/pin"),
    "plan node": ("plan-node.json", ""),
    "plan.json": ("plan.json", ""),
    "run.json": ("run.json", ""),
    "slug": ("node.json", "/$defs/slug"),
    "standard": ("standard.json", ""),
    "uncovered": ("plan-node.json", "/properties/uncovered"),
    "unresolved": ("plan-node.json", "/properties/unresolved"),
    "waived": ("plan-node.json", "/properties/waived"),
}

# Words this framework uses normatively and no contract defines. The note says where the word is
# used and what it collides with — never what it means, because a meaning stated here would be the
# second home this script exists to avoid.
OPEN: dict[str, str] = {
    "base (the knowledge root)": "the root the analysis writes into and every plan binds to, defined "
                                 "as an input in each skill's required inputs and in CLAUDE.md's "
                                 "`What the base is`, and by no contract. The same word is a task's "
                                 "pin field, which a contract does define — see `base (the pin on a "
                                 "task)` above; one paragraph of skills/plan-work/SKILL.md uses both "
                                 "senses.",
    "bound": "used of a base node a task's `nodes` names, in the validators' refusals and in every "
             "skill; inferable only from `binding`, and never stated.",
    "construct": "four unrelated senses, none defined: the DDD construct (`ddd`), an implementation "
                 "shape the base admits (which decides a `blocking` note in "
                 "agents/execution-contract-binder.md), a syntactic thing at a location in a file "
                 "(a finding's `where`, a standard's forbidden construct), and the idiom `by "
                 "construction`. The load-bearing one is the second: no contract states it, and a "
                 "note's class turns on it.",
    "impact set": "defined twice and differently — mechanically in skills/analyse-domain/SKILL.md "
                  "and loosely in agents/backlog-decomposer.md — and no contract holds either.",
    "proof": "one of the three delivery kinds, with a path and a required-field branch; what a "
             "proof node is is stated nowhere.",
    "record": "the most-used term in the framework after `node` and `root`; no contract defines it, "
              "and run.py uses the same word for a run's outcome, which is explicitly not a record.",
    "root (the DDD aggregate root)": "a value of the `ddd` vocabulary and the subject of a "
                                     "cross-node refusal in graph.py; the enum lists it and nothing "
                                     "says what it is. Distinct from a knowledge, work or delivery "
                                     "root, which are inputs the skills define.",
}

WIDTH = 96


def resolve(pointer: str, document: object, term: str, relative: str) -> object:
    """The object a JSON pointer names, or a refusal naming the term whose pointer broke."""
    current = document
    for raw in pointer.split("/")[1:]:
        key = raw.replace("~1", "/").replace("~0", "~")
        if not isinstance(current, dict) or key not in current:
            die(f"{term}: {relative}{pointer} does not resolve; the definition moved, and a "
                f"glossary that skipped it would read as complete")
        current = current[key]
    return current


def die(message: str) -> None:
    print(f"cannot run: {message}", file=sys.stderr)
    raise SystemExit(2)


def load(relative: str) -> object:
    path = SCHEMAS / relative
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError:
        die(f"{path} cannot be read; the contracts sit beside this script under schemas/")
    except json.JSONDecodeError as broken:
        die(f"{path} does not parse: {broken}")


def definition(term: str) -> str:
    relative, pointer = TERMS[term]
    target = resolve(pointer, load(relative), term, relative)
    if not isinstance(target, dict) or not isinstance(target.get("description"), str):
        die(f"{term}: {relative}{pointer} carries no description; the definition this term "
            f"pointed at is gone")
    return target["description"]


def emit(term: str) -> None:
    """Resolved before anything is printed: a header above a refusal reads as a term that answered."""
    relative, pointer = TERMS[term]
    text = definition(term)
    print(f"{term}  [{relative}{pointer}/description]")
    for line in textwrap.wrap(text, width=WIDTH - 4, break_on_hyphens=False, break_long_words=False):
        print(f"    {line}")
    print()


def main(argv: list[str]) -> int:
    if argv:
        unknown = [t for t in argv if t not in TERMS]
        if unknown:
            print(f"no contract defines {', '.join(unknown)}", file=sys.stderr)
            if any(t in OPEN for t in unknown):
                print("named below as holding no definition; see the full listing.",
                      file=sys.stderr)
            return 1
        for term in argv:
            emit(term)
        return 0

    for term in sorted(TERMS):
        emit(term)

    print("no definition holds these:")
    print()
    for term in sorted(OPEN):
        print(f"{term}")
        for line in textwrap.wrap(OPEN[term], width=WIDTH - 4, break_on_hyphens=False,
                                 break_long_words=False):
            print(f"    {line}")
        print()
    print(f"{len(TERMS)} term(s) defined by a contract, {len(OPEN)} named as holding no definition.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
