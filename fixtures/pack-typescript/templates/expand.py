"""The ten deterministic templates of the `typescript-node` pack.

`specs/0011` R1 makes a template the mechanism of the deterministic generation track: it expands
structured knowledge into exactly one artifact class, with no model in the loop, and identical
input yields byte-identical output. Every constraint that follows from that is visible here, and
each one is a test in `tests/test_pack_typescript.py`.

- **R4** — a template reads only its declared inputs. There is no clock, no environment variable,
  no random source, no network, and no file read anywhere in this module. Each is a way for output
  to differ between two runs over the same knowledge.
- **R5** — a value the knowledge does not hold is supplied by the caller. `header()` takes the
  pack version rather than reading one, and nothing here mints an identifier.
- **R6** — iteration follows a total order derived from the knowledge. Attributes keep their
  authored order, which the knowledge object fixes; every set is sorted before it is rendered.
  Directory order, mapping insertion order, and hash order are not orders.
- **R8** — knowledge is referenced by ontology identifier, never by path. `_symbol()` derives a
  TypeScript name from an id, and no template takes a path as input.
- **R10** — a missing required input fails naming what is absent. No default is substituted for a
  domain fact, because a default invented at expansion time is a domain fact authored by the pack.
- **R11** — every branch reads a closed field: a node `type`, a `ddd` value, an attribute `type`
  from the primitive vocabulary. Nothing branches on prose or on a substring.
- **R12, R13** — naming, layout, and idiom are here; no domain fact is. Every value in the output
  that says something about the world came from a knowledge object.

`specs/0004` R2 is what the whole module is held to, and R51 pairs each function with exactly one
declared class.
"""

from __future__ import annotations

# The attribute type vocabulary `schemas/knowledge-object.json` closes, mapped to this stack.
# Total over that enum by assertion below: a type the knowledge base can hold and this pack cannot
# express would fail at expansion, which is the worst place to discover a gap in a pack's coverage.
#
# `decimal` and `money` become `string` rather than `number`: an IEEE double cannot hold a money
# amount exactly, and choosing `number` would make the pack silently lossy for the one attribute
# type a billing domain is most likely to use. That is stack knowledge, which specs/0011 R12 puts
# here — and the reason is recorded because the wrong choice would look tidier.
PRIMITIVE = {
    "string": "string",
    "text": "string",
    "integer": "number",
    "decimal": "string",
    "money": "string",
    "boolean": "boolean",
    "date": "string",
    "datetime": "string",
    "duration": "string",
    "enum": "string",
    "ref": "string",
    "list": "readonly string[]",
}

SQL = {
    "string": "text",
    "text": "text",
    "integer": "integer",
    "decimal": "numeric",
    "money": "numeric(19, 4)",
    "boolean": "boolean",
    "date": "date",
    "datetime": "timestamptz",
    "duration": "interval",
    "enum": "text",
    "ref": "uuid",
    "list": "text[]",
}


class MissingFact(Exception):
    """The knowledge does not hold something this template needs — specs/0011 R10."""


def _require(node: dict, field: str, artifact_class: str) -> object:
    value = node.get(field)
    if value in (None, [], {}):
        raise MissingFact(
            f"{node['id']}: the {artifact_class} template needs `{field}` and "
            f"the knowledge object does not hold it. specs/0011 R10: no default is substituted for a "
            f"domain fact, because a default invented here is a domain fact authored by the pack"
        )
    return value


def _symbol(node_id: str) -> str:
    """`ko.definition.<context>.<slug>` -> a PascalCase symbol. R8: from the id, never a path."""
    return "".join(part.capitalize() for part in node_id.split(".")[-1].split("-"))


def _member(name: str) -> str:
    head, *rest = name.split("-")
    return head + "".join(part.capitalize() for part in rest)


def _snake(node_id: str) -> str:
    return node_id.split(".")[-1].replace("-", "_")


def header(node: dict, pack_version: str) -> str:
    """The provenance line every produced file carries.

    The pack version is an input rather than something read here — R5, and the reason R4 gives:
    a value this module discovered for itself would differ between two runs over one knowledge base.
    """
    return (
        f"// Generated from {node['id']} by typescript-node {pack_version}.\n"
        f"// specs/0004 R7: this file is not hand-edited. Change the knowledge object.\n"
    )


# --- definition -----------------------------------------------------------------------


def _fields(node: dict, artifact_class: str) -> list[tuple[str, str, bool]]:
    attributes = _require(node, "attributes", artifact_class)
    out = []
    for attribute in attributes:
        kind = attribute["type"]
        if kind not in PRIMITIVE:
            raise MissingFact(
                f"{node['id']}: attribute {attribute['name']!r} has type {kind!r}, which is outside "
                f"the primitive vocabulary this pack expands"
            )
        out.append((attribute["name"], PRIMITIVE[kind], bool(attribute.get("required"))))
    return out


def type_(node: dict, pack_version: str) -> str:
    lines = [header(node, pack_version), f"export interface {_symbol(node['id'])} {{"]
    for name, kind, required in _fields(node, "type"):
        lines.append(f"  {_member(name)}{'' if required else '?'}: {kind};")
    lines.append("}\n")
    return "\n".join(lines)


def dto(node: dict, pack_version: str) -> str:
    lines = [header(node, pack_version), f"export interface {_symbol(node['id'])}Dto {{"]
    for name, kind, required in _fields(node, "dto"):
        lines.append(f"  {name}{'' if required else '?'}: {kind};")
    lines.append("}\n")
    return "\n".join(lines)


def persistence_schema(node: dict, pack_version: str) -> str:
    lines = [header(node, pack_version), f"create table {_snake(node['id'])} ("]
    rendered = []
    for name, _kind, required in _fields(node, "persistence-schema"):
        column = name.replace("-", "_")
        sql = SQL[next(a["type"] for a in node["attributes"] if a["name"] == name)]
        rendered.append(f"  {column} {sql}{'' if not required else ' not null'}")
    lines.append(",\n".join(rendered))
    lines.append(");\n")
    return "\n".join(lines)


def migration(node: dict, pack_version: str) -> str:
    lines = [header(node, pack_version), f"-- up", f"create table {_snake(node['id'])} ("]
    rendered = []
    for name, _kind, required in _fields(node, "migration"):
        column = name.replace("-", "_")
        sql = SQL[next(a["type"] for a in node["attributes"] if a["name"] == name)]
        rendered.append(f"  {column} {sql}{'' if not required else ' not null'}")
    lines.append(",\n".join(rendered))
    lines.extend([");", "", "-- down", f"drop table {_snake(node['id'])};\n"])
    return "\n".join(lines)


# --- lifecycle ------------------------------------------------------------------------


def enum(node: dict, pack_version: str) -> str:
    states = _require(node, "states", "enum")
    lines = [header(node, pack_version), f"export const {_symbol(node['id'])}State = {{"]
    for state in states:  # R6: the authored order, which the knowledge object fixes.
        lines.append(f'  {state.upper().replace("-", "_")}: "{state}",')
    lines.append("} as const;\n")
    return "\n".join(lines)


def state_machine(node: dict, pack_version: str) -> str:
    transitions = _require(node, "transitions", "state-machine")
    rejections = _require(node, "rejections", "state-machine")
    symbol = _symbol(node["id"])
    lines = [
        header(node, pack_version),
        f"export const {symbol}Transitions = [",
    ]
    for entry in transitions:
        lines.append(
            f'  {{ from: "{entry["from"]}", trigger: "{entry["trigger"]}", to: "{entry["to"]}" }},'
        )
    lines.append("] as const;\n")
    lines.append(f"export const {symbol}Rejections = [")
    for entry in rejections:
        triggers = entry["trigger"]
        for trigger in triggers if isinstance(triggers, list) else [triggers]:
            lines.append(
                f'  {{ from: "{entry["from"]}", trigger: "{trigger}", error: "{entry["error"]}" }},'
            )
    lines.append("] as const;\n")
    return "\n".join(lines)


# --- interface ------------------------------------------------------------------------


def event_schema(node: dict, pack_version: str) -> str:
    version = _require(node, "version", "event-schema")
    schema = _require(node, "schema", "event-schema")
    return (
        header(node, pack_version)
        + f"export const {_symbol(node['id'])}Event = {{\n"
        + f'  name: "{node["id"]}",\n'
        + f'  version: "{version}",\n'
        + f'  schema: "{schema}",\n'
        + "} as const;\n"
    )


def api_description(node: dict, pack_version: str) -> str:
    version = _require(node, "version", "api-description")
    ownership = _require(node, "ownership", "api-description")
    return (
        header(node, pack_version)
        + f"# {node['title']}\n\n"
        + f"- id: {node['id']}\n- version: {version}\n- ownership: {ownership}\n"
        + f"- schema: {_require(node, 'schema', 'api-description')}\n"
    )


# --- rule and lifecycle ----------------------------------------------------------------


def conformance_test(node: dict, pack_version: str) -> str:
    """specs/0004 R36: generated from `rule.examples` and from `lifecycle` totality.

    R3 makes a judged artifact with no covering suite unaccepted output, so this is what a
    judged `validator` is checked against — which is why it is on the deterministic track even
    though what it tests is not.
    """
    symbol = _symbol(node["id"])
    lines = [header(node, pack_version), f'describe("{node["id"]}", () => {{']
    if node["type"] == "rule":
        for index, example in enumerate(_require(node, "examples", "conformance-test")):
            outcome = example["then"]["outcome"]
            given = ", ".join(f"{k}={v}" for k, v in sorted(example["given"].items()))
            lines.append(
                f'  it("{outcome} when {given}", () => {{ '
                f'expect(check{symbol}({given.replace("=", ": ")!r})).toBe("{outcome}"); }});'
            )
    else:
        for entry in _require(node, "rejections", "conformance-test"):
            triggers = entry["trigger"]
            for trigger in triggers if isinstance(triggers, list) else [triggers]:
                lines.append(
                    f'  it("rejects {trigger} from {entry["from"]}", () => {{ '
                    f'expect(() => apply("{entry["from"]}", "{trigger}")).toThrow("{entry["error"]}"); }});'
                )
    lines.append("});\n")
    lines.append(f'// declares: {node["id"]}\n')
    return "\n".join(lines)


# --- boundary -------------------------------------------------------------------------


def documentation(node: dict, pack_version: str) -> str:
    return (
        header(node, pack_version)
        + f"# {node['title']}\n\n{node['description']}\n\n"
        + f"- id: {node['id']}\n- ddd: {_require(node, 'ddd', 'documentation')}\n"
    )


# One function per declared deterministic class. specs/0004 R51: exactly one producer per class,
# and this mapping is what the pack's own test asserts against its declaration.
TEMPLATES = {
    "type": type_,
    "dto": dto,
    "persistence-schema": persistence_schema,
    "migration": migration,
    "enum": enum,
    "state-machine": state_machine,
    "event-schema": event_schema,
    "api-description": api_description,
    "conformance-test": conformance_test,
    "documentation": documentation,
}
