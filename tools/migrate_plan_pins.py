#!/usr/bin/env python3
"""Migrate a work root from the aggregate base pin to a digest per bound node (siegard-plan/2).

**This is not part of the distribution.** It sits under `tools/`, outside `src/claude/`, so no
assembly ships it. It exists once, for the change that made every persisted plan node
schema-invalid, and a consumer who has already migrated has no further use for it.

It does not contradict the rejection of a shipped `--repin` command. That rejection was of a
*command inside the framework* rewriting nodes that carry judgment — scripts derive, skills write.
This asks no judgment: which nodes a task binds is already written, and what it stamps is a value
the index already lists. Nothing here decides anything a binder would have decided.

**The rewrite is textual, not a YAML round-trip.** Re-dumping the frontmatter would reformat every
line of every task and leave a diff nobody can read, which defeats the review the migration exists
to be checked by. So the `nodes:` block is rebuilt in place and the `base:` line is dropped, and
every other byte of the file is left exactly as it was.

**A task whose binding names a node the base does not hold is refused, not guessed.** There is no
digest to stamp, and inventing one would put a value in the file that no `sha256sum` reproduces —
the one thing a pin must never be.

Usage:  tools/migrate_plan_pins.py <work-root> <knowledge-root> [--dry-run]
Exit:   0 migrated (or, with --dry-run, migratable)
        1 something is in the way; nothing was written
        2 cannot run
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src/claude/bin"))

try:
    import yaml
except ImportError:  # pragma: no cover
    print("cannot run: PyYAML is required (pip install pyyaml)", file=sys.stderr)
    raise SystemExit(2)

import graph  # noqa: E402  - the path is set above, the way a consumer runs the shipped scripts

FENCE = re.compile(r"^---\n(.*?)\n---\n", re.S)
BLOCK_ITEM = re.compile(r"^\s*-\s+(\S+)\s*$")


def frontmatter(text: str) -> tuple[dict, int, int] | None:
    """The parsed frontmatter and the span it occupies, or None where there is no fence."""
    match = FENCE.match(text)
    if not match:
        return None
    try:
        front = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return None
    return (front, match.start(1), match.end(1)) if isinstance(front, dict) else None


def rewrite(text: str, digests: dict[str, str]) -> tuple[str, list[str], list[str]]:
    """One task's text with its binding stamped and its `base` line dropped. Returns the new text,
    the nodes stamped, and whatever stood in the way."""
    parsed = frontmatter(text)
    if parsed is None:
        return text, [], ["carries no frontmatter this script can read"]
    front, start, end = parsed
    if "base" not in front and all(isinstance(n, dict) for n in front.get("nodes") or []):
        return text, [], []  # already migrated

    bound = front.get("nodes") or []
    if not all(isinstance(n, str) for n in bound):
        return text, [], ["`nodes` is neither all identifiers nor already migrated"]
    missing = [n for n in bound if n not in digests]
    if missing:
        return text, [], [f"binds {', '.join(missing)}, which the base does not hold — "
                          f"there is no digest to stamp, and inventing one is the one thing a "
                          f"pin must never be"]

    lines = text[start:end].split("\n")
    out: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.rstrip() == "base:" or line.startswith("base: "):
            index += 1
            continue
        if line.rstrip() == "nodes:":
            out.append("nodes:")
            index += 1
            while index < len(lines) and BLOCK_ITEM.match(lines[index]):
                node = BLOCK_ITEM.match(lines[index]).group(1)
                out.append(f"  - node: {node}")
                out.append(f"    digest: {digests[node]}")
                index += 1
            continue
        out.append(line)
        index += 1

    rebuilt = text[:start] + "\n".join(out) + text[end:]
    check = frontmatter(rebuilt)
    if check is None:
        return text, [], ["the rewrite did not parse back; nothing written"]
    got = check[0].get("nodes") or []
    if [n.get("node") for n in got] != bound or "base" in check[0]:
        return text, [], ["the rewrite did not produce the binding it was given; nothing written"]
    return rebuilt, bound, []


def main(argv: list[str]) -> int:
    dry = "--dry-run" in argv
    roots = [a for a in argv if a != "--dry-run"]
    if len(roots) != 2:
        print(__doc__.strip().split("Usage:")[1].strip(), file=sys.stderr)
        return 2
    work, knowledge = Path(roots[0]), Path(roots[1])
    for root in (work, knowledge):
        if not root.is_dir():
            print(f"cannot run: {root} is not a directory", file=sys.stderr)
            return 2

    validator, allowed, obligations = graph.contract()
    nodes, problems = graph.collect(knowledge, validator, allowed, obligations)
    problems += graph.cross_problems(nodes)
    if problems:
        print(f"cannot run: the base at {knowledge} does not hold together "
              f"({len(problems)} problem(s)); fix it with graph.py first", file=sys.stderr)
        return 2
    digests = {nid: node["digest"] for nid, node in nodes.items()}

    tasks = sorted((work / "task").rglob("*.md")) if (work / "task").is_dir() else []
    if not tasks:
        print(f"{work} holds no task; nothing to migrate")
        return 0

    touched, skipped, blocked = [], [], []
    for path in tasks:
        text = path.read_text(encoding="utf-8")
        rebuilt, stamped, said = rewrite(text, digests)
        name = path.relative_to(work).with_suffix("").as_posix()
        if said:
            blocked.append(f"{name}: {said[0]}")
        elif not stamped and rebuilt == text:
            skipped.append(name)
        else:
            touched.append((name, len(stamped), path, rebuilt))

    for line in blocked:
        print(line, file=sys.stderr)
    if blocked:
        print(f"\n{len(blocked)} task(s) in the way; nothing was written", file=sys.stderr)
        return 1

    for name, count, path, rebuilt in touched:
        if not dry:
            path.write_text(rebuilt, encoding="utf-8")
        print(f"{name}: {count} digest(s) stamped, base removed")
    for name in skipped:
        print(f"{name}: already migrated")
    verb = "would migrate" if dry else "migrated"
    print(f"\n{verb} {len(touched)} task(s); {len(skipped)} already migrated. "
          f"Validate with plan.py, and read the diff.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
