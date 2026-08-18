"""The distribution is what src/claude says it is.

`dist/.claude/` is assembled from `src/claude/` by copying it, and until this module existed
nothing checked that the copy had happened. Every other test in this suite reads `src/claude`, so
a dist that had lost a file, kept a deleted one, or drifted a line would have passed the whole
suite and shipped anyway. This is the cheapest test here and the one that would have caught the
most embarrassing defect.

`dist/` is the shape of a consumer repository, not a directory of parts: `.claude/` lands as the
plugin, and `CLAUDE.md` beside it lands at the consumer's root. The rules file is authored at
`src/consumer/CLAUDE.md` and deliberately not under `src/claude/` — it governs work in the
repository that installs the framework rather than being installed by it, a CLAUDE.md inside the
plugin directory is loaded by nothing, and the copy that update-by-rsync kept planting there was
dead weight every consumer had to notice and delete.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "src/claude"
DIST = REPO / "dist/.claude"
MANIFEST = ".claude-plugin/plugin.json"


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
    """The consumer's rules load from their repository root; a copy inside `.claude/` is read by
    nothing — measured, not assumed — and every update-by-copy used to replant it."""
    assert not (SRC / "CLAUDE.md").exists(), \
        "src/claude/CLAUDE.md is back; the consumer rules are authored at src/consumer/CLAUDE.md"
    assert not (DIST / "CLAUDE.md").exists(), \
        "dist/.claude/CLAUDE.md is back; nothing loads a CLAUDE.md inside the plugin directory"


def test_the_consumer_rules_are_distributed_beside_the_plugin():
    authored = REPO / "src/consumer/CLAUDE.md"
    distributed = REPO / "dist/CLAUDE.md"
    assert authored.is_file(), "the consumer rules file is not authored"
    assert distributed.is_file(), \
        "dist/CLAUDE.md is missing; the consumer has no rules file to place at their root"
    assert authored.read_bytes() == distributed.read_bytes(), \
        "dist/CLAUDE.md drifted from src/consumer/CLAUDE.md; the assembly is a copy"


def test_every_skill_and_agent_the_suite_holds_is_distributed(trees):
    """The two lists this suite treats as one truth reach the consumer as one truth."""
    from test_agent_contract import AGENTS
    from test_skill_contract import SKILLS
    _, dist = trees
    for name in SKILLS:
        assert f"skills/{name}/SKILL.md" in dist, f"{name} is tested and not distributed"
    for name in AGENTS:
        assert f"agents/{name}.md" in dist, f"{name} is tested and not distributed"


# ------------------------------------------------ what the rules file has to have heard of

CONSUMER_RULES = REPO / "src/consumer/CLAUDE.md"


def test_the_rules_a_consumer_loads_name_every_skill_that_ships():
    """The one file in this framework that cannot report its own gaps.

    Every other artifact is held to something: a schema, a validator, a suite. These rules are
    held to nothing, and a session reading them has nothing to compare them against — so a skill
    that shipped without reaching this file is a skill no consumer has any reason to know exists,
    and nothing anywhere says so. That is not hypothetical: `/siegard-status`, `/siegard-archive`
    and `/siegard-standard` each shipped and each went unnamed here for releases, and `reference`
    shipped with its contract, its skill and its agent all acting on it while this file said
    nothing at all.

    Naming is the whole of what is checked. What each one does, and how much this file says about
    it, stays an author's judgment — mechanising that would only produce a file written to pass."""
    rules = CONSUMER_RULES.read_text(encoding="utf-8")
    shipped = sorted(p.name for p in (REPO / "src/claude/skills").iterdir() if p.is_dir())
    absent = [name for name in shipped if f"/{name}`" not in rules]
    assert absent == [], \
        f"{absent} ship as skills and the consumer's own rules never name them; a consumer " \
        f"reading these rules has no reason to know they exist"


def test_the_rules_a_consumer_loads_name_every_agent_that_ships():
    """The same guard one layer down. These rules tell a consumer which judgments are delegated
    and to whom — that is how a reader knows the binder never sees the cut it judges — so an agent
    named nowhere here is a guarantee nobody was told about."""
    rules = CONSUMER_RULES.read_text(encoding="utf-8")
    shipped = sorted(p.stem for p in (REPO / "src/claude/agents").glob("*.md"))
    absent = [name for name in shipped if f"`{name}`" not in rules]
    assert absent == [], \
        f"{absent} ship as agents and the consumer's own rules never name them"
