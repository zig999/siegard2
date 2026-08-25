#!/usr/bin/env python3
"""Print what this framework's terms mean, straight from the contracts that define them.

Every term below is already defined, once, in a schema this framework ships — almost always in the
`description` of the field that carries it. The problem this solves is not that the definitions are
missing; it is that they sit in files only an agent opens, while the same words come back at a human
in the validators' refusals: `a bound node passed over in silence`, `is pinned at ... and stands at
...`, `a covered node reaches a task or a stated why`. Three terms in one line, each defined in a
schema nobody reading that line has open.

**This script holds pointers, never text.** A term maps to a file and a JSON pointer, and what gets
printed is read out of the schema at that pointer. Nothing here paraphrases a definition, and there is
no copy to drift: a schema whose wording changes changes this output in the same commit, because the
output was never anywhere else. That is the same rule `spec.py --digest` follows — report from the
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
in two places — `covers` over specification nodes and `covers` over a criterion — each sense is
its own row, named apart. A single row for a word with two meanings is the collision left in
place with a definition on top of it.

Declared dependencies: none beyond the standard library.

Usage:  terms.py                 every term, alphabetically
        terms.py <term> [...]    only the terms named
        terms.py --help          print this text and stop
Exit:   0 printed
        1 a term was named that no contract defines
        2 cannot run
"""

from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path
from typing import NoReturn

SCHEMAS = Path(__file__).resolve().parent.parent / "schemas"

# term -> (schema file, JSON pointer to the object whose `description` is the definition). The
# empty pointer is the schema itself, whose own description defines what one of its nodes is.
# Never a definition. Add a term by pointing at where a contract already states it; where no
# contract states it, the term belongs in OPEN below until one does.
TERMS: dict[str, tuple[str, str]] = {
    "cause": ("delivery-node.json", "/$defs/finding/properties/cause"),
    "covers (an epic over specification nodes)": ("plan-node.json", "/properties/covers"),
    "covers (a test over a criterion)":
        ("delivery-node.json", "/$defs/coverageEntry/properties/state"),
    "criteria": ("plan-node.json", "/properties/criteria"),
    "decided_by": ("standard.json", "/$defs/rule/properties/decided_by"),
    "delivery node": ("delivery-node.json", ""),
    "digest (on a trace binding)": ("trace.json", "/$defs/binding/properties/digest"),
    "delivery.json": ("delivery.json", ""),
    "implements": ("plan-node.json", "/properties/implements"),
    "objective": ("plan-node.json", "/properties/objective"),
    "pin": ("delivery-node.json", "/$defs/pin"),
    "plan node": ("plan-node.json", ""),
    "plan.json": ("plan.json", ""),
    "run.json": ("run.json", ""),
    "slug": ("plan-node.json", "/$defs/slug"),
    "specification node": ("plan-node.json", "/$defs/specNodeRef"),
    "standard": ("standard.json", ""),
    "telemetry report": ("telemetry.json", ""),
    "trace.json": ("trace.json", ""),
    "uncovered": ("plan-node.json", "/properties/uncovered"),
}

# Words this framework uses normatively and no contract defines. The note says where the word is
# used and what it collides with — never what it means, because a meaning stated here would be the
# second home this script exists to avoid.
OPEN: dict[str, str] = {
    "specification (the specification root)": "the root the analysis writes into and every plan "
                                 "implements against, defined as an input in each skill's required "
                                 "inputs and in CLAUDE.md's `What the specification is`, and by no "
                                 "contract. It collides with nothing: a task names a node it "
                                 "implements by identity alone, with no pin of any kind.",
    "bound": "used of the judgment execution-contract-binder returns, in the validators' refusals "
             "and in every skill; inferable only from the agent's own name, and never stated by a "
             "contract.",
    "construct": "four unrelated senses, none defined: the type of a Domain Model element (`type` "
                 "in schemas/spec/element.json), an implementation shape the specification admits "
                 "(which decides an `underdetermined` note in agents/execution-contract-binder.md), "
                 "a syntactic thing at a location in a file (a finding's `where`, a standard's "
                 "forbidden construct), and the idiom `by construction`. The load-bearing one is "
                 "the second: no contract states it, and a note's class turns on it.",
    "impact set": "defined three times and differently — in skills/analyse/SKILL.md, in "
                  "skills/plan-work/SKILL.md, and loosely in agents/backlog-decomposer.md — and no "
                  "contract holds any of them.",
    "proof": "one of the three delivery kinds, with a path and a required-field branch; what a "
             "proof node is is stated nowhere.",
    "record": "the most-used term in the framework after `node` and `root`; no contract defines it, "
              "and run.py uses the same word for a run's outcome, which is explicitly not a record.",
    "root (the aggregate root)": "a value of `type` on a Domain Model element "
                                 "(schemas/spec/element.json) and the subject of a cross-node "
                                 "refusal in spec.py (\"an aggregate root has one state machine\"); "
                                 "the enum lists it and nothing says what it is. Distinct from a "
                                 "specification, work or delivery root, which are inputs the "
                                 "skills define.",
}

WIDTH = 96


def resolve(pointer: str, document: object, term: str, relative: str) -> object:
    """The object a JSON pointer names, or a refusal naming the term whose pointer broke."""
    if pointer and not pointer.startswith("/"):
        # A pointer is rooted or it is empty (RFC 6901). Splitting an unrooted one drops its
        # first token, which resolves the wrong place and says nothing about it.
        die(f"{term}: {relative}{pointer} is not a JSON pointer; a pointer names its path from "
            f"the root and begins with '/'")
    current = document
    for raw in pointer.split("/")[1:]:
        key = raw.replace("~1", "/").replace("~0", "~")
        if not isinstance(current, dict) or key not in current:
            die(f"{term}: {relative}{pointer} does not resolve; the definition moved, and a "
                f"glossary that skipped it would read as complete")
        current = current[key]
    return current


def die(message: str) -> NoReturn:
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
    if "--help" in argv:
        # The docstring is this script's one home of what it does and how it is called,
        # so `--help` prints that rather than a second copy of it that could drift.
        print(__doc__.strip())
        return 0
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
