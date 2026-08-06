#!/usr/bin/env python3
"""Derive the plan graph from the markdown plan nodes, and refuse what breaks it.

The path is the identity. `inventory/<slug>.md` and `epic/<slug>.md` are two-part nodes;
`task/<epic>/<slug>.md` sits under the epic its path names. No node carries an id, a type or an
epic field, so none of the three can disagree with where the file sits — the kind this script
validates against is read from the path.

**The schema decides one file; this script decides what needs two — and what needs the base.**
Per-node validation is `schemas/plan-node.json` applied as written: a plan node has no gap
mechanic of its own, because the epistemic record lives in `unresolved` and `waived`, which are
fields like any other. On top of that run the checks no per-file schema can express: a task's
epic exists, dependencies resolve and close no cycle, every bound or covered base node exists,
every open gap on every bound node is unresolved or waived (never silently ignored), a triage
entry answers a gap the base still holds on a node the task binds, an epic's covered nodes are
each bound by a task or declared uncovered (never neither, never both), a task's `## Notes`
naming a base node outside its epic's covers carries the caller's decision line beside it
(never silence), and each task's `base` pin matches the base as it stands. `intake/` under the work root holds the material the planning
read: kept for `sources` to point at, never validated.

**The base is read through graph.py's own pipeline, never through its graph.json** — an index
this script did not just derive could be stale, and a plan validated against a stale index
reports a soundness nobody has. A base that does not hold together is a refusal to run: fix it
with graph.py first. The pin each task carries is the SHA-256 of the graph.json text a sound
base derives to, so `sha256sum <knowledge-root>/graph.json` computes the same value by hand.

**A `closure.md` at the work root marks the plan closed.** A closed plan is history: every
structural check still runs — corrupted history is refused — but the base is never touched,
because history must stay checkable after the base moves on, breaks, or disappears. Each
task's pin stops being a currency constraint and stands as the historical anchor naming the
base the binding read. The marker itself is prose for the reviewer, kept like `intake/` and
never validated as a node; the knowledge root becomes optional, and when given it is ignored.

**plan.json is derived, never edited.** It is refused entirely while the plan has problems: an
index over a broken plan reports a shape nobody decided. `--check` compares and never repairs.
This script answers pointed questions itself (`--unresolved`) and never reads plan.json to do it:
both the index and the report derive from the nodes by the same pipeline, so neither can
disagree with the other, and neither can be stale.

Declared dependencies: PyYAML, jsonschema.

Usage:  plan.py <work-root> [<knowledge-root>]          validate everything, then write plan.json
        plan.py --check <work-root> [<knowledge-root>]  validate and compare; write nothing
        plan.py --unresolved <work-root> [<knowledge-root>]
                                                        validate, then print each task's open
                                                        gaps and questions; write nothing
        plan.py --node <file> <work-root> [<knowledge-root>]
                                                        validate one file (cross-node checks and
                                                        base checks do not run)
        The knowledge root is required while the plan is live, and ignored once closure.md
        marks it closed.
Exit:   0 sound (and, with --check, current)
        1 problems, or --check and plan.json is stale
        2 cannot run (including a knowledge base that does not hold together)
"""

from __future__ import annotations

import hashlib
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

import graph

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


def triage_of(front: dict, field: str) -> set[str]:
    """The gap references one triage field carries, read defensively."""
    return {entry["gap"] for entry in listed(front, field)
            if isinstance(entry, dict) and isinstance(entry.get("gap"), str)}


def node_problems(front, kind: str, validator, allowed) -> list[str]:
    """Everything wrong with one plan node on its own: the schema, applied as written, plus the
    one contradiction a single file can hold — a gap both unresolved and waived."""
    if not isinstance(front, dict):
        return [f"frontmatter is a {type(front).__name__}, not a mapping"]
    if any(not isinstance(key, str) for key in front):
        return ["frontmatter carries a non-string key"]

    problems: list[str] = []
    data = {**front, "kind": kind}
    for error in validator.iter_errors(data):
        where = ".".join(str(part) for part in error.absolute_path) or "frontmatter"
        problems.append(f"{where}: {error.message}")

    for ref in sorted(triage_of(front, "unresolved") & triage_of(front, "waived")):
        problems.append(f"`{ref}` is both unresolved and waived; the two answers "
                        f"contradict each other")
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


def named_in(line: str, base_ids: set[str]) -> set[str]:
    """Every base node one line of prose names by identifier. A name matches whole: an
    identifier inside a longer path or slug is that construct's name, never this one's."""
    return {ref for ref in base_ids
            if re.search(rf"(?<![a-z0-9/-]){re.escape(ref)}(?![a-z0-9/-])", line)}


def beyond_covers_problems(nid: str, notes: str, covers: set[str],
                           base_ids: set[str]) -> list[str]:
    """A task's `## Notes` naming a base node outside its epic's covers carries the caller's
    decision beside it — a `Decision, beyond the covers — ` line naming that node. Growing
    the claim or moving the task erases the condition through the re-bind; standing is the
    decision that persists; silence is what this check refuses."""
    named: set[str] = set()
    decided: set[str] = set()
    for raw in notes.splitlines():
        line = raw.strip()
        if not line:
            continue
        beyond = {ref for ref in named_in(line, base_ids) if ref not in covers}
        (decided if line.startswith(DECISION_OPENING) else named).update(beyond)
    return [f"{nid}: ## Notes names {ref}, which the epic's covers do not claim, and no "
            f"`{DECISION_OPENING.rstrip()}` line names it; a claim beyond the covers never "
            f"travels alone — grow the claim and re-bind, move the task and re-bind, or "
            f"stand and record the decision beside the note"
            for ref in sorted(named - decided)]


def references(front: dict, kind: str) -> list[tuple[str, str, str]]:
    """Every reference this node declares: (target, edge kind, locator). `depends_on` stays
    inside the plan; `binds` and `covers` point at the base. Declared, never inferred — and read
    defensively, because this also runs over nodes the schema has already reported."""
    refs: list[tuple[str, str, str]] = []

    def add(target, edge_kind: str, at: str) -> None:
        if isinstance(target, str) and target:
            refs.append((target, edge_kind, at))

    if kind == "task":
        for index, target in enumerate(listed(front, "depends_on")):
            add(target, "depends_on", f"depends_on[{index}]")
        for index, target in enumerate(listed(front, "nodes")):
            add(target, "binds", f"nodes[{index}]")
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


def gap_fields_of(base_node: dict) -> set[str]:
    return {g["field"] for g in (base_node["front"].get("gaps") or [])
            if isinstance(g, dict) and isinstance(g.get("field"), str)}


def task_problems(nid: str, front: dict, base_nodes: dict[str, dict] | None,
                  pin: str | None) -> list[str]:
    """One task against the base: the binding resolves, the triage is total and honest, and the
    pin matches the base as it stands. A closed plan passes base_nodes=None — its base is
    history's, not today's — so only the checks internal to the plan run."""
    problems: list[str] = []
    bound = {t for t in listed(front, "nodes") if isinstance(t, str)}

    for field in ("unresolved", "waived"):
        for index, entry in enumerate(listed(front, field)):
            if not isinstance(entry, dict) or not isinstance(entry.get("gap"), str):
                continue  # a question, or a shape the schema already reported
            node_ref, _, gap_field = entry["gap"].partition("#")
            if base_nodes is not None and node_ref not in base_nodes:
                problems.append(f"{nid}: {field}[{index}] names {node_ref}, "
                                f"which the base does not hold")
                continue
            if node_ref not in bound:
                problems.append(f"{nid}: {field}[{index}] triages a gap on {node_ref}, which "
                                f"`nodes` does not bind; triage covers the nodes the task cites "
                                f"— bind {node_ref} if it governs this task, or drop the entry")
            if base_nodes is not None and gap_field not in gap_fields_of(base_nodes[node_ref]):
                problems.append(f"{nid}: {field}[{index}] names `{entry['gap']}`, and "
                                f"{node_ref} declares no open gap on `{gap_field}`; a triage "
                                f"entry answers a gap the base still holds")

    if base_nodes is None:
        return problems

    triaged = triage_of(front, "unresolved") | triage_of(front, "waived")
    for node_ref in sorted(bound):
        if node_ref not in base_nodes:
            continue  # already reported as a broken binding
        for gap_field in sorted(gap_fields_of(base_nodes[node_ref])):
            ref = f"{node_ref}#{gap_field}"
            if ref not in triaged:
                problems.append(f"{nid}: {node_ref} declares an open gap on `{gap_field}`, and "
                                f"the task neither lists `{ref}` as unresolved nor waives it; "
                                f"a gap ignored in silence is the failure this check refuses")

    declared = front.get("base")
    if isinstance(declared, str) and declared != pin:
        problems.append(f"{nid}: base pin {declared} is not the base as it stands ({pin}); "
                        f"the binding read a base that has since moved — re-bind the task, "
                        f"or restate the pin deliberately")
    return problems


def epic_problems(nid: str, front: dict, nodes: dict[str, dict],
                  base_nodes: dict[str, dict] | None) -> list[str]:
    """One epic against its tasks, in both directions: every covered base node is bound by a
    task under the epic or declared uncovered — never neither, never both — and every node a
    task binds sits in the epic's covers, because a binding outside the claim is scope the
    plan does not declare."""
    problems: list[str] = []
    slug = nid.split("/")[1]
    covers = [t for t in listed(front, "covers") if isinstance(t, str)]

    bound_below: set[str] = set()
    for tid in sorted(nodes):
        if nodes[tid]["kind"] != "task" or nodes[tid]["epic"] != slug:
            continue
        for index, target in enumerate(listed(nodes[tid]["front"], "nodes")):
            if not isinstance(target, str):
                continue  # the schema already reported the shape
            bound_below.add(target)
            if target not in covers:
                problems.append(f"{tid}: nodes[{index}] binds {target}, which {nid} does not "
                                f"cover; a binding outside the epic's claim is scope the plan "
                                f"does not declare — grow `covers`, or move the task")

    declared_uncovered: set[str] = set()
    for index, entry in enumerate(listed(front, "uncovered")):
        if not isinstance(entry, dict) or not isinstance(entry.get("node"), str):
            continue  # the schema already reported the shape
        node_ref = entry["node"]
        declared_uncovered.add(node_ref)
        if base_nodes is not None and node_ref not in base_nodes:
            problems.append(f"{nid}: uncovered[{index}].node names {node_ref}, "
                            f"which the base does not hold")
        if node_ref not in covers:
            problems.append(f"{nid}: uncovered[{index}].node names {node_ref}, which `covers` "
                            f"does not claim; uncovered declares the deliberate remainder "
                            f"of covers")
        elif node_ref in bound_below:
            problems.append(f"{nid}: uncovered[{index}].node names {node_ref}, which a task "
                            f"under this epic binds; the declaration contradicts the plan")

    for node_ref in covers:
        if node_ref not in bound_below and node_ref not in declared_uncovered:
            problems.append(f"{nid}: covers names {node_ref}, which no task under it binds and "
                            f"uncovered does not declare; a covered node reaches a task or "
                            f"a stated why, never neither — bind it in a task under this epic, "
                            f"or declare it in `uncovered` with a why")
    return problems


def cross_problems(nodes: dict[str, dict], base_nodes: dict[str, dict] | None,
                   pin: str | None) -> list[str]:
    """The rules that need to see more than one node at once — or the base. With
    base_nodes=None the plan is closed: every internal rule still runs, and every rule that
    would open today's base is skipped, because a closed plan answers to the base it pinned."""
    problems: list[str] = []
    for nid in sorted(nodes):
        node, front = nodes[nid], nodes[nid]["front"]
        if node["kind"] == "task" and f"epic/{node['epic']}" not in nodes:
            problems.append(f"{nid}: sits under epic `{node['epic']}`, and "
                            f"epic/{node['epic']} does not exist; the path names an epic "
                            f"the plan does not hold")
        for target, edge_kind, at in references(front, node["kind"]):
            if (edge_kind in ("binds", "covers") and base_nodes is not None
                    and target not in base_nodes):
                problems.append(f"{nid}: {at} names {target}, which the base does not hold")
        if node["kind"] == "task":
            problems.extend(task_problems(nid, front, base_nodes, pin))
            epic_node = nodes.get(f"epic/{node['epic']}")
            if base_nodes is not None and epic_node is not None:
                covers = {t for t in listed(epic_node["front"], "covers")
                          if isinstance(t, str)}
                problems.extend(beyond_covers_problems(
                    nid, node.get("notes", ""), covers, set(base_nodes)))
        if node["kind"] == "epic":
            problems.extend(epic_problems(nid, front, nodes, base_nodes))
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
    """The base, read through graph.py's own pipeline — never through a graph.json that could
    be stale."""
    validator, allowed, obligations = graph.contract()
    nodes, problems = graph.collect(root, validator, allowed, obligations)
    return nodes, sorted(set(problems + graph.cross_problems(nodes)))


def base_pin(base_nodes: dict[str, dict]) -> str:
    """The pin of the base as it stands: the SHA-256 of the graph.json text the base derives
    to, so `sha256sum <knowledge-root>/graph.json` computes the same value by hand."""
    text = json.dumps(graph.derive(base_nodes), indent=2, ensure_ascii=False) + "\n"
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


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
            if isinstance(front.get("base"), str):
                entry["base"] = front["base"]
            unresolved = sorted(triage_of(front, "unresolved"))
            if unresolved:
                entry["unresolved"] = unresolved
            questions = sum(1 for e in listed(front, "unresolved")
                            if isinstance(e, dict) and isinstance(e.get("question"), str))
            if questions:
                entry["questions"] = questions
        out_nodes.append(entry)
        for target, edge_kind, at in references(front, node["kind"]):
            out_edges.append({"from": nid, "to": target, "kind": edge_kind, "at": at})
    out_edges.sort(key=lambda e: (e["from"], e["at"], e["to"]))
    return {"contract_version": "siegard-plan/1", "nodes": out_nodes, "edges": out_edges}


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
    print(f"{nid}: sound on its own. Cross-node checks and base checks did not run; "
          f"they run on the whole plan.")
    return 0


def unresolved_report(nodes: dict[str, dict]) -> str:
    """Each task's open gaps and questions — derived from the nodes the same way plan.json is,
    so the two can never disagree. The judgment behind each entry stays in the task file."""
    lines = []
    for nid in sorted(nodes):
        if nodes[nid]["kind"] != "task":
            continue
        front = nodes[nid]["front"]
        entries = listed(front, "unresolved")
        gaps = sorted(e["gap"] for e in entries
                      if isinstance(e, dict) and isinstance(e.get("gap"), str))
        questions = [e["question"] for e in entries
                     if isinstance(e, dict) and isinstance(e.get("question"), str)]
        if not gaps and not questions:
            continue
        lines.append(f"{nid}:")
        lines += [f"  gap {ref}" for ref in gaps]
        lines += [f"  question {q}" for q in questions]
    return "\n".join(lines) if lines else "no unresolved entries"


def main() -> int:
    args = sys.argv[1:]
    verify = "--check" in args
    args = [a for a in args if a != "--check"]
    report = "--unresolved" in args
    args = [a for a in args if a != "--unresolved"]
    single = None
    if "--node" in args:
        at = args.index("--node")
        if at + 1 >= len(args):
            print("cannot run: --node takes a file", file=sys.stderr)
            return CANNOT_RUN
        single = args[at + 1]
        del args[at:at + 2]
    if report and (verify or single is not None):
        print("cannot run: --unresolved stands alone", file=sys.stderr)
        return CANNOT_RUN
    if len(args) not in (1, 2) or any(a.startswith("--") for a in args):
        print("cannot run: expected [--check | --unresolved | --node <file>] "
              "<work-root> [<knowledge-root>]", file=sys.stderr)
        return CANNOT_RUN
    work = Path(args[0])
    if not work.is_dir():
        print(f"cannot run: work root {work} is not a directory", file=sys.stderr)
        return CANNOT_RUN
    closed = (work / CLOSURE_FILE).is_file()
    knowledge = Path(args[1]) if len(args) == 2 else None
    if not closed:
        if knowledge is None:
            print("cannot run: a live plan validates against its base; name the "
                  "knowledge root", file=sys.stderr)
            return CANNOT_RUN
        if not knowledge.is_dir():
            print(f"cannot run: knowledge root {knowledge} is not a directory",
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
        base_nodes, pin = None, None  # a closed plan never opens today's base
    else:
        base_nodes, base_problems = load_base(knowledge)
        if base_problems:
            for problem in base_problems:
                print(problem, file=sys.stderr)
            print(f"cannot run: the knowledge base at {knowledge} does not hold together "
                  f"({len(base_problems)} problem(s) above); fix it with graph.py before "
                  f"planning over it", file=sys.stderr)
            return CANNOT_RUN
        pin = base_pin(base_nodes)

    nodes, problems = collect(work, validator, allowed)
    problems += cross_problems(nodes, base_nodes, pin)
    if problems:
        for problem in sorted(set(problems)):
            print(problem)
        refused = "the unresolved report" if report else "plan.json"
        print(f"\n{len(set(problems))} problem(s) over {len(nodes)} node(s). "
              f"{refused} is not derived over a plan that does not hold together.")
        return 1

    if report:
        print(unresolved_report(nodes))
        return 0

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
    unresolved = sum(len(triage_of(n["front"], "unresolved")) for n in tasks)
    unique = len({ref for n in tasks for ref in triage_of(n["front"], "unresolved")})
    questions = sum(1 for n in tasks for e in listed(n["front"], "unresolved")
                    if isinstance(e, dict) and isinstance(e.get("question"), str))
    waived = sum(len(triage_of(n["front"], "waived")) for n in tasks)
    print(f"derived {target}: {len(plan['nodes'])} node(s), {len(plan['edges'])} edge(s), "
          f"contract siegard-plan/1")
    print(f"  {', '.join(by_kind) or 'no nodes'}; {unresolved} unresolved gap citation(s) "
          f"({unique} unique); {questions} open question(s); {waived} waived"
          + ("; closed" if closed else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
