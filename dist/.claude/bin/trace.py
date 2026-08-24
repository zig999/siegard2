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

Six things this script does, and nobody else does any of them:

    trace.py <target-root>                                        read and validate the file
    trace.py --check <target-root> [--all]                        the same, then report drift
    trace.py --bind <target-root> <spec-root> <node> <file> ...    write or extend one binding
    trace.py --bind-record <target-root> <spec-root> <record>     every binding that record states
    trace.py --bind ... --replace                                 write it in full instead
    trace.py --prune <target-root>                                drop the bindings nothing can fix
    trace.py --reconciliation <record>                            hold a reconciliation to its
                                                                  contract before it is bound

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

The `code` class has the same arithmetic inside itself, and the listing answers it the same way.
One file bound by sixteen nodes drifts sixteen findings the day it changes once — a live consumer
tree measured exactly that, one shared service file burying the report on every edit — so the
listing prints that class per file: one line naming the file, the reason, and every binding the
change staled. The findings are still counted per binding, because that is what they are; the
grouping is the listing's, because the remedy for this class is a reconciliation and a
reconciliation is invoked over a file set — the report is keyed the way the remedy consumes it.

The same arithmetic is what `edits_freely` answers, one class over. A target whose surface changes
for reasons no node governs — a label, a colour, a column's order — produces a `code` finding per
edit, weekly, and buries `moved` and `orphaned` under a list nobody finishes. So a project may name
those targets in `siegard.json`, and `--check` stops listing that class for files sitting under
them. Three things this deliberately is not. It is not per-invocation: the declaration is read from
the project file beside this one, so a check run from anywhere reports the same tree the same way,
and a check over a traced target never loses a finding because a sibling target is exempt. It is
not a change to what is bound — `--bind-record` still writes the link, `moved` still says the
specification shifted under those files, `orphaned` still says the node is gone. And it is not
silence: a receipt says how many findings were held back and `--all` lists them, which is what
keeps a declaration a consumer can measure from becoming one it forgets it made.

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

That refusal is over form — a node this specification does not hold, a file that is not there — and
it is not the reconciliation route's per-node judgment. A reconciliation record answers node by
node, and a node the judgment did not clear carries no `encoded_at`; the nodes that cleared are
written and that one is not. Refusing the record over it would make a judgment that resolved
thirty-eight of forty nodes worth exactly as much as one that resolved none, and buy nothing for
it: the two nodes it could not write stay precisely as drifted as they were, which is what the
next `--check` says. What the bind owes instead is a receipt naming them, so a partial bind never
reads like a complete one.

`--reconciliation` is the one form here that writes nothing. It holds a reconciliation record —
source that changed outside any task, at `siegard-reconcile/<slug>.md` beside this file — to
`schemas/reconciliation.json`, so that `--bind-record` can then read it exactly as it reads an
implementation record. That split is deliberate and it is the same one the delivery route already
has: `bin/deliver.py` validates an implementation record and this script binds what it says, never
holding a second opinion about a contract it does not own. What is different is that nobody else
owns this one. A reconciliation record has no life outside the trace — it exists to justify a bind
and nothing reads it for any other purpose — so the validation lands here rather than in a script
invented to hold it. The check that matters is the accounting: every path a node claims is a path
the record's own file set names, and every file it names is claimed by a node or declared unbound.
A record that binds a file nobody declared would widen the reconciliation past what a human
scoped, silently, and the trace would carry the result forever.

`--bind` validates <spec-root> the way spec.py does, refuses a node it does not hold, reads that
node's digest and each file's digest fresh, and writes the entry. It is the one bind no record
backs — every skill binds through `--bind-record`, where an implementation or reconciliation
record holds the judgment — so every `--bind` prints a receipt saying the judgment behind this
entry lives nowhere, because the trace it writes reads afterwards exactly like one a record
justified. By default it extends whatever
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
        trace.py --check <target-root> [--all]
        trace.py --bind <target-root> <spec-root> <node> <file> [<file> ...] [--replace]
        trace.py --bind-record <target-root> <spec-root> <implementation-record> [--replace]
        trace.py --prune <target-root>
        trace.py --reconciliation <reconciliation-record>
        trace.py --help
                print this text and stop
Exit:   0 sound / drift-free / bound / pruned / the record holds
        1 problems: an invalid file, drift found, an unsound specification, an unknown node
          or file, a record its contract refuses
        2 cannot run
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path, PurePosixPath
from typing import NoReturn

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
RECONCILE_CONTRACT = PLUGIN_ROOT / "schemas" / "reconciliation.json"
TRACE_FILE = "siegard-trace.json"
RECONCILE_DIR = "siegard-reconcile"

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


def freely_edited(home: Path) -> list[str]:
    """The path prefixes whose `code` findings this tree asked not to be listed, read from the
    project file sitting beside the trace.

    Read here rather than taken as a flag, because which targets those are is the consumer's
    standing declaration and not a thing an invocation gets to answer differently each time. Read
    defensively: a project file that does not parse, or does not declare the field, suppresses
    nothing — `project.py` is what holds that file to its contract and says so properly, and a
    drift report is the wrong place to learn the project file is broken.

    The prefixes come back spelled from this file's own directory, which is the anchor every path
    in the trace already uses, so the comparison below is a prefix test and never a pattern."""
    declared_at = home / project.PROJECT_FILE
    if not declared_at.is_file():
        return []
    try:
        declared = json.loads(declared_at.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(declared, dict):
        return []
    named = declared.get("edits_freely") or []
    targets = declared.get("targets") or {}
    if not isinstance(named, list) or not isinstance(targets, dict):
        return []
    prefixes = []
    for key in named:
        where = targets.get(key) if isinstance(key, str) else None
        if isinstance(where, str) and where:
            prefixes.append(PurePosixPath(where).as_posix().rstrip("/"))
    return sorted(set(prefixes))


def under(path: str, prefixes: list[str]) -> bool:
    """Whether one path of the trace sits under any of those prefixes. A prefix of `.` — a target
    that is the toplevel itself — reaches everything, which is what a project declaring its whole
    tree freely edited asked for."""
    parts = PurePosixPath(path).parts
    for prefix in prefixes:
        if prefix in (".", ""):
            return True
        if parts[:len(PurePosixPath(prefix).parts)] == PurePosixPath(prefix).parts:
            return True
    return False


def cannot_run(message: str) -> NoReturn:
    """Refuse and stop. A trace this script cannot read is never repaired into a default: the
    file is the record, and a default would bind against a record nobody wrote."""
    print(f"cannot run: {message}", file=sys.stderr)
    raise SystemExit(CANNOT_RUN)


def trace_path(target: Path) -> Path:
    return home_of(target) / TRACE_FILE


def load(target: Path) -> dict | None:
    """The trace declared at <target-root>, or None where none has been bound yet.

    A trace that does not parse, or that parses to anything but a mapping, is refused here rather
    than carried further. This is the one file the framework keeps after a plan is history, and
    it is one of the two that conflict in a worktree batch — so a trace holding merge markers is
    a state that happens, and every form of this script would otherwise end in a traceback over
    it instead of saying which file to fix."""
    path = trace_path(target)
    if not path.is_file():
        return None
    try:
        declared = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as broken:
        cannot_run(f"{path} does not parse: {broken}")
    if not isinstance(declared, dict):
        cannot_run(f"{path} holds a {type(declared).__name__}, not a trace; a trace is an object "
                   f"with a specification and its bindings")
    return declared


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


def drift_of(declared: dict,
             home: Path) -> tuple[list[tuple[str, str, str | None, str]], list[str]]:
    """Every binding that no longer computes to what was recorded for it, each under the class its
    remedy belongs to — and, separately, whatever stopped the reading before any of that.

    A finding carries the path it is about where it has one, so that a caller filtering by where
    the file sits reads the path rather than the sentence. The classes about a node carry none:
    a node moved or gone is not a fact about any one file.

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
    blindness.

    A `code` finding's message carries the reason alone — the node and the path already ride the
    tuple's own slots, and the report lists this class per file (`code_report`), so a message
    restating either would be parsed back out of prose to group it. The pinned digests are not in
    the message either: the trace file holds them, and a reconciliation reads them there."""
    spec_root = home / declared["specification"]
    if not spec_root.is_dir():
        return [], [f"specification: {spec_root} is not a directory; "
                    f"{declared['specification']} no longer resolves"]
    nodes, node_problems = spec.collect(spec_root, spec.contracts())
    node_problems += spec.cross_problems(nodes, spec_root)
    if node_problems:
        return [], [f"specification: {spec_root} is not sound; run spec.py against it directly"]

    findings: list[tuple[str, str, str | None, str]] = []
    for entry in declared.get("bindings") or []:
        node_id, digest = entry["node"], entry["digest"]
        current = nodes.get(node_id)
        if current is None:
            findings.append((ORPHANED, node_id, None,
                             f"{node_id}: no longer in the specification; the binding is stale"))
        elif current["digest"] != digest:
            findings.append((MOVED, node_id, None,
                             f"{node_id}: bound at {digest}, now {current['digest']}; "
                             f"the specification moved since this bind"))
        for file_entry in entry.get("files") or []:
            where = file_entry["path"]
            path = home / where
            if not path.is_file():
                findings.append((CODE, node_id, where, "the file no longer exists"))
                continue
            if spec.digest_of(path) != file_entry["digest"]:
                findings.append((CODE, node_id, where, "the file changed without a rebind"))
    return findings, []


def traced_files_of(target: Path, home: Path, files: list[str]) -> tuple[list[dict], list[str]]:
    """Each named file as the trace stores it: the path re-anchored on this file's own directory,
    and the digest read now. A file that does not exist is a problem rather than an omission —
    binding a node to a path nothing holds would record a link to nowhere.

    The refusal names the anchor, because the anchor is what is usually wrong. Every path this
    script prints back — a drift finding, an entry of the trace — is spelled from the target's git
    toplevel, and every path it reads is spelled from the target source root. A caller who copies
    one into the other gets a path that is neither, and `<target>/<target>/...` is a stranger thing
    to be handed than the reason it happened."""
    offset = Path(os.path.relpath(target.resolve(), home.resolve()))
    entries, problems = [], []
    claimed: set[str] = set()
    for given in files:
        source = target / given
        if not source.is_file():
            problems.append(f"{source} does not exist; a path is read relative to {target}, the "
                            f"target source root, never from the repository around it")
            continue
        try:
            source.resolve().relative_to(target.resolve())
        except ValueError:
            # The sentence above is the whole rule, and `../` is the one spelling that passes
            # `is_file()` while breaking it. Stored unnormalised it would also alias: one file
            # under two spellings is two entries no reader can tell apart.
            problems.append(f"{given} climbs out of {target}, the target source root; a bound "
                            f"path is read from inside it, never from the repository around it")
            continue
        stored = given if str(offset) == "." else (offset / given).as_posix()
        if stored in claimed:
            problems.append(f"{stored} is named twice in one bind; a second entry for one path "
                            f"carries nothing the first does not, and every later reading of the "
                            f"trace would count the file twice")
            continue
        claimed.add(stored)
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


def unrecorded(node_id: str) -> str:
    """The receipt for a bind no record backs. A statement, never a refusal: `--bind` is the
    general form and stays open — it is the one door a tree with untraced code has — but every
    other bind this framework writes rests on a record that says which node the source encodes
    and why, and this one rests on the caller's say-so alone. The receipt is the only trace of
    that difference, because the entry this bind writes reads afterwards exactly like one a
    record justified — and how often this line shows up in reports is what will say whether the
    raw form costs more than it serves."""
    return (f"  this binding rests on no record: --bind wrote what the caller stated, and the "
            f"judgment behind it lives nowhere a reader can reopen. A delivery's record or a "
            f"reconciliation is the recorded route — for a hand edit over bound source, "
            f"/reconcile writes the same binding with the judgment kept. The trace carries no "
            f"mark of the difference on {node_id}; this line is the only one")


def stale_after(declared: dict, home: Path, acted: dict[str, str],
                bound: set[str]) -> list[tuple[str, str, str]]:
    """The bindings this act left stale, found at the one moment both sides are in hand.

    A bind restamps only the nodes it was handed. That leaves two kinds of binding asserting a
    digest the tree no longer holds, both knowable right now and both silent afterwards until
    somebody runs `--check`: another node's binding over a path this act just restamped — the
    fresh digest is already in memory and differs — and a path a bound node carried forward from
    an earlier bind whose file changed on its own. Only this act's neighborhood is read — the
    bound nodes' own entries and the paths this act wrote, never the whole trace: a receipt that
    restated every standing drift would bury the ones this act just made or met."""
    stale = []
    for entry in declared["bindings"]:
        node = entry["node"]
        for held in entry.get("files") or []:
            path, stored = held["path"], held["digest"]
            if node not in bound:
                if path in acted and stored != acted[path]:
                    stale.append((node, path, "this act restamped the file under another node"))
            elif path not in acted:
                source = home / path
                if not source.is_file():
                    stale.append((node, path,
                                  "carried forward from an earlier bind, and the file is gone"))
                elif spec.digest_of(source) != stored:
                    stale.append((node, path, "carried forward from an earlier bind, and the "
                                              "file has since changed"))
    return sorted(stale)


def code_report(findings: list[tuple[str, str, str | None, str]]) -> list[str]:
    """The `code` class, listed per file rather than per binding.

    A file bound by sixteen nodes that changes once is one act to take, not sixteen lines to
    read — the live consumer runs measured exactly that shape, one shared service file burying
    the report every time it moved. The remedy for this class is a reconciliation, and a
    reconciliation is invoked over a file set, so the listing is keyed the way the remedy
    consumes it: one line per file, naming every binding the change staled. Nothing about the
    findings themselves changes — the tally still counts bindings, `suppressed()` still counts
    both, and the trace still holds one entry per node — grouping is the listing's business
    and stops there."""
    grouped: dict[tuple[str, str], list[str]] = {}
    for _, node_id, where, why in findings:
        grouped.setdefault((where, why), []).append(node_id)
    return [f"{where}: {why} — {len(nodes)} binding(s): {', '.join(sorted(nodes))}"
            for (where, why), nodes in sorted(grouped.items())]


def suppressed(held: list[tuple[str, str, str | None, str]], prefixes: list[str]) -> str:
    """The receipt for the `code` findings a declared target held back. A count, never silence,
    and it follows the same discipline `released()` already sets for the trace's other loss: what
    a report stops saying it says once, in a line, so the reader can tell a clean tree from a tree
    whose findings were filed elsewhere. Without it the declaration would be the one thing in this
    framework a consumer could turn on and never measure again.

    The number is the point rather than the list, which is why the paths are behind `--all`: a
    surface that moves weekly produces this count by the hundred, and reprinting them here would
    rebuild exactly the unreadable report the declaration exists to prevent."""
    files = sorted({finding[2] for finding in held})
    return (f"  suppressed {len(held)} `code` finding(s) over {len(files)} file(s) under "
            f"{', '.join(prefixes)} — declared freely edited in {project.PROJECT_FILE}. "
            f"`--all` lists them, and that list is what /check-source reads to hold those files "
            f"to the rules a reading decides")


def left_stale(stale: list[tuple[str, str, str]]) -> str:
    """The receipt for the bindings a bind left stale. A statement, never a warning, the same as
    `released()`: nothing here is wrong yet — a bind restamps exactly the nodes it was handed,
    and that is the contract — but each line below is a `code` drift finding on the next
    `--check`, and this is the one moment the maker of the change is still holding it."""
    lines = [f"  this act leaves {len(stale)} binding(s) stale — a bind restamps only the nodes "
             f"it was handed:"]
    lines += [f"    {node}: {path} — {why}" for node, path, why in stale]
    lines.append("    each is a `code` drift finding on the next --check; a reconciliation over "
                 "these paths is the route, whatever wrote the change")
    return "\n".join(lines)


def opened(target: Path, spec_root: Path,
           home: Path) -> tuple[dict | None, str | None]:
    """The trace as it stands, ready to be folded into, or nothing and the reason. The first bind
    for a target root creates it; every later one is held to the same specification, and one
    naming a different specification is refused rather than silently repointed."""
    spec_relative = Path(os.path.relpath(spec_root.resolve(), home.resolve())).as_posix()
    declared = load(target) or {"specification": spec_relative, "bindings": []}
    if not isinstance(declared.get("specification"), str) or \
            not isinstance(declared.get("bindings"), list):
        return None, (f"{trace_path(target)} carries no specification and bindings; it is not a "
                      f"trace this can fold into — validate it first")
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
    print(unrecorded(node_id))
    if dropped:
        print(released(node_id, dropped))
    stale = stale_after(declared, home, {e["path"]: e["digest"] for e in traced}, {node_id})
    if stale:
        print(left_stale(stale))
    return 0


def frontmatter_of(record: Path) -> tuple[dict | None, str | None]:
    """One record's frontmatter as a mapping, or nothing and the reason it could not be read.

    Every way a file fails to be a record at all is the same failure to both callers here, and
    saying it twice is how the two drift into disagreeing about what a record even is."""
    if not record.is_file():
        return None, f"{record} does not exist"
    text, unreadable = spec.read_node(record)
    if text is None:
        return None, f"{record}: {unreadable}"
    match = spec.FENCE.match(text)
    if not match:
        return None, f"{record} carries no frontmatter fence; it is not a record this can read"
    try:
        front = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as broken:
        return None, f"{record}: frontmatter does not parse: {broken}"
    if not isinstance(front, dict):
        return None, f"{record}: frontmatter is not a mapping"
    return front, None


def accounted(front: dict) -> list[str]:
    """Every way a reconciliation's own paths fail to add up, once the contract has held.

    The schema says what a field may hold; this says whether the fields agree with each other, and
    it is the half that carries the risk. `--bind-record` binds every path a node's `encoded_at`
    names, so a path that reached the record without reaching its file set is ground the human
    never scoped, asserted in the one file this framework keeps after every plan is gone. The
    accounting runs both ways for the same reason a bind and a drift check do: a named file no node
    accounts for is a file somebody meant to reconcile and nothing did, and it would leave the
    record reading complete."""
    named = [entry["path"] for entry in front["files"]]
    problems = [f"files: {path} is named {named.count(path)} times; one entry per file"
                for path in sorted(set(named)) if named.count(path) > 1]

    seen: dict[str, int] = {}
    claimed: set[str] = set()
    for entry in front["nodes"]:
        node_id = entry["node"]
        seen[node_id] = seen.get(node_id, 0) + 1
        where = "encoded_at" if entry["conforms"] else "observed_at"
        for path in entry[where]:
            claimed.add(path)
            if path not in named:
                problems.append(f"{node_id}: {where} names {path}, which this record's file set "
                                f"does not; a reconciliation reaches only what the human scoped")
    problems += [f"nodes: {node_id} appears {count} times; one entry per node"
                 for node_id, count in sorted(seen.items()) if count > 1]

    unbound = front.get("unbound") or []
    for path in unbound:
        if path not in named:
            problems.append(f"unbound: {path} is not in this record's file set")
        if path in claimed:
            problems.append(f"unbound: {path} is also accounted for by a node; a file is one or "
                            f"the other, and the trace either holds a binding to it or does not")

    for path in sorted(set(named) - claimed - set(unbound)):
        problems.append(f"files: {path} is named and no node accounts for it; a file the trace "
                        f"binds nothing to belongs under `unbound`, said rather than left out")
    return problems


def reconciliation(record: Path) -> int:
    """Hold one reconciliation record to its contract, and write nothing.

    It is validated here and bound by `--bind-record`, the same split the delivery route already
    has between `bin/deliver.py` and this script. The difference is that no other script owns this
    contract: a reconciliation record exists to justify a bind and is read for nothing else, so
    inventing a script to hold it would be a fourth validator for one file class."""
    if not RECONCILE_CONTRACT.is_file():
        print(f"cannot run: {RECONCILE_CONTRACT} is missing; nothing can be validated without it",
              file=sys.stderr)
        return CANNOT_RUN

    front, refusal = frontmatter_of(record)
    if front is None:
        print(f"cannot run: {refusal}", file=sys.stderr)
        return CANNOT_RUN

    if record.parent.name != RECONCILE_DIR:
        print(f"cannot run: {record} does not sit under {RECONCILE_DIR}/; a record that justifies "
              f"a bind lives where the trace it justifies lives, and one filed anywhere else is a "
              f"judgment the next reader has no way to find", file=sys.stderr)
        return CANNOT_RUN

    schema = json.loads(RECONCILE_CONTRACT.read_text(encoding="utf-8"))
    problems = [f"{'/'.join(str(part) for part in error.path) or 'record'}: {error.message}"
                for error in Draft202012Validator(schema).iter_errors(front)]
    if not problems:
        problems = accounted(front)
    if problems:
        for problem in sorted(set(problems)):
            print(f"{record.name}: {problem}")
        print(f"\n{len(set(problems))} problem(s); this record binds nothing until they are gone.")
        return 1

    binds = [entry for entry in front["nodes"] if entry["conforms"]]
    held = [entry for entry in front["nodes"] if not entry["conforms"]]
    print(f"{record.name} holds: {len(front['files'])} file(s), {len(binds)} node(s) the judgment "
          f"cleared, {len(held)} it did not, {len(front.get('unbound') or [])} file(s) the trace "
          f"binds nothing to.")
    if held:
        print(f"--bind-record will write {len(binds)} binding(s) from this record and none for "
              f"{', '.join(entry['node'] for entry in held)}: a node without `encoded_at` is a "
              f"node this form cannot bind.")
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
    it. What this reads is two field names, defensively — which is also why a reconciliation record
    is read by this same form: it declares the same two, and `--reconciliation` is what held it to
    its own contract first."""
    front, refusal = frontmatter_of(record)
    if front is None:
        return [], [refusal]

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


def as_reconciliation(record: Path) -> dict | None:
    """The record read as a reconciliation, or nothing where it is not one.

    Two readers here need the same three-part guard — it sits under `siegard-reconcile/`, its
    frontmatter parses, and it declares this contract — and a delivery record must fall through
    every one of them, since `--bind-record` serves both forms. A record whose frontmatter is
    unreadable falls through silently on purpose: `encoded_in` already refused it, and one refusal
    per defect is enough."""
    if record.parent.name != RECONCILE_DIR:
        return None
    front, _ = frontmatter_of(record)
    if not isinstance(front, dict):
        return None
    version = front.get("contract_version")
    if not isinstance(version, str) or not version.startswith("siegard-reconcile/"):
        return None
    return front


def withheld(record: Path) -> list[str]:
    """Every node a reconciliation record answered for and did not clear. Empty for a delivery
    record, which has no such class.

    A reconciliation is bound node by node — a node without `encoded_at` is one this form cannot
    reach, which is the whole of the join between the judgment and the trace — so a record
    carrying a finding writes the bindings that cleared and stops there. That is the right act:
    every line it writes is one a judgment stands behind, and the node it could not write stays
    exactly as drifted as it was, which is what the next `--check` reports.

    What was missing was saying so here. `--reconciliation` names the held nodes before anything
    is written, but the bind's own output listed what it bound and nothing else, so a partial bind
    read exactly like a complete one at the only moment the person who ran it was still looking.
    A bind that quietly reconciles thirty-eight of forty is the report this framework spends its
    receipts preventing."""
    front = as_reconciliation(record)
    if front is None:
        return []
    return sorted({entry["node"] for entry in front.get("nodes") or []
                   if isinstance(entry, dict) and isinstance(entry.get("node"), str)
                   and entry.get("conforms") is False})


def left_owed(held: list[str], record: Path) -> str:
    """The receipt for the nodes a reconciliation did not clear, printed by the bind that wrote
    the rest. The same discipline `left_stale()` sets one class over: nothing here is wrong — the
    bind stated exactly what the judgment cleared — but each node below is still owed, and this is
    the one moment the person who ran it is still holding the whole set."""
    lines = [f"  {len(held)} node(s) of {record.name} the judgment did not clear, and this bind "
             f"wrote none of them:"]
    lines += [f"    {node}" for node in held]
    lines.append("    each stays as it stood — its drift, where the file was bound before, is "
                 "still a finding on the next --check, and the record says what was found "
                 "against it")
    return "\n".join(lines)


def unaccounted(record: Path, declared: dict, nodes: dict[str, dict],
                offset: Path) -> list[str]:
    """Every node the trace binds to a file this reconciliation names and the record says nothing
    about. Empty for a record that accounts for all of them, and for any record this does not apply
    to.

    `reconciliation.json` defines the node set as "every specification node the trace binds to a
    named file", and the skill that writes one says it in as many words — "what you keep is every
    node those findings name, and never a subset … reconciling a file against the part of the
    specification that happens to agree with it is the failure this whole route exists to prevent".
    Until this ran, nothing held a record to it: a record naming a file and answering for one of
    the two nodes bound to it would rebind that one and leave the other asserting a link nobody
    re-read, while reading exactly like a complete reconciliation.

    An orphaned binding is excluded. Its node is gone from the specification, no bind can repair it
    and `--prune` is the only thing that clears it, so demanding an answer for it would refuse a
    record over ground the route explicitly hands elsewhere.

    This is the one place this script reads a record as a reconciliation rather than as two field
    names. It is not a second opinion about somebody else's contract: `schemas/reconciliation.json`
    is trace.py's own, and `--reconciliation` is where it is enforced."""
    front = as_reconciliation(record)
    if front is None:
        return []

    named = {entry["path"] for entry in front.get("files") or []
             if isinstance(entry, dict) and isinstance(entry.get("path"), str)}
    if not named:
        return []
    # The record spells its paths from the target source root; the trace spells them from its own
    # directory. Compare in the trace's spelling, the way a bind writes them.
    anchored = named if str(offset) == "." else {(offset / p).as_posix() for p in named}

    answered = {entry["node"] for entry in front.get("nodes") or []
                if isinstance(entry, dict) and isinstance(entry.get("node"), str)}
    problems = []
    for entry in declared.get("bindings") or []:
        node_id = entry.get("node")
        if not isinstance(node_id, str) or node_id in answered or node_id not in nodes:
            continue
        for held in entry.get("files") or []:
            if isinstance(held, dict) and held.get("path") in anchored:
                problems.append(
                    f"{node_id} is bound to {held['path']}, which this record names, and the "
                    f"record answers for it nowhere; a reconciliation reads every node a named "
                    f"file answers to, never the subset that happened to agree")
                break
    return sorted(problems)


def bind_record(target: Path, spec_root: Path, record: Path, replace: bool = False) -> int:
    """Every binding one implementation record states, written as one act.

    Per node, the older form paid a full specification validation and a full read-and-rewrite of
    the trace. Here they are paid once, and the whole of it is refused before anything is written:
    a delivery half bound describes a link nobody made, and the file it would leave behind reads
    exactly like a complete one.

    Refused means over form. What a reconciliation's judgment held back is a different thing and
    is not refused here: those nodes carry no `encoded_at`, the rest are written, and `left_owed()`
    is what keeps the partial act legible."""
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
    if declared is not None:
        refusals += unaccounted(record, declared, nodes,
                               Path(os.path.relpath(target.resolve(), home.resolve())))
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
    acted = {entry["path"]: entry["digest"]
             for _, traced in folded for entry in traced}
    stale = stale_after(declared, home, acted, {node_id for node_id, _ in folded})
    if stale:
        print(left_stale(stale))
    owed = withheld(record)
    if owed:
        print(left_owed(owed, record))
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

    stale = sorted({finding[1] for finding in findings if finding[0] == ORPHANED})
    if not stale:
        held = len(declared.get("bindings") or [])
        print(f"nothing to prune: every one of {held} binding(s) names a node the specification "
              f"still holds")
        return 0

    gone = set(stale)
    declared["bindings"] = [entry for entry in declared["bindings"]
                            if entry.get("node") not in gone]
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
    if "--help" in args:
        # The docstring is this script's one home of what it does and how it is called,
        # so `--help` prints that rather than a second copy of it that could drift.
        print(__doc__.strip())
        return 0
    check = "--check" in args
    show_all = "--all" in args
    do_bind = "--bind" in args
    do_record = "--bind-record" in args
    do_prune = "--prune" in args
    do_reconciliation = "--reconciliation" in args
    replace = "--replace" in args
    args = [a for a in args
            if a not in ("--check", "--all", "--bind", "--bind-record", "--replace", "--prune",
                         "--reconciliation")]
    named = [name for name, given in (("--check", check), ("--bind", do_bind),
                                      ("--bind-record", do_record),
                                      ("--prune", do_prune),
                                      ("--reconciliation", do_reconciliation)) if given]
    if len(named) > 1:
        print(f"cannot run: {' and '.join(named)} are mutually exclusive", file=sys.stderr)
        return CANNOT_RUN
    if replace and not (do_bind or do_record):
        print("cannot run: --replace only applies to --bind and --bind-record", file=sys.stderr)
        return CANNOT_RUN
    if show_all and not check:
        print("cannot run: --all only applies to --check; it is what lists the findings a "
              "declared target holds back", file=sys.stderr)
        return CANNOT_RUN

    if do_reconciliation:
        if len(args) != 1 or args[0].startswith("--"):
            print("cannot run: expected --reconciliation <reconciliation-record>", file=sys.stderr)
            return CANNOT_RUN
        return reconciliation(Path(args[0]))
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
        print("cannot run: expected [--check [--all]] <target-root>", file=sys.stderr)
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

    home = home_of(target)
    findings, refusals = drift_of(declared, home)
    if refusals:
        for refusal in refusals:
            print(refusal)
        return 1

    # What a target declared freely edited is held back from the listing, never from the reading:
    # the finding was computed either way, and `--all` prints it. Suppression is a report's
    # decision about what a reader can act on, so nothing above it knows this happened.
    prefixes = [] if show_all else freely_edited(home)

    def held_back(finding) -> bool:
        return finding[0] == CODE and bool(finding[2]) and under(finding[2], prefixes)

    # Partitioned by the predicate rather than by membership in `held`: two findings that compare
    # equal would suppress each other, and the membership test walked `held` once per finding.
    held = [f for f in findings if held_back(f)]
    listed = [f for f in findings if not held_back(f)]

    if listed:
        # Class by class rather than one flat list: the tally is what a reader acts on, and the
        # orphaned count is what says how much of this report no rebind will ever shorten.
        # `code` alone is listed per file (code_report): its remedy is a reconciliation, which
        # is invoked over a file set, so its listing is keyed the way the remedy consumes it.
        for cls in (ORPHANED, MOVED):
            for finding in [f for f in listed if f[0] == cls]:
                print(finding[3])
        code_listed = [f for f in listed if f[0] == CODE]
        for line in code_report(code_listed):
            print(line)
        print(f"\n{len(listed)} drift finding(s) over {count} binding(s):")
        for cls in (ORPHANED, MOVED, CODE):
            # The suppressed count rides its own class's line rather than sitting under the tally:
            # `0 code` printed above a receipt saying one was held back is a line a reader can
            # finish and walk away from.
            also = f" ({len(held)} suppressed)" if cls == CODE and held else ""
            tally = sum(1 for f in listed if f[0] == cls)
            # The file count rides the code tally because the listing above is keyed by file:
            # `16 code over 2 file(s)` is what says sixteen findings are two acts, not sixteen.
            over = (f" over {len({f[2] for f in code_listed})} file(s)"
                    if cls == CODE and code_listed else "")
            print(f"  {tally} {cls}{over}{also}: {CLASSES[cls]}")
    else:
        print(f"no drift: {count} binding(s) match the specification and the code as both stand "
              f"now" if not held else
              f"no drift to act on: {count} binding(s), and every difference found sits under a "
              f"target this project declares freely edited")
    if held:
        print(suppressed(held, prefixes))
    return 1 if listed else 0


if __name__ == "__main__":
    raise SystemExit(main())
