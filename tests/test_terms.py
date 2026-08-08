"""The glossary is derived, and these tests are what keeps it from becoming a copy.

The central one is `test_the_printed_definition_is_the_schema_text`. A glossary that paraphrased
its sources would read the same on the day it was written and be wrong a month later, with nothing
to say so. Holding the printed text to the schema's byte-for-byte is the whole guarantee: the only
way to change what `terms.py` prints is to change the contract it points at.

The rest hold the two conditions the script's own refusals depend on — every pointer resolves, and
no term is both defined and named as undefined — plus the drift these tests were written after: the
`slug` definition had already lost its second sentence in one of the four schemas that state it, and
`$defs/pin` carried no description in either schema that referenced it.
"""
from __future__ import annotations

import json
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCHEMAS = REPO / "src/claude/schemas"
TERMS_PY = REPO / "src/claude/bin/terms.py"

sys.path.insert(0, str(REPO / "src/claude/bin"))
import terms  # noqa: E402


def resolve(document: object, pointer: str) -> object:
    current = document
    for raw in pointer.split("/")[1:]:
        current = current[raw.replace("~1", "/").replace("~0", "~")]
    return current


@pytest.fixture(scope="module")
def loaded() -> dict[str, object]:
    return {p.name: json.loads(p.read_text(encoding="utf-8")) for p in SCHEMAS.glob("*.json")}


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(TERMS_PY), *args],
                          capture_output=True, text=True)


@pytest.mark.parametrize("term", sorted(terms.TERMS))
def test_every_pointer_resolves_to_a_description(term, loaded):
    """A pointer that stopped resolving is the failure mode this table is exposed to: a definition
    moves, and a glossary that skipped the term it could no longer find would read as complete."""
    relative, pointer = terms.TERMS[term]
    assert relative in loaded, f"{term} points at {relative}, which src/claude/schemas does not hold"
    target = resolve(loaded[relative], pointer)
    assert isinstance(target, dict), f"{term}: {relative}{pointer} is not an object"
    assert isinstance(target.get("description"), str) and target["description"], \
        f"{term}: {relative}{pointer} carries no description"


@pytest.mark.parametrize("term", sorted(terms.TERMS))
def test_the_printed_definition_is_the_schema_text(term, loaded):
    """Unwrapped, what the script prints is the contract's own sentence — never a paraphrase of it.
    This is the anti-drift guarantee, and it is the reason the table holds pointers and not text."""
    relative, pointer = terms.TERMS[term]
    expected = resolve(loaded[relative], pointer)["description"]
    printed = run(term)
    assert printed.returncode == 0, printed.stderr
    body = "\n".join(line[4:] for line in printed.stdout.splitlines() if line.startswith("    "))
    assert " ".join(body.split()) == " ".join(expected.split()), \
        f"{term}: what is printed is not what {relative}{pointer} says"


def test_no_term_is_both_defined_and_undefined():
    both = sorted(set(terms.TERMS) & set(terms.OPEN))
    assert both == [], f"{both} are listed as defined and as holding no definition"


def test_the_open_list_names_something():
    """An empty open list would mean every term is defined, which is a claim this repository cannot
    make yet. If it ever empties honestly, delete this test in the same change that empties it."""
    assert terms.OPEN, "the open list is empty; every term the framework uses is now defined?"


def test_naming_an_undefined_term_is_a_refusal_not_a_silence():
    result = run("record")
    assert result.returncode == 1
    assert "record" in result.stderr


def test_the_full_listing_holds_every_term(loaded):
    result = run()
    assert result.returncode == 0, result.stderr
    for term in terms.TERMS:
        assert term in result.stdout, f"the listing omits {term}"
    for term in terms.OPEN:
        assert term in result.stdout, f"the listing omits the open term {term}"


# ------------------------------------------------- the drift these tests were written after


SLUG_HOLDERS = ("plan-node.json", "standard.json", "project.json")


def test_every_slug_definition_is_the_same_sentence(loaded):
    """These schemas state what a slug is with the identical full sentence — node.json once made
    a third before it retired, and one of the two remaining had quietly dropped the clause that
    decides a name which will not reduce. Copies of one definition are kept honest mechanically or
    not at all."""
    stated = {name: loaded[name]["$defs"]["slug"]["description"] for name in SLUG_HOLDERS}
    assert len(set(stated.values())) == 1, \
        f"the slug definition differs across the schemas that state it: {stated}"


@pytest.mark.parametrize("relative", ("delivery-node.json", "trace.json"))
def test_the_shared_pin_definition_says_what_a_pin_is(relative, loaded):
    """These schemas reference `$defs/pin` while it carried a pattern and nothing else, so the one
    definition every pin field pointed at said nothing at all. plan-node.json dropped the concept
    entirely: a task names what it implements by identity, and nothing there is pinned any more."""
    shared = loaded[relative]["$defs"]["pin"]
    assert isinstance(shared.get("description"), str) and shared["description"], \
        f"{relative} $defs/pin carries no description; every field referencing it defines nothing"
