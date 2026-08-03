#!/usr/bin/env python3
"""Read and write one node of the graph, and nothing else.

This is the only module that opens a node file. Everything above it — the change session, the
door a human calls, whatever generates source — goes through these functions, so there is one
place where a node can be written and one place to put the guard that says a write is well
formed.

**What it knows is arithmetic, not vocabulary.** `dm.<kind>.<scope>.<slug>` becomes
`<kind>/<scope>/<slug>.md` and back, with no lookup and no index, and a kind that is itself a
scope takes one segment fewer. The rule is uniform — drop the `dm` and join the rest with `/` —
so this module never needs the list of kinds to compute a path. Whether `<kind>` is one of the
eight the profile closes is the contract's question, and the door is where the contract is
consulted.

That split is deliberate. A file layer that also validated against a contract would have to load
one, and then every read of a node would depend on a schema being present and current. Reading a
node in order to report that the schema is missing is worse than reading it.

**Three things it refuses**, and each is the same fact from a different side. The identifier in
the frontmatter must be the identifier being written; the kind in the frontmatter must be the
kind in the identifier; and the identifier must compute to the path it is being written at.
Every reference in the graph resolves by that arithmetic and by nothing else, so a write is the
only moment it can be broken, and this is the only place a write happens.

**What it does not do:** it does not validate against the domain contract, it does not record
anything in a change session, and it does not know that either exists. A caller that writes
through this module without recording has bypassed the door, and this module cannot tell.

Declared dependencies: PyYAML.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

# `dm.<kind>.<slug>` for a kind that is itself a scope, `dm.<kind>.<scope>.<slug>` for the rest.
# The kinds are not spelled here: which names are legal is the profile's to say, and this pattern
# only has to recognise the shape it can turn into a path.
SLUG = r"[a-z0-9]+(?:-[a-z0-9]+)*"
NODE_ID = re.compile(rf"^dm\.{SLUG}(?:\.{SLUG}){{1,2}}$")

FENCE = re.compile(r"^---\n(.*?)\n---\n", re.S)


class NodeIOError(Exception):
    """A node could not be read or written, or a write would break the arithmetic."""


def path_of(node_id: str) -> Path:
    """The path this identifier computes to, relative to the knowledge root.

    `dm.subdomain.sales` sits at `subdomain/sales.md`; `dm.definition.sales.order` sits at
    `definition/sales/order.md`. One rule covers both: drop the `dm` and join what is left.
    """
    if not NODE_ID.match(node_id or ""):
        raise NodeIOError(
            f"`{node_id}` is not of the form dm.<kind>.<slug> or dm.<kind>.<scope>.<slug>, so no "
            f"path computes from it"
        )
    return Path(*node_id.split(".")[1:]).with_suffix(".md")


def id_of(relative: Path | str) -> str:
    """The identifier a path computes to — the inverse of `path_of`, and checked against it."""
    parts = Path(relative).with_suffix("").parts
    if len(parts) not in (2, 3):
        raise NodeIOError(
            f"`{relative}` is not <kind>/<slug>.md or <kind>/<scope>/<slug>.md, so no identifier "
            f"computes from it"
        )
    node_id = "dm." + ".".join(parts)
    if not NODE_ID.match(node_id):
        raise NodeIOError(f"`{relative}` computes to `{node_id}`, which is not a well-formed identifier")
    return node_id


def exists(root: Path, node_id: str) -> bool:
    """Whether the graph holds this node. A caller distinguishes edit from create with this."""
    return (Path(root) / path_of(node_id)).is_file()


def read(root: Path, node_id: str) -> tuple[dict, str]:
    """This node's frontmatter and its body.

    The body is returned verbatim, including its trailing newline or the absence of one, because
    a caller that rewrites a node it did not mean to reformat should produce no diff.
    """
    path = Path(root) / path_of(node_id)
    if not path.is_file():
        raise NodeIOError(f"{path}: the graph holds no `{node_id}`")
    text = path.read_text(encoding="utf-8")
    match = FENCE.match(text)
    if not match:
        raise NodeIOError(f"{path}: carries no frontmatter fence")
    loaded = yaml.safe_load(match.group(1))
    if loaded is not None and not isinstance(loaded, dict):
        raise NodeIOError(f"{path}: the frontmatter is a {type(loaded).__name__}, not a mapping")
    return loaded or {}, text[match.end():]


def write(root: Path, node_id: str, frontmatter: dict, body: str) -> Path:
    """Write this node, refusing anything that would break the identifier arithmetic.

    Key order is the caller's: `yaml.safe_dump` is told not to sort, so a node read, altered in
    one field and written back keeps every other line where it was. A caller that builds a
    frontmatter dict from scratch owns the order it chose, and choosing a different one next time
    produces a diff nobody made.
    """
    if not isinstance(frontmatter, dict):
        raise NodeIOError(f"`{node_id}`: the frontmatter is a {type(frontmatter).__name__}, not a mapping")

    declared = frontmatter.get("id")
    if declared != node_id:
        raise NodeIOError(
            f"`{node_id}` is being written with an `id` of `{declared}`. The identifier is the path "
            f"and the path is the identifier; a node whose frontmatter names a different one "
            f"resolves to a file nobody can reach from it"
        )

    kind = node_id.split(".")[1]
    if frontmatter.get("type") != kind:
        raise NodeIOError(
            f"`{node_id}` names kind `{kind}` and the frontmatter declares "
            f"`{frontmatter.get('type')}`. The kind is in the identifier because the path is, and "
            f"the two cannot disagree"
        )

    path = Path(root) / path_of(node_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    front = yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True, default_flow_style=False)
    path.write_text(f"---\n{front}---\n{body}", encoding="utf-8")
    return path


def remove(root: Path, node_id: str) -> Path:
    """Delete this node's file, and any directory the deletion leaves empty.

    The empty directory matters because a path is derived rather than looked up: an empty
    `definition/sales/` says a scope exists that holds nothing, and the next reader cannot tell it
    from one whose contents were never written.
    """
    path = Path(root) / path_of(node_id)
    if not path.is_file():
        raise NodeIOError(f"{path}: the graph holds no `{node_id}`")
    path.unlink()
    parent = path.parent
    while parent != Path(root) and parent.is_dir() and not any(parent.iterdir()):
        parent.rmdir()
        parent = parent.parent
    return path


def every_node(root: Path) -> list[str]:
    """Every identifier the graph holds, in sorted order.

    Derived from the tree rather than from an index, for the reason nothing allocates an
    identifier: an index is a second home for what the paths already say, and the two drift.
    Files that do not compute to an identifier are skipped rather than reported — this module
    reports on a node it was asked for, and a caller that wants to know about strays asks for a
    check instead.
    """
    found = []
    for path in sorted(Path(root).rglob("*.md")):
        try:
            found.append(id_of(path.relative_to(root)))
        except NodeIOError:
            continue
    return found
