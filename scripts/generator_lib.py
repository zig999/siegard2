"""Roots and reporting for the generator's own scripts.

This module exists because of a name that meant two things. `frontmatter_lib.py` ships,
so its notion of a root is `Path(__file__).parent.parent` — the plugin root when a
consumer runs it, `src/claude/` when it runs from source. That is the only root a shipped
library can know. The generator's scripts resolve against the *repository*, and while
both trees were flat in `scripts/` the two roots coincided and nothing noticed.

They no longer coincide, and the coincidence was the bug: a generator script importing a
root from a shipped library depends on a value whose meaning changes with where the file
sits. So the generator owns its root here, and imports only parsing from the shipped tree.

`sys.path` reaches `src/claude/bin/` because the dependency runs one way — the generator
builds on the product's libraries, and nothing in the product imports from `scripts/`.

Declared dependencies: none beyond the standard library.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SHIPPED_BIN = REPO_ROOT / "src" / "claude" / "bin"

if str(SHIPPED_BIN) not in sys.path:
    sys.path.insert(0, str(SHIPPED_BIN))


def display(path: Path) -> str:
    """Repo-relative path when the file lives in the repo, absolute otherwise.

    Validator roots are CLI arguments, so they can legitimately point outside the repo.
    """
    try:
        return str(Path(path).relative_to(REPO_ROOT))
    except ValueError:
        return str(path)
