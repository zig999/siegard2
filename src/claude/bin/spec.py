#!/usr/bin/env python3
"""Validate a Siegard specification against the five-class metamodel, and derive its projections.

The path is the identity (SPEC-003 R1). `domain/<context>/<slug>.md` is a Domain Model element
and `domain/<context>/_context.md` its context descriptor; `rules/`, `scenarios/` and
`contracts/` follow the same shape; `constraints/<slug>.md` is system-wide work; and
`decision-log.md` at the root is the one mandatory non-normative artifact. No file carries an
id, a name or a class field, so none can disagree with where it sits.

**The schema decides one file; this script decides what needs two.** Per-file validation is
`schemas/spec/*.json` applied as written. On top run the checks no per-file schema can express:
every reference resolves and lands on the class the field demands, an attribute never points at
an identity-bearing element and a relationship never points at a value (one home per fact,
SPEC-002 R8), composition stays inside its aggregate, an invariant stays inside one aggregate
and a crossing policy says how it converges, a state machine is total over its states and
triggers, every entity, value object and enumeration is reachable (SPEC-001 R6), and every
decision-log entry locates a file and field that exist (SPEC-001 R9).

**No provenance meta-fields.** A `gaps`, `sources`, `rationale` or `proposal` key is refused
with its own message (SPEC-001 R8): a fact the material does not state is decided and disclosed
in the decision log, never marked in an artifact.

**Projections are derived, never edited.** `--project` writes `projections/` from the files —
class diagrams, the context map (a context pair with no contract between them has gone separate
ways, and the map says so), state diagrams, the capability map and the overview — sorted
throughout, so identical input is byte-identical output. They are refused entirely while the
specification has problems.

**Every node's digest is content identity.** `--digest` prints `<identity>  sha256:<hexdigest>`
for every node, one line each, sorted by identity — the hash of the exact bytes of its file, the
same value `sha256sum <path>` computes by hand. This script keeps no second copy of it: it exists
so something outside this script, living beside generated code rather than inside the
specification, can pin which version of a node it was written against and later ask whether that
node moved. Refused entirely while the specification has problems, the same as `--project`.

**A file can be checked on its own while it is being written.** `--node <file>` applies the
one schema its class demands and nothing else: no reference resolution, no reachability, no
decision-log check — those need the whole specification, and a file mid-authoring has not
earned them yet. It is refused the same as any file the whole run would refuse; it just does
not also fail for references a later file in the same session has not been written yet either.

Declared dependencies: PyYAML, jsonschema.

Usage:  spec.py <spec-root>              validate everything
        spec.py --project <spec-root>    validate, then write projections/
        spec.py --digest <spec-root>     validate, then print every node's content digest
        spec.py --node <file> <spec-root>
                                          validate one file (cross-node checks do not run)
Exit:   0 sound
        1 problems
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
SCHEMA_DIR = PLUGIN_ROOT / "schemas" / "spec"
PROJECTIONS = "projections"
SYSTEM = "system"
PRIMITIVES = ("string", "integer", "decimal", "boolean", "date", "datetime")
META_FIELDS = ("gaps", "sources", "rationale", "proposal")

SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
FENCE = re.compile(r"^---\n(.*?)\n---\n?", re.S)

SCHEMAS = {"context": "context.json", "element": "element.json", "rule": "rule.json",
           "scenario": "scenario.json", "contract": "contract.json",
           "constraint": "constraint.json", "log": "decision-log.json"}
HEADINGS = {"context": ["## Description", "## Responsibility"],
            "element": ["## Description", "## Responsibility"],
            "rule": ["## Description"], "scenario": ["## Description"],
            "contract": ["## Description"], "constraint": ["## Description"],
            "log": None}
STEREOTYPES = {"aggregate-root": "AggregateRoot", "entity": "Entity",
               "value-object": "ValueObject", "domain-service": "Service",
               "enumeration": "Enumeration"}
ARROWS = {"composition": "*--", "reference": "-->", "association": "--"}


def classify(relative: Path) -> tuple[str, str | None, str] | None:
    """(class, context, slug) this path computes to, or None where it computes to nothing."""
    if relative.suffix != ".md":
        return None
    parts = relative.with_suffix("").parts
    if parts == ("decision-log",):
        return ("log", None, "decision-log")
    if len(parts) == 3 and parts[0] == "domain" and parts[2] == "_context":
        return ("context", parts[1], parts[1]) if SLUG.match(parts[1]) else None
    if len(parts) == 3 and parts[0] in ("domain", "rules", "scenarios", "contracts"):
        cls = {"domain": "element", "rules": "rule",
               "scenarios": "scenario", "contracts": "contract"}[parts[0]]
        if SLUG.match(parts[1]) and SLUG.match(parts[2]):
            return (cls, parts[1], parts[2])
        return None
    if len(parts) == 2 and parts[0] == "constraints" and SLUG.match(parts[1]):
        return ("constraint", None, parts[1])
    return None


def digest_of(path: Path) -> str:
    """Content identity: sha256 of the file's exact bytes, computable by hand as `sha256sum`."""
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def reduce_display(display: str) -> str:
    """The slug a display form reduces back to."""
    spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", "-", display)
    return spaced.replace(" ", "-").replace("_", "-").lower()


def pascal(node: dict) -> str:
    if isinstance(node["front"].get("display"), str):
        return node["front"]["display"]
    return "".join(part.capitalize() for part in node["slug"].split("-"))


def camel(slug: str) -> str:
    parts = re.split(r"[-_]", slug)
    return parts[0] + "".join(part.capitalize() for part in parts[1:])


def body_problems(cls: str, body: str) -> list[str]:
    expected = HEADINGS[cls]
    if expected is None:
        return []
    headings = [line.rstrip() for line in body.splitlines() if line.startswith("## ")]
    if headings != expected:
        return [f"body headings are {headings if headings else 'absent'}; "
                f"this class carries exactly {expected}"]
    return []


def contracts() -> dict[str, Draft202012Validator]:
    validators = {}
    for cls, name in SCHEMAS.items():
        path = SCHEMA_DIR / name
        if not path.is_file():
            raise FileNotFoundError(f"{path} is missing; nothing can be validated without it")
        validators[cls] = Draft202012Validator(json.loads(path.read_text(encoding="utf-8")))
    return validators


def collect(root: Path, validators) -> tuple[dict[str, dict], list[str]]:
    """Every file in the specification, and everything wrong with the files on their own."""
    nodes: dict[str, dict] = {}
    problems: list[str] = []
    for path in sorted(root.rglob("*.md")):
        relative = path.relative_to(root)
        if relative.parts[0] == PROJECTIONS:
            continue  # derived, never validated as source
        placed = classify(relative)
        if placed is None:
            problems.append(f"{relative.as_posix()}: the path computes to no identity; "
                            f"see the layout in SPEC-003")
            continue
        cls, context, slug = placed
        identity = "/".join(relative.with_suffix("").parts)
        text = path.read_text(encoding="utf-8")
        match = FENCE.match(text)
        if not match:
            problems.append(f"{identity}: carries no frontmatter fence")
            continue
        try:
            front = yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError as broken:
            problems.append(f"{identity}: frontmatter does not parse: {broken}")
            continue
        if not isinstance(front, dict) or any(not isinstance(k, str) for k in front):
            problems.append(f"{identity}: frontmatter is not a mapping of string keys")
            continue
        for field in META_FIELDS:
            if field in front:
                problems.append(
                    f"{identity}: carries `{field}`, a provenance meta-field; a fact the "
                    f"material does not state is decided and disclosed in the decision log, "
                    f"never marked in an artifact (SPEC-001 R8)")
        front = {k: v for k, v in front.items() if k not in META_FIELDS}
        for error in validators[cls].iter_errors(front):
            where = ".".join(str(part) for part in error.absolute_path) or "frontmatter"
            problems.append(f"{identity}: {where}: {error.message}")
        problems += [f"{identity}: {p}" for p in body_problems(cls, text[match.end():])]
        display = front.get("display")
        if isinstance(display, str) and reduce_display(display) != slug:
            problems.append(f"{identity}: display `{display}` reduces to "
                            f"`{reduce_display(display)}`, not to the slug `{slug}`")
        nodes[identity] = {"cls": cls, "context": context, "slug": slug, "front": front,
                           "digest": digest_of(path)}
    return nodes, problems


def check_single(root: Path, named: str, validators) -> int:
    """One file against its own schema, nothing more — the per-file half of `collect`, without
    the walk and without anything that needs to see a second file."""
    path = Path(named)
    if not path.is_absolute():
        path = (root / named) if (root / named).is_file() else Path.cwd() / named
    try:
        relative = path.resolve().relative_to(root.resolve())
    except ValueError:
        print(f"cannot run: {named} is not under {root}", file=sys.stderr)
        return CANNOT_RUN
    if relative.parts and relative.parts[0] == PROJECTIONS:
        print(f"{relative.as_posix()}: sits under {PROJECTIONS}/, which is derived and "
              f"never validated as source")
        return 0
    placed = classify(relative)
    if placed is None:
        print(f"{relative.as_posix()}: the path computes to no identity; "
              f"see the layout in SPEC-003")
        return 1
    cls, _, slug = placed
    identity = "/".join(relative.with_suffix("").parts)
    if not path.is_file():
        print(f"cannot run: {path} does not exist", file=sys.stderr)
        return CANNOT_RUN
    text = path.read_text(encoding="utf-8")
    match = FENCE.match(text)
    if not match:
        print(f"{identity}: carries no frontmatter fence")
        return 1
    try:
        front = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as broken:
        print(f"{identity}: frontmatter does not parse: {broken}")
        return 1
    if not isinstance(front, dict) or any(not isinstance(k, str) for k in front):
        print(f"{identity}: frontmatter is not a mapping of string keys")
        return 1

    problems: list[str] = []
    for field in META_FIELDS:
        if field in front:
            problems.append(
                f"carries `{field}`, a provenance meta-field; a fact the material does not "
                f"state is decided and disclosed in the decision log, never marked in an "
                f"artifact (SPEC-001 R8)")
    checked = {k: v for k, v in front.items() if k not in META_FIELDS}
    for error in validators[cls].iter_errors(checked):
        where = ".".join(str(part) for part in error.absolute_path) or "frontmatter"
        problems.append(f"{where}: {error.message}")
    problems += body_problems(cls, text[match.end():])
    display = checked.get("display")
    if isinstance(display, str) and reduce_display(display) != slug:
        problems.append(f"display `{display}` reduces to `{reduce_display(display)}`, "
                        f"not to the slug `{slug}`")

    for problem in problems:
        print(f"{identity}: {problem}")
    if problems:
        return 1
    print(f"{identity}: sound on its own. Cross-node checks did not run; "
          f"they run on the whole specification.")
    return 0


def resolve(ref: str, context: str | None) -> str:
    """A bare slug resolves inside its own context's domain directory; everything else is
    already an identity (SPEC-003 R2)."""
    return ref if "/" in ref else f"domain/{context}/{ref}"


def aggregate_of(node: dict) -> tuple[str, str] | None:
    """The (context, root-slug) boundary an element sits in, or None for the shareable kinds."""
    kind = node["front"].get("type")
    if kind == "aggregate-root":
        return (node["context"], node["slug"])
    if kind == "entity" and isinstance(node["front"].get("aggregate"), str):
        return (node["context"], node["front"]["aggregate"])
    return None


def element_refs(node: dict) -> list[tuple[str, str, str]]:
    """Every reference one element declares: (target identity, expectation, locator)."""
    refs: list[tuple[str, str, str]] = []
    front, context = node["front"], node["context"]
    for attribute in front.get("attributes") or []:
        if not isinstance(attribute, dict):
            continue
        declared = attribute.get("type")
        if isinstance(declared, str) and declared not in PRIMITIVES:
            refs.append((resolve(declared, context), "value",
                         f"attributes[{attribute.get('name', '?')}].type"))
    for index, entry in enumerate(front.get("relationships") or []):
        if isinstance(entry, dict) and isinstance(entry.get("target"), str):
            refs.append((resolve(entry["target"], context), "identity-bearing",
                         f"relationships[{index}].target"))
    if isinstance(front.get("aggregate"), str):
        refs.append((resolve(front["aggregate"], context), "root", "aggregate"))
    return refs


def state_machine_problems(identity: str, node: dict, nodes: dict[str, dict]) -> list[str]:
    """Anchors, state coherence, and totality — the check that must survive the redesign."""
    problems: list[str] = []
    front = node["front"]
    status = nodes.get(front.get("status", ""))
    states: list[str] = []
    if status is None or status["cls"] != "element" \
            or status["front"].get("type") != "enumeration":
        problems.append(f"{identity}: status must name an enumeration; the states are its values")
    else:
        states = [v for v in status["front"].get("values") or [] if isinstance(v, str)]
    subject = nodes.get(front.get("subject", ""))
    if subject is None or subject["cls"] != "element" \
            or subject["front"].get("type") != "aggregate-root":
        problems.append(f"{identity}: subject must name an aggregate root")

    declared = set(states)
    terminal = {s for s in front.get("terminal") or [] if isinstance(s, str)}
    transitions = [t for t in front.get("transitions") or [] if isinstance(t, dict)]
    rejections = [r for r in front.get("rejections") or [] if isinstance(r, dict)]

    def held(state, at: str) -> None:
        if isinstance(state, str) and declared and state not in declared:
            problems.append(f"{identity}: {at} names `{state}`, which is not a value of "
                            f"{front.get('status')}")

    held(front.get("initial"), "initial")
    for state in sorted(terminal):
        held(state, "terminal")
    for index, transition in enumerate(transitions):
        held(transition.get("from"), f"transitions[{index}].from")
        held(transition.get("to"), f"transitions[{index}].to")
    for index, rejection in enumerate(rejections):
        held(rejection.get("from"), f"rejections[{index}].from")

    covered: dict[tuple, int] = {}
    for entry in transitions + rejections:
        pair = (entry.get("from"), entry.get("trigger"))
        covered[pair] = covered.get(pair, 0) + 1
    for pair, count in sorted(covered.items(), key=str):
        if count > 1:
            problems.append(f"{identity}: state `{pair[0]}` decides trigger `{pair[1]}` "
                            f"{count} times; one pairing, one decision")
    triggers = sorted({entry.get("trigger") for entry in transitions + rejections
                       if isinstance(entry.get("trigger"), str)})
    for state in states:
        if state in terminal:
            continue  # terminal is declared, and declared is what exempts it
        for trigger in triggers:
            if (state, trigger) not in covered:
                problems.append(
                    f"{identity}: state `{state}` has no transition and no rejection for "
                    f"trigger `{trigger}`; an undecided pairing is a decision to make and "
                    f"log, never silence")
    return problems


def cross_problems(nodes: dict[str, dict], root: Path) -> list[str]:
    """The rules that need to see more than one file at once."""
    problems: list[str] = []
    elements = {i: n for i, n in nodes.items() if n["cls"] == "element"}
    contexts = sorted({n["context"] for n in nodes.values()
                       if n["cls"] in ("element", "context")})
    referenced: set[str] = set()

    def landing(identity: str, expectation: str, owner: str, at: str) -> dict | None:
        target = nodes.get(identity)
        if target is None:
            problems.append(f"{owner}: {at} names {identity}, "
                            f"which the specification does not hold")
            return None
        referenced.add(identity)
        return target

    # --- namespaces and the floor
    for reserved in (f"domain/{SYSTEM}", f"rules/{SYSTEM}"):
        if any(i.startswith(reserved + "/") for i in nodes):
            problems.append(f"{reserved}: `{SYSTEM}` is a reserved namespace; "
                            f"no bounded context may take that slug (SPEC-003 R3)")
    if SYSTEM in contexts:
        contexts.remove(SYSTEM)
    for context in contexts:
        if f"domain/{context}/_context" not in nodes:
            problems.append(f"domain/{context}: carries no _context.md; every context "
                            f"declares its descriptor")
        if not any(n["context"] == context for n in elements.values()):
            problems.append(f"domain/{context}: holds no element; a linguistic boundary "
                            f"with no language is not comprehensible (SPEC-001 R2)")
    for identity, node in sorted(nodes.items()):
        if node["cls"] in ("rule", "scenario", "contract") and node["context"] != SYSTEM \
                and node["context"] not in contexts:
            problems.append(f"{identity}: sits under context `{node['context']}`, "
                            f"which domain/ does not declare")

    # --- elements
    for identity, node in sorted(elements.items()):
        front = node["front"]
        for target_id, expectation, at in element_refs(node):
            target = landing(target_id, expectation, identity, at)
            if target is None or target["cls"] != "element":
                if target is not None:
                    problems.append(f"{identity}: {at} names {target_id}, "
                                    f"which is not a Domain Model element")
                continue
            kind = target["front"].get("type")
            if expectation == "value" and kind not in ("value-object", "enumeration"):
                problems.append(f"{identity}: {at} names {target_id}, a {kind}; a link to an "
                                f"identity-bearing element is a relationship, never an "
                                f"attribute (SPEC-002 R8)")
            if expectation == "identity-bearing" \
                    and kind not in ("entity", "aggregate-root"):
                problems.append(f"{identity}: {at} names {target_id}, a {kind}; a link to a "
                                f"value is an attribute, never a relationship (SPEC-002 R8)")
            if expectation == "root" and kind != "aggregate-root":
                problems.append(f"{identity}: {at} names {target_id}, a {kind}; an entity "
                                f"belongs to an aggregate root")
        by_target: dict[str, list[dict]] = {}
        for index, entry in enumerate(front.get("relationships") or []):
            if not isinstance(entry, dict) or not isinstance(entry.get("target"), str):
                continue
            target_id = resolve(entry["target"], node["context"])
            by_target.setdefault(target_id, []).append(entry)
            target = nodes.get(target_id)
            if target is None or target["cls"] != "element":
                continue
            kind = target["front"].get("type")
            if entry.get("type") == "composition":
                if front.get("type") not in ("aggregate-root", "entity"):
                    problems.append(f"{identity}: relationships[{index}] composes, and a "
                                    f"{front.get('type')} has no consistency boundary to "
                                    f"compose into")
                elif kind != "entity":
                    problems.append(f"{identity}: relationships[{index}] composes {target_id}, "
                                    f"a {kind}; composition holds entities inside one "
                                    f"aggregate (SPEC-002 R11)")
                elif aggregate_of(target) != aggregate_of(node):
                    problems.append(f"{identity}: relationships[{index}] composes {target_id}, "
                                    f"which sits in aggregate {aggregate_of(target)}; "
                                    f"composition never crosses an aggregate boundary "
                                    f"(SPEC-002 R11)")
            if entry.get("type") == "reference" and kind != "aggregate-root":
                problems.append(f"{identity}: relationships[{index}] references {target_id}, "
                                f"a {kind}; a reference points at another aggregate's root, "
                                f"by identity (SPEC-002 R11)")
        for target_id, entries in sorted(by_target.items()):
            if len(entries) > 1 and any(not isinstance(e.get("role"), str) for e in entries):
                problems.append(f"{identity}: {len(entries)} relationships share the target "
                                f"{target_id} and not all carry `role`; unlabeled edges to "
                                f"one target are indistinguishable (SPEC-002 R10)")

    # --- rules
    machines: dict[str, list[str]] = {}
    for identity, node in sorted(nodes.items()):
        if node["cls"] != "rule":
            continue
        front = node["front"]
        boundaries: set[tuple[str, str]] = set()
        spanned: set[str] = set()
        for index, target_id in enumerate(front.get("constrains") or []):
            target = landing(target_id, "element", identity, f"constrains[{index}]")
            if target is None or target["cls"] != "element":
                continue
            spanned.add(target["context"])
            boundary = aggregate_of(target)
            if boundary:
                boundaries.add(boundary)
        crossing = len(boundaries) > 1 or len(spanned) > 1
        if front.get("type") == "invariant" and crossing:
            problems.append(f"{identity}: an invariant constrains inside one aggregate, and "
                            f"this one spans {sorted(boundaries) or sorted(spanned)}; what "
                            f"crosses a boundary is a policy declaring how it converges")
        if front.get("type") == "policy" and crossing:
            if front.get("consistency") is None:
                problems.append(f"{identity}: constrains crosses a boundary and declares no "
                                f"consistency; what spans two aggregates cannot hold in one "
                                f"transaction")
            elif front.get("consistency") == "immediate":
                problems.append(f"{identity}: immediate across an aggregate boundary is a "
                                f"boundary redrawn, not a rule (SPEC-003)")
        if front.get("type") == "state-machine":
            for field in ("subject", "status"):
                if isinstance(front.get(field), str):
                    landing(front[field], field, identity, field)
            problems += state_machine_problems(identity, node, nodes)
            if isinstance(front.get("subject"), str):
                machines.setdefault(front["subject"], []).append(identity)
    for subject, claimants in sorted(machines.items()):
        if len(claimants) > 1:
            problems.append(f"{' and '.join(claimants)} both govern {subject}; "
                            f"an aggregate root has one state machine")

    # --- scenarios and contracts
    for identity, node in sorted(nodes.items()):
        front = node["front"]
        if node["cls"] == "scenario":
            if isinstance(front.get("subject"), str):
                landing(front["subject"], "subject", identity, "subject")
            for index, touched in enumerate(front.get("involves") or []):
                if isinstance(touched, str):
                    landing(touched, "involved", identity, f"involves[{index}]")
        if node["cls"] == "contract":
            if node["context"] == SYSTEM and front.get("type") != "capability":
                problems.append(f"{identity}: the `{SYSTEM}` namespace holds capabilities "
                                f"only (SPEC-003)")
            if node["context"] != SYSTEM and front.get("type") == "capability":
                problems.append(f"{identity}: a capability is the system's promise and lives "
                                f"only under contracts/{SYSTEM}/ (SPEC-003)")
            for field in ("payload", "refusal"):
                if isinstance(front.get(field), str):
                    target = landing(front[field], field, identity, field)
                    if field == "refusal" and target is not None \
                            and target["front"].get("type") != "value-object":
                        problems.append(f"{identity}: refusal names {front[field]}, "
                                        f"a {target['front'].get('type')}; a refusal "
                                        f"surfaces a value object")
            if isinstance(front.get("upstream"), str):
                upstream = landing(front["upstream"], "upstream", identity, "upstream")
                if upstream is not None:
                    # A capability declares no `direction` field at all (contract.json's
                    # capability branch admits only `type` and `display`) because it is always
                    # published — SPEC-003 states this outright. Demanding the field here would
                    # make a third-party integration impossible to model as SKILL.md's own prose
                    # requires ("a third-party system is an upstream capability"), so its absence
                    # on a capability target counts as published, not as unset.
                    is_published = upstream["front"].get("type") == "capability" \
                        or upstream["front"].get("direction") == "published"
                    if not is_published:
                        problems.append(f"{identity}: upstream names {front['upstream']}, "
                                        f"whose direction is not published; the chain ends "
                                        f"at the context that owes compatibility")
                    if upstream["context"] == node["context"]:
                        problems.append(f"{identity}: upstream sits in the same context; "
                                        f"a context does not consume its own contract")
        if node["cls"] == "constraint":
            scope = front.get("scope")
            if isinstance(scope, str) and scope != SYSTEM and scope not in contexts:
                problems.append(f"{identity}: scope names `{scope}`, "
                                f"which domain/ does not declare")

    # --- reachability (SPEC-001 R6)
    for identity, node in sorted(elements.items()):
        kind = node["front"].get("type")
        if kind in ("aggregate-root", "domain-service"):
            continue  # a boundary and a named behavior justify themselves
        if identity not in referenced:
            problems.append(f"{identity}: nothing reaches this {kind} — no attribute, "
                            f"relationship, rule, contract or scenario names it; an element "
                            f"answering no comprehension question does not exist "
                            f"(SPEC-001 R6)")

    # --- the decision log
    log = nodes.get("decision-log")
    if log is None:
        problems.append("decision-log.md is missing; the log is mandatory and non-normative "
                        "(SPEC-003 R5)")
    else:
        for index, entry in enumerate(log["front"].get("entries") or []):
            if not isinstance(entry, dict) or not isinstance(entry.get("location"), str):
                continue  # the schema already reported the shape
            location = entry["location"]
            target = nodes.get("/".join(Path(location).with_suffix("").parts))
            if target is None or not (root / location).is_file():
                problems.append(f"decision-log: entries[{index}] locates {location}, "
                                f"which the specification does not hold (SPEC-001 R9)")
                continue
            field = entry.get("field")
            if isinstance(field, str):
                head = field.split(".")[0].split("[")[0]
                if head not in target["front"]:
                    problems.append(f"decision-log: entries[{index}] locates `{field}` in "
                                    f"{location}, which declares no `{head}` (SPEC-001 R9)")
    return problems


# ---------------------------------------------------------------- projections


def attribute_line(attribute: dict, nodes: dict[str, dict], context: str) -> str:
    declared = attribute["type"]
    if declared in PRIMITIVES:
        shown = declared
    else:
        target = nodes.get(resolve(declared, context))
        shown = pascal(target) if target else declared
    if attribute.get("many"):
        shown += "[]"
    return f"        +{shown} {camel(attribute['name'])}"


def class_diagram(context: str, nodes: dict[str, dict]) -> str:
    members = {i: n for i, n in nodes.items()
               if n["cls"] == "element" and n["context"] == context}

    def block(node: dict) -> list[str]:
        lines = [f"    class {pascal(node)} {{",
                 f"        <<{STEREOTYPES[node['front']['type']]}>>"]
        for attribute in node["front"].get("attributes") or []:
            lines.append(attribute_line(attribute, nodes, context))
        for value in node["front"].get("values") or []:
            lines.append(f"        {value.replace('-', '_').upper()}")
        for operation in node["front"].get("operations") or []:
            lines.append(f"        +{camel(operation)}()")
        lines.append("    }")
        return lines

    lines = ["classDiagram"]
    boundaries: dict[tuple, list[str]] = {}
    for identity in sorted(members):
        boundary = aggregate_of(members[identity])
        if boundary:
            boundaries.setdefault(boundary, []).append(identity)
    for boundary in sorted(boundaries):
        lines.append(f"    namespace {pascal(members[f'domain/{boundary[0]}/{boundary[1]}'])}"
                     f"Aggregate {{")
        for identity in boundaries[boundary]:
            lines += ["    " + line for line in block(members[identity])]
        lines.append("    }")
    for identity in sorted(members):
        if aggregate_of(members[identity]) is None:
            lines += block(members[identity])
    for identity in sorted(members):
        node = members[identity]
        for entry in node["front"].get("relationships") or []:
            target = nodes.get(resolve(entry["target"], context))
            if target is None:
                continue
            source_end = entry.get("source-cardinality") \
                or ("1" if entry["type"] == "composition" else "0..*")
            edge = (f"    {pascal(node)} \"{source_end}\" {ARROWS[entry['type']]} "
                    f"\"{entry['cardinality']}\" {pascal(target)}")
            if isinstance(entry.get("role"), str):
                edge += f" : {camel(entry['role'])}"
            lines.append(edge)
    return "\n".join(lines) + "\n"


def context_map(nodes: dict[str, dict]) -> str:
    contexts = sorted(n["context"] for n in nodes.values() if n["cls"] == "context")
    lines = ["flowchart LR"]
    for context in contexts:
        descriptor = nodes[f"domain/{context}/_context"]
        lines.append(f"    {context.replace('-', '_')}"
                     f"[\"{pascal(descriptor)} ({descriptor['front']['strategic']})\"]")
    edges = set()
    for identity, node in nodes.items():
        if node["cls"] == "contract" and isinstance(node["front"].get("upstream"), str):
            upstream = nodes.get(node["front"]["upstream"])
            if upstream is not None:
                edges.add((upstream["context"], node["context"], upstream["slug"]))
    for source, target, label in sorted(edges):
        lines.append(f"    {source.replace('-', '_')} -->|{label}| "
                     f"{target.replace('-', '_')}")
    connected = {(s, t) for s, t, _ in edges} | {(t, s) for s, t, _ in edges}
    for index, one in enumerate(contexts):
        for other in contexts[index + 1:]:
            if (one, other) not in connected:
                lines.append(f"    %% separate ways: {one} and {other} share no contract")
    return "\n".join(lines) + "\n"


def state_diagram(node: dict, nodes: dict[str, dict]) -> str:
    front = node["front"]
    lines = ["stateDiagram-v2", f"    [*] --> {front['initial']}"]
    for transition in front.get("transitions") or []:
        lines.append(f"    {transition['from']} --> {transition['to']} : "
                     f"{camel(transition['trigger'])}")
    for state in front.get("terminal") or []:
        lines.append(f"    {state} --> [*]")
    for rejection in front.get("rejections") or []:
        lines.append(f"    %% rejected: {camel(rejection['trigger'])} in {rejection['from']}")
    return "\n".join(lines) + "\n"


def capability_contexts(identity: str, nodes: dict[str, dict]) -> list[str]:
    touched = set()
    for node in nodes.values():
        if node["cls"] != "scenario" or node["front"].get("subject") != identity:
            continue
        for ref in [node["front"]["subject"]] + list(node["front"].get("involves") or []):
            context = ref.split("/")[1]
            if context != SYSTEM:
                touched.add(context)
    return sorted(touched)


def capability_map(nodes: dict[str, dict]) -> str:
    lines = ["flowchart TD"]
    for identity in sorted(nodes):
        node = nodes[identity]
        if node["cls"] != "contract" or node["front"].get("type") != "capability":
            continue
        anchor = node["slug"].replace("-", "_")
        lines.append(f"    {anchor}[\"{pascal(node)}\"]")
        for context in capability_contexts(identity, nodes):
            lines.append(f"    {anchor} --> {context.replace('-', '_')}")
    return "\n".join(lines) + "\n"


def overview(nodes: dict[str, dict]) -> str:
    lines = ["# Specification overview", "",
             "Derived by spec.py from the specification files; never edited.", "",
             "## Contexts", "",
             "| context | strategic | elements | rules | contracts | scenarios |",
             "|---|---|---|---|---|---|"]
    contexts = sorted(n["context"] for n in nodes.values() if n["cls"] == "context")
    for context in contexts:
        counts = {cls: sum(1 for n in nodes.values()
                           if n["cls"] == cls and n["context"] == context)
                  for cls in ("element", "rule", "contract", "scenario")}
        strategic = nodes[f"domain/{context}/_context"]["front"]["strategic"]
        lines.append(f"| {context} | {strategic} | {counts['element']} | {counts['rule']} "
                     f"| {counts['contract']} | {counts['scenario']} |")
    lines += ["", "## Capabilities", ""]
    capabilities = [i for i, n in sorted(nodes.items())
                    if n["cls"] == "contract" and n["front"].get("type") == "capability"]
    for identity in capabilities:
        touched = capability_contexts(identity, nodes)
        suffix = f" — orchestrates {', '.join(touched)}" if touched else ""
        lines.append(f"- {nodes[identity]['slug']}{suffix}")
    if not capabilities:
        lines.append("None.")
    lines += ["", "## Constraints", ""]
    constraints = [n for i, n in sorted(nodes.items()) if n["cls"] == "constraint"]
    for node in constraints:
        lines.append(f"- {node['slug']} ({node['front'].get('scope')})")
    if not constraints:
        lines.append("None.")
    decided = len(nodes.get("decision-log", {"front": {}})["front"].get("entries") or [])
    lines += ["", f"{decided} decision(s) disclosed in the decision log.", ""]
    return "\n".join(lines)


def project(nodes: dict[str, dict]) -> dict[str, str]:
    """Every projection the specification derives to, by filename."""
    files: dict[str, str] = {}
    for context in sorted(n["context"] for n in nodes.values() if n["cls"] == "context"):
        files[f"class-diagram-{context}.mmd"] = class_diagram(context, nodes)
    files["context-map.mmd"] = context_map(nodes)
    for identity in sorted(nodes):
        node = nodes[identity]
        if node["cls"] == "rule" and node["front"].get("type") == "state-machine":
            subject = node["front"]["subject"].split("/")[-1]
            files[f"state-{node['context']}-{subject}.mmd"] = state_diagram(node, nodes)
    files["capability-map.mmd"] = capability_map(nodes)
    files["overview.md"] = overview(nodes)
    return files


def main() -> int:
    args = sys.argv[1:]
    write = "--project" in args
    show_digests = "--digest" in args
    args = [a for a in args if a not in ("--project", "--digest")]
    single = None
    if "--node" in args:
        at = args.index("--node")
        if at + 1 >= len(args):
            print("cannot run: --node takes a file", file=sys.stderr)
            return CANNOT_RUN
        single = args[at + 1]
        del args[at:at + 2]
    if (write or show_digests) and single is not None:
        print("cannot run: --node validates one file, and --project/--digest are facts about "
              "the whole specification", file=sys.stderr)
        return CANNOT_RUN
    if write and show_digests:
        print("cannot run: --project and --digest are mutually exclusive", file=sys.stderr)
        return CANNOT_RUN
    if len(args) != 1 or args[0].startswith("--"):
        print("cannot run: expected [--project | --digest | --node <file>] <spec-root>",
              file=sys.stderr)
        return CANNOT_RUN
    root = Path(args[0])
    if not root.is_dir():
        print(f"cannot run: {root} is not a directory", file=sys.stderr)
        return CANNOT_RUN
    try:
        validators = contracts()
    except (FileNotFoundError, json.JSONDecodeError) as broken:
        print(f"cannot run: {broken}", file=sys.stderr)
        return CANNOT_RUN

    if single is not None:
        return check_single(root, single, validators)

    nodes, problems = collect(root, validators)
    problems += cross_problems(nodes, root)
    if problems:
        for problem in sorted(set(problems)):
            print(problem)
        refused = "projections are" if write else "digests are" if show_digests \
            else "the specification is"
        print(f"\n{len(set(problems))} problem(s) over {len(nodes)} file(s); "
              f"{refused} not sound while these stand.")
        return 1

    contexts = sorted({n["context"] for n in nodes.values() if n["cls"] == "context"})
    by_class = {cls: sum(1 for n in nodes.values() if n["cls"] == cls)
                for cls in ("element", "rule", "scenario", "contract", "constraint")}
    counted = ", ".join(f"{count} {cls}(s)" for cls, count in by_class.items() if count)
    decided = len(nodes.get("decision-log", {"front": {}})["front"].get("entries") or [])
    print(f"specification sound: {counted or 'no files'} across "
          f"{len(contexts)} context(s); {decided} decision(s) disclosed")

    if write:
        target = root / PROJECTIONS
        target.mkdir(exist_ok=True)
        derived = project(nodes)
        for stale in sorted(target.iterdir()):
            if stale.is_file() and stale.name not in derived:
                stale.unlink()
        for name, content in sorted(derived.items()):
            (target / name).write_text(content, encoding="utf-8")
        print(f"projected {len(derived)} file(s) into {target}: "
              f"{', '.join(sorted(derived))}")

    if show_digests:
        for identity in sorted(nodes):
            print(f"{identity}  {nodes[identity]['digest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
