#!/usr/bin/env python3
"""Count, per shipped instruction file, every variant schemas/terms.json lists for a concept.

`schemas/terms.json` is the one list of concepts and their variants; this module reads it and
counts each variant over a file's prose — frontmatter, fenced blocks, «…» quotations and inline
code removed, whole words, case-insensitive. `tests/test_terms.py` holds the counts:
`forbidden` variants at zero in a concept's `clean` files, and every count elsewhere exactly at
the pin tests/fixtures/term-counts.json records. A file cleaned lowers its pin; `--write`
rewrites the pins from the tree as it stands, and the change that runs it says why in its commit.

Usage:
    python3 tools/term_counts.py            # print the counts as the pin file would hold them
    python3 tools/term_counts.py --write    # rewrite tests/fixtures/term-counts.json
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TERMS = REPO / "schemas/terms.json"
PINS = REPO / "tests/fixtures/term-counts.json"
FRONT = re.compile(r"\A---\n.*?\n---\n", re.S)
FENCE = re.compile(r"```.*?```", re.S)
QUOTE = re.compile(r"«[^»]*»")
INLINE = re.compile(r"`[^`\n]*`")


def terms() -> dict:
    return json.loads(TERMS.read_text(encoding="utf-8"))


def scope() -> list[Path]:
    found: set[Path] = set()
    for pattern in terms()["scope"]:
        found.update(REPO.glob(pattern))
    return sorted(found)


def relative(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def prose(text: str) -> str:
    text = FENCE.sub(" ", FRONT.sub("", text))
    text = INLINE.sub(" ", QUOTE.sub(" ", text))
    return re.sub(r"\s+", " ", text).lower()


def count(text: str, variant: str) -> int:
    words = r"\s+".join(re.escape(w) for w in variant.lower().split())
    return len(re.findall(rf"(?<![\w-]){words}(?![\w'’-])", text))


def is_clean(path: str, concept: dict) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in concept["clean"])


def counts() -> dict[str, dict[str, int]]:
    """{file: {variant: n}} for every variant counted anywhere, zeros left out."""
    out: dict[str, dict[str, int]] = {}
    for path in scope():
        text = prose(path.read_text(encoding="utf-8"))
        for concept in terms()["concepts"]:
            for variant in concept["forbidden"] + concept["counted"]:
                n = count(text, variant)
                if n:
                    out.setdefault(relative(path), {})[variant] = n
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--write", action="store_true")
    a = parser.parse_args()
    rendered = json.dumps(counts(), indent=1, sort_keys=True, ensure_ascii=False) + "\n"
    if a.write:
        PINS.write_text(rendered, encoding="utf-8")
        print(f"wrote {relative(PINS)}")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
