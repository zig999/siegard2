"""The distribution is what src/claude says it is.

`dist/.claude/` is assembled from `src/claude/` by copying it, and until this module existed
nothing checked that the copy had happened. Every other test in this suite reads `src/claude`, so
a dist that had lost a file, kept a deleted one, or drifted a line would have passed the whole
suite and shipped anyway. This is the cheapest test here and the one that would have caught the
most embarrassing defect.
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


def test_every_skill_and_agent_the_suite_holds_is_distributed(trees):
    """The two lists this suite treats as one truth reach the consumer as one truth."""
    from test_agent_contract import AGENTS
    from test_skill_contract import SKILLS
    _, dist = trees
    for name in SKILLS:
        assert f"skills/{name}/SKILL.md" in dist, f"{name} is tested and not distributed"
    for name in AGENTS:
        assert f"agents/{name}.md" in dist, f"{name} is tested and not distributed"
