"""The five-class metamodel holds: every rejection SPEC-001/002/003 promise, proven.

Each test copies the sound fixture and breaks exactly one thing, so the message asserted is
the message a real specification would get. The fixture is the one full valid specification
SPEC-003's acceptance demands; the projections' determinism closes its second demand.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

import spec

REPO = Path(__file__).resolve().parent.parent
FIXTURE = REPO / "tests" / "fixtures" / "spec-model"
SCHEMA_DIR = REPO / "src" / "claude" / "schemas" / "spec"


@pytest.fixture
def spec_root(tmp_path: Path) -> Path:
    root = tmp_path / "specification"
    shutil.copytree(FIXTURE, root)
    shutil.rmtree(root / "projections", ignore_errors=True)
    return root


def problems_of(root: Path) -> list[str]:
    nodes, problems = spec.collect(root, spec.contracts())
    return problems + spec.cross_problems(nodes, root)


def rewrite(root: Path, relative: str, mutate) -> None:
    """Parse one file's frontmatter, let the test break it, and write it back."""
    path = root / relative
    text = path.read_text(encoding="utf-8")
    match = spec.FENCE.match(text)
    front = yaml.safe_load(match.group(1))
    mutate(front)
    path.write_text("---\n" + yaml.safe_dump(front, sort_keys=False)
                    + "---\n" + text[match.end():], encoding="utf-8")


def hits(problems: list[str], fragment: str) -> list[str]:
    return [p for p in problems if fragment in p]


# ------------------------------------------------------------------ the floor


def test_the_fixture_is_sound(spec_root):
    assert problems_of(spec_root) == []


def test_a_context_with_no_element_is_refused(spec_root):
    (spec_root / "domain/monitoring/alert.md").unlink()
    assert hits(problems_of(spec_root), "holds no element")


def test_a_context_with_no_descriptor_is_refused(spec_root):
    (spec_root / "domain/monitoring/_context.md").unlink()
    assert hits(problems_of(spec_root), "carries no _context.md")


def test_a_missing_decision_log_is_refused(spec_root):
    (spec_root / "decision-log.md").unlink()
    assert hits(problems_of(spec_root), "decision-log.md is missing")


# ------------------------------------------------- decide-and-disclose (SPEC-001)


def test_a_provenance_meta_field_is_refused_by_name(spec_root):
    rewrite(spec_root, "domain/troubleshooting/case.md",
            lambda f: f.update(gaps=[{"field": "attributes", "why": "old style"}]))
    found = hits(problems_of(spec_root), "provenance meta-field")
    assert found and "decision log" in found[0]


def test_a_log_entry_locating_a_missing_file_is_refused(spec_root):
    rewrite(spec_root, "decision-log.md",
            lambda f: f["entries"].append({
                "location": "domain/troubleshooting/ghost.md", "field": "type",
                "unstated": "x", "decided": "y", "why": "z"}))
    assert hits(problems_of(spec_root), "which the specification does not hold (SPEC-001 R9)")


def test_a_log_entry_locating_a_missing_field_is_refused(spec_root):
    rewrite(spec_root, "decision-log.md",
            lambda f: f["entries"].append({
                "location": "domain/troubleshooting/case.md", "field": "values.open",
                "unstated": "x", "decided": "y", "why": "z"}))
    assert hits(problems_of(spec_root), "declares no `values`")


# ------------------------------------------------------ one home per fact (SPEC-002)


def test_an_attribute_pointing_at_an_entity_is_refused(spec_root):
    rewrite(spec_root, "domain/troubleshooting/case.md",
            lambda f: f["attributes"].append({"name": "work", "type": "investigation"}))
    assert hits(problems_of(spec_root), "a relationship, never an attribute")


def test_a_relationship_pointing_at_a_value_is_refused(spec_root):
    rewrite(spec_root, "domain/troubleshooting/case.md",
            lambda f: f["relationships"].append(
                {"target": "case-id", "type": "association", "cardinality": "1"}))
    assert hits(problems_of(spec_root), "an attribute, never a relationship")


def test_a_dangling_reference_is_refused(spec_root):
    rewrite(spec_root, "domain/troubleshooting/case.md",
            lambda f: f["attributes"].append({"name": "severity", "type": "severity-level"}))
    assert hits(problems_of(spec_root), "which the specification does not hold")


def test_composition_crossing_an_aggregate_is_refused(spec_root):
    rewrite(spec_root, "domain/monitoring/alert.md",
            lambda f: f.update(relationships=[{
                "target": "domain/troubleshooting/investigation",
                "type": "composition", "cardinality": "1"}]))
    assert hits(problems_of(spec_root), "composition never crosses an aggregate boundary")


def test_two_edges_to_one_target_without_roles_are_refused(spec_root):
    rewrite(spec_root, "domain/troubleshooting/case.md",
            lambda f: f["relationships"].append(
                {"target": "resolution", "type": "association", "cardinality": "0..1"}))
    assert hits(problems_of(spec_root), "not all carry `role`")


def test_an_unreachable_element_is_refused(spec_root):
    (spec_root / "domain/troubleshooting/severity.md").write_text(
        "---\ntype: value-object\nattributes:\n  - name: value\n    type: string\n---\n\n"
        "## Description\n\nOrphaned on purpose.\n\n## Responsibility\n\nNone.\n",
        encoding="utf-8")
    assert hits(problems_of(spec_root), "answering no comprehension question does not exist")


def test_a_display_that_does_not_reduce_to_the_slug_is_refused(spec_root):
    rewrite(spec_root, "domain/troubleshooting/case.md",
            lambda f: f.update(display="Ticket"))
    assert hits(problems_of(spec_root), "not to the slug `case`")
    assert spec.reduce_display("ISBNCode") == "isbn-code"


# ------------------------------------------------------------- rules (SPEC-003)


def test_an_invariant_crossing_a_boundary_is_refused(spec_root):
    rewrite(spec_root, "rules/troubleshooting/hypothesis-requires-evidence.md",
            lambda f: f["constrains"].append("domain/monitoring/alert"))
    assert hits(problems_of(spec_root), "an invariant constrains inside one aggregate")


def test_a_crossing_policy_without_consistency_is_refused(spec_root):
    rewrite(spec_root, "rules/troubleshooting/alert-opens-case.md",
            lambda f: f.pop("consistency"))
    assert hits(problems_of(spec_root), "declares no consistency")


def test_a_crossing_policy_demanding_immediate_is_refused(spec_root):
    rewrite(spec_root, "rules/troubleshooting/alert-opens-case.md",
            lambda f: f.update(consistency="immediate"))
    assert hits(problems_of(spec_root), "a boundary redrawn, not a rule")


def test_an_uncovered_state_trigger_pairing_is_refused(spec_root):
    rewrite(spec_root, "rules/troubleshooting/case-transitions.md",
            lambda f: f.update(rejections=f["rejections"][1:]))
    found = hits(problems_of(spec_root), "no transition and no rejection")
    assert found and "`open`" in found[0] and "`resolve`" in found[0]


def test_a_second_state_machine_for_one_subject_is_refused(spec_root):
    source = spec_root / "rules/troubleshooting/case-transitions.md"
    (spec_root / "rules/troubleshooting/case-flow.md").write_text(
        source.read_text(encoding="utf-8"), encoding="utf-8")
    assert hits(problems_of(spec_root), "an aggregate root has one state machine")


# -------------------------------------------------------- contracts (SPEC-003)


def test_the_system_namespace_is_reserved_for_capabilities(spec_root):
    rewrite(spec_root, "contracts/system/troubleshoot-customer-problem.md",
            lambda f: f.update(type="domain-event", direction="published",
                               payload="domain/troubleshooting/case"))
    assert hits(problems_of(spec_root), "holds capabilities only")


def test_a_capability_outside_the_system_namespace_is_refused(spec_root):
    (spec_root / "contracts/troubleshooting/full-diagnosis.md").write_text(
        "---\ntype: capability\n---\n\n## Description\n\nMisplaced.\n", encoding="utf-8")
    assert hits(problems_of(spec_root), "lives only under contracts/system/")


def test_a_context_named_system_is_refused(spec_root):
    target = spec_root / "domain/system"
    target.mkdir()
    (target / "_context.md").write_text(
        "---\nstrategic: generic\n---\n\n## Description\n\nX.\n\n## Responsibility\n\nX.\n",
        encoding="utf-8")
    assert hits(problems_of(spec_root), "reserved namespace")


def test_a_consumed_contract_without_upstream_is_refused(spec_root):
    rewrite(spec_root, "contracts/troubleshooting/alert-raised.md",
            lambda f: f.pop("upstream"))
    assert hits(problems_of(spec_root), "'upstream' is a required property")


def test_an_upstream_that_is_not_published_is_refused(spec_root):
    rewrite(spec_root, "contracts/troubleshooting/alert-raised.md",
            lambda f: f.update(upstream="contracts/troubleshooting/case-resolved"))
    problems = problems_of(spec_root)
    assert hits(problems, "does not consume its own contract")
    rewrite(spec_root, "contracts/monitoring/alert-raised.md",
            lambda f: f.update(direction="consumed",
                               upstream="contracts/troubleshooting/case-resolved"))
    rewrite(spec_root, "contracts/troubleshooting/alert-raised.md",
            lambda f: f.update(upstream="contracts/monitoring/alert-raised"))
    assert hits(problems_of(spec_root), "whose direction is not published")


# ------------------------------------------------------------------ projections


def test_projections_are_deterministic(spec_root):
    nodes, problems = spec.collect(spec_root, spec.contracts())
    assert problems + spec.cross_problems(nodes, spec_root) == []
    assert spec.project(nodes) == spec.project(nodes)


def test_every_projected_fact_traces_to_a_file(spec_root):
    """Removing the one consumed contract removes the map's edge and declares separate ways."""
    nodes, _ = spec.collect(spec_root, spec.contracts())
    before = spec.project(nodes)["context-map.mmd"]
    assert "monitoring -->|alert-raised| troubleshooting" in before
    (spec_root / "contracts/troubleshooting/alert-raised.md").unlink()
    nodes, _ = spec.collect(spec_root, spec.contracts())
    after = spec.project(nodes)["context-map.mmd"]
    assert "-->" not in after
    assert "separate ways: monitoring and troubleshooting" in after


def test_the_class_diagram_keeps_values_outside_the_aggregate(spec_root):
    nodes, _ = spec.collect(spec_root, spec.contracts())
    diagram = spec.project(nodes)["class-diagram-troubleshooting.mmd"]
    boundary = diagram[diagram.index("namespace CaseAggregate"):diagram.index("\n    }\n")]
    assert "class Investigation" in boundary
    assert "class Evidence" not in boundary
    assert 'Case "1" *-- "1" Investigation' in diagram


def test_the_state_diagram_derives_from_the_state_machine(spec_root):
    nodes, _ = spec.collect(spec_root, spec.contracts())
    diagram = spec.project(nodes)["state-troubleshooting-case.mmd"]
    assert "[*] --> open" in diagram
    assert "open --> investigating : startInvestigation" in diagram
    assert "resolved --> [*]" in diagram


def test_the_capability_map_derives_from_scenarios(spec_root):
    nodes, _ = spec.collect(spec_root, spec.contracts())
    diagram = spec.project(nodes)["capability-map.mmd"]
    assert "troubleshoot_customer_problem --> monitoring" in diagram
    assert "troubleshoot_customer_problem --> troubleshooting" in diagram


# ------------------------------------------------------------ the CLI contract


def test_the_cli_validates_and_projects(spec_root):
    run = subprocess.run(
        [sys.executable, "-B", str(REPO / "src/claude/bin/spec.py"),
         "--project", str(spec_root)],
        capture_output=True, text=True)
    assert run.returncode == 0, run.stdout + run.stderr
    assert "specification sound" in run.stdout
    assert (spec_root / "projections/overview.md").is_file()

    (spec_root / "decision-log.md").unlink()
    run = subprocess.run(
        [sys.executable, "-B", str(REPO / "src/claude/bin/spec.py"), str(spec_root)],
        capture_output=True, text=True)
    assert run.returncode == 1
    assert "decision-log.md is missing" in run.stdout


# ------------------------------------------------------- the schemas' own examples


def test_every_schema_example_satisfies_its_schema():
    from jsonschema import Draft202012Validator
    for path in sorted(SCHEMA_DIR.glob("*.json")):
        schema = json.loads(path.read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)
        examples = list(schema.get("examples", []))
        for branch in schema.get("allOf", []):
            examples += branch.get("then", {}).get("examples", [])
        assert examples, f"{path.name} demonstrates nothing"
        for example in examples:
            problems = [e.message for e in validator.iter_errors(example)]
            assert problems == [], f"{path.name}: {problems}"
            assert yaml.safe_load(yaml.safe_dump(example)) == example
