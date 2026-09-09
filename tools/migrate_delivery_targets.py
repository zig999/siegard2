"""Stamp `target` on every delivery record a consumer holds, once, for siegard 4.0.0.

A record written against siegard-delivery 3.x anchored every path it carries — `files`, `tests`,
`reviewed`, `standard.at` — at a target source root it never named. From 4.0.0 the record carries
the key `siegard.json`'s `targets` declares for that root, and `deliver.py` resolves each record
at its own root rather than at the one the invocation happened to name. A record without the key
does not satisfy the contract, so a consumer updating across the major runs this once.

The key is derived, never asked, in the order the evidence deserves:

1. the files: every path the record lists exists under exactly one declared root;
2. the standard: `standard.at` resolves under exactly one declared root;
3. the siblings: every decided record in the same delivery root agrees on one key;
4. otherwise the record is undecided, and this script names it and writes nothing.

Where the files decide one root and the standard resolves under another, the files win — a
record written from the wrong target root spells its standard relative to that wrong root — and
`standard.at` is respelled relative to the root the files name. Every respelling is reported.

The rewrite is textual: one `target: <key>` line inserted directly under the opening `---`, one
`at:` line replaced where a respelling is owed, and nothing else touched — re-dumping the
frontmatter would reformat every line and bury the change the review exists to see. A record
already carrying `target` is left alone, so running twice is running once.

Inserting a line changes an implementation's bytes, and every proof pins the SHA-256 of the
implementation it demonstrates. So every proof whose implementation this run rewrites is re-pinned
to the digest that implementation's new text hashes to — computed in memory, never by reading a
file this run already wrote. A proof whose pin was already stale before this run touched anything
is left as it was and reported: restating it is a deliberate act the skill owns, not a side effect
of a migration.

All or nothing, and decided before anything is written: an undecided record, a proof already
stale, or one this script cannot re-pin stops the whole run and writes nothing. A dry run reports
every one of these exactly as `--write` would meet them, because both derive the same texts and
pins from the tree as it stands; only `--write` puts them on disk.

Deliberately not distributed — it sits outside `src/claude/`, so no assembly ships it, and a
consumer who has migrated has no further use for it. Run it from the consumer's project root:

    python3 -B <this repository>/tools/migrate_delivery_targets.py <project-root> [--write]

Without `--write` it reports what it would do and touches nothing.

Exit:   0 nothing left to do, or every record stamped and every owed proof re-pinned
        1 nothing written: an undecided record, an unreadable one, a malformed rewrite, or a
          proof already stale or unreadable before this run touched anything
        2 cannot run
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path

CANNOT_RUN = 2

try:
    import yaml
except ImportError:  # pragma: no cover - exercised by the environment, not the suite
    print("cannot run: PyYAML is required (pip install pyyaml)", file=sys.stderr)
    raise SystemExit(CANNOT_RUN)
KINDS = ("implementation", "proof", "review")


def pin_of(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def split(text: str) -> tuple[str, str] | None:
    """The frontmatter's text and the rest, or None where the file does not open on `---`."""
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end < 0:
        return None
    return text[4:end + 1], text[end + 1:]


def paths_of(front: dict) -> list[str]:
    out: list[str] = []
    for key in ("files", "tests"):
        for entry in front.get(key) or []:
            if isinstance(entry, dict):
                value = entry.get("path", entry.get("file"))
                if isinstance(value, str):
                    out.append(value)
    out += [p for p in (front.get("reviewed") or []) if isinstance(p, str)]
    return out


def roots_holding(paths: list[str], roots: dict[str, Path]) -> list[str]:
    if not paths:
        return []
    return [key for key, root in roots.items()
            if all((root / p).exists() for p in paths)]


def roots_resolving(at: str | None, roots: dict[str, Path]) -> list[str]:
    if not isinstance(at, str) or not at or Path(at).is_absolute():
        return []
    return [key for key, root in roots.items() if (root / at).is_file()]


class Record:
    def __init__(self, path: Path, home: Path):
        self.path = path
        self.name = path.relative_to(home).as_posix()
        self.text = path.read_text(encoding="utf-8")
        parts = split(self.text)
        self.front: dict = {}
        self.broken = parts is None
        if parts is not None:
            try:
                loaded = yaml.safe_load(parts[0])
            except yaml.YAMLError:
                loaded = None
            if isinstance(loaded, dict):
                self.front = loaded
            else:
                self.broken = True
        self.key: str | None = None
        self.how = ""
        self.respell: tuple[str, str] | None = None

    @property
    def stamped(self) -> bool:
        return "target" in self.front

    @property
    def standard_at(self) -> str | None:
        declared = self.front.get("standard")
        return declared.get("at") if isinstance(declared, dict) else None


def decide(record: Record, roots: dict[str, Path]) -> None:
    by_files = roots_holding(paths_of(record.front), roots)
    by_standard = roots_resolving(record.standard_at, roots)
    if len(by_files) == 1:
        record.key, record.how = by_files[0], "files"
        if by_standard and record.key not in by_standard:
            at = record.standard_at
            assert at is not None
            standing = roots[by_standard[0]] / at
            corrected = Path(os.path.relpath(standing.resolve(),
                                             roots[record.key].resolve())).as_posix()
            record.respell = (at, corrected)
        return
    if len(by_standard) == 1:
        record.key, record.how = by_standard[0], "standard"


def decide_by_siblings(records: list[Record]) -> None:
    """A key every other decided record in this delivery root agrees on — including one already
    carrying `target` from an earlier run, since a root migrated in two passes is the exact state
    an UNDECIDED record's own remedy produces: fix it by hand, then run again."""
    keys = {r.key for r in records if r.key is not None}
    keys |= {r.front["target"] for r in records
            if r.stamped and isinstance(r.front.get("target"), str)}
    if len(keys) != 1:
        return
    (key,) = keys
    for record in records:
        if record.key is None and not record.stamped and not record.broken:
            record.key, record.how = key, "siblings"


def stamped_text(record: Record) -> str:
    text = record.text
    if record.respell is not None:
        old, new = record.respell
        pattern = re.compile(r"^(\s*at:\s*)(['\"]?)" + re.escape(old) + r"\2\s*$", re.M)
        text, count = pattern.subn(lambda m: f"{m.group(1)}{new}", text, count=1)
        if count != 1:
            raise ValueError(f"{record.name}: the `at:` line spelling {old} was not found once")
    return f"---\ntarget: {record.key}\n" + text[4:]


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--write"]
    write = "--write" in sys.argv[1:]
    if len(args) != 1:
        print(__doc__.strip(), file=sys.stderr)
        return CANNOT_RUN
    home = Path(args[0]).resolve()
    declared_at = home / "siegard.json"
    if not declared_at.is_file():
        print(f"cannot run: {declared_at} does not exist", file=sys.stderr)
        return CANNOT_RUN
    try:
        declared = json.loads(declared_at.read_text(encoding="utf-8"))
    except json.JSONDecodeError as broken:
        print(f"cannot run: {declared_at} is not JSON: {broken}", file=sys.stderr)
        return CANNOT_RUN
    targets = declared.get("targets") if isinstance(declared, dict) else None
    if not isinstance(targets, dict) or not targets:
        print(f"cannot run: {declared_at} declares no targets", file=sys.stderr)
        return CANNOT_RUN
    roots = {key: home / path for key, path in targets.items() if isinstance(path, str)}
    named_delivery_root = declared.get("delivery_root") if isinstance(declared, dict) else None
    if not isinstance(named_delivery_root, str):
        print(f"cannot run: {declared_at} declares no delivery_root; an absent field is a stop, "
              f"never a guess", file=sys.stderr)
        return CANNOT_RUN
    delivery_root = home / named_delivery_root
    if not delivery_root.is_dir():
        print(f"cannot run: delivery root {delivery_root} is not a directory", file=sys.stderr)
        return CANNOT_RUN

    by_root: dict[Path, list[Record]] = {}
    for slug in sorted(p for p in delivery_root.iterdir() if p.is_dir()):
        records: list[Record] = []
        for kind in KINDS:
            for path in sorted((slug / kind).rglob("*.md")):
                records.append(Record(path, home))
        by_root[slug] = records

    broken = [r for records in by_root.values() for r in records if r.broken]
    for records in by_root.values():
        for record in records:
            if not record.broken and not record.stamped:
                decide(record, roots)
        decide_by_siblings(records)

    pending = [r for records in by_root.values() for r in records
               if not r.broken and not r.stamped]
    undecided = [r for r in pending if r.key is None]
    decided = [r for r in pending if r.key is not None]
    already = sum(1 for records in by_root.values() for r in records if r.stamped)

    verb = "to stamp" if write else "that would be stamped"
    counts = {how: sum(1 for r in decided if r.how == how)
              for how in ("files", "standard", "siblings")}
    print(f"{len(decided)} record(s) {verb} ({counts['files']} by files, "
          f"{counts['standard']} by standard, {counts['siblings']} by siblings); "
          f"{already} already carry target; {len(undecided)} undecided; {len(broken)} unreadable")
    for record in decided:
        if record.respell is not None:
            print(f"  respell {record.name}: standard.at {record.respell[0]} -> "
                  f"{record.respell[1]} (files stand under {record.key})")
    for record in broken:
        print(f"  UNREADABLE {record.name}: no frontmatter between `---` lines")
    for record in undecided:
        paths = paths_of(record.front)
        print(f"  UNDECIDED {record.name}: {len(paths)} path(s), none of them under one root; "
              f"standard.at {record.standard_at!r} resolves under none; siblings do not agree. "
              f"Add `target: <key>` by hand, then run again")
    if undecided or broken:
        print("nothing written: every record decides, or none is touched")
        return 1
    if not decided:
        print("nothing to do")
        return 0

    # Every one of these reads the tree as it stands, unmodified, and every text this run would
    # write is computed here — a proof's re-pin is hashed from the stamped text in memory, never
    # from a file this run already wrote. So a dry run reports exactly what --write would do,
    # and --write itself either writes everything or, on a single bad record, nothing at all.
    by_name = {r.name: r for records in by_root.values() for r in records}
    texts: dict[str, str] = {}
    malformed: list[tuple[str, str]] = []
    for record in decided:
        try:
            texts[record.name] = stamped_text(record)
        except ValueError as broken_text:
            malformed.append((record.name, str(broken_text)))

    stale: list[tuple[str, str, str]] = []
    unread: list[str] = []
    repins: dict[str, str] = {}
    for record in decided:
        if "/proof/" not in record.name:
            continue
        implementation_name = record.name.replace("/proof/", "/implementation/", 1)
        implementation = by_name.get(implementation_name)
        if implementation is None or implementation.name not in texts:
            continue  # its implementation was not itself rewritten; nothing to re-pin
        # This record's own text is the one this run is about to write — the proof's `target`
        # stamp lives there too, and re-pinning from the pre-stamp text would silently drop it
        # the moment a caller writes this text over what the stamping pass just wrote.
        proof_text = texts[record.name]
        match = re.search(r"^implementation:\s*(['\"]?)(sha256:[0-9a-f]{64})\1\s*$",
                          proof_text, re.M)
        if match is None:
            unread.append(record.name)
            continue
        current = pin_of(implementation.path)
        if match.group(2) != current:
            stale.append((record.name, match.group(2), current))
            continue
        new_pin = "sha256:" + hashlib.sha256(
            texts[implementation.name].encode("utf-8")).hexdigest()
        texts[record.name] = (proof_text[:match.start(2)] + new_pin
                              + proof_text[match.end(2):])
        repins[record.name] = texts[record.name]

    for name, why in malformed:
        print(f"  MALFORMED {name}: {why}")
    for name, pinned, was in stale:
        print(f"  STALE {name}: pinned {pinned}, and the implementation stands at {was} before "
              f"this run touches it; restate it deliberately, or write the proof again — a "
              f"migration does not paper over a citation that was already wrong")
    for name in unread:
        print(f"  UNREAD {name}: its implementation is being rewritten and no `implementation:` "
              f"line holding one pin was found to re-stamp; fix it by hand first")
    if malformed or stale or unread:
        print("nothing written: every record's text and every proof's pin resolve cleanly, "
              "or none is touched")
        return 1

    if not write:
        print(f"would re-pin {len(repins)} proof(s)")
        print("dry run; pass --write to apply")
        return 0

    for record in decided:
        record.path.write_text(texts[record.name], encoding="utf-8")

    print(f"stamped {len(decided)} record(s); re-pinned {len(repins)} proof(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
