#!/usr/bin/env python3
"""Derive the knowledge graph from the markdown nodes, and refuse what breaks it.

The path is the identity. `context/<slug>.md` is a context; `<kind>/<context>/<slug>.md` is
everything else. No node carries an id, a type or a boundary field, so none of the three can
disagree with where the file sits — the kind this script validates against is read from the path.

**The schema decides one file; this script decides what needs two.** Per-node validation is
`schemas/node.json` applied as written, with one behaviour the schema states and cannot enforce:
a required field may be absent when a `gaps` entry names it. A gap excuses knowledge, never form —
a malformed value is an error whatever the gaps say. On top of that run the checks no per-file
schema can express: references resolve, one lifecycle per subject, one root per aggregate, a
consumed interface's upstream is published, a transition emits an event, a rule reaching outside
its aggregate says how it holds, and a transition table is total over its non-terminal states —
where a gap names `transitions.<state>.<trigger>`, or a rejection's absent error as
`rejections.<from>.<trigger>.error`, the absence is declared and accepted. `intake/` under the
root holds the material the analysis read: kept for `sources` to point at, never validated.

**graph.json is derived, never edited.** It is refused entirely while the base has problems: an
index over a broken base reports a shape nobody decided. `--check` compares and never repairs,
because a check that fixes what it was meant to detect reports success on a defect.

**This script validates, derives and reports from the nodes; it never reads graph.json to
answer a question.** The index is something it writes and checks, never consults. Bulk context —
identifiers, titles, summaries, edges — is read from `graph.json` by whoever needs it; a pointed
report (`--gaps`) is asked of this script. Both derive from the nodes by the same pipeline, so
neither can disagree with the other, and neither can be stale.

Declared dependencies: PyYAML, jsonschema.

Usage:  graph.py <knowledge-root>              validate everything, then write graph.json
        graph.py --check <knowledge-root>      validate and compare; write nothing
        graph.py --gaps <knowledge-root>       validate, then print `<node>: <gap fields>`;
                                               write nothing
        graph.py --node <file> <knowledge-root>  validate one file (cross-node checks do not run)
Exit:   0 sound (and, with --check, current)
        1 problems, or --check and graph.json is stale
        2 cannot run
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

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
NODE_CONTRACT = PLUGIN_ROOT / "schemas" / "node.json"
GRAPH_CONTRACT = PLUGIN_ROOT / "schemas" / "graph.json"
GRAPH_FILE = "graph.json"

SCOPED = ("aggregate", "definition", "rule", "lifecycle", "interface", "process")
KINDS = ("context",) + SCOPED
HEADINGS = ["## What it is", "## Rules"]
EVENTS = ("domain-event", "integration-event")

SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
FENCE = re.compile(r"^---\n(.*?)\n---\n?", re.S)
REQUIRED_MSG = re.compile(r"'(.+?)' is a required property")


def id_of(relative: Path) -> str | None:
    """The identifier this path computes to, or None where it computes to nothing."""
    if relative.suffix != ".md":
        return None
    parts = relative.with_suffix("").parts
    if len(parts) == 2 and parts[0] == "context":
        pass
    elif len(parts) == 3 and parts[0] in SCOPED:
        pass
    else:
        return None
    if not all(SLUG.match(p) for p in parts[1:]):
        return None
    return "/".join(parts)


def contract() -> tuple[Draft202012Validator, dict[str, set[str]], dict[str, set[str]]]:
    """The node validator, and two tables read out of the contract rather than restated here:
    per kind, which fields it may declare, and which its obligations (plain and conditional) are.
    """
    if not NODE_CONTRACT.is_file():
        raise FileNotFoundError(f"{NODE_CONTRACT} is missing; nothing can be validated without it")
    schema = json.loads(NODE_CONTRACT.read_text(encoding="utf-8"))
    allowed: dict[str, set[str]] = {}
    obligations: dict[str, set[str]] = {}
    for branch in schema.get("allOf", []):
        kind = branch["if"]["properties"]["kind"]["const"]
        then = branch["then"]
        allowed[kind] = set(then["propertyNames"]["enum"])
        obligations[kind] = set(then.get("required", []))
        for nested in then.get("allOf", []):
            obligations[kind] |= set(nested.get("then", {}).get("required", []))
    return Draft202012Validator(schema), allowed, obligations


def node_problems(front, kind: str, validator, allowed, obligations) -> list[str]:
    """Everything wrong with one node on its own: the schema, minus gap-excused absences,
    plus the gap discipline the schema states and cannot check."""
    if not isinstance(front, dict):
        return [f"frontmatter is a {type(front).__name__}, not a mapping"]
    if any(not isinstance(key, str) for key in front):
        return ["frontmatter carries a non-string key"]

    problems: list[str] = []
    gaps = [g for g in (front.get("gaps") or []) if isinstance(g, dict)]
    bare = {g["field"] for g in gaps if isinstance(g.get("field"), str) and "." not in g["field"]}

    data = {**front, "kind": kind}
    for error in validator.iter_errors(data):
        if error.validator == "required" and not list(error.absolute_path):
            named = REQUIRED_MSG.match(error.message)
            if named and named.group(1) in bare and named.group(1) in obligations[kind]:
                continue  # absent and named by a gap: the one absence the contract accepts
        where = ".".join(str(part) for part in error.absolute_path) or "frontmatter"
        problems.append(f"{where}: {error.message}")

    for index, gap in enumerate(gaps):
        field = gap.get("field")
        if not isinstance(field, str):
            continue  # the schema already reported the shape
        head = field.split(".")[0].split("[")[0]
        if head not in allowed[kind] or head in ("kind", "title", "summary", "gaps"):
            problems.append(f"gaps[{index}]: `{field}` is not a field a {kind} declares")
        elif "." in field or "[" in field:
            if head not in front:
                problems.append(f"gaps[{index}]: `{field}` points inside `{head}`, "
                                f"which the node does not declare")
        elif head in front:
            problems.append(f"gaps[{index}]: `{field}` is declared by the node; "
                            f"a gap names an absent fact. An absence inside `{field}` "
                            f"takes a dotted path (`{field}.<what-is-missing>`)")
    return problems


def body_problems(body: str) -> list[str]:
    headings = [line.rstrip() for line in body.splitlines() if line.startswith("## ")]
    if headings != HEADINGS:
        return [f"body headings are {headings if headings else 'absent'}; "
                f"every node carries exactly {HEADINGS}"]
    return []


def references(front: dict, kind: str, context: str) -> list[tuple[str, str, str]]:
    """Every reference this node declares: (target, edge kind, locator).
    Declared, never inferred — and read defensively, because this also runs over nodes the
    schema has already reported."""
    refs: list[tuple[str, str, str]] = []

    def add(target, edge_kind: str, at: str) -> None:
        if isinstance(target, str) and target:
            refs.append((target, edge_kind, at))

    if kind == "context":
        for index, entry in enumerate(front.get("relationships") or []):
            if isinstance(entry, dict) and isinstance(entry.get("with"), str):
                add(f"context/{entry['with']}", "relationship", f"relationships[{index}].with")
    if kind in ("definition", "rule") and isinstance(front.get("aggregate"), str):
        add(f"aggregate/{context}/{front['aggregate']}", "aggregate", "aggregate")
    if kind == "definition":
        for attribute in front.get("attributes") or []:
            if not isinstance(attribute, dict):
                continue
            name = attribute.get("name", "?")
            add(attribute.get("target"), "attribute.ref", f"attributes[{name}].target")
            add(attribute.get("of"), "attribute.of", f"attributes[{name}].of")
            add(attribute.get("lifecycle"), "attribute.lifecycle", f"attributes[{name}].lifecycle")
    if kind == "rule":
        for index, target in enumerate(front.get("constrains") or []):
            add(target, "constrains", f"constrains[{index}]")
    if kind == "lifecycle":
        add(front.get("subject"), "subject", "subject")
        for index, transition in enumerate(front.get("transitions") or []):
            if isinstance(transition, dict):
                for position, emitted in enumerate(transition.get("emits") or []):
                    add(emitted, "emits", f"transitions[{index}].emits[{position}]")
        for index, rejection in enumerate(front.get("rejections") or []):
            if isinstance(rejection, dict):
                add(rejection.get("error"), "rejection.error", f"rejections[{index}].error")
    if kind == "interface":
        add(front.get("payload"), "payload", "payload")
        add(front.get("upstream"), "upstream", "upstream")
    if kind == "process":
        for index, step in enumerate(front.get("steps") or []):
            if isinstance(step, dict):
                add(step.get("node"), "step", f"steps[{index}].node")
                add(step.get("compensated_by"), "compensation", f"steps[{index}].compensated_by")
    return refs


def lifecycle_problems(nid: str, front: dict) -> list[str]:
    """State coherence and totality — the checks that read one lifecycle whole."""
    problems: list[str] = []
    states = [s for s in (front.get("states") or []) if isinstance(s, str)]
    declared = set(states)
    terminal = {s for s in (front.get("terminal") or []) if isinstance(s, str)}
    transitions = [t for t in (front.get("transitions") or []) if isinstance(t, dict)]
    rejections = [r for r in (front.get("rejections") or []) if isinstance(r, dict)]
    gap_fields = {g["field"] for g in (front.get("gaps") or [])
                  if isinstance(g, dict) and isinstance(g.get("field"), str)}

    def held(state, at: str) -> None:
        if isinstance(state, str) and state not in declared:
            problems.append(f"{nid}: {at} names `{state}`, which is not a declared state")

    held(front.get("initial"), "initial")
    for state in sorted(terminal):
        held(state, "terminal")
    for index, transition in enumerate(transitions):
        held(transition.get("from"), f"transitions[{index}].from")
        held(transition.get("to"), f"transitions[{index}].to")
    for index, rejection in enumerate(rejections):
        held(rejection.get("from"), f"rejections[{index}].from")
        if "error" in rejection or not (isinstance(rejection.get("from"), str)
                                        and isinstance(rejection.get("trigger"), str)):
            continue  # named, or a shape the schema already reported
        field = f"rejections.{rejection['from']}.{rejection['trigger']}.error"
        if field not in gap_fields:
            problems.append(
                f"{nid}: rejections[{index}] carries no error and no gap names `{field}`; "
                f"an unnamed refusal is a gap, never an invented domain error")

    covered = {(entry.get("from"), entry.get("trigger")) for entry in transitions + rejections}
    excused = set()
    for field in sorted(gap_fields):
        parts = field.split(".")
        if len(parts) != 3 or parts[0] != "transitions":
            continue
        state, trigger = parts[1], parts[2]
        held(state, f"the gap on `{field}`")
        if (state, trigger) in covered:
            problems.append(f"{nid}: the gap on `{field}` names a covered pairing; "
                            f"a gap names an absent fact")
        excused.add((state, trigger))

    triggers = sorted({entry.get("trigger") for entry in transitions + rejections
                       if isinstance(entry.get("trigger"), str)})
    for state in states:
        if state in terminal:
            continue  # terminal is declared, and declared is what exempts it
        for trigger in triggers:
            if (state, trigger) not in covered and (state, trigger) not in excused:
                problems.append(
                    f"{nid}: state `{state}` has no transition, no rejection and no gap for "
                    f"trigger `{trigger}`; an uncovered pairing is where behaviour gets "
                    f"invented later")
    return problems


def cross_problems(nodes: dict[str, dict]) -> list[str]:
    """The rules that need to see more than one node at once."""
    problems: list[str] = []

    for nid in sorted(nodes):
        node = nodes[nid]
        for target, _, at in references(node["front"], node["kind"], node["context"]):
            if target not in nodes:
                problems.append(f"{nid}: {at} names {target}, which the base does not hold")

    claims: dict[str, list[str]] = {}
    for nid in sorted(nodes):
        node = nodes[nid]
        if node["kind"] == "lifecycle" and isinstance(node["front"].get("subject"), str):
            claims.setdefault(node["front"]["subject"], []).append(nid)
    for subject, lifecycles in sorted(claims.items()):
        if len(lifecycles) > 1:
            problems.append(f"{' and '.join(lifecycles)} both claim {subject}; "
                            f"a definition has one lifecycle")

    roots: dict[str, list[str]] = {}
    for nid in sorted(nodes):
        node = nodes[nid]
        if (node["kind"] == "definition" and node["front"].get("ddd") == "aggregate-root"
                and isinstance(node["front"].get("aggregate"), str)):
            roots.setdefault(f"aggregate/{node['context']}/{node['front']['aggregate']}",
                             []).append(nid)
    for nid in sorted(nodes):
        if nodes[nid]["kind"] != "aggregate":
            continue
        found = roots.get(nid, [])
        if not found:
            problems.append(f"{nid}: no definition declares it with an aggregate-root ddd; "
                            f"the root is derived from its members and this one has none")
        elif len(found) > 1:
            problems.append(f"{nid}: {len(found)} definitions claim its root: {', '.join(found)}")

    for nid in sorted(nodes):
        node, front = nodes[nid], nodes[nid]["front"]
        if node["kind"] == "interface" and isinstance(front.get("upstream"), str):
            target = nodes.get(front["upstream"])
            if target and target["front"].get("ownership") != "published":
                problems.append(
                    f"{nid}: upstream names {front['upstream']}, whose ownership is not "
                    f"published; the chain ends at the context that owes compatibility")
        if node["kind"] == "lifecycle":
            problems.extend(lifecycle_problems(nid, front))
            for index, transition in enumerate(front.get("transitions") or []):
                if not isinstance(transition, dict):
                    continue
                for emitted in transition.get("emits") or []:
                    target = nodes.get(emitted)
                    if target and target["front"].get("ddd") not in EVENTS:
                        problems.append(
                            f"{nid}: transitions[{index}].emits names {emitted}, whose ddd is "
                            f"`{target['front'].get('ddd')}`; a state change raises an event")
        if node["kind"] == "rule":
            reached = set()
            for target_id in front.get("constrains") or []:
                target = nodes.get(target_id)
                if target and target["kind"] == "definition":
                    reached.add((target["context"], target["front"].get("aggregate")))
            own = (node["context"], front["aggregate"]) \
                if isinstance(front.get("aggregate"), str) else None
            outside = {r for r in reached if r != own} if own \
                else (reached if len(reached) > 1 else set())
            gapped = any(isinstance(g, dict) and g.get("field") == "consistency"
                         for g in front.get("gaps") or [])
            if outside and not front.get("consistency") and not gapped:
                problems.append(
                    f"{nid}: constrains reaches outside its own aggregate and declares no "
                    f"consistency; what spans two aggregates cannot hold in one transaction")
    return problems


def digest_of(path: Path) -> str:
    """The content identity of one node: the SHA-256 of its file's bytes, so
    `sha256sum <knowledge-root>/<id>.md` computes the same value by hand.

    The whole file, frontmatter and body together. A digest over the frontmatter alone would miss
    what `## Rules` points at and could not be recomputed with one command, and a pin nobody but
    this script can verify is a claim rather than a verification."""
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def collect(root: Path, validator, allowed, obligations) -> tuple[dict[str, dict], list[str]]:
    """Every node in the base, and everything wrong with the files as files."""
    nodes: dict[str, dict] = {}
    problems: list[str] = []
    for path in sorted(root.rglob("*.md")):
        relative = path.relative_to(root)
        if relative.parts[0] == "intake":
            continue  # the material the analysis read: kept for sources, never validated
        nid = id_of(relative)
        if nid is None:
            problems.append(f"{relative.as_posix()}: not context/<slug>.md or "
                            f"<kind>/<context>/<slug>.md; the path is the identity "
                            f"and this one computes to none")
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
        context = relative.with_suffix("").parts[1]
        problems += [f"{nid}: {p}" for p in node_problems(front, kind, validator,
                                                          allowed, obligations)]
        problems += [f"{nid}: {p}" for p in body_problems(text[match.end():])]
        if isinstance(front, dict):
            nodes[nid] = {"front": front, "kind": kind, "context": context,
                          "digest": digest_of(path)}
    return nodes, problems


def staleness(target: Path, graph: dict) -> list[str]:
    """What differs between the index on disk and the index the nodes derive to.

    `--check` compared whole texts and said STALE, which is true and leaves the reader to run a
    diff to learn which of two very different things happened. A node that changed is somebody's
    edit, and the index is behind their work. An index whose every entry differs only in a field
    this version derives and the stored one never carried is this framework having moved under a
    root nobody touched — the state a contract migration leaves in every consumer, discovered at
    whatever invocation runs next. Both are fixed by rederiving; only one of them means anything
    about the base, and telling them apart is the reader's first question."""
    try:
        stored = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ["it does not parse as JSON, so nothing in it can be compared entry by entry"]
    if not isinstance(stored, dict):
        return ["it is not a mapping, so nothing in it can be compared entry by entry"]

    entries = stored.get("nodes")
    was = {n["id"]: n for n in (entries if isinstance(entries, list) else [])
           if isinstance(n, dict) and isinstance(n.get("id"), str)}
    now = {n["id"]: n for n in graph["nodes"]}
    lines: list[str] = []
    if gone := sorted(set(was) - set(now)):
        lines.append(f"{len(gone)} node(s) the index holds and the root does not: "
                     f"{', '.join(gone)}")
    if new := sorted(set(now) - set(was)):
        lines.append(f"{len(new)} node(s) the root holds and the index does not: "
                     f"{', '.join(new)}")

    # An entry whose difference is confined to fields one side has no key for did not change: the
    # shape around it did. Comparing only the keys both carry is what separates the two, and it is
    # what keeps a stored index written before a field existed from reporting every node as moved.
    differing = [nid for nid in sorted(set(was) & set(now)) if was[nid] != now[nid]]
    shape = [nid for nid in differing
             if {k: v for k, v in was[nid].items() if k in now[nid]}
             == {k: v for k, v in now[nid].items() if k in was[nid]}]
    if changed := [nid for nid in differing if nid not in shape]:
        lines.append(f"{len(changed)} node(s) whose derived facts changed: {', '.join(changed)}")
    if shape:
        fields = sorted({k for nid in shape for k in set(now[nid]) ^ set(was[nid])})
        lines.append(f"{len(shape)} node(s) differing only in {', '.join(fields)}, which one side "
                     f"carries no key for; the index's own shape moved and those nodes did not")
    if stored.get("edges") != graph["edges"]:
        lines.append("the edge set differs, which follows the references the nodes declare")
    if not lines:
        lines.append("no node was added, removed or changed; the difference is outside the "
                     "entries, and rederiving rewrites the index alone")
    return lines


def derive(nodes: dict[str, dict]) -> dict:
    """The graph a sound base derives to. Sorted throughout, so identical input is
    byte-identical output."""
    out_nodes, out_edges = [], []
    for nid in sorted(nodes):
        node, front = nodes[nid], nodes[nid]["front"]
        entry = {
            "id": nid,
            "kind": node["kind"],
            "file": f"{nid}.md",
            "context": node["context"],
            "title": front.get("title", ""),
            "summary": front.get("summary", ""),
            "digest": node["digest"],
        }
        if isinstance(front.get("aggregate"), str):
            entry["aggregate"] = front["aggregate"]
        if isinstance(front.get("ddd"), str):
            entry["ddd"] = front["ddd"]
        gaps = front.get("gaps") or []
        if gaps:
            entry["gaps"] = sorted(g["field"] for g in gaps)
        out_nodes.append(entry)
        for target, edge_kind, at in references(front, node["kind"], node["context"]):
            out_edges.append({"from": nid, "to": target, "kind": edge_kind, "at": at})
    out_edges.sort(key=lambda e: (e["from"], e["at"], e["to"]))
    return {"contract_version": "siegard/1", "nodes": out_nodes, "edges": out_edges}


def check_single(root: Path, named: str, validator, allowed, obligations) -> int:
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
              f"analysis read and is never validated")
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
    problems = node_problems(front, relative.parts[0], validator, allowed, obligations)
    problems += body_problems(text[match.end():])
    for problem in problems:
        print(f"{nid}: {problem}")
    if problems:
        return 1
    print(f"{nid}: sound on its own. Cross-node checks did not run; they run on the whole base.")
    return 0


def gaps_report(nodes: dict[str, dict]) -> str:
    """One line per node with gaps — `<id>: <field>, <field>` — derived from the nodes the
    same way graph.json is, so the two can never disagree. The `why` behind each field stays
    in the node file the line names."""
    lines = []
    for nid in sorted(nodes):
        gaps = nodes[nid]["front"].get("gaps") or []
        if gaps:
            lines.append(f"{nid}: {', '.join(sorted(g['field'] for g in gaps))}")
    return "\n".join(lines) if lines else "no gaps declared"


def main() -> int:
    args = sys.argv[1:]
    verify = "--check" in args
    args = [a for a in args if a != "--check"]
    report = "--gaps" in args
    args = [a for a in args if a != "--gaps"]
    single = None
    if "--node" in args:
        at = args.index("--node")
        if at + 1 >= len(args):
            print("cannot run: --node takes a file", file=sys.stderr)
            return CANNOT_RUN
        single = args[at + 1]
        del args[at:at + 2]
    if report and (verify or single is not None):
        print("cannot run: --gaps stands alone", file=sys.stderr)
        return CANNOT_RUN
    if len(args) != 1 or args[0].startswith("--"):
        print("cannot run: expected [--check | --gaps | --node <file>] <knowledge-root>",
              file=sys.stderr)
        return CANNOT_RUN
    root = Path(args[0])
    if not root.is_dir():
        print(f"cannot run: {root} is not a directory", file=sys.stderr)
        return CANNOT_RUN

    try:
        validator, allowed, obligations = contract()
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as broken:
        print(f"cannot run: {broken}", file=sys.stderr)
        return CANNOT_RUN

    if single is not None:
        return check_single(root, single, validator, allowed, obligations)

    nodes, problems = collect(root, validator, allowed, obligations)
    problems += cross_problems(nodes)
    if problems:
        for problem in sorted(set(problems)):
            print(problem)
        refused = "the gap report" if report else "graph.json"
        print(f"\n{len(set(problems))} problem(s) over {len(nodes)} node(s). "
              f"{refused} is not derived over a base that does not hold together.")
        return 1

    if report:
        print(gaps_report(nodes))
        return 0

    graph = derive(nodes)
    graph_contract = json.loads(GRAPH_CONTRACT.read_text(encoding="utf-8"))
    broken = sorted(Draft202012Validator(graph_contract).iter_errors(graph), key=str)
    if broken:  # a derivation this script produced and cannot ship is a defect in this script
        print(f"cannot run: the derived graph does not satisfy {GRAPH_CONTRACT.name}: "
              f"{broken[0].message}", file=sys.stderr)
        return CANNOT_RUN
    text = json.dumps(graph, indent=2, ensure_ascii=False) + "\n"
    target = root / GRAPH_FILE

    if verify:
        if not target.is_file():
            print(f"STALE: {target} does not exist; the graph has never been derived")
            return 1
        if target.read_text(encoding="utf-8") != text:
            print(f"STALE: {target} is not what the nodes derive to. Run without --check to "
                  f"rewrite it; do not edit it, because every fact in it lives in a node file")
            for line in staleness(target, graph):
                print(f"  {line}")
            return 1
        print(f"graph checked: {target} matches {len(graph['nodes'])} node(s)")
        return 0

    target.write_text(text, encoding="utf-8")
    by_kind = [f"{count} {kind}" for kind in KINDS
               if (count := sum(1 for n in nodes.values() if n["kind"] == kind))]
    gaps = sum(len(n["front"].get("gaps") or []) for n in nodes.values())
    rationale = sum(1 for n in nodes.values() if n["front"].get("rationale"))
    print(f"derived {target}: {len(graph['nodes'])} node(s), {len(graph['edges'])} edge(s), "
          f"contract {graph['contract_version']}")
    print(f"  {', '.join(by_kind) or 'no nodes'}; {gaps} gap(s); "
          f"{rationale} node(s) with rationale")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
