#!/usr/bin/env python3
"""The set of nodes a change has touched, held for as long as the change is open.

A change is opened, every node written while it is open is recorded, and closing it clears the
set. What is recorded is the identifier and nothing else: not the operation, not the fields, not
the previous value. Which nodes a requirement moved is the question; what moved inside them is a
question the node itself answers, and recording it here would be a second copy that goes stale
the moment the node is written again.

**The operation is recoverable, so it is not stored.** An identifier computes to a path with no
lookup, so a recorded node with no file at its path was deleted and one with a file was created
or edited. Storing `created` beside it would be storing what the tree already says.

**This module is the mechanism, not the door.** It will record whatever it is handed and clear
whenever it is asked. Two policies live one layer up, in the module a human actually calls:

- that a node cannot be written outside an open change;
- that a change cannot be closed while the graph is incoherent — a dangling reference, a loop in
  containment, a gap naming nothing. "The change is finished" has to mean the graph closes, or
  the set is cleared and the incoherence stays with nobody holding a record of what to look at.

Putting either here would make the set depend on the domain contract, and then holding a list of
strings would require a schema to be present and current.

**What an empty set does not tell you.** It is written by the same call that writes the node, so
an empty set means either that nothing changed or that something changed without coming through
the door. This module cannot distinguish them, by construction, and nothing downstream should
read an empty set as proof that the graph is unchanged.

Declared dependencies: none beyond the standard library.
"""

from __future__ import annotations

import json
from pathlib import Path

# Under the knowledge root, so the state travels with the graph it describes, and dot-prefixed so
# it is not mistaken for a node — every `<kind>/<scope>/<slug>.md` under the root is one.
STATE_DIR = ".siegard"
STATE_FILE = "change.json"

# The directory ignores itself. The set is session state and is cleared when the change closes, so
# committing it is noise in every diff — and the knowledge root belongs to whoever installed the
# framework, whose `.gitignore` is not ours to edit.
SELF_IGNORING = "*\n"


class ChangeError(Exception):
    """A change could not be opened, recorded against, or closed."""


def _state_path(root: Path) -> Path:
    return Path(root) / STATE_DIR / STATE_FILE


def _load(root: Path) -> dict:
    path = _state_path(root)
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ChangeError(
            f"no change is open under {root}. A node is written inside a change or not at all, "
            f"so that what a requirement touched is known while it is being touched"
        ) from None
    except json.JSONDecodeError as broken:
        raise ChangeError(
            f"{path}: the open change is unreadable ({broken}). It is not repaired here — a "
            f"repair would invent a set of touched nodes, and an invented one is worse than none. "
            f"Discard the change and open a new one"
        ) from None
    if not isinstance(loaded, dict) or not isinstance(loaded.get("touched"), list):
        raise ChangeError(f"{path}: the open change does not hold a `touched` list")
    return loaded


def _save(root: Path, state: dict) -> None:
    directory = Path(root) / STATE_DIR
    directory.mkdir(parents=True, exist_ok=True)
    (directory / ".gitignore").write_text(SELF_IGNORING, encoding="utf-8")
    _state_path(root).write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def is_open(root: Path) -> bool:
    """Whether a change is open under this root."""
    return _state_path(root).is_file()


def requirement_of(root: Path) -> str | None:
    """What the open change was opened for, where the caller named it."""
    return _load(root).get("requirement")


def open_change(root: Path, requirement: str | None = None) -> None:
    """Begin a change. Every node written from now on is recorded until it is closed.

    Refused where one is already open. Two changes sharing one set is two changes where neither
    knows which nodes are its own, and the second to close would clear the first's record.
    """
    if not Path(root).is_dir():
        raise ChangeError(f"{root} is not a directory, so there is no graph to change")
    if is_open(root):
        held = touched(root)
        raise ChangeError(
            f"a change is already open under {root}, holding {len(held)} node(s). Close it, or "
            f"discard it if it was abandoned — opening a second would leave neither able to say "
            f"which nodes are its own"
        )
    state: dict = {"touched": []}
    if requirement is not None:
        state = {"requirement": requirement, "touched": []}
    _save(root, state)


def record(root: Path, node_id: str) -> None:
    """Note that this node was touched. Idempotent, and first-seen order is kept.

    Idempotent because the set answers *which* nodes moved, and a node written twice in one change
    moved once. Ordered because the order a change was made in is free to keep and occasionally
    tells a reader something; nothing depends on it.
    """
    state = _load(root)
    if node_id not in state["touched"]:
        state["touched"].append(node_id)
        _save(root, state)


def touched(root: Path) -> list[str]:
    """The nodes this change has touched so far."""
    return list(_load(root)["touched"])


def close_change(root: Path) -> list[str]:
    """Finish the change, clearing the set, and return what was cleared.

    The set does not survive, by design. It is returned because this call is the last moment
    anything can see it, and a caller that discards the return value has thrown away the answer
    to the question the change was opened to ask.

    Whether the graph is coherent enough to close is not decided here. See the module docstring.
    """
    held = touched(root)
    _discard(root)
    return held


def discard_change(root: Path) -> list[str]:
    """Abandon the change, clearing the set, and return what was cleared.

    Separate from `close_change` because a change that was abandoned and one that was finished
    leave the same empty state, and the caller is the only thing that knows which happened. It
    exists so that the way out of an abandoned change is a call rather than deleting the file by
    hand — a change nobody can leave through the door is a reason to stop using the door.
    """
    held = touched(root)
    _discard(root)
    return held


def _discard(root: Path) -> None:
    _state_path(root).unlink()
    directory = Path(root) / STATE_DIR
    ignore = directory / ".gitignore"
    if ignore.is_file():
        ignore.unlink()
    if directory.is_dir() and not any(directory.iterdir()):
        directory.rmdir()
