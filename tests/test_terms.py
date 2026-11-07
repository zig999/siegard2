"""One name per concept in the shipped instructions, held against schemas/terms.json.

«Use one name for a concept across specs, schemas, code, and tests» (this repository's CLAUDE.md).
schemas/terms.json lists each concept's term and its variants; tools/term_counts.py counts them
over each file's prose. Three holds:

- a `forbidden` variant never appears in a concept's `clean` files;
- every other count equals its pin in tests/fixtures/term-counts.json — a ratchet: a file cleaned
  lowers its pin (`python3 tools/term_counts.py --write`), a file that gains a variant is red;
- a skill's `## Terms` defines only concepts schemas/terms.json lists, one per item, opens each
  definition with the concept's `means` verbatim — the one definition, as a «…» citation carries
  a requirement's own sentence — and uses each term again.
"""
from __future__ import annotations

import fnmatch
import json
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import term_counts  # noqa: E402

TERMS = term_counts.terms()
CONCEPTS = TERMS["concepts"]
INFLECTIONS = ("", "s", "ed", "ing")
ITEM = re.compile(r"^- (.*?)(?=^- |\Z)", re.S | re.M)
DEFINITION = re.compile(r"\*\*([^*]+)\*\* — (.*)", re.S)


def test_every_concept_is_stated_whole():
    for concept in CONCEPTS:
        assert set(concept) == {"term", "means", "forbidden", "counted", "clean"}, concept["term"]
        assert concept["means"].strip(), concept["term"]
    variants = [v.lower() for c in CONCEPTS for v in c["forbidden"] + c["counted"]]
    assert len(variants) == len(set(variants)), "a variant is listed under two concepts"
    names = {c["term"].lower() for c in CONCEPTS}
    assert len(names) == len(CONCEPTS), "a term is listed twice"
    assert not names & set(variants), "a term is also listed as a variant"


def test_every_clean_pattern_names_a_shipped_file():
    shipped = [term_counts.relative(p) for p in term_counts.scope()]
    for concept in CONCEPTS:
        for pattern in concept["clean"]:
            assert any(fnmatch.fnmatch(p, pattern) for p in shipped), \
                f"{concept['term']}: clean pattern {pattern} matches no file in scope"


def test_the_count_reads_prose_and_whole_words_only():
    """The guard is not vacuous: a variant in prose counts; in a quotation, inline code, a fence or
    a longer word it does not."""
    text = term_counts.prose("---\nname: x\n---\nThe human decides. «the human» `the human`\n"
                             "```\nthe human\n```\nthe humane; the human's call.\n")
    assert term_counts.count(text, "the human") == 1
    assert term_counts.count(text, "the human's") == 1


@pytest.mark.parametrize("concept", [c for c in CONCEPTS if c["forbidden"] and c["clean"]],
                         ids=lambda c: c["term"])
def test_a_clean_file_carries_no_forbidden_variant(concept):
    found = {}
    for path in term_counts.scope():
        name = term_counts.relative(path)
        if not term_counts.is_clean(name, concept):
            continue
        text = term_counts.prose(path.read_text(encoding="utf-8"))
        hits = {v: term_counts.count(text, v) for v in concept["forbidden"]}
        hits = {v: n for v, n in hits.items() if n}
        if hits:
            found[name] = hits
    assert not found, f"'{concept['term']}' is named otherwise in files held clean: {found}"


def test_every_count_is_at_its_pin():
    pinned = json.loads(term_counts.PINS.read_text(encoding="utf-8"))
    now = term_counts.counts()
    grew = {f: {v: n for v, n in c.items() if n > pinned.get(f, {}).get(v, 0)} for f, c in now.items()}
    grew = {f: c for f, c in grew.items() if c}
    assert not grew, f"a variant of a listed concept grew: {grew} — name the concept by its term " \
                     f"(schemas/terms.json)"
    assert now == pinned, "a count fell below its pin: lower it with " \
                          "`python3 tools/term_counts.py --write` in the same change"


def terms_section(text: str) -> str:
    match = re.search(r"^## Terms\n(.*?)(?=^## )", text, re.S | re.M)
    return match.group(1) if match else ""


def concept_of(defined: str) -> dict | None:
    word = defined.lower().removeprefix("the ").strip()
    for concept in CONCEPTS:
        term = concept["term"].lower()
        if word in (term, term + "s", term.removeprefix("the ")):
            return concept
    return None


SKILLS_WITH_TERMS = sorted(p.parent.name for p in (REPO / "src/claude/skills").glob("*/SKILL.md")
                           if terms_section(p.read_text(encoding="utf-8")))


def test_some_skill_defines_its_terms():
    assert "implement-task" in SKILLS_WITH_TERMS, "the guard below lost its subject"


def definitions(section: str) -> list[tuple[str, str]]:
    """Each `## Terms` item as (the bold term, what follows the dash), whitespace collapsed; an
    item that does not take that form comes back with an empty term."""
    out = []
    for item in ITEM.findall(section):
        item = " ".join(item.split())
        match = DEFINITION.fullmatch(item)
        out.append((match.group(1), match.group(2)) if match else ("", item))
    return out


@pytest.mark.parametrize("skill", SKILLS_WITH_TERMS)
def test_a_skill_defines_each_term_by_its_one_definition(skill):
    """A definition is the concept's `means`, verbatim, as the item's first sentence; what follows
    says how this skill uses the term, never what it means. Changing a `means` reddens every skill
    that carries it until the skill follows."""
    section = terms_section((REPO / "src/claude/skills" / skill / "SKILL.md").read_text(encoding="utf-8"))
    items = definitions(section)
    assert items, f"{skill}'s ## Terms defines nothing"
    for name, body in items:
        assert name, f"{skill}: a ## Terms item is not `- **<Term>** — <definition>`: {body[:80]}"
        concept = concept_of(name)
        assert concept, f"{skill} defines '{name}', which schemas/terms.json does not list"
        means = " ".join(concept["means"].split())
        assert body == means + "." or body.startswith(means + ". "), \
            f"{skill} defines '{name}' as {body[:len(means) + 20]!r}; schemas/terms.json's one " \
            f"definition is {means!r}"
    names = [concept_of(n)["term"] for n, _ in items]
    assert len(names) == len(set(names)), f"{skill} defines a term twice: {names}"


@pytest.mark.parametrize("skill", SKILLS_WITH_TERMS)
def test_a_skill_uses_each_term_it_defines(skill):
    folder = REPO / "src/claude/skills" / skill
    text = (folder / "SKILL.md").read_text(encoding="utf-8")
    section = terms_section(text)
    rest = text.replace(section, "") + "".join(
        p.read_text(encoding="utf-8") for p in sorted(folder.glob("references/*.md")))
    rest = term_counts.prose(rest)
    for name, _ in definitions(section):
        concept = concept_of(name)
        used = sum(term_counts.count(rest, concept["term"] + ending) for ending in INFLECTIONS)
        assert used or concept["term"] == "you", \
            f"{skill} defines '{name}' and never uses '{concept['term']}' outside ## Terms"
