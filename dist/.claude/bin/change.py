#!/usr/bin/env python3
"""Open, inspect, close and abandon a change to the graph, from a command line.

Only the session belongs here. Creating, editing and deleting a node stays in Python — a node is
a frontmatter mapping and a body, and a shell is a poor place to hand one over. What a person
needs outside Python is the boundary of the work: begin it, see what it has touched so far, and
end it.

**Closing is where this earns its place.** The set of touched nodes does not survive the close, so
the moment it is cleared is the last moment anything can see it, and `close` prints it. A close
run from a script that discards the output has thrown away the answer the change was opened to
get.

**It refuses and never repairs.** A close over a graph that does not hold together prints every
disagreement and leaves the change open, because clearing the set would take with it the only
record of where to look. Abandoning is `discard`, which is a different statement and says so.

Usage:
    change.py open <knowledge-root> [--requirement=<id>]
    change.py status <knowledge-root>
    change.py close <knowledge-root>
    change.py discard <knowledge-root>

Exit:
    0  the command did what it was asked
    1  refused — a change is already open, none is open, or the graph does not hold together
    2  cannot run — the arguments are wrong, the root is not a directory, the contract is missing

`status` exits 0 whenever it can answer, whether or not a change is open. Not being in a change is
a state, not a failure, and a caller that needs to branch on it has the Python API.
"""

from __future__ import annotations

import sys
from pathlib import Path

import change_set
import check_knowledge
import graph_edit

CANNOT_RUN = 2
COMMANDS = ("open", "status", "close", "discard")


def option(name: str) -> str | None:
    """The value of `--name=value`, or None. Written as one token so that the positional
    arguments stay recoverable by dropping everything that starts with a dash."""
    prefix = f"--{name}="
    for argument in sys.argv[1:]:
        if argument.startswith(prefix):
            return argument[len(prefix):]
    return None


def report(held: list[str], verb: str) -> None:
    print(f"change {verb}: {len(held)} node(s) touched")
    for node_id in held:
        print(f"  {node_id}")


def main() -> int:
    positional = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(positional) != 2 or positional[0] not in COMMANDS:
        print(f"cannot run: expected <{'|'.join(COMMANDS)}> <knowledge-root> "
              f"[--requirement=<id>]", file=sys.stderr)
        return CANNOT_RUN
    command, root = positional[0], Path(positional[1])
    if not root.is_dir():
        print(f"cannot run: {root} is not a directory", file=sys.stderr)
        return CANNOT_RUN

    if command == "status":
        if not change_set.is_open(root):
            print(f"no change is open under {root}")
            return 0
        requirement = change_set.requirement_of(root)
        named = f" for {requirement}" if requirement else ""
        report(change_set.touched(root), f"open{named}")
        return 0

    if command == "open":
        try:
            graph_edit.open_change(root, option("requirement"))
        except change_set.ChangeError as refused:
            print(f"{refused}", file=sys.stderr)
            return 1
        requirement = change_set.requirement_of(root)
        print(f"change open under {root}" + (f" for {requirement}" if requirement else ""))
        return 0

    if command == "discard":
        try:
            report(change_set.discard_change(root), "discarded")
        except change_set.ChangeError as refused:
            print(f"{refused}", file=sys.stderr)
            return 1
        print("the graph is left as it stands; nothing is rolled back")
        return 0

    # close
    if not check_knowledge.contract_path().is_file():
        print(f"cannot run: {check_knowledge.contract_path()} is missing, so the graph cannot be "
              f"checked before the change closes", file=sys.stderr)
        return CANNOT_RUN
    try:
        report(graph_edit.close_change(root), "closed")
    except (graph_edit.GraphEditError, change_set.ChangeError) as refused:
        print(f"{refused}", file=sys.stderr)
        print("\nthe change is still open — repair the graph and close again, or `discard` it",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
