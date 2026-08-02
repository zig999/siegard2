"""Shared plumbing for the framework test suite.

The suite runs on unittest from the standard library rather than on pytest. Every script in
this repository declares its dependencies and exits with a named error when one is missing; a
test suite that added a third dependency to run at all would make `make test` fail for a reason
unrelated to the framework.

This module used to carry more. Every knowledge test followed one shape — copy the fixture,
break exactly one thing, assert the validator names it — and the `KnowledgeCase` base class
that did the copying lived here, beside the `validate_knowledge` import it called. Both went
with `fixtures/`: this repository keeps none, so there is no tree to
copy and no shipped validator to run over one.

What is left is what the four modules that still import this actually used — a root and a
renderer — and both stay here rather than being copied into each, for the reason the harness
was extracted in the first place: four copies of one path are four chances to disagree about
where the repository starts.
"""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent


def render(data: dict, body: str) -> str:
    """Frontmatter mapping plus body, in the fenced form every Siegard artifact class uses."""
    return "---\n" + yaml.safe_dump(data, sort_keys=False, allow_unicode=True) + "---\n" + body
