#!/usr/bin/env python3
"""Validate a governed repository's knowledge base against .

This script is a boundary validator. Every frontmatter constraint lives in
schemas/knowledge-object.json, which R30 makes the single authority for the attribute
type system; materialization lives in bin/knowledge_graph_lib.py. What lives here is
the set of checks the specification defers to a script, each decided against the
materialized graph rather than against one file:

  R11 lifecycle totality, with both shorthands expanded before the product is checked,
       plus reachability from `initial` and an outgoing transition for every non-terminal
  R15 a reference crossing a bounded context targets an `interface`
  R18 edge cardinality, in both directions where the table declares an inverse
  R20 at most one lifecycle names one definition as `subject`
  R21 exactly one boundary per object, derived from the member's own field
  R22 an edge naming an id the graph does not hold, together with orphans and cycles
  R27 a lifecycle-bound enum resolves to a lifecycle
  R28 a `ref` crossing an aggregate declares `binding: by-identity`
  R29 a `ref` or `list` target the graph does not hold
  R38 id and path compute each other, with no lookup
  R39 no id segment is a sequential number
  R43 exactly the two body sections the type names, in order, none empty
  R44 one sentence per line
  R45 one RFC 2119 keyword and no pronoun in a normative statement
  R48 a body length ceiling, read from the knowledge base rather than invented here
  R35 a synonym is declared in `aliases` and appears in no body

Every problem is reported and none is repaired: R22 says so for the materializer, and
A check that repairs what it detects reports success on a defect. This
script writes nothing, so `make validate` stays non-mutating.

Two rules of R46 are NOT enforced mechanically, named here rather than left to be
discovered: that a body carries no rationale, history, alternatives, or motivating
narrative, and that a body is not the only place a fact a machine reads appears. Both are
judgments about meaning, and model judgment stays out of enforcement.

Declared dependencies: PyYAML, jsonschema. Both are required; the script exits with a
named error rather than degrading silently if either is missing.

Usage: bin/validate_knowledge.py [knowledge_root ...]
        with no argument, every the named root tree is validated
Exit: 0 every knowledge base valid, 1 validation failures, 2 cannot run
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

from frontmatter_lib import PLUGIN_ROOT, display

from cli import cannot_run

try:
    import yaml # noqa: F401 (imported for the named-error path below)
except ImportError:
    cannot_run("cannot run: PyYAML is not installed (pip install pyyaml)")

try:
    from jsonschema import Draft202012Validator # noqa: F401
except ImportError:
    cannot_run("cannot run: jsonschema is not installed (pip install jsonschema)")

from knowledge_graph_lib import ( # noqa: E402 (after the dependency guards)
    ACYCLIC_KINDS,
    EDGE_KINDS,
    KO_SCHEMA_PATH,
    PRONOUNS,
    RFC2119,
    SECTION_HEADING,
    SECTIONS,
    SENTENCE_RUN_ON,
    TERMINAL,
    WORD,
    Graph,
    context_of,
    load,
)


# What a scaffold leaves behind when a value is not substituted. The generator's expander refuses one;
# a consumer's agent has no expander, so the refusal has to happen here instead.
PLACEHOLDER = re.compile(r"\{\{([a-z0-9_]+)\}\}")


# --- resolution, cardinality, and shape of the graph itself -------------------------


def check_resolution(graph: Graph) -> None:
    """Every edge names a node the graph holds, of a type the edge table permits (R22, R29).

    `superseded_by` is checked here too and is not an edge: R22 requires the target to resolve
    and forbids expansion from following it, so it lives in `graph.supersessions` rather than
    in `graph.edges`. A superseded object must also name a replacement of its own type, since
    a rule is never replaced by a lifecycle.
    """
    for reference in graph.supersessions:
        source = graph.nodes[reference.source]
        target = graph.nodes.get(reference.target)
        if target is None:
            graph.report(
                source.path,
                f"superseded_by: names '{reference.target}', which the graph does not hold",
            )
        elif target.kind != source.kind:
            graph.report(
                source.path,
                f"superseded_by: names a '{target.kind}', and a '{source.kind}' is replaced by "
                f"a '{source.kind}'",
            )

    for edge in graph.edges:
        kind = EDGE_KINDS[edge.kind]
        source = graph.nodes[edge.source]
        if kind.origin_types and source.kind not in kind.origin_types:
            graph.report(
                source.path,
                f"{edge.locator}: a '{source.kind}' declares '{edge.kind}', which only "
                f"{' or '.join(kind.origin_types)} may declare",
            )
        target = graph.nodes.get(edge.target)
        if target is None:
            graph.report(
                source.path, f"{edge.locator}: names '{edge.target}', which the graph does not hold"
            )
            continue
        if kind.target_types and target.kind not in kind.target_types:
            graph.report(
                source.path,
                f"{edge.locator}: names a '{target.kind}', but '{edge.kind}' targets "
                f"{' or '.join(kind.target_types)}",
            )


def check_cardinality(graph: Graph) -> None:
    """Enforce the cardinality every edge declares, in both directions (R18, R20, R21)."""
    outgoing: dict[tuple[str, str], int] = defaultdict(int)
    incoming: dict[tuple[str, str], int] = defaultdict(int)
    for edge in graph.edges:
        outgoing[(edge.source, edge.kind)] += 1
        incoming[(edge.target, edge.kind)] += 1

    for name, kind in EDGE_KINDS.items():
        for node in graph.nodes.values():
            if not node.is_ko:
                continue
            if kind.origin_types and node.kind not in kind.origin_types:
                continue
            count = outgoing[(node.id, name)]
            minimum = _effective_minimum(name, kind.minimum, node)
            if count < minimum:
                graph.report(
                    node.path, f"declares {count} '{name}' edge(s), and cardinality requires {minimum}"
                )
            if kind.maximum is not None and count > kind.maximum:
                graph.report(
                    node.path,
                    f"declares {count} '{name}' edge(s), and cardinality permits at most "
                    f"{kind.maximum}",
                )
        if kind.inverse_maximum is None:
            continue
        for node in graph.nodes.values():
            count = incoming[(node.id, name)]
            if count > kind.inverse_maximum:
                sources = sorted(e.source for e in graph.edges if e.kind == name and e.target == node.id)
                graph.report(
                    node.path,
                    f"is named by {count} '{name}' edge(s) — {', '.join(sources)} — and the "
                    f"inverse cardinality permits at most {kind.inverse_maximum}",
                )


def _effective_minimum(name: str, declared: int, node) -> int:
    """A bounded-context boundary declares no boundary edge: its absence marks a partition root."""
    if name == "boundary" and node.kind == "boundary" and node.data.get("ddd") == "bounded-context":
        return 0
    return declared


def check_boundary_partition(graph: Graph) -> None:
    """The id's context segment must agree with the boundary the object declares (R21, R38).

    Without this agreement the layout's own selection glob, `knowledge/*/<context>/*.md`
    for everything in one context, silently misses an object that declares a boundary in
    a different context from the directory it sits in.
    """
    for node in graph.nodes.values():
        if not node.is_ko or node.kind == "boundary":
            continue
        context = context_of(graph, node.id)
        if context is None:
            graph.report(
                node.path,
                f"boundary '{node.data.get('boundary')}' does not resolve to a bounded context",
            )
            continue
        expected = context.split(".")[2]
        actual = node.id.split(".")[2]
        if expected != actual:
            graph.report(
                node.path,
                f"id names context '{actual}' but the boundary chain resolves to '{expected}'",
            )


def check_cycles(graph: Graph) -> None:
    """Report a cycle in each edge kind whose acyclicity is a defect (R22)."""
    for name in ACYCLIC_KINDS:
        adjacency: dict[str, list[str]] = defaultdict(list)
        for edge in graph.edges:
            if edge.kind == name:
                adjacency[edge.source].append(edge.target)
        colour: dict[str, int] = {}

        def walk(node_id: str, trail: list[str]) -> None:
            colour[node_id] = 1
            for nxt in adjacency.get(node_id, []):
                if colour.get(nxt) == 1:
                    cycle = trail[trail.index(nxt) :] if nxt in trail else [nxt]
                    graph.report(
                        graph.nodes[node_id].path if node_id in graph.nodes else None,
                        f"'{name}' forms a cycle: {' -> '.join(cycle + [nxt])}",
                    )
                elif colour.get(nxt) is None:
                    walk(nxt, trail + [nxt])
            colour[node_id] = 2

        for node_id in sorted(adjacency):
            if colour.get(node_id) is None:
                walk(node_id, [node_id])


def check_orphans(graph: Graph) -> None:
    """A node no knowledge references and which references no knowledge is an orphan (R22).

    Two exclusions keep the degree meaningful. An object's own `boundary` edge does not
    count for the object, because every object declares one and counting it would make the
    check vacuous — but it does count for the boundary, because members are exactly what a
    boundary is for, and a boundary with none is an empty partition. `governed_by` counts
    for neither: citing an ADR records why an object was decided, not that knowledge uses it.
    """
    degree: dict[str, int] = defaultdict(int)
    for edge in graph.edges:
        if edge.kind == "governed_by":
            continue
        if edge.kind != "boundary":
            degree[edge.source] += 1
        degree[edge.target] += 1
    for node in graph.nodes.values():
        if node.is_ko and degree[node.id] == 0:
            graph.report(node.path, "is an orphan: no knowledge references it and it references none")


# --- the checks the specification names one by one ----------------------------------


def check_lifecycles(graph: Graph) -> None:
    """Totality, reachability, and outgoing transitions, with both shorthands expanded (R11)."""
    for node in graph.nodes.values():
        if node.kind != "lifecycle":
            continue
        data = node.data
        states = list(data["states"])
        state_set = set(states)
        if len(state_set) != len(states):
            graph.report(node.path, "`states` repeats a state name")
        if TERMINAL in state_set:
            graph.report(node.path, f"'{TERMINAL}' is reserved as a rejection shorthand and MUST NOT be a state")
        if data["initial"] not in state_set:
            graph.report(node.path, f"`initial` names '{data['initial']}', which is not a declared state")
        terminal = list(data.get("terminal") or [])
        for state in terminal:
            if state not in state_set:
                graph.report(node.path, f"`terminal` names '{state}', which is not a declared state")
        terminal_set = {s for s in terminal if s in state_set}

        transitions: dict[tuple[str, str], int] = {}
        triggers: set[str] = set()
        for i, transition in enumerate(data["transitions"]):
            for key in ("from", "to"):
                if transition[key] not in state_set:
                    graph.report(
                        node.path,
                        f"transitions[{i}].{key} names '{transition[key]}', which is not a declared state",
                    )
            triggers.add(transition["trigger"])
            pair = (transition["from"], transition["trigger"])
            if pair in transitions:
                graph.report(
                    node.path,
                    f"transitions[{i}] repeats the pair ({pair[0]}, {pair[1]}), so the move is ambiguous",
                )
            transitions[pair] = i

        rejections: dict[tuple[str, str], int] = {}
        for i, rejection in enumerate(data["rejections"]):
            origin = rejection["from"]
            if origin == TERMINAL:
                if not terminal_set:
                    graph.report(
                        node.path,
                        f"rejections[{i}] uses the `{TERMINAL}` shorthand, but no `terminal` state is declared",
                    )
                origins = sorted(terminal_set)
            elif origin not in state_set:
                graph.report(
                    node.path,
                    f"rejections[{i}].from names '{origin}', which is neither a declared state nor "
                    f"the reserved '{TERMINAL}'",
                )
                origins = []
            else:
                origins = [origin]
            declared = rejection["trigger"]
            expanded = declared if isinstance(declared, list) else [declared]
            triggers.update(expanded)
            for state in origins:
                for trigger in expanded:
                    pair = (state, trigger)
                    if pair in transitions:
                        graph.report(
                            node.path,
                            f"({state}, {trigger}) is both a transition and rejections[{i}]: the pair "
                            f"is decided twice",
                        )
                    if pair in rejections:
                        graph.report(
                            node.path,
                            f"({state}, {trigger}) is rejected twice, by rejections["
                            f"{rejections[pair]}] and rejections[{i}]",
                        )
                    rejections[pair] = i

        decided = set(transitions) | set(rejections)
        for state in states:
            for trigger in sorted(triggers):
                if (state, trigger) not in decided:
                    graph.report(
                        node.path,
                        f"({state}, {trigger}) is neither a transition nor a rejection, so the "
                        f"transition table is not total",
                    )

        reached = {data["initial"]} if data["initial"] in state_set else set()
        frontier = list(reached)
        while frontier:
            current = frontier.pop()
            for (origin, _trigger), _i in transitions.items():
                if origin != current:
                    continue
                for transition in data["transitions"]:
                    if transition["from"] == origin and transition["to"] not in reached:
                        reached.add(transition["to"])
                        frontier.append(transition["to"])
        for state in states:
            if state not in reached:
                graph.report(node.path, f"state '{state}' is not reachable from '{data['initial']}'")
            if state not in terminal_set and not any(t["from"] == state for t in data["transitions"]):
                graph.report(node.path, f"non-terminal state '{state}' has no outgoing transition")


def check_rejection_errors(graph: Graph) -> None:
    """A rejection raises a domain error, which is a definition recording that construct."""
    for edge in graph.edges:
        if edge.kind != "rejections[].error":
            continue
        target = graph.nodes.get(edge.target)
        if target is not None and target.data.get("ddd") != "domain-error":
            graph.report(
                graph.nodes[edge.source].path,
                f"{edge.locator}: '{edge.target}' carries ddd '{target.data.get('ddd')}', and a "
                f"rejection raises a definition with ddd domain-error",
            )


def check_cross_context(graph: Graph) -> None:
    """A reference leaving a bounded context targets an `interface` (R15).

    The edge table restricts an attribute's `target` and `of` to a definition, so a `ref`
    or `list` crossing a context can never satisfy R15 and is reported as a defect rather
    than repaired. Cross-context linkage therefore runs through `depends_on` to a
    published or consumed interface, which is the only shape both rules admit.
    """
    exempt = {name for name, kind in EDGE_KINDS.items() if kind.crosses_context}
    for edge in graph.edges:
        if edge.kind in exempt:
            continue
        source = graph.nodes[edge.source]
        target = graph.nodes.get(edge.target)
        if target is None or not target.is_ko:
            continue
        source_context = context_of(graph, edge.source)
        target_context = context_of(graph, edge.target)
        if source_context is None or target_context is None or source_context == target_context:
            continue
        if target.kind != "interface":
            graph.report(
                source.path,
                f"{edge.locator}: crosses from '{source_context}' to '{target_context}' and names a "
                f"'{target.kind}'. A reference leaving a bounded context targets an interface",
            )


#: The two primitives that reference another definition, and the parameter naming the target.
#: R28 binds both identically. Reading one table rather than branching on `ref` alone is what
#: keeps the check from being enforced on one field and silent on an equivalent one.
REFERENCING_PRIMITIVES = {"ref": "target", "list": "of"}


def check_aggregate_binding(graph: Graph) -> None:
    """A `ref` or `list` whose target lies in another aggregate declares by-identity (R28)."""
    for node in graph.nodes.values():
        if node.kind != "definition":
            continue
        for attribute in node.data.get("attributes") or []:
            parameter = REFERENCING_PRIMITIVES.get(attribute.get("type"))
            if parameter is None:
                continue
            target = graph.nodes.get(attribute[parameter])
            if target is None:
                continue
            same = node.data.get("boundary") == target.data.get("boundary")
            if not same and attribute.get("binding") != "by-identity":
                graph.report(
                    node.path,
                    f"attributes.{attribute['name']}: {parameter}s '{attribute[parameter]}' in "
                    f"'{target.data.get('boundary')}' rather than '{node.data.get('boundary')}', so "
                    f"`binding` MUST be by-identity, not '{attribute.get('binding')}'",
                )


def check_identity(graph: Graph) -> None:
    """A definition's identity names attributes the definition holds.

    Whether a definition declares `identity` at all is decided by the frontmatter contract
    from its `ddd` value, per R9: required of an entity, aggregate root, or read model, and
    forbidden of a value object or a domain error. This check only reads the identity that is
    present, so it stays silent on the two constructs that correctly have none.
    """
    for node in graph.nodes.values():
        if node.kind != "definition":
            continue
        held = {a["name"] for a in node.data.get("attributes") or []}
        for name in node.data.get("identity", {}).get("attributes", []):
            if name not in held:
                graph.report(node.path, f"identity names attribute '{name}', which this definition does not hold")


# --- body form ---------------------------------------------------------------------


def check_bodies(graph: Graph) -> None:
    """The two-section arity, one sentence per line, and normative-statement form."""
    ceiling = graph.limits.get("body_lines")
    if not isinstance(ceiling, int) or ceiling < 1:
        graph.report(
            graph.root / "system.md",
            "declares no positive `limits.body_lines`, so R48's body length ceiling cannot be "
            "enforced. The ceiling is a fact of the knowledge base, and "
            "a validator that supplied it would be a hidden default",
        )
        ceiling = None

    aliases: list[tuple[str, str]] = []
    for node in graph.nodes.values():
        if node.kind == "definition":
            aliases.extend((alias, node.id) for alias in node.data.get("aliases") or [])

    for node in graph.nodes.values():
        if not node.is_ko:
            continue
        body = node.body
        lines = body.splitlines()
        if ceiling is not None and len(lines) > ceiling:
            graph.report(
                node.path,
                f"body is {len(lines)} lines against a ceiling of {ceiling}. R48 reports an excess "
                f"as a single-responsibility violation under R8, not as a formatting warning",
            )

        headings = [
            (len(match.group(0).strip()), body[match.start() : body.find("\n", match.start())].strip())
            for match in SECTION_HEADING.finditer(body)
        ]
        titles = [text for level, text in headings if level == 1]
        sections = [text for level, text in headings if level == 2]
        deeper = [text for level, text in headings if level >= 3]
        expected = list(SECTIONS[node.kind])
        if len(titles) != 1 or (headings and headings[0][0] != 1):
            graph.report(node.path, "body must open with exactly one '# ' title heading")
        if sections != expected:
            graph.report(
                node.path,
                f"body carries sections {sections or '[]'}, and a '{node.kind}' carries exactly "
                f"{expected}, in that order",
            )
        for text in deeper:
            graph.report(node.path, f"body carries the extra heading '{text}', which R43 forbids")

        for heading in expected:
            content = _section_body(body, heading)
            if heading in body and not content.strip():
                graph.report(
                    node.path,
                    f"section '{heading}' is empty. An empty section is not decidable; a section "
                    f"with no content carries the literal line 'None.'",
                )

        for number, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if SENTENCE_RUN_ON.search(stripped):
                graph.report(node.path, f"line {number} holds more than one sentence, and R44 allows one")
            keywords = _rfc2119_count(stripped)
            if keywords >= 2:
                graph.report(
                    node.path,
                    f"line {number} uses {keywords} RFC 2119 keywords, and a normative statement uses one",
                )
            if keywords >= 1:
                found = sorted({w.lower() for w in WORD.findall(stripped)} & PRONOUNS)
                if found:
                    graph.report(
                        node.path,
                        f"line {number} is normative and uses the pronoun(s) {', '.join(found)}: "
                        f"there is no antecedent to resolve, so nothing may be guessed",
                    )
        for alias, owner in aliases:
            if _holds_word(body, alias):
                graph.report(
                    node.path,
                    f"body uses '{alias}', a synonym declared in {owner}.aliases. A synonym is "
                    f"declared and never written, so one surface form per concept survives",
                )


def _section_body(body: str, heading: str) -> str:
    start = body.find(heading)
    if start == -1:
        return ""
    after = start + len(heading)
    match = SECTION_HEADING.search(body, after)
    return body[after : match.start()] if match else body[after:]


def _rfc2119_count(line: str) -> int:
    """Count RFC 2119 keywords, longest first so MUST inside MUST NOT is counted once."""
    remaining = line
    total = 0
    for keyword in RFC2119:
        total += remaining.count(keyword)
        remaining = remaining.replace(keyword, " ")
    return total


def _holds_word(body: str, word: str) -> bool:
    return word.lower() in {w.lower() for w in WORD.findall(body)}


def check_unexpanded_scaffold(graph: Graph) -> None:
    """No authored object carries a placeholder a scaffold left behind.

    The distribution ships thirteen scaffolds and no expander, and the check does not rest on that. It
    rests on the fact that no expander could carry this guarantee anywhere. Four paths go around one and
    none needs bad faith: not running it, running it and editing the output, writing the object by hand,
    and passing a placeholder as a value — the generator's own expander accepts `title: "{{title}}"`,
    because it checks that every placeholder received a value and not that the value is one.

    So the guarantee belongs where a producer's work is checked rather than where it is intended: at the
    boundary, after the agent returns, on the artifact. That is the same reason the boundary validator
    runs after an authoring agent rather than inside it — a guarantee a producer self-reports is not a
    guarantee, whatever tools the producer was granted.

    A bare `{{name}}` in frontmatter already fails, but by accident and unhelpfully — YAML reads it as a
    flow mapping and reports an unhashable key. Quoted, or in the body, it passes everything: `"{{title}}"`
    is a non-empty string, and no schema can tell it from a title. It then reaches the graph, the
    projections, and generation, because every one of those reads the same objects.
    """
    for node in graph.nodes.values():
        seen: list[str] = []
        for number, line in enumerate(node.path.read_text().splitlines(), 1):
            for name in PLACEHOLDER.findall(line):
                if name not in seen:
                    seen.append(name)
                    graph.report(
                        node.path,
                        f"line {number} still holds the scaffold placeholder `{{{{{name}}}}}`. A "
                        f"scaffold is a skeleton and every value in it is the author's to supply; one "
                        f"left behind is a decision nobody made, and it is a valid string that no "
                        f"schema can refuse",
                    )


CHECKS = (
    check_unexpanded_scaffold,
    check_resolution,
    check_cardinality,
    check_boundary_partition,
    check_cycles,
    check_orphans,
    check_lifecycles,
    check_rejection_errors,
    check_cross_context,
    check_aggregate_binding,
    check_identity,
    check_bodies,
)


def validate(root: Path) -> list[str]:
    """Materialize and check one knowledge base, returning every problem found."""
    graph = load(root)
    # A node that failed its frontmatter contract is absent from the graph, so a check
    # over the graph would report its dangling edges as separate defects. Rejecting at the
    # boundary and stopping there is R6 of spec 0001: reject, never repair.
    if not graph.problems:
        for check in CHECKS:
            check(graph)
    return graph.problems


def main() -> int:
    """Validate every knowledge root named on the command line.

    A root is named, never defaulted. This script shipped with the generator's own
    layout as its fallback, which resolved to a path that exists only in that
    repository — in an installation the default found nothing and the run reported
    success over an empty set.
    A validator that passes over nothing reports a guarantee it never checked.
    """
    if not KO_SCHEMA_PATH.is_file():
        cannot_run(f"cannot run: schema {KO_SCHEMA_PATH} does not exist")

    roots = [Path(a) for a in sys.argv[1:]]
    if not roots:
        cannot_run("cannot run: name at least one knowledge root; there is no default")
    for root in roots:
        if not root.is_dir():
            cannot_run(f"cannot run: knowledge root {root} does not exist")

    total = 0
    failures: list[str] = []
    for root in roots:
        problems = validate(root)
        objects = len(list(root.rglob("*.md")))
        total += objects
        print(f"knowledge base {display(root)}: {objects} file(s), {len(problems)} problem(s)")
        failures.extend(problems)

    print(f"knowledge files checked: {total} schema: {display(KO_SCHEMA_PATH)}")
    if failures:
        print(f"FAILED: {len(failures)} problem(s)\n")
        for problem in failures:
            print(f" {problem}")
        return 1
    print("all knowledge bases valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
