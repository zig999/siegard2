"""Test package for the Siegard framework.

The one job of this module is to put both code trees on the import path before any test
module loads. It lives here rather than in `support.py` because a path set up by a sibling
module only works while every test imports that sibling first — which held by accident of
alphabetical discovery order until `test_edge_table_agreement` sorted ahead of it and failed.
A package initializer runs before every module in the package, so the ordering is guaranteed
rather than lucky.

Two trees, in the order the dependency runs. `src/claude/bin/` holds what the framework
ships; `scripts/` holds the generator that assembles it and imports from the first. The
suite tests both, so it reaches both, and the order matters only in that a name defined on
each side resolves to the generator's — which is the side that would be wrong to shadow.

`make test` therefore runs discovery with the repository root as the top-level directory, so
these modules are imported as `tests.*` and this file runs first.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src" / "claude" / "bin"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

# The two trees, named once. A test reaches for a schema, a scaffold, or an executable, and
# which tree holds it is the same question `CLAUDE.md` **Repository layout** answers with its
# `Reaches the consumer` column: `SHIPPED_*` is what a consumer installs, and the bare names
# are the generator's own.
SHIPPED_ROOT = REPO_ROOT / "src" / "claude"
SHIPPED_SCHEMAS = SHIPPED_ROOT / "schemas"
SHIPPED_BIN = SHIPPED_ROOT / "bin"
SHIPPED_TEMPLATES = SHIPPED_ROOT / "templates"
GENERATOR_SCHEMAS = REPO_ROOT / "schemas"
GENERATOR_SCRIPTS = REPO_ROOT / "scripts"
GENERATOR_TEMPLATES = REPO_ROOT / "templates"
