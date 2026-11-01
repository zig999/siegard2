#!/usr/bin/env python3
"""Write text for a sibling project's session to a file, and confirm it from that session.

Text carried from one project's session to another's by copy and paste lands wherever it is
pasted: a session of the wrong project, or of another plugin version, reads it as its own, and a
file a session left in a scratch directory is gone when the other session needs it. A relay file
is the text on disk in the origin project, under a digest, headed by the one line that refuses it
anywhere but where it was meant to go.

**`--to` writes into the origin, never into the sibling.** «Text for a sibling project's session
is written by `bin/relay.py` to `relay-<stamp>-<sibling>.md` under the origin project's telemetry
root, and never into the sibling's repository.» (SPEC-010 R4) The file is:

    confirm: python3 -B "${CLAUDE_PLUGIN_ROOT}/bin/relay.py" --confirm <this file>
    root: <the sibling's root>
    version: <the plugin version the receiving session must run>
    from: <the origin's root>
    sha256: <the text's digest>

    <the text, verbatim>

The sibling's root is where its `siegard.json` sits, as `project.py` resolves it, and the
version is the one in the plugin manifest `project.py` reads. The text is copied byte for byte
from a file or from stdin (`-`); its digest is the first 16 hex characters of its sha256. «A
sibling that declares no `siegard.json`, or that resolves to the origin project itself, is refused
and nothing is written.» (SPEC-010 R4) It prints the file's path and the line to paste into the
sibling's session.

**`--confirm` runs in the receiving session, from its own working directory.** «`bin/relay.py
--confirm` prints the relay's text only where the session running it is in the sibling's
project, as `project.py` resolves the working directory, runs the plugin version the relay names,
and holds the text the relay's digest names.» (SPEC-010 R5) The first line is `confirmed` or
`refuses`; `checked:` and `refused:` lines follow, one per check, and under `confirmed` the text
follows a `text:` line, verbatim. Under `refuses` nothing of the text is printed: a text read in
the wrong project is the act the refusal exists to prevent.

Every project root comes from `project.py`, run as a command, so `siegard.json` keeps its one
reader.

Declared dependencies: none beyond the standard library (this script imports project.py, its
sibling, and runs it as a command).

Usage:  relay.py --to <sibling-project-root> --from <project-root> --text-file <file|->
                                    write the text, verbatim, to relay-<stamp>-<sibling>.md under
                                    the origin's telemetry root, then print its path and the line
                                    the sibling's session runs
        relay.py --confirm <relay-file>
                                    from the receiving session's working directory: print the
                                    text where this is the sibling's project, the plugin runs the
                                    version named and the digest holds, or refuse
        relay.py --help             print this text and stop
Exit:   0 written, or confirmed
        1 refused, with every reason
        2 cannot run
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BIN = Path(__file__).resolve().parent
sys.path.insert(0, str(BIN))

import project  # noqa: E402

CANNOT_RUN = 2
REFUSED = 1
DIGEST_LENGTH = 16
HEADER = ("confirm", "root", "version", "from", "sha256")


class Refused(Exception):
    pass


class CannotRun(Exception):
    pass


def digest_of(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()[:DIGEST_LENGTH]


def plugin_version() -> str:
    return json.loads(project.MANIFEST.read_text(encoding="utf-8"))["version"]


def resolve(directory: Path) -> tuple[Path, list[str]]:
    """Where the project's `siegard.json` sits and what `project.py` printed over it; a project
    that declares none, or whose file does not hold together, is refused."""
    done = subprocess.run([sys.executable, "-B", str(BIN / "project.py"), str(directory)],
                          capture_output=True, text=True)
    out = (done.stdout + done.stderr).rstrip("\n")
    home = project.toplevel_of(directory).resolve()
    if done.returncode != 0:
        raise Refused(f"project.py {directory} exits {done.returncode}: its siegard.json does not "
                      f"hold together\n{out}")
    if out.startswith("no project file") or "\nno project file" in out:
        raise Refused(f"{home} declares no siegard.json — a sibling is a project that declares "
                      f"its own")
    return home, out.splitlines()


def read_text(source: str) -> bytes:
    if source == "-":
        return sys.stdin.buffer.read()
    path = Path(source)
    if not path.is_file():
        raise CannotRun(f"{source} is not a file")
    return path.read_bytes()


def write(sibling: Path, origin: Path, source: str) -> list[str]:
    content = read_text(source)
    if not content.strip():
        raise Refused(f"{source} holds no text to relay")
    same = project.toplevel_of(origin).resolve()
    if project.toplevel_of(sibling).resolve() == same:
        raise Refused(f"--to and --from both resolve to {same} — a relay goes to another "
                      f"project; text for this one needs no relay")
    try:
        sibling_home, _ = resolve(sibling)
    except Refused as refusal:
        raise Refused(f"the sibling: {refusal}") from None
    origin_home, lines = resolve(origin)
    roots = [line[len("telemetry_root: "):] for line in lines
             if line.startswith("telemetry_root: ")]
    if not roots:
        raise Refused(f"{origin_home}/siegard.json declares no telemetry_root — the relay is "
                      f"written under it; /siegard-config declares it")
    telemetry = Path(roots[0])
    name = re.sub(r"[^A-Za-z0-9._-]+", "-", sibling_home.name).strip("-") or "sibling"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    written = telemetry / f"relay-{stamp}-{name}.md"
    if written.exists():
        raise Refused(f"{written} exists — a relay is never overwritten; relay again in the next "
                      f"second")
    confirm = f'python3 -B "${{CLAUDE_PLUGIN_ROOT}}/bin/relay.py" --confirm {written}'
    header = "\n".join([f"confirm: {confirm}", f"root: {sibling_home}",
                        f"version: {plugin_version()}", f"from: {origin_home}",
                        f"sha256: {digest_of(content)}"])
    telemetry.mkdir(parents=True, exist_ok=True)
    written.write_bytes(header.encode("utf-8") + b"\n\n" + content)
    return [f"relay: {written}",
            f"paste into the session of {sibling_home}: {confirm}"]


def confirm(relay: Path, here: Path) -> tuple[bool, list[str], bytes]:
    raw = relay.read_bytes()
    head, separator, content = raw.partition(b"\n\n")
    fields: dict[str, str] = {}
    for line in head.decode("utf-8", errors="replace").splitlines():
        key, _, value = line.partition(": ")
        fields[key] = value
    missing = [key for key in HEADER if not fields.get(key)]
    if not separator or missing:
        return False, [f"refused: {relay} is no relay file — its header lacks "
                       f"{', '.join(missing) or 'the blank line before the text'}"], b""
    said: list[str] = []
    refused = False
    expected = Path(fields["root"])
    try:
        home, _ = resolve(here)
        if home == expected.resolve():
            said.append(f"checked: this session's project is {home}, the relay's root")
        else:
            refused = True
            said.append(f"refused: this session's project is {home}, and the relay is for "
                        f"{expected} — paste the line into that project's session")
    except Refused as refusal:
        refused = True
        said.append(f"refused: this session's working directory {here} is no project the relay "
                    f"is for ({expected}): {refusal}")
    running = plugin_version()
    if running == fields["version"]:
        said.append(f"checked: the plugin runs {running}, the version the relay names")
    else:
        refused = True
        said.append(f"refused: the plugin runs {running}, and the relay names "
                    f"{fields['version']} — the session that reads it runs other rules")
    held = digest_of(content)
    if held == fields["sha256"]:
        said.append(f"checked: the text holds sha256 {held}")
    else:
        refused = True
        said.append(f"refused: the text hashes to sha256 {held}, not {fields['sha256']} — it "
                    f"changed since it was relayed")
    return not refused, said, content


def take(args: list[str], flag: str) -> str | None:
    if flag not in args:
        return None
    at = args.index(flag)
    if at + 1 >= len(args) or args[at + 1].startswith("--"):
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
        to = take(args, "--to")
        origin = take(args, "--from")
        source = take(args, "--text-file")
        relay = take(args, "--confirm")
        if args:
            raise CannotRun(f"not understood: {' '.join(args)}")
        if relay is not None:
            if to or origin or source:
                raise CannotRun("--confirm takes the relay file alone")
            path = Path(relay)
            if not path.is_file():
                raise CannotRun(f"{relay} is not a file")
            ok, said, content = confirm(path, Path.cwd())
            print("confirmed" if ok else "refuses")
            print("\n".join(said))
            if ok:
                print("text:")
                sys.stdout.flush()
                sys.stdout.buffer.write(content)
                sys.stdout.flush()
            return 0 if ok else REFUSED
        if not (to and origin and source):
            raise CannotRun("expected --to <sibling-project-root> --from <project-root> "
                            "--text-file <file|->, or --confirm <relay-file>")
        for given in (to, origin):
            if not Path(given).is_dir():
                raise CannotRun(f"{given} is not a directory")
        print("\n".join(write(Path(to).resolve(), Path(origin).resolve(), source)))
    except CannotRun as refusal:
        print(f"cannot run: {refusal}", file=sys.stderr)
        return CANNOT_RUN
    except Refused as refusal:
        print(f"refused: {refusal}")
        return REFUSED
    return 0


if __name__ == "__main__":
    sys.exit(main())
