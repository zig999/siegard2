#!/usr/bin/env python3
"""Validate a Siegard specification against the five-class metamodel, and derive its projections.

«Identity is the node's path from the specification root, without `.md`» (SPEC-003 R1). `domain/<context>/<slug>.md` is a Domain Model element
and `domain/<context>/_context.md` its context descriptor; `rules/`, `scenarios/` and
`contracts/` follow the same shape; `constraints/<slug>.md` is system-wide work; and
`decision-log.md` at the root is the one mandatory non-normative artifact. No file carries an
id, a name or a class field, so none can disagree with where it sits.

**The schema decides one file; this script decides what needs two.** Per-file validation is
`schemas/spec/*.json` applied as written. On top run the checks no per-file schema can express:
every reference resolves and lands on the class the field demands, an attribute never points at
an identity-bearing element and a relationship never points at a value — «No fact appears as both» (SPEC-002 R8), composition stays inside its aggregate — «composition never crosses an aggregate boundary»
(SPEC-002 R11), a crossing policy says how it converges — «immediate across an aggregate boundary
is a validation error» (SPEC-003 §Rule), a rule's or constraint's `statement` is one sentence —
«One condition is one sentence» (SPEC-003 §Rule), a state machine is total over its states and
triggers — «an undecided pairing is a decision to make and log, never silence» (SPEC-003 §Rule),
every entity, value object and enumeration is reachable — «an element nothing reaches is bloat and
fails validation» (SPEC-001 R6), and every decision-log entry locates a file and field that exist
— «An entry whose location does not resolve fails validation» (SPEC-001 R9).

**No provenance meta-fields.** A `gaps`, `sources`, `rationale` or `proposal` key is refused
with its own message — «Artifacts carry no provenance meta-fields» (SPEC-001 R8); «What the
material does not state, the analysis decides» (SPEC-001 R4), and the decision is disclosed in the
log, never marked in an artifact.

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

**An impact set is closed by reading, not by hand.** `--impact` prints, for each node named,
every reference it declares, every node that declares one at it, and every decision-log entry
that located it — one hop, in both directions. The edges are read off the same walk that
validates them, so the report and the check cannot drift apart. Two things it deliberately does
not do. It never closes a second hop: the transitive closure of a connected specification is the
specification, and a reader who wants another hop runs it again over what the first printed. And
it answers over a specification that still has problems, marking what does not resolve, because
an impact set is a reading rather than a derived artifact and the analysis that authors these
files needs one before the last file parses.

What it cannot answer is which nodes to name. That is the scope's vocabulary read against the
specification's, it is judgment, and a set closed perfectly around the wrong candidates is still
the wrong set.

**What the prose has become is measured, never refused.** `--shape` reports, per class, how long
a node and its `statement` run, how many statements carry more than one sentence, and which
`expression` outgrew the `statement` it restates — `statement` governs, so a restatement that
grew is one that added; then, per node, the reading closure — every node this one's prose names, transitively, and what that comes
to in words. It holds no threshold: a limit invented here would be arbitrary, while a node at the
far end of its own class's distribution is one a reader can open. It also names the longest phrase each
set of nodes shares in its normative fields — a clause two rules both carry is one definition
kept twice, which no reference resolves and no reachability reaches — every normative field
speaking about the specification rather than the domain, every long statement no scenario pins,
and how far each `why` of the decision log runs. Two readings are kept apart. A declared
reference passes through the same walk that validates it and is passed in rather than
recomputed; a node named in prose passes through no field and no check, so it is counted
separately, a bare slug two nodes answer to is reported ambiguous rather than resolved to
whichever sorts first, and a name that resolves to no node is listed rather than dropped — an operation, a table, a set invoked normatively with nowhere to be
is this report's finding, not its error bar. The obligations it measures against are stated where
obligations are stated: «`statement` (one falsifiable condition) is required» (SPEC-003 §Rule), and
«Prose explains what the node governs» (SPEC-001 R14). Both are judgment — «R3, R5, R7 and R14 are
the analysis's judgment» (SPEC-001 R11); this is the reading a reviewer judges from.

**`--of` names the nodes the reader is answerable for.** Three of the sections rank and cut,
because their whole point is the far end. Ranked over a populated root, that far end belongs to
whatever was written before, so a node written now sits below the cut and is never seen by the
one reader obliged to fix it. A node named here is marked `>` and its line is shown wherever it
appears, past any cut. The totals do not change: the distribution a node sits in is the whole
root's, never one invocation's slice of it, and a report that narrowed its counts to the slice
would say a node is unremarkable by comparing it only to its own siblings.

Declared dependencies: PyYAML, jsonschema.

Usage:  spec.py <spec-root>              validate everything
        spec.py --project <spec-root>    validate, then write projections/
        spec.py --digest <spec-root>     validate, then print every node's content digest
        spec.py --shape [--of <identity>[,<identity>...]] <spec-root>
                                          report how long the nodes run and how far their prose
                                          reaches; never refuses. `--of` marks the nodes the
                                          reader answers for and shows their lines past any cut
        spec.py --node <file> <spec-root>
                                          validate one file (cross-node checks do not run)
        spec.py --impact <identity>[,<identity>...] <spec-root>
                                          print one hop around each named node, both directions
        spec.py --contract [<class>]     print what one node class may and must declare, read
                                          from its own schema; with no class, list them
        spec.py --help                   print this text and stop
Exit:   0 sound
        1 problems
        2 cannot run
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from collections.abc import Callable
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
SENTENCE = re.compile(r"(?<=[.!?])\s+(?=[A-Z`])")
FENCE = re.compile(r"^---\n(.*?)\n---\n?", re.S)

SCHEMAS = {"context": "context.json", "element": "element.json", "rule": "rule.json",
           "scenario": "scenario.json", "contract": "contract.json",
           "constraint": "constraint.json", "log": "decision-log.json"}


def resolve_refs(node: object, schema: dict, seen: frozenset[str] = frozenset()) -> object:
    """Every `{"$ref": "#/$defs/X"}` this subtree carries, inlined in place. A slice printed for a
    reader has to stand on its own — a reader handed a slice and a dangling pointer into a file
    they were not given has the same problem printing the slice exists to remove. A name already
    on the path back to itself is left as the pointer instead of expanded again, since a cycle
    inlined without end is not a slice, it is the whole file with extra steps.

    Draft 2020-12 admits keywords beside a `$ref`, and a field written that way — a shared shape,
    with a description of what this particular use of it means — is how a contract says both
    without copying the shape into a second home. Inlined, the siblings win over what the target
    declares: they are the more specific statement, which is why they were written there.

    This is the one home of the rule. It sits here because the import graph reaches here from
    everywhere: `deliver.py` and `plan.py` both import this module, and each kept an identical
    copy until one of them was corrected and the other was not — which is what two copies of one
    rule eventually do."""
    if isinstance(node, dict):
        ref = node.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/$defs/"):
            name = ref[len("#/$defs/"):]
            target = schema.get("$defs", {}).get(name)
            if name in seen or target is None:
                return dict(node)
            inlined = resolve_refs(target, schema, seen | {name})
            beside = {key: resolve_refs(value, schema, seen)
                      for key, value in node.items() if key != "$ref"}
            if not beside:
                return inlined
            return {**inlined, **beside} if isinstance(inlined, dict) else dict(node)
        return {key: resolve_refs(value, schema, seen) for key, value in node.items()}
    if isinstance(node, list):
        return [resolve_refs(item, schema, seen) for item in node]
    return node


def contract_branch(schema: dict, branch: str) -> dict | None:
    """One self-contained slice of a contract: a `$defs` entry, or every property one `kind` value
    admits, both with `$ref` resolved. `None` where `branch` names neither — the caller decides
    what a refusal over that looks like, since its callers refuse differently."""
    defs = schema.get("$defs", {})
    if branch in defs:
        return resolve_refs(defs[branch], schema)
    for clause in schema.get("allOf", []):
        const = clause.get("if", {}).get("properties", {}).get("kind", {}).get("const")
        if const != branch:
            continue
        then = clause.get("then", {})
        names = then.get("propertyNames", {}).get("enum", [])
        sliced: dict = {
            "kind": branch,
            "required": then.get("required", []),
            "properties": {name: schema["properties"][name] for name in names
                           if name in schema.get("properties", {})},
        }
        if "examples" in then:
            sliced["examples"] = then["examples"]
        return resolve_refs(sliced, schema)
    return None


def contract_branches(schema: dict) -> list[str]:
    """Every branch name a slice answers for in this schema, sorted — what a refusal over an
    unknown branch offers instead of leaving the caller to guess."""
    kinds = [clause["if"]["properties"]["kind"]["const"] for clause in schema.get("allOf", [])
             if "const" in clause.get("if", {}).get("properties", {}).get("kind", {})]
    return sorted(set(schema.get("$defs", {})) | set(kinds))


def whole_contract(schema: dict) -> dict:
    """A schema printed as its own slice: everything but `$defs`, which is inlined where it is
    used. A node class is one file rather than a branch of one, so what answers "what does a Rule
    carry" is the file, resolved."""
    return {key: resolve_refs(value, schema)
            for key, value in schema.items() if key != "$defs"}
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
        return ("context", parts[1], parts[1]) if SLUG.fullmatch(parts[1]) else None
    if len(parts) == 3 and parts[0] in ("domain", "rules", "scenarios", "contracts"):
        cls = {"domain": "element", "rules": "rule",
               "scenarios": "scenario", "contracts": "contract"}[parts[0]]
        if SLUG.fullmatch(parts[1]) and SLUG.fullmatch(parts[2]):
            return (cls, parts[1], parts[2])
        return None
    if len(parts) == 2 and parts[0] == "constraints" and SLUG.fullmatch(parts[1]):
        return ("constraint", None, parts[1])
    return None


def digest_of(path: Path) -> str:
    """Content identity: sha256 of the file's exact bytes, computable by hand as `sha256sum`."""
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def listed(front: dict, field: str) -> list:
    """A list field read defensively: anything but a list reads as empty, because the schema
    already reported the shape and iterating a string would report its characters."""
    value = front.get(field)
    return value if isinstance(value, list) else []


def read_node(path: Path) -> tuple[str | None, str | None]:
    """A node file's text, or the problem that says why it could not be read — never a traceback.
    Exactly one of the two is set.

    A file that is not UTF-8 is a problem naming the file, not a `UnicodeDecodeError` that names
    the byte offset and nothing else. A byte-order mark is consumed rather than refused: it is
    invisible to whoever wrote the file, and leaving it in makes the fence miss, which reports a
    file whose fence is visibly there as carrying none. Digests are unaffected — `digest_of`
    hashes the bytes on disk and is what `sha256sum` computes by hand."""
    try:
        return path.read_text(encoding="utf-8-sig"), None
    except UnicodeDecodeError as broken:
        return None, f"is not UTF-8: {broken}"
    except OSError as broken:
        return None, f"cannot be read: {broken}"


def parse_node(path: Path) -> tuple[dict | None, str, str | None]:
    """One node file split into its frontmatter and its body, or the problem that says why it
    could not be. Exactly one of the mapping and the problem is set.

    The three steps are the same wherever a node file is opened — read the bytes, match the
    fence, parse the YAML — and every caller differs only in what it does with the answer. Held
    together here so a guard added at one of those steps reaches all of them; they drifted once
    already, and the drift was a traceback in one script and a clean refusal in its sibling."""
    text, unreadable = read_node(path)
    if text is None:
        return None, "", unreadable
    match = FENCE.match(text)
    if not match:
        return None, "", "carries no frontmatter fence"
    try:
        front = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as broken:
        said = f"frontmatter does not parse: {broken}"
        # PyYAML's own message for the commonest authoring error — a colon inside an unquoted
        # scalar — names the grammar and not the fix, and working the fix out from the grammar
        # is paid once per occurrence. The match is on the library's
        # wording; a version that rewords it loses the hint and nothing else.
        if "mapping values are not allowed" in str(broken):
            said += (" — usually a colon inside an unquoted scalar; quote the whole string, or "
                     "compose the frontmatter with yaml.safe_dump instead of typing it by hand")
        return None, "", said
    return front, text[match.end():], None


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


def headings_of(body: str) -> list[str]:
    """The `## ` headings a body carries, ignoring anything inside a fenced code block. A note
    quoting markdown — a README's own `## Install`, a snippet from a task's criteria — was counted
    as a heading of the node itself, and the file was refused for a structure it does not have."""
    headings, fenced = [], False
    for line in body.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if not fenced and line.startswith("## "):
            headings.append(line.rstrip())
    return headings


def body_problems(cls: str, body: str) -> list[str]:
    expected = HEADINGS[cls]
    if expected is None:
        return []
    headings = headings_of(body)
    if headings != expected:
        return [f"body headings are {headings if headings else 'absent'}; "
                f"this class carries exactly {expected}"]
    return []


def statement_problems(cls: str, front: object) -> list[str]:
    """«One condition is one sentence» (SPEC-003 §Rule) — the half of that rule a sentence
    count decides. Whether one sentence carries one condition stays judgment, and `--shape`
    naming the far end of the class is where a reviewer reads it; this refuses only what no
    reading can defend, a statement that stopped and started again. No escape hatch: a second
    sentence is a definition — «as the name of the element it means» (SPEC-001 R3) — an example (a scenario's), or a second
    condition (a second rule's), and each of those already has a home."""
    if cls not in ("rule", "constraint") or not isinstance(front, dict):
        return []
    statement = front.get("statement")
    if not isinstance(statement, str):
        return []
    count = len([s for s in SENTENCE.split(statement) if s.strip()])
    if count <= 1:
        return []
    return [f"statement carries {count} sentences; a second sentence is a second rule, a scenario, "
            f"or an element's definition — «One condition is one sentence» (SPEC-003 §Rule)"]


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
                            f"«every node of every class, flat per context, kebab-case slugs, no type in "
                            f"filenames» (SPEC-003 R4)")
            continue
        cls, context, slug = placed
        identity = "/".join(relative.with_suffix("").parts)
        front, body, unreadable = parse_node(path)
        if front is None:
            problems.append(f"{identity}: {unreadable}")
            continue
        if not isinstance(front, dict) or any(not isinstance(k, str) for k in front):
            problems.append(f"{identity}: frontmatter is not a mapping of string keys")
            continue
        for field in META_FIELDS:
            if field in front:
                problems.append(
                    f"{identity}: carries `{field}`, a provenance meta-field — «Artifacts carry no "
                    f"provenance meta-fields» (SPEC-001 R8); «What the material does not state, "
                    f"the analysis decides» (SPEC-001 R4), and the decision is disclosed in the "
                    f"decision log, never marked in an artifact")
        front = {k: v for k, v in front.items() if k not in META_FIELDS}
        for error in validators[cls].iter_errors(front):
            where = ".".join(str(part) for part in error.absolute_path) or "frontmatter"
            problems.append(f"{identity}: {where}: {error.message}")
        problems += [f"{identity}: {p}" for p in body_problems(cls, body)]
        problems += [f"{identity}: {p}" for p in statement_problems(cls, front)]
        display = front.get("display")
        if isinstance(display, str) and reduce_display(display) != slug:
            problems.append(f"{identity}: display `{display}` reduces to "
                            f"`{reduce_display(display)}`, not to the slug `{slug}`")
        nodes[identity] = {"cls": cls, "context": context, "slug": slug, "front": front,
                           "digest": digest_of(path), "path": path}
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
              f"«every node of every class, flat per context, kebab-case slugs, no type in "
                            f"filenames» (SPEC-003 R4)")
        return 1
    cls, _, slug = placed
    identity = "/".join(relative.with_suffix("").parts)
    if not path.is_file():
        print(f"cannot run: {path} does not exist", file=sys.stderr)
        return CANNOT_RUN
    front, body, unreadable = parse_node(path)
    if front is None:
        print(f"{identity}: {unreadable}")
        return 1
    if not isinstance(front, dict) or any(not isinstance(k, str) for k in front):
        print(f"{identity}: frontmatter is not a mapping of string keys")
        return 1

    problems: list[str] = []
    for field in META_FIELDS:
        if field in front:
            problems.append(
                f"carries `{field}`, a provenance meta-field — «Artifacts carry no provenance "
                f"meta-fields» (SPEC-001 R8); «What the material does not state, the analysis "
                f"decides» (SPEC-001 R4), and the decision is disclosed in the decision log, never "
                f"marked in an artifact")
    checked = {k: v for k, v in front.items() if k not in META_FIELDS}
    for error in validators[cls].iter_errors(checked):
        where = ".".join(str(part) for part in error.absolute_path) or "frontmatter"
        problems.append(f"{where}: {error.message}")
    problems += body_problems(cls, body)
    problems += statement_problems(cls, front)
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
    """«A reference is a bare slug inside the same directory and the full identity everywhere
    else» (SPEC-003 R2); a bare slug in an element's field resolves inside its own context's
    domain directory."""
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
    for attribute in listed(front, "attributes"):
        if not isinstance(attribute, dict):
            continue
        declared = attribute.get("type")
        if isinstance(declared, str) and declared not in PRIMITIVES:
            refs.append((resolve(declared, context), "value",
                         f"attributes[{attribute.get('name', '?')}].type"))
    for index, entry in enumerate(listed(front, "relationships")):
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
        states = [v for v in listed(status["front"], "values") if isinstance(v, str)]
    subject = nodes.get(front.get("subject", ""))
    if subject is None or subject["cls"] != "element" \
            or subject["front"].get("type") != "aggregate-root":
        problems.append(f"{identity}: subject must name an aggregate root")

    declared = set(states)
    terminal = {s for s in listed(front, "terminal") if isinstance(s, str)}
    transitions = [t for t in listed(front, "transitions") if isinstance(t, dict)]
    rejections = [r for r in listed(front, "rejections") if isinstance(r, dict)]

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

    # A terminal state "accepts no further trigger" — its own contract's words, and the whole of
    # what exempts it from the totality check below. A transition leaving one contradicts the
    # declaration that exempted it, and the projected diagram drew both `S --> [*]` and `S --> T`.
    for index, transition in enumerate(transitions):
        if transition.get("from") in terminal:
            problems.append(f"{identity}: transitions[{index}].from names `"
                            f"{transition.get('from')}`, which `terminal` declares accepts no "
                            f"further trigger; a state is terminal or it transitions, never both")
    for index, rejection in enumerate(rejections):
        if rejection.get("from") in terminal:
            problems.append(f"{identity}: rejections[{index}].from names `"
                            f"{rejection.get('from')}`, which `terminal` declares accepts no "
                            f"further trigger; a terminal state decides no pairing")

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


def cross_problems(nodes: dict[str, dict], root: Path,
                   record: Callable[[str, str, str, bool], None] | None = None) -> list[str]:
    """The rules that need to see more than one file at once.

    `record` is how `--impact` reads the edges without owning a second list of which fields carry
    a reference. Every declared reference in this specification passes through `landing` below on
    its way to being checked, so a field that gains a reference is one both the check and the
    report see, or neither — there is no third place to keep them agreeing.
    """
    problems: list[str] = []
    elements = {i: n for i, n in nodes.items() if n["cls"] == "element"}
    contexts = sorted({n["context"] for n in nodes.values()
                       if n["cls"] in ("element", "context")})
    referenced: set[str] = set()

    def landing(identity: str, expectation: str, owner: str, at: str) -> dict | None:
        target = nodes.get(identity)
        if record is not None:
            record(owner, at, identity, target is not None)
        if target is None:
            problems.append(f"{owner}: {at} names {identity}, "
                            f"which the specification does not hold")
            return None
        referenced.add(identity)
        return target

    # --- namespaces and the floor
    for reserved in (f"domain/{SYSTEM}", f"rules/{SYSTEM}"):
        if any(i.startswith(reserved + "/") for i in nodes):
            problems.append(f"{reserved}: `{SYSTEM}` is a reserved namespace — "
                            f"«no bounded context may take that slug» (SPEC-003 R3)")
    if SYSTEM in contexts:
        contexts.remove(SYSTEM)
    for context in contexts:
        if f"domain/{context}/_context" not in nodes:
            problems.append(f"domain/{context}: carries no _context.md; every context "
                            f"declares its descriptor")
        if not any(n["context"] == context for n in elements.values()):
            problems.append(f"domain/{context}: holds no element — «a linguistic boundary "
                            f"with no language is not comprehensible» (SPEC-001 R2)")
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
                problems.append(f"{identity}: {at} names {target_id}, a {kind}; «A link to an "
                                      f"entity or an aggregate root is a relationship» (SPEC-002 R8), "
                                      f"never an attribute")
            if expectation == "identity-bearing" \
                    and kind not in ("entity", "aggregate-root"):
                problems.append(f"{identity}: {at} names {target_id}, a {kind}; «A link to a "
                                      f"primitive, a value object, or an enumeration is an attribute» "
                                      f"(SPEC-002 R8), never a relationship")
            if expectation == "root" and kind != "aggregate-root":
                problems.append(f"{identity}: {at} names {target_id}, a {kind}; an entity "
                                f"belongs to an aggregate root")
        by_target: dict[str, list[dict]] = {}
        for index, entry in enumerate(listed(front, "relationships")):
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
                                    f"a {kind} — «composition holds entities inside one "
                                          f"aggregate» (SPEC-002 R11)")
                elif aggregate_of(target) != aggregate_of(node):
                    problems.append(f"{identity}: relationships[{index}] composes {target_id}, "
                                    f"which sits in aggregate {aggregate_of(target)}; "
                                    f"«composition never crosses an aggregate boundary» "
                                          f"(SPEC-002 R11)")
            if entry.get("type") == "reference" and kind != "aggregate-root":
                problems.append(f"{identity}: relationships[{index}] references {target_id}, "
                                f"a {kind} — «reference is how an element points at another "
                                          f"aggregate's root, always by identity» (SPEC-002 R11)")
        for target_id, entries in sorted(by_target.items()):
            if len(entries) > 1 and any(not isinstance(e.get("role"), str) for e in entries):
                problems.append(f"{identity}: {len(entries)} relationships share the target "
                                f"{target_id} and not all carry `role` — «Two unlabeled edges to "
                                    f"one target are indistinguishable» (SPEC-002 R10)")

    # --- rules
    machines: dict[str, list[str]] = {}
    for identity, node in sorted(nodes.items()):
        if node["cls"] != "rule":
            continue
        front = node["front"]
        boundaries: set[tuple[str, str]] = set()
        spanned: set[str] = set()
        for index, target_id in enumerate(listed(front, "constrains")):
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
                problems.append(f"{identity}: «immediate across an aggregate boundary is a "
                                    f"validation error — that demand is a boundary redrawn, not a rule» "
                                    f"(SPEC-003 §Rule)")
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
            for index, touched in enumerate(listed(front, "involves")):
                if isinstance(touched, str):
                    landing(touched, "involved", identity, f"involves[{index}]")
        if node["cls"] == "contract":
            if node["context"] == SYSTEM and front.get("type") != "capability":
                problems.append(f"{identity}: the `{SYSTEM}` namespace holds capabilities "
                                    f"only — a capability «lives only in the reserved system namespace» "
                                    f"(SPEC-003 §Contract)")
            if node["context"] != SYSTEM and front.get("type") == "capability":
                problems.append(f"{identity}: a capability is «the system's promise to its users» "
                                    f"(SPEC-003 §Contract), and lives only under contracts/{SYSTEM}/")
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
                    # published — «A capability is always published» (SPEC-003 §Contract). Demanding the field here would
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

    # --- reachability — «an element nothing reaches is bloat and fails validation» (SPEC-001 R6)
    for identity, node in sorted(elements.items()):
        kind = node["front"].get("type")
        if kind in ("aggregate-root", "domain-service"):
            continue  # a boundary and a named behavior justify themselves
        if identity not in referenced:
            problems.append(f"{identity}: nothing reaches this {kind} — no attribute, "
                            f"relationship, rule, contract or scenario names it; «an element "
                            f"nothing reaches is bloat and fails validation» (SPEC-001 R6)")

    # --- the decision log
    log = nodes.get("decision-log")
    if log is None:
        problems.append("decision-log.md is missing — the log «is mandatory and non-normative: it "
                        "constrains nothing; it discloses» (SPEC-003 R5)")
    else:
        for index, entry in enumerate(listed(log["front"], "entries")):
            if not isinstance(entry, dict) or not isinstance(entry.get("location"), str):
                continue  # the schema already reported the shape
            location = entry["location"]
            located = "/".join(Path(location).with_suffix("").parts)
            target = nodes.get(located)
            if record is not None:
                record("decision-log", f"entries[{index}]", located,
                       target is not None and (root / location).is_file())
            if target is None or not (root / location).is_file():
                problems.append(f"decision-log: entries[{index}] locates {location}, "
                        f"which the specification does not hold — «An entry whose location does "
                        f"not resolve fails validation» (SPEC-001 R9)")
                continue
            field = entry.get("field")
            if isinstance(field, str):
                head = field.split(".")[0].split("[")[0]
                if head not in target["front"]:
                    problems.append(f"decision-log: entries[{index}] locates `{field}` in "
                                    f"{location}, which declares no `{head}` — «An entry whose location does not "
                        f"resolve fails validation» (SPEC-001 R9)")
    return problems


def impact_of(nodes: dict[str, dict], root: Path,
              named: list[str]) -> tuple[dict[str, list], dict[str, list], list[str]]:
    """One hop around each named node, in both directions, read off the same walk that validates.

    The edges come from `cross_problems`'s own `landing`, so what this reports and what the
    validator checks cannot drift apart: a field that gains a reference is seen by both, and a
    field neither walks is a reference this specification does not declare.

    **One hop, and no flag for more.** An impact set exists to say what governs a scope, and the
    transitive closure of a connected specification is the specification — a reader who needs a
    second hop runs this again over what the first one printed, deciding each time, rather than
    receiving a graph nobody chose to read.
    """
    outward: dict[str, list] = {}
    inward: dict[str, list] = {}

    def record(owner: str, at: str, target: str, resolved: bool) -> None:
        outward.setdefault(owner, []).append((at, target, resolved))
        inward.setdefault(target, []).append((owner, at, resolved))

    cross_problems(nodes, root, record)
    reached = sorted({identity for identity in named}
                     | {target for identity in named
                        for _, target, resolved in outward.get(identity, []) if resolved}
                     | {owner for identity in named
                        for owner, _, resolved in inward.get(identity, []) if resolved})
    return outward, inward, reached


def print_impact(nodes: dict[str, dict], root: Path, named: list[str],
                 problems: list[str]) -> int:
    """`--impact`'s own body: the closure around the named nodes, printed to be quoted verbatim.

    This is a reading, never a derived artifact, which is why it answers over a specification that
    does not yet hold together — `/analyse` closes an impact set while it is still authoring the
    files, and a closure refused until the last file parses is a closure that arrives after the
    decisions it was for. What did not resolve is marked rather than dropped, and the problems are
    named at the end so nobody quotes this as a clean run.

    What it does not answer is which nodes to name in the first place. That is the scope's
    vocabulary against the specification's, it is judgment, and no closure can supply it — a set
    closed perfectly around the wrong candidates is still the wrong set.
    """
    missing = [identity for identity in named if not (root / f"{identity}.md").is_file()]
    if missing:
        print(f"cannot run: {', '.join(missing)} names no file under {root}; "
              f"an identity is a node's path without `.md`", file=sys.stderr)
        return CANNOT_RUN

    outward, inward, reached = impact_of(nodes, root, named)
    unheld = " — the specification does not hold this"
    print(f"impact set: {len(reached)} node(s) from {len(named)} named, one hop, both directions.")
    if problems:
        print(f"read over a specification with {len(set(problems))} problem(s): what did not "
              f"resolve is marked, and the problems are listed below.")
    for identity in named:
        print(f"\n{identity}")
        lines = [f"  declares  -> {target:<48} {at}{'' if resolved else unheld}"
                 for at, target, resolved in sorted(outward.get(identity, []))]
        lines += [f"  named by  <- {owner:<48} {at}{'' if resolved else unheld}"
                  for owner, at, resolved in sorted(inward.get(identity, []))]
        if identity not in nodes:
            lines.append("  (this file did not parse; its own references are unread)")
        print("\n".join(lines) or "  (declares nothing, and nothing declares it)")
    print("\nread:")
    for identity in reached:
        print(f"  {root / f'{identity}.md'}")
    if problems:
        print()
        for problem in sorted(set(problems)):
            print(problem)
    return 0



# ---------------------------------------------------------------- shape


PROSE_PATH = re.compile(r"\b(?:domain|rules|scenarios|contracts|constraints)"
                        r"/[a-z0-9-]+(?:/[a-z0-9-]+)?\b")
PROSE_SLUG = re.compile(r"`([a-z0-9]+(?:-[a-z0-9]+)+)`")


def percentile(values: list[int], fraction: float) -> int:
    """The value at `fraction` of a sorted sample, by nearest rank — no interpolation, so the
    number printed is one a node actually has and a reader can go find.

    Naming which node has it is the rest of that sentence, and the table below does: a
    distribution nobody can open is the measurement this whole reading exists to replace."""
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(len(ordered) * fraction))]


def prose_mentions(identity: str, body: str,
                   nodes: dict[str, dict]) -> tuple[set[str], set[str], set[str]]:
    """(node identities this prose names, names resolving to no node, names resolving to two).

    A declared reference passes through `landing` on its way to being checked; this is the other
    reading — a node named in prose, which no field carries and no check sees. The two are
    counted apart in the report because they are different readings, and this one resolves a bare
    slug against every node's slug rather than against the citing node's own directory: what it
    models is what an agent reading this prose will open, and an agent finds the node the name
    denotes wherever it sits. Where a *declared* reference may be bare is «A reference is a bare slug
    inside the same directory and the full identity everywhere else» (SPEC-003 R2);
    nothing here checks it.

    What does not resolve is named by the report rather than dropped from it. A name a
    specification uses in prose and holds in no node is the finding, not the error bar: an
    operation, a table, a set invoked normatively with nowhere to be.

    **A bare slug is read only where it carries a hyphen.** A single-word slug in backticks is
    indistinguishable from any other word a writer sets in code style — a field name, a value, a
    literal — so reading one would put nodes in this closure that no prose named. The cost is
    stated rather than hidden: a node whose slug is one word is not counted here, so what this
    reports of prose is a floor on it and never a total.

    **A bare slug two nodes answer to is reported ambiguous, never resolved to one of them.**
    A slug is unique inside a directory and not across the specification — `capability-registry`
    can be the element and the api that publishes over it, two classes answering two questions —
    so picking whichever sorts first would put a node in this reader's closure that its prose may
    never have meant, and be wrong silently. This is `terms.py`'s own rule over the framework's
    vocabulary: one word with two senses is two entries named apart, never one entry with a
    definition on top of it.
    """
    by_slug: dict[str, set[str]] = {}
    for held in nodes:
        by_slug.setdefault(held.rsplit("/", 1)[-1], set()).add(held)
    named: set[str] = set()
    unheld: set[str] = set()
    ambiguous: set[str] = set()
    for match in PROSE_PATH.finditer(body):
        written = match.group(0)
        # A context is named by its directory; its descriptor is the node that holds it, and
        # the underscore keeping that file outside the slug space is not something prose writes.
        held = written if written in nodes else f"{written}/_context"
        (named if held in nodes else unheld).add(held if held in nodes else written)
    for match in PROSE_SLUG.finditer(body):
        word = match.group(1)
        if word in nodes:
            named.add(word)
        elif word not in by_slug:
            unheld.add(word)
        elif len(by_slug[word]) > 1:
            ambiguous.add(word)
        else:
            named.add(next(iter(by_slug[word])))
    named.discard(identity)
    return named, unheld, ambiguous


NORMATIVE = ("statement", "expression")
PHRASE = 8
ROWS_SHOWN = 12
DISTRIBUTION = 10
WORD = re.compile(r"[a-z']+")


def shared_phrases(nodes: dict[str, dict]) -> list[tuple[frozenset[str], str]]:
    """The longest phrase each set of nodes shares in its normative fields, longest first.

    R3 and R7 leave restatement to judgment and nothing looks for it. This looks: an index of
    every eight-word phrase to the nodes holding it, then, per set of holders, the longest phrase
    that set shares. Collapsing to the holder set is what makes the answer readable — the same
    duplicated clause otherwise arrives as every sub-phrase of itself.

    Two properties earn its place. It fires on nothing over a sound specification, so a listing
    is a finding rather than a floor. And what it finds is what no other check can: a clause two
    rules both carry is one definition kept in two places, which no reference resolves and no
    reachability reaches, because neither node declares anything about the other.

    Ranked by words times holders, because both matter and neither alone: a long clause in two
    nodes is a duplicated obligation, and a short one in nineteen is a table that has no node.
    """
    words = {identity: WORD.findall(" ".join(
        node["front"][field] for field in NORMATIVE
        if isinstance(node["front"].get(field), str)).lower())
        for identity, node in nodes.items()}
    index: dict[str, set[str]] = {}
    for identity, held in words.items():
        for at in range(max(0, len(held) - PHRASE + 1)):
            index.setdefault(" ".join(held[at:at + PHRASE]), set()).add(identity)
    longest: dict[frozenset[str], str] = {}
    for phrase, holders in index.items():
        if len(holders) < 2:
            continue
        key = frozenset(holders)
        if key not in longest or len(phrase) > len(longest[key]):
            longest[key] = phrase
    return sorted(longest.items(),
                  key=lambda pair: (-(len(pair[1].split()) * len(pair[0])), pair[1]))


SELF_REFERENCE = re.compile(
    r"\b(that statement|this statement|this specification'?s?|this node|no node stated"
    r"|stated here)\b", re.I)


def shape_of(nodes: dict[str, dict], declared: dict[str, set[str]] | None = None) -> dict:
    """Every measurement `--shape` reports, read off the files in one pass.

    `declared` is what the validating walk saw: `cross_problems`'s own `record`, keyed by owner.
    It is passed in rather than recomputed so the two never disagree about which fields carry a
    reference — the discipline that walk's own docstring states. The prose side beside it is a
    text scan and a heuristic; the report keeps them apart and says which is which.

    Sizes, the sentence count of each `statement`, what each node's prose names, and the
    transitive closure of that naming. No threshold is applied and none is held here: a word
    count that refused would be a limit invented in this file, while a node at the far end of
    its own class's distribution is a node a reader can go look at. The obligation this measures
    is stated where obligations are stated — «`statement` (one falsifiable condition) is
    required» (SPEC-003 §Rule), and «Prose explains what the node governs» (SPEC-001 R14).
    """
    read: dict[str, dict] = {}
    for identity, node in nodes.items():
        front, body, _ = parse_node(node["path"])
        text = node["path"].read_text(encoding="utf-8")
        statement = front.get("statement") if isinstance(front, dict) else None
        statement = statement if isinstance(statement, str) else None
        selfref = sorted({m.group(0).lower() for m in SELF_REFERENCE.finditer(
            " ".join(front.get(f) for f in NORMATIVE
                     if isinstance(front, dict) and isinstance(front.get(f), str)))})
        expression = front.get("expression") if isinstance(front, dict) else None
        expression = expression if isinstance(expression, str) else None
        named, unheld, ambiguous = prose_mentions(identity, body or "", nodes)
        read[identity] = {
            "cls": node["cls"],
            "words": len(text.split()),
            "body_words": len((body or "").split()),
            "statement_words": len(statement.split()) if statement else None,
            "expression_words": len(expression.split()) if expression else None,
            "sentences": len([s for s in SENTENCE.split(statement) if s.strip()])
                         if statement else None,
            "names": named,
            "unheld": unheld,
            "ambiguous": ambiguous,
            "selfref": selfref,
            "declared": len((declared or {}).get(identity, ())),
        }
        if node["cls"] == "log":
            entries = [e for e in listed(front or {}, "entries") if isinstance(e, dict)]
            read[identity]["why_words"] = sorted(
                len(e["why"].split()) for e in entries if isinstance(e.get("why"), str))
    anchored: dict[str, int] = {}
    for node in nodes.values():
        subject = node["front"].get("subject")
        if node["cls"] == "scenario" and isinstance(subject, str):
            anchored[subject] = anchored.get(subject, 0) + 1
    for identity, entry in read.items():
        entry["scenarios"] = anchored.get(identity, 0)
    for entry in read.values():
        seen: set[str] = set()
        frontier = sorted(entry["names"])
        while frontier:
            reached = frontier.pop()
            if reached in seen or reached not in read:
                continue
            seen.add(reached)
            frontier += sorted(read[reached]["names"] - seen)
        entry["closure"] = seen
        entry["closure_words"] = sum(read[held]["words"] for held in seen)
    return read


def print_shape(nodes: dict[str, dict], root: Path, problems: list[str],
                declared: dict[str, set[str]] | None = None,
                scope: list[str] | None = None) -> int:
    """`--shape`'s own body: what this specification's prose has become, never a refusal.

    This reports and returns 0 whatever it finds. A specification drifts one node at a time, and
    every node is defensible on its own; what is not defensible is a distribution nobody
    measured. So the numbers are stated per class, with the far end of each named so a reader can
    open it, and the judgment stays with the reader — «R3, R5, R7 and R14 are the analysis's
    judgment» (SPEC-001 R11).

    It answers over a specification that still has problems, for the reason `--impact` does: the
    analysis that authors these files needs the reading while it is authoring them.

    **`scope` is which nodes the reader is answerable for, and it changes what is shown, never
    what is counted.** Three sections rank and cut, because their whole point is the far end;
    ranked over a populated root, the far end belongs to whatever was written before, and a node
    written now lands below the cut and is never seen by the only reader obliged to fix it. So a
    scoped node's line is shown wherever it appears regardless of rank, and marked. The totals
    stay the specification's, because the distribution a node sits in is the distribution of the
    whole root and not of one invocation's slice of it.
    """
    read = shape_of(nodes, declared)
    if not read:
        print(f"shape: {root} holds no node to measure.")
        return 0
    named = set(scope or ())

    def mark(identity: str) -> str:
        return ">" if identity in named else " "

    def cut(rows: list, key) -> list:
        """The top of the ranking, plus every scoped row wherever it sits."""
        held = rows[:ROWS_SHOWN]
        return held + [row for row in rows[ROWS_SHOWN:] if named & set(key(row))]

    print(f"shape: {len(read)} node(s) over "
          f"{len({e['cls'] for e in read.values()})} class(es), read from {root}.")
    if named:
        print(f"answering for {len(named)} node(s), marked `>`: their line is shown wherever it "
              f"appears, past any cut, because a ranking over the whole root puts what was "
              f"written now below what was written before.")
    if problems:
        print(f"read over a specification with {len(set(problems))} problem(s); "
              f"a node that did not parse is not measured.")
    print(f"\n{'class':<12}{'n':>5}{'words':>9}{'p90':>7}{'max':>7}"
          f"{'stmt':>7}{'p90':>7}{'max':>7}{'>1 sentence':>13}")
    for cls in sorted({entry["cls"] for entry in read.values()}):
        held = [entry for entry in read.values() if entry["cls"] == cls]
        words = [entry["words"] for entry in held]
        stated = [entry["statement_words"] for entry in held
                  if entry["statement_words"] is not None]
        multi = sum(1 for entry in held if (entry["sentences"] or 0) > 1)
        columns = (f"{percentile(stated, 0.5):>7}{percentile(stated, 0.9):>7}"
                   f"{max(stated):>7}{multi:>13}") if stated else f"{'-':>7}{'-':>7}{'-':>7}{'-':>13}"
        print(f"{cls:<12}{len(held):>5}{percentile(words, 0.5):>9}"
              f"{percentile(words, 0.9):>7}{max(words):>7}{columns}")
        if len(held) < DISTRIBUTION:
            continue  # below this a class is its own list, and every node is already in view
        far = percentile(words, 0.9)
        for identity in sorted(identity for identity, entry in read.items()
                               if entry["cls"] == cls and entry["words"] >= far):
            print(f"{mark(identity)}   at or past p90: {read[identity]['words']:>5}w  {identity}")

    multi = sorted(identity for identity, entry in read.items()
                   if (entry["sentences"] or 0) > 1)
    print(f"\nstatement carrying more than one sentence — {len(multi)}; "
          f"«One condition is one sentence» (SPEC-003 §Rule):")
    for identity in multi:
        print(f"{mark(identity)} {read[identity]['sentences']} sentences  "
              f"{read[identity]['statement_words']:>4}w  {identity}")
    if not multi:
        print("  (none)")

    outgrew = sorted((identity for identity, entry in read.items()
                      if entry["expression_words"] is not None
                      and entry["statement_words"] is not None
                      and entry["expression_words"] > entry["statement_words"]))
    print(f"\nexpression longer than the statement it restates — {len(outgrew)}; `statement` "
          f"governs and `expression` «adds no obligation of its own» (SPEC-003 §Rule), so a "
          f"restatement that grew is one that added:")
    for identity in outgrew:
        print(f"{mark(identity)} {read[identity]['statement_words']:>4}w -> "
              f"{read[identity]['expression_words']:>4}w  {identity}")
    if not outgrew:
        print("  (none)")

    for cls in sorted({e["cls"] for e in read.values()}):
        stated = [e["statement_words"] for e in read.values()
                  if e["cls"] == cls and e["statement_words"] is not None]
        if not stated:
            continue
        far = percentile(stated, 0.9)
        long_unpinned = sorted(identity for identity, entry in read.items()
                               if entry["cls"] == cls and entry["scenarios"] == 0
                               and (entry["statement_words"] or 0) >= far)
        print(f"\n{cls}: statement at or past this class's p90 ({far}w) with no scenario "
              f"anchored — {len(long_unpinned)}; a long condition no concrete case pins is the "
              f"one a scenario would settle (an abstract rule legitimately has none):")
        for identity in long_unpinned:
            print(f"{mark(identity)} {read[identity]['statement_words']:>4}w  {identity}")
        if not long_unpinned:
            print("  (none)")

    for identity, entry in sorted(read.items()):
        stated = entry.get("why_words")
        if not stated:
            continue
        far = percentile(stated, 0.9)
        print(f"\n{identity}: {len(stated)} entry(ies); `why` median "
              f"{percentile(stated, 0.5)}w, p90 {far}w, max {max(stated)}w. «`why` carries one "
              f"claim a reviewer can reject» (SPEC-001 R9) — {sum(1 for w in stated if w >= far)} "
              f"entry(ies) at or past that p90 are where to check whether it carries an argument "
              f"about the specification's composition instead.")

    selfref = sorted(identity for identity, entry in read.items() if entry["selfref"])
    print(f"\nnormative field speaking about the specification rather than the domain — "
          f"{len(selfref)}; a statement is a falsifiable condition, not a remark about itself:")
    for identity in selfref:
        print(f"{mark(identity)} {', '.join(read[identity]['selfref'])}  in  {identity}")
    if not selfref:
        print("  (none)")

    phrases = shared_phrases(nodes)
    print(f"\nlongest phrase each set of nodes shares in its normative fields — {len(phrases)} "
          f"set(s), {min(len(phrases), ROWS_SHOWN)} shown, by words times holders; a clause "
          f"two nodes both carry — «a noun phrase restated across nodes is one definition kept in as "
          f"many places as it appears» (SPEC-001 R3):")
    for holders, phrase in cut(phrases, lambda row: row[0]):
        print(f"{'>' if named & set(holders) else ' '} {len(phrase.split()):>3}w x "
              f"{len(holders):>2} node(s)  \"{phrase}\"")
        for identity in sorted(holders):
            print(f"       {mark(identity)}{identity}")
    if not phrases:
        print("  (none)")

    argued = sorted(((entry["prose_gap"], identity) for identity, entry in
                     ((i, dict(e, prose_gap=len(e["names"]) - e["declared"]))
                      for i, e in read.items()) if entry["prose_gap"] > 0), reverse=True)
    print(f"\nprose naming more sibling nodes than the fields declare — {len(argued)}; the "
          f"declared side is the walk that validates it, the prose side is a text scan. A node "
          f"declaring two and naming twenty is arguing, not governing — «It does not argue that "
          f"the node is consistent with its neighbours» (SPEC-001 R14):")
    for gap, identity in cut(argued, lambda row: (row[1],)):
        entry = read[identity]
        print(f"{mark(identity)} {len(entry['names']):>3} in prose / "
              f"{entry['declared']:>2} declared  (+{gap})  {entry['words']:>5}w  {identity}")
    if not argued:
        print("  (none)")

    ranked = cut(sorted(read.items(), key=lambda pair: -pair[1]["closure_words"]),
                 lambda row: (row[0],))
    print(f"\nreading closure — every node a node's prose names, transitively, and what that "
          f"comes to in words:")
    for identity, entry in ranked:
        print(f"{mark(identity)} {len(entry['closure']):>4} node(s)  "
              f"{entry['closure_words']:>7}w  {identity}")

    unheld: dict[str, int] = {}
    for entry in read.values():
        for name in entry["unheld"]:
            unheld[name] = unheld.get(name, 0) + 1
    print(f"\nnames this prose holds that resolve to no node — {len(unheld)}; "
          f"a name used normatively and held nowhere is a node owed, not a typo:")
    for name, count in sorted(unheld.items(), key=lambda pair: (-pair[1], pair[0])):
        print(f"  {count:>4} node(s)  {name}")
    if not unheld:
        print("  (none)")

    unsure: dict[str, int] = {}
    for entry in read.values():
        for name in entry["ambiguous"]:
            unsure[name] = unsure.get(name, 0) + 1
    print(f"\nbare names two nodes answer to — {len(unsure)}; resolved to neither, "
          f"«A slug is unique inside a directory and not across the specification» (SPEC-003 R2):")
    for name, count in sorted(unsure.items(), key=lambda pair: (-pair[1], pair[0])):
        holds = sorted(i for i in nodes if i.rsplit("/", 1)[-1] == name)
        print(f"  {count:>4} node(s)  `{name}`  ->  {', '.join(holds)}")
    if not unsure:
        print("  (none)")
    return 0


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
        for attribute in listed(node["front"], "attributes"):
            lines.append(attribute_line(attribute, nodes, context))
        for value in listed(node["front"], "values"):
            lines.append(f"        {value.replace('-', '_').upper()}")
        for operation in listed(node["front"], "operations"):
            lines.append(f"        +{camel(operation)}()")
        lines.append("    }")
        return lines

    def foreign(members: dict[str, dict]) -> dict[str, dict]:
        """Every element another context owns that this diagram names — through an attribute's
        type or a relationship's target. Without a declared block Mermaid autocreates each as a
        bare box, and a reader of one diagram cannot tell the foreign name from a local one; the
        stereotype says whose it is and which diagram states it. The block stays empty on
        purpose: the attributes live in the owning context's diagram, and restating them here
        would be the second home the documentation floor exists to refuse."""
        named: dict[str, dict] = {}
        for node in members.values():
            declared = [a["type"] for a in listed(node["front"], "attributes")
                        if a["type"] not in PRIMITIVES]
            declared += [r["target"] for r in listed(node["front"], "relationships")]
            for ref in declared:
                target = nodes.get(resolve(ref, context))
                if target is not None and target["context"] != context:
                    named[resolve(ref, context)] = target
        return named

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
    named_foreign = foreign(members)
    drawn: dict[str, str] = {}
    for identity in sorted(named_foreign):
        target = named_foreign[identity]
        name = pascal(target)
        # Two foreign elements of different contexts sharing a slug emit one class name, and
        # Mermaid merges two declarations of one name into a single box carrying whichever
        # stereotype came last. Renaming them would change every existing diagram's labels, so
        # the collision is refused instead of drawn wrong.
        if name in drawn and drawn[name] != identity:
            raise Collision(f"the {context} class diagram names {name} for both "
                            f"{drawn[name]} and {identity}; two foreign elements of one name "
                            f"merge into one box, and the diagram would state a boundary "
                            f"neither of them has")
        drawn[name] = identity
        lines += [f"    class {name} {{",
                  f"        <<external: {target['context']}>>",
                  "    }"]
    for identity in sorted(members):
        node = members[identity]
        for entry in listed(node["front"], "relationships"):
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


def model_reading(node: dict) -> str | None:
    """How a consumed contract crosses its boundary, read from the payload alone: the upstream's
    own element means the consuming context adopts that model; an element of its own means it
    translates. An api carries operations and no payload, so it reads neither way."""
    payload = node["front"].get("payload")
    if not isinstance(payload, str):
        return None
    return "translated" if payload.split("/")[1] == node["context"] else "adopted"


def context_map(nodes: dict[str, dict]) -> str:
    contexts = sorted(n["context"] for n in nodes.values() if n["cls"] == "context")
    lines = ["flowchart LR"]
    for context in contexts:
        descriptor = nodes[f"domain/{context}/_context"]
        lines.append(f"    {context.replace('-', '_')}"
                     f"[\"{pascal(descriptor)} ({descriptor['front']['strategic']})\"]")
    edges = set()
    consumed = set()
    for identity, node in nodes.items():
        if node["cls"] == "contract" and isinstance(node["front"].get("upstream"), str):
            consumed.add(node["front"]["upstream"])
            upstream = nodes.get(node["front"]["upstream"])
            if upstream is not None:
                edges.add((upstream["context"], node["context"], upstream["slug"],
                           model_reading(node)))
    for source, target, label, reading in sorted(edges, key=lambda e: e[:3]):
        shown = f"{label} ({reading})" if reading else label
        lines.append(f"    {source.replace('-', '_')} -->|{shown}| "
                     f"{target.replace('-', '_')}")
    # A model referenced across contexts is a dependency no contract declares: the referencing
    # context reads the owner's element as its own, which is a kernel the two share. Thick, so a
    # shared model never reads as the consumption the solid edges state.
    shared = set()
    for identity, node in nodes.items():
        if node["cls"] != "element":
            continue
        for target, _, _ in element_refs(node):
            owner = nodes.get(target)
            if owner is not None and owner["context"] != node["context"]:
                shared.add((node["context"], owner["context"], owner["slug"]))
    for source, target, slug in sorted(shared):
        lines.append(f"    {source.replace('-', '_')} ==>|model: {slug}| "
                     f"{target.replace('-', '_')}")
    # A published contract nothing inside consumes is a door for the outside — the system's own
    # surface. Until these edges existed the map drew only internal consumption, so the one
    # diagram a reader opens first was silent about every entry point the system offers; the
    # dashed edge keeps the two kinds of fact apart. Capabilities are not repeated here: they
    # live in the system context and the capability map is theirs.
    offered = sorted((node["context"], node["slug"]) for identity, node in nodes.items()
                     if node["cls"] == "contract" and node["context"] != SYSTEM
                     and node["front"].get("direction") == "published"
                     and identity not in consumed)
    if offered:
        lines.append("    outside([\"outside\"])")
        for context, label in offered:
            lines.append(f"    {context.replace('-', '_')} -.->|{label}| outside")
    pairs = {(s, t) for s, t, _, _ in edges} | {(s, t) for s, t, _ in shared}
    connected = pairs | {(t, s) for s, t in pairs}
    for index, one in enumerate(contexts):
        for other in contexts[index + 1:]:
            if (one, other) not in connected:
                lines.append(f"    %% separate ways: {one} and {other} share no contract "
                             f"and no model")
    return "\n".join(lines) + "\n"


def state_diagram(node: dict, nodes: dict[str, dict]) -> str:
    front = node["front"]
    lines = ["stateDiagram-v2", f"    [*] --> {front['initial']}"]
    for transition in listed(front, "transitions"):
        lines.append(f"    {transition['from']} --> {transition['to']} : "
                     f"{camel(transition['trigger'])}")
    for state in listed(front, "terminal"):
        lines.append(f"    {state} --> [*]")
    for rejection in listed(front, "rejections"):
        lines.append(f"    %% rejected: {camel(rejection['trigger'])} in {rejection['from']}")
    return "\n".join(lines) + "\n"


def capability_contexts(identity: str, nodes: dict[str, dict]) -> list[str]:
    touched = set()
    for node in nodes.values():
        if node["cls"] != "scenario" or node["front"].get("subject") != identity:
            continue
        for ref in [node["front"]["subject"]] + list(listed(node["front"], "involves")):
            context = ref.split("/")[1]
            if context != SYSTEM:
                touched.add(context)
    return sorted(touched)


def capability_consumers(identity: str, nodes: dict[str, dict]) -> list[str]:
    """The contexts whose own consumed contracts name this capability upstream — consumption the
    files already declare, reaching the map without a scenario. It is the second of the two
    sources an edge can derive from, and the two say different things: a scenario says the
    capability's flow orchestrates the context, an upstream says the context consumes the
    capability, and the map draws them apart."""
    return sorted({node["context"] for node in nodes.values()
                   if node["cls"] == "contract"
                   and node["front"].get("upstream") == identity
                   and node["context"] != SYSTEM})


def capability_map(nodes: dict[str, dict]) -> str:
    lines = ["flowchart TD"]
    for identity in sorted(nodes):
        node = nodes[identity]
        if node["cls"] != "contract" or node["front"].get("type") != "capability":
            continue
        # Namespaced: a capability whose slug equals a context's would share that context's
        # node id, and Mermaid merges two declarations of one id into one box — a capability
        # silently drawn as the context it points at.
        anchor = "cap_" + node["slug"].replace("-", "_")
        lines.append(f"    {anchor}[\"{pascal(node)}\"]")
        touched = capability_contexts(identity, nodes)
        consumers = [c for c in capability_consumers(identity, nodes) if c not in touched]
        for context in touched:
            lines.append(f"    {anchor} --> {context.replace('-', '_')}")
        for context in consumers:
            lines.append(f"    {anchor} -.-> {context.replace('-', '_')}")
        if not touched and not consumers:
            # A node with no edge reads as a finished map; what it means is that nobody wrote
            # the scenario and nothing consumes the capability, and the absence has to say so —
            # the same reason the context map declares separate ways instead of staying silent.
            lines.append(f"    %% unmapped: no scenario names {node['slug']} and no contract "
                         f"consumes it; which contexts realize it is undeclared")
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
    # One line per consistency boundary, so its size is read here rather than by opening one
    # class diagram per context: the boundary is what changes together, and how much it holds is
    # the first thing to weigh about it.
    lines += ["", "## Aggregates", ""]
    roots = [i for i, n in sorted(nodes.items())
             if n["cls"] == "element" and n["front"].get("type") == "aggregate-root"]
    for identity in roots:
        root = nodes[identity]
        inside = sum(1 for n in nodes.values() if n["cls"] == "element" and n is not root
                     and aggregate_of(n) == (root["context"], root["slug"]))
        lines.append(f"- {root['context']}/{root['slug']} — {inside} entity(ies) inside, "
                     f"{len(listed(root['front'], 'attributes'))} attribute(s) on the root")
    if not roots:
        lines.append("None.")
    lines += ["", "## Capabilities", ""]
    capabilities = [i for i, n in sorted(nodes.items())
                    if n["cls"] == "contract" and n["front"].get("type") == "capability"]
    for identity in capabilities:
        touched = capability_contexts(identity, nodes)
        consumers = [c for c in capability_consumers(identity, nodes) if c not in touched]
        said = []
        if touched:
            said.append(f"orchestrates {', '.join(touched)}")
        if consumers:
            said.append(f"consumed by {', '.join(consumers)}")
        suffix = f" — {'; '.join(said)}" if said else \
            " — unmapped: no scenario names it and no contract consumes it"
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


def full_text(nodes: dict[str, dict]) -> str:
    """Every specification file's text, verbatim, under a header naming its identity. One grep
    target instead of a walk: a reader hunting where a fact lives greps this once, then opens the
    node the match names — the projection locates and never states, and a claim about a node is
    made from the node's own file. Verbatim because anything less is a summary, and a summary is
    exactly what a search over it would find instead of the specification."""
    lines = ["# Full text",
             "",
             "Derived by spec.py from the specification files; never edited. Grep here to locate;",
             "open the node file a match names before claiming anything about it.",
             ""]
    for identity in sorted(nodes):
        lines += [f"=== {identity}",
                  nodes[identity]["path"].read_text(encoding="utf-8").rstrip("\n"),
                  ""]
    return "\n".join(lines)


def decisions_by_node(nodes: dict[str, dict]) -> str:
    """The decision log's entries, grouped by the file each one located. The log itself is
    append-only and ordered by when — the right shape for disclosure, the wrong one for the
    question a conformance reading asks, which is `what was decided about this node`: answering
    that from the log reads every entry ever written, and the read grows with the project's whole
    history. The log stays the authority; this locates its entries and restates nothing beyond
    what each one says."""
    lines = ["# Decisions by node",
             "",
             "Derived by spec.py from decision-log.md; never edited. The log is the authority —",
             "this groups its entries by the file each one located.",
             ""]
    entries = nodes.get("decision-log", {"front": {}})["front"].get("entries") or []
    grouped: dict[str, list[dict]] = {}
    for entry in entries:
        if isinstance(entry, dict) and isinstance(entry.get("location"), str):
            grouped.setdefault(entry["location"], []).append(entry)
    for location in sorted(grouped):
        lines.append(f"## {location}")
        for entry in grouped[location]:
            lines += [f"- {entry.get('field', '?')} — decided: {entry.get('decided', '?')}",
                      f"  unstated: {entry.get('unstated', '?')}",
                      f"  why: {entry.get('why', '?')}"]
        lines.append("")
    if not grouped:
        lines.append("No decisions disclosed yet.")
    return "\n".join(lines).rstrip("\n") + "\n"


class Collision(Exception):
    """Two nodes computing to one projection filename. Raised rather than returned because it is
    a defect in this script's naming, not a problem with the specification it read."""


def project(nodes: dict[str, dict]) -> dict[str, str]:
    """Every projection the specification derives to, by filename."""
    files: dict[str, str] = {}
    for context in sorted(n["context"] for n in nodes.values() if n["cls"] == "context"):
        files[f"class-diagram-{context}.mmd"] = class_diagram(context, nodes)
    files["context-map.mmd"] = context_map(nodes)
    # A state diagram is named for the machine's subject, not for the rule's own context: two
    # rules in one context over subjects of the same name in different contexts computed to one
    # filename, and the second silently replaced the first in a specification with no problems.
    projected_by: dict[str, str] = {}
    for identity in sorted(nodes):
        node = nodes[identity]
        if node["cls"] == "rule" and node["front"].get("type") == "state-machine":
            subject = node["front"]["subject"]
            anchor = nodes.get(subject)
            context = anchor["context"] if anchor else node["context"]
            name = f"state-{context}-{subject.split('/')[-1]}.mmd"
            if name in projected_by:
                raise Collision(f"{name} is projected by two state machines, "
                                f"{projected_by[name]} and {identity}; writing the second would "
                                f"drop the first, and a projection that loses a diagram is worse "
                                f"than no projection")
            projected_by[name] = identity
            files[name] = state_diagram(node, nodes)
    files["capability-map.mmd"] = capability_map(nodes)
    files["overview.md"] = overview(nodes)
    files["full-text.md"] = full_text(nodes)
    files["decisions-by-node.md"] = decisions_by_node(nodes)
    return files


def print_class_contract(named: str | None) -> int:
    """What one node class may and must declare, read out of its own schema and printed whole.

    It exists because the specification is the artifact a human writes most of by hand, and the
    only home of what a class admits is a file under the plugin's own `schemas/spec/`. A person
    with the question had to know that directory exists and open it; every other contract in this
    framework already answers the same question through its own script. Named with no class, this
    lists them, because being told a name is wrong without being told the names costs the lookup
    twice."""
    if named is None:
        print("the specification's node classes, and what each is:")
        for cls, filename in sorted(SCHEMAS.items()):
            path = SCHEMA_DIR / filename
            title = "—"
            if path.is_file():
                title = json.loads(path.read_text(encoding="utf-8")).get("title", "—")
            print(f"  {cls:<11} {title}  [{filename}]")
        print("\nname one to print what it may and must declare, its `$ref`s resolved: "
              "spec.py --contract <class>")
        return 0
    if named not in SCHEMAS:
        print(f"cannot run: {named} is not a node class; one of "
              f"{', '.join(sorted(SCHEMAS))}", file=sys.stderr)
        return CANNOT_RUN
    path = SCHEMA_DIR / SCHEMAS[named]
    if not path.is_file():
        print(f"cannot run: {path} is missing; nothing can be printed without it", file=sys.stderr)
        return CANNOT_RUN
    print(json.dumps(whole_contract(json.loads(path.read_text(encoding="utf-8"))),
                     indent=2, ensure_ascii=False))
    return 0


def main() -> int:
    args = sys.argv[1:]
    if "--help" in args:
        # The docstring is this script's one home of what it does and how it is called,
        # so `--help` prints that rather than a second copy of it that could drift.
        print(__doc__.strip())
        return 0
    if "--contract" in args:
        at = args.index("--contract")
        rest = [a for a in args[at + 1:] if not a.startswith("--")]
        if len(args) != at + 1 + len(rest) or len(rest) > 1 or at != 0:
            print("cannot run: --contract stands alone, optionally with one class name",
                  file=sys.stderr)
            return CANNOT_RUN
        return print_class_contract(rest[0] if rest else None)
    write = "--project" in args
    show_digests = "--digest" in args
    shape = "--shape" in args
    args = [a for a in args if a not in ("--project", "--digest", "--shape")]
    of = None
    if "--of" in args:
        at = args.index("--of")
        if at + 1 >= len(args):
            print("cannot run: --of takes a comma-separated list of node identities",
                  file=sys.stderr)
            return CANNOT_RUN
        of = [name.strip() for name in args[at + 1].split(",") if name.strip()]
        del args[at:at + 2]
        if not of:
            print("cannot run: --of names no node", file=sys.stderr)
            return CANNOT_RUN
        if not shape:
            print("cannot run: --of scopes what --shape marks and stands beside nothing else",
                  file=sys.stderr)
            return CANNOT_RUN
    impact = None
    if "--impact" in args:
        at = args.index("--impact")
        if at + 1 >= len(args):
            print("cannot run: --impact takes a comma-separated list of node identities",
                  file=sys.stderr)
            return CANNOT_RUN
        impact = [name.strip() for name in args[at + 1].split(",") if name.strip()]
        del args[at:at + 2]
        if not impact:
            print("cannot run: --impact names no node", file=sys.stderr)
            return CANNOT_RUN
    single = None
    if "--node" in args:
        at = args.index("--node")
        if at + 1 >= len(args):
            print("cannot run: --node takes a file", file=sys.stderr)
            return CANNOT_RUN
        single = args[at + 1]
        del args[at:at + 2]
    if impact is not None and (write or show_digests or shape or single is not None):
        print("cannot run: --impact reads the specification and derives nothing; it stands "
              "beside no other flag", file=sys.stderr)
        return CANNOT_RUN
    if (write or show_digests or shape) and single is not None:
        print("cannot run: --node validates one file, and --project/--digest/--shape are facts "
              "about the whole specification", file=sys.stderr)
        return CANNOT_RUN
    if sum((write, show_digests, shape)) > 1:
        print("cannot run: --project, --digest and --shape are mutually exclusive",
              file=sys.stderr)
        return CANNOT_RUN
    if len(args) != 1 or args[0].startswith("--"):
        print("cannot run: expected [--project | --digest | "
              "--shape [--of <identity>[,<identity>...]] | --node <file> | "
              "--impact <identity>[,<identity>...]] <spec-root>", file=sys.stderr)
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
    declared: dict[str, set[str]] = {}
    problems += cross_problems(
        nodes, root,
        (lambda owner, at, target, resolved:
         declared.setdefault(owner, set()).add(target)) if shape else None)
    if impact is not None:
        return print_impact(nodes, root, impact, problems)
    if shape:
        missing = [identity for identity in (of or [])
                   if not (root / f"{identity}.md").is_file()]
        if missing:
            print(f"cannot run: {', '.join(missing)} names no file under {root}; "
                  f"an identity is a node's path without `.md`", file=sys.stderr)
            return CANNOT_RUN
        return print_shape(nodes, root, problems, declared, of)
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
        try:
            derived = project(nodes)
        except Collision as broken:
            print(f"cannot run: {broken}", file=sys.stderr)
            return CANNOT_RUN
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
