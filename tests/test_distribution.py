"""The distribution is what src/claude says it is.

`dist/.claude/` is assembled from `src/claude/` by copying it, and until this module existed
nothing checked that the copy had happened. Every other test in this suite reads `src/claude`, so
a dist that had lost a file, kept a deleted one, or drifted a line would have passed the whole
suite and shipped anyway. This is the cheapest test here and the one that would have caught the
most embarrassing defect.

`dist/` is the shape of a consumer repository, not a directory of parts: `.claude/` lands as the
plugin, and what `src/consumer/` authors lands beside it, at the consumer's root, for a person to
copy. The session rules are not among those: they ship inside the plugin at `hooks/rules.md` and
reach every session and every agent through the plugin's own hooks, so no `CLAUDE.md` is
authored for the consumer's root and none sits at the plugin's own root, where nothing loads it.
"""
from __future__ import annotations

import hashlib
import json
import re
import os
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "src/claude"
DIST = REPO / "dist/.claude"
MANIFEST = ".claude-plugin/plugin.json"
CONSUMER_ROOT = REPO / "src/consumer"


def shipped(tree: Path) -> dict[str, str]:
    """Every file the tree ships, by relative path, with the digest of its bytes. `__pycache__`
    is not shipped: it is a side effect of running the validators, and it is not in git."""
    return {
        p.relative_to(tree).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(tree.rglob("*"))
        if p.is_file() and "__pycache__" not in p.parts
    }


@pytest.fixture(scope="module")
def trees() -> tuple[dict[str, str], dict[str, str]]:
    assert DIST.is_dir(), f"{DIST} does not exist; the distribution has never been assembled"
    return shipped(SRC), shipped(DIST)


def test_the_distribution_holds_every_authored_file(trees):
    src, dist = trees
    missing = sorted(set(src) - set(dist))
    assert missing == [], \
        f"{missing} is authored and not distributed; a consumer installing this would get a " \
        f"framework whose skills cite paths their plugin root does not hold"


def test_the_distribution_holds_nothing_else(trees):
    src, dist = trees
    extra = sorted(set(dist) - set(src))
    assert extra == [], \
        f"{extra} is distributed and not authored; a file nothing authors is a file nothing " \
        f"validates, and this suite reads src/claude"


def test_every_distributed_file_is_the_authored_file(trees):
    src, dist = trees
    drifted = sorted(p for p in set(src) & set(dist) if src[p] != dist[p])
    assert drifted == [], \
        f"{drifted} differ between src/claude and dist/.claude; the assembly is a copy, and a " \
        f"copy that diverged means the distribution is a version nobody authored"


def test_the_manifest_satisfies_its_contract():
    schema = json.loads((REPO / "schemas/plugin.json").read_text(encoding="utf-8"))
    manifest = json.loads((SRC / MANIFEST).read_text(encoding="utf-8"))
    problems = [e.message for e in Draft202012Validator(schema).iter_errors(manifest)]
    assert problems == [], f"the plugin manifest: {problems}"


def test_the_version_is_set_and_is_one_value():
    src = json.loads((SRC / MANIFEST).read_text(encoding="utf-8"))
    dist = json.loads((DIST / MANIFEST).read_text(encoding="utf-8"))
    assert src["version"] == dist["version"], \
        "the two manifests name different versions; a plugin without one version has none"
    assert src["name"] == dist["name"] == "siegard"


def test_the_plugin_ships_no_claude_md():
    """A CLAUDE.md at the plugin's own root is read by nothing — measured, not assumed — and one
    authored for the consumer's root would be a second copy of what the hooks place. The rules
    have one home, `hooks/rules.md`, and one carrier, `hooks/hooks.json`."""
    assert not (SRC / "CLAUDE.md").exists(), \
        "src/claude/CLAUDE.md is back; the rules are authored at src/claude/hooks/rules.md"
    assert not (DIST / "CLAUDE.md").exists(), \
        "dist/.claude/CLAUDE.md is back; nothing loads a CLAUDE.md inside the plugin directory"
    assert not (CONSUMER_ROOT / "CLAUDE.md").exists() and not (REPO / "dist/CLAUDE.md").exists(), \
        "a CLAUDE.md is authored for the consumer's root again; the hooks already place the rules"


def test_the_rules_marker_names_the_shipped_version():
    """The rules and the skills are two halves of one release; the marker line the rules open
    with is what a root copy is recognised and dated by, so it moves with the manifest. The
    pattern has one home, `project.py`, and this test reads it from there."""
    import project
    manifest = json.loads((SRC / MANIFEST).read_text(encoding="utf-8"))
    found = project.RULES_MARKER.search((SRC / "hooks/rules.md").read_text(encoding="utf-8"))
    assert found is not None, "src/claude/hooks/rules.md carries no version marker"
    assert found.group(1) == manifest["version"], \
        f"the rules say Siegard {found.group(1)} and the manifest says {manifest['version']}; " \
        f"shipping is what sets both, and it set one"


def beside_the_plugin() -> tuple[dict[str, bytes], dict[str, bytes]]:
    """What is authored for the consumer's own root, and what the distribution puts there.

    Written as a set rather than as one named file: the rules file was the only thing that landed
    beside the plugin for as long as it was the only thing authored, and a second one added later
    would have shipped nowhere with nothing saying so. `.claude/` is excluded because it is the
    plugin, held to its own tests above."""
    dist = REPO / "dist"
    authored = {p.relative_to(CONSUMER_ROOT).as_posix(): p.read_bytes()
                for p in sorted(CONSUMER_ROOT.rglob("*")) if p.is_file()}
    distributed = {p.relative_to(dist).as_posix(): p.read_bytes()
                   for p in sorted(dist.rglob("*"))
                   if p.is_file() and p.relative_to(dist).parts[0] != ".claude"}
    return authored, distributed


def test_everything_authored_for_the_consumer_root_is_distributed_there():
    authored, distributed = beside_the_plugin()
    assert sorted(authored) == sorted(distributed), \
        f"authored {sorted(authored)} and distributed {sorted(distributed)} beside the plugin; a " \
        f"file authored for the consumer's root and not shipped reaches nobody, and one shipped " \
        f"and not authored is a file nothing here validates"
    drifted = sorted(name for name in authored if authored[name] != distributed[name])
    assert drifted == [], \
        f"{drifted} drifted from src/consumer/; the assembly is a copy"


def test_a_consumer_root_script_is_distributed_runnable():
    """A script a person is told to run, shipped without its executable bit, is a script whose
    first answer is `Permission denied` and whose second is a chmod nothing documents."""
    for name in sorted(beside_the_plugin()[0]):
        if not name.endswith(".sh"):
            continue
        for tree in (CONSUMER_ROOT, REPO / "dist"):
            assert os.access(tree / name, os.X_OK), f"{tree / name} is not executable"


def test_every_skill_and_agent_the_suite_holds_is_distributed(trees):
    """The two lists this suite treats as one truth reach the consumer as one truth."""
    from test_agent_contract import AGENTS
    from test_skill_contract import SKILLS
    _, dist = trees
    for name in SKILLS:
        assert f"skills/{name}/SKILL.md" in dist, f"{name} is tested and not distributed"
    for name in AGENTS:
        assert f"agents/{name}.md" in dist, f"{name} is tested and not distributed"


# ------------------------------------------------ the storefront the plugin installs from

MARKETPLACE = REPO / ".claude-plugin/marketplace.json"


@pytest.fixture(scope="module")
def marketplace() -> dict:
    assert MARKETPLACE.is_file(), \
        f"{MARKETPLACE} does not exist; without a marketplace there is nothing for a consumer " \
        f"to add once and receive updates from"
    return json.loads(MARKETPLACE.read_text(encoding="utf-8"))


def test_the_marketplace_satisfies_its_contract(marketplace):
    schema = json.loads((REPO / "schemas/marketplace.json").read_text(encoding="utf-8"))
    problems = [e.message for e in Draft202012Validator(schema).iter_errors(marketplace)]
    assert problems == [], f"the marketplace file: {problems}"


def test_the_marketplace_entry_is_the_plugin_that_ships(marketplace):
    """The entry restates two facts the manifest owns — name and description — and the harness
    reads the version from the manifest alone, so what this test pins is the whole of what could
    disagree: the restated facts are equal, and the source resolves to the assembled plugin."""
    manifest = json.loads((SRC / MANIFEST).read_text(encoding="utf-8"))
    entry = marketplace["plugins"][0]
    assert entry["name"] == manifest["name"], \
        f"the marketplace distributes {entry['name']} and the manifest names " \
        f"{manifest['name']}; an install under one name reports back under the other"
    assert entry["description"] == manifest["description"], \
        "the entry's description drifted from the manifest's; one identity, two prose homes"
    assert (REPO / entry["source"]).resolve() == DIST.resolve(), \
        f"the entry's source {entry['source']} does not resolve to the assembled plugin at " \
        f"{DIST}; a consumer would install a tree this suite never validated"
    assert "version" not in entry, \
        "the entry restates the version; it has one home, the plugin manifest, and the update " \
        "check reads it there"


# ------------------------------------------------ what the rules file may name

CONSUMER_RULES = SRC / "hooks/rules.md"


def test_every_skill_the_rules_name_ships():
    """The rules file carries what binds a session outside a skill — the routes and the
    session-wide rules — and names an entry point only where a route runs through it. The
    catalog of what ships is the skills' own descriptions, which the harness loads in every
    session; this file is not a second copy of it. What is checked is the other direction: a
    route naming a skill nobody ships is a route a consumer cannot take."""
    rules = CONSUMER_RULES.read_text(encoding="utf-8")
    shipped = {p.name for p in (REPO / "src/claude/skills").iterdir() if p.is_dir()}
    named = set(re.findall(r"`/([a-z][a-z0-9-]*)`", rules))
    assert named <= shipped, \
        f"{sorted(named - shipped)} are named as entry points by the consumer rules and ship " \
        f"as no skill"


def test_the_rules_name_no_agent():
    """Which judgment is delegated to whom is each skill's own statement, made where the
    delegation happens. An agent named in the rules would be a description of a delegation
    held apart from the skill that performs it, and the two would drift."""
    rules = CONSUMER_RULES.read_text(encoding="utf-8")
    shipped = sorted(p.stem for p in (REPO / "src/claude/agents").glob("*.md"))
    named = [name for name in shipped if f"`{name}`" in rules]
    assert named == [], f"{named} are named by the consumer rules; the delegating skill is their home"
