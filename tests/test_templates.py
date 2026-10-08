"""The templates are held to the contracts they are a starting point for.

`templates/` is where a new artifact is copied from, and until this module existed nothing read
any file in it. Two drifts had already landed: both frontmatter templates predate the pass that
made `effort` a field every shipped agent and skill declares, and the skill template's section
headings matched none of the ten skills actually shipped — so an artifact copied from it began by
disagreeing with every one of its siblings.

SPEC-002's own acceptance list asks for the first of these ("the template stays in step with
R5–R12") and nothing was answering it.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent
TEMPLATES = REPO / "templates"
SCHEMAS = REPO / "schemas"
SPEC_SCHEMAS = REPO / "src/claude/schemas/spec"
FENCE = re.compile(r"^---\n(.*?)\n---\n", re.S)


def fields_of(path: Path) -> list[str]:
    """The frontmatter keys a template declares, read as text: the values are placeholders and
    do not parse as YAML."""
    match = FENCE.match(path.read_text(encoding="utf-8"))
    assert match, f"{path.name} carries no frontmatter fence"
    return [line.split(":", 1)[0]
            for line in match.group(1).splitlines()
            # Top level only: a nested shape (an attribute's own `type`, a relationship's `role`)
            # is the schema's business under its parent, not a field of the node.
            if line[:1] not in (" ", "-", "#", "") and ":" in line]


@pytest.mark.parametrize("template,contract", [
    ("agent.md", "agent.json"),
    ("skill.md", "skill.json"),
])
def test_the_template_declares_only_fields_its_contract_admits(template, contract):
    schema = json.loads((SCHEMAS / contract).read_text(encoding="utf-8"))
    admitted = set(schema["properties"])
    declared = set(fields_of(TEMPLATES / template))
    assert declared <= admitted, \
        f"{template} declares {sorted(declared - admitted)}, which {contract} does not admit"


@pytest.mark.parametrize("template,contract", [
    ("agent.md", "agent.json"),
    ("skill.md", "skill.json"),
])
def test_the_template_declares_every_field_its_contract_requires(template, contract):
    schema = json.loads((SCHEMAS / contract).read_text(encoding="utf-8"))
    required = set(schema.get("required", []))
    declared = set(fields_of(TEMPLATES / template))
    assert required <= declared, \
        f"{template} omits {sorted(required - declared)}, which {contract} requires — an artifact " \
        f"copied from it starts invalid"


@pytest.mark.parametrize("template,shipped,pattern", [
    ("agent.md", "src/claude/agents", "*.md"),
    ("skill.md", "src/claude/skills", "*/SKILL.md"),
])
def test_the_template_declares_what_every_shipped_artifact_declares(template, shipped, pattern):
    """A field every shipped artifact carries and the template omits is a field the next artifact
    will be missing. `effort` was exactly that for both templates."""
    paths = sorted((REPO / shipped).glob(pattern))
    assert paths, f"{shipped} ships nothing; the guard lost its subject"
    universal = set.intersection(*(
        set(yaml.safe_load(FENCE.match(p.read_text(encoding="utf-8")).group(1)))
        for p in paths))
    declared = set(fields_of(TEMPLATES / template))
    assert universal <= declared, \
        f"{template} omits {sorted(universal - declared)}, which every artifact under {shipped} " \
        f"declares"


def test_the_element_template_declares_only_what_the_element_schema_admits():
    """SPEC-002's acceptance list asks for this one by name. The template's frontmatter is
    commented prose around placeholder values, so what is checked is the field inventory."""
    schema = json.loads((SPEC_SCHEMAS / "element.json").read_text(encoding="utf-8"))
    admitted = set(schema["properties"])
    declared = set(fields_of(TEMPLATES / "domain-model-element.md"))
    assert declared <= admitted, \
        f"the element template declares {sorted(declared - admitted)}, which element.json does " \
        f"not admit"


def test_the_skill_template_uses_the_headings_the_shipped_skills_use():
    """A template whose sections match none of the ten shipped skills teaches a shape the
    framework does not use."""
    template = {line.rstrip() for line in (TEMPLATES / "skill.md").read_text(encoding="utf-8")
                .splitlines() if line.startswith("## ")}
    shipped = [set(line.rstrip() for line in p.read_text(encoding="utf-8").splitlines()
                   if line.startswith("## "))
               for p in sorted((REPO / "src/claude/skills").rglob("SKILL.md"))]
    for heading in sorted(template):
        assert any(heading in one for one in shipped), \
            f"the skill template's {heading!r} appears in no shipped skill"


SPEC_STATUSES = ("proposed", "accepted", "retired")


@pytest.mark.parametrize("spec", sorted(p.name for p in (REPO / "specs").glob("*.md")))
def test_every_specification_declares_a_status_the_vocabulary_holds(spec):
    """`status` was on all three specifications and defined by no artifact, so it could hold any
    word at all and nothing would say so. The vocabulary now lives in the specification template;
    this holds each specification to it."""
    front = yaml.safe_load(FENCE.match((REPO / "specs" / spec).read_text(encoding="utf-8"))
                           .group(1))
    assert front.get("status") in SPEC_STATUSES, \
        f"{spec} declares status {front.get('status')!r}, which is not one of {SPEC_STATUSES}"


VALIDATION = re.compile(r"^## Validation required before acceptance\n\n1\. ", re.M)
REVERSAL = re.compile(r"\b(reverses|reversed|reopens)\b")
READING = re.compile(r"^- \d{4}-\d{2}-\d{2} — ", re.M)


@pytest.mark.parametrize("spec", sorted(p.name for p in (REPO / "specs").glob("*.md")))
def test_every_specification_carries_its_validation_list(spec):
    """`proposed` and `accepted` are statements about the validation list, so a specification
    with no list has no exit from `proposed` and nothing names what would prove it."""
    text = (REPO / "specs" / spec).read_text(encoding="utf-8")
    assert VALIDATION.search(text), \
        f"{spec} carries no 'Validation required before acceptance' list with a first item"


@pytest.mark.parametrize("spec", sorted(p.name for p in (REPO / "specs").glob("*.md")))
def test_a_specification_naming_a_reversal_records_its_readings(spec):
    """A validation item that names the fact reversing a requirement is an obligation to read
    that fact; a reading nobody records is a reversal nobody can trigger. The section is the
    record, one dated line per reading, and `not yet read` with its precondition is a reading."""
    text = (REPO / "specs" / spec).read_text(encoding="utf-8")
    validation = text.split("## Validation required before acceptance", 1)[-1]
    validation = validation.split("## Readings", 1)[0]
    if not REVERSAL.search(validation):
        pytest.skip("this specification names no reversal")
    assert "\n## Readings\n" in text, f"{spec} names a reversal and records no readings"
    readings = text.split("\n## Readings\n", 1)[1]
    assert READING.search(readings), f"{spec}: its Readings section holds no dated line"


def test_the_specification_template_states_what_each_status_means():
    """The vocabulary is only a vocabulary while something says what its words mean. A template
    that listed the three words without defining them would leave the same gap one level down."""
    text = (TEMPLATES / "specification.md").read_text(encoding="utf-8")
    for status in SPEC_STATUSES:
        assert re.search(rf"#\s+{status}\s+—", text), \
            f"the template names {status!r} without saying what it means"
