#!/usr/bin/env python3
"""Hold an object's gaps and its absences to each other: every gap names a real requirement, and
every requirement it does not meet is named by a gap.

An object may declare a gap in place of a field it lacks, and the contract then accepts it. That
alternation is what lets a base hold an object which says "this entity exists and its identity
strategy is unstated" instead of holding nothing about the entity — and it is only as strong as the
field names in the gaps.

**Both directions, and the schema enforces neither.** The per-type alternation reads "everything
this type requires, **or** `gaps`", and `gaps` there is any gap over any field. So an object short
of `attributes` while declaring a gap about its identity strategy validates. The forward check
below catches a gap that names nothing real; the converse catches a requirement nothing names.
While the expansion derived every gap from these same requirements the two could not disagree, so
the converse cost nothing to omit. A producer that writes its objects by judgment can leave a hole
nobody named — and an object incomplete in a way nobody stated is indistinguishable from one whose
incompleteness is justified.

The schema cannot check them. `gaps[].field` is a dotted path and the requirement it excuses is a
conditional elsewhere in the same document, so nothing inside JSON Schema relates the two. Without
this, `gaps: [{kind: domain, field: colour}]` excuses an object from declaring `attributes`, and an
object incomplete in a way nobody named passes as one whose incompleteness is justified.

**The requirements are read from the contract, not restated here.** Which fields a node type demands
is already stated once, in the per-type conditionals of the schema this validates against, and a
second copy in this file would be a second thing to keep in step. So the vocabulary is derived: the
first branch of each type's alternation is exactly the list of fields a gap may name, plus whatever a
nested conditional on `ddd` adds for the object at hand.

Two dotted forms are admitted beyond a bare field name, because the ontology's own shapes need them:
`identity.attributes`, which names the part of a required object that is missing, and
`attributes[<name>].<parameter>`, which names a parameter the primitive requires of an attribute the
object carries. An attribute name the object does not carry is refused like any other invention.

Declared dependencies: PyYAML.

**The identifier is held to its arithmetic.** `dm.<kind>.<scope>.<slug>` computes to a path, and a
path computes back to an identifier, with no lookup. While a script wrote both they could not disagree;
written by judgment they can, and every reference in the base rests on them agreeing.

**The checks a per-file schema cannot express** run here too. Each compares two objects, and a boundary
validator is handed one:

- a lifecycle's transition table is **total** — every pairing of a declared state with a trigger the
  table mentions is either a transition or a rejection. An incomplete table is where whatever produces
  software later invents behaviour, and it invents it silently;
- **no two lifecycles claim one subject** — a definition with two state machines has no single state
  set to generate from, and which one binds is a question neither file answers;
- a reference **crossing a bounded context targets an interface** — a context that reaches into
  another's internals has no boundary, and the published contract is what the other side owes
  compatibility on;
- **containment is acyclic** — `boundary` admits an aggregate inside an aggregate, so a loop is
  expressible, and a loop leaves every node on it with no partition root;
- a node's **`boundary` agrees with its identifier** — the parent is written twice, once fixing the
  path and once fixing membership, and a node whose two parents disagree sits in two trees;
- an aggregate's **`root` agrees that it is one** — its `ddd` says `aggregate-root` and its own
  `boundary` is that aggregate;
- a consumed interface's **`upstream` is published** — a chain of consumed interfaces records copies
  of a contract and no owner;
- a transition **emits an event** — an `api` is called and a `command` is sent, and a state change
  raises neither;
- a rule reaching **outside its own aggregate declares `consistency`** — what spans two aggregates
  cannot hold inside one transaction, and a boundary wide enough to hide that is drawn wrong.

Usage:  check_knowledge.py <knowledge-root>
Exit:   0 gaps, absences and cross-object rules all hold, 1 one fails, 2 cannot run
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from field_ownership import ENRICHMENT_FIELDS

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
CANNOT_RUN = 2

# Files a knowledge root holds that are not objects: the system declaration and the three
# projections the materializer derives.
RESERVED = {"system.md", "index.md", "glossary.md", "context-map.md"}

# The parameters each primitive requires and does not inherit. Read from the contract below rather
# than listed here would be better still; the contract states them as per-primitive conditionals on
# an attribute, and the same derivation walks them.
ATTRIBUTE_CONDITIONAL = ("$defs", "attribute", "allOf")

try:
    import yaml
except ImportError:  # pragma: no cover - exercised by the environment, not the suite
    print("cannot run: PyYAML is not installed (pip install pyyaml)", file=sys.stderr)
    raise SystemExit(CANNOT_RUN)


def frontmatter(path: Path) -> dict:
    match = re.match(r"^---\n(.*?)\n---\n", path.read_text(), re.S)
    if not match:
        raise ValueError("carries no frontmatter fence")
    return yaml.safe_load(match.group(1)) or {}


def excuses_by_gap(branch: dict) -> bool:
    """True where this branch of an alternation is the one that accepts a gap in the field's place."""
    return branch.get("required") == ["gaps"]


def offered_by(clause: dict) -> set[str]:
    """The fields one alternation demands, ignoring the branch that accepts a gap instead.

    A single-field clause offers one name. The one genuine alternation — a `rule` declares
    `expression` **or** `examples` — offers two, and they come back as one set because either
    satisfies it and a gap may legitimately name either.
    """
    return {
        field
        for branch in clause.get("anyOf", [])
        if not excuses_by_gap(branch)
        for field in branch.get("required", [])
    }


def conditional_obligation(nested: dict, data: dict) -> set[str]:
    """The obligation a conditional adds, on whichever side this object selects.

    The condition is read from whatever property it names rather than from `ddd` alone. A
    `definition` owes `identity` for three of its five `ddd` values, and an `interface` owes
    `upstream` when its `ownership` is `consumed` — same shape, different property. Reading only
    the first would leave `upstream` in no obligation, which is worse than missing a check: a gap
    legitimately naming it would be reported as naming something the kind does not require.

    Every named property must select the same side. A conditional over two properties is an `and`,
    and taking `then` because one of them matched would demand a field the contract does not.
    """
    condition = nested.get("if", {}).get("properties", {})
    if not condition:
        return set()
    matched = all(
        data.get(name) in (against.get("enum") or ([against["const"]] if "const" in against else []))
        for name, against in condition.items()
    )
    side = nested.get("then" if matched else "else") or {}
    return offered_by(side) or set(side.get("required", []))


def obligations(contract: dict, data: dict) -> list[set[str]]:
    """What this node type demands of an object with this `ddd`, as one entry per obligation.

    An obligation is a set of alternatives and is met by any one of them. Most hold a single field:
    a `definition` declares `attributes`, and nothing else will do. One is a genuine alternation —
    a `rule` declares `expression` **or** `examples` — and collapsing the two shapes into a flat
    set of names would lose the difference, which is exactly what the converse check needs: a rule
    carrying an expression owes no gap for its examples.

    Two contract shapes are read, because the profile is being narrowed and the two have to be
    readable by one checker while both exist.

    `domain-object/1` alternates once per **kind**: every field the kind requires, or `gaps`. That
    form is what made this function necessary — any gap over any field satisfies it, so the schema
    cannot tell an object short of `attributes` from one short of nothing, and `unnamed_absences`
    is where the difference is decided.

    The narrowed form alternates once per **field**, each against a gap naming that field, so the
    schema refuses what it used to admit. The obligations are the same either way, which is the
    point: this function reports what the kind demands, and neither shape changes that.

    A shape neither branch recognises yields an empty list, and an empty list is indistinguishable
    from a kind that demands nothing — every object would pass while nothing was checked. So an
    unrecognised `then` is raised rather than skipped.
    """
    node_type = data.get("type")
    found: list[set[str]] = []
    for clause in contract.get("allOf", []):
        if clause.get("if", {}).get("properties", {}).get("type", {}).get("const") != node_type:
            continue
        then = clause.get("then", {})

        if "allOf" in then and "anyOf" not in then:
            for nested in then["allOf"]:
                offered = conditional_obligation(nested, data) if "if" in nested else offered_by(nested)
                if offered:
                    found.append(offered)
            continue

        if "anyOf" in then:
            branch = then["anyOf"][0]
            found += [{field} for field in branch.get("required", [])]
            alternatives = offered_by(branch)
            if alternatives:
                found.append(alternatives)
            for nested in branch.get("allOf", []):
                offered = conditional_obligation(nested, data)
                if offered:
                    found.append(offered)
            continue

        raise ValueError(
            f"the contract states `{node_type}`'s requirements in a shape this checker does not "
            f"read: `then` carries {sorted(then)}. Reading it as no requirement would pass every "
            f"object of this kind while reporting nothing"
        )
    return found


def type_requirements(contract: dict, data: dict) -> set[str]:
    """Every field name an obligation of this object's type mentions, flattened."""
    return {field for obligation in obligations(contract, data) for field in obligation}


def attribute_parameters(contract: dict, primitive: str) -> set[str]:
    """What the contract requires of an attribute of this primitive, and does not inherit."""
    node = contract
    for step in ATTRIBUTE_CONDITIONAL:
        node = node.get(step, {})
    parameters: set[str] = set()
    for clause in node if isinstance(node, list) else []:
        condition = clause.get("if", {}).get("properties", {}).get("type", {})
        if condition.get("const") == primitive:
            parameters.update(clause.get("then", {}).get("required", []))
    return parameters


def nameable(contract: dict, data: dict) -> set[str]:
    """Every field name a gap on this object may legitimately carry.

    Dotted forms are expanded from the object rather than admitted as a pattern: `attributes[x].y`
    is nameable only where `x` is an attribute this object holds and `y` is a parameter its
    primitive requires, so a gap naming a parameter of an attribute nobody declared is refused.
    """
    fields = type_requirements(contract, data)
    names = set(fields)
    if "identity" in fields:
        # A required object whose own required part may be what is missing. The contract states
        # `identity.required = ["attributes"]`, so the dotted form names something real.
        for part in contract.get("properties", {}).get("identity", {}).get("required", []):
            names.add(f"identity.{part}")
    for attribute in data.get("attributes") or []:
        name, primitive = attribute.get("name"), attribute.get("type")
        if not name:
            continue
        for parameter in attribute_parameters(contract, primitive):
            names.add(f"attributes[{name}].{parameter}")
    return names


def missing_parameters(contract: dict, data: dict) -> list[tuple[str, str]]:
    """Each attribute parameter its primitive requires and the attribute does not carry.

    Two forms are admitted for a stated parameter — beside the attribute, or under `parameters` —
    because the contract admits both and a check that knew only one would report a fact the object
    holds as one it lacks.
    """
    absent: list[tuple[str, str]] = []
    for attribute in data.get("attributes") or []:
        name, primitive = attribute.get("name"), attribute.get("type")
        if not name:
            continue
        stated = set(attribute) | set(attribute.get("parameters") or {})
        for parameter in sorted(attribute_parameters(contract, primitive) - stated):
            absent.append((name, parameter))
    return absent


def excused(field: str, gapped: set[str]) -> bool:
    """True where a declared gap names this field, or the part of it that is missing.

    A gap may name `identity` or `identity.attributes`, and both say the same thing: the object
    does not have the identity its `ddd` requires. Matching on the root is what admits the second
    without admitting a gap about some unrelated field that happens to start alike.
    """
    return any(gap == field or gap.split(".")[0].split("[")[0] == field for gap in gapped)


def identity_of(data: dict, relative: str) -> list[str]:
    """The identifier against the path it computes to, and against the kind it names.

    An identifier is arithmetic — `dm.<kind>.<scope>.<slug>` becomes `<kind>/<scope>/<slug>.md`, and a
    kind that is itself a scope takes one segment fewer. Nothing allocates one, so a mismatch is a
    defect rather than a convention somebody is trusted to have followed.

    It cost nothing to check while a script computed both. It stops being free the moment the objects
    are written by judgment: an id that disagrees with its path breaks the one property every reference
    rests on, which is that a target resolves to a file without a lookup.
    """
    identifier, kind = data.get("id"), data.get("type")
    if not identifier or not kind:
        return []
    parts = identifier.split(".")
    if len(parts) < 3 or parts[0] != "dm":
        return [f"{relative}: `{identifier}` is not of the form dm.<kind>.<scope>.<slug>"]
    if parts[1] != kind:
        return [
            f"{relative}: `{identifier}` names kind `{parts[1]}` and the object declares `{kind}`. "
            f"The kind is in the identifier because the path is, and the two cannot disagree"
        ]
    expected = "/".join(parts[1:]) + ".md"
    if expected != relative:
        return [
            f"{relative}: `{identifier}` computes to `{expected}`. A path is derivable from an "
            f"identifier and an identifier from a path, with no lookup — a reference resolves by "
            f"that arithmetic and by nothing else"
        ]
    return []


def unnamed_absences(data: dict, contract: dict, authoring: set[str], relative: str) -> list[str]:
    """Every fact this object's type requires, does not hold, and does not declare a gap for.

    This is the converse of the check above, and without it the object's own alternation is only
    half enforced. The contract accepts an object that declares everything its type requires **or**
    declares `gaps` — any gap, over any field. So an object short of `attributes` while declaring a
    gap about its identity strategy satisfies the schema, and the gap check above passes it too,
    because the gap it declares does name a field the type requires.

    What nothing checked is whether the gap names *the fact that is missing*. Until now the
    expansion derived every gap mechanically from these same requirements, so the two could not
    disagree; a producer that writes its objects by judgment can leave a hole nobody named, and
    then an object incomplete in a way nobody stated passes as one whose incompleteness is
    justified.
    """
    found: list[str] = []
    gapped = {gap.get("field") for gap in data.get("gaps") or [] if gap.get("field")}
    node_type = data.get("type")

    for obligation in obligations(contract, data):
        # Present, rather than truthy. `attributes: []` on a domain error is the positive statement
        # that it holds none, and reading it as an absence would demand a gap for a fact the object
        # states. Whether empty is *allowed* is the schema's question, and it answers it per field.
        if any(field in data and data[field] is not None for field in obligation):
            continue
        if any(excused(field, gapped) for field in obligation):
            continue
        wanted = " or ".join(f"`{field}`" for field in sorted(obligation))
        found.append(
            f"{relative}: a {node_type} declares {wanted}, and this object declares neither the "
            f"fact nor a gap naming it. An object incomplete in a way nobody named is "
            f"indistinguishable from one whose incompleteness is justified"
        )

    for name, parameter in missing_parameters(contract, data):
        if f"attributes[{name}].{parameter}" not in gapped:
            found.append(
                f"{relative}: attribute `{name}` states no `{parameter}`, which its primitive "
                f"requires, and no gap names `attributes[{name}].{parameter}`"
            )

    for field in sorted(authoring):
        if field not in data and not excused(field, gapped):
            found.append(
                f"{relative}: `{field}` is unwritten and no `authoring` gap names it. The gap is "
                f"what tells a pass that has not run from a field nobody owes"
            )

    return found


def problems_for(data: dict, contract: dict, authoring: set[str], relative: str) -> list[str]:
    """Every gap that names something its type does not require, and every absence nothing names."""
    found: list[str] = unnamed_absences(data, contract, authoring, relative)
    allowed = nameable(contract, data)
    for gap in data.get("gaps") or []:
        field, kind = gap.get("field"), gap.get("kind")
        if kind == "authoring":
            if field not in authoring:
                found.append(
                    f"{relative}: the `authoring` gap names `{field}`, which no pass of this "
                    f"framework writes. The closed set is {', '.join(sorted(authoring))}"
                )
            elif data.get(field):
                found.append(
                    f"{relative}: `{field}` is written and its `authoring` gap is still open — "
                    f"closing the gap is what records that the field was filled"
                )
            continue
        if field in allowed:
            root = field.split(".")[0].split("[")[0]
            if data.get(root) is not None and "." not in field and "[" not in field:
                found.append(
                    f"{relative}: the `domain` gap names `{field}`, which this object declares. A "
                    f"gap records a fact that is missing, and one beside the fact it names would "
                    f"keep an object out of the base for something it already holds"
                )
            continue
        found.append(
            f"{relative}: the `domain` gap names `{field}`, which a {data.get('type')} does not "
            f"require. It excuses the object from nothing, and an object incomplete in a way "
            f"nobody named would pass as one whose incompleteness is justified"
        )
    return found


def expanded_rejections(data: dict) -> set[tuple[str, str]]:
    """Every (state, trigger) pair the rejections cover, with both shorthands expanded.

    A trigger list stands for one entry per trigger, and `from: terminal` stands for every state the
    object lists as terminal. Both exist so a declaration states decisions rather than padding, and
    both have to be expanded before the product can be checked — a check reading the shorthand
    literally would report a table as incomplete because it was written economically.
    """
    terminal = list(data.get("terminal") or [])
    covered: set[tuple[str, str]] = set()
    for rejection in data.get("rejections") or []:
        triggers = rejection.get("trigger")
        triggers = triggers if isinstance(triggers, list) else [triggers]
        origin = rejection.get("from")
        states = terminal if origin == "terminal" else [origin]
        for state in states:
            for trigger in triggers:
                if state and trigger:
                    covered.add((state, trigger))
    return covered


def totality_of(data: dict, relative: str) -> list[str]:
    """Every state-and-trigger pair this lifecycle leaves undecided."""
    states = list(data.get("states") or [])
    transitions = data.get("transitions") or []
    triggers = sorted({t.get("trigger") for t in transitions if t.get("trigger")}
                      | {trigger for _state, trigger in expanded_rejections(data)})
    if not states or not triggers:
        return []
    decided = {(t.get("from"), t.get("trigger")) for t in transitions} | expanded_rejections(data)
    # Every pairing, terminal states included. A terminal state has no *outgoing transition*, which
    # is a different statement from having no decision: what a proposal does when issued twice is a
    # fact the domain owns, and exempting the state here would let the table stay silent about it.
    missing = [
        (state, trigger)
        for state in states
        for trigger in triggers
        if (state, trigger) not in decided
    ]
    if not missing:
        return []
    shown = ", ".join(f"{state} + {trigger}" for state, trigger in missing[:6])
    more = f" and {len(missing) - 6} more" if len(missing) > 6 else ""
    return [
        f"{relative}: the transition table is not total. Undecided: {shown}{more}. Every pairing is "
        f"either a transition or a rejection — an incomplete table is where whatever produces "
        f"software later invents behaviour, and it invents it silently"
    ]


def cross_object(objects: dict[str, dict], paths: dict[str, str]) -> list[str]:
    """The rules no single file can decide, each needing more than one object to answer.

    A lifecycle cannot see whether another claims its subject. An object cannot see which context
    its reference target sits in without reading that target. Containment cannot be shown to be a
    forest from inside one node, and an aggregate cannot see whether the definition it names as
    root agrees that it is one.

    What these have in common is that the schema cannot reach them: every one of them compares two
    objects, and a boundary validator is handed one.
    """
    problems: list[str] = []

    claimed: dict[str, list[str]] = {}
    for identifier, data in objects.items():
        if data.get("type") == "lifecycle" and data.get("subject"):
            claimed.setdefault(data["subject"], []).append(identifier)
    for subject, holders in sorted(claimed.items()):
        if len(holders) > 1:
            problems.append(
                f"{subject} is claimed by {len(holders)} lifecycles — {', '.join(sorted(holders))}. "
                f"A definition with two state machines has no single state set to generate from, and "
                f"which one binds is a question neither file answers"
            )

    # Containment must be a forest before anything walks it. `boundary` admits an aggregate inside
    # an aggregate, so a loop is expressible, and a loop makes the scope of every node on it
    # undefined. Reported here rather than absorbed by the `seen` guard below: a walk that stops
    # quietly on a cycle answers "no context" for a node whose context is not missing but circular,
    # and the two want different repairs.
    for identifier in sorted(objects):
        seen: list[str] = []
        current: str | None = identifier
        while current and current in objects and current not in seen:
            seen.append(current)
            data = objects[current]
            current = data.get("subdomain") if data.get("type") == "context" else data.get("boundary")
        if current and current in seen:
            loop = seen[seen.index(current):]
            problems.append(
                f"{paths.get(identifier, identifier)}: containment closes a loop — "
                f"{' -> '.join(loop + [current])}. A scope that contains itself leaves every node "
                f"inside it with no partition root, and the walk that resolves one does not end"
            )

    for identifier, data in sorted(objects.items()):
        boundary = data.get("boundary")
        if not boundary:
            continue
        own, parent = str(identifier).split("."), str(boundary).split(".")
        if len(own) < 3 or len(parent) < 3 or own[2] == parent[2]:
            continue
        problems.append(
            f"{paths.get(identifier, identifier)}: `{identifier}` is filed under context "
            f"`{own[2]}` and declares `{boundary}`, which sits in `{parent[2]}`. The parent is "
            f"written twice — once in the identifier, which fixes the path, and once in `boundary`, "
            f"which fixes membership — and a node whose two parents disagree sits in two trees"
        )

    for identifier, data in sorted(objects.items()):
        if data.get("type") != "aggregate" or not data.get("root"):
            continue
        root = data["root"]
        if root not in objects:
            continue  # unresolved is reported above; this rule is about what a held root says
        held = objects[root]
        if held.get("ddd") != "aggregate-root":
            problems.append(
                f"{paths.get(identifier, identifier)}: `root` names {root}, whose `ddd` is "
                f"`{held.get('ddd')}`. That this definition heads an aggregate is stated twice — "
                f"by this edge and by its own `ddd` — and the two disagree"
            )
        if held.get("boundary") != identifier:
            problems.append(
                f"{paths.get(identifier, identifier)}: `root` names {root}, whose `boundary` is "
                f"`{held.get('boundary')}` rather than this aggregate. A root outside the aggregate "
                f"it heads is not its entry point"
            )

    # Every edge names an identifier, and every identifier has to be one the base holds. Reported
    # and never repaired: a repair would either invent the missing node or drop the edge, and each
    # decides a domain question on behalf of whoever owns it. This is also what makes a deletion
    # safe to allow — removing a node is legal, and leaving something pointing at it is not.
    for identifier, data in sorted(objects.items()):
        for target, locator in references(data) + structural_references(data):
            if target in objects:
                continue
            problems.append(
                f"{paths.get(identifier, identifier)}: {locator} names {target}, which the base "
                f"does not hold. A reference resolves by arithmetic and by nothing else, so an "
                f"identifier nothing sits at is a defect rather than a node somewhere else"
            )

    for identifier, data in sorted(objects.items()):
        if data.get("type") != "interface" or not data.get("upstream"):
            continue
        held = objects.get(data["upstream"])
        if held is not None and held.get("ownership") != "published":
            problems.append(
                f"{paths.get(identifier, identifier)}: `upstream` names {data['upstream']}, whose "
                f"`ownership` is `{held.get('ownership')}`. A consumed interface pointing at another "
                f"consumed one records two copies of a contract and no owner — the chain ends at the "
                f"context that owes compatibility"
            )

    for identifier, data in sorted(objects.items()):
        if data.get("type") != "lifecycle":
            continue
        for index, transition in enumerate(data.get("transitions") or []):
            for emitted in transition.get("emits") or []:
                held = objects.get(emitted)
                if held is None or held.get("ddd") in ("domain-event", "integration-event"):
                    continue
                problems.append(
                    f"{paths.get(identifier, identifier)}: transitions[{index}].emits names "
                    f"{emitted}, whose `ddd` is `{held.get('ddd')}`. A state change raises something "
                    f"that happened; an api is called and a command is sent, and a transition raises "
                    f"neither"
                )

    def aggregate_of(identifier: str) -> str | None:
        """The aggregate an object sits in, or None where it sits directly in a context."""
        boundary = objects.get(identifier, {}).get("boundary")
        return boundary if str(boundary).startswith("dm.aggregate.") else None

    for identifier, data in sorted(objects.items()):
        if data.get("type") != "rule" or data.get("consistency"):
            continue
        home = aggregate_of(identifier)
        reaches = [
            target
            for target in data.get("depends_on") or []
            if target in objects and aggregate_of(target) != home
        ]
        if not reaches:
            continue
        if excused("consistency", {gap.get("field") for gap in data.get("gaps") or []}):
            continue
        problems.append(
            f"{paths.get(identifier, identifier)}: this rule reaches {', '.join(sorted(reaches))}, "
            f"outside the aggregate it is written in, and declares no `consistency`. A rule spanning "
            f"two aggregates cannot hold inside one transaction, and a boundary wide enough to hide "
            f"that question is drawn wrong"
        )

    def context_of(identifier: str) -> str | None:
        """The bounded context an object sits in, followed up through its scopes."""
        seen: set[str] = set()
        current = identifier
        while current and current in objects and current not in seen:
            seen.add(current)
            data = objects[current]
            if data.get("type") == "context":
                return current
            current = data.get("boundary")
        return current if current and str(current).startswith("dm.context.") else None

    for identifier, data in sorted(objects.items()):
        origin = context_of(identifier)
        if not origin:
            continue
        for edge, locator in references(data):
            if edge not in objects:
                continue
            if context_of(edge) in (None, origin):
                continue
            if objects[edge].get("type") == "interface":
                continue
            problems.append(
                f"{paths.get(identifier, identifier)}: {locator} names {edge}, which sits in another "
                f"bounded context and is not an interface. What crosses a boundary is a published "
                f"contract; reaching into another context's internals is how a boundary stops being one"
            )
    return problems


def structural_references(data: dict) -> list[tuple[str, str]]:
    """The two edges that say where an object sits: `boundary`, and a context's `subdomain`.

    Held apart from `references` because the crossing rule must not see them. `boundary` crossing
    a bounded context is not a violation — it is what the field is *for*, since the context a node
    belongs to is named from outside it — so folding these in there would report every node in the
    base. Resolution has no such exemption: a `boundary` naming a scope the base does not hold is
    a node whose parent is missing, which is the same defect as any other unresolved edge and a
    worse one, because the parent is what the path is derived from.
    """
    found: list[tuple[str, str]] = []
    for field in ("boundary", "subdomain"):
        target = data.get(field)
        if isinstance(target, str) and target:
            found.append((target, field))
    return found


def references(data: dict) -> list[tuple[str, str]]:
    """Every content identifier this object points at, with where it sits.

    `boundary` and `subdomain` are not here; see `structural_references` for why.
    """
    found: list[tuple[str, str]] = []
    for index, target in enumerate(data.get("depends_on") or []):
        found.append((target, f"depends_on[{index}]"))
    for attribute in data.get("attributes") or []:
        name = attribute.get("name", "?")
        for field in ("target", "of", "lifecycle"):
            if attribute.get(field):
                found.append((attribute[field], f"attributes[{name}].{field}"))
    if data.get("subject"):
        found.append((data["subject"], "subject"))
    for index, transition in enumerate(data.get("transitions") or []):
        if transition.get("guard"):
            found.append((transition["guard"], f"transitions[{index}].guard"))
        for position, emitted in enumerate(transition.get("emits") or []):
            found.append((emitted, f"transitions[{index}].emits[{position}]"))
    for field in ("payload", "upstream"):
        if data.get(field):
            found.append((data[field], field))
    for index, rejection in enumerate(data.get("rejections") or []):
        if rejection.get("error"):
            found.append((rejection["error"], f"rejections[{index}].error"))
    for index, step in enumerate(data.get("steps") or []):
        # `domain-object/1` spells this `ko` and the narrowed profile spells it `node`. Both are
        # read while both exist: a step whose target went unresolved because the checker knew one
        # spelling is an edge missing from the graph, not an edge that resolves.
        for spelling in ("node", "ko"):
            if step.get(spelling):
                found.append((step[spelling], f"steps[{index}].{spelling}"))
                break
        if step.get("compensated_by"):
            found.append((step["compensated_by"], f"steps[{index}].compensated_by"))
    if data.get("root"):
        found.append((data["root"], "root"))
    return found


def contract_path() -> Path:
    """Where the frontmatter contract sits, for a caller that wants to read it once."""
    return PLUGIN_ROOT / "schemas" / "domain-object.json"


def problems_in(root: Path, contract: dict) -> tuple[list[str], int, int]:
    """Every disagreement this whole base holds, with the gap and object counts behind it.

    Separated from `main` so that something other than a command line can ask. The change door
    calls this before it will let a change close: a change that finishes while the graph does not
    resolve clears the set of touched nodes, and then the incoherence is still there with nothing
    left saying where to look for it.

    Returns rather than prints, and never repairs. A caller decides what a problem means — the
    command line exits non-zero, the door refuses to close — and neither is this function's to
    decide.
    """
    # The derived files carry no frontmatter and are not objects. Skipped by name rather than by
    # trying to parse them: a reader who has just run the materializer would otherwise be told the
    # index is malformed, which is true of every index and useful about none.
    objects = [p for p in sorted(Path(root).rglob("*.md")) if p.name not in RESERVED]

    # The fields no analysis carries, read from the one module that declares the ownership line.
    # It used to be derived as the difference between two contracts' required sets, which worked
    # while a second contract existed to differ — and said nothing once the profile was one.
    authoring = set(ENRICHMENT_FIELDS)

    problems: list[str] = []
    held: dict[str, dict] = {}
    where: dict[str, str] = {}
    declared = 0
    for path in objects:
        relative = path.relative_to(root).as_posix()
        try:
            data = frontmatter(path)
        except ValueError as broken:
            problems.append(f"{relative}: {broken}")
            continue
        declared += len(data.get("gaps") or [])
        problems += problems_for(data, contract, authoring, relative)
        problems += identity_of(data, relative)
        if data.get("type") == "lifecycle":
            problems += totality_of(data, relative)
        if data.get("id"):
            held[data["id"]] = data
            where[data["id"]] = relative

    problems += cross_object(held, where)
    return problems, declared, len(held)


def main() -> int:
    if len(sys.argv) != 2:
        print("cannot run: expected <knowledge-root>", file=sys.stderr)
        return CANNOT_RUN
    root = Path(sys.argv[1])
    if not root.is_dir():
        print(f"cannot run: {root} is not a directory", file=sys.stderr)
        return CANNOT_RUN

    if not contract_path().is_file():
        print(f"cannot run: {contract_path()} is missing", file=sys.stderr)
        return CANNOT_RUN
    contract = json.loads(contract_path().read_text())

    if not [p for p in root.rglob("*.md") if p.name not in RESERVED]:
        print(f"cannot run: {root} holds no object", file=sys.stderr)
        return CANNOT_RUN

    problems, declared, count = problems_in(root, contract)

    print(f"knowledge checked: {declared} gap(s) and {count} object(s), with identifier "
          f"arithmetic, lifecycle totality, one lifecycle per subject, acyclic containment, "
          f"boundary against identifier, an aggregate against its root, a consumed interface "
          f"against its publisher, what a transition may emit, consistency on a rule that reaches "
          f"outside its aggregate, every reference resolving, and what may cross a context  "
          f"contract: "
          f"{contract['properties']['contract_version']['const']}")
    if problems:
        print(f"FAILED: {len(problems)} disagreement(s) between what is declared and what is named\n")
        for problem in problems:
            print(f"  {problem}")
        return 1
    print("every identifier computes to the path it sits at, every gap names a fact its kind requires "
          "and the object lacks, every fact it lacks is named by a gap, and the nine cross-object "
          "rules hold")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
