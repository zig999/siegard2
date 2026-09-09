"""Every distributed citation of a specification carries a sentence of it verbatim.

A `(SPEC-00x Rn)` in a message, a docstring, a schema description or a skill's prose is this
repository's pointer: it names the requirement the artifact implements, and `specs/` never
ships, so a consumer cannot follow it. What the consumer gets instead is the sentence beside
it — `«…»`, the requirement's own words, so the rule is read in the words it was decided in
rather than in a paraphrase that drifts. These tests hold the two together: a specification
that changes its words leaves this red until every artifact citing it follows, and a citation
that names a requirement whose words it does not carry is a pointer to something else.

Two things measured before this existed. Of 65 citations carrying a requirement number, 7 were
verbatim and 58 paraphrased; two of the 58 paraphrased a *different* requirement than the one
they named — `SPEC-001 R8` beside R4's sentence, `SPEC-003 R2` beside SPEC-002 R4's. Only a
verbatim check sees that class: the pointer resolves, the words belong elsewhere. And of 39
requirement lines edited over this repository's history, 22 were on requirements cited in the
distribution — the coupling this test creates is the coupling those edits already had, unchecked.

The quote is delimited, never inferred: three heuristic extractors over the same corpus found
3, 5 and 7 verbatim citations, and a test whose false negatives are unknown certifies what it
cannot see. `«»` occurs nowhere else under src/claude, so the span is exact.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SPECS = REPO / "specs"
SRC = REPO / "src"  # claude/ ships as the plugin, consumer/ ships to the consumer's root
MIN_WORDS = 3

CITATION = re.compile(r"\((SPEC-00\d)(?: (R\d+)| §([^)]+?))?\)")
TOKEN = re.compile(r"SPEC-00\d")
QUOTED = re.compile(r"«([^»]*)»\s*\((SPEC-00\d)(?: (R\d+)| §([^)]+?))?\)")
REQUIREMENT = re.compile(r"^- \*\*(R\d+)\*\* — (.*?)(?=\n- \*\*R|\n\n|\n#|\Z)", re.S | re.M)
HEADING = re.compile(r"^(#{2,3}) (.+?)\s*$", re.M)
PLACEHOLDER = re.compile(r"\{[^}]*\}")
CONTINUATION = re.compile(r'"\s*\n\s*f?"')


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[`*\"'’]", "", text)).strip().lower()


def requirements() -> dict[str, str]:
    """`SPEC-00x Rn` -> bullet text; `SPEC-00x §Heading` -> the text under that heading."""
    held: dict[str, str] = {}
    for path in sorted(SPECS.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        spec = re.search(r'^id: "(SPEC-\d+)"', text, re.M).group(1)
        for number, body in REQUIREMENT.findall(text):
            held[f"{spec} {number}"] = body
        heads = list(HEADING.finditer(text))
        for at, head in enumerate(heads):
            level, title = len(head.group(1)), head.group(2)
            end = len(text)
            for later in heads[at + 1:]:
                if len(later.group(1)) <= level:
                    end = later.start()
                    break
            held[f"{spec} §{title}"] = text[head.end():end]
    return held


def distributed() -> list[tuple[Path, str]]:
    out = []
    for path in sorted(SRC.rglob("*")):
        if path.suffix in (".py", ".json", ".md") and path.is_file():
            text = path.read_text(encoding="utf-8")
            if path.suffix == ".py":
                text = CONTINUATION.sub("", text)
            out.append((path, text))
    return out


def key_of(spec: str, number: str | None, section: str | None) -> str:
    return f"{spec} {number}" if number else f"{spec} §{section}" if section else spec


def line_of(text: str, at: int) -> int:
    return text.count("\n", 0, at) + 1


@pytest.fixture(scope="module")
def held():
    return requirements()


def test_the_specifications_hold_requirements_and_sections(held):
    assert any(k.endswith(" R1") for k in held), "no requirement bullet parsed; the guard lost its subject"
    assert any("§" in k for k in held), "no section parsed"


def test_every_citation_names_a_requirement_or_section(held):
    """A pointer to a whole specification cites no sentence; it must name the requirement or
    the section whose words it carries, so the next test knows what to compare against."""
    problems = []
    for path, text in distributed():
        for m in CITATION.finditer(text):
            spec, number, section = m.group(1), m.group(2), m.group(3)
            if not number and not section:
                problems.append(f"{path.relative_to(REPO)}:{line_of(text, m.start())}: "
                                f"({spec}) names no requirement and no section")
            elif key_of(spec, number, section) not in held:
                problems.append(f"{path.relative_to(REPO)}:{line_of(text, m.start())}: "
                                f"{key_of(spec, number, section)} — nothing under specs/ answers to it")
    assert not problems, f"{len(problems)} citation(s) resolve to nothing:\n  " + "\n  ".join(problems)


def test_no_citation_stands_without_its_quote():
    """The old suffix form — a paraphrase and then `(SPEC-…)` — is what let the words drift from
    the pointer. Every citation is preceded by `«…»`, or it is not a citation this repository
    makes."""
    problems = []
    for path, text in distributed():
        covered = [(m.start(), m.end()) for m in QUOTED.finditer(text)]
        for m in TOKEN.finditer(text):
            if not any(a <= m.start() < b for a, b in covered):
                problems.append(f"{path.relative_to(REPO)}:{line_of(text, m.start())}: "
                                f"{text[max(0, m.start() - 30):m.end() + 12].strip()!r} — a "
                                f"specification is named only as «sentence» (SPEC-00x Rn|§Section)")
    assert not problems, f"{len(problems)} citation(s) without a quote:\n  " + "\n  ".join(problems)


def test_every_citation_quotes_its_requirement_verbatim(held):
    """The sentence in `«…»` is a substring of the requirement or section it names — words
    intact, whitespace and markup ignored, no placeholder inside. Three words at least: below
    that it is not a sentence of anything."""
    problems = []
    for path, text in distributed():
        for m in QUOTED.finditer(text):
            quote, spec, number, section = m.group(1), m.group(2), m.group(3), m.group(4)
            key = key_of(spec, number, section)
            where = f"{path.relative_to(REPO)}:{line_of(text, m.start())}"
            if key not in held:
                continue  # the previous test names this
            if PLACEHOLDER.search(quote):
                problems.append(f"{where}: «{quote}» carries a placeholder; the quote is the "
                                f"rule's words, not the message's variables")
            elif len(quote.split()) < MIN_WORDS:
                problems.append(f"{where}: «{quote}» is under {MIN_WORDS} words; not a sentence")
            elif normalise(quote) not in normalise(held[key]):
                problems.append(f"{where}: «{quote}» is not a sentence of {key}\n"
                                f"      {key} reads: {re.sub(r'\\s+', ' ', held[key])[:220]}")
    assert not problems, f"{len(problems)} quote(s) not verbatim:\n  " + "\n  ".join(problems)
