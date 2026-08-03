"""The exit-code convention every script in this repository documents.

Fourteen scripts state `Exit: ... 2 cannot run`, and every one of them reached that path
through `sys.exit("cannot run: ...")`. Passing a string to `sys.exit` prints it to stderr and
exits **1** — the same code those scripts use for "I ran, and what I checked is wrong". So the
documented distinction between a failed check and an environment that cannot run the check did
not exist in any of them.

`make validate` never noticed, because it treats any non-zero as a failure. That is exactly why
it was worth fixing rather than deleting from the docstrings: the distinction matters to a
caller that has to decide whether to report a defect or to install a dependency, and this
repository does not keep a stated contract that nothing honours.

Extracted for the same reason `frontmatter_lib` was — a convention shared by enough callers that
restating it in each one is how the copies start to drift.
"""

from __future__ import annotations

import sys
from typing import NoReturn

CANNOT_RUN = 2


def cannot_run(message: str) -> NoReturn:
    """Report an environment that cannot run this check, and exit 2.

    For a missing dependency, an absent root, or arguments that make no sense — never for a
    check that ran and found a problem. That is exit 1, and conflating the two tells a caller
    to fix the wrong thing.
    """
    print(message if message.startswith("cannot run") else f"cannot run: {message}", file=sys.stderr)
    raise SystemExit(CANNOT_RUN)
