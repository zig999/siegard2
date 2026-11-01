#!/usr/bin/env python3
"""Record the person's own words that authorize what a session does next, and read them back.

A compaction leaves a session holding a summary of what the person said, never the words, and a
summary is the session's reading of them: a route resumed over it re-asks for an authorization the
person already gave. A recorded ask is the words themselves, on disk, under a digest — «A route
resumed after a compaction reads its authorization from a recorded ask, printed by `ask.py
--read`, in place of a summary of an earlier context: a recorded ask is the person's words, and a
summary is the session's.» (SPEC-010 R3) What the ask authorizes is still read from its words under
the session rules: «What an ask authorizes is read from its words under the session rules, and
recording it widens nothing.» (SPEC-010 R3)

**`--record` copies; it never edits.** «An ask is recorded by `bin/ask.py --record` to
`ask-<stamp>.md` under the telemetry root, its bytes the person's own words copied whole and never
edited, and is named by its path and its sha256 digest, which the script prints.» (SPEC-010 R1)
The text comes from a file or from stdin (`-`), byte for byte: no newline is added, trimmed or
normalized, so what the digest names is exactly what the person wrote. The digest is the first 16
hex characters of the sha256, the form a goal's objective file is named by. A path already taken
and an empty text are refused, and the file is written only after both pass.

**`--read` prints the ask verbatim, or refuses.** «`bin/ask.py --read` prints the newest recorded
ask, or the one named by path, verbatim beneath its path and digest, and refuses a digest named
beside it that the file no longer holds.» (SPEC-010 R2) The first line is `ask: <path> (sha256
<digest>)`; every byte after it is the file's. A digest that does not match prints a `refused:`
line and nothing of the text, because a text that changed since it was recorded is no longer the
words the digest named. The newest ask is the one whose stamp sorts last.

The telemetry root comes from `project.py`, run as a command, so `siegard.json` keeps its one
reader. The measure commits the telemetry root whole, so a recorded ask is committed with it.

Declared dependencies: none beyond the standard library (this script runs project.py, its
sibling, as a command).

Usage:  ask.py --record <project-root> --text-file <file|->
                                    write the text, verbatim, to ask-<stamp>.md under the
                                    telemetry root, then print its path and digest
        ask.py --read <project-root> [--path <file>] [--sha256 <digest>]
                                    print the newest recorded ask, or the one --path names,
                                    verbatim beneath its path and digest; --sha256 refuses a file
                                    that no longer holds that digest (16 hex characters, or 64)
        ask.py --help               print this text and stop
Exit:   0 recorded, or read
        1 refused: an empty text, a path taken, no ask recorded, a path that is no recorded ask,
          a digest that does not match, or a project declaring no telemetry root
        2 cannot run
"""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BIN = Path(__file__).resolve().parent
CANNOT_RUN = 2
REFUSED = 1
ASK_NAME = re.compile(r"^ask-\d{8}T\d{6}Z\.md$")
DIGEST_LENGTH = 16


class Refused(Exception):
    pass


class CannotRun(Exception):
    pass


def digest_of(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()[:DIGEST_LENGTH]


def telemetry_root(project_root: Path) -> Path:
    """The telemetry root `project.py` prints, read from its own line."""
    done = subprocess.run([sys.executable, "-B", str(BIN / "project.py"), str(project_root)],
                          capture_output=True, text=True)
    out = (done.stdout + done.stderr).rstrip("\n")
    if done.returncode != 0 or out.startswith("no project file") or "\nno project file" in out:
        raise Refused(f"project.py {project_root} did not resolve the project:\n{out}")
    for line in out.splitlines():
        if line.startswith("telemetry_root: "):
            return Path(line[len("telemetry_root: "):])
    raise Refused("siegard.json declares no telemetry_root — the ask is recorded under it; "
                  "/siegard-config declares it")


def read_text(source: str) -> bytes:
    if source == "-":
        return sys.stdin.buffer.read()
    path = Path(source)
    if not path.is_file():
        raise CannotRun(f"{source} is not a file")
    return path.read_bytes()


def record(project_root: Path, source: str) -> list[str]:
    content = read_text(source)
    if not content.strip():
        raise Refused(f"{source} holds no text — an ask is the person's words, and there are none")
    root = telemetry_root(project_root)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    written = root / f"ask-{stamp}.md"
    if written.exists():
        raise Refused(f"{written} exists — a recorded ask is never overwritten; record again in "
                      f"the next second")
    root.mkdir(parents=True, exist_ok=True)
    written.write_bytes(content)
    digest = digest_of(content)
    return [f"ask: {written} (sha256 {digest})",
            f"read: python3 -B {BIN / 'ask.py'} --read {project_root} --path {written} "
            f"--sha256 {digest}"]


def read(project_root: Path, named: str | None, digest: str | None) -> bytes:
    root = telemetry_root(project_root).resolve()
    if named is not None:
        path = Path(named)
        path = (path if path.is_absolute() else project_root / path).resolve()
        if path.parent != root or not ASK_NAME.match(path.name):
            raise Refused(f"{path} is no recorded ask — one is ask-<stamp>.md directly under the "
                          f"telemetry root {root}")
        if not path.is_file():
            raise Refused(f"{path} does not exist")
    else:
        held = sorted(p for p in root.glob("ask-*.md") if ASK_NAME.match(p.name)) \
            if root.is_dir() else []
        if not held:
            raise Refused(f"no ask is recorded under {root}")
        path = held[-1]
    content = path.read_bytes()
    full = hashlib.sha256(content).hexdigest()
    if digest is not None and digest.lower() not in (full, full[:DIGEST_LENGTH]):
        raise Refused(f"{path} hashes to sha256 {full[:DIGEST_LENGTH]}, not {digest} — the file "
                      f"changed since it was recorded, and what it holds is not the ask the "
                      f"digest names")
    return f"ask: {path} (sha256 {full[:DIGEST_LENGTH]})\n".encode("utf-8") + content


def take(args: list[str], flag: str) -> str | None:
    if flag not in args:
        return None
    at = args.index(flag)
    if at + 1 >= len(args) or (args[at + 1].startswith("--")):
        raise CannotRun(f"{flag} takes a value")
    value = args[at + 1]
    del args[at:at + 2]
    if flag in args:
        raise CannotRun(f"{flag} is named twice")
    return value


def main() -> int:
    args = sys.argv[1:]
    if "--help" in args:
        # The docstring is this script's one home of what it does and how it is called,
        # so `--help` prints that rather than a second copy of it that could drift.
        print(__doc__.strip())
        return 0
    try:
        recording = take(args, "--record")
        reading = take(args, "--read")
        source = take(args, "--text-file")
        named = take(args, "--path")
        digest = take(args, "--sha256")
        if args or (recording is None) == (reading is None):
            raise CannotRun("expected --record <project-root> --text-file <file|-> or --read "
                            "<project-root> [--path <file>] [--sha256 <digest>]"
                            + (f"; not understood: {' '.join(args)}" if args else ""))
        if recording is not None and (source is None or named or digest):
            raise CannotRun("--record takes --text-file, and neither --path nor --sha256")
        if reading is not None and source is not None:
            raise CannotRun("--read takes no --text-file")
        project_root = Path(recording or reading).resolve()
        if not project_root.is_dir():
            raise CannotRun(f"{project_root} is not a directory")
        if recording is not None:
            print("\n".join(record(project_root, source)))
        else:
            sys.stdout.buffer.write(read(project_root, named, digest))
            sys.stdout.flush()
    except CannotRun as refusal:
        print(f"cannot run: {refusal}", file=sys.stderr)
        return CANNOT_RUN
    except Refused as refusal:
        print(f"refused: {refusal}")
        return REFUSED
    return 0


if __name__ == "__main__":
    sys.exit(main())
