"""Test package for the Siegard framework.

The one job of this module is to put `scripts/` on the import path before any test module
loads. It lives here rather than in `support.py` because a path set up by a sibling module
only works while every test imports that sibling first — which held by accident of
alphabetical discovery order until `test_edge_table_agreement` sorted ahead of it and failed.
A package initializer runs before every module in the package, so the ordering is guaranteed
rather than lucky.

`make test` therefore runs discovery with the repository root as the top-level directory, so
these modules are imported as `tests.*` and this file runs first.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
