#!/usr/bin/env python3
"""Concatenate every file distributed under dist/ into one file under export/.

Each file is preceded by a header carrying its path relative to dist/, which is
treated as the root. Files are emitted in sorted path order so the output is
deterministic. Paths ignored by the repository (bytecode caches, Windows
Zone.Identifier metadata) are skipped.

Usage:
    python3 tools/export_dist.py [--dist DIR] [--out FILE]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DIST = REPO_ROOT / "dist"
DEFAULT_OUT = REPO_ROOT / "export" / "dist.txt"
RULE = "=" * 80


def is_skipped(rel: Path) -> bool:
    return "__pycache__" in rel.parts or rel.name.endswith(":Zone.Identifier")


def collect(dist: Path) -> list[Path]:
    files = [p for p in dist.rglob("*") if p.is_file()]
    return sorted(
        (p for p in files if not is_skipped(p.relative_to(dist))),
        key=lambda p: p.relative_to(dist).as_posix(),
    )


def render(dist: Path, files: list[Path]) -> str:
    parts: list[str] = []
    for path in files:
        rel = path.relative_to(dist).as_posix()
        body = path.read_text(encoding="utf-8")
        if body and not body.endswith("\n"):
            body += "\n"
        parts.append(f"{RULE}\n{rel}\n{RULE}\n{body}\n")
    return "".join(parts)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dist", type=Path, default=DEFAULT_DIST)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)

    dist = args.dist.resolve()
    if not dist.is_dir():
        print(f"error: {dist} is not a directory", file=sys.stderr)
        return 1

    files = collect(dist)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(render(dist, files), encoding="utf-8")
    print(f"{len(files)} files from {dist} -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
