"""Shared frontmatter plumbing for Siegard boundary validators.

Extracted when the third artifact class (Claude Code components) arrived, exactly as
scripts/validate_adrs.py recorded it would be. This module holds no rules: schemas hold
the constraints, each validator holds its own cross-file checks, and this module only
parses and formats.

Named `frontmatter_lib` rather than `frontmatter` so it can never shadow, or be
shadowed by, the PyPI package of that name.
"""

from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

try:
    import yaml
except ImportError:
    sys.exit("cannot run: PyYAML is not installed (pip install pyyaml)")


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


def display(path: Path) -> str:
    """Repo-relative path when the file lives in the repo, absolute otherwise.

    Validator roots are CLI arguments, so they can legitimately point outside the repo.
    """
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


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
