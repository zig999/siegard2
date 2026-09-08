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


@pytest.mark.parametrize("word", sorted({terms.base_of(t) for t in terms.TERMS}))
def test_the_bare_word_answers_for_every_sense_it_names(word):
    """The word is what a refusal puts in front of a reader — `a covered node reaches a task or a
    stated why` says `covers`, not the parenthetical this table tells its senses apart by. A
    lookup answering that word with `no contract defines it`, while holding two definitions of
    it, is the silence this script exists to refuse."""
    result = run(word)
    assert result.returncode == 0, result.stderr
    for term in terms.TERMS:
        if terms.base_of(term) == word:
            assert term in result.stdout, f"{word} does not answer for {term}"


def test_a_sense_named_in_full_answers_alone():
    result = run("covers (a test over a criterion)")
    assert result.returncode == 0, result.stderr
    assert "covers (an epic over specification nodes)" not in result.stdout


def test_a_word_split_across_the_two_tables_says_both():
    """`proof` is defined of a certification's tests and undefined of a delivery kind. Answering
    with the definition alone would let the sense that has one stand for the whole word."""
    result = run("proof")
    assert result.returncode == 0, result.stderr
    assert "proof (a certification's tests)" in result.stdout
    assert "proof (a delivery kind)" in result.stdout


def test_a_word_with_two_senses_is_named_apart_in_both_tables():
    """The disambiguation rule is one rule over both tables. A word held bare in one and
    parenthesized in the other reads, from the bare side, as the whole word — which is how
    `proof` came to be listed as holding no definition while a contract defined it."""
    counted: dict[str, list[str]] = {}
    for term in list(terms.TERMS) + list(terms.OPEN):
        counted.setdefault(terms.base_of(term), []).append(term)
    for word, held in sorted(counted.items()):
        if len(held) > 1:
            assert all(term != word for term in held), \
                f"{word} names {len(held)} senses and one of them is the bare word: {held}"


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


def test_every_slug_definition_is_the_same_pattern(loaded):
    """The sibling test above holds the slug's *description* equal across the schemas that state
    it, which is the half a reader sees. This holds the *pattern* equal — the half that decides
    what validates. They were consistent when this was written, and nothing was keeping them so:
    the descriptions could stay identical while one schema quietly accepted a name the others
    refused, and every message about it would still read the same."""
    stated = {name: loaded[name]["$defs"]["slug"]["pattern"] for name in SLUG_HOLDERS}
    assert len(set(stated.values())) == 1, \
        f"the slug pattern differs across the schemas that state it: {stated}"


def test_the_scripts_and_the_schemas_agree_on_what_a_slug_is(loaded):
    """Four scripts compile the slug pattern and three schemas declare it, and until this test
    existed the seven copies were held together by nothing at all. A slug is the identity of a
    run, a node, a target and an initiative; two spellings of it in one framework is two answers
    to what a thing is called."""
    compiled = {}
    for name in ("run.py", "spec.py", "plan.py", "deliver.py"):
        source = (REPO / "src/claude/bin" / name).read_text(encoding="utf-8")
        line = next(l for l in source.splitlines() if l.startswith("SLUG = re.compile("))
        compiled[name] = line.split('r"', 1)[1].rsplit('"', 1)[0]
    declared = {name: loaded[name]["$defs"]["slug"]["pattern"] for name in SLUG_HOLDERS}
    assert len(set(compiled.values()) | set(declared.values())) == 1, \
        f"the scripts and the schemas do not agree on what a slug is: {compiled} vs {declared}"


SHARED_DEFS = {
    "specNodeRef": ("plan-node.json", "delivery-node.json", "reconciliation.json"),
    "pin": ("delivery-node.json", "trace.json", "check.json"),
    "ruleRef": ("check.json", "delivery-node.json"),
}


@pytest.mark.parametrize("name,holders", sorted(SHARED_DEFS.items()))
def test_a_definition_stated_in_more_than_one_schema_validates_the_same_thing(name, holders,
                                                                              loaded):
    """These schemas are deliberately self-contained — no cross-file `$ref`, so a consumer can
    read one contract without resolving four. The cost of that choice is copies, and a copy is
    honest only while something compares them. `slug` already lost a clause in one of its holders
    once; these three carried the same risk with no guard at all.

    What is held equal is the half that decides validation: the type and the pattern. The
    descriptions are deliberately free to differ, because each says the same thing to a different
    reader — `ruleRef` warns against confusing it with a specification node exactly where that
    confusion is possible — and forcing one wording would strip the sentence that earns its place
    in one file to make it match a file where it does not."""
    stated = {holder: {k: v for k, v in loaded[holder]["$defs"][name].items()
                       if k != "description"}
              for holder in holders}
    first = stated[holders[0]]
    for holder in holders[1:]:
        assert stated[holder] == first, \
            f"`$defs/{name}` validates differently in {holders[0]} and {holder}: " \
            f"{first} vs {stated[holder]}"


def test_the_index_and_the_node_contract_name_the_same_passes(loaded):
    """`delivery.json`'s `ran` enum and `delivery-node.json`'s `passName` enum are two statements
    of one vocabulary, and the `ran` description names the risk itself: a name the node contract
    accepts and the index does not would make the derivation refuse an index for a review nobody
    could have written differently. The guard was deliver.py exiting 2 over its own derived
    output, which fires only where a record happens to use the diverging name."""
    index = loaded["delivery.json"]["properties"]["nodes"]["items"]["properties"]["ran"]["items"]
    node = loaded["delivery-node.json"]["$defs"]["passName"]
    assert index["enum"] == node["enum"], \
        f"the index accepts {index['enum']} and a record accepts {node['enum']}"
