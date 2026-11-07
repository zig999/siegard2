#!/usr/bin/env python3
"""Measure the instruction text of one skill and the agents it spawns, as a reader pays for it.

The measures are the ones Anthropic's guidance for skills and prompts names: what the text costs
in context (characters), how long its sentences run, whether one concept carries one name, how
wide its prose lines are, and how long the descriptions every session loads are. Nothing here
judges a sentence; it counts. `tests/test_text_metrics.py` holds the shipped text to the baseline
recorded beside the implement-task benchmark, so a change that grows a measure is red.

Prose is the file minus its frontmatter, its fenced blocks and its «…» quotations — a quotation
is a requirement's own words, which this text may not change. Line width is read on the file's own
lines outside fenced and indented blocks and tables; a synonym is counted outside inline code,
where a name such as a file's is not the word.

Usage:
    python3 tools/text_metrics.py <plugin-root> [<skill>] [--agents a,b,c]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

FENCE = re.compile(r"```.*?```", re.S)
FRONT = re.compile(r"\A---\n(.*?)\n---\n", re.S)
QUOTE = re.compile(r"«[^»]*»")
INLINE_CODE = re.compile(r"`[^`\n]*`")
SENTENCE_END = re.compile(r"(?<=[.;:!?])\s+(?=[A-Z`*«(\[])")
SYNONYMS = {
    "the person": ("the human", "a human", "human's"),
    "subagent": ("delegation",),
}


def files_of(plugin: Path, skill: str, agents: tuple[str, ...]) -> list[Path]:
    folder = plugin / "skills" / skill
    return [folder / "SKILL.md", *sorted((folder / "references").glob("*.md")),
            *(plugin / "agents" / f"{a}.md" for a in agents)]


def prose(text: str) -> str:
    text = FRONT.sub("", text)
    text = FENCE.sub("\n\n", text)
    return QUOTE.sub("«»", text)


def prose_lines(text: str) -> list[str]:
    """The file's own prose lines: no frontmatter, no fenced or indented block, no table row."""
    text = FENCE.sub("\n", FRONT.sub("", text))
    return [line for line in text.splitlines()
            if not line.startswith("    ") and not line.lstrip().startswith("|")]


ITEM = re.compile(r"\n(?=\s*(?:- |\d+\. ))")


def sentences(text: str) -> list[int]:
    """Words per sentence; a list item starts a sentence, and an indented block holds none."""
    words = []
    for para in re.split(r"\n\s*\n", prose(text)):
        if para.startswith("    "):
            continue
        for item in ITEM.split(para):
            item = " ".join(line.strip() for line in item.splitlines()
                            if not line.lstrip().startswith(("#", "|")))
            item = re.sub(r"^(?:- |\d+\. )", "", item)
            for s in SENTENCE_END.split(item):
                if s.strip():
                    words.append(len(s.split()))
    return words


def description(text: str) -> str:
    match = FRONT.match(text)
    if not match:
        return ""
    found = re.search(r"^description: (.*)$", match.group(1), re.M)
    return found.group(1) if found else ""


def percentile(values: list[int], share: float) -> int:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(len(ordered) * share))] if ordered else 0


def measure(paths: list[Path]) -> dict:
    texts = {p: p.read_text(encoding="utf-8") for p in paths}
    words = [n for t in texts.values() for n in sentences(t)]
    wide = sum(1 for t in texts.values() for line in prose_lines(t) if len(line) > 100)
    lowered = {p: INLINE_CODE.sub("", prose(t)).lower() for p, t in texts.items()}
    synonyms = {name: sum(lowered[p].count(s) for p in paths for s in banned)
                for name, banned in SYNONYMS.items()}
    return {
        "files": len(paths),
        "chars": sum(len(t) for t in texts.values()),
        "skill_chars": len(texts[paths[0]]),
        "sentences": len(words),
        "sentence_words_median": percentile(words, 0.5),
        "sentence_words_p90": percentile(words, 0.9),
        "sentence_words_max": max(words, default=0),
        "sentences_over_60_words": sum(1 for n in words if n > 60),
        "prose_lines_over_100": wide,
        "synonyms": synonyms,
        "description_chars": {p.stem if p.name != "SKILL.md" else "skill": len(description(t))
                              for p, t in texts.items() if description(t)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("plugin", type=Path)
    parser.add_argument("skill", nargs="?", default="implement-task")
    parser.add_argument("--agents", default="task-implementer,test-author,failure-diagnostician")
    a = parser.parse_args()
    print(json.dumps(measure(files_of(a.plugin, a.skill, tuple(a.agents.split(",")))), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
