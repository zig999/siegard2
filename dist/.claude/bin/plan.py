#!/usr/bin/env python3
"""Derive the plan graph from the markdown plan nodes, and refuse what breaks it.

The path is the identity. `inventory/<slug>.md` and `epic/<slug>.md` are two-part nodes;
`task/<epic>/<slug>.md` sits under the epic its path names. No node carries an id, a type or an
epic field, so none of the three can disagree with where the file sits — the kind this script
validates against is read from the path.

**The schema decides one file; this script decides what needs two — and what needs the
specification.** Per-node validation is `schemas/plan-node.json` applied as written. On top run
the checks no per-file schema can express: a task's epic exists, dependencies resolve and close
no cycle, every node a task implements or an epic covers exists in the specification, an epic's
covered nodes are each implemented by a task under it or declared uncovered (never neither, never
both), and a task's `## Notes` naming a specification node outside its epic's covers carries the
caller's decision line beside it (never silence). `intake/` under the work root holds the material
the planning read: kept for `sources` to point at, never validated.

**The specification is read through spec.py's own pipeline, and does not move underfoot.** A plan
carries no pin against it: the specification does not change during a plan's execution, by
convention — the discipline that replaced verifying it, once decide-and-disclose closed off the
one way a specification used to carry an open question a task could outlive. A specification that
does not hold together is a refusal to run: fix it with spec.py first.

**A `closure.md` at the work root marks the plan closed.** A closed plan is history: every
structural check still runs — corrupted history is refused — but the specification is never
touched, because history must stay checkable after it moves on, breaks, or disappears. Each
task's `implements` stands as the historical record of which nodes the work addressed. The marker
itself is prose for the reviewer, kept like `intake/` and never validated as a node; the
specification root becomes optional, and when given it is ignored.

**plan.json is derived, never edited.** It is refused entirely while the plan has problems: an
index over a broken plan reports a shape nobody decided. `--check` compares and never repairs.

Declared dependencies: PyYAML, jsonschema.

Usage:  plan.py <work-root> [<specification-root>]
                                                        validate everything, then write plan.json
        plan.py --check <work-root> [<specification-root>]
                                                        validate and compare; write nothing
        plan.py --node <file> <work-root> [<specification-root>]
                                                        validate one file (cross-node checks and
                                                        specification checks do not run)
        plan.py --standard <file> --against DIR <work-root> [<specification-root>]
                                                        also reconcile what the project's own
                                                        standard presupposes against DIR and the
                                                        tasks' `produces`; the two flags travel
                                                        together
        The specification root is required while the plan is live, and ignored once closure.md
        marks it closed.
Exit:   0 sound (and, with --check, current)
        1 problems, or --check and plan.json is stale
        2 cannot run (including a specification that does not hold together)
"""

from __future__ import annotations

import json
import re
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

import spec

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
PLAN_CONTRACT = PLUGIN_ROOT / "schemas" / "plan-node.json"
PLAN_GRAPH_CONTRACT = PLUGIN_ROOT / "schemas" / "plan.json"
PLAN_FILE = "plan.json"
CLOSURE_FILE = "closure.md"

KINDS = ("inventory", "epic", "task")
HEADINGS = ["## What it is", "## Notes"]
DECISION_OPENING = "Decision, beyond the covers — "

SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
FENCE = re.compile(r"^---\n(.*?)\n---\n?", re.S)


def id_of(relative: Path) -> str | None:
    """The identifier this path computes to, or None where it computes to nothing."""
    if relative.suffix != ".md":
        return None
    parts = relative.with_suffix("").parts
    if len(parts) == 2 and parts[0] in ("inventory", "epic"):
        pass
    elif len(parts) == 3 and parts[0] == "task":
        pass
    else:
        return None
    if not all(SLUG.match(p) for p in parts[1:]):
        return None
    return "/".join(parts)


def contract() -> tuple[Draft202012Validator, dict[str, set[str]]]:
    """The plan-node validator, and the per-kind field table read out of the contract rather
    than restated here."""
    if not PLAN_CONTRACT.is_file():
        raise FileNotFoundError(f"{PLAN_CONTRACT} is missing; nothing can be validated without it")
    schema = json.loads(PLAN_CONTRACT.read_text(encoding="utf-8"))
    allowed: dict[str, set[str]] = {}
    for branch in schema.get("allOf", []):
        kind = branch["if"]["properties"]["kind"]["const"]
        allowed[kind] = set(branch["then"]["propertyNames"]["enum"])
    return Draft202012Validator(schema), allowed


def listed(front: dict, field: str) -> list:
    """A list field read defensively: anything but a list reads as empty, because the schema
    already reported the shape and iterating a string would report its characters."""
    value = front.get(field)
    return value if isinstance(value, list) else []


def implements_of(front: dict) -> set[str]:
    """Just the specification node identities this task implements, read defensively."""
    return {ref for ref in listed(front, "implements") if isinstance(ref, str)}


def node_problems(front, kind: str, validator, allowed) -> list[str]:
    """Everything wrong with one plan node on its own: the schema, applied as written."""
    if not isinstance(front, dict):
        return [f"frontmatter is a {type(front).__name__}, not a mapping"]
    if any(not isinstance(key, str) for key in front):
        return ["frontmatter carries a non-string key"]

    problems: list[str] = []
    data = {**front, "kind": kind}
    for error in validator.iter_errors(data):
        where = ".".join(str(part) for part in error.absolute_path) or "frontmatter"
        problems.append(f"{where}: {error.message}")
    return problems


def body_problems(body: str) -> list[str]:
    headings = [line.rstrip() for line in body.splitlines() if line.startswith("## ")]
    if headings != HEADINGS:
        return [f"body headings are {headings if headings else 'absent'}; "
                f"every plan node carries exactly {HEADINGS}"]
    return []


def notes_of(body: str) -> str:
    """The text under `## Notes`, as composed. Absent — a shape body_problems already
    reported — it reads as empty."""
    lines = body.splitlines()
    for at, line in enumerate(lines):
        if line.rstrip() == "## Notes":
            return "\n".join(lines[at + 1:])
    return ""


def named_in(line: str, spec_ids: set[str]) -> set[str]:
    """Every specification node one line of prose names by identifier. A name matches whole: an
    identifier inside a longer path or slug is that construct's name, never this one's."""
    return {ref for ref in spec_ids
            if re.search(rf"(?<![a-z0-9/-]){re.escape(ref)}(?![a-z0-9/-])", line)}


def beyond_covers_problems(nid: str, notes: str, covers: set[str],
                           spec_ids: set[str]) -> list[str]:
    """A task's `## Notes` naming a specification node outside its epic's covers carries the
    caller's decision beside it — a `Decision, beyond the covers — ` line naming that node.
    Growing the claim or moving the task erases the condition through the re-implementation;
    standing is the decision that persists; silence is what this check refuses."""
    named: set[str] = set()
    decided: set[str] = set()
    for raw in notes.splitlines():
        line = raw.strip()
        if not line:
            continue
        beyond = {ref for ref in named_in(line, spec_ids) if ref not in covers}
        (decided if line.startswith(DECISION_OPENING) else named).update(beyond)
    return [f"{nid}: ## Notes names {ref}, which the epic's covers do not claim, and no "
            f"`{DECISION_OPENING.rstrip()}` line names it; a claim beyond the covers never "
            f"travels alone — grow the claim and re-implement, move the task and re-implement, "
            f"or stand and record the decision beside the note"
            for ref in sorted(named - decided)]


def references(front: dict, kind: str) -> list[tuple[str, str, str]]:
    """Every reference this node declares: (target, edge kind, locator). `depends_on` stays
    inside the plan; `implements` and `covers` point at the specification. Declared, never
    inferred — and read defensively, because this also runs over nodes the schema has already
    reported."""
    refs: list[tuple[str, str, str]] = []

    def add(target, edge_kind: str, at: str) -> None:
        if isinstance(target, str) and target:
            refs.append((target, edge_kind, at))

    if kind == "task":
        for index, target in enumerate(listed(front, "depends_on")):
            add(target, "depends_on", f"depends_on[{index}]")
        for index, target in enumerate(listed(front, "implements")):
            add(target, "implements", f"implements[{index}]")
    if kind == "epic":
        for index, target in enumerate(listed(front, "covers")):
            add(target, "covers", f"covers[{index}]")
    return refs


def dependency_problems(nodes: dict[str, dict]) -> list[str]:
    """Dependencies resolve inside the plan and close no cycle — a loop has no startable task."""
    problems: list[str] = []
    edges: dict[str, list[str]] = {}
    for nid in sorted(nodes):
        if nodes[nid]["kind"] != "task":
            continue
        edges[nid] = []
        for index, target in enumerate(listed(nodes[nid]["front"], "depends_on")):
            if not isinstance(target, str):
                continue  # the schema already reported the shape
            if target == nid:
                problems.append(f"{nid}: depends_on[{index}] names itself")
            elif target not in nodes:
                problems.append(f"{nid}: depends_on[{index}] names {target}, "
                                f"which the plan does not hold")
            else:
                edges[nid].append(target)

    state: dict[str, int] = {}  # 1 visiting, 2 done
    def walk(nid: str, trail: list[str]) -> None:
        state[nid] = 1
        for target in edges.get(nid, []):
            if state.get(target) == 1:
                cycle = trail[trail.index(target):] + [target]
                problems.append(f"{' -> '.join(cycle)}: depends_on closes a cycle; "
                                f"a dependency loop has no startable task")
            elif target not in state:
                walk(target, trail + [target])
        state[nid] = 2

    for nid in sorted(edges):
        if nid not in state:
            walk(nid, [nid])
    return problems


def epic_problems(nid: str, front: dict, nodes: dict[str, dict],
                  spec_ids: set[str] | None) -> list[str]:
    """One epic against its tasks, in both directions: every covered specification node is
    implemented by a task under the epic or declared uncovered — never neither, never both — and
    every node a task implements sits in the epic's covers, because a reference outside the
    claim is scope the plan does not declare."""
    problems: list[str] = []
    slug = nid.split("/")[1]
    covers = [t for t in listed(front, "covers") if isinstance(t, str)]

    implemented_below: set[str] = set()
    for tid in sorted(nodes):
        if nodes[tid]["kind"] != "task" or nodes[tid]["epic"] != slug:
            continue
        for index, target in enumerate(listed(nodes[tid]["front"], "implements")):
            if not isinstance(target, str):
                continue  # the schema already reported the shape
            implemented_below.add(target)
            if target not in covers:
                problems.append(f"{tid}: implements[{index}] names {target}, which {nid} does "
                                f"not cover; a reference outside the epic's claim is scope the "
                                f"plan does not declare — grow `covers`, or move the task")

    declared_uncovered: set[str] = set()
    for index, entry in enumerate(listed(front, "uncovered")):
        if not isinstance(entry, dict) or not isinstance(entry.get("node"), str):
            continue  # the schema already reported the shape
        node_ref = entry["node"]
        declared_uncovered.add(node_ref)
        if spec_ids is not None and node_ref not in spec_ids:
            problems.append(f"{nid}: uncovered[{index}].node names {node_ref}, "
                            f"which the specification does not hold")
        if node_ref not in covers:
            problems.append(f"{nid}: uncovered[{index}].node names {node_ref}, which `covers` "
                            f"does not claim; uncovered declares the deliberate remainder "
                            f"of covers")
        elif node_ref in implemented_below:
            problems.append(f"{nid}: uncovered[{index}].node names {node_ref}, which a task "
                            f"under this epic implements; the declaration contradicts the plan")

    for node_ref in covers:
        if node_ref not in implemented_below and node_ref not in declared_uncovered:
            problems.append(f"{nid}: covers names {node_ref}, which no task under it implements "
                            f"and uncovered does not declare; a covered node reaches a task or "
                            f"a stated why, never neither — implement it in a task under this "
                            f"epic, or declare it in `uncovered` with a why")
    return problems


def substrate_problems(nodes: dict[str, dict], named: str, tree: Path) -> list[str]:
    """Every artifact the project's own standard presupposes, held against this plan and the tree
    it plans over. A rule of a standard is a condition over a file that exists and can never ask
    for one, so an artifact a registry needs and a tree does not hold is work no rule can demand
    and no epic covers — the specification holds no node for a manifest, and it should not. What
    makes it the plan's business anyway is what happens downstream: a delivery refuses to write
    source over the absence, so a plan that leaves it unplanned is a plan whose every task stops
    on a condition only the plan can end.

    The reconciliation runs one way only, deliberately. A task may produce an artifact no standard
    presupposes — creating a file is ordinary work — and refusing that would make the plan
    relitigate what a registry never asked about. The other direction is the one that costs
    something, so it is the one that is checked.

    `deliver` is imported here rather than at the top because it imports this module. How a
    standard is read has one home, and reaching it from inside the function is what lets both
    scripts use that home without a cycle at import time.
    """
    import deliver
    data, found = deliver.load_standard(Path(named), deliver.standard_contract())
    if data is None:
        return [f"{named}: {problem}" for problem in found] + [
            f"the plan is not reconciled against {named}: a registry that does not hold together "
            f"presupposes nothing anybody can check"]

    produced = {path for node in nodes.values() if node["kind"] == "task"
                for path in listed(node["front"], "produces") if isinstance(path, str)}
    problems: list[str] = []
    for entry in listed(data, "presupposes"):
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            continue  # the registry's own contract already reported the shape
        where = entry["path"]
        if (tree / where).exists() or where in produced:
            continue
        rules = ", ".join(r for r in listed(entry, "rules") if isinstance(r, str))
        problems.append(
            f"{named} presupposes {where}, which {tree} does not hold and no task produces; "
            f"{rules} cannot be applied to anything this plan delivers, and /implement-task "
            f"refuses to write source while it is absent — so every task here stops until one of "
            f"them declares {where} in `produces`")
    return problems


def cross_problems(nodes: dict[str, dict], spec_nodes: dict[str, dict] | None) -> list[str]:
    """The rules that need to see more than one node at once — or the specification. With
    spec_nodes=None the plan is closed: every internal rule still runs, and every rule that would
    open today's specification is skipped, because a closed plan answers to the specification it
    read, not to today's."""
    problems: list[str] = []
    spec_ids = None if spec_nodes is None else set(spec_nodes)
    for nid in sorted(nodes):
        node, front = nodes[nid], nodes[nid]["front"]
        if node["kind"] == "task" and f"epic/{node['epic']}" not in nodes:
            problems.append(f"{nid}: sits under epic `{node['epic']}`, and "
                            f"epic/{node['epic']} does not exist; the path names an epic "
                            f"the plan does not hold")
        for target, edge_kind, at in references(front, node["kind"]):
            if (edge_kind in ("implements", "covers") and spec_ids is not None
                    and target not in spec_ids):
                problems.append(f"{nid}: {at} names {target}, "
                                f"which the specification does not hold")
        if node["kind"] == "task":
            epic_node = nodes.get(f"epic/{node['epic']}")
            if spec_ids is not None and epic_node is not None:
                covers = {t for t in listed(epic_node["front"], "covers")
                          if isinstance(t, str)}
                problems.extend(beyond_covers_problems(
                    nid, node.get("notes", ""), covers, spec_ids))
        if node["kind"] == "epic":
            problems.extend(epic_problems(nid, front, nodes, spec_ids))
    problems.extend(dependency_problems(nodes))
    return problems


def collect(root: Path, validator, allowed) -> tuple[dict[str, dict], list[str]]:
    """Every node in the plan, and everything wrong with the files as files."""
    nodes: dict[str, dict] = {}
    problems: list[str] = []
    for path in sorted(root.rglob("*.md")):
        relative = path.relative_to(root)
        if relative.parts[0] == "intake":
            continue  # the material the planning read: kept for sources, never validated
        if relative.parts == (CLOSURE_FILE,):
            continue  # the closure marker: it says the plan is closed, and is never a node
        nid = id_of(relative)
        if nid is None:
            problems.append(f"{relative.as_posix()}: not inventory/<slug>.md, epic/<slug>.md "
                            f"or task/<epic>/<slug>.md; the path is the identity and this one "
                            f"computes to none")
            continue
        text = path.read_text(encoding="utf-8")
        match = FENCE.match(text)
        if not match:
            problems.append(f"{nid}: carries no frontmatter fence")
            continue
        try:
            front = yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError as broken:
            problems.append(f"{nid}: frontmatter does not parse: {broken}")
            continue
        kind = relative.parts[0]
        epic = relative.with_suffix("").parts[1] if kind == "task" else None
        problems += [f"{nid}: {p}" for p in node_problems(front, kind, validator, allowed)]
        problems += [f"{nid}: {p}" for p in body_problems(text[match.end():])]
        if isinstance(front, dict):
            nodes[nid] = {"front": front, "kind": kind, "epic": epic}
            if kind == "task":
                nodes[nid]["notes"] = notes_of(text[match.end():])
    return nodes, problems


def load_base(root: Path) -> tuple[dict[str, dict], list[str]]:
    """The specification, read through spec.py's own pipeline — never through a derived index
    that could be stale."""
    validators = spec.contracts()
    nodes, problems = spec.collect(root, validators)
    return nodes, sorted(set(problems + spec.cross_problems(nodes, root)))


def derive(nodes: dict[str, dict]) -> dict:
    """The plan graph a sound plan derives to. Sorted throughout, so identical input is
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
        if node["kind"] == "task":
            entry["epic"] = node["epic"]
        out_nodes.append(entry)
        for target, edge_kind, at in references(front, node["kind"]):
            out_edges.append({"from": nid, "to": target, "kind": edge_kind, "at": at})
    out_edges.sort(key=lambda e: (e["from"], e["at"], e["to"]))
    return {"contract_version": "siegard-plan/3", "nodes": out_nodes, "edges": out_edges}


def check_single(root: Path, named: str, validator, allowed) -> int:
    path = Path(named)
    if not path.is_absolute():
        path = (root / named) if (root / named).is_file() else Path.cwd() / named
    try:
        relative = path.resolve().relative_to(root.resolve())
    except ValueError:
        print(f"cannot run: {named} is not under {root}", file=sys.stderr)
        return CANNOT_RUN
    if relative.parts[0] == "intake":
        print(f"{relative.as_posix()}: sits under intake/, which holds the material the "
              f"planning read and is never validated")
        return 0
    if relative.parts == (CLOSURE_FILE,):
        print(f"{relative.as_posix()}: marks the plan closed and is never validated as a node")
        return 0
    nid = id_of(relative)
    if nid is None:
        print(f"{relative.as_posix()}: the path computes to no identifier")
        return 1
    if not path.is_file():
        print(f"cannot run: {path} does not exist", file=sys.stderr)
        return CANNOT_RUN
    text = path.read_text(encoding="utf-8")
    match = FENCE.match(text)
    if not match:
        print(f"{nid}: carries no frontmatter fence")
        return 1
    try:
        front = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as broken:
        print(f"{nid}: frontmatter does not parse: {broken}")
        return 1
    problems = node_problems(front, relative.parts[0], validator, allowed)
    problems += body_problems(text[match.end():])
    for problem in problems:
        print(f"{nid}: {problem}")
    if problems:
        return 1
    print(f"{nid}: sound on its own. Cross-node checks and specification checks did not run; "
          f"they run on the whole plan.")
    return 0


def main() -> int:
    args = sys.argv[1:]
    verify = "--check" in args
    args = [a for a in args if a != "--check"]
    single = None
    if "--node" in args:
        at = args.index("--node")
        if at + 1 >= len(args):
            print("cannot run: --node takes a file", file=sys.stderr)
            return CANNOT_RUN
        single = args[at + 1]
        del args[at:at + 2]
    named = against = None
    for flag in ("--standard", "--against"):
        if flag in args:
            at = args.index(flag)
            if at + 1 >= len(args):
                print(f"cannot run: {flag} takes "
                      f"{'a file' if flag == '--standard' else 'a directory'}", file=sys.stderr)
                return CANNOT_RUN
            value = args[at + 1]
            del args[at:at + 2]
            if flag == "--standard":
                named = value
            else:
                against = value
    if (named is None) != (against is None):
        print("cannot run: --standard and --against travel together; a registry is reconciled "
              "against the tree this plan plans over, and neither half decides anything alone",
              file=sys.stderr)
        return CANNOT_RUN
    if named is not None and single is not None:
        print("cannot run: --node validates one file, and what a standard presupposes is a fact "
              "about the whole plan", file=sys.stderr)
        return CANNOT_RUN
    if len(args) not in (1, 2) or any(a.startswith("--") for a in args):
        print("cannot run: expected [--check | --node <file>] "
              "[--standard <file> --against <target-source-root>] "
              "<work-root> [<specification-root>]", file=sys.stderr)
        return CANNOT_RUN
    work = Path(args[0])
    if not work.is_dir():
        print(f"cannot run: work root {work} is not a directory", file=sys.stderr)
        return CANNOT_RUN
    closed = (work / CLOSURE_FILE).is_file()
    if closed and named is not None:
        print(f"cannot run: {work} is closed, and what a standard presupposes is a question about "
              f"work still to be cut. A closed plan answers to the tree it planned over, not to "
              f"today's; reopening it on an artifact nobody built then would make history refuse "
              f"to validate for a reason history cannot act on", file=sys.stderr)
        return CANNOT_RUN
    specification = Path(args[1]) if len(args) == 2 else None
    if not closed:
        if specification is None:
            print("cannot run: a live plan validates against its specification; name the "
                  "specification root", file=sys.stderr)
            return CANNOT_RUN
        if not specification.is_dir():
            print(f"cannot run: specification root {specification} is not a directory",
                  file=sys.stderr)
            return CANNOT_RUN

    try:
        validator, allowed = contract()
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as broken:
        print(f"cannot run: {broken}", file=sys.stderr)
        return CANNOT_RUN

    if single is not None:
        return check_single(work, single, validator, allowed)

    if closed:
        spec_nodes = None  # a closed plan never opens today's specification
    else:
        spec_nodes, spec_problems = load_base(specification)
        if spec_problems:
            for problem in spec_problems:
                print(problem, file=sys.stderr)
            print(f"cannot run: the specification at {specification} does not hold together "
                  f"({len(spec_problems)} problem(s) above); fix it with spec.py before "
                  f"planning over it", file=sys.stderr)
            return CANNOT_RUN

    nodes, problems = collect(work, validator, allowed)
    problems += cross_problems(nodes, spec_nodes)
    if named is not None:
        tree = Path(against)
        if not tree.is_dir():
            print(f"cannot run: target source root {tree} is not a directory", file=sys.stderr)
            return CANNOT_RUN
        problems += substrate_problems(nodes, named, tree)
    if problems:
        for problem in sorted(set(problems)):
            print(problem)
        print(f"\n{len(set(problems))} problem(s) over {len(nodes)} node(s). "
              f"plan.json is not derived over a plan that does not hold together.")
        return 1

    plan = derive(nodes)
    plan_contract = json.loads(PLAN_GRAPH_CONTRACT.read_text(encoding="utf-8"))
    broken = sorted(Draft202012Validator(plan_contract).iter_errors(plan), key=str)
    if broken:  # a derivation this script produced and cannot ship is a defect in this script
        print(f"cannot run: the derived plan does not satisfy {PLAN_GRAPH_CONTRACT.name}: "
              f"{broken[0].message}", file=sys.stderr)
        return CANNOT_RUN
    text = json.dumps(plan, indent=2, ensure_ascii=False) + "\n"
    target = work / PLAN_FILE

    if verify:
        if not target.is_file():
            print(f"STALE: {target} does not exist; the plan has never been derived")
            return 1
        if target.read_text(encoding="utf-8") != text:
            print(f"STALE: {target} is not what the nodes derive to. Run without --check to "
                  f"rewrite it; do not edit it, because every fact in it lives in a node file")
            return 1
        print(f"plan checked: {target} matches {len(plan['nodes'])} node(s)")
        return 0

    target.write_text(text, encoding="utf-8")
    by_kind = [f"{count} {kind}" for kind in KINDS
               if (count := sum(1 for n in nodes.values() if n["kind"] == kind))]
    tasks = [n for n in nodes.values() if n["kind"] == "task"]
    implemented = sum(len(implements_of(n["front"])) for n in tasks)
    unique = len({ref for n in tasks for ref in implements_of(n["front"])})
    print(f"derived {target}: {len(plan['nodes'])} node(s), {len(plan['edges'])} edge(s), "
          f"contract {plan['contract_version']}")
    print(f"  {', '.join(by_kind) or 'no nodes'}; {implemented} specification node reference(s) "
          f"implemented ({unique} unique)" + ("; closed" if closed else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
