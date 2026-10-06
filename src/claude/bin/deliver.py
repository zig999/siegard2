#!/usr/bin/env python3
"""Derive the delivery graph from the markdown delivery nodes, and refuse what breaks it.

The path is the identity. `implementation/<epic>/<slug>.md` and `proof/<epic>/<slug>.md` sit at
the path of the task they answer — `task/<epic>/<slug>` — and `review/<slug>.md` names one
review. No node carries an id, a type or a task field, so none of the three can disagree with
where the file sits, and the task a record answers is not something anybody types.

**The schema decides one file; this script decides what needs two — and what needs the plan.**
Per-node validation is `schemas/delivery-node.json` applied as written, plus the contradictions
one file can hold: a finding attributed to a pass that did not run, a `cause` on a pass that is
not the failures pass or missing from one that is, and a coverage or run reference that
disagrees with whether its pass ran. On top of that run the checks no per-file schema can
express: the task exists, a proof sits beside an implementation, every criterion of the task is
answered exactly once and nothing else is, every specification node the task implements is
answered, the plan pin matches the plan as it stands, and no task is delivered before the tasks
it declares it builds on. `run/` under the delivery root holds what the commands printed: kept
for a review to point at, never validated as a node. `orchestration.md` at the delivery root is
`/deliver-scope`'s log of its own run — a marker, never a node, kept the way plan.py keeps
`closure.md`.

**The plan is read through plan.py's own pipeline, and its plan.json for the one fact no node
file holds.** The nodes are collected and checked afresh, never taken from the index; what the
index alone carries is the anchor — the digest of each specification node a task implements, as
the derivation read it — and it is read through `plan.anchors`, the same reader `plan.py --check`
holds it through. An index whose edges are not what the nodes derive to, or a live one carrying no
anchors, is stale, and a delivery validated against a stale index reports a soundness nobody has;
both are a refusal to run, as a plan that does not hold together is: fix it with plan.py first. A
task whose implemented node no longer computes to its anchor waits on a re-bind in
`--outstanding`, and a record over it is refused — the node moved after the binder read it, and a
delivery against it answers text nobody cut the task from. A closed plan's index is never read.
The pin each record carries is the SHA-256 of its own task's file, so
`sha256sum <work-root>/task/<epic>/<slug>.md` computes the same value by hand — a record answers
one task, and that is what it is held to.

**There is no status here.** What is delivered is what has a record, and the record's presence
in git is the whole of that state — this script stores nothing about progress and no node
carries a field for it. `--outstanding` answers the question a status field would have answered,
from the tasks that have no record and the four things a delivery stops on — the dependencies
they declare, the substrate a task of this plan produces and the tree does not hold, a standing
`BLOCKING, from the specification —` note only a person settles, and an implemented node that
moved since the plan was derived, which a re-bind settles — so the answer is
derived from the files every time and can never be stale or wrong. It names the deliverable set
rather than leaving it to be subtracted by eye, and the report itself refuses nothing. The stops
it names are held where a record is validated: a record over a task whose `## Notes` still
carries a blocking note is refused, quoting the entry and naming both ways out of it, a record
over a task whose implemented node moved is refused naming the node, and a task
waits on a dependency until that dependency is delivered and proven — or delivered the substrate
alone, which no proof can hold up. A dependency delivered and never proven is source nobody
executed under a record saying it stands.

**A run is held to what it ran, never to the names it ran under.** A record that points at a run
is held to the registry's steps by name, by command and by working directory: each owed step
passed, the command it ran is the command the registry declares under that name — compared as
`bin/run.py` records it, one string per step, both sides normalised the same way — and the run's
`cwd` is the target source root. A step the caller added beyond the registry stands; one the
registry declares under a different command is a step nobody decided the rule under. The
working directory is held by its path within the project: the target root itself, or the same
path under another checkout of the project, which is what a git worktree is. A target that is its
project's whole tree has no path within it to hold, and the check says nothing there.

**Over a closed plan, the checks that hold a record to what stands beside it are receipts.** A
plan `closure.md` marks closed takes no further record — nothing delivers into it again — so a
refusal there stops no writer and only hides the index of a finished initiative behind a fact
nobody remains to settle. Six findings are receipted over a closed plan, printed with the index
and refused over a live one: a run's step under a command the registry does not declare under
that name, or a run from outside the target; a review naming no run over a registry declaring
commands; a review's green run that skipped a step the registry declares; a review's file set
narrower than what its tasks' records wrote; a dependency delivered and never proven; and a red
suite attempt the proof's `## Notes` does not name. No delivery node carries a contract version
of its own, so the plan's closure is the one fact that separates a record nobody will write
again from one being written now. Every other refusal holds over a closed plan as over a live
one.

**A deliverable set holding more than one task may be delivered in parallel, one git worktree
each — and this script is where that is said, because reading this report is where somebody
learns the set holds more than one.** No orchestrator ships for it: every guarantee holds per
worktree because each delivery is the ordinary `/implement-task` path, unvaried, and the parts
that are not a skill's are a person's, with two named exceptions below. The tempting substitute —
one general-purpose agent per task, handed the whole delivery — is not a variation of this route
but its undoing: a subagent cannot spawn the two producers, so the implementation and its proof
are written in one context and agree by construction — a parallel pass paid in full whose every
proof is then paid again through the ordinary route. Three preconditions: the plan is committed,
since a worktree sees commits and never trees; the tasks come from this set, so nothing in the
batch depends on anything else in it; and a task expected to install a package is delivered
alone, because the manifest is everybody's file and two deliveries editing it concurrently is the
one conflict no disjointness prevents.

One absence to expect rather than diagnose: a worktree carries commits and never gitignored
files, so an artifact the registry presupposes and git ignores — an `.env`, a credential file —
is absent in every fresh worktree, and the substrate check refuses each delivery before it
writes. That refusal is correct; reading this sentence first is cheaper than reading it K times.
`.worktreeinclude` at the repository root is the harness's own mechanism for carrying such files
into every new worktree; `--worktreeinclude` derives its lines from the same `presupposes` the
substrate check already reads, so the two can never name a different set. Writing the file with
those lines is still the consumer's act — a hand-added line for something no registry declares
stands untouched, and only running the flag with `--write` changes the file at all.

The first named exception is `role: prepare`: a command a registry declares to provision what one
worktree cannot share with another running the same suite concurrently — a test database schema
chief among them. It runs once per worktree, before `install`, and it is the consumer's own
command exactly as `install` and `suite` already are — this framework composes none of them and
authorizes no package, only the roles that order what the registry already named. The second is
`install` itself, run once up front instead of retyped from memory:

    git worktree add -b batch/<task> ../wt-<task> <base>   one per task
    per worktree:  deliver.py --worktreeinclude <standard> \
                        <target-source-root> --write        run from the new worktree's root
    per worktree:  run.py --step prepare=... --step install=...
                                                             the roles this registry declared, if any
    per worktree:  /implement-task <task>                  the ordinary invocation
    per worktree:  commit the delivery                     the orchestrator's act, never the skill's
    merge the branches, sequentially, resolving as below
    deliver.py <roots>                                     rederives delivery.json
    trace.py --bind-record ... <each record>               recomposes the trace's union
    /review-change over the union of the file sets         the integration gate
    git worktree remove; the branches are disposable

Exactly two files conflict and both are derived — `delivery.json` and `siegard-trace.json`. Take
either side; the content is disposable and the rederivation above is what completes the
resolution. Name the files that conflicted in the merge commit's message — the resolution is
mechanical and leaves the merge looking clean, so that message is the only place the fact of the
conflict survives, and how often this route conflicts is a number worth being able to read back.
**Never merge either by hand**: a hand-merged index is an index somebody authored, and
`--check` on both is what says the reconciliation is done. A conflict in *source* is a different
finding — the two tasks were not independent, so abort that branch's merge and re-deliver its task
alone on the integrated tree, because a file hand-merged between two deliveries is a file neither
record describes. A worktree that failed is discarded: its task stays recordless, `--outstanding`
reports it again, and nothing in the base repository has to be undone. Discard the checkout,
never the evidence: commit what the worktree holds and keep its branch unmerged before removing
it — an unmerged branch costs nothing until deliberately deleted, and its `run/` directories are
the captured record of the red attempts. A worktree removed uncommitted takes those captures with
it, and a run whose capture is gone did not happen. The commit is the orchestrator's act, exactly
as every commit on this route is.

Two limits, both real. The union is only exercised at the review — two tasks that each passed
alone are not a change that passes together, and the run that finds it is `/review-change`'s, at
the end. And the route buys wall-clock and isolation, never model cost: each invocation still pays
its own full reading.

**A project's own standard is the project's, and it stays in the project's own tree.** A record
names it by its own path relative to the target source root — the root `siegard.json`'s `targets`
declares under the key the record's `target` carries — and pins the SHA-256 of its text as read
when the record was written. Nothing is copied: this is
the same discipline `files[].path` already holds code to. The pin is a citation, not a standing
guarantee — like a task's `implements`, it is read once and never mechanically reverified against
the file as it stands today, so an old record stays held to the text it actually read even after
the project's registry moves on. What the pin does not do is freeze the rules: every citation a
record makes — a finding's `cites`, a departure's `cites` — resolves against the registry as it
stands, so a rule's id is permanent. Renaming a rule is declaring a new rule and retiring the old
one, and a registry that reused an id under a different statement would have every earlier record
citing it re-read against words nobody wrote at the time. `--standard <file>` validates a registry
on its own, which is what a consumer runs before any review reads it.

**delivery.json is derived, never edited.** It is refused entirely while the delivery has
problems: an index over a broken delivery reports a shape nobody decided. `--check` compares and
never repairs. This script answers pointed questions itself (`--outstanding`) and never reads
delivery.json to do it: both the index and the report derive from the nodes by the same
pipeline, so neither can disagree with the other, and neither can be stale. Nothing a standard
decides reaches the index, so the derivation stays a function of the delivery root alone.

Declared dependencies: PyYAML, jsonschema.

Usage:  deliver.py <delivery-root> <work-root> <target-source-root> [<specification-root>]
                                                        validate everything, then write
                                                        delivery.json
        deliver.py --check <delivery-root> <work-root> <target-source-root> [<specification-root>]
                                                        validate and compare; write nothing
        deliver.py --outstanding <delivery-root> <work-root> <target-source-root> [<specification-root>]
                                                        validate, then print every task with no
                                                        record, what each waits on, and the set
                                                        deliverable now; write nothing
        deliver.py --node <file> <delivery-root>
                                                        validate one file (cross-node checks,
                                                        plan checks and standard checks do not
                                                        run, so no other root is taken)
        deliver.py --standard <file> [--against DIR] [--specification DIR]
                                                        validate one project standard on its own;
                                                        stands alone, needs no root. With a tree
                                                        named, also say whether it holds what the
                                                        registry presupposes — exit 1 while any
                                                        of it is absent. With a specification root
                                                        named, also resolve every constraint a
                                                        step `decides` — exit 1 while one names a
                                                        node the specification does not hold — and
                                                        say which constraints no step decides
        deliver.py --standard <file> --reading [--for <path> ...]
                                                        print only the rules this registry marks
                                                        `decided_by: reading`, as JSON — narrowed,
                                                        with one or more --for, to the ones whose
                                                        scope reaches at least one named path.
                                                        What a reading judgment is handed in place
                                                        of the whole registry
        deliver.py --check-record <record> <target-source-root>
                                                        validate one source check record — the
                                                        reading /check-source leaves beside the
                                                        trace over files no task delivered — and
                                                        every citation it makes, against the
                                                        registry it pins
        deliver.py --unrecorded <target-source-root> <record> [<record> ...]
                                                        print every path the working tree
                                                        changed under the target source root —
                                                        against HEAD, untracked included — that
                                                        none of the named records names, outside
                                                        the framework's own roots; exit 1 while
                                                        any is. What a delivery runs over its own
                                                        records before it validates, since the
                                                        tree it started from was clean
        deliver.py --worktreeinclude <file> <target-source-root> [--write]
                                                        print every `presupposes` path, joined
                                                        onto the target source root, as
                                                        `.worktreeinclude` lines — the artifacts a
                                                        fresh worktree needs carried in because git
                                                        never carries a gitignored file across one.
                                                        `--write` merges the missing ones into
                                                        `.worktreeinclude` in the current directory
                                                        instead of printing; a line already there,
                                                        hand-written or not, is left alone
        deliver.py --contract <branch>
                                                        print one self-contained slice of
                                                        delivery-node.json — a `$defs` entry, or
                                                        every property one `kind` value admits —
                                                        with every `$ref` inlined; stands alone,
                                                        needs no root. What a delegation is handed
                                                        in place of the whole file
        The target source root is the one this invocation delivers into. Every record names its
        own by key, and resolves its `standard` reference and its paths at the root `siegard.json`
        declares under that key — read from the project file at the target's git toplevel, so a
        delivery whose records reach several targets validates whole under any one of them. The
        specification root is required while the plan is live, and ignored once closure.md marks
        it closed — the same rule plan.py applies, because the plan is read through it.
        deliver.py --help
                                                        print this text and stop
Exit:   0 sound (and, with --check, current)
        1 problems, or --check and delivery.json is stale
        2 cannot run (including a plan that does not hold together)
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import functools
import shlex
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

import plan
import project
import spec

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
DELIVERY_CONTRACT = PLUGIN_ROOT / "schemas" / "delivery-node.json"
DELIVERY_GRAPH_CONTRACT = PLUGIN_ROOT / "schemas" / "delivery.json"
STANDARD_CONTRACT = PLUGIN_ROOT / "schemas" / "standard.json"
DELIVERY_FILE = "delivery.json"
RUN_DIR = "run"
ORCHESTRATION_FILE = "orchestration.md"

KINDS = ("implementation", "proof", "review")
PAIRED = ("implementation", "proof")
HEADINGS = ["## What it is", "## Notes"]

SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def id_of(relative: Path) -> str | None:
    """The identifier this path computes to, or None where it computes to nothing."""
    if relative.suffix != ".md":
        return None
    parts = relative.with_suffix("").parts
    if len(parts) == 3 and parts[0] in PAIRED:
        pass
    elif len(parts) == 2 and parts[0] == "review":
        pass
    else:
        return None
    if not all(SLUG.fullmatch(p) for p in parts[1:]):
        return None
    return "/".join(parts)


def task_of(nid: str) -> str | None:
    """The task a paired record answers, read from its path — never from a field."""
    parts = nid.split("/")
    return f"task/{parts[1]}/{parts[2]}" if parts[0] in PAIRED else None


def contract() -> Draft202012Validator:
    """The delivery-node validator. The per-kind field table the contract carries needs no second
    reading here: `propertyNames` fires through the validator itself."""
    if not DELIVERY_CONTRACT.is_file():
        raise FileNotFoundError(
            f"{DELIVERY_CONTRACT} is missing; nothing can be validated without it")
    return Draft202012Validator(json.loads(DELIVERY_CONTRACT.read_text(encoding="utf-8")))


def resolve_refs(node: object, schema: dict, seen: frozenset[str] = frozenset()) -> object:
    """spec.py's, which is the one home of the rule — see its docstring. Delegated rather than
    copied: two copies of one rule drift apart the first time one is corrected and the other is
    not, and the import graph reaches spec.py from this file and plan.py alike."""
    return spec.resolve_refs(node, schema, seen)


def contract_branch(schema: dict, branch: str) -> dict | None:
    """spec.py's; see there."""
    return spec.contract_branch(schema, branch)


def contract_branches(schema: dict) -> list[str]:
    """spec.py's; see there."""
    return spec.contract_branches(schema)


def sliceable() -> list[Path]:
    """The contracts this script slices, in the order a refusal offers them: what a delivery
    records, and what the project's own registry declares. Both are this script's to validate, so
    both are its to print — a registry is the artifact a human authors by hand, and until this
    printed it the only home of what `commands[]` or a rule may declare was a file under the
    plugin's own `schemas/`, which a person with the question had to know was there."""
    return [DELIVERY_CONTRACT, STANDARD_CONTRACT]


def print_contract_index() -> int:
    """Every branch `--contract` answers for, by the contract it belongs to. A caller who knows
    the flag exists and not the names is the ordinary case, and a refusal is a poor way to learn
    them."""
    for path in sliceable():
        if not path.is_file():
            continue
        schema = json.loads(path.read_text(encoding="utf-8"))
        print(f"{schema.get('title', path.name)}  [{path.name}]")
        print(f"  {', '.join(contract_branches(schema))}")
    print("\nname one to print it whole, its `$ref`s resolved: deliver.py --contract <branch>")
    print("a plan node's contract is plan.py --contract")
    return 0


def print_contract_branch(schema_path: Path | None, branch: str) -> int:
    """`--contract`'s own body: find the contract that holds the branch, slice it, print the
    slice — or refuse, naming every branch each contract does answer for, because a refusal that
    only says "no" over a typo costs the same lookup twice.

    The branch is searched across the contracts this script owns rather than fixed to one, so a
    caller asking for `command` or `rule` reaches the registry's contract without having to know
    that a second schema exists. A name two of them held would be ambiguous, and none does —
    which is checked here rather than assumed."""
    paths = [schema_path] if schema_path is not None else sliceable()
    found = []
    for path in paths:
        if not path.is_file():
            continue
        schema = json.loads(path.read_text(encoding="utf-8"))
        sliced = contract_branch(schema, branch)
        if sliced is not None:
            found.append((path, sliced))
    if len(found) > 1:
        print(f"cannot run: {branch} is a branch of "
              f"{' and '.join(p.name for p, _ in found)}; the name is ambiguous and this script "
              f"will not pick one", file=sys.stderr)
        return CANNOT_RUN
    if not found:
        offered = "; ".join(f"{p.name}: {', '.join(contract_branches(json.loads(p.read_text(encoding='utf-8'))))}"
                            for p in paths if p.is_file())
        print(f"cannot run: {branch} is not a branch of any contract this script slices — "
              f"{offered}", file=sys.stderr)
        return CANNOT_RUN
    print(json.dumps(found[0][1], indent=2, ensure_ascii=False))
    return 0


@functools.lru_cache(maxsize=1)
def pass_names() -> tuple[str, ...]:
    """The passes a review answers for, read out of the contract rather than restated here. Read
    once: the file does not change under one invocation, and every caller wants the same list."""
    schema = json.loads(DELIVERY_CONTRACT.read_text(encoding="utf-8"))
    return tuple(schema["$defs"]["passName"]["enum"])


# The shape guard has one home, in spec.py: a list field read defensively, so that a string
# where a list belongs reports once from the schema instead of once per character.
listed = spec.listed


def texts(entries: list, field: str) -> list[str]:
    """The string values one field carries across a list of mappings, read defensively."""
    return [e[field] for e in entries
            if isinstance(e, dict) and isinstance(e.get(field), str)]


def ran_passes(front: dict, names: list[str]) -> set[str]:
    """The passes a review recorded as having run: an entry naming no missing input."""
    return {e["pass"] for e in listed(front, "passes")
            if isinstance(e, dict) and e.get("pass") in names and "missing" not in e}


def review_problems(front: dict, names: list[str]) -> list[str]:
    """One review against itself: the passes are total, and every field that depends on a pass
    having run agrees with whether it ran. A review reported as clean over a pass that never ran
    is the failure these checks refuse."""
    problems: list[str] = []
    entries = [e for e in listed(front, "passes") if isinstance(e, dict)]
    declared = [e["pass"] for e in entries if isinstance(e.get("pass"), str)]
    for name in names:
        if declared.count(name) == 0:
            problems.append(f"passes names no entry for `{name}`; every pass is answered for, "
                            f"and one that did not run says which input was missing")
        elif declared.count(name) > 1:
            problems.append(f"passes names `{name}` {declared.count(name)} times; "
                            f"a review records one answer per pass")

    ran = ran_passes(front, names)
    reviewed = [p for p in listed(front, "reviewed") if isinstance(p, str)]
    for index, finding in enumerate(listed(front, "findings")):
        if not isinstance(finding, dict) or not isinstance(finding.get("pass"), str):
            continue  # the schema already reported the shape
        name = finding["pass"]
        if name in names and name not in ran:
            problems.append(f"findings[{index}] is attributed to `{name}`, which did not run; "
                            f"a pass that did not run found nothing")
        # A pass that scans the file set is held to it. The failures pass is not: its subject is a
        # captured run, and a change breaks tests it never touched.
        if (name != "failures" and isinstance(finding.get("file"), str)
                and finding["file"] not in reviewed):
            problems.append(f"findings[{index}] is in {finding['file']}, which `reviewed` does "
                            f"not list; a finding outside the file set is a finding over "
                            f"something nobody said was under review")
        # Each of these fields belongs to exactly one pass, and both halves are held: a pass that
        # states nothing where its own field is required, and a pass that states another's.
        for field, owner, absent, foreign in (
                ("cause", "failures",
                 "a failure with no cause named is a failure nobody read",
                 "cause explains why a captured run failed and nothing else"),
                ("cites", "standard",
                 "a finding citing no rule is taste with a location attached",
                 "only a rule of the project's standard is cited, and only that pass reads one")):
            if name == owner and field not in finding:
                problems.append(f"findings[{index}] belongs to the {owner} pass and states no "
                                f"`{field}`; {absent}")
            if name != owner and field in finding:
                problems.append(f"findings[{index}] states `{field}` outside the {owner} pass; "
                                f"{foreign}")

    for field, name, want in (("coverage", "coverage", "the criteria it paired with tests"),
                              ("run", "failures", "the captured run it read"),
                              ("failures_counted", "failures",
                               "how many failures the run reported"),
                              ("standard", "standard",
                               "the standard it read and the rules that were in scope")):
        # `run` is the one field a pass that did not run may hold: a run that passed is
        # recorded as evidence and read by no pass, and `run_problems` holds the outcome to
        # the entry — a run that did not pass is a failures pass that ran.
        if field in front and name not in ran and field != "run":
            problems.append(f"`{field}` is present and the {name} pass did not run; "
                            f"a pass that did not run holds {want} over nothing")
        if field not in front and name in ran:
            problems.append(f"the {name} pass ran and `{field}` is absent; a pass that ran "
                            f"records {want}")

    # One direction only. `unpaired` present while the pass did not run is a claim about a reading
    # nobody made; `unpaired` absent while the pass ran is every review written under an earlier
    # version of this contract, which `unread_unpaired()` says as a receipt rather than refusing the root that
    # holds it.
    if "unpaired" in front and "coverage" not in ran:
        problems.append("`unpaired` is present and the coverage pass did not run; a pass that did "
                        "not run read no test for what no criterion derives")

    if "coverage" in ran and not listed(front, "tasks"):
        problems.append("the coverage pass ran and this review names no task; the criteria it "
                        "pairs tests with are the tasks', and without them it would be pairing "
                        "tests with criteria nobody wrote")

    counted = front.get("failures_counted")
    if isinstance(counted, int) and not isinstance(counted, bool):
        recorded = sum(1 for f in listed(front, "findings")
                       if isinstance(f, dict) and f.get("pass") == "failures")
        if counted != recorded:
            problems.append(f"failures_counted is {counted} and the failures pass recorded "
                            f"{recorded} finding(s); the two disagreeing is how a failure goes "
                            f"unexamined while the record still looks complete — read the run "
                            f"again and find out which is wrong, never lower the count or drop "
                            f"a finding to make the two agree")
    return problems


def standard_contract() -> Draft202012Validator:
    """The validator for a project's own standard. The registry is the project's artifact, so this
    framework holds it to a contract and authors none of its content."""
    if not STANDARD_CONTRACT.is_file():
        raise FileNotFoundError(
            f"{STANDARD_CONTRACT} is missing; a standard cannot be validated without it")
    return Draft202012Validator(json.loads(STANDARD_CONTRACT.read_text(encoding="utf-8")))


def load_standard(path: Path, validator) -> tuple[dict | None, list[str]]:
    """One standard, read and held to its contract. Returns nothing usable while it has problems:
    a review is never checked against a registry that does not hold together.

    Memoised on the resolved path for the length of one invocation: N records pinning one registry
    were N file reads and N full schema validations of the same bytes, and a file cannot change
    under a run that already refuses to write over a tree it did not read."""
    key = str(path.resolve()) if path.exists() else str(path)
    hit = _STANDARDS.get(key)
    if hit is not None:
        return hit
    found = _read_standard(path, validator)
    _STANDARDS[key] = found
    return found


_STANDARDS: dict[str, tuple[dict | None, list[str]]] = {}


def _read_standard(path: Path, validator) -> tuple[dict | None, list[str]]:
    """`load_standard` without the memo — the read itself."""
    if not path.is_file():
        return None, [f"{path} does not exist"]
    try:
        data = spec.load_yaml(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as broken:
        return None, [f"{path} cannot be read: {broken}"]
    if not isinstance(data, dict):
        return None, [f"{path} is a {type(data).__name__}, not a mapping"]

    problems = []
    for error in sorted(validator.iter_errors(data), key=str):
        where = ".".join(str(part) for part in error.absolute_path) or "the standard"
        problems.append(f"{where}: {error.message}")
    ids = [r["id"] for r in listed(data, "rules")
           if isinstance(r, dict) and isinstance(r.get("id"), str)]
    for value in sorted({i for i in ids if ids.count(i) > 1}):
        problems.append(f"declares `{value}` {ids.count(value)} times; two rules under one id "
                        f"cannot be told apart by the finding that cites it")
    for rule in listed(data, "rules"):
        if isinstance(rule, dict) and rule.get("decided_by") == "reading" and "tool" in rule:
            problems.append(f"{rule.get('id')} is decided by reading and names the tool "
                            f"`{rule['tool']}`; a rule is one or the other, and a rule a tool "
                            f"decides is not a review's to read")
    for field in ("presupposes", "dependencies"):
        for index, entry in enumerate(listed(data, field)):
            if not isinstance(entry, dict):
                continue
            for cited in listed(entry, "rules"):
                if isinstance(cited, str) and cited not in ids:
                    problems.append(f"{field}[{index}] names {cited}, which this registry does "
                                    f"not declare; naming a rule is how an entry says what it "
                                    f"costs, and one citing nothing that resolves is a cost "
                                    f"nobody can weigh")
    problems += command_problems(data) + package_problems(data)
    return (None if problems else data), problems


def command_problems(data: dict) -> list[str]:
    """One registry's commands, against itself and against the rules that expect them. The join is
    the step name: a rule says a tool decides it, a command says how that tool is run, and
    `bin/run.py` records the outcome under the same name. A registry that declares no command at
    all is held to none of this — it behaves the way every registry did before the field, with
    nothing running on its own and a review saying which rules went unanswered."""
    problems: list[str] = []
    entries = [c for c in listed(data, "commands") if isinstance(c, dict)]
    if not entries:
        return problems

    names = [c["step"] for c in entries if isinstance(c.get("step"), str)]
    for value in sorted({n for n in names if names.count(n) > 1}):
        problems.append(f"declares the step `{value}` {names.count(value)} times; a run records "
                        f"one outcome per step, and two commands under one name cannot both be it")

    for role in ("prepare", "install", "suite"):
        carrying = [c["step"] for c in entries if c.get("role") == role
                    and isinstance(c.get("step"), str)]
        if len(carrying) > 1:
            problems.append(f"{', '.join(sorted(carrying))} all carry the role `{role}`; a "
                            f"delivery runs one of them at a named moment, and which one is not "
                            f"something a caller may pick")

    declared = set(names)
    for rule in listed(data, "rules"):
        if not isinstance(rule, dict) or not isinstance(rule.get("tool"), str):
            continue
        if rule["tool"] not in declared:
            problems.append(f"{rule.get('id')} says the step `{rule['tool']}` decides it, and this "
                            f"registry declares no such command; a rule declared mechanical with "
                            f"nothing named to decide it is a rule nobody applies, which is worse "
                            f"than one nobody wrote")

    return problems


def package_problems(data: dict) -> list[str]:
    """One registry's authorized packages, against themselves. Checked whether or not the registry
    declares a command, because the list is an allowlist first and an install second: a name
    written twice is a record that resolves against one of two entries with no way to say which."""
    packages = [d["package"] for d in listed(data, "dependencies")
                if isinstance(d, dict) and isinstance(d.get("package"), str)]
    return [f"authorizes `{value}` {packages.count(value)} times; a record naming it resolves "
            f"against one entry, and two cannot both be the reason it was admitted"
            for value in sorted({p for p in packages if packages.count(p) > 1})]


def pin_of(path: Path) -> str:
    """The pin of a file's bytes, computable by hand as `sha256sum <path>`."""
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def in_scope(rule: dict, paths: list[str]) -> bool:
    return any(project.reaches(scope, path)
               for scope in listed(rule, "applies_to") for path in paths)


def standard_of(nid: str | None, front: dict, target: Path,
                validator) -> tuple[dict | None, str | None, list[str]]:
    """The standard a record read, from the project's own path in the target source root. The pin
    is a citation of what was read when the record was written — not a standing guarantee this
    resolves: like a task's `implements`, it is never mechanically reverified against the file as
    it stands today, so a project free to evolve its own registry cannot retroactively invalidate
    every record written against an earlier version of it. A citation that no longer resolves is
    reported on its own terms — the registry moved on, in a way this script does not diagnose
    further."""
    declared = front.get("standard")
    if not isinstance(declared, dict) or not isinstance(declared.get("at"), str):
        return None, None, []  # the schema already reported the shape

    at = declared["at"]
    if Path(at).is_absolute():
        # The schema anchors this path inside the target (`^[^/]`); joining an absolute one wins
        # the join outright, so a record that already failed its contract would send this script
        # reading a file anywhere on the machine.
        return None, at, [f"{f'{nid}: ' if nid else ''}{at} is absolute; a standard is read "
                          f"from inside {target}"]
    path = target / at
    lead = f"{nid}: " if nid else ""
    if not path.is_file():
        # The commonest wrong spelling is the right path under the wrong anchor: a record that
        # wrote the path from the repository root while the rule reads it from the target source
        # root. A bare "does not exist" sends each occurrence into its own fix-and-rerun
        # cycle — so the refusal hands the corrected spelling,
        # found by walking the target's ancestors, and ends the class in one cycle.
        for ancestor in target.resolve().parents:
            candidate = ancestor / at
            if candidate.is_file():
                corrected = Path(os.path.relpath(candidate, target.resolve())).as_posix()
                return None, at, [
                    f"{lead}{at}: does not resolve inside {target}; a record spells the "
                    f"standard's path relative to the target source root, never to the "
                    f"repository around it. The file stands at {candidate} — from the target "
                    f"that is spelled `{corrected}`"]
    data, found = load_standard(path, validator)
    return data, at, [f"{lead}{at}: {p}" for p in found]


def target_roots(target: Path) -> tuple[dict[str, Path], str | None]:
    """Every target source root the project declares, by key, read from `siegard.json` beside
    the trace — the same file `trace.py` reads `edits_freely` and `targets` from, for the same
    reason: which roots a project has is the consumer's declaration, not an invocation's. A record
    names its root by key, and this is the one place a key resolves."""
    home = project.toplevel_of(target)
    declared_at = home / "siegard.json"
    if not declared_at.is_file():
        return {}, (f"no project file at {declared_at}; every record names its target by the key "
                    f"`targets` declares there, and nothing else resolves one")
    try:
        declared = json.loads(declared_at.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as broken:
        return {}, f"{declared_at} cannot be read: {broken}"
    targets = declared.get("targets") if isinstance(declared, dict) else None
    if not isinstance(targets, dict) or not targets:
        return {}, f"{declared_at} declares no targets, so no record's target resolves"
    return {key: home / path for key, path in targets.items() if isinstance(path, str)}, None


def anchor_of(nid: str, front: dict, roots: dict[str, Path]) -> tuple[Path | None, list[str]]:
    """The target source root this record's paths are anchored at, by the key it names."""
    key = front.get("target")
    if not isinstance(key, str):
        return None, []  # the schema already reported the shape
    if key not in roots:
        return None, [f"{nid}: names target {key}, which siegard.json's `targets` does not "
                      f"declare (declared: {', '.join(sorted(roots)) or 'none'})"]
    return roots[key], []


def rules_of(data: dict) -> dict[str, dict]:
    return {r["id"]: r for r in listed(data, "rules")
            if isinstance(r, dict) and isinstance(r.get("id"), str)}


def read_run(record: Path, where: str) -> tuple[dict | None, str | None]:
    """One captured run.json, read and shaped, or the problem that says why it could not be.
    Exactly one of the two is set — three callers open this file for three different questions,
    and a guard added to one of them was never reaching the other two."""
    try:
        captured = json.loads(record.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as broken:
        return None, f"{where}/run.json cannot be read: {broken}"
    if not isinstance(captured, dict):
        return None, f"{where}/run.json is not a mapping"
    return captured, None


def record_run_problems(nid: str, front: dict, root: Path) -> list[str]:
    """One record that wrote something, against the run it points at. A record and its run are one
    act: the run is what the delivery saw before it wrote, so a record over a run that did not pass
    claims what the run denied. It is the exact mirror of `run_problems`, which refuses a review's
    run that passed — there, a green run is a diagnosis nobody should have asked for; here, a red
    one is a delivery that should not exist. The failure is not erased by either: the run that
    failed keeps its directory, and `bin/run.py` refuses to let any later run take its name."""
    where = front.get("run")
    if not isinstance(where, str):
        return []
    if Path(where).is_absolute():
        # The schema pins this to `run/<slug>`; an absolute value wins the join and would send
        # the read outside the delivery root the invocation named.
        return [f"{nid}: run names {where}, which is absolute; a run sits under {root}"]
    record = root / where / "run.json"
    if not record.is_file():
        return [f"{nid}: run names {where}, which holds no run.json; the runner writes one for "
                f"every run, so a directory without it is not a run this framework captured"]
    captured, unreadable = read_run(record, where)
    if captured is None:
        return [f"{nid}: {unreadable}"]
    if captured.get("outcome") != "passed":
        failed = captured.get("failed_step")
        return [f"{nid}: {where} ended `{captured.get('outcome')}` at the step `{failed}`, and "
                f"this record was written anyway; what a record says was delivered is what the "
                f"run it points at showed, and this one showed the opposite — fix what failed and "
                f"run again under a name of its own, or leave the record unwritten"]
    return []


def record_standard_problems(nid: str, front: dict, root: Path, target: Path, validator,
                             tfront: dict) -> list[str]:
    """Every rule a record that wrote something says it departed from — an implementation or a
    proof alike — resolved against the standard it names, plus every package it says it installed
    and whether the run its kind owes was captured at all. Unlike a review's citation a departure
    may name a rule a tool decides: a record obeys the whole standard, and departing from a rule
    the compiler owns is a real departure that the run will show. The validator holds the citation
    and says nothing about whether departing was right, which is a reader's to judge."""
    data, at, problems = standard_of(nid, front, target, validator)
    if data is None:
        return problems
    rules = rules_of(data)
    problems += installed_problems(nid, front, data, at)
    problems += owed_run_problems(nid, front, data, at, root, tfront)

    for index, entry in enumerate(listed(front, "divergences")):
        if not isinstance(entry, dict) or not isinstance(entry.get("cites"), str):
            continue  # reported by the shape checks, or a departure from something else
        cited, where = entry["cites"], entry.get("file")
        rule = rules.get(cited)
        if rule is None:
            problems.append(f"{nid}: divergences[{index}] cites {cited}, which {at} does not "
                            f"declare")
        elif isinstance(where, str) and not in_scope(rule, [where]):
            problems.append(f"{nid}: divergences[{index}] cites {cited} against {where}, which "
                            f"that rule's scope does not reach")
    return problems


def installed_problems(nid: str, front: dict, data: dict, at: str) -> list[str]:
    """Every package a record says it installed, against the list its standard authorizes. The
    list is where a human's approval of a package lives — the only place it survives the session it
    was given in — so a delivery that could install past it would make the approval decorative.
    The check is over names and never over a manifest: reading one would be reading a stack this
    framework ships no knowledge of."""
    authorized = {d["package"] for d in listed(data, "dependencies")
                  if isinstance(d, dict) and isinstance(d.get("package"), str)}
    return [f"{nid}: installed names {package}, which {at} does not authorize; a package this "
            f"registry has not admitted is one nobody approved, and the approval that admits it is "
            f"the registry gaining an entry — not an answer given while it was being installed"
            for package in listed(front, "installed")
            if isinstance(package, str) and package not in authorized]


def steps_that_passed(root: Path, where: str) -> dict[str, dict] | None:
    """The steps one captured run recorded as passed, by name, each with what the runner wrote of
    it — the command it ran above all — or `None` where the run cannot be read at all. The `None`
    matters: `record_run_problems` already refuses a record whose run holds no run.json or will
    not parse, and a second refusal here would name one missing file twice."""
    captured, _ = read_run(root / where / "run.json", where)
    return None if captured is None else passed_steps_of(captured)


def passed_steps_of(captured: dict) -> dict[str, dict]:
    return {step["name"]: step for step in listed(captured, "steps")
            if isinstance(step, dict) and isinstance(step.get("name"), str)
            and step.get("outcome") == "passed"}


def normalised(command: str) -> str:
    """One command line as `bin/run.py` records it: split by the shell's own rules and joined
    back, so a quoting difference between the registry's spelling and the runner's is not a
    different command. A line the shell cannot split is compared as written."""
    try:
        return shlex.join(shlex.split(command))
    except ValueError:
        return command


def within_project(target: Path) -> Path | None:
    """The target source root's path inside its project — relative to the git toplevel — or
    `None` where the target is the toplevel itself, which has no path within it to hold a
    working directory to."""
    home = project.toplevel_of(target)
    try:
        relative = target.resolve().relative_to(home.resolve())
    except ValueError:
        return None
    return None if relative == Path(".") else relative


def ran_in_target(cwd: str, target: Path) -> bool:
    """Whether a run's working directory is the target source root: the root itself, or the same
    path within the project under another checkout of it — a git worktree carries the whole tree
    at another toplevel, and a run captured there ran in the target as much as one captured
    here. A target that is its project's whole tree is held to itself alone, because no path
    within the project remains to compare, and a run anywhere would match it."""
    where = Path(cwd).resolve()
    if where == target.resolve():
        return True
    inside = within_project(target)
    if inside is None:
        return False
    parts = inside.parts
    return len(where.parts) > len(parts) and where.parts[-len(parts):] == parts


def held_run_problems(nid: str, where: str, owed: list[dict], at: str, root: Path,
                      target: Path) -> list[str]:
    """One captured run against the registry's steps it owes: each step that passed did so under
    the command the registry declares for that name, and the whole run was in the target source
    root. Whether every owed step passed is the coverage check's, stated once there. A step the
    caller added beyond the registry is not held: the registry says what must run, not what may.

    The name is the join and never the whole of it. A run recording `lint` as passed says a step
    called `lint` exited 0; what the rule `lint` decides needs is the registry's `lint` to have
    exited 0, and the only thing that ties the two is the command string the runner wrote beside
    the outcome. A run from another directory is the same gap one level up: the registry's
    commands are stated against the target source root, and a step run from anywhere else
    reports on a tree nobody delivered into."""
    captured, _ = read_run(root / where / "run.json", where)
    if captured is None:
        return []  # record_run_problems and run_problems name the run that cannot be read
    passed = passed_steps_of(captured)
    found: list[str] = []
    for command in owed:
        name, declared = command.get("step"), command.get("command")
        step = passed.get(name)
        if step is None or not isinstance(declared, str):
            continue  # a step that did not pass is the coverage refusal's, stated once
        ran = step.get("command")
        if isinstance(ran, str) and normalised(ran) != normalised(declared):
            found.append(f"{nid}: run {where} step {name} ran `{ran}` where the registry "
                         f"declares `{declared}`; a step is held to the command {at} declares "
                         f"under its name, because the name alone is what a rule's `tool` "
                         f"resolves to and a different command under it decided nothing that "
                         f"rule states")
    cwd = captured.get("cwd")
    if isinstance(cwd, str) and not ran_in_target(cwd, target):
        found.append(f"{nid}: run {where} ran in {cwd}, not the target {target}; the registry's "
                     f"commands are stated against the target source root, and a run from "
                     f"anywhere else reports on a tree this record did not deliver into")
    return found


def run_holding_problems(nodes: dict[str, dict], plan_nodes: dict[str, dict], root: Path,
                         roots: dict[str, Path], validator) -> list[str]:
    """Every record's run against the registry's commands and the target, through
    `held_run_problems`: a paired record over the steps its kind owes, a review over every step
    the registry declares but `prepare`. Held here, beside the coverage check rather than inside
    it, because the module docstring receipts this finding over a closed plan and refuses it
    over a live one, and the one place that knows which is `cross_problems`."""
    problems: list[str] = []
    for nid in sorted(nodes):
        node, front = nodes[nid], nodes[nid]["front"]
        where = front.get("run")
        if not isinstance(where, str) or Path(where).is_absolute():
            continue
        anchor, _ = anchor_of(nid, front, roots)
        if anchor is None:
            continue
        data, at, _ = standard_of(nid, front, anchor, validator)
        if data is None:
            continue
        task = task_of(nid)
        if node["kind"] == "review":
            owed = phase_steps([c for c in listed(data, "commands") if isinstance(c, dict)],
                               "suite")
        elif task in plan_nodes and plan_nodes[task]["kind"] == "task":
            owed = owed_steps(front, data, plan_nodes[task]["front"])
        else:
            continue
        if owed and (root / where / "run.json").is_file():
            problems += held_run_problems(nid, where, owed, at, root, anchor)
    return problems


def substrate_only(front: dict, tfront: dict, data: dict) -> bool:
    """Whether this record delivered the substrate and nothing any rule can reach.

    Two conditions, and neither alone is enough. The task declares `produces` — the same field,
    read the same way, that exempts it from the substrate check at the plan gate and at the situate
    step: the task building the artifacts every rule needs is the one task their absence cannot
    stop, and with no exemption nothing could ever build them. And nothing this record wrote sits in
    the scope of any rule the registry declares, which is what makes the other steps vacuous rather
    than merely inconvenient — a step decides a rule over a file, and there is no such file yet.

    The second condition is what keeps the first from being a licence. A task may declare `produces`
    and also write source, and source is not exempt from the steps that decide the rules reaching
    it. For a genuine substrate the condition holds by construction: `presupposes` exists for the
    artifacts no rule can ask for, a scope names a directory and an ending, and a path at the root
    of the tree has no separator to match one. So this refuses nothing anybody meant to write."""
    if not listed(tfront, "produces"):
        return False
    written, _ = wrote(front)
    return not any(in_scope(rule, sorted(written))
                   for rule in listed(data, "rules") if isinstance(rule, dict))


def phase_steps(commands: list[dict], phase: str) -> list[dict]:
    """The commands one phase of a delivery runs, in the order it runs them: the install first,
    because nothing reads a package before the install made it real, and the suite last and only
    in the suite phase, because it is held back until the tests exist. `setup` is the install
    alone — the whole of what runs before an implementer is spawned, and the whole of what a task
    declaring `produces` ever runs. One selection with two readers, on purpose: `check_standard`
    prints each phase composed for `bin/run.py`, and `owed_run_problems` holds the captured run
    to the same list — what a caller was handed to run and what the validator says was owed
    cannot drift apart while both are this function. `prepare` carries neither reader: it runs
    once per worktree, not once per task, so no phase here selects it and no delivery is held to
    having run it."""
    install = [c for c in commands if c.get("role") == "install"]
    middle = [c for c in commands if c.get("role") not in ("prepare", "install", "suite")]
    suite = [c for c in commands if c.get("role") == "suite"]
    if phase == "setup":
        return install
    if phase == "build":
        return install + middle
    return install + middle + suite


def owed_steps(front: dict, data: dict, tfront: dict) -> list[dict]:
    """The registry's steps one record owes a run of. What each kind owes differs because of when
    it is written — an implementation is written before any test exists, so it owes the checks
    that do not need one; a proof is written after, so it owes them all. One exemption, and it is
    `substrate_only`'s. It is an implementation's alone: a proof exists because tests exist, and
    a suite held back is the one thing a proof is for."""
    commands = [c for c in listed(data, "commands") if isinstance(c, dict)]
    kind = "proof" if "tests" in front else "implementation"
    owed = phase_steps(commands, "suite" if kind == "proof" else "build")
    if kind == "implementation" and substrate_only(front, tfront, data):
        owed = phase_steps(commands, "setup")
    return owed


def owed_run_problems(nid: str, front: dict, data: dict, at: str, root: Path,
                      tfront: dict) -> list[str]:
    """Whether a record captured the run its kind owes, and whether that run covered it — every
    owed step passed. A registry declaring how the project is installed and checked is a registry
    whose delivery could be run, and a delivery that could be run and was not is the state this
    whole arrangement exists to end: source handed over having never been executed, with every
    rule a tool decides unanswered by anything.

    Presence is not the whole question: a record pointing at a run of one step out of four is the
    same source nobody executed, declared executed. Nor is the step's name: a run whose `lint`
    passed under a command that is not the registry's `lint` decided nothing that rule states,
    and a run from another directory decided it over another tree. `held_run_problems` holds
    those two, for a delivery's run and a review's alike."""
    owed = owed_steps(front, data, tfront)
    if not owed:
        return []

    named = ", ".join(str(c.get("step")) for c in owed)
    where = front.get("run")
    if not isinstance(where, str):
        return [f"{nid}: {at} declares the step(s) {named} and this record captured no run; a "
                f"delivery whose project could be installed and checked and was not is source "
                f"nobody executed, which is exactly what a record pointing at a green run says "
                f"did not happen"]

    passed = steps_that_passed(root, where)
    if passed is None:
        return []  # record_run_problems names the run that cannot be read
    missing = [str(c.get("step")) for c in owed if c.get("step") not in passed]
    if not missing:
        return []

    covered = f"passed only {', '.join(sorted(passed))}" if passed else "passed no step of it"
    said = (f"{nid}: {at} declares the step(s) {named} and {where} {covered}; nothing decided the "
            f"rules {', '.join(missing)} own. A delivery that ran a fraction of the checks its own "
            f"registry declares is the same source nobody executed — run them and point at that "
            f"run")
    if listed(tfront, "produces"):
        said += (f". This task declares `produces` and would owe the install alone, but it wrote a "
                 f"file a rule of {at} reaches: what builds the substrate is exempt, and the "
                 f"source written beside it is not")
    return [said]


RECONCILE_DIR = "siegard-reconcile"
TRACE_FILE = "siegard-trace.json"


def review_reconciliation_problems(nid: str, front: dict, target: Path) -> list[str]:
    """The join between a review and the reconciliation record its conformance pass folded.

    Over a traced target the conformance pass judges every node the trace binds to the reviewed
    files — the delivery's own and every other node's claim on the same file — and binds what
    cleared, so the delivery's bind is not the last word on a file other nodes still answer for.
    The record that justifies that bind lives under `siegard-reconcile/` at the target's git
    toplevel, and this field is how a review names it. The join is held only where the record
    claims the field: a review naming a record over a pass that did not run cites a judgment nobody
    made, a record that is not there justifies nothing, and the record's own file set must be the
    review's — a reconciliation over fewer files than the review read is a pass that skipped part
    of the change, and over more is a scope nobody stated. A review that names none is not
    refused: every review written under an earlier version of this contract names none, and a
    field that became required refuses a consumer's whole delivery root the day the framework
    updates. What such a
    review did — judge the plan's nodes alone and leave every other binding of its files as it
    stood — `unreconciled_reviews()` says as a receipt."""
    named = front.get("reconciliation")
    if named is None:
        return []
    ran = "conformance" in ran_passes(front, pass_names())
    if not ran:
        return [f"{nid}: `reconciliation` is present and the conformance pass did not run; the "
                f"record it names is that pass's own fold, and a pass that did not run folded "
                f"nothing"]
    if not isinstance(named, str):
        return []  # the schema already reported the shape
    home = project.toplevel_of(target)
    record = home / named
    if not record.is_file():
        return [f"{nid}: `reconciliation` names {named}, and {record} does not exist; the path "
                f"is spelled from the target's git toplevel, where {RECONCILE_DIR}/ sits"]
    front_of = spec.parse_node(record)[0]
    if not isinstance(front_of, dict):
        return [f"{nid}: `reconciliation` names {named}, which carries no frontmatter this can "
                f"read"]
    recorded = sorted({e["path"] for e in listed(front_of, "files")
                       if isinstance(e, dict) and isinstance(e.get("path"), str)})
    reviewed = sorted(p for p in listed(front, "reviewed") if isinstance(p, str))
    if recorded != reviewed:
        missing = sorted(set(reviewed) - set(recorded))
        stray = sorted(set(recorded) - set(reviewed))
        parts = []
        if missing:
            parts.append(f"{named} accounts for none of {', '.join(missing)}")
        if stray:
            parts.append(f"{named} accounts for {', '.join(stray)}, which `reviewed` does not "
                         f"list")
        return [f"{nid}: {'; '.join(parts)}; the conformance pass is staged over the review's "
                f"own file set, whole, and a record over a different set judged a different "
                f"change"]
    return []



def unread_unpaired(nodes: dict[str, dict]) -> list[str]:
    """The receipt for a review whose coverage pass ran and that records no `unpaired` list. A
    statement, never a refusal, on the same terms as `unreconciled_reviews()`: every review written
    under an earlier version of this contract records none, and a field that became required would refuse a
    consumer's whole delivery root the day the framework updates. What such a review did not do is
    read its test set in the other direction — «a test with no obligation is a proof of something
    nobody stated» (SPEC-004 R15) — so a test of that kind may stand in its set unnamed, and the
    next review over those files is where the reading is made."""
    names = pass_names()
    unread = sorted(nid for nid, node in nodes.items()
                    if node["kind"] == "review"
                    and "coverage" in ran_passes(node["front"], names)
                    and "unpaired" not in node["front"])
    return [f"{nid}: the coverage pass ran and the review records no `unpaired` list; it paired "
            f"criteria with tests and never read the set for tests no criterion derives, so one "
            f"proving a fact nobody stated may stand there unnamed"
            for nid in unread]


def unreconciled_reviews(nodes: dict[str, dict], target: Path) -> list[str]:
    """The receipt for a review whose conformance pass ran over a traced target and folded no
    record. A statement, never a refusal, on the same terms as the standards line: nothing here is
    wrong by the contract the record was written under — but each such review read the plan's
    nodes alone, and every other node bound to the files it reviewed still asserts the digest that
    was there before the delivery, which `trace.py --check` reports as `code` drift and only a
    `/reconcile` over those files now closes."""
    home = project.toplevel_of(target)
    if not (home / TRACE_FILE).is_file():
        return []
    names = pass_names()
    unfolded = sorted(nid for nid, node in nodes.items()
                      if node["kind"] == "review"
                      and "conformance" in ran_passes(node["front"], names)
                      and "reconciliation" not in node["front"])
    return [f"{nid}: the conformance pass ran over a traced target and names no reconciliation "
            f"record; it judged the plan's nodes alone, and every other binding of the files it "
            f"reviewed stands as it stood before the delivery — `trace.py --check` reports those "
            f"as `code` drift, and a /reconcile over those files is what closes them"
            for nid in unfolded]


def review_standard_problems(nid: str, front: dict, target: Path, validator) -> list[str]:
    """Every citation a review makes, resolved against the standard it names. A review may only cite
    a rule the standard leaves to a reading — judging one a tool decides exactly would re-decide it
    in a model at worse recall, and would make the tool's own findings look like opinions. Which
    rules were in scope is not read from the record: it is a function of this reference and
    `reviewed`, and both sit in this root. The run the registry's commands make the review owe is
    `review_run_problems`'."""
    data, at, problems = standard_of(nid, front, target, validator)
    if data is None:
        return problems
    rules = rules_of(data)

    for index, finding in enumerate(listed(front, "findings")):
        if not isinstance(finding, dict) or finding.get("pass") != "standard":
            continue
        cited, where = finding.get("cites"), finding.get("file")
        if not isinstance(cited, str):
            continue  # the schema already reported it
        rule = rules.get(cited)
        if rule is None:
            problems.append(f"{nid}: findings[{index}] cites {cited}, which {at} does not declare")
        elif rule.get("decided_by") != "reading":
            problems.append(f"{nid}: findings[{index}] cites {cited}, which {at} says a tool "
                            f"decides; a rule a linter or a compiler decides exactly runs as a "
                            f"step of the project's own suite, and what it finds arrives through "
                            f"the failures pass instead")
        elif isinstance(where, str) and not in_scope(rule, [where]):
            problems.append(f"{nid}: findings[{index}] cites {cited} against {where}, which that "
                            f"rule's scope does not reach")
    return problems


def review_run_problems(nid: str, front: dict, target: Path, validator, root: Path) -> list[str]:
    """The run a registry's commands make a review owe. A registry declaring commands is a registry
    whose review runs them over the whole change — the one run that exercises the union of every
    task under review, which no delivery's own run did — so a review naming no run over such a
    registry is a review that read the change and never built it. The run it names is held to
    every step the registry declares other than `prepare`: a green run that skipped one proved
    nothing about the rules that step decides. A red run is held to what it ran, because the step
    it failed at is where the run stopped, and the failures pass is what reads it. The commands
    and the directory are `run_holding_problems`', for a review's run as for a delivery's."""
    data, at, _ = standard_of(nid, front, target, validator)
    if data is None:
        return []  # review_standard_problems reports the registry that does not resolve
    owed = phase_steps([c for c in listed(data, "commands") if isinstance(c, dict)], "suite")
    if not owed:
        return []
    named = ", ".join(str(c.get("step")) for c in owed)
    where = front.get("run")
    if not isinstance(where, str):
        return [f"{nid}: {at} declares the step(s) {named} and this review captured no run; the "
                f"review is the one run over the whole change, and a change reviewed without "
                f"being built is source nobody executed together — run them under this "
                f"review's name and point at that run"]
    if Path(where).is_absolute() or not (root / where / "run.json").is_file():
        return []  # run_problems names the run that is not there
    captured, _ = read_run(root / where / "run.json", where)
    if captured is None or captured.get("outcome") != "passed":
        return []
    passed = passed_steps_of(captured)
    missing = [str(c.get("step")) for c in owed if c.get("step") not in passed]
    if not missing:
        return []
    return [f"{nid}: {at} declares the step(s) {named} and {where} passed having run only "
            f"{', '.join(sorted(passed)) or 'none of them'}; nothing decided the rules "
            f"{', '.join(missing)} own, and a green run over a fraction of the registry is not "
            f"the change passing"]


def wrote(front: dict) -> tuple[set[str], str]:
    """Every path one record says it wrote, and the field that said so. An implementation writes
    `files`; a proof writes `tests`, and `files` for what it changed that holds no test. One
    expression serves either, so a departure is checked against the same rule whichever wrote it."""
    files = {f["path"] for f in listed(front, "files")
             if isinstance(f, dict) and isinstance(f.get("path"), str)}
    tests = {t["file"] for t in listed(front, "tests")
             if isinstance(t, dict) and isinstance(t.get("file"), str)}
    return (files | tests), ("files" if "files" in front else "tests")


def divergence_problems(front: dict) -> list[str]:
    """One record's disclosed departures, against itself. A departure names exactly one thing it
    departed from, and where a standard's rule is what it names, it says which file — so the
    citation can be checked against the scope the rule declares and a reader can open the place.
    Whether the departure was justified is nobody's here to decide."""
    problems: list[str] = []
    written, field = wrote(front)
    for index, entry in enumerate(listed(front, "divergences")):
        if not isinstance(entry, dict):
            continue  # the schema already reported the shape
        names_from, cites, where = "from" in entry, "cites" in entry, entry.get("file")
        if names_from and cites:
            problems.append(f"divergences[{index}] names both `from` and `cites`; one departure "
                            f"departs from one thing, and a rule of the standard is cited rather "
                            f"than described")
        elif not names_from and not cites:
            problems.append(f"divergences[{index}] names neither `from` nor `cites`; a departure "
                            f"from nothing stated is a departure nobody can pair with anything")
        if cites and not isinstance(where, str):
            problems.append(f"divergences[{index}] cites {entry['cites']} and names no `file`; a "
                            f"citation is checked against the scope its rule declares, and "
                            f"without a path there is nothing to check it against")
        if isinstance(where, str) and not cites:
            problems.append(f"divergences[{index}] names the file {where} and cites no rule; "
                            f"`file` locates a citation, and a departure described in prose is "
                            f"located in that prose")
        if isinstance(where, str) and where not in written:
            problems.append(f"divergences[{index}] names {where}, which `{field}` does not list; a "
                            f"departure sits in a file this record says it wrote")
        if cites and "standard" not in front:
            problems.append(f"divergences[{index}] cites {entry['cites']} and this record names no "
                            f"standard; a citation resolves against the standard the record names, "
                            f"and without one it names nothing")
    return problems


def node_problems(front, kind: str, validator, names: list[str]) -> list[str]:
    """Everything wrong with one delivery node on its own: the schema, applied as written, plus
    the contradictions a single file can hold."""
    if not isinstance(front, dict):
        return [f"frontmatter is a {type(front).__name__}, not a mapping"]
    if any(not isinstance(key, str) for key in front):
        return ["frontmatter carries a non-string key"]

    if "kind" in front:
        return ["carries `kind`, which the validator supplies from the path; a node that stated "
                "its own kind could disagree with where it sits, and the path is the identity"]

    problems: list[str] = []
    data = {**front, "kind": kind}
    for error in validator.iter_errors(data):
        where = ".".join(str(part) for part in error.absolute_path) or "frontmatter"
        problems.append(f"{where}: {error.message}")

    for field, quoted in (("criteria", "criterion"), ("coverage", "criterion"),
                          ("nodes", "node")):
        seen = texts(listed(front, field), quoted)
        for value in sorted({v for v in seen if seen.count(v) > 1}):
            problems.append(f"{field} answers for `{value}` {seen.count(value)} times; "
                            f"a record answers each of them once")

    if kind == "review":
        problems.extend(review_problems(front, names))
    if kind in PAIRED:
        problems.extend(divergence_problems(front))
        if "installed" in front and "standard" not in front:
            problems.append("`installed` names packages and this record names no standard; what "
                            "authorizes a package is a registry's own list, and without one the "
                            "names resolve against nothing")
    return problems


def body_problems(body: str) -> list[str]:
    headings = spec.headings_of(body)
    if headings != HEADINGS:
        return [f"body headings are {headings if headings else 'absent'}; "
                f"every delivery node carries exactly {HEADINGS}"]
    return []


def notes_of(body: str) -> str:
    """The text under `## Notes`, the section a record explains itself in."""
    _, found, notes = body.partition(HEADINGS[-1])
    return notes if found else ""


def red_suite_runs(nid: str, root: Path) -> list[str]:
    """Every run under the delivery root captured under this proof's suite name — `<epic>-<slug>-
    suite`, and the `-N` names a retry takes — whose outcome is not `passed`, as the runner named
    them. Read from the directory and never from a record, because the runs that failed are
    exactly the ones no record points at."""
    _, epic, slug = nid.split("/")
    suite = re.compile(rf"^{re.escape(epic)}-{re.escape(slug)}-suite(-[0-9]+)?$")
    red: list[str] = []
    runs = root / RUN_DIR
    if not runs.is_dir():
        return red
    for directory in sorted(runs.iterdir()):
        if not suite.fullmatch(directory.name) or not (directory / "run.json").is_file():
            continue
        captured, _ = read_run(directory / "run.json", f"{RUN_DIR}/{directory.name}")
        if captured is not None and captured.get("outcome") != "passed":
            red.append(directory.name)
    return red


def red_run_problems(nid: str, body: str, root: Path) -> list[str]:
    """A proof's `## Notes` against the red suite runs beside it. A suite that failed before it
    passed keeps every attempt's directory, and the proof names each red one with the cause its
    diagnosis returned — the diagnosis otherwise lives only in the conversation that made it,
    and a reader meeting three run directories beside one proof is owed the sentence that says
    why. Held as a substring of the section, so the run is named by its directory or by its
    `run/` path alike."""
    notes = notes_of(body)
    unnamed = [name for name in red_suite_runs(nid, root) if name not in notes]
    if not unnamed:
        return []
    return [f"## Notes names none of {', '.join(f'{RUN_DIR}/{n}' for n in unnamed)}, which "
            f"ran this task's suite and did not pass; a proof names each red attempt with the "
            f"cause its diagnosis returned, one sentence per run, because the cause otherwise "
            f"lives in no file"]


def references(nid: str, front: dict, kind: str) -> list[tuple[str, str, str]]:
    """Every reference this node declares: (target, edge kind, locator). `implements` and
    `reviews` point at tasks of the plan, `proves` at the implementation this proof sits beside,
    and `encodes` at the specification nodes the source now holds a fact of. Read defensively, because
    this also runs over nodes the schema has already reported."""
    refs: list[tuple[str, str, str]] = []
    if kind == "implementation":
        refs.append((task_of(nid), "implements", "the path"))
        for index, entry in enumerate(listed(front, "nodes")):
            if isinstance(entry, dict) and isinstance(entry.get("node"), str) \
                    and entry.get("encoded_at"):
                refs.append((entry["node"], "encodes", f"nodes[{index}]"))
    if kind == "proof":
        refs.append((f"implementation/{nid.split('/', 1)[1]}", "proves", "the path"))
    if kind == "review":
        for index, target in enumerate(listed(front, "tasks")):
            if isinstance(target, str):
                refs.append((target, "reviews", f"tasks[{index}]"))
    return refs


def settled_tasks(nodes: dict[str, dict], plan_nodes: dict[str, dict], roots: dict[str, Path],
                  validator) -> set[str]:
    """Every task a dependent may build on: delivered, and either proven or delivered as the
    substrate alone. A dependency is what has to stand first, and an implementation record
    without its proof is source nobody executed under a record saying it stands — a dependent
    written over it builds on a claim. The substrate is the one exemption, and it is
    `substrate_only`'s: what builds the artifacts every rule needs wrote nothing a test can
    reach, and holding it to a proof would hold it to a suite the registry held back."""
    proven = {task_of(nid) for nid, node in nodes.items() if node["kind"] == "proof"}
    settled: set[str] = set()
    for nid in sorted(nodes):
        node = nodes[nid]
        if node["kind"] != "implementation":
            continue
        task = task_of(nid)
        if task in proven:
            settled.add(task)
            continue
        planned = plan_nodes.get(task)
        if planned is None or planned["kind"] != "task":
            continue
        anchor, _ = anchor_of(nid, node["front"], roots)
        data = None
        if anchor is not None:
            data, _, _ = standard_of(nid, node["front"], anchor, validator)
        if substrate_only(node["front"], planned["front"], data or {}):
            settled.add(task)
    return settled


def unproven_dependency_problems(nid: str, tfront: dict, delivered: set[str],
                                 settled: set[str]) -> list[str]:
    """Every dependency this record's task builds on that is delivered and not settled — an
    implementation record with no proof beside it, over a task that did not deliver the
    substrate alone. Beside `implementation_problems` rather than in it because the module
    docstring receipts this over a closed plan and refuses it over a live one."""
    return [f"{nid}: the task declares it builds on {target}, which is implemented and no proof "
            f"record holds up; a dependency is delivered and proven before anything builds on "
            f"it, because an implementation without its proof is source nobody executed under a "
            f"record saying it stands — write the proof, or, where the task delivered the "
            f"substrate alone, nothing any rule reaches"
            for target in listed(tfront, "depends_on")
            if isinstance(target, str) and target in delivered and target not in settled]


def implementation_problems(nid: str, front: dict, task: dict, work: Path,
                            delivered: set[str], anchor: Path | None) -> list[str]:
    """One implementation against the task it answers: the task is not blocked, the criteria and
    the specification references are each answered in full, what the task produces was written
    and stands in the target, the dependencies it declares are delivered first, and the pin
    matches the plan as it stands. That a dependency is also proven is
    `unproven_dependency_problems`'."""
    problems: list[str] = []
    tfront = task["front"]
    tid = task_of(nid)

    for ref in task.get("moved") or []:
        problems.append(f"{nid}: answers {tid}, which implements {ref}, whose text moved since "
                        f"the plan was derived; a record over it answers the node as the binder "
                        f"never read it. Re-run /plan-work over this slug — the binder reads the "
                        f"node as it stands and the derivation refreshes the anchor — and hold "
                        f"the record to the task as it then stands")

    blocking = plan.blocking_notes_of(task.get("notes") or "")
    if blocking:
        problems.append(f"{nid}: answers {tid}, whose ## Notes carries `{blocking[0]}`; a "
                        f"record over a task the plan holds blocked encodes a contradiction "
                        f"the specification has not settled, as though the business had "
                        f"decided it, and only a person settles it. Two doors, and the record "
                        f"waits behind either: `/plan-work`, re-cutting the scope so it no "
                        f"longer asserts what the note names, or `/analyse`, amending the "
                        f"specification with the statement the note quotes. After either the "
                        f"task re-runs the implement-against step and the note is gone; the "
                        f"record is written then, against the task as it then stands")

    stated = [c for c in listed(tfront, "criteria") if isinstance(c, str)]
    answered = texts(listed(front, "criteria"), "criterion")
    for criterion in stated:
        if criterion not in answered:
            problems.append(f"{nid}: the task states the criterion `{criterion}`, and this "
                            f"record answers for no such criterion; a record answering only "
                            f"some of them cannot be read as complete")
    for criterion in answered:
        if criterion not in stated:
            problems.append(f"{nid}: criteria answers for `{criterion}`, which the task does "
                            f"not state; the criterion is quoted as the task states it, or it "
                            f"is a criterion nobody wrote")

    written, _ = wrote(front)
    for path in listed(tfront, "produces"):
        if not isinstance(path, str):
            continue
        if path not in written:
            problems.append(f"{nid}: the task says it produces {path}, and `files` does not list "
                            f"it; what a task produces is what its own standard presupposes — the "
                            f"artifact no rule can ask for and every rule needs — so a record "
                            f"claiming the task and not the artifact leaves the next delivery "
                            f"stopped on an absence this one was cut to end")
        elif anchor is not None and not Path(path).is_absolute() \
                and not (anchor / path).exists():
            problems.append(f"{nid}: the task says it produces {path}, `files` lists it, and "
                            f"{anchor} does not hold it; the claim that ends the substrate stop "
                            f"is held to the tree and not to the record alone, because every "
                            f"later delivery refuses on this artifact's absence and a record "
                            f"saying it stands is what would hide that it does not")

    said_stands = {p for p in listed(tfront, "stands") if isinstance(p, str)}
    record_stands = {p for p in listed(front, "stands") if isinstance(p, str)}
    if said_stands != record_stands:
        problems.append(f"{nid}: the task says its implementation stands at "
                        f"{', '.join(sorted(said_stands)) or 'nothing'} and this record says "
                        f"{', '.join(sorted(record_stands)) or 'nothing'}; a record answering a "
                        f"task whose implementation already stands writes no source and names "
                        f"exactly where it stands, and one that disagrees with its task is either "
                        f"source written under a proof task or a proof task delivered as source")
    elif anchor is not None:
        for path in sorted(record_stands):
            if not Path(path).is_absolute() and not (anchor / path).is_file():
                problems.append(f"{nid}: says the implementation stands at {path}, and "
                                f"{anchor} does not hold it; the proof this record pairs with "
                                f"is read against that file to certify the node, and a file "
                                f"that is not there certifies nothing")

    implements = sorted(plan.implements_of(tfront))
    accounted = texts(listed(front, "nodes"), "node")
    for node_ref in implements:
        if node_ref not in accounted:
            problems.append(f"{nid}: the task implements {node_ref}, and this record does not "
                            f"say how the source answers to it; a node the task implements "
                            f"passed over in silence is the specification going unanswered in "
                            f"code — answer it in `nodes`, or update the task's `implements` "
                            f"through /plan-work if it does not govern this work")
    for node_ref in accounted:
        if node_ref not in implements:
            problems.append(f"{nid}: nodes answers for {node_ref}, which the task does not "
                            f"implement; a record reaches exactly what the task implements, and "
                            f"more is work the plan does not declare")

    for index, target in enumerate(listed(tfront, "depends_on")):
        if isinstance(target, str) and target not in delivered:
            problems.append(f"{nid}: the task declares it builds on {target}, which no "
                            f"implementation record answers; the dependency is what has to be "
                            f"delivered first, and the records are how that is known")

    declared, actual = front.get("task"), task_pin(work, task_of(nid))
    if isinstance(declared, str) and actual is not None and declared != actual:
        problems.append(f"{nid}: task pin {declared} is not {task_of(nid)} as it stands ({actual}); "
                        f"the record answers a task that has since changed. Three ways out, and "
                        f"which one is right turns on what this record describes, not on the pin: "
                        f"deliver it again against the task as it now stands; restate the pin "
                        f"deliberately, where the change left what this record says untouched; or, "
                        f"where the source it describes no longer exists, delete the record, "
                        f"because a record of a delivery nothing holds has no subject, the way a "
                        f"review of a task nothing delivered has none. Only the source settles the "
                        f"third, and no root named here holds it. It is never the way past a pin "
                        f"that merely moved: a record deleted to clear a refusal is a test "
                        f"weakened to clear a suite, performed one root over")
    return problems


def review_plan_problems(nid: str, front: dict, plan_nodes: dict[str, dict],
                         delivered: set[str], names: list[str], root: Path) -> list[str]:
    """One review against the plan and the delivery: the tasks it names are delivered tasks, the
    coverage pass answers for every criterion of them, and the run it read exists."""
    problems: list[str] = []
    tasks = [t for t in listed(front, "tasks") if isinstance(t, str)]

    for index, target in enumerate(tasks):
        if target not in plan_nodes or plan_nodes[target]["kind"] != "task":
            problems.append(f"{nid}: tasks[{index}] names {target}, which the plan does not "
                            f"hold as a task")
        elif target not in delivered:
            problems.append(f"{nid}: tasks[{index}] names {target}, which no implementation "
                            f"record answers; a review of a task nothing delivered has no "
                            f"subject")

    if "coverage" in ran_passes(front, names) and tasks:
        stated = [c for target in tasks if target in plan_nodes
                  for c in listed(plan_nodes[target]["front"], "criteria")
                  if isinstance(c, str)]
        audited = texts(listed(front, "coverage"), "criterion")
        for criterion in stated:
            if criterion not in audited:
                problems.append(f"{nid}: the review names a task stating the criterion "
                                f"`{criterion}`, and coverage answers for no such criterion; "
                                f"an omitted criterion reads as one that passed")
        for criterion in audited:
            if criterion not in stated:
                problems.append(f"{nid}: coverage answers for `{criterion}`, which no task "
                                f"this review names states; the criterion is quoted as the "
                                f"task states it")

    problems.extend(run_problems(nid, front, root, names))
    return problems


def run_problems(nid: str, front: dict, root: Path, names: list[str]) -> list[str]:
    """One review against the run it read. The record says whether the failures pass ran and, if
    it did, how many failures it counted; this opens the run and holds both to it. A run that
    passed is recorded and read by no pass — the entry says the run passed, which is what was
    missing — and a run that did not pass is a failures pass that ran. Without that, every fact
    a review states about a run is the reviewer's own, and a review claiming the failures pass
    ran and found nothing over a run that failed passes every other check — which is exactly the
    failure the count was written to expose."""
    problems: list[str] = []
    where = front.get("run")
    if not isinstance(where, str):
        return problems
    read = "failures" in ran_passes(front, names)
    directory = root / where
    if not directory.is_dir():
        return [f"{nid}: run names {where}, which the delivery root does not hold; "
                f"the captured run is the evidence a diagnosis was read from"]

    record = directory / "run.json"
    if not record.is_file():
        return [f"{nid}: {where} holds no run.json; the runner writes one for every run, so a "
                f"directory without it is not a run this framework captured"]
    captured, unreadable = read_run(record, where)
    if captured is None:
        return [f"{nid}: {unreadable}"]

    outcome = captured.get("outcome")
    if outcome == "passed" and read:
        problems.append(f"{nid}: {where} passed, and the failures pass reads a run to say why it "
                        f"failed; a run holding no failure is a pass that should not have been "
                        f"asked for, and the entry says so instead")
    if outcome != "passed" and not read:
        problems.append(f"{nid}: {where} ended `{outcome}` and the failures pass did not run; a "
                        f"run that did not pass reported something, and a review recording the "
                        f"run without reading it leaves the failure unexamined under a record "
                        f"that looks complete")
    counted = front.get("failures_counted")
    if outcome != "passed" and counted == 0:
        problems.append(f"{nid}: {where} ended `{outcome}` and this review counted no failures; a "
                        f"run that did not pass reported something, and a count of none over it "
                        f"is how a failure goes unexamined while the record still looks complete")
    return problems


def demonstrates_problems(nid: str, front: dict, task: dict) -> list[str]:
    """Every node a proof's tests offer themselves as the proof of that its own task does not
    implement.

    A proof answers one task, and what that task took on is `implements`. A test claiming a node
    outside it claims ground the plan never gave the task — and the claim is not idle: a review
    certifies these, and a certification the auditor clears makes the trace decide that node by
    running this test from then on. The specification is not consulted here: a task's `implements`
    is already held to the specification by `bin/plan.py`, and a second opinion about that would
    be a second home for it."""
    implements = {n for n in listed(task, "implements") if isinstance(n, str)}
    problems = []
    for entry in listed(front, "tests"):
        if not isinstance(entry, dict) or not isinstance(entry.get("demonstrates"), str):
            continue
        node = entry["demonstrates"]
        if node not in implements:
            problems.append(
                f"{nid}: a test demonstrates {node}, which this task does not implement"
                + (f"; it implements {', '.join(sorted(implements))}" if implements
                   else " — the task implements none")
                + ". A proof answers its own task, and a review would certify this claim into a "
                  "binding the trace decides by running that test")
    return problems


def cross_problems(nodes: dict[str, dict], plan_nodes: dict[str, dict], work: Path,
                   names: list[str], root: Path, target: Path,
                   standard: Draft202012Validator | None = None, closed: bool = False,
                   receipts: list[str] | None = None) -> list[str]:
    """The rules that need to see more than one node at once — or the plan, or the project's own
    standard, read fresh from the target source root. Over a closed plan the findings the module
    docstring receipts land in `receipts` instead of being returned, worded as what they are."""
    problems: list[str] = []
    delivered = {task_of(nid) for nid, node in nodes.items()
                 if node["kind"] == "implementation"}
    roots, unresolvable = target_roots(target)
    if unresolvable:
        problems.append(unresolvable)
    validator = standard or standard_contract()
    settled = settled_tasks(nodes, plan_nodes, roots, validator)
    held: list[str] = run_holding_problems(nodes, plan_nodes, root, roots, validator)

    for nid in sorted(nodes):
        node, front = nodes[nid], nodes[nid]["front"]
        anchor, unresolved = anchor_of(nid, front, roots)
        problems.extend(unresolved)
        task = task_of(nid)
        if task is not None:
            if task not in plan_nodes or plan_nodes[task]["kind"] != "task":
                problems.append(f"{nid}: answers {task}, which the plan does not hold as a "
                                f"task; the path is the identity and this one names nothing")
                continue
            if anchor is not None:
                problems.extend(record_standard_problems(
                    nid, front, root, anchor, standard or standard_contract(),
                    plan_nodes[task]["front"]))
            elif isinstance(front.get("standard"), dict):
                problems.append(f"{nid}: names a standard, but its own target does not resolve; "
                                f"the citation, the installed packages and the run it owes are "
                                f"unchecked until `target` does")
            problems.extend(record_run_problems(nid, front, root))
            if node["kind"] == "implementation":
                problems.extend(implementation_problems(nid, front, plan_nodes[task], work,
                                                        delivered, anchor))
                held.extend(unproven_dependency_problems(nid, plan_nodes[task]["front"],
                                                         delivered, settled))
            else:
                problems.extend(demonstrates_problems(nid, front, plan_nodes[task]["front"]))
                pair = f"implementation/{nid.split('/', 1)[1]}"
                if pair not in nodes:
                    problems.append(f"{nid}: proves a task with no implementation record at "
                                    f"{pair}; what a proof holds up has to exist first")
                else:
                    declared = front.get("implementation")
                    actual = pin_of(root / f"{pair}.md")
                    if isinstance(declared, str) and declared != actual:
                        problems.append(
                            f"{nid}: the implementation pin is not {pair} as it stands ({actual}); "
                            f"the record these tests were written against has been rewritten and "
                            f"the proof has not — write the proof again, or restate the pin "
                            f"deliberately")
        if node["kind"] == "review":
            problems.extend(review_plan_problems(nid, front, plan_nodes, delivered,
                                                 names, root))
            if anchor is not None:
                problems.extend(review_standard_problems(nid, front, anchor, validator))
                held.extend(review_run_problems(nid, front, anchor, validator, root))
            elif isinstance(front.get("standard"), dict):
                problems.append(f"{nid}: names a standard, but its own target does not resolve; "
                                f"its citations and the run it owes are unchecked until "
                                f"`target` does")
            problems.extend(review_reconciliation_problems(nid, front, target))
            held.extend(review_set_problems(nid, front, nodes))
    return problems + receipted(held, closed, receipts)


def receipted(found: list[str], closed: bool, receipts: list[str] | None) -> list[str]:
    """The findings the module docstring receipts over a closed plan: returned as refusals over a
    live one, and over a closed one appended to `receipts` — worded as a receipt — and withheld
    from the refusals. The caller that prints receipts hands the list; one that only asks whether
    the delivery holds together hands none, and the receipts are dropped rather than refused."""
    if not closed:
        return found
    if receipts is not None:
        receipts.extend(f"{line} — a receipt, never a refusal: the plan is closed, nothing "
                        f"delivers into it again, and the record stands as written"
                        for line in found)
    return []


def review_set_problems(nid: str, front: dict, nodes: dict[str, dict]) -> list[str]:
    """The review's file set against the records of the tasks it answers: every path an
    implementation or a proof of those tasks says it wrote is in `reviewed`. The set is the
    caller's to state and never the review's to discover, and this is what holds the statement
    to the records: a review over fewer files than the tasks wrote is a review that skipped part
    of the change, and every pass it ran was clean over a set nobody delivered."""
    reviewed = {p for p in listed(front, "reviewed") if isinstance(p, str)}
    problems: list[str] = []
    for task in listed(front, "tasks"):
        if not isinstance(task, str) or not task.startswith("task/"):
            continue
        for kind in PAIRED:
            record = f"{kind}/{task[len('task/'):]}"
            if record not in nodes:
                continue
            written, field = wrote(nodes[record]["front"])
            missing = sorted(written - reviewed)
            if missing:
                problems.append(f"{nid}: `reviewed` does not list {', '.join(missing)}, which "
                                f"{record} says it wrote in `{field}`; a review answers for a "
                                f"task over every file its records wrote, and one over fewer "
                                f"was clean over a change nobody delivered")
            standing = {p for p in listed(nodes[record]["front"], "stands")
                        if isinstance(p, str)}
            unread = sorted(standing - reviewed)
            if unread:
                problems.append(f"{nid}: `reviewed` does not list {', '.join(unread)}, where "
                                f"{record} says the implementation stands; the proof of a task "
                                f"whose implementation already stood is certified against that "
                                f"file, and a review that did not read it certified nothing")
    return problems


def collect(root: Path, validator, names: list[str], closed: bool = False,
            receipts: list[str] | None = None) -> tuple[dict[str, dict], list[str]]:
    """Every node in the delivery, and everything wrong with the files as files. A proof's `##
    Notes` is held to the red suite attempts beside it here, where the body is read; over a
    closed plan that finding is a receipt, on the terms `cross_problems` states."""
    nodes: dict[str, dict] = {}
    problems: list[str] = []
    unnamed: list[str] = []
    for path in sorted(root.rglob("*.md")):
        relative = path.relative_to(root)
        if relative.parts[0] == RUN_DIR:
            continue  # what a run printed: material, never a node
        if relative.as_posix() == ORCHESTRATION_FILE:
            continue  # the orchestration log: it says what a run did, and is never a node
        nid = id_of(relative)
        if nid is None:
            problems.append(f"{relative.as_posix()}: not implementation/<epic>/<slug>.md, "
                            f"proof/<epic>/<slug>.md or review/<slug>.md; the path is the "
                            f"identity and this one computes to none. Material a judgment was "
                            f"read from belongs under run/, and an orchestration log is "
                            f"{ORCHESTRATION_FILE} at the delivery root; neither is validated "
                            f"as a node")
            continue
        front, body, unreadable = spec.parse_node(path)
        if front is None:
            problems.append(f"{nid}: {unreadable}")
            continue
        kind = relative.parts[0]
        problems += [f"{nid}: {p}"
                     for p in node_problems(front, kind, validator, names)]
        problems += [f"{nid}: {p}" for p in body_problems(body)]
        if kind == "proof":
            unnamed += [f"{nid}: {p}" for p in red_run_problems(nid, body, root)]
        if isinstance(front, dict):
            nodes[nid] = {"front": front, "kind": kind}
    return nodes, problems + receipted(unnamed, closed, receipts)


def load_plan(work: Path, specification: Path | None) -> tuple[dict[str, dict], list[str]]:
    """The plan, read through plan.py's own pipeline, with each live task's moved nodes under
    `moved` — read from plan.json's anchors through `plan.anchors`, so a stale or unanchored index
    is a problem here as it is under `plan.py --check`. A closed plan is read the way plan.py reads
    it: without opening today's specification, and without its index."""
    validator = plan.contract()
    if (work / plan.CLOSURE_FILE).is_file():
        spec_nodes = None
    else:
        spec_nodes, spec_problems = plan.load_base(specification)
        if spec_problems:
            return {}, spec_problems
    nodes, problems = plan.collect(work, validator)
    problems += plan.cross_problems(nodes, spec_nodes)
    if problems or spec_nodes is None:
        return nodes, sorted(set(problems))
    held, stale = plan.anchors(work, nodes, spec_nodes)
    if stale:
        return nodes, stale
    for task, refs in plan.moved(held, spec_nodes).items():
        if task in nodes:
            nodes[task]["moved"] = refs
    return nodes, []


def task_pin(work: Path, tid: str) -> str | None:
    """The pin of one task as it stands: the SHA-256 of its file's text, so
    `sha256sum <work-root>/<tid>.md` computes the same value by hand. None where the file is gone,
    which the plan checks report before this is consulted.

    It pins the task rather than the plan's derived index deliberately. The index carries the
    plan's shape and not each task's criteria, so pinning it would leave the one thing a record
    answers for uncovered while making every record in the root stale whenever any unrelated task
    is added — and no entry point owns re-pinning records it was forbidden to read."""
    path = work / f"{tid}.md"
    return pin_of(path) if path.is_file() else None


def derive(nodes: dict[str, dict], names: list[str]) -> dict:
    """The delivery graph a sound delivery derives to. Sorted throughout, so identical input is
    byte-identical output."""
    out_nodes, out_edges = [], []
    for nid in sorted(nodes):
        node, front = nodes[nid], nodes[nid]["front"]
        entry = {
            "id": nid,
            "kind": node["kind"],
            "file": f"{nid}.md",
            "title": front.get("title", ""),
            "summary": front.get("summary", ""),
        }
        task = task_of(nid)
        if task is not None:
            entry["task"] = task
        if node["kind"] == "implementation":
            unmet = sorted(e["criterion"] for e in listed(front, "criteria")
                           if isinstance(e, dict) and e.get("met") is False
                           and isinstance(e.get("criterion"), str))
            if unmet:
                entry["unmet"] = unmet
        if node["kind"] == "review":
            ran = sorted(ran_passes(front, names), key=names.index)
            if ran:
                entry["ran"] = ran
            unproven = sorted(e["criterion"] for e in listed(front, "coverage")
                              if isinstance(e, dict) and e.get("state") != "covered"
                              and isinstance(e.get("criterion"), str))
            if unproven:
                entry["unproven"] = unproven
            findings = len(listed(front, "findings"))
            if findings:
                entry["findings"] = findings
        out_nodes.append(entry)
        for target, edge_kind, at in references(nid, front, node["kind"]):
            out_edges.append({"from": nid, "to": target, "kind": edge_kind, "at": at})
    out_edges.sort(key=lambda e: (e["from"], e["kind"], e["at"], e["to"]))
    return {"contract_version": "siegard-delivery/2", "nodes": out_nodes, "edges": out_edges}


def check_single(root: Path, named: str, validator, names: list[str]) -> int:
    path = Path(named)
    if not path.is_absolute():
        path = (root / named) if (root / named).is_file() else Path.cwd() / named
    try:
        relative = path.resolve().relative_to(root.resolve())
    except ValueError:
        print(f"cannot run: {named} is not under {root}", file=sys.stderr)
        return CANNOT_RUN
    if relative.parts[0] == RUN_DIR:
        print(f"{relative.as_posix()}: sits under {RUN_DIR}/, which holds what the commands "
              f"printed and is never validated as a node")
        return 0
    if relative.as_posix() == ORCHESTRATION_FILE:
        print(f"{relative.as_posix()}: the orchestration log — what a /deliver-scope run did, "
              f"and never a node")
        return 0
    nid = id_of(relative)
    if nid is None:
        print(f"{relative.as_posix()}: the path computes to no identifier")
        return 1
    if not path.is_file():
        print(f"cannot run: {path} does not exist", file=sys.stderr)
        return CANNOT_RUN
    front, body, unreadable = spec.parse_node(path)
    if front is None:
        print(f"{nid}: {unreadable}")
        return 1
    problems = node_problems(front, relative.parts[0], validator, names)
    problems += body_problems(body)
    for problem in problems:
        print(f"{nid}: {problem}")
    if problems:
        return 1
    print(f"{nid}: sound on its own. Cross-node checks and plan checks did not run; "
          f"they run on the whole delivery.")
    return 0


def check_contract() -> Draft202012Validator:
    """The validator for a source check record. Held here rather than in a script of its own for
    the reason the reconciliation record is held in trace.py: a record has its validation where the
    thing it is about lives, and what this one is about is a standard, whose every other check is
    already here."""
    contract = PLUGIN_ROOT / "schemas" / "check.json"
    if not contract.is_file():
        raise FileNotFoundError(f"{contract} is missing; nothing can be validated without it")
    return Draft202012Validator(json.loads(contract.read_text(encoding="utf-8")))


def check_record(named: str, target_root: str) -> int:
    """Validate one source check record: its own contract, then every citation against the registry
    it pins, read fresh from the project's own path.

    The citation checks are the same three a review's are held to, and being the same is the point
    rather than a saving. A rule cited here and a rule cited in a review are answerable to one
    registry, and a reading that could cite a rule a tool decides — or hang one on a file that
    rule's scope does not reach — would produce findings a reader cannot tell from a review's while
    being held to less than a review's are."""
    try:
        validator = check_contract()
        standard_validator = standard_contract()
    except (FileNotFoundError, json.JSONDecodeError) as broken:
        print(f"cannot run: {broken}", file=sys.stderr)
        return CANNOT_RUN

    path, target = Path(named), Path(target_root)
    if not path.is_file():
        print(f"cannot run: {path} does not exist", file=sys.stderr)
        return CANNOT_RUN
    if not target.is_dir():
        print(f"cannot run: {target} is not a directory", file=sys.stderr)
        return CANNOT_RUN
    if path.parent.name != "siegard-check":
        print(f"cannot run: {path} does not sit under siegard-check/; a record of source held to "
              f"a standard lives beside the trace, and one filed anywhere else is a reading the "
              f"next reader has no way to find", file=sys.stderr)
        return CANNOT_RUN

    front, body, unreadable = spec.parse_node(path)
    if front is None:
        print(f"{path.name}: {unreadable}")
        return 1

    problems = [f"{'.'.join(str(p) for p in e.absolute_path) or 'top level'}: {e.message}"
                for e in sorted(validator.iter_errors(front), key=str)]
    problems += body_problems(body)
    if not problems:
        problems += check_citation_problems(front, target, standard_validator)

    for problem in problems:
        print(f"{path.name}: {problem}")
    if problems:
        print(f"\n{len(problems)} problem(s).")
        return 1

    findings = listed(front, "findings")
    reviewed = listed(front, "reviewed")
    print(f"check record sound: {path.name} holds {len(findings)} finding(s) over "
          f"{len(reviewed)} file(s) of target {front.get('target')}")
    print("  the rules a tool decides were not read here and are not answered by this record; "
          "they are the project's own suite's, over its whole tree")
    return 0


def check_citation_problems(front: dict, target: Path, validator) -> list[str]:
    """Every citation a check record makes, resolved against the standard it pins — declared, left
    to a reading, and in scope for the file. Held to the file set too: a finding outside it is a
    finding over something nobody said was under check."""
    # No node prefix: a check record is one file, and the reader already knows which.
    data, at, problems = standard_of(None, front, target, validator)
    if data is None:
        return problems
    rules = rules_of(data)
    reviewed = [p for p in listed(front, "reviewed") if isinstance(p, str)]

    # `unread` is the half of the file set this check did not read. Both statements its own
    # description makes are held here: an unread path is a path the set names, and a finding
    # cannot come out of a file nobody opened.
    unread = [p for p in listed(front, "unread") if isinstance(p, str)]
    for index, where in enumerate(unread):
        if where not in reviewed:
            problems.append(f"unread[{index}] names {where}, which `reviewed` does not list; "
                            f"unread names the files of the set that could not be read")

    for index, finding in enumerate(listed(front, "findings")):
        if not isinstance(finding, dict):
            continue
        cited, where = finding.get("cites"), finding.get("file")
        if isinstance(where, str) and where not in reviewed:
            problems.append(f"findings[{index}] is in {where}, which `reviewed` does not list; a "
                            f"finding outside the file set is a finding over something nobody "
                            f"said was under check")
        elif isinstance(where, str) and where in unread:
            problems.append(f"findings[{index}] is in {where}, which `unread` says this check "
                            f"could not read; a finding out of a file nobody opened states more "
                            f"than the reading has")
        if not isinstance(cited, str):
            continue
        rule = rules.get(cited)
        if rule is None:
            problems.append(f"findings[{index}] cites {cited}, which {at} does not declare")
        elif rule.get("decided_by") != "reading":
            problems.append(f"findings[{index}] cites {cited}, which {at} says a tool decides; a "
                            f"rule a linter or a compiler decides exactly is answered by the "
                            f"project's own suite, and re-deciding it in a model has strictly "
                            f"worse recall at more cost")
        elif isinstance(where, str) and not in_scope(rule, [where]):
            problems.append(f"findings[{index}] cites {cited} against {where}, which that rule's "
                            f"scope does not reach")
    return problems


def standards_held(nodes: dict[str, dict]) -> list[str]:
    """The standards this root's records were written against, and how many pin each. It is here
    because the one thing that silences the whole standard half of this framework is nobody naming
    a registry, and that is invisible from inside an invocation: a delivery written against no
    rules and one written against rules nobody handed over produce the same clean output. The root
    is what remembers. A path earlier records name, beside an invocation naming none, is the
    regression this line exists to make visible."""
    pinned: dict[tuple[str, str], int] = {}
    for node in nodes.values():
        declared = node["front"].get("standard")
        if isinstance(declared, dict) and isinstance(declared.get("at"), str):
            key = (str(node["front"].get("target")), declared["at"])
            pinned[key] = pinned.get(key, 0) + 1
    return [f"{at} (target {target}): pinned by {count} record(s); an invocation naming no "
            f"standard now writes source these rules will still be read against"
            for (target, at), count in sorted(pinned.items())]


def substrate_absences(plan_nodes: dict[str, dict], delivered: set[str],
                       target: Path) -> dict[str, tuple[list[str], list[str]]]:
    """Every outstanding task that builds the substrate, with what it declared and what of it the
    tree does not hold yet.

    It is here because this barrier is real and invisible. The task that produces what every rule
    needs takes no dependency edge and never will: an edge from every other task to it would be a
    fact somebody had to keep true by hand, so the plan states the artifacts instead and each
    delivery refuses on their absence. The consequence is that `waits on` alone is silent about
    the one task whose absence stops all the others, and a
    caller reading only it picks a task that will stop before it writes.

    Existence is the whole of the question, exactly as it is for what a registry presupposes:
    whether a manifest declares the right script is decided by running it, and a framework that
    read one would be reading a stack it ships no knowledge of."""
    absences: dict[str, tuple[list[str], list[str]]] = {}
    for tid in sorted(plan_nodes):
        node = plan_nodes[tid]
        if node["kind"] != "task" or tid in delivered:
            continue
        produces = [p for p in listed(node["front"], "produces") if isinstance(p, str)]
        absent = [p for p in produces if not (target / p).exists()]
        if absent:
            absences[tid] = (produces, absent)
    return absences


def outstanding_report(nodes: dict[str, dict], plan_nodes: dict[str, dict],
                       target: Path) -> str:
    """What the plan still holds and the delivery does not — derived from the records every
    time, which is why no field records it.

    It answers one question, and it answers it in the four terms a delivery actually stops on. A
    task waits on the dependencies it declares: a fact of the plan, read here rather than tracked.
    It waits on the substrate, where a task of this plan produces what the tree does not hold. And
    it waits on a person, where its `## Notes` still carries a standing `BLOCKING, from the
    specification —` entry. And it waits on a re-bind, where a node it implements no longer
    computes to the anchor plan.json holds for it. The first was the only one this report named,
    and the others were left to whoever read the files — which is how a caller chose a task that
    stopped two commands later, and how the deliverable set the handoff describes in words stayed
    something nobody computed. Beside those it quotes the underdetermined entries, which stop nothing: they are
    what a task's tests must exclude, `/implement-task` hands them to the test author quoted
    whole, and a set a script read is a set no eye had to collect.

    None of the four is a refusal here. This writes nothing and exits 0 over every state it can
    describe; the refusals are the records' — a record written over a blocked task, over a
    dependency nothing proves, or over a node that moved, is refused where the record is
    validated — and the skill about to write one is where the entry is quoted and both doors
    handed over ready to open. A
    dependency is waited on until it is settled: delivered and proven, or delivered as the
    substrate alone."""
    delivered = {task_of(nid) for nid, node in nodes.items()
                 if node["kind"] == "implementation"}
    proven = {task_of(nid) for nid, node in nodes.items() if node["kind"] == "proof"}
    roots, _ = target_roots(target)
    settled = settled_tasks(nodes, plan_nodes, roots, standard_contract())
    tasks = [tid for tid in sorted(plan_nodes) if plan_nodes[tid]["kind"] == "task"]
    absences = substrate_absences(plan_nodes, delivered, target)

    lines: list[str] = []
    ready: list[str] = []
    for tid in tasks:
        front = plan_nodes[tid]["front"]
        if tid in delivered:
            if tid not in proven:
                lines.append(f"{tid}: implemented, and no proof record holds it up"
                             + ("" if tid in settled else
                                "; nothing that builds on it is deliverable until one does"))
            continue
        waits = [t for t in listed(front, "depends_on")
                 if isinstance(t, str) and t not in settled]
        notes = plan_nodes[tid].get("notes") or ""
        blocking = plan.blocking_notes_of(notes)
        # Underdetermined entries bar nothing — they travel with the task to whoever writes the
        # tests — and they are quoted here so that set reaches /implement-task from a reading
        # rather than assembled by eye out of the task file.
        underdetermined = plan.underdetermined_notes_of(notes)
        rebind = plan_nodes[tid].get("moved") or []
        said = ["no record"]
        if waits:
            said.append(f"waits on {', '.join(sorted(waits))}")
        for ref in rebind:
            said.append(f"waits on a re-bind: {ref} moved since the plan was derived "
                        f"(/plan-work over this slug)")
        if tid in absences:
            said.append("produces the substrate every other delivery waits on")
        if blocking:
            said.append(f"{len(blocking)} standing BLOCKING note(s), which only a person settles")
        if underdetermined:
            said.append(f"{len(underdetermined)} UNDERDETERMINED note(s) the proof must exclude")
        lines.append(f"{tid}: {'; '.join(said)}")
        if tid in absences:
            produces, absent = absences[tid]
            lines += [f"  {path}: {'ABSENT' if path in absent else 'stands'}"
                      for path in produces]
        lines += [f"  {entry}" for entry in blocking + underdetermined]
        if not waits and not blocking and not rebind:
            ready.append(tid)

    if any(tid not in delivered for tid in tasks):
        if absences:
            ready = [tid for tid in ready if tid in absences]
        lines.append(deliverable_line(ready, bool(absences)))
    if not lines:
        lines = ["every task has a record, and every record its proof"]
    return "\n".join(lines + standards_held(nodes))


def deliverable_line(ready: list[str], barred: bool) -> str:
    """The set a caller may deliver now, stated once from the same pass that printed the reasons —
    so it can disagree with none of them. It is not a schedule and it is not an order: the plan
    refuses to hold either, and any of these may be taken next."""
    if not ready:
        return ("deliverable now: none — every task without a record waits on something named "
                "above")
    named = ", ".join(ready)
    if barred:
        return (f"deliverable now: {named} — the task(s) building what the tree does not hold. "
                f"Every other delivery stops before it writes while an artifact above is ABSENT, "
                f"so this is the whole of the set until one of these holds a record")
    parallel = ("" if len(ready) < 2 else
                " Any of them may also be delivered concurrently, one git worktree each — the"
                " preconditions and the two conflicts to expect are in this script's own"
                " docstring, and nothing here orchestrates it. Each worktree runs the ordinary"
                " /implement-task; delegating a whole delivery to one general-purpose agent is"
                " not that route — an agent cannot spawn the two producers, so the"
                " implementation and its proof land in one context, which is the pair this"
                " discipline exists to keep apart.")
    return (f"deliverable now: {named} — no record, nothing they wait on, no standing BLOCKING "
            f"note. Which one is the caller's to choose; nothing here orders them.{parallel}")


def substrate_report(data: dict, tree: Path) -> tuple[list[str], int]:
    """Which artifacts this registry presupposes the tree holds, and which it does not. Existence
    is the whole of the question: whether a manifest declares the right script is decided by
    running it, and a framework that read one would be reading a stack it ships no knowledge of.
    The absent ones carry the rules they take with them, because a refusal saying an artifact is
    missing tells nobody what it costs, and one naming eleven rules that cannot be applied tells
    them exactly."""
    lines, absent = [], 0
    for entry in listed(data, "presupposes"):
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            continue  # the contract already reported the shape
        where = entry["path"]
        rules = ", ".join(r for r in listed(entry, "rules") if isinstance(r, str))
        if (tree / where).exists():
            lines.append(f"  {where}: stands, and {rules} can be applied")
            continue
        absent += 1
        lines.append(f"  {where}: ABSENT — {entry.get('provides', '')}".rstrip())
        lines.append(f"      unanswerable while it is: {rules}")
    return lines, absent


def decides_report(data: dict, specification: Path) -> tuple[list[str], list[str]]:
    """Which Architecture Constraints this registry's steps decide, resolved against the
    specification, and which constraints the specification holds that no step decides. Existence is
    the whole of what is decided here, exactly as it is for what a registry presupposes: the nodes
    are read through spec.py's own collection and nothing more is asked of them, so a specification
    still being authored answers the same as a sound one. A `decides` naming a node the
    specification does not hold is a problem — a step holding the tree to a constraint nobody wrote
    decides nothing anybody can weigh. A constraint no step decides is a line and never a problem:
    it is held by reading alone, and naming which ones is what this report exists for."""
    nodes, _ = spec.collect(specification, spec.contracts())
    constraints = {identity for identity, node in nodes.items() if node["cls"] == "constraint"}
    decided: set[str] = set()
    lines: list[str] = []
    problems: list[str] = []
    for command in listed(data, "commands"):
        if not isinstance(command, dict) or not isinstance(command.get("step"), str):
            continue
        named = [c for c in listed(command, "decides") if isinstance(c, str)]
        if not named:
            continue
        lines.append(f"    {command['step']} decides {', '.join(named)}")
        for identity in named:
            if identity in constraints:
                decided.add(identity)
            else:
                problems.append(f"the step `{command['step']}` decides {identity}, which "
                                f"{specification} does not hold; a step holding the tree to a "
                                f"constraint nobody wrote decides nothing anybody can weigh")
    undecided = sorted(constraints - decided)
    if undecided:
        lines.append(f"    no step decides {', '.join(undecided)}: held by reading alone")
    elif constraints:
        lines.append("    every constraint the specification holds is decided by a step")
    else:
        lines.append(f"    {specification} holds no constraint")
    return lines, problems


def worktreeinclude_paths(data: dict, target_root: Path) -> list[str]:
    """Every `presupposes[].path` this registry declares, joined onto the target source root and
    printed as a `.worktreeinclude` line — the paths a fresh worktree needs carried in because git
    never carries a gitignored file across one. A path git already tracks is harmless to list
    twice; deciding which of these git ignores would read a stack this framework ships no
    knowledge of, so nothing here tries."""
    paths = []
    for entry in listed(data, "presupposes"):
        if isinstance(entry, dict) and isinstance(entry.get("path"), str):
            paths.append((target_root / entry["path"]).as_posix())
    return paths


def write_worktreeinclude(paths: list[str], dest: Path) -> list[str]:
    """`paths` merged into `dest`, one per line, in the order first seen — an existing line a
    consumer wrote by hand for something this registry does not declare is left standing, since
    this never repairs a file it does not own outright. Returns the lines actually added."""
    existing = dest.read_text(encoding="utf-8").splitlines() if dest.is_file() else []
    seen = set(existing)
    added = [p for p in paths if p not in seen]
    if added:
        with dest.open("a", encoding="utf-8") as handle:
            for path in added:
                handle.write(path + "\n")
    return added


def run_worktreeinclude(named: str, target: str, write: bool) -> int:
    """`--worktreeinclude`'s own body: load the registry, resolve `presupposes` onto the target
    source root, and either print the lines or merge them into `.worktreeinclude` in the current
    directory — the file the harness reads at the repository root, which this never assumes it
    is standing in."""
    try:
        validator = standard_contract()
    except (FileNotFoundError, json.JSONDecodeError) as broken:
        print(f"cannot run: {broken}", file=sys.stderr)
        return CANNOT_RUN
    path = Path(named)
    data, problems = load_standard(path, validator)
    for problem in problems:
        print(f"{path.name}: {problem}")
    if data is None:
        print(f"\n{len(problems)} problem(s). Nothing is printed or written from a registry that "
              f"does not hold together.")
        return 1
    target_root = Path(target)
    if not target_root.is_dir():
        print(f"cannot run: target source root {target_root} is not a directory", file=sys.stderr)
        return CANNOT_RUN
    paths = worktreeinclude_paths(data, target_root)
    if not paths:
        print("it presupposes nothing, so there is nothing a worktree needs carried in")
        return 0
    if not write:
        print("\n".join(paths))
        return 0
    dest = Path(".worktreeinclude")
    added = write_worktreeinclude(paths, dest)
    if added:
        print(f"{dest}: added {len(added)} line(s):")
        print("\n".join(f"  {p}" for p in added))
    else:
        print(f"{dest}: already carries every path this registry presupposes")
    return 0


FRAMEWORK_FILES = ("siegard.json", "siegard-trace.json", "siegard-reconcile", "siegard-check",
                   ".worktreeinclude")
FRAMEWORK_ROOTS = ("specification_root", "work_root", "delivery_root", "telemetry_root")


def framework_paths(home: Path) -> list[Path]:
    """Every path at the project's toplevel that the framework writes rather than a delivery:
    the roots `siegard.json` declares, and the files beside it the scripts own. A delivery into a
    target that is the whole tree writes its records under one of these, and none of them is the
    change a review reads source for."""
    found = [home / name for name in FRAMEWORK_FILES]
    try:
        declared = json.loads((home / "siegard.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return found
    if isinstance(declared, dict):
        found += [home / declared[key] for key in FRAMEWORK_ROOTS
                  if isinstance(declared.get(key), str) and declared[key].strip()]
    return found


def unrecorded(target: str, named: list[str]) -> int:
    """`--unrecorded`'s own body: every path the working tree changed under the target source
    root — against `HEAD`, staged, unstaged and untracked together — that none of the named
    records names, «Every path a delivery created, modified or deleted under its target source
    root is named by one of the delivery's records» (SPEC-004 R16).

    The tree is the witness, and it is a sound one only because the delivering invocation starts
    from a tree its own pathspec holds clean: what git shows changed under the target is what
    this delivery did. A record names a path under its own target's root, the same anchor every
    other check resolves it at, so a record over another target names nothing here."""
    import trace

    target_root = Path(target)
    if not target_root.is_dir():
        print(f"cannot run: target source root {target_root} is not a directory", file=sys.stderr)
        return CANNOT_RUN
    if not named:
        print("cannot run: expected --unrecorded <target-source-root> <record> ...; the records "
              "are what the tree is held to, and none was named", file=sys.stderr)
        return CANNOT_RUN
    roots, trouble = target_roots(target_root)
    if trouble is not None:
        print(f"cannot run: {trouble}", file=sys.stderr)
        return CANNOT_RUN
    recorded: set[Path] = set()
    for each in named:
        path = Path(each)
        if not path.is_file():
            print(f"cannot run: record {path} does not exist", file=sys.stderr)
            return CANNOT_RUN
        front, _, unreadable = spec.parse_node(path)
        if front is None:
            print(f"cannot run: {path}: {unreadable}", file=sys.stderr)
            return CANNOT_RUN
        anchor = roots.get(front.get("target")) if isinstance(front.get("target"), str) else None
        if anchor is None:
            print(f"cannot run: {path} names target {front.get('target')!r}, which siegard.json's "
                  f"`targets` does not declare", file=sys.stderr)
            return CANNOT_RUN
        written, _ = wrote(front)
        recorded |= {(anchor / p).resolve() for p in written}
    home = project.toplevel_of(target_root)
    changed, failed = trace.changed_paths(home, None)
    if failed is not None:
        print(f"cannot run: {failed}", file=sys.stderr)
        return CANNOT_RUN
    base = target_root.resolve()
    owned = [p.resolve() for p in framework_paths(home)]
    missing: list[str] = []
    for spelled in changed:
        where = (home / spelled).resolve()
        if where != base and base not in where.parents:
            continue
        if any(where == o or o in where.parents for o in owned):
            continue
        if where not in recorded:
            missing.append(where.relative_to(base).as_posix())
    if missing:
        for path in missing:
            print(f"unrecorded: {path}")
        print(f"\n{len(missing)} path(s) this tree changed under {target_root} that no named "
              f"record names. A source path goes in the implementation's `files`; a test file in "
              f"the proof's `tests`, or its `files` where the path holds no test `tests` names — "
              f"each with what the producer that changed it says it now does.")
        return 1
    print(f"every path this tree changed under {target_root} is named by the "
          f"{len(named)} record(s) given")
    return 0


def check_standard(named: str, against: str | None = None,
                   specification: str | None = None) -> int:
    """Validate one project standard on its own, so a consumer can hold a registry to its contract
    before any review reads it. Every root this framework validates has a validator; a standard is
    not a root, and this is the closest thing it gets. With a tree named, it also answers whether
    that tree holds what the registry presupposes — the one question about a standard that cannot
    be answered from the registry alone, and the one whose wrong answer is discovered a file at a
    time in a review instead of once, before the first of them. With a specification root named,
    it also resolves every constraint a step `decides` — the one question about a `decides` that
    cannot be answered from the registry alone — and names the constraints no step decides."""
    try:
        validator = standard_contract()
    except (FileNotFoundError, json.JSONDecodeError) as broken:
        print(f"cannot run: {broken}", file=sys.stderr)
        return CANNOT_RUN
    path = Path(named)
    data, problems = load_standard(path, validator)
    for problem in problems:
        print(f"{path.name}: {problem}")
    if data is None:
        print(f"\n{len(problems)} problem(s). A review is never checked against a standard that "
              f"does not hold together.")
        return 1
    rules = [r for r in listed(data, "rules") if isinstance(r, dict)]
    reading = sum(1 for r in rules if r.get("decided_by") == "reading")
    tools = [r["tool"] for r in rules if isinstance(r.get("tool"), str)]
    load = sorted({step: tools.count(step) for step in tools}.items())
    print(f"standard checked: {path} declares {len(rules)} rule(s) — {reading} decided by "
          f"reading, {len(rules) - reading} by a tool")
    print(f"  pin {pin_of(path)}")
    print(f"  the rules a tool decides run as step(s) "
          + (", ".join(f"{step} ({count} rule(s))" for step, count in load) or "named nothing")
          + f"; a review reads only the {reading} decided by reading")
    if load:
        # The counts are printed rather than the names because the number is what makes an author
        # look. A step exits 0 when it decided every rule resting on it and when it decided none —
        # a linter with no rule loaded for the files it read exits 0 over every one of them — and
        # nothing here can tell those apart without reading a stack it ships no knowledge of. What
        # it can do is show the weight, at the one moment somebody is in a position to check it.
        print("  what a step exits 0 over is the command exiting 0. Whether it is configured to "
              "decide the rule(s) resting on it is this registry's to know: nothing here reads a "
              "stack, and a step deciding nothing passes exactly like one deciding all of them")

    commands = [c for c in listed(data, "commands") if isinstance(c, dict)]
    if commands:
        roles = {c.get("role"): c.get("step") for c in commands if c.get("role")}
        # The timeout is printed beside each command because it is the one fact a caller composing
        # a run still had to open the registry for: the steps, the roles and the dependencies were
        # all here, and one missing number sent every invocation back to the whole file.
        print(f"  it declares {len(commands)} command(s): "
              + ", ".join(f"{c.get('step')} = {c.get('command')} "
                          f"({c.get('timeout_seconds')}s)" for c in commands))
        print(f"    prepares a fresh worktree with {roles.get('prepare') or 'nothing'}, "
              f"installs with {roles.get('install') or 'nothing'}, "
              f"proves with {roles.get('suite') or 'nothing'}, "
              f"and the rest run as checks on both sides of the tests")
        # Each phase composed and ready, because the prose rule ("everything except the suite,
        # install first") was interpreted at every delivery — and one omitted install cost a
        # full build to learn what this line says for free. What is printed is what
        # `owed_run_problems` holds the captured run to: the same function selects both.
        print("  each delivery phase, composed for bin/run.py — the delivery root, "
              "--run <slug> and --cwd stay the caller's, and the captured run is held to "
              "exactly these steps:")
        for phase in ("setup", "build", "suite"):
            steps = phase_steps(commands, phase)
            if not steps:
                print(f"    {phase}: nothing runs — no step carries the role this phase needs")
                continue
            largest = max(c.get("timeout_seconds") for c in steps
                          if isinstance(c.get("timeout_seconds"), int))
            args = " ".join("--step " + shlex.quote(f"{c.get('step')}={c.get('command')}")
                            for c in steps)
            print(f"    {phase}: --timeout-seconds {largest} {args}")
        print("    a task declaring `produces` runs the setup line where build is named and "
              "nothing at the suite — the substrate exemption, stated once here")
    else:
        print("  it declares no command: nothing runs on its own, and a review says which rules "
              "went unanswered")

    referenced = sum(len(listed(c, "decides")) for c in commands)
    unresolved: list[str] = []
    if specification is not None:
        root = Path(specification)
        if not root.is_dir():
            print(f"cannot run: {root} is not a directory", file=sys.stderr)
            return CANNOT_RUN
        lines, unresolved = decides_report(data, root)
        print(f"  against the specification at {root}:")
        print("\n".join(lines))
        for problem in unresolved:
            print(f"  {problem}")
        if unresolved:
            print(f"  {len(unresolved)} `decides` reference(s) do not resolve; a registry is never "
                  f"held against a constraint the specification does not hold")
    elif referenced:
        print(f"  {referenced} constraint reference(s) in `decides`, unresolved here; "
              f"--specification <root> resolves them and names the constraints no step decides")

    packages = [d for d in listed(data, "dependencies") if isinstance(d, dict)]
    print(f"  it authorizes {len(packages)} direct dependency(ies)"
          + (": " + ", ".join(str(d.get("package")) for d in packages) if packages else
             "; a package a delivery needs and this list omits is a stop that names it")
          + ". What they pull in transitively is nobody's approval and the lockfile's record")

    presupposed = listed(data, "presupposes")
    if against is None:
        print(f"  it presupposes {len(presupposed)} artifact(s)"
              + ("; --against <target-source-root> says whether they stand" if presupposed else
                 ": every rule is a condition over a file, and none needs one to exist first"))
        return 1 if unresolved else 0

    tree = Path(against)
    if not tree.is_dir():
        print(f"cannot run: {tree} is not a directory", file=sys.stderr)
        return CANNOT_RUN
    if not presupposed:
        print(f"  it presupposes nothing, so {tree} holds everything it needs to")
        return 1 if unresolved else 0
    lines, absent = substrate_report(data, tree)
    print(f"  against {tree}:")
    print("\n".join(lines))
    if absent:
        gone = ", ".join(e["path"] for e in presupposed
                         if isinstance(e, dict) and isinstance(e.get("path"), str)
                         and not (tree / e["path"]).exists())
        print(f"\n{absent} presupposed artifact(s) absent. Source written now answers to a "
              f"registry that cannot be applied to it: the rules above go unanswered, and the "
              f"absence is found once per file in a review instead of once here. The artifact is "
              f"built by a task that declares it in `produces`, planned through /plan-work — "
              f"ready below, but for the two roots only the caller knows:")
        print(f"\n  /plan-work\n"
              f"\n  Scope: the registry at {path} presupposes {gone}, absent from {tree}."
              f"\n  One cut: the task that produces {'them' if absent > 1 else 'it'}, declared in "
              f"`produces`, covering the rules named above."
              f"\n  Work root: <the plan this initiative runs under>"
              f"\n  Specification root: <the specification that plan implements against>"
              f"\n  Target source root: {tree}"
              f"\n  Project standard: {path}")
    return 1 if absent or unresolved else 0


def print_reading_rules(named: str, for_paths: list[str]) -> int:
    """The rules a reading judgment needs, and only those: every rule this registry marks
    `decided_by: reading`, narrowed to the ones `--for`'s paths reach where any were named. A
    rule a tool decides is not the reading pass's to see — `standard-conformance-reviewer.md`
    already says so, after the whole registry handed it that rule anyway — and a rule scoped away
    from every file this reading touches is the same absence for a different reason. This is the
    filter `in_scope` already computes for `cross_problems`, run here before a judgment starts
    instead of after one names a finding the registry never meant for it."""
    try:
        validator = standard_contract()
    except (FileNotFoundError, json.JSONDecodeError) as broken:
        print(f"cannot run: {broken}", file=sys.stderr)
        return CANNOT_RUN
    path = Path(named)
    data, problems = load_standard(path, validator)
    for problem in problems:
        print(f"{path.name}: {problem}")
    if data is None:
        print(f"\n{len(problems)} problem(s). A review is never checked against a standard that "
              f"does not hold together.")
        return 1
    rules = [r for r in listed(data, "rules") if isinstance(r, dict)]
    reading = [r for r in rules if r.get("decided_by") == "reading"]
    if for_paths:
        reading = [r for r in reading if in_scope(r, for_paths)]
    print(json.dumps(reading, indent=2, ensure_ascii=False))
    return 0


def main() -> int:
    args = sys.argv[1:]
    if "--help" in args:
        # The docstring is this script's one home of what it does and how it is called,
        # so `--help` prints that rather than a second copy of it that could drift.
        print(__doc__.strip())
        return 0
    verify = "--check" in args
    args = [a for a in args if a != "--check"]
    report = "--outstanding" in args
    args = [a for a in args if a != "--outstanding"]
    single = None
    if "--node" in args:
        at = args.index("--node")
        if at + 1 >= len(args):
            print("cannot run: --node takes a file", file=sys.stderr)
            return CANNOT_RUN
        single = args[at + 1]
        del args[at:at + 2]
    against = None
    if "--against" in args:
        at = args.index("--against")
        if at + 1 >= len(args):
            print("cannot run: --against takes a directory", file=sys.stderr)
            return CANNOT_RUN
        against = args[at + 1]
        del args[at:at + 2]
    specification = None
    if "--specification" in args:
        at = args.index("--specification")
        if at + 1 >= len(args):
            print("cannot run: --specification takes a directory", file=sys.stderr)
            return CANNOT_RUN
        specification = args[at + 1]
        del args[at:at + 2]
    if "--check-record" in args:
        at = args.index("--check-record")
        if at + 1 >= len(args):
            print("cannot run: --check-record takes a file", file=sys.stderr)
            return CANNOT_RUN
        named = args[at + 1]
        del args[at:at + 2]
        if verify or report or single is not None or against is not None \
                or specification is not None or len(args) != 1:
            print("cannot run: expected --check-record <record> <target-source-root>",
                  file=sys.stderr)
            return CANNOT_RUN
        return check_record(named, args[0])
    if "--unrecorded" in args:
        at = args.index("--unrecorded")
        rest = args[at + 1:]
        del args[at:]
        if verify or report or single is not None or against is not None \
                or specification is not None or args or not rest \
                or any(a.startswith("--") for a in rest):
            print("cannot run: expected --unrecorded <target-source-root> <record> ...",
                  file=sys.stderr)
            return CANNOT_RUN
        return unrecorded(rest[0], rest[1:])
    if "--contract" in args:
        at = args.index("--contract")
        branch = args[at + 1] if at + 1 < len(args) and not args[at + 1].startswith("--") \
            else None
        del args[at:at + 1 + (1 if branch is not None else 0)]
        if verify or report or single is not None or against is not None \
                or specification is not None or args:
            print("cannot run: --contract stands alone, with a branch name at most",
                  file=sys.stderr)
            return CANNOT_RUN
        return print_contract_index() if branch is None else print_contract_branch(None, branch)
    if "--worktreeinclude" in args:
        at = args.index("--worktreeinclude")
        if at + 1 >= len(args):
            print("cannot run: --worktreeinclude takes a file", file=sys.stderr)
            return CANNOT_RUN
        named = args[at + 1]
        del args[at:at + 2]
        write = "--write" in args
        args = [a for a in args if a != "--write"]
        if verify or report or single is not None or against is not None \
                or specification is not None or len(args) != 1:
            print("cannot run: expected --worktreeinclude <file> <target-source-root> [--write]",
                  file=sys.stderr)
            return CANNOT_RUN
        return run_worktreeinclude(named, args[0], write)
    if "--standard" in args:
        at = args.index("--standard")
        if at + 1 >= len(args):
            print("cannot run: --standard takes a file", file=sys.stderr)
            return CANNOT_RUN
        named = args[at + 1]
        del args[at:at + 2]
        reading = "--reading" in args
        args = [a for a in args if a != "--reading"]
        for_paths: list[str] = []
        while "--for" in args:
            at = args.index("--for")
            if at + 1 >= len(args):
                print("cannot run: --for takes a file", file=sys.stderr)
                return CANNOT_RUN
            for_paths.append(args[at + 1])
            del args[at:at + 2]
        if for_paths and not reading:
            print("cannot run: --for narrows --reading; it has no effect without it",
                  file=sys.stderr)
            return CANNOT_RUN
        if reading:
            if verify or report or single is not None or against is not None \
                    or specification is not None or args:
                print("cannot run: --reading stands with --standard and --for at most",
                      file=sys.stderr)
                return CANNOT_RUN
            return print_reading_rules(named, for_paths)
        if verify or report or single is not None or args:
            print("cannot run: --standard stands alone, with --against and --specification at "
                  "most", file=sys.stderr)
            return CANNOT_RUN
        return check_standard(named, against, specification)
    if against is not None:
        print("cannot run: --against says which tree a standard is held against, and only "
              "--standard holds one", file=sys.stderr)
        return CANNOT_RUN
    if specification is not None:
        print("cannot run: --specification says which specification a standard's `decides` "
              "resolve against, and only --standard holds one", file=sys.stderr)
        return CANNOT_RUN
    if report and (verify or single is not None):
        print("cannot run: --outstanding stands alone", file=sys.stderr)
        return CANNOT_RUN

    if single is not None:
        if verify or len(args) != 1 or any(a.startswith("--") for a in args):
            print("cannot run: expected --node <file> <delivery-root>; one file is validated "
                  "against its contract and the delivery root it sits under, and nothing else "
                  "is opened", file=sys.stderr)
            return CANNOT_RUN
        root = Path(args[0])
        if not root.is_dir():
            print(f"cannot run: delivery root {root} is not a directory", file=sys.stderr)
            return CANNOT_RUN
        try:
            validator = contract()
            names = pass_names()
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as broken:
            print(f"cannot run: {broken}", file=sys.stderr)
            return CANNOT_RUN
        return check_single(root, single, validator, names)
    if len(args) not in (3, 4) or any(a.startswith("--") for a in args):
        print("cannot run: expected [--check | --outstanding] "
              "<delivery-root> <work-root> <target-source-root> [<specification-root>], "
              "or --standard <file>, or --contract <branch>, on its own", file=sys.stderr)
        return CANNOT_RUN

    root = Path(args[0])
    if not root.is_dir():
        print(f"cannot run: delivery root {root} is not a directory", file=sys.stderr)
        return CANNOT_RUN
    work = Path(args[1])
    if not work.is_dir():
        print(f"cannot run: work root {work} is not a directory", file=sys.stderr)
        return CANNOT_RUN

    try:
        validator = contract()
        names = pass_names()
        standard = standard_contract()
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as broken:
        print(f"cannot run: {broken}", file=sys.stderr)
        return CANNOT_RUN

    target = Path(args[2])
    if not target.is_dir():
        print(f"cannot run: target source root {target} is not a directory", file=sys.stderr)
        return CANNOT_RUN
    closed = (work / plan.CLOSURE_FILE).is_file()
    specification = Path(args[3]) if len(args) == 4 else None
    if not closed:
        if specification is None:
            print("cannot run: a live plan validates against its specification, and this "
                  "validates against the plan; name the specification root", file=sys.stderr)
            return CANNOT_RUN
        if not specification.is_dir():
            print(f"cannot run: specification root {specification} is not a directory",
                  file=sys.stderr)
            return CANNOT_RUN

    plan_nodes, plan_problems = load_plan(work, specification)
    if plan_problems:
        for problem in plan_problems:
            print(problem, file=sys.stderr)
        print(f"cannot run: the plan at {work} does not hold together "
              f"({len(plan_problems)} problem(s) above); fix it with plan.py before "
              f"delivering against it", file=sys.stderr)
        return CANNOT_RUN
    receipts: list[str] = []
    nodes, problems = collect(root, validator, names, closed, receipts)
    problems += cross_problems(nodes, plan_nodes, work, names, root, target, standard, closed,
                               receipts)
    if problems:
        for problem in sorted(set(problems)):
            print(problem)
        refused = "the outstanding report" if report else DELIVERY_FILE
        print(f"\n{len(set(problems))} problem(s) over {len(nodes)} node(s). "
              f"{refused} is not derived over a delivery that does not hold together.")
        return 1

    if report:
        print(outstanding_report(nodes, plan_nodes, target))
        return 0

    delivery = derive(nodes, names)
    graph_contract = json.loads(DELIVERY_GRAPH_CONTRACT.read_text(encoding="utf-8"))
    broken = sorted(Draft202012Validator(graph_contract).iter_errors(delivery), key=str)
    if broken:  # a derivation this script produced and cannot ship is a defect in this script
        print(f"cannot run: the derived delivery does not satisfy "
              f"{DELIVERY_GRAPH_CONTRACT.name}: {broken[0].message}", file=sys.stderr)
        return CANNOT_RUN
    text = json.dumps(delivery, indent=2, ensure_ascii=False) + "\n"
    index_path = root / DELIVERY_FILE

    if verify:
        if not index_path.is_file():
            print(f"STALE: {index_path} does not exist; the delivery has never been derived")
            return 1
        if index_path.read_text(encoding="utf-8") != text:
            print(f"STALE: {index_path} is not what the nodes derive to. Run without --check to "
                  f"rewrite it; do not edit it, because every fact in it lives in a node file")
            return 1
        print(f"delivery checked: {index_path} matches {len(delivery['nodes'])} node(s)")
        for line in unread_unpaired(nodes):
            print(line)
        for line in unreconciled_reviews(nodes, target):
            print(f"  {line}")
        for line in receipts:
            print(f"  {line}")
        return 0

    index_path.write_text(text, encoding="utf-8")
    by_kind = [f"{count} {kind}" for kind in KINDS
               if (count := sum(1 for n in nodes.values() if n["kind"] == kind))]
    tasks = sum(1 for n in plan_nodes.values() if n["kind"] == "task")
    done = len({task_of(nid) for nid, node in nodes.items()
                if node["kind"] == "implementation"})
    unmet = sum(len(n.get("unmet", [])) for n in delivery["nodes"])
    unproven = sum(len(n.get("unproven", [])) for n in delivery["nodes"])
    findings = sum(n.get("findings", 0) for n in delivery["nodes"])
    print(f"derived {index_path}: {len(delivery['nodes'])} node(s), "
          f"{len(delivery['edges'])} edge(s), contract {delivery['contract_version']}")
    for line in unread_unpaired(nodes):
        print(line)
    for line in unreconciled_reviews(nodes, target):
        print(f"  {line}")
    for line in receipts:
        print(f"  {line}")
    print(f"  {', '.join(by_kind) or 'no nodes'}; {done} of {tasks} task(s) hold a record; "
          f"{unmet} criterion(s) recorded unmet; {unproven} recorded unproven; "
          f"{findings} finding(s)"
          + ("; the plan is closed" if closed else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
