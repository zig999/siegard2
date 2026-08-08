#!/usr/bin/env python3
"""Resolve and maintain the trace: which specification node produced which file, once the plan
that wrote it is gone.

Planning and delivery are disposable — a task exists to get code written, and nothing requires
its files to survive that. `siegard-trace.json`, beside `siegard.json` at the git toplevel of the
target source root, is the one fact this framework keeps instead: for a node it has bound, the
digest it read and the file(s) it produced, each pinned the same way. A later run recomputes both
digests from what is on disk now and compares — a node whose digest no longer matches moved in
the specification since the bind; a file whose digest no longer matches moved in the code without
a rebind. Either is drift, and this script is what says so without any plan's history to consult.

Three things this script does, and nobody else does any of them:

    trace.py <target-root>                                        read and validate the file
    trace.py --check <target-root>                                the same, then report drift
    trace.py --bind <target-root> <spec-root> <node> <file> ...    write or replace one binding

`--bind` validates <spec-root> the way spec.py does, refuses a node it does not hold, reads that
node's digest and each file's digest fresh, and writes the entry — replacing whatever that node
held before, in full: a file left out of the list is a file this bind no longer claims. The first
bind for a target root creates the trace file; every later one is held to the same specification,
named once, and a --bind naming a different one is refused rather than silently repointed.

Every path this file holds — `specification`, and every binding's `files[].path` — is relative to
this file's own directory, exactly the way `siegard.json`'s `standard` is. `<target-root>` and
`<file>` on the --bind command line are relative to the target source root instead, the anchor
every other contract in this framework uses; this script converts, so a caller working the way
every other skill already does never computes the git toplevel itself.

Declared dependencies: jsonschema (this script also imports spec.py and project.py, its siblings
under bin/).

Usage:  trace.py <target-root>
        trace.py --check <target-root>
        trace.py --bind <target-root> <spec-root> <node> <file> [<file> ...]
Exit:   0 sound / drift-free / bound
        1 problems: an invalid file, drift found, an unsound specification, an unknown node
          or file
        2 cannot run
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

CANNOT_RUN = 2

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover - exercised by the environment, not the suite
    print("cannot run: jsonschema is required (pip install jsonschema)", file=sys.stderr)
    raise SystemExit(CANNOT_RUN)

import project
import spec

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
TRACE_CONTRACT = PLUGIN_ROOT / "schemas" / "trace.json"
TRACE_FILE = "siegard-trace.json"


def home_of(target: Path) -> Path:
    """Where the trace file sits: the same directory `siegard.json` sits in."""
    return project.toplevel_of(target)


def trace_path(target: Path) -> Path:
    return home_of(target) / TRACE_FILE


def load(target: Path) -> dict | None:
    """The trace declared at <target-root>, or None where none has been bound yet."""
    path = trace_path(target)
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def problems_of(declared: dict) -> list[str]:
    """Everything wrong with a trace on its own terms: the schema, plus one entry per node."""
    schema = json.loads(TRACE_CONTRACT.read_text(encoding="utf-8"))
    problems = [f"{'.'.join(str(part) for part in error.absolute_path) or 'top level'}: "
                f"{error.message}"
                for error in sorted(Draft202012Validator(schema).iter_errors(declared), key=str)]
    counted: dict[str, int] = {}
    for entry in declared.get("bindings") or []:
        if isinstance(entry, dict) and isinstance(entry.get("node"), str):
            counted[entry["node"]] = counted.get(entry["node"], 0) + 1
    problems += [f"bindings: {node} is bound {count} times; one entry per node"
                 for node, count in sorted(counted.items()) if count > 1]
    return problems


def drift_of(declared: dict, home: Path) -> list[str]:
    """Every binding whose node or file no longer computes to the digest recorded for it."""
    spec_root = home / declared["specification"]
    if not spec_root.is_dir():
        return [f"specification: {spec_root} is not a directory; "
                f"{declared['specification']} no longer resolves"]
    nodes, node_problems = spec.collect(spec_root, spec.contracts())
    node_problems += spec.cross_problems(nodes, spec_root)
    if node_problems:
        return [f"specification: {spec_root} is not sound; run spec.py against it directly"]

    problems = []
    for entry in declared.get("bindings") or []:
        node_id, digest = entry["node"], entry["digest"]
        current = nodes.get(node_id)
        if current is None:
            problems.append(f"{node_id}: no longer in the specification; the binding is stale")
        elif current["digest"] != digest:
            problems.append(f"{node_id}: bound at {digest}, now {current['digest']}; "
                            f"the specification moved since this bind")
        for file_entry in entry.get("files") or []:
            path = home / file_entry["path"]
            if not path.is_file():
                problems.append(f"{node_id}: {file_entry['path']} no longer exists")
                continue
            now = spec.digest_of(path)
            if now != file_entry["digest"]:
                problems.append(f"{node_id}: {file_entry['path']} bound at "
                                f"{file_entry['digest']}, now {now}; the file changed without "
                                f"a rebind")
    return problems


def bind(target: Path, spec_root: Path, node_id: str, files: list[str]) -> int:
    if not target.is_dir():
        print(f"cannot run: {target} is not a directory", file=sys.stderr)
        return CANNOT_RUN
    if not spec_root.is_dir():
        print(f"cannot run: {spec_root} is not a directory", file=sys.stderr)
        return CANNOT_RUN

    nodes, problems = spec.collect(spec_root, spec.contracts())
    problems += spec.cross_problems(nodes, spec_root)
    if problems:
        for problem in sorted(set(problems)):
            print(problem)
        print(f"\n{spec_root} is not sound; nothing was bound.")
        return 1
    if node_id not in nodes:
        print(f"cannot bind: {spec_root} holds no node {node_id}")
        return 1

    home = home_of(target)
    offset = Path(os.path.relpath(target.resolve(), home.resolve()))

    traced_files = []
    for given in files:
        source = target / given
        if not source.is_file():
            print(f"cannot bind: {source} does not exist")
            return 1
        stored = given if str(offset) == "." else (offset / given).as_posix()
        traced_files.append({"path": stored, "digest": spec.digest_of(source)})

    spec_relative = Path(os.path.relpath(spec_root.resolve(), home.resolve())).as_posix()

    declared = load(target) or {"specification": spec_relative, "bindings": []}
    if declared["specification"] != spec_relative:
        print(f"cannot bind: {trace_path(target)} already traces against "
              f"{declared['specification']}, not {spec_relative}; a trace names one "
              f"specification")
        return 1

    bindings = [entry for entry in declared["bindings"] if entry.get("node") != node_id]
    bindings.append({"node": node_id, "digest": nodes[node_id]["digest"], "files": traced_files})
    declared["bindings"] = sorted(bindings, key=lambda entry: entry["node"])

    problems = problems_of(declared)
    if problems:
        for problem in problems:
            print(f"cannot bind: {problem}")
        return 1

    path = trace_path(target)
    path.write_text(json.dumps(declared, indent=2) + "\n", encoding="utf-8")
    print(f"bound {node_id} to {len(traced_files)} file(s) at {path}")
    return 0


def main() -> int:
    args = sys.argv[1:]
    check = "--check" in args
    do_bind = "--bind" in args
    args = [a for a in args if a not in ("--check", "--bind")]
    if check and do_bind:
        print("cannot run: --check and --bind are mutually exclusive", file=sys.stderr)
        return CANNOT_RUN
    if not TRACE_CONTRACT.is_file():
        print(f"cannot run: {TRACE_CONTRACT} is missing; nothing can be validated without it",
              file=sys.stderr)
        return CANNOT_RUN

    if do_bind:
        if len(args) < 4:
            print("cannot run: expected --bind <target-root> <spec-root> <node> "
                  "<file> [<file> ...]", file=sys.stderr)
            return CANNOT_RUN
        target, spec_root, node_id, *files = args
        return bind(Path(target), Path(spec_root), node_id, files)

    if len(args) != 1 or args[0].startswith("--"):
        print("cannot run: expected [--check] <target-root>", file=sys.stderr)
        return CANNOT_RUN
    target = Path(args[0])
    if not target.is_dir():
        print(f"cannot run: {target} is not a directory", file=sys.stderr)
        return CANNOT_RUN

    path = trace_path(target)
    declared = load(target)
    if declared is None:
        print(f"no trace file: {path} does not exist; nothing has been bound yet")
        return 0

    problems = problems_of(declared)
    if problems:
        for problem in problems:
            print(f"{path}: {problem}")
        return 1

    count = len(declared.get("bindings") or [])
    if not check:
        print(f"trace sound: {count} binding(s), traced against {declared['specification']}")
        return 0

    drift = drift_of(declared, home_of(target))
    if drift:
        for problem in drift:
            print(problem)
        print(f"\n{len(drift)} drift finding(s) over {count} binding(s).")
        return 1
    print(f"no drift: {count} binding(s) match the specification and the code as both stand now")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
