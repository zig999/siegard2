"""Roots and reporting for the generator's own scripts.

This module exists because of a name that meant two things. `frontmatter_lib.py` shipped,
so its notion of a root was `Path(__file__).parent.parent` — the plugin root when a
consumer ran it, `src/claude/` when it ran from source. That is the only root a shipped
library can know. The generator's scripts resolve against the *repository*, and while
both trees were flat in `scripts/` the two roots coincided and nothing noticed.

They stopped coinciding, and the coincidence was the bug: a generator script importing a
root from a shipped library depends on a value whose meaning changes with where the file
sits. So the generator owns its root here.

`src/claude/bin/` holds nothing now — the last shipped executable went with the generation
path, and `frontmatter_lib` and `cli` moved to `scripts/`, where every caller of theirs
already lived. This module therefore injects nothing onto `sys.path`: a script run as
`python3 scripts/<name>.py` gets `scripts/` at `sys.path[0]` from the interpreter, and the
suite puts it there in `tests/__init__.py`. Injecting a path for a directory that holds
nothing would assert that something ships.

Declared dependencies: none beyond the standard library.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def display(path: Path) -> str:
    """Repo-relative path when the file lives in the repo, absolute otherwise.

    Validator roots are CLI arguments, so they can legitimately point outside the repo.
    """
    try:
        return str(Path(path).relative_to(REPO_ROOT))
    except ValueError:
        return str(path)
