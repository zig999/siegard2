"""The closed set of files a knowledge base derives, and nothing else.

R42 and R51 make a projection derived and never hand-edited, and R50 closes the
projection list at three. `graph.json` is the materialized graph rather than a projection, and
R42 names it alongside `index.md`.

This module exists so the list has one home. `bin/project_knowledge.py` writes these files
and `src/claude/hooks/reject-derived-write.py` refuses writes to them; two copies of the list
would drift, and the drift would be silent in the worst direction — a hook protecting a file the
materializer no longer produces, and not protecting one it does.

Names rather than paths: a knowledge root is wherever the governed repository put it, and the
hook is given a path to judge rather than a tree to scan.

Declared dependencies: none beyond the standard library.
"""

from __future__ import annotations

from pathlib import PurePosixPath

# Keyed by name relative to the knowledge root. `bin/project_knowledge.py` asserts that its
# own output keys equal this set, so adding a projection there without adding it here fails.
DERIVED_NAMES = frozenset({"graph.json", "index.md", "glossary.md", "context-map.md"})

# The directory a knowledge base lives under, as every fixture and the shipped skill use it.
# A file called `index.md` somewhere else in a repository is not a projection, and refusing a
# write to it would make the hook a nuisance rather than a guarantee.
KNOWLEDGE_DIR = "knowledge"


def is_derived(path: str) -> bool:
    """Whether `path` names a file the knowledge materializer owns.

    True only for a derived name sitting directly inside a `knowledge/` directory. Both halves
    matter: the name alone would catch an unrelated `index.md`, and the directory alone would
    catch every authored knowledge object.
    """
    parts = PurePosixPath(path.replace("\\", "/")).parts
    if len(parts) < 2:
        return False
    return parts[-1] in DERIVED_NAMES and parts[-2] == KNOWLEDGE_DIR
