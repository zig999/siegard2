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

Five things this script does, and nobody else does any of them:

    trace.py <target-root>                                        read and validate the file
    trace.py --check <target-root>                                the same, then report drift
    trace.py --bind <target-root> <spec-root> <node> <file> ...    write or extend one binding
    trace.py --bind-record <target-root> <spec-root> <record>     every binding that record states
    trace.py --bind ... --replace                                 write it in full instead
    trace.py --prune <target-root>                                drop the bindings nothing can fix

Drift is reported in three classes, because a caller can act on each differently and could act on
none of them while all three arrived as one list. A node the specification no longer holds is
`orphaned`: the fact it named is gone, and no operation here can repair the entry — `--bind`
refuses a node the specification does not hold, and this script is the trace's one writer, so the
finding repeats on every run forever. A node whose text moved is `moved`, and a file that changed
or vanished is `code`; both are true statements about real drift, and the answer to each is a
rebind by whoever owns the change. Only the first is `--prune`'s, and `--prune` touches only it:
dropping a binding whose file moved would discard the one record of which node that code answers
to, which is the whole of what this file keeps.

Left unpruned, the orphaned class is what makes the other two unreadable. A tree carrying eighty
stale entries reports eighty-three findings the day three files drift, and nobody reads the three:
the report a caller stops reading is a report that says nothing, however true every line of it is.

`--bind-record` is the form a delivery uses, and it exists because the older one made its caller
retype what a record already says. An implementation record names every node the source encodes and
every file each one reached; binding them one invocation at a time paid a full specification
validation and a full read-and-rewrite of the trace per node, and left the rule that a bind states
exactly what the record says — never a second judgment about it — resting on prose. This reads the
record: a node it does not name cannot be bound from this form, and one it does cannot be skipped.
The whole of it is refused before anything is written, because a delivery half bound describes a
link nobody made while reading exactly like a complete one. A record naming no node with
`encoded_at` is not a failure: the nodes it answers only by `how` reached no file, a bind with none
is refused, and there is simply nothing to write.

`--bind` validates <spec-root> the way spec.py does, refuses a node it does not hold, reads that
node's digest and each file's digest fresh, and writes the entry. By default it extends whatever
that node already held: a file this call does not name but an earlier bind of the same node did
stays bound, at the digest that earlier bind recorded, because two tasks landing the same rule in
two different files is not one of them undoing the other's work. A file this call does name is
written at the digest read just now, whether or not an earlier bind already held that path.
`--replace` writes the entry in full instead, exactly as every bind used to: a file left off the
list is a file this bind no longer claims — for the case where a fact genuinely moved out of a
file rather than into an additional one. **It substitutes the whole entry, not the files this call
names**, so where two records answer one node, replacing from the second drops what the first
bound. That is legitimate and often intended, and it is never silent: every path a `--replace`
stops claiming is printed as a receipt once the write succeeds, because the trace it leaves is
internally consistent and `--check` would come back clean over the loss. The first bind for a
target root creates the trace file;
every later one is held to the same specification, named once, and a bind naming a different one
is refused rather than silently repointed.

Every path this file holds — `specification`, and every binding's `files[].path` — is relative to
this file's own directory, exactly the way `siegard.json`'s `standard` is. `<target-root>` and
`<file>` on the command line are relative to the target source root instead, the anchor every other
contract in this framework uses — and so is every path a record's `encoded_at` carries; this script
converts, so a caller working the way every other skill already does never computes the git
toplevel itself.

Declared dependencies: PyYAML, jsonschema (this script also imports spec.py and project.py, its
siblings under bin/).

Usage:  trace.py <target-root>
        trace.py --check <target-root>
        trace.py --bind <target-root> <spec-root> <node> <file> [<file> ...] [--replace]
        trace.py --bind-record <target-root> <spec-root> <implementation-record> [--replace]
        trace.py --prune <target-root>
Exit:   0 sound / drift-free / bound / pruned
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
    import yaml
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover - exercised by the environment, not the suite
    print("cannot run: PyYAML and jsonschema are required (pip install pyyaml jsonschema)",
          file=sys.stderr)
    raise SystemExit(CANNOT_RUN)

import project
import spec

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
TRACE_CONTRACT = PLUGIN_ROOT / "schemas" / "trace.json"
TRACE_FILE = "siegard-trace.json"

ORPHANED, MOVED, CODE = "orphaned", "moved", "code"
CLASSES = {
    ORPHANED: "bound to a node the specification no longer holds — no bind can repair these, "
              "and `--prune` is the only thing that clears them",
    MOVED: "bound to a node whose text moved since the bind — rebind whoever owns the change",
    CODE: "bound to a file that changed or is gone — rebind whoever owns the change",
}


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


def drift_of(declared: dict, home: Path) -> tuple[list[tuple[str, str, str]], list[str]]:
    """Every binding that no longer computes to what was recorded for it, each under the class its
    remedy belongs to — and, separately, whatever stopped the reading before any of that.

    The classes are not three flavours of one fact, and a caller who cannot tell them apart cannot
    act on any of them. `orphaned` is the one nothing here could fix until `--prune` existed: the
    node left the specification, `--bind` refuses a node the specification does not hold, and this
    script is the trace's one writer — so the entry stays, its finding repeats on every run, and a
    file drift that arrived today reads as one more line in a list nobody finishes. `moved` and
    `code` are the drift this file exists to report, and neither is a deletion's business: a rebind
    by whoever owns the change is the answer, and dropping the entry instead would throw away the
    one record of which node that code answers to.

    Refusals come back apart from findings because they are not findings. A specification that does
    not resolve or does not hold together says nothing about any binding — reporting `orphaned` for
    every node of a base nobody could read would be this script inventing drift out of its own
    blindness."""
    spec_root = home / declared["specification"]
    if not spec_root.is_dir():
        return [], [f"specification: {spec_root} is not a directory; "
                    f"{declared['specification']} no longer resolves"]
    nodes, node_problems = spec.collect(spec_root, spec.contracts())
    node_problems += spec.cross_problems(nodes, spec_root)
    if node_problems:
        return [], [f"specification: {spec_root} is not sound; run spec.py against it directly"]

    findings: list[tuple[str, str, str]] = []
    for entry in declared.get("bindings") or []:
        node_id, digest = entry["node"], entry["digest"]
        current = nodes.get(node_id)
        if current is None:
            findings.append((ORPHANED, node_id,
                             f"{node_id}: no longer in the specification; the binding is stale"))
        elif current["digest"] != digest:
            findings.append((MOVED, node_id,
                             f"{node_id}: bound at {digest}, now {current['digest']}; "
                             f"the specification moved since this bind"))
        for file_entry in entry.get("files") or []:
            path = home / file_entry["path"]
            if not path.is_file():
                findings.append((CODE, node_id,
                                 f"{node_id}: {file_entry['path']} no longer exists"))
                continue
            now = spec.digest_of(path)
            if now != file_entry["digest"]:
                findings.append((CODE, node_id,
                                 f"{node_id}: {file_entry['path']} bound at "
                                 f"{file_entry['digest']}, now {now}; the file changed without "
                                 f"a rebind"))
    return findings, []


def traced_files_of(target: Path, home: Path, files: list[str]) -> tuple[list[dict], list[str]]:
    """Each named file as the trace stores it: the path re-anchored on this file's own directory,
    and the digest read now. A file that does not exist is a problem rather than an omission —
    binding a node to a path nothing holds would record a link to nowhere."""
    offset = Path(os.path.relpath(target.resolve(), home.resolve()))
    entries, problems = [], []
    for given in files:
        source = target / given
        if not source.is_file():
            problems.append(f"{source} does not exist")
            continue
        stored = given if str(offset) == "." else (offset / given).as_posix()
        entries.append({"path": stored, "digest": spec.digest_of(source)})
    return entries, problems


def fold(declared: dict, node_id: str, digest: str, traced_files: list[dict],
         replace: bool) -> tuple[int, list[str]]:
    """Fold one binding into the trace in place; say how many files that node now holds, and which
    ones this call stopped claiming.

    Extending what the node already held is the default: two tasks landing one node in two
    different files is not one of them undoing the other's work. `--replace` writes the entry in
    full instead, for the case where a fact genuinely moved out of a file rather than into an
    additional one.

    The second return value is why this reports at all. `--replace` substitutes the whole entry,
    not the files this call names, so a path an earlier bind put there and this one leaves off is
    gone — and gone invisibly, because the trace it writes is internally consistent and `--check`
    comes back clean over it. That is the same silent loss the union default was introduced to end,
    surviving behind a flag. Nothing here refuses it: dropping a file is exactly what `--replace`
    is for, and the caller who omitted a vanished path meant to. What was missing is the receipt —
    the two sides are both in hand at this moment and one of them was being discarded unread.

    Paths, never records. Which delivery put a file here is not something this file stores, so the
    receipt names what stopped being claimed and says nothing about who claimed it."""
    existing = next((entry for entry in declared["bindings"]
                     if entry.get("node") == node_id), None)
    given = {entry["path"] for entry in traced_files}
    dropped = (sorted(entry["path"] for entry in existing.get("files") or []
                      if entry["path"] not in given)
               if replace and existing is not None else [])
    if replace or existing is None:
        files = traced_files
    else:
        files = [entry for entry in existing.get("files") or []
                 if entry["path"] not in given] + traced_files
    files = sorted(files, key=lambda entry: entry["path"])
    bindings = [entry for entry in declared["bindings"] if entry.get("node") != node_id]
    bindings.append({"node": node_id, "digest": digest, "files": files})
    declared["bindings"] = sorted(bindings, key=lambda entry: entry["node"])
    return len(files), dropped


def released(node_id: str, dropped: list[str]) -> str:
    """The receipt for what a `--replace` stopped claiming. A statement, never a warning: the
    ordinary use of `--replace` is a file that genuinely left, and an alarm on the correct path is
    an alarm nobody reads by the third time. It ends by pointing at where the entry before this
    write survives if it survives anywhere, which is git — stated as a direction rather than a
    guarantee, because a trace that was never committed has no earlier state to return to."""
    return (f"  --replace released {len(dropped)} path(s) this call did not name; "
            f"{node_id} no longer claims {', '.join(dropped)}. Where the fact moved out of those "
            f"files, that is what --replace is for; where another delivery had bound one of them, "
            f"that binding is gone from here, and the last committed trace is where it survives "
            f"if anywhere")


def opened(target: Path, spec_root: Path,
           home: Path) -> tuple[dict | None, str | None]:
    """The trace as it stands, ready to be folded into, or nothing and the reason. The first bind
    for a target root creates it; every later one is held to the same specification, and one
    naming a different specification is refused rather than silently repointed."""
    spec_relative = Path(os.path.relpath(spec_root.resolve(), home.resolve())).as_posix()
    declared = load(target) or {"specification": spec_relative, "bindings": []}
    if declared["specification"] != spec_relative:
        return None, (f"{trace_path(target)} already traces against "
                      f"{declared['specification']}, not {spec_relative}; a trace names one "
                      f"specification")
    return declared, None


def sound_specification(spec_root: Path) -> tuple[dict[str, dict] | None, int]:
    """Every node the specification holds, or nothing and the exit status. Read through spec.py's
    own pipeline, because a trace bound against a specification that does not hold together records
    a link to a fact nobody validated."""
    nodes, problems = spec.collect(spec_root, spec.contracts())
    problems += spec.cross_problems(nodes, spec_root)
    if problems:
        for problem in sorted(set(problems)):
            print(problem)
        print(f"\n{spec_root} is not sound; nothing was bound.")
        return None, 1
    return nodes, 0


def write_trace(target: Path, declared: dict, act: str = "bind") -> int:
    problems = problems_of(declared)
    if problems:
        for problem in problems:
            print(f"cannot {act}: {problem}")
        return 1
    trace_path(target).write_text(json.dumps(declared, indent=2) + "\n", encoding="utf-8")
    return 0


def bind(target: Path, spec_root: Path, node_id: str, files: list[str],
         replace: bool = False) -> int:
    if not target.is_dir():
        print(f"cannot run: {target} is not a directory", file=sys.stderr)
        return CANNOT_RUN
    if not spec_root.is_dir():
        print(f"cannot run: {spec_root} is not a directory", file=sys.stderr)
        return CANNOT_RUN

    nodes, status = sound_specification(spec_root)
    if nodes is None:
        return status
    if node_id not in nodes:
        print(f"cannot bind: {spec_root} holds no node {node_id}")
        return 1

    home = home_of(target)
    traced, problems = traced_files_of(target, home, files)
    for problem in problems:
        print(f"cannot bind: {problem}")
    if problems:
        return 1

    declared, refusal = opened(target, spec_root, home)
    if declared is None:
        print(f"cannot bind: {refusal}")
        return 1

    held, dropped = fold(declared, node_id, nodes[node_id]["digest"], traced, replace)
    if write_trace(target, declared) != 0:
        return 1
    print(f"bound {node_id} to {held} file(s) at {trace_path(target)}")
    if dropped:
        print(released(node_id, dropped))
    return 0


def encoded_in(record: Path) -> tuple[list[tuple[str, list[str]]], list[str]]:
    """Every node one implementation record says the source encodes, with the files it names.

    The record is the only thing that knows which nodes reached the code and where, and until this
    existed its caller retyped both — one node per invocation, with the rule that a bind states
    exactly what the record says and never a second judgment about it held by prose alone. Reading
    the record here makes that rule structural: a node it does not name cannot be bound from this
    form, and one it does cannot be skipped.

    A node the record answers only by `how` — constrained, encoded nowhere — is not here, and that
    is not an omission: there is no file to name, and a bind with none is refused.

    Nothing here validates the record as a delivery node. `bin/deliver.py` did that before this
    runs, and a second opinion about a contract this script does not own would be a second home for
    it. What this reads is two field names, defensively."""
    if not record.is_file():
        return [], [f"{record} does not exist"]
    text = record.read_text(encoding="utf-8")
    match = spec.FENCE.match(text)
    if not match:
        return [], [f"{record} carries no frontmatter fence; it is not a record this can read"]
    try:
        front = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as broken:
        return [], [f"{record}: frontmatter does not parse: {broken}"]
    if not isinstance(front, dict):
        return [], [f"{record}: frontmatter is not a mapping"]

    pairs = []
    for entry in front.get("nodes") or []:
        if not isinstance(entry, dict) or not isinstance(entry.get("node"), str):
            continue
        where = entry.get("encoded_at")
        if not isinstance(where, list):
            continue
        files = [f for f in where if isinstance(f, str)]
        if files:
            pairs.append((entry["node"], files))
    return pairs, []


def bind_record(target: Path, spec_root: Path, record: Path, replace: bool = False) -> int:
    """Every binding one implementation record states, written as one act.

    Per node, the older form paid a full specification validation and a full read-and-rewrite of
    the trace. Here they are paid once, and the whole of it is refused before anything is written:
    a delivery half bound describes a link nobody made, and the file it would leave behind reads
    exactly like a complete one."""
    if not target.is_dir():
        print(f"cannot run: {target} is not a directory", file=sys.stderr)
        return CANNOT_RUN
    if not spec_root.is_dir():
        print(f"cannot run: {spec_root} is not a directory", file=sys.stderr)
        return CANNOT_RUN

    pairs, problems = encoded_in(record)
    for problem in problems:
        print(f"cannot run: {problem}", file=sys.stderr)
    if problems:
        return CANNOT_RUN
    if not pairs:
        print(f"nothing to bind: {record} names no node with `encoded_at`; a node the record "
              f"answers only by `how` reached no file, and a bind with none is refused")
        return 0

    nodes, status = sound_specification(spec_root)
    if nodes is None:
        return status

    home = home_of(target)
    refusals, folded = [], []
    for node_id, files in pairs:
        if node_id not in nodes:
            refusals.append(f"{spec_root} holds no node {node_id}, which {record.name} says the "
                            f"source encodes")
            continue
        traced, missing = traced_files_of(target, home, files)
        refusals += [f"{node_id}: {problem}" for problem in missing]
        if not missing:
            folded.append((node_id, traced))

    declared, refusal = opened(target, spec_root, home)
    if refusal is not None:
        refusals.append(refusal)
    if refusals:
        for problem in refusals:
            print(f"cannot bind: {problem}")
        print(f"\n{len(refusals)} problem(s); nothing was bound. A record's bindings are one act, "
              f"so a trace holding some of them would say this delivery is linked when it is not.")
        return 1

    held = [(node_id, *fold(declared, node_id, nodes[node_id]["digest"], traced, replace))
            for node_id, traced in folded]
    if write_trace(target, declared) != 0:
        return 1
    for node_id, count, dropped in held:
        print(f"bound {node_id} to {count} file(s)")
        if dropped:
            print(released(node_id, dropped))
    print(f"{len(held)} binding(s) written at {trace_path(target)}, read from {record.name}")
    let_go = sum(len(dropped) for _, _, dropped in held)
    if let_go:
        print(f"{let_go} path(s) released across {sum(1 for _, _, d in held if d)} node(s); a "
              f"total is here because one node's receipt is easy to read past in a record that "
              f"bound twenty")
    return 0


def prune(target: Path) -> int:
    """Drop every binding to a node the specification no longer holds, and nothing else.

    This is the only thing here that deletes, and it exists because one class of drift had no exit
    at all. A node the specification dropped cannot be rebound — `--bind` refuses a node that is
    not there — and a trace is hand-edited by nobody, this script being its one writer. So the
    entry stayed, its finding repeated on every `--check`, and the pile of them is what a real
    drift arriving later disappears into.

    It refuses the two classes it is not for, and the refusal is the point rather than a
    conservatism. A file that moved or vanished is drift with an owner and a remedy: the node is
    still in the base, still answered by code somewhere, and deleting the binding would destroy the
    one record of which node that code answers to while reporting the tree as clean. The narrow
    class is safe for the opposite reason — the node is gone, so the entry links code to nothing,
    and nothing downstream can ask a question of it that an absence does not already answer.

    It reads the specification through the same pipeline `--check` does, and refuses over one that
    does not hold together. Pruning against a base nobody could read would delete bindings for
    nodes that exist, on the strength of not having been able to see them."""
    if not target.is_dir():
        print(f"cannot run: {target} is not a directory", file=sys.stderr)
        return CANNOT_RUN

    path = trace_path(target)
    declared = load(target)
    if declared is None:
        print(f"no trace file: {path} does not exist; there is nothing to prune")
        return 0

    problems = problems_of(declared)
    if problems:
        for problem in problems:
            print(f"{path}: {problem}")
        return 1

    findings, refusals = drift_of(declared, home_of(target))
    if refusals:
        for refusal in refusals:
            print(refusal)
        print(f"\nnothing was pruned: a specification this cannot read says nothing about which "
              f"bindings it still holds")
        return 1

    stale = sorted({node for cls, node, _ in findings if cls == ORPHANED})
    if not stale:
        held = len(declared.get("bindings") or [])
        print(f"nothing to prune: every one of {held} binding(s) names a node the specification "
              f"still holds")
        return 0

    declared["bindings"] = [entry for entry in declared["bindings"]
                            if entry.get("node") not in set(stale)]
    if write_trace(target, declared, act="prune") != 0:
        return 1
    for node_id in stale:
        print(f"dropped {node_id}: the specification no longer holds it")
    remaining = len(declared["bindings"])
    print(f"\n{len(stale)} binding(s) pruned at {path}; {remaining} remain. What was dropped was "
          f"a link to a node that is gone — every drift with a node still in the base is still "
          f"here, and still owed a rebind.")
    return 0


def main() -> int:
    args = sys.argv[1:]
    check = "--check" in args
    do_bind = "--bind" in args
    do_record = "--bind-record" in args
    do_prune = "--prune" in args
    replace = "--replace" in args
    args = [a for a in args
            if a not in ("--check", "--bind", "--bind-record", "--replace", "--prune")]
    named = [name for name, given in (("--check", check), ("--bind", do_bind),
                                      ("--bind-record", do_record),
                                      ("--prune", do_prune)) if given]
    if len(named) > 1:
        print(f"cannot run: {' and '.join(named)} are mutually exclusive", file=sys.stderr)
        return CANNOT_RUN
    if replace and not (do_bind or do_record):
        print("cannot run: --replace only applies to --bind and --bind-record", file=sys.stderr)
        return CANNOT_RUN
    if not TRACE_CONTRACT.is_file():
        print(f"cannot run: {TRACE_CONTRACT} is missing; nothing can be validated without it",
              file=sys.stderr)
        return CANNOT_RUN

    if do_record:
        if len(args) != 3:
            print("cannot run: expected --bind-record <target-root> <spec-root> "
                  "<implementation-record> [--replace]", file=sys.stderr)
            return CANNOT_RUN
        target, spec_root, record = args
        return bind_record(Path(target), Path(spec_root), Path(record), replace)

    if do_prune:
        if len(args) != 1 or args[0].startswith("--"):
            print("cannot run: expected --prune <target-root>", file=sys.stderr)
            return CANNOT_RUN
        return prune(Path(args[0]))

    if do_bind:
        if len(args) < 4:
            print("cannot run: expected --bind <target-root> <spec-root> <node> "
                  "<file> [<file> ...] [--replace]", file=sys.stderr)
            return CANNOT_RUN
        target, spec_root, node_id, *files = args
        return bind(Path(target), Path(spec_root), node_id, files, replace)

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

    findings, refusals = drift_of(declared, home_of(target))
    if refusals:
        for refusal in refusals:
            print(refusal)
        return 1
    if findings:
        # Class by class rather than one flat list: the tally is what a reader acts on, and the
        # orphaned count is what says how much of this report no rebind will ever shorten.
        for cls in (ORPHANED, MOVED, CODE):
            for _, _, said in [f for f in findings if f[0] == cls]:
                print(said)
        print(f"\n{len(findings)} drift finding(s) over {count} binding(s):")
        for cls in (ORPHANED, MOVED, CODE):
            print(f"  {sum(1 for f in findings if f[0] == cls)} {cls}: {CLASSES[cls]}")
        return 1
    print(f"no drift: {count} binding(s) match the specification and the code as both stand now")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
