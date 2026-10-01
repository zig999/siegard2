#!/usr/bin/env python3
"""Split a root `decision-log.md` into one log beside each node, once, for siegard 5.0.0.

Before 5.0.0 a specification held one decision log at its root, each entry naming the file it
filled under `location`. From 5.0.0 the log sits beside the node it discloses, `<slug>.log.md`
in the node's own directory, and an entry names only the `field` — the file beside it is the
location (SPEC-001 R9). A consumer updating across the major runs this once over its
specification root.

What it does, in order:

1. reads every YAML block of the root log — every stretch between `---` fences, not only the
   first, because a log appended to by hand can carry entries past its closing fence, and a
   reader of the first block alone would drop them silently;
2. groups the entries by `location`, drops the field, and writes `<location>.log.md` beside the
   node as the writer lays it out: one block per entry, every scalar on one line, no body;
3. refuses to continue unless the entries written equal the entries read, and prints both;
4. removes `decision-log.md` and `projections/decisions-by-node.md`;
5. runs `spec.py` over the root and prints its output — a log whose node is gone and whose
   last entry retires nothing is reported there, not repaired here: a tombstone is a decision
   about where the fact went, and this script decides nothing.

`--dry-run` prints what would be written and writes nothing.

Usage:  python3 tools/migrate_decision_log.py [--dry-run] <specification-root>
Exit:   0 migrated and the root is sound
        1 migrated and `spec.py` reports problems, or the counts disagree and nothing was written
        2 cannot run
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import OrderedDict
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
SPEC = REPO / "src" / "claude" / "bin" / "spec.py"
FENCE_LINE = re.compile(r"^---[ \t]*$", re.M)


ENTRY_START = re.compile(r"^(\s*)- ", re.M)


def blocks_of(text: str) -> list[object]:
    """Every YAML document the file holds, in order: each stretch between `---` lines that
    parses, whether it is the frontmatter mapping or a bare list left past the fence.

    A block that does not parse — a colon inside an unquoted scalar is the usual cause, in an
    entry typed by hand past the fence — is split at its entries and each is parsed alone, so
    the refusal names the lines of the file to repair rather than a position inside a block."""
    parsed: list[object] = []
    broken_at: list[str] = []
    line = 1
    for chunk in FENCE_LINE.split(text):
        first_line = line
        line += chunk.count("\n")
        if not chunk.strip():
            continue
        try:
            loaded = yaml.safe_load(chunk)
        except yaml.YAMLError:
            loaded = None
            starts = [m.start() for m in ENTRY_START.finditer(chunk)
                      if m.group(1) in ("", "  ")]
            for index, start in enumerate(starts):
                end = starts[index + 1] if index + 1 < len(starts) else len(chunk)
                piece = chunk[start:end]
                at = first_line + chunk[:start].count("\n")
                try:
                    yaml.safe_load(piece)
                except yaml.YAMLError as why:
                    said = re.sub(r"\s+", " ", str(why))
                    broken_at.append(f"  lines {at}-{at + piece.rstrip().count(chr(10))}: {said[:160]}")
        if loaded is not None:
            parsed.append(loaded)
    if broken_at:
        print(f"cannot run: {len(broken_at)} entry(ies) of the log do not parse as YAML; repair "
              f"them (usually a colon inside an unquoted scalar — quote the whole string) and "
              f"rerun; nothing written:", file=sys.stderr)
        for said in broken_at:
            print(said, file=sys.stderr)
        raise SystemExit(2)
    return parsed


def entries_of(blocks: list[object]) -> list[dict]:
    entries: list[dict] = []
    for block in blocks:
        if isinstance(block, dict):
            held = block.get("entries")
            entries += [e for e in held if isinstance(e, dict)] if isinstance(held, list) else []
        elif isinstance(block, list):
            entries += [e for e in block if isinstance(e, dict)]
    return entries


def entry_block(entry: dict) -> str:
    return yaml.safe_dump([entry], sort_keys=False, allow_unicode=True, width=float("inf"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("root", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    root: Path = args.root
    log = root / "decision-log.md"
    if not root.is_dir():
        print(f"cannot run: {root} is not a directory", file=sys.stderr)
        return 2
    if not log.is_file():
        print(f"cannot run: {log} does not exist; nothing to migrate", file=sys.stderr)
        return 2
    text = log.read_text(encoding="utf-8-sig")
    entries = entries_of(blocks_of(text))
    fences = len(FENCE_LINE.findall(text))
    print(f"read {len(entries)} entry(ies) from {log} across {fences} fence line(s)")

    grouped: "OrderedDict[str, list[dict]]" = OrderedDict()
    unlocated: list[dict] = []
    for entry in entries:
        location = entry.get("location")
        if not isinstance(location, str) or not location.endswith(".md"):
            unlocated.append(entry)
            continue
        grouped.setdefault(location, []).append({k: v for k, v in entry.items()
                                                 if k != "location"})
    if unlocated:
        print(f"cannot run: {len(unlocated)} entry(ies) carry no `location` ending in .md; "
              f"nothing written", file=sys.stderr)
        return 2
    targets = {location: root / (location[:-len(".md")] + ".log.md") for location in grouped}
    standing = [str(path) for path in targets.values() if path.exists()]
    if standing:
        print(f"cannot run: {len(standing)} target log(s) already exist — this migration runs "
              f"once; first: {standing[0]}", file=sys.stderr)
        return 2

    for location, held in grouped.items():
        print(f"  {targets[location].relative_to(root)}  <- {len(held)} entry(ies)")
    written = sum(len(held) for held in grouped.values())
    if written != len(entries):
        print(f"refused: {len(entries)} read, {written} would be written; nothing written")
        return 1
    if args.dry_run:
        print(f"dry run: {written} entry(ies) would land in {len(grouped)} log(s); nothing written")
        return 0

    for location, held in grouped.items():
        path = targets[location]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("---\nentries:\n" + "".join(entry_block(e) for e in held) + "---\n",
                        encoding="utf-8")
    check = sum(len(entries_of(blocks_of(path.read_text(encoding="utf-8"))))
                for path in targets.values())
    print(f"written {check} entry(ies) into {len(targets)} log(s)")
    if check != len(entries):
        print(f"refused: {len(entries)} read, {check} read back; the logs written stand for "
              f"inspection and the root log was not removed")
        return 1
    log.unlink()
    projection = root / "projections" / "decisions-by-node.md"
    if projection.exists():
        projection.unlink()
        print(f"removed {projection.relative_to(root)}")
    print(f"removed decision-log.md")

    done = subprocess.run([sys.executable, "-B", str(SPEC), str(root)],
                          capture_output=True, text=True)
    sys.stdout.write(done.stdout)
    sys.stderr.write(done.stderr)
    return 0 if done.returncode == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
