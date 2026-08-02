#!/usr/bin/env python3
"""Turn a validated domain model into staged knowledge objects and the plan that records the run.

This is the step that used to be an agent. Its evidence is a measured run: classifying 24 constructs
cost 75,329 tokens and produced a mapping that was 1:1 with the model in every entry, because the
mapping *is* a table — the ontology states it, closed, and nothing here decides anything the table
does not already say. The identifiers are arithmetic the same document specifies. A property that
must hold regardless of model judgment belongs in a script rather than in prompt text, and this is
that script.

Requirement numbers below name the ontology's own, which a consumer reads in the schemas this ships
beside. Nothing here cites a path outside the installation: the documents that decide these rules
stay in the repository that produced this file, and a citation to one would not resolve here.

What it refuses to do is as load-bearing as what it does. It supplies no fact the model does not
carry: a field the node type requires and the model leaves absent becomes a **gap** on the object,
named with what the domain would have to say. It repairs nothing: a fact the model states in a form
the ontology rejects becomes a **refusal**, and no file is written for that construct. The three
outcomes are the plan's own vocabulary.

Three roots and no defaults. The model, the knowledge root, and the instant come from the caller,
because a value this script chose would be a value nobody decided.

Declared dependencies: PyYAML.

Usage:  expand_model.py <model.json> <staging-root> <intake-id> <generated-by> <generated-at>
Exit:   0 the tree and the plan were written, 1 the model failed its contract, 2 cannot run
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from field_ownership import ENRICHMENT_FIELDS, SHARED_FIELD, closable

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
CANNOT_RUN = 2

try:
    import yaml
except ImportError:  # pragma: no cover - exercised by the environment, not the suite
    print("cannot run: PyYAML is not installed (pip install pyyaml)", file=sys.stderr)
    raise SystemExit(CANNOT_RUN)


# The mapping spec 0003 states, transcribed. A DDD kind lands in a node type, and the kind itself
# survives as the object's `ddd` value except where the table folds it into a field of another
# object: a subdomain is `boundary.subdomain_type`, and a context map is
# `boundary.context_relationships[]`. Neither yields an object of its own, so neither is here.
NODE_TYPE = {
    "context": "boundary",
    "aggregate": "boundary",
    "definition": "definition",
    "rule": "rule",
    "lifecycle": "lifecycle",
    "interface": "interface",
    "process": "process",
}

# Which model list holds each kind, and the `ddd` value a boundary takes from its kind rather than
# from a field of its own.
COLLECTION = {
    "context": "contexts", "aggregate": "aggregates", "definition": "definitions",
    "rule": "rules", "lifecycle": "lifecycles", "interface": "interfaces", "process": "processes",
}
BOUNDARY_DDD = {"context": "bounded-context", "aggregate": "aggregate"}

# The closed primitive vocabulary of spec 0003, and the parameters each primitive requires and does
# not inherit. A type outside this set is a refusal rather than a gap: the model states a fact the
# ontology rejects, and dropping the attribute to make the object conform would discard data.
PRIMITIVES = {
    "string": ("max_length",), "text": (), "integer": (), "decimal": ("precision", "scale"),
    "money": (), "boolean": (), "date": (), "datetime": (), "duration": (),
    "enum": (), "ref": ("target", "binding"), "list": ("of", "binding"),
}

# Body sections per node type, in the order spec 0003 fixes. The headings are written empty: the
# enrichment step fills them, and pre-placing them is what keeps it from inventing a third.
SECTIONS = {
    "definition": ("Answer", "Invariants"), "rule": ("Answer", "Conditions"),
    "lifecycle": ("Answer", "State semantics"), "interface": ("Answer", "Semantics"),
    "boundary": ("Answer", "Responsibilities"), "process": ("Answer", "Outcomes"),
}

# What each node type requires and the model may not supply. `authoring` is closed and identical for
# every type: the three fields no analysis carries, which a later step writes.
AUTHORING_FIELDS = ENRICHMENT_FIELDS

# What the expansion writes. Not `knowledge-object`: the four fields only judgment supplies are
# absent by construction here, and a staged file declaring the base's contract would be a file
# claiming to be something the boundary then rejects. Promotion rewrites this line after validating.
STAGED_CONTRACT = "staged-knowledge-object/2"

SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


class Refused(Exception):
    """The model states something the ontology rejects. Reported per construct, never repaired."""


def fail(message: str) -> "None":
    print(message, file=sys.stderr)
    raise SystemExit(1)


def slug(value: str) -> str | None:
    """Kebab-case, or None where the value will not reduce to one.

    Returning None rather than transliterating is deliberate. A name that needs an accent stripped
    or a script transliterated would take a rule no specification states, and R8 requires the same
    model to yield the same identifiers on every run — a rule invented here would be invented
    differently next time.
    """
    reduced = re.sub(r"[^a-z0-9]+", "-", (value or "").lower()).strip("-")
    return reduced if SLUG.match(reduced or "") else None


def boundary_of(element: dict, kind: str) -> str:
    """The one scope this object belongs to, per R16 and the identifier arithmetic of R33.

    A definition placed in an aggregate names that aggregate's boundary; everything else names its
    context. The model carries `aggregate` on a definition only, so the coarser placement is the
    declared rule rather than an omission — the proposal records it as lacuna A.
    """
    context = slug(element.get("context", ""))
    aggregate = slug(element.get("aggregate", "")) if kind == "definition" else None
    return f"ko.boundary.{context}.{aggregate}" if aggregate else f"ko.boundary.{context}"


def identifier(element: dict, kind: str, model: dict) -> str:
    """`ko.<type>.<boundary>.<slug>`, computed rather than allocated (R33, R34)."""
    node_type = NODE_TYPE[kind]
    if kind == "context":
        return f"ko.boundary.{slug(element['name'])}"
    if kind == "aggregate":
        return f"ko.boundary.{slug(element['context'])}.{slug(element['name'])}"
    if kind == "lifecycle":
        # R7: a lifecycle takes the slug of its subject, having no name of its own.
        name = element["subject"]
    else:
        name = element["name"]
    return f"ko.{node_type}.{slug(element['context'])}.{slug(name)}"


def resolve(name: str, index: dict[str, list[str]]) -> str:
    """A model reference by name, resolved to the one identifier it names, or refused.

    Two fields of the model point at another element by the name the model gives it —
    `process.steps[].element` and `lifecycle.transitions[].guard`. The object requires an
    identifier. Unique match or refusal: R18 reports an edge naming an id the graph does not hold
    and repairs nothing, and a name matching two elements of different kinds resolves to neither.
    """
    key = slug(name)
    found = index.get(key or "", [])
    if len(found) == 1:
        return found[0]
    if not found:
        raise Refused(f"names {name!r}, which matches no element of this model")
    raise Refused(f"names {name!r}, which matches {len(found)} elements: {', '.join(sorted(found))}")


def attributes_of(element: dict, index: dict) -> tuple[list[dict], list[dict]]:
    """The typed attributes and the gaps in them, with every reference resolved to an identifier.

    `target` and `of` point at another definition by the name the model gives it, exactly as
    `steps[].element` and `transitions[].guard` do, and the object requires an identifier in all
    four places. Unique match or refusal — a name matching two elements resolves to neither.

    A type outside the closed vocabulary raises rather than becoming a gap: it is a wrong fact and
    R19 rejects it, where a missing parameter is a fact the domain has not stated.
    """
    resolved: list[dict] = []
    gaps: list[dict] = []
    for attribute in element.get("attributes") or []:
        primitive = attribute.get("type")
        if primitive not in PRIMITIVES:
            raise Refused(
                f"attribute {attribute.get('name')!r} is typed {primitive!r}, which is outside the "
                f"closed primitive vocabulary; the type system admits no free-text type"
            )
        copy = dict(attribute)
        for reference in ("target", "of"):
            if copy.get(reference):
                copy[reference] = resolve(copy[reference], index)
        for parameter in PRIMITIVES[primitive]:
            if parameter not in copy and parameter not in (copy.get("parameters") or {}):
                gaps.append({
                    "kind": "domain",
                    "field": f"attributes[{attribute['name']}].{parameter}",
                    "why": f"a {primitive} requires {parameter} and the model states none",
                })
        resolved.append(copy)
    return resolved, gaps


def frontmatter_for(element: dict, kind: str, model: dict, index: dict, stamp: dict) -> tuple[dict, list[dict]]:
    """The object's frontmatter and its gaps, derived from the element and from nothing else."""
    node_type = NODE_TYPE[kind]
    gaps: list[dict] = []
    data: dict = {
        "id": identifier(element, kind, model),
        "type": node_type,
        "title": element.get("name") or element.get("subject"),
        "contract_version": STAGED_CONTRACT,
        "generated": dict(stamp),
        "origin": element["origin"],
    }
    if kind != "context":
        data["boundary"] = boundary_of(element, kind)

    if kind in BOUNDARY_DDD:
        data["ddd"] = BOUNDARY_DDD[kind]
    elif "ddd" in element:
        data["ddd"] = element["ddd"]

    if kind == "context":
        subdomains = {s["name"]: s for s in model.get("subdomains") or []}
        subdomain = subdomains.get(element.get("subdomain"))
        if subdomain:
            data["subdomain_type"] = subdomain["type"]
        else:
            gaps.append({"kind": "domain", "field": "subdomain_type",
                         "why": "the model classifies this context under no subdomain"})
        relationships = element.get("relationships") or []
        if relationships:
            data["context_relationships"] = [
                {"with": f"ko.boundary.{slug(r['with'])}", "pattern": r["pattern"]}
                for r in relationships
            ]

    if kind == "definition":
        if element.get("attributes"):
            data["attributes"], attribute_holes = attributes_of(element, index)
            gaps += attribute_holes
        else:
            gaps.append({"kind": "domain", "field": "attributes",
                         "why": "the model states no attribute this definition holds"})
        if element["ddd"] in ("entity", "aggregate-root", "read-model"):
            if element.get("identity"):
                data["identity"] = {"attributes": element["identity"]}
            else:
                gaps.append({"kind": "domain", "field": "identity.attributes",
                             "why": f"a {element['ddd']} is identified, and the model names no "
                                    f"attribute that identifies one"})

    if kind == "rule":
        data["statement"] = element["statement"]
        for optional in ("expression", "examples"):
            if element.get(optional):
                data[optional] = element[optional]
        if not (element.get("expression") or element.get("examples")):
            gaps.append({"kind": "domain", "field": "expression",
                         "why": "a rule is falsifiable, and the model states neither an expression "
                                "nor an example on either side of it"})

    if kind == "lifecycle":
        data["subject"] = f"ko.definition.{slug(element['context'])}.{slug(element['subject'])}"
        data["states"] = element["states"]
        data["initial"] = element["initial"]
        data["transitions"] = [
            {**{k: v for k, v in t.items() if k != "guard"},
             **({"guard": resolve(t["guard"], index)} if t.get("guard") else {})}
            for t in element["transitions"]
        ]
        if element.get("terminal"):
            data["terminal"] = element["terminal"]
        if element.get("rejections"):
            data["rejections"] = element["rejections"]
        else:
            gaps.append({"kind": "domain", "field": "rejections",
                         "why": "the transition table must be total, and the model records no "
                                "rejection for any state-and-trigger pair it leaves out"})

    if kind == "interface":
        data["ownership"] = element["ownership"]
        for field in ("version", "schema"):
            if element.get(field):
                data[field] = element[field]
            else:
                gaps.append({"kind": "domain", "field": field,
                             "why": f"an interface declares its {field}, and the model states none"})

    if kind == "process":
        data["steps"] = [
            {"order": step["order"], "ko": resolve(step["element"], index),
             **({"outcome": step["outcome"]} if step.get("outcome") else {})}
            for step in sorted(element["steps"], key=lambda s: s["order"])
        ]

    data["sources"] = [
        {"resource": artifact, "id": model["request"]["id"]}
        for artifact in model["request"].get("artifacts") or []
    ] or [{"resource": model["request"]["id"], "id": model["request"]["id"]}]

    gaps += [{"kind": "authoring", "field": field} for field in AUTHORING_FIELDS]
    if gaps:
        data["gaps"] = gaps
    return data, gaps


def render(data: dict, node_type: str, body: str | None = None) -> str:
    """Frontmatter plus the two sections the type names, empty unless an enrichment filled them."""
    if body is None:
        body = "\n".join(f"## {section}\n" for section in SECTIONS[node_type])
    front = yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=100)
    return f"---\n{front}---\n\n# {data['title']}\n\n{body}"


def carry_enrichment(path: Path, data: dict, node_type: str) -> tuple[dict, str | None]:
    """Re-expanding over an enriched object: keep its side, rewrite ours, reopen what moved under it.

    The expansion owns everything derived from the model and the enrichment owns four fields and the
    body — `field_ownership` declares the line once and this is one of its three readers. So a
    second run over a model that changed rewrites its own side and preserves the other, rather than
    discarding sentences somebody wrote.

    The third clause is the one that matters, and preserving without it would be worse than
    overwriting. An enrichment written against a design that has since changed is *stale*, and
    silently keeping it would leave the object internally inconsistent with no trace. So where any
    field the expansion owns actually changed, the `authoring` gaps reopen: the enrichment's text
    stays and is marked as owed again, and the pass that revisits it sees which objects moved under
    it and which did not.

    An unchanged element is untouched, so a re-expansion over an unchanged model is a no-op and two
    runs still compare byte for byte.
    """
    if not path.is_file():
        return data, None
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", path.read_text(), re.S)
    if not match:
        return data, None
    previous = yaml.safe_load(match.group(1)) or {}

    # `render` writes the title heading, so what is carried is what follows it. Carrying the whole
    # remainder would give the object two. Sliced rather than split: a split takes a count, and a
    # bare number in a shipped file is what the threshold check is written to catch — correctly,
    # because a reader cannot tell a limit somebody calibrated from one somebody typed.
    remainder = match.group(2)
    title = re.search(r"^# .*$", remainder, re.MULTILINE)
    body = remainder[title.end():].lstrip("\n") if title else remainder

    carried = {field: previous[field] for field in ENRICHMENT_FIELDS if field in previous}
    written = re.sub(r"^## .*$", "", body, flags=re.MULTILINE).strip()
    if not carried and not written:
        # Nothing on the enrichment's side of the line, so there is nothing to preserve and the
        # object is rewritten exactly as a first expansion would write it.
        return data, None

    design_moved = any(
        key not in (SHARED_FIELD, *ENRICHMENT_FIELDS) and previous.get(key) != value
        for key, value in data.items()
    )
    merged = dict(data)
    merged.update(carried)

    # `gaps` is the one field both sides touch, so it is combined rather than taken from either.
    # A `domain` gap is re-derived every run and is the expansion's; whether an `authoring` gap is
    # open records what the enrichment did, and is the enrichment's — except where the design moved
    # under it, which reopens exactly what it had closed.
    domain_gaps = [gap for gap in data.get(SHARED_FIELD) or [] if not closable(gap)]
    still_open = [gap for gap in previous.get(SHARED_FIELD) or [] if closable(gap)]
    if design_moved:
        already = {gap["field"] for gap in still_open}
        still_open += [
            {"kind": "authoring", "field": field}
            for field in ENRICHMENT_FIELDS
            if field in carried and field not in already
        ]
        still_open.sort(key=lambda gap: ENRICHMENT_FIELDS.index(gap["field"]))
    combined = domain_gaps + still_open
    if combined:
        merged[SHARED_FIELD] = combined
    else:
        merged.pop(SHARED_FIELD, None)
    return merged, body


def build_index(model: dict) -> dict[str, list[str]]:
    """Every element by its slug, so a reference by name resolves to an identifier or to nothing."""
    index: dict[str, list[str]] = {}
    for kind, collection in COLLECTION.items():
        for element in model.get(collection) or []:
            name = element.get("name") or element.get("subject")
            key = slug(name)
            if key:
                index.setdefault(key, []).append(identifier(element, kind, model))
    return index


def expand(model: dict, staging: Path, intake_id: str, stamp: dict) -> dict:
    """Write one file per classified construct, and return the plan that records every construct."""
    index = build_index(model)
    entries: list[dict] = []

    for kind, collection in COLLECTION.items():
        for element in model.get(collection) or []:
            construct = element.get("name") or element.get("subject")
            try:
                data, gaps = frontmatter_for(element, kind, model, index, stamp)
            except Refused as refusal:
                entries.append({"construct": construct, "outcome": "refused",
                                "reason": str(refusal)})
                continue
            if slug(construct) is None:
                entries.append({
                    "construct": construct, "outcome": "refused",
                    "reason": "the name does not reduce to a kebab-case slug, and an identifier "
                              "derived by a rule no specification states would not be reproduced",
                })
                continue
            node_type = NODE_TYPE[kind]
            path = staging / node_type / Path(*data["id"].split(".")[2:])
            path = path.with_suffix(".md")
            path.parent.mkdir(parents=True, exist_ok=True)
            data, body = carry_enrichment(path, data, node_type)
            path.write_text(render(data, node_type, body))
            entries.append({
                "construct": construct, "outcome": "classified", "node_type": node_type,
                # A `lifecycle` carries no `ddd`: it is the node type a state machine becomes,
                # rather than a type carrying which construct it is. Emitting one filled a field
                # the object then rejects, which is what forced the classification to invent
                # `ddd: "lifecycle"` before this was a conditional.
                **({"ddd": data["ddd"]} if "ddd" in data else {}),
                "origin": element["origin"],
                **({"boundary": data["boundary"]} if "boundary" in data else {}),
                "proposed_id": data["id"], "gaps": gaps,
            })

    for excluded in model.get("excluded") or []:
        entries.append({"construct": excluded["subject"], "outcome": "unmapped",
                        "reason": excluded["reason"]})

    entries.sort(key=lambda e: (e["outcome"] != "classified", e.get("proposed_id", e["construct"])))
    return {
        "contract_version": "knowledge-intake-plan/6",
        "intake_id": intake_id,
        "producer": "expand-model",
        "consumer": "ingest-domain",
        "source": {
            "description": f"The domain model {model['model_id']}, answering request "
                           f"{model['request']['id']}",
            "artifacts": model["request"].get("artifacts") or [model["request"]["id"]],
        },
        "state": "classified",
        "entries": entries,
    }


def main() -> int:
    if len(sys.argv) != 6:
        print(__doc__.strip().splitlines()[-2], file=sys.stderr)
        return CANNOT_RUN
    model_path, staging, intake_id, by, at = sys.argv[1:]
    source = Path(model_path)
    if not source.is_file():
        print(f"cannot run: {model_path} is not a file", file=sys.stderr)
        return CANNOT_RUN
    model = json.loads(source.read_text())
    if model.get("contract_version") != "domain-model/4":
        fail(f"{model_path} declares {model.get('contract_version')!r}; this reads domain-model/4")
    if model.get("state") == "blocked":
        fail(f"{model_path} declares itself blocked: {model.get('blocking_reason')}")

    plan = expand(model, Path(staging), intake_id, {"by": by, "at": at})
    counts: dict[str, int] = {}
    for entry in plan["entries"]:
        counts[entry["outcome"]] = counts.get(entry["outcome"], 0) + 1
    print(json.dumps(plan, indent=2, ensure_ascii=False))
    summary = ", ".join(f"{count} {outcome}" for outcome, count in sorted(counts.items()))
    print(f"expanded into {staging}: {summary}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
