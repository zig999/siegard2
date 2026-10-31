#!/usr/bin/env python3
"""Render a handoff from its record, or hold a handoff already written to what is decidable.

«A handoff that hands a person a decision is rendered by `bin/handoff.py --render` from a record,
never composed as free text» (SPEC-006 R8). The record is `schemas/handoff.json`: the state in
one line, each decision with the door recommended — or what would settle a choice that is the
person's own — the other doors with their reply words, what stays if none is taken, the line ready
to paste, and the path of the full report on disk. The prose is the record's, in the language it
names; the rendering adds only the fixed words that language has under `x-labels`, so a person
never reads a label in a language they did not write in.

What the schema cannot express is decided here, from numbers and lists the schema holds: the
state within `x-ceilings.state` characters, each decision's block within `x-ceilings.block` with
its line ready to paste aside, the whole message within `x-ceilings.message`; no term of
`x-jargon` in any prose field; a reply word no other door in the handoff uses; a report path that
names a file. A record that fails any of them is refused with one line per failure, and nothing is
printed for the person to read.

`--check` reads a handoff already written as free text, where no record says what it holds, and
decides only what the text alone decides: no term of `x-jargon` in its first `x-ceilings.opening`
characters; and, where it hands a decision — `x-hands-a-decision` — a length within
`x-ceilings.message` and a word of `x-decision-words` within those first characters. Text inside a
code fence is a paste and is read for its length only. Whether the prose is in the person's
language is not decidable from the text and is not checked. `telemetry.py` imports `reading` and
`violations` from here, so a handoff is measured by the same definition it is held to.

Declared dependencies: jsonschema.

Usage:  handoff.py --render <record.json>    render the record, or refuse it
        handoff.py --render -                render the record read from standard input
        handoff.py --check <message-file>    hold a written handoff to what is decidable
        handoff.py --check -                 hold the handoff read from standard input
        handoff.py --help                    print this text and stop
Exit:   0 rendered: the message on standard output; or checked: nothing found
        1 the record is refused, or the handoff does not hold: one problem per line
        2 cannot run
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

CANNOT_RUN = 2
CONTRACT = Path(__file__).resolve().parent.parent / "schemas" / "handoff.json"
FENCE = re.compile(r"^[ \t]*```.*?^[ \t]*```[^\n]*$", re.S | re.M)
INVOCATION = re.compile(r"^[ \t]*`?/[a-z][\w:-]*(?:[ \t`]|$)", re.M)
CLOSING = (".", "!", "?", ":", "…")


def load_contract(path: Path = CONTRACT) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def prose_of(text: str) -> str:
    """The text a person reads as prose: every fenced code block removed, the paste it holds
    being the one place a command or a skill's name belongs."""
    return FENCE.sub("", text)


def asks(text: str) -> bool:
    """Whether a message closes on a question: its final paragraph holds one."""
    return "?" in text.strip().rsplit("\n\n", 1)[-1]


def jargon_in(text: str, contract: dict) -> list[tuple[str, str]]:
    """Every term or pattern of `x-jargon` the text carries, in order of first appearance, each
    as its name in the list and the words it matched."""
    listed = contract["x-jargon"]
    found: list[tuple[int, str, str]] = []
    for term in listed["terms"]:
        hit = re.search(r"(?<![\w-])" + re.escape(term) + r"(?![\w-])", text, re.I)
        if hit:
            found.append((hit.start(), term, hit.group(0)))
    for name, pattern in listed["patterns"].items():
        hit = re.search(pattern, text)
        if hit:
            found.append((hit.start(), name, hit.group(0)))
    return [(name, matched) for _, name, matched in sorted(found)]


def decision_word_at(text: str, contract: dict, kinds: tuple[str, ...] = ("recommendation", "own")
                     ) -> int | None:
    """Where the first word of `x-decision-words` of the kinds named begins, or None."""
    stems = [stem for kind in kinds for stem in contract["x-decision-words"][kind]]
    hit = re.search(r"(?<!\w)(?:" + "|".join(re.escape(s) for s in stems) + ")", text, re.I)
    return hit.start() if hit else None


def hands_a_decision(text: str, contract: dict) -> bool:
    prose = prose_of(text)
    return asks(prose) or bool(INVOCATION.search(prose)) \
        or decision_word_at(prose, contract) is not None


def reading(text: str, contract: dict) -> dict:
    """What a handoff's text decides, as counts and names and none of its words: its length,
    whether it hands a decision, the list's terms in its opening, whether it carries a word of
    recommendation, and where its first decision word sits as a share of its prose."""
    prose = prose_of(text)
    opening = contract["x-ceilings"]["opening"]
    first = decision_word_at(prose, contract)
    return {
        "characters": len(text),
        "hands_decision": hands_a_decision(text, contract),
        "jargon_in_opening": [name for name, _ in jargon_in(prose[:opening], contract)],
        "recommendation_word": decision_word_at(prose, contract, ("recommendation",)) is not None,
        "decision_word_at": first,
        "decision_word_share": round(first / len(prose), 3) if first is not None and prose else None,
    }


def violations(read: dict, contract: dict) -> list[str]:
    """One line per way a reading fails what `--check` decides."""
    ceilings = contract["x-ceilings"]
    problems = []
    if read["jargon_in_opening"]:
        problems.append(f"opening: the first {ceilings['opening']} characters carry "
                        + ", ".join(read["jargon_in_opening"])
                        + " — words of this framework a person never reads there")
    if read["hands_decision"]:
        if read["characters"] > ceilings["message"]:
            problems.append(f"length: {read['characters']} characters, over the ceiling of "
                            f"{ceilings['message']} for a handoff that hands a decision; the "
                            f"rest belongs in the report on disk")
        at = read["decision_word_at"]
        if at is None or at >= ceilings["opening"]:
            problems.append(f"decision: hands a decision and carries no word of recommendation or "
                            f"of the person's own decision in its first {ceilings['opening']} "
                            f"characters" + (f" (the first is at character {at})"
                                             if at is not None else ""))
    return problems


def sentence(text: str) -> str:
    text = text.strip()
    return text if text.endswith(CLOSING) else text + "."


def block_of(number: int, decision: dict, labels: dict) -> tuple[str, str | None]:
    """One decision's block as the person reads it, and its line ready to paste apart."""
    lines = [f"{number}. {decision['ask']}"]
    chosen = decision.get("recommended")
    if chosen:
        lines.append(f"   - **{labels['recommended']}** `{chosen['reply_word']}`: "
                     f"{sentence(chosen['door'])} {sentence(chosen['why'])} "
                     f"{labels['reverses_if']} {sentence(chosen['reverses_if'])}")
    else:
        lines.append(f"   - **{labels['own']}**: {sentence(decision['settles'])}")
    for door in decision["others"]:
        lines.append(f"   - `{door['reply_word']}`: {sentence(door['what_it_does'])}")
    lines.append(f"   - {labels['if_none']}: {sentence(decision['if_none'])}")
    return "\n".join(lines), decision.get("invocation")


def prose_fields(record: dict) -> list[tuple[str, str]]:
    """Every field of the record a person reads as prose, by where it sits; the line ready to
    paste and the report's path are not prose."""
    fields = [("state", record["state"])]
    if "withdraws" in record:
        fields.append(("withdraws", record["withdraws"]))
    for at, decision in enumerate(record.get("decisions", [])):
        where = f"decisions/{at}"
        fields.append((f"{where}/ask", decision["ask"]))
        if "recommended" in decision:
            for key in ("door", "why", "reverses_if"):
                fields.append((f"{where}/recommended/{key}", decision["recommended"][key]))
        if "settles" in decision:
            fields.append((f"{where}/settles", decision["settles"]))
        for other, door in enumerate(decision["others"]):
            fields.append((f"{where}/others/{other}/what_it_does", door["what_it_does"]))
        fields.append((f"{where}/if_none", decision["if_none"]))
    return fields


def render(record: object, contract: dict, base: Path) -> tuple[str | None, list[str]]:
    """The message the record renders to, or None and the problems that refuse it."""
    problems = []
    for error in sorted(Draft202012Validator(contract).iter_errors(record), key=str):
        where = "/".join(str(part) for part in error.absolute_path) or "(record)"
        problems.append(f"{where}: {error.message}")
    if problems:
        return None, problems
    ceilings = contract["x-ceilings"]
    labels = contract["x-labels"][record["language"]]
    if len(record["state"]) > ceilings["state"]:
        problems.append(f"state: {len(record['state'])} characters, over the ceiling of "
                        f"{ceilings['state']}")
    for where, text in prose_fields(record):
        for name, matched in jargon_in(text, contract):
            problems.append(f"{where}: carries {name} ({matched!r}), a word of this framework a "
                            f"person never reads in a handoff")
    seen: dict[str, str] = {}
    for at, decision in enumerate(record.get("decisions", [])):
        doors = ([decision["recommended"]] if "recommended" in decision else []) + decision["others"]
        for door in doors:
            word = door["reply_word"].casefold()
            if word in seen:
                problems.append(f"decisions/{at}: reply word {door['reply_word']!r} already names "
                                f"a door in {seen[word]}; one reply names one door")
            seen.setdefault(word, f"decisions/{at}")
    if "report" in record:
        path = Path(record["report"])
        if not (path if path.is_absolute() else base / path).is_file():
            problems.append(f"report: {record['report']} names no file; the full report is "
                            f"written before the handoff that points at it")
    parts = [record["state"]]
    if "withdraws" in record:
        parts.append(record["withdraws"])
    for number, decision in enumerate(record.get("decisions", []), 1):
        block, invocation = block_of(number, decision, labels)
        if len(block) > ceilings["block"]:
            problems.append(f"decisions/{number - 1}: its block renders to {len(block)} "
                            f"characters, over the ceiling of {ceilings['block']}")
        parts.append(block + (f"\n\n   ```\n   {invocation}\n   ```" if invocation else ""))
    if "body" in record:
        parts.append(record["body"])
    if "report" in record:
        parts.append(f"{labels['report']}: {record['report']}")
    message = "\n\n".join(parts) + "\n"
    if record["kind"] == "decision":
        read = dict(reading(message, contract), jargon_in_opening=[])
        problems.extend(violations(read, contract))
    if problems:
        return None, problems
    return message, []


def main() -> int:
    args = sys.argv[1:]
    if "--help" in args:
        print(__doc__.strip())
        return 0
    if len(args) != 2 or args[0] not in ("--render", "--check"):
        print("cannot run: expected --render <record.json|-> or --check <message-file|->",
              file=sys.stderr)
        return CANNOT_RUN
    try:
        contract = load_contract()
    except (OSError, json.JSONDecodeError) as broken:
        print(f"cannot run: {CONTRACT} is unreadable: {broken}", file=sys.stderr)
        return CANNOT_RUN
    try:
        text = sys.stdin.read() if args[1] == "-" else Path(args[1]).read_text(encoding="utf-8")
    except OSError as broken:
        print(f"cannot run: {broken}", file=sys.stderr)
        return CANNOT_RUN
    if args[0] == "--check":
        problems = violations(reading(text, contract), contract)
        for problem in problems:
            print(problem)
        return 1 if problems else 0
    try:
        record = json.loads(text)
    except json.JSONDecodeError as broken:
        print(f"cannot run: the record is not JSON: {broken}", file=sys.stderr)
        return CANNOT_RUN
    message, problems = render(record, contract, Path.cwd())
    for problem in problems:
        print(problem)
    if problems:
        return 1
    print(message, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
