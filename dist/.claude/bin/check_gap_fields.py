#!/usr/bin/env python3
"""Hold every declared gap to naming a field its node type would actually require.

An object may declare a gap in place of a field it lacks, and the contract then accepts it. That
alternation is what lets a base hold an object which says "this entity exists and its identity
strategy is unstated" instead of holding nothing about the entity — and it is only as strong as the
field names in the gaps.

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

Usage:  check_gap_fields.py <knowledge-or-staging-root>
Exit:   0 every gap names a field its type requires, 1 one does not, 2 cannot run
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
CANNOT_RUN = 2

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


def type_requirements(contract: dict, node_type: str, ddd: str | None) -> set[str]:
    """Every field this node type demands of an object with this `ddd`, read from the contract."""
    required: set[str] = set()
    for clause in contract.get("allOf", []):
        if clause.get("if", {}).get("properties", {}).get("type", {}).get("const") != node_type:
            continue
        branch = clause["then"]["anyOf"][0]
        required.update(branch.get("required", []))
        # A nested alternation is a requirement too, and either side of it may be what is missing.
        # A rule declares `expression` or `examples`, so a gap may legitimately name either — and
        # naming one is exactly how a rule with neither says which it is short of.
        for alternative in branch.get("anyOf", []):
            required.update(alternative.get("required", []))
        for nested in branch.get("allOf", []):
            condition = nested.get("if", {}).get("properties", {}).get("ddd", {})
            admitted = condition.get("enum") or ([condition["const"]] if "const" in condition else [])
            matched = ddd in admitted
            side = nested.get("then" if matched else "else") or {}
            required.update(side.get("required", []))
    return required


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
    node_type, ddd = data.get("type"), data.get("ddd")
    fields = type_requirements(contract, node_type, ddd)
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


def problems_for(data: dict, contract: dict, authoring: set[str], relative: str) -> list[str]:
    """Every gap on this object that names something its type does not require."""
    found: list[str] = []
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


def main() -> int:
    if len(sys.argv) != 2:
        print("cannot run: expected <knowledge-or-staging-root>", file=sys.stderr)
        return CANNOT_RUN
    root = Path(sys.argv[1])
    if not root.is_dir():
        print(f"cannot run: {root} is not a directory", file=sys.stderr)
        return CANNOT_RUN

    contract_path = PLUGIN_ROOT / "schemas" / "knowledge-object.json"
    if not contract_path.is_file():
        print(f"cannot run: {contract_path} is missing", file=sys.stderr)
        return CANNOT_RUN
    contract = json.loads(contract_path.read_text())

    # The three fields no analysis carries, read from the contract's own required set rather than
    # listed: they are exactly the required fields the staged contract drops.
    staged_path = PLUGIN_ROOT / "schemas" / "staged-knowledge-object.json"
    if not staged_path.is_file():
        print(f"cannot run: {staged_path} is missing", file=sys.stderr)
        return CANNOT_RUN
    authoring = set(contract["required"]) - set(json.loads(staged_path.read_text())["required"])

    objects = sorted(root.rglob("*.md"))
    if not objects:
        print(f"cannot run: {root} holds no object", file=sys.stderr)
        return CANNOT_RUN

    problems: list[str] = []
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

    print(f"gaps checked: {declared} across {len(objects)} object(s)  contract: "
          f"{contract['properties']['contract_version']['const']}")
    if problems:
        print(f"FAILED: {len(problems)} gap(s) name a field their type does not require\n")
        for problem in problems:
            print(f"  {problem}")
        return 1
    print("every gap names a field its node type requires and the object does not hold")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
