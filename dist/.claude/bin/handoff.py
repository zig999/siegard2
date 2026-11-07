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
`x-jargon` in any prose field — a `body` above a `report` path read whole, as the short form it
is, and a body with no path read over its opening span; a body that recommends carrying the
words `x-labels` opens the reversing fact with; a reply word no other door in the handoff uses; a
report path that names a file. A record that fails any of them is refused with one line per
failure, and nothing is printed for the person to read.

**`--prepare` writes what the session must not.** «The state a handoff opens with is a script's
line, never the session's» (SPEC-006 R10). It prints the record's skeleton as JSON: `state`
already written, and `state_from` naming where it was read — the first line of `goal.py --state`
over the goal armed through the framework (`siegard/goal.json` under the repository's git common
directory), else the segment `progress.py` prints for the initiative named, else the line it
prints for the project, else the fixed words `x-labels` holds for a project with nothing live.
Given `--ledger`, a material ledger the skill answered, the count of the lines it leaves open
leads that line under `x-labels`' `open_lines` — «the count of open lines leads the state the
analysis's handoff opens with, beside a door back to the analysis» (SPEC-001 R16) — and the skill
itself is the first door. The line is cut to `x-ceilings.state`. Its doors are the invocations
the skill's own report names ready to paste — the marker "`/<skill>` invocation ready to paste" inside the file's report
section — each under `others`, none recommended, each carrying `entry` and the `check` that
`door.py --check` answered for it: its first line and its `refused:` facts, or `not checked` with
why, where no script decides that door or an input it takes is not named here. `report` is a path
under `siegard/handoff/` in the same git common directory — outside the tree every entry point
holds to `git status`, so writing the report there makes no root pending. `--save-report` writes
it there from standard input, because the harness asks the person before its own file tools write
under a git directory; it refuses a path outside `siegard/handoff/` and a report already written.
Every field only the model can fill is left empty, and the skeleton fails the schema on exactly
those.

`--render` reads `state_from` again and refuses a record whose `state` differs from what the
script prints now; it is required of kind `decision`. A state read from a script is quoted as the
script printed it, in a fence, and the term list does not read it. `--render` refuses a door
recommended whose `check` says `refuses`, and a recommendation whose `why` or `reverses_if` is
blank: «without all four, none is named» (SPEC-006 R2).

`--check` reads a handoff already written as free text, where no record says what it holds, and
decides only what the text alone decides: no term of `x-jargon` in its first `x-ceilings.opening`
characters; and, where it hands a decision — `x-hands-a-decision` — a length within
`x-ceilings.message` and a word of `x-decision-words` within those first characters. Text inside a
code fence is a paste and is read for its length only. A term `x-jargon` holds as plain English
counts in English text only backticked or inside one of its phrases, and as a whole word in text
of another language; a record names its language, and free text is read as English where the
English markers of `x-jargon` outnumber the others. Whether the prose is in the person's language
is not decidable from the text and is not checked. `telemetry.py` imports `reading` and
`violations` from here, so a handoff is measured by the same definition it is held to.

Declared dependencies: jsonschema; PyYAML for `--prepare` and for a `state_from` naming `goal.py`
(this script imports goal.py, progress.py and door.py, its siblings, only there).

Usage:  handoff.py --prepare --skill <name> --project <root> [--slug <slug>] [--target <key>] [--file <path>]... [--ledger <ledger.md>] [--language <en|pt-BR>]
                                             print the record's skeleton: the state a script
                                             printed, the skill's next doors each checked, the
                                             report's path. --file is the file set a door that
                                             takes one is checked over
        handoff.py --save-report <path>      write the full report read from standard input to
                                             the path the skeleton's `report` names
        handoff.py --render <record.json>    render the record, or refuse it
        handoff.py --render -                render the record read from standard input
        handoff.py --check <message-file>    hold a written handoff to what is decidable
        handoff.py --check -                 hold the handoff read from standard input
        handoff.py --help                    print this text and stop
Exit:   0 prepared: the skeleton on standard output; rendered: the message; or checked: nothing found
        1 the record is refused, or the handoff does not hold: one problem per line
        2 cannot run
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator

BIN = Path(__file__).resolve().parent
sys.path.insert(0, str(BIN))

CANNOT_RUN = 2
CONTRACT = BIN.parent / "schemas" / "handoff.json"
SKILLS = BIN.parent / "skills"
FENCE = re.compile(r"^[ \t]*```.*?^[ \t]*```[^\n]*$", re.S | re.M)
INVOCATION = re.compile(r"^[ \t]*`?/[a-z][\w:-]*(?:[ \t`]|$)", re.M)
CLOSING = (".", "!", "?", ":", "…")
REPORT_HEADING = re.compile(r"^(#{2,3}) (?:\d+\. )?(?:Report\b|The report\b)", re.M)
REFERENCE_REPORT = re.compile(r"# (?:Report\b|The report\b)")
NEXT_DOOR = re.compile(r"`/([a-z][\w-]*)` invocation ready to paste")
STATE_SCRIPTS = ("goal.py", "progress.py")
HANDOFF_DIR = ("siegard", "handoff")
GIT_TIMEOUT_SECONDS = 5


def load_contract(path: Path = CONTRACT) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def prose_of(text: str) -> str:
    """The text a person reads as prose: every fenced code block removed, the paste it holds
    being the one place a command or a skill's name belongs."""
    return FENCE.sub("", text)


def asks(text: str) -> bool:
    """Whether a message closes on a question: its final paragraph holds one."""
    return "?" in text.strip().rsplit("\n\n", 1)[-1]


def words_of(text: str) -> list[str]:
    return re.findall(r"[^\W\d_]+", text.casefold())


def english(text: str, contract: dict) -> bool:
    """Whether free text reads as English: its words of `x-jargon`'s English markers outnumber
    its words of the other markers."""
    listed = contract["x-jargon"]
    counted = words_of(text)
    ours = set(listed["english_markers"])
    theirs = set(listed["other_markers"])
    return sum(w in ours for w in counted) > sum(w in theirs for w in counted)


def jargon_in(text: str, contract: dict, language: str | None = None) -> list[tuple[str, str]]:
    """Every term, phrase or pattern of `x-jargon` the text carries, in order of first
    appearance, each as its name in the list and the words it matched. A term of
    `english_terms` counts backticked wherever it sits, and as a whole word only where the text
    is not English — by the record's `language` where one is named, by `english` otherwise."""
    listed = contract["x-jargon"]
    plain_english = language == "en" if language is not None else english(text, contract)
    found: list[tuple[int, str, str]] = []

    def whole(term: str) -> re.Match | None:
        return re.search(r"(?<![\w-])" + re.escape(term) + r"(?![\w-])", text, re.I)

    for term in listed["terms"]:
        hit = whole(term)
        if hit:
            found.append((hit.start(), term, hit.group(0)))
    for term in listed["english_terms"]:
        hit = re.search(r"`" + re.escape(term) + r"`", text, re.I) if plain_english else whole(term)
        if hit:
            found.append((hit.start(), term, hit.group(0)))
    for phrase in listed["phrases"]:
        hit = re.search(r"(?<![\w-])" + r"\s+".join(map(re.escape, phrase.split())) + r"(?![\w-])",
                        text, re.I)
        if hit:
            found.append((hit.start(), phrase, hit.group(0)))
    for name, pattern in listed["patterns"].items():
        hit = re.search(pattern, text)
        if hit:
            found.append((hit.start(), name, hit.group(0)))
    seen: set[str] = set()
    out = []
    for _, name, matched in sorted(found):
        if name not in seen:
            seen.add(name)
            out.append((name, matched))
    return out


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
    language = "en" if english(prose, contract) else "other"
    return {
        "characters": len(text),
        "hands_decision": hands_a_decision(text, contract),
        "jargon_in_opening": [name for name, _ in jargon_in(prose[:opening], contract, language)],
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


# ------------------------------------------------------------------ the state, from a script


def cut(line: str, contract: dict) -> str:
    ceiling = contract["x-ceilings"]["state"]
    line = " ".join(line.split())
    return line if len(line) <= ceiling else line[:ceiling - 1] + "…"


def armed_goal(project: Path) -> dict | None:
    """The goal armed through the framework over this project's repository, or None."""
    import goal
    try:
        return goal.read_armed(goal.armed_path(project))
    except (goal.Refused, OSError):
        return None


def goal_line(project: Path) -> str:
    import goal
    record = armed_goal(project)
    if record is None:
        return "goal.py: no goal is armed in this project"
    try:
        fields = goal.resolve(Path(record["project_root"]), record.get("target"))
        first, _ = goal.state(fields, record["slug"], record["since"], record["version"],
                              list(record.get("scope") or []), list(record.get("untouched") or []))
    except (goal.Refused, KeyError, OSError) as broken:
        return f"goal.py --state cannot run: {broken}".splitlines()[0]
    return first


def progress_line(project: Path, slug: str | None, language: str, contract: dict) -> str:
    """The segment `progress.py` prints for the slug, where the line holds one; else its whole
    line; else the fixed words for a project with nothing live."""
    import progress
    try:
        line = progress.line_of(project)
    except Exception:
        line = ""
    if slug and line:
        for segment in line.split(" | "):
            if segment == slug or segment.startswith(slug + progress.SEPARATOR):
                return segment
    return line or contract["x-labels"][language]["quiet"]


def open_count(ledger: str | None) -> int:
    """The lines of the material a ledger leaves open, as `trace.py` reads them; none named, none
    open. A ledger that cannot be read is no count the state can carry, and counts none."""
    if not ledger:
        return 0
    import trace
    return trace.open_lines(Path(ledger)) or 0


def state_now(source: dict, language: str, contract: dict) -> str:
    """The line `state_from` names, as its script prints it now, cut to the state ceiling — led by
    the count of lines a material ledger it names leaves open: «the count of open lines leads the
    state the analysis's handoff opens with» (SPEC-001 R16)."""
    project = Path(source["project"])
    if source["script"] == "goal.py":
        line = goal_line(project)
    else:
        line = progress_line(project, source.get("slug"), language, contract)
    count = open_count(source.get("ledger"))
    if count:
        line = contract["x-labels"][language]["open_lines"].format(n=count) + " · " + line
    return cut(line, contract)


def state_source(project: Path, slug: str | None, ledger: str | None = None) -> dict:
    """Which script the state is read from: the armed goal where one is, else progress; and the
    material ledger whose open lines lead it, where the skill names one."""
    held = {"ledger": str(Path(ledger).resolve())} if ledger else {}
    if armed_goal(project) is not None:
        return {"script": "goal.py", "project": str(project), **held}
    return {"script": "progress.py", "project": str(project), **({"slug": slug} if slug else {}),
            **held}


# ------------------------------------------------------------------ the doors, checked


def report_sections(text: str) -> str:
    """Every report section of a skill's file — from its heading to the next heading of the
    same level or higher — joined, whitespace collapsed so a marker may wrap."""
    sections = []
    for head in REPORT_HEADING.finditer(text):
        rest = text[head.end():]
        end = re.search(r"^#{2,%d} " % len(head.group(1)), rest, re.M)
        sections.append(rest[:end.start()] if end else rest)
    return re.sub(r"\s+", " ", " ".join(sections))


def report_text(skill: str) -> str:
    """The report of `skill`: the report sections of its `SKILL.md`, then every reference file
    of the skill whose own title is the report, whole."""
    texts = [report_sections((SKILLS / skill / "SKILL.md").read_text(encoding="utf-8"))]
    for path in sorted((SKILLS / skill / "references").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        if REFERENCE_REPORT.match(text):
            texts.append(re.sub(r"\s+", " ", text))
    return " ".join(texts)


def next_doors(skill: str) -> list[str]:
    """The skills the report of `skill`'s own files hands as invocations ready to paste, in the
    order the files name them first."""
    doors: list[str] = []
    for name in NEXT_DOOR.findall(report_text(skill)):
        if name != skill and name not in doors:
            doors.append(name)
    return doors


def check_door(name: str, project: Path, slug: str | None, target: str | None,
               files: list[str]) -> dict:
    """`door.py --check`'s first line and `refused:` facts for the door, or `not checked` and
    why where no script decides it or an input it takes is not named."""
    import door
    if name not in door.DOORS:
        return {"answer": "not checked",
                "why": f"no script decides what /{name} refuses; its own file states it"}
    if name == "reconcile":
        return {"answer": "not checked",
                "why": "/reconcile reads the file set and free slug `trace.py --reconcile-set` "
                       "prints, and no script here decides what it refuses"}
    if name in door.NAMED_SLUG and not slug:
        return {"answer": "not checked", "why": f"/{name} takes a slug, and none was named"}
    args = {"target": target, "slug": slug, "task": [], "name": None, "scope": [], "file": files,
            "standard": None}
    lines = door.check(name, project, args).lines(name)
    return {"answer": lines[0],
            "refused": [line[len("refused: "):] for line in lines if line.startswith("refused: ")]}


def report_path(project: Path, skill: str) -> Path | None:
    """Where the full report is written: under the repository's git common directory, outside
    the tree; None where git does not hold the project."""
    try:
        done = subprocess.run(["git", "-C", str(project), "rev-parse", "--path-format=absolute",
                               "--git-common-dir"], capture_output=True, text=True,
                              timeout=GIT_TIMEOUT_SECONDS)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if done.returncode != 0 or not done.stdout.strip():
        return None
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return Path(done.stdout.strip()).joinpath(*HANDOFF_DIR) / f"{stamp}-{skill}.md"


def prepare(skill: str, project: Path, slug: str | None, target: str | None, files: list[str],
            language: str, contract: dict, ledger: str | None = None) -> dict:
    """The record's skeleton: what scripts decide written, what only the model writes empty. A
    ledger leaving lines open hands the skill itself as the first door — «beside a door back to
    the analysis, so an analysis with lines open is never handed as complete» (SPEC-001 R16)."""
    source = state_source(project, slug, ledger)
    names = next_doors(skill)
    if open_count(source.get("ledger")):
        names = [skill] + names
    doors = [{"reply_word": "", "what_it_does": "", "entry": f"/{name}",
              "check": check_door(name, project, slug, target, files)}
             for name in names]
    record: dict = {"contract_version": contract["properties"]["contract_version"]["const"],
                    "kind": "decision" if doors else "report", "language": language,
                    "state": state_now(source, language, contract), "state_from": source}
    if doors:
        record["decisions"] = [{"ask": "", "others": doors, "if_none": ""}]
    path = report_path(project, skill)
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        record["report"] = str(path)
    return record


# ------------------------------------------------------------------ the rendering


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


def prose_fields(record: dict, opening: int) -> list[tuple[str, str]]:
    """Every field of the record a person reads as prose, by where it sits; the line ready to
    paste, the report's path, and a state a script printed are not the record's prose. A `body`
    above a `report` path is the short form and is read whole; a body that is the answer itself
    is read over its opening span, as free text is."""
    fields = [] if "state_from" in record else [("state", record["state"])]
    if "body" in record:
        fields.append(("body", record["body"] if "report" in record
                       else record["body"][:opening]))
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


def unfilled_recommendations(record: object) -> list[str]:
    """A recommendation whose `why` or `reverses_if` is blank, named before the schema speaks,
    so the refusal says what is missing rather than that a string is too short."""
    problems = []
    decisions = record.get("decisions") if isinstance(record, dict) else None
    for at, decision in enumerate(decisions if isinstance(decisions, list) else []):
        chosen = decision.get("recommended") if isinstance(decision, dict) else None
        if not isinstance(chosen, dict):
            continue
        for key in ("why", "reverses_if"):
            value = chosen.get(key)
            if not isinstance(value, str) or not value.strip():
                problems.append(f"decisions/{at}/recommended/{key}: empty — a recommendation "
                                f"names why it holds and the fact that would change it, and "
                                f"without both none is named")
    return problems


def render(record: object, contract: dict, base: Path, state_of=state_now
           ) -> tuple[str | None, list[str]]:
    """The message the record renders to, or None and the problems that refuse it. `state_of`
    reads a `state_from` as its script prints it now."""
    problems = unfilled_recommendations(record)
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
    if "state_from" in record:
        now = state_of(record["state_from"], record["language"], contract)
        if record["state"] != now:
            problems.append(f"state: differs from what {record['state_from']['script']} prints "
                            f"now ({now!r}); the state is the script's line — run "
                            f"handoff.py --prepare again and carry its state")
    for where, text in prose_fields(record, ceilings["opening"]):
        for name, matched in jargon_in(text, contract, record["language"]):
            problems.append(f"{where}: carries {name} ({matched!r}), a word of this framework a "
                            f"person never reads in a handoff")
    body = record.get("body", "")
    if decision_word_at(body, contract, ("recommendation",)) is not None \
            and labels["reverses_if"].casefold() not in body.casefold():
        problems.append(f"body: recommends without the fact that would change it — say it after "
                        f"{labels['reverses_if']!r}: «without all four, none is named» "
                        f"(SPEC-006 R2)")
    seen: dict[str, str] = {}
    for at, decision in enumerate(record.get("decisions", [])):
        chosen = decision.get("recommended")
        if chosen and chosen.get("check", {}).get("answer") == "refuses":
            problems.append(f"decisions/{at}/recommended: {chosen.get('entry', 'the door')} is "
                            f"refused by its own entry point as the tree stands — "
                            + "; ".join(chosen["check"].get("refused") or ["no fact recorded"])
                            + " — an excluded door is said excluded, never recommended")
        doors = ([chosen] if chosen else []) + decision["others"]
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
    parts = [f"```\n{record['state']}\n```" if "state_from" in record else record["state"]]
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


# ------------------------------------------------------------------ the command


class CannotRun(Exception):
    pass


def take(args: list[str], flag: str, many: bool = False):
    values = []
    while flag in args:
        at = args.index(flag)
        if at + 1 >= len(args) or args[at + 1].startswith("--"):
            raise CannotRun(f"{flag} takes a value")
        values.append(args[at + 1])
        del args[at:at + 2]
        if not many:
            if flag in args:
                raise CannotRun(f"{flag} is named twice")
            break
    return values if many else (values[0] if values else None)


def main_prepare(args: list[str], contract: dict) -> int:
    try:
        skill = take(args, "--skill")
        project = take(args, "--project")
        slug = take(args, "--slug")
        target = take(args, "--target")
        files = take(args, "--file", many=True)
        ledger = take(args, "--ledger")
        language = take(args, "--language") or "en"
    except CannotRun as refusal:
        print(f"cannot run: {refusal}", file=sys.stderr)
        return CANNOT_RUN
    if args or not skill or not project:
        print("cannot run: --prepare takes --skill <name> and --project <root>"
              + (f"; not understood: {' '.join(args)}" if args else ""), file=sys.stderr)
        return CANNOT_RUN
    skill = skill.removeprefix("/").removeprefix("siegard:")
    if not (SKILLS / skill / "SKILL.md").is_file():
        print(f"cannot run: {skill} is no skill of this plugin", file=sys.stderr)
        return CANNOT_RUN
    if language not in contract["x-labels"] or language == "description":
        print(f"cannot run: {language} is no language the record admits — "
              + ", ".join(contract["properties"]["language"]["enum"]), file=sys.stderr)
        return CANNOT_RUN
    root = Path(project).resolve()
    if not root.is_dir():
        print(f"cannot run: {root} is not a directory", file=sys.stderr)
        return CANNOT_RUN
    if ledger and not Path(ledger).is_file():
        print(f"cannot run: {ledger} is no ledger file", file=sys.stderr)
        return CANNOT_RUN
    record = prepare(skill, root, slug, target, files, language, contract, ledger)
    print(json.dumps(record, indent=2, ensure_ascii=False))
    return 0


def main_save_report(args: list[str]) -> int:
    if len(args) != 1:
        print("cannot run: --save-report takes the report's path, the text on standard input",
              file=sys.stderr)
        return CANNOT_RUN
    path = Path(args[0]).resolve()
    if tuple(path.parent.parts[-len(HANDOFF_DIR):]) != HANDOFF_DIR or path.suffix != ".md":
        print(f"refused: {path} is no report path: --prepare names one under "
              f"{'/'.join(HANDOFF_DIR)}/ in the git common directory")
        return 1
    if path.exists():
        print(f"refused: {path} is already written; run --prepare again for a new report path")
        return 1
    text = sys.stdin.read()
    if not text.strip():
        print("refused: the report read from standard input is empty")
        return 1
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")
    except OSError as broken:
        print(f"cannot run: {broken}", file=sys.stderr)
        return CANNOT_RUN
    print(path)
    return 0


def main() -> int:
    args = sys.argv[1:]
    if "--help" in args:
        print(__doc__.strip())
        return 0
    try:
        contract = load_contract()
    except (OSError, json.JSONDecodeError) as broken:
        print(f"cannot run: {CONTRACT} is unreadable: {broken}", file=sys.stderr)
        return CANNOT_RUN
    if args[:1] == ["--prepare"]:
        return main_prepare(args[1:], contract)
    if args[:1] == ["--save-report"]:
        return main_save_report(args[1:])
    if len(args) != 2 or args[0] not in ("--render", "--check"):
        print("cannot run: expected --prepare --skill <name> --project <root>, "
              "--render <record.json|-> or --check <message-file|->", file=sys.stderr)
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
