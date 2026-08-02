"""Frontmatter parsing for this repository's validators.

This module holds no rules: schemas hold the constraints, each validator holds its own
cross-file checks, and this module only parses and normalizes.

Named `frontmatter_lib` rather than `frontmatter` so it can never shadow, or be shadowed
by, the PyPI package of that name.

It sat in `src/claude/bin/` while the framework shipped executables, and moved here with
the last of them. What moved with it is only the parsing: the two roots it used to
export — `PLUGIN_ROOT` for the tree it shipped in and `INVOCATION_ROOT` for the caller's
files — meant something because the same file resolved paths from two different places
depending on who ran it. Generator-side there is one root, `generator_lib.REPO_ROOT`
owns it, and a second name for it would be the drift that pair was written to prevent.
`display` moved for the same reason: two functions of that name existed, one per root,
and only one root is left.

`foundation/0003` R31 obliges the *distribution* to ship a boundary validator over
knowledge objects, and this repository ships none today. When it does, that validator
needs frontmatter parsing in the shipped tree — deciding here what shape it takes would
be deciding for a component that does not exist.

Declared dependencies: PyYAML.
"""

from __future__ import annotations

import datetime as dt

from cli import cannot_run

try:
    import yaml
except ImportError:
    cannot_run("cannot run: PyYAML is not installed (pip install pyyaml)")


def normalize(value):
    """Render YAML native timestamps as the canonical strings the schemas expect.

    YAML resolves an unquoted `2026-07-29T16:33:28Z` to a datetime and an unquoted
    `2026-07-29` to a date. OKF's own example frontmatter is unquoted, so rejecting
    those would reject the form the spec documents. Normalizing here accepts both the
    quoted and unquoted forms while leaving each schema's pattern constraint meaningful.
    """
    if isinstance(value, dt.datetime):
        return value.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if isinstance(value, dt.date):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, dict):
        return {k: normalize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [normalize(v) for v in value]
    return value


def split_frontmatter(text: str) -> tuple[dict, str]:
    """Return (frontmatter mapping, body), or raise ValueError.

    Raises on a missing or unclosed fence, non-mapping frontmatter, and an empty body:
    every Siegard artifact class requires a body, and a file that is all frontmatter is
    a defect in each of them.
    """
    if not text.startswith("---\n"):
        raise ValueError("file does not begin with a '---' frontmatter fence")
    end = text.find("\n---\n", 3)
    if end == -1:
        raise ValueError("frontmatter fence is never closed")
    data = yaml.safe_load(text[4 : end + 1])
    if not isinstance(data, dict):
        raise ValueError(f"frontmatter is {type(data).__name__}, expected a mapping")
    body = text[end + 5 :]
    if not body.strip():
        raise ValueError("file has frontmatter but no body")
    return normalize(data), body
