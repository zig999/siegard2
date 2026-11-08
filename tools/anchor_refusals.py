#!/usr/bin/env python3
"""Write each refusal an api contract repeats once, under a YAML anchor, and alias it elsewhere.

«A refusal two operations answer alike is written once, under a YAML anchor, and named by alias
at its place in each operation's list» (SPEC-003 §Contract). This rewrites a contract's
frontmatter so every refusal that appears more than once is held by one object, which the dumper
writes as `&refusal-N` at its first place and `*refusal-N` at every later one; each operation's
order is untouched. The body is kept byte for byte. A file is written only where its reading —
`spec.reading_of`, the frontmatter as data and the body as bytes — is identical before and after,
so the change is form alone and `trace.py --carry` restamps what it moved.

Usage:
    python3 tools/anchor_refusals.py <specification-root> [--write]

Without `--write` it reports, per contract, the characters before and after and writes nothing.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src/claude/bin"))
import spec  # noqa: E402


class AnchorDumper(yaml.SafeDumper):
    """Names an anchor for what it is, so a reader sees `*refusal-3` and not `*id003`."""

    count = 0

    def generate_anchor(self, node):
        AnchorDumper.count += 1
        return f"refusal-{AnchorDumper.count}"


def anchored(front: dict) -> tuple[dict, int]:
    """The same frontmatter with every repeated refusal held by one object, and how many."""
    held: dict[str, dict] = {}
    seen: dict[str, int] = {}
    for answer in front.get("answers") or []:
        for refusal in answer.get("refusals") or []:
            key = json.dumps(refusal, sort_keys=True)
            seen[key] = seen.get(key, 0) + 1
    for answer in front.get("answers") or []:
        refusals = answer.get("refusals")
        if not isinstance(refusals, list):
            continue
        for index, refusal in enumerate(refusals):
            key = json.dumps(refusal, sort_keys=True)
            if seen[key] > 1:
                refusals[index] = held.setdefault(key, refusal)
    return front, sum(1 for n in seen.values() if n > 1)


def convert(path: Path) -> tuple[bytes, bytes, int] | None:
    old = path.read_bytes()
    before = spec.reading_of(old)
    front, body, problem = spec.parse_node(path)
    if problem or before is None or not isinstance(front, dict) or front.get("type") != "api":
        return None
    front, shared = anchored(front)
    if not shared:
        return None
    AnchorDumper.count = 0
    dumped = yaml.dump(front, Dumper=AnchorDumper, sort_keys=False, allow_unicode=True,
                       width=100, default_flow_style=False)
    new = f"---\n{dumped}---\n{body}".encode("utf-8")
    if spec.reading_of(new) != before:
        raise SystemExit(f"refused: {path} would not keep its reading; nothing written")
    return old, new, shared


def main() -> int:
    args = sys.argv[1:]
    write = "--write" in args
    args = [a for a in args if a != "--write"]
    if len(args) != 1:
        print(__doc__.strip())
        return 2
    root = Path(args[0])
    total_old = total_new = 0
    for path in sorted((root / "contracts").rglob("*.md")):
        if path.name.endswith(".log.md"):
            continue
        done = convert(path)
        if done is None:
            continue
        old, new, shared = done
        total_old += len(old)
        total_new += len(new)
        print(f"{path.relative_to(root)}: {shared} refusal(s) anchored, "
              f"{len(old)} -> {len(new)} bytes")
        if write:
            path.write_bytes(new)
    print(f"\n{total_old} -> {total_new} bytes over the converted contracts"
          + ("" if write else "; nothing written (pass --write)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
