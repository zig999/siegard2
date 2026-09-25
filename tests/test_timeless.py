"""What ships states what the framework is, never what it was.

CLAUDE.md's "What ships is timeless" binds everything under `src/`: no rule, skill, agent,
docstring or schema description carries a measurement from a named consumer, an observed
anecdote, an "until this existed", or the form a rule superseded. The evidence that produced a
rule lives in this repository's commits and records; the distribution carries the standing fact.

This test holds the phrasings that species takes. It is a floor, not a proof: history can be
written in words no pattern here names, and a hit is read before it is rewritten. The figure
pattern is digits-only — `3 of 5` is a count someone took; `one of two` is a shape — and the
exceptions list is empty on purpose: a phrase that is legitimate is rewritten until it is not
one of these.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "src"

PATTERNS = [
    r"grew out of",
    r"until this existed",
    r"until these \w+ existed",
    r"did not always",
    r"one consumer",
    r"a consumer's (?:plan|transcripts|project|delivery)",
    r"measured over",
    r"arrived with",
    r"\b\d[\d,]* of \d[\d,]*\b",
]
HISTORY = [re.compile(p.replace(" ", r"\s+"), re.I) for p in PATTERNS]
EXCEPTIONS: list[str] = []


def distributed() -> list[tuple[Path, str]]:
    out = []
    for path in sorted(SRC.rglob("*")):
        if path.suffix in (".py", ".json", ".md") and path.is_file():
            out.append((path, path.read_text(encoding="utf-8")))
    return out


def line_of(text: str, at: int) -> int:
    return text.count("\n", 0, at) + 1


def test_the_corpus_is_read():
    assert any(path.name == "SKILL.md" for path, _ in distributed()), "no skill read; the guard lost its subject"


def test_no_shipped_text_carries_history_or_a_measurement():
    problems = []
    for path, text in distributed():
        for pattern in HISTORY:
            for m in pattern.finditer(text):
                where = f"{path.relative_to(REPO)}:{line_of(text, m.start())}"
                if where in EXCEPTIONS:
                    continue
                problems.append(f"{where}: {' '.join(m.group(0).split())!r}")
    assert not EXCEPTIONS, "the exceptions list is empty by rule; rewrite the text instead"
    assert not problems, (f"{len(problems)} history or measurement phrase(s) under src/ — state the "
                          f"standing fact in the present tense:\n  " + "\n  ".join(problems))
