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


def test_a_capability_is_a_valid_upstream_despite_declaring_no_direction(spec_root):
    """A capability's schema branch admits only `type` and `display` — it is always published
    by SPEC-003's own description, never by an explicit field. Before this held, a consumed
    contract could never name a capability upstream (SKILL.md's own "a third-party system is an
    upstream capability" was unreachable), because the missing field read as "not published"."""
    rewrite(spec_root, "contracts/troubleshooting/alert-raised.md",
            lambda f: f.update(upstream="contracts/system/troubleshoot-customer-problem"))
    assert hits(problems_of(spec_root), "whose direction is not published") == []


# ------------------------------------------------------------------ projections


def test_projections_are_deterministic(spec_root):
    nodes, problems = spec.collect(spec_root, spec.contracts())
    assert problems + spec.cross_problems(nodes, spec_root) == []
    assert spec.project(nodes) == spec.project(nodes)


def test_every_projected_fact_traces_to_a_file(spec_root):
    """Removing the one consumed contract removes the map's edge and declares separate ways."""
    nodes, _ = spec.collect(spec_root, spec.contracts())
    before = spec.project(nodes)["context-map.mmd"]
    assert "monitoring -->|alert-raised (adopted)| troubleshooting" in before
    (spec_root / "contracts/troubleshooting/alert-raised.md").unlink()
    nodes, _ = spec.collect(spec_root, spec.contracts())
    after = spec.project(nodes)["context-map.mmd"]
    assert "-->" not in after
    assert "separate ways: monitoring and troubleshooting" in after


def test_the_context_map_reads_adoption_from_the_payload(spec_root):
    """The one strategic fact a consumed contract carries and nothing declares: whose model
    crosses the boundary. The fixture's consumer names the upstream's own element as its
    payload, so it adopts that model; renamed to an element of its own, it translates. Read from
    the payload alone, because a field stating it would be a second home for what the payload
    already says."""
    nodes, _ = spec.collect(spec_root, spec.contracts())
    assert "monitoring -->|alert-raised (adopted)| troubleshooting" \
        in spec.project(nodes)["context-map.mmd"]
    rewrite(spec_root, "contracts/troubleshooting/alert-raised.md",
            lambda f: f.update(payload="domain/troubleshooting/case"))
    nodes, _ = spec.collect(spec_root, spec.contracts())
    assert "monitoring -->|alert-raised (translated)| troubleshooting" \
        in spec.project(nodes)["context-map.mmd"]


def test_a_model_referenced_across_contexts_reaches_the_context_map(spec_root):
    """An element naming another context's element by identity is a kernel the two share, and
    no contract declares it — so the map draws it apart from consumption, and a pair joined only
    by a shared model has not gone separate ways."""
    rewrite(spec_root, "domain/troubleshooting/case.md",
            lambda f: f.update(relationships=(f.get("relationships") or []) + [
                {"target": "domain/monitoring/alert", "type": "association",
                 "cardinality": "1", "role": "opened-by"}]))
    (spec_root / "contracts/troubleshooting/alert-raised.md").unlink()
    nodes, _ = spec.collect(spec_root, spec.contracts())
    diagram = spec.project(nodes)["context-map.mmd"]
    assert "troubleshooting ==>|model: alert| monitoring" in diagram
    assert "-->" not in diagram, "a shared model is not consumption"
    assert "separate ways" not in diagram


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


def test_an_unmapped_capability_is_said_rather_than_silent(spec_root):
    """Three floating nodes read as a finished map; what they mean is that nobody wrote the
    scenario and nothing consumes the capability — the same absence the context map already
    declares as separate ways instead of leaving blank."""
    (spec_root / "scenarios/system/troubleshoot-from-alert.md").unlink()
    nodes, _ = spec.collect(spec_root, spec.contracts())
    files = spec.project(nodes)
    assert ("%% unmapped: no scenario names troubleshoot-customer-problem and no contract "
            "consumes it") in files["capability-map.mmd"]
    assert "unmapped: no scenario names it and no contract consumes it" in files["overview.md"]


def test_a_consumed_capability_maps_without_a_scenario(spec_root):
    """The second derivation source: a consumed contract naming the capability upstream is
    consumption the files already declare, and the map draws it dashed — apart from the solid
    edge a scenario's orchestration earns — with no scenario needed."""
    rewrite(spec_root, "contracts/troubleshooting/alert-raised.md",
            lambda f: f.update(upstream="contracts/system/troubleshoot-customer-problem"))
    (spec_root / "scenarios/system/troubleshoot-from-alert.md").unlink()
    nodes, _ = spec.collect(spec_root, spec.contracts())
    files = spec.project(nodes)
    assert "troubleshoot_customer_problem -.-> troubleshooting" in files["capability-map.mmd"]
    assert "unmapped" not in files["capability-map.mmd"]
    assert "consumed by troubleshooting" in files["overview.md"]


def test_a_foreign_class_is_marked_with_its_home_context(spec_root):
    """A class referenced across contexts used to reach the diagram only through an edge or an
    attribute's type, which Mermaid autocreates as a bare box — a reader of one diagram could
    not tell the foreign name from a local one. The declared block says whose it is, and stays
    empty because the attributes live in the owning context's diagram."""
    rewrite(spec_root, "domain/troubleshooting/case.md",
            lambda f: f.update(relationships=(f.get("relationships") or []) + [
                {"target": "domain/monitoring/alert", "type": "association",
                 "cardinality": "1", "role": "opened-by"}]))
    nodes, _ = spec.collect(spec_root, spec.contracts())
    diagram = spec.project(nodes)["class-diagram-troubleshooting.mmd"]
    # The exact match is the whole point: opening line, stereotype, closing brace and nothing
    # between — a foreign block restates no attribute, because they live in the owning diagram.
    assert "class Alert {\n        <<external: monitoring>>\n    }" in diagram
    home = spec.project(nodes)["class-diagram-monitoring.mmd"]
    assert "<<external" not in home, "the owning context's diagram declares it in full"


def test_the_overview_counts_each_aggregate(spec_root):
    """A boundary's size is the first thing to weigh about it, and it was readable only by
    opening one class diagram per context. Counted and said, never held to a threshold: an
    aggregate legitimately large would be refused for a number nobody measured."""
    nodes, _ = spec.collect(spec_root, spec.contracts())
    overview = spec.project(nodes)["overview.md"]
    assert "## Aggregates" in overview
    assert "- troubleshooting/case — 3 entity(ies) inside, 4 attribute(s) on the root" in overview
    assert "- monitoring/alert — 0 entity(ies) inside, 2 attribute(s) on the root" in overview


def test_an_offered_contract_reaches_the_context_map(spec_root):
    """A published contract nothing inside consumes is the system's own surface, and the map
    used to be silent about every such door. Dashed, so the outward offer never reads as the
    internal consumption the solid edges state."""
    nodes, _ = spec.collect(spec_root, spec.contracts())
    diagram = spec.project(nodes)["context-map.mmd"]
    assert 'troubleshooting -.->|case-resolved| outside' in diagram
    assert "monitoring -.->" not in diagram, \
        "a published contract someone consumes is an edge between contexts, never an offer"
    assert "troubleshoot-customer-problem| outside" not in diagram, \
        "a capability lives in the system context and the capability map is its home"


# ------------------------------------------------------------ the CLI contract


def test_every_node_carries_a_digest_matching_its_bytes(spec_root):
    import hashlib
    nodes, _ = spec.collect(spec_root, spec.contracts())
    for identity, node in nodes.items():
        path = spec_root / f"{identity}.md"
        expected = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
        assert node["digest"] == expected, identity


def test_a_changed_node_changes_only_its_own_digest(spec_root):
    nodes_before, _ = spec.collect(spec_root, spec.contracts())
    (spec_root / "domain/troubleshooting/case.md").write_text(
        (spec_root / "domain/troubleshooting/case.md").read_text(encoding="utf-8") + "\n",
        encoding="utf-8")
    nodes_after, _ = spec.collect(spec_root, spec.contracts())
    for identity in nodes_before:
        if identity == "domain/troubleshooting/case":
            assert nodes_after[identity]["digest"] != nodes_before[identity]["digest"]
        else:
            assert nodes_after[identity]["digest"] == nodes_before[identity]["digest"]


def test_the_cli_prints_digests_sorted_by_identity(spec_root):
    run = subprocess.run(
        [sys.executable, "-B", str(REPO / "src/claude/bin/spec.py"),
         "--digest", str(spec_root)],
        capture_output=True, text=True)
    assert run.returncode == 0, run.stdout + run.stderr
    lines = [line for line in run.stdout.splitlines() if "  sha256:" in line]
    identities = [line.split("  ")[0] for line in lines]
    assert identities == sorted(identities)
    assert "domain/troubleshooting/case  sha256:" in run.stdout
    for line in lines:
        identity, digest = line.split("  ")
        assert digest.startswith("sha256:") and len(digest) == len("sha256:") + 64


def test_digests_are_refused_over_an_unsound_specification(spec_root):
    (spec_root / "decision-log.md").unlink()
    run = subprocess.run(
        [sys.executable, "-B", str(REPO / "src/claude/bin/spec.py"),
         "--digest", str(spec_root)],
        capture_output=True, text=True)
    assert run.returncode == 1
    assert "digests are not sound" in run.stdout
    assert "sha256:" not in run.stdout


def test_project_and_digest_are_mutually_exclusive(spec_root):
    run = subprocess.run(
        [sys.executable, "-B", str(REPO / "src/claude/bin/spec.py"),
         "--project", "--digest", str(spec_root)],
        capture_output=True, text=True)
    assert run.returncode == spec.CANNOT_RUN
    assert "mutually exclusive" in run.stderr


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


# --------------------------------------------------------------------- --node


def run_node(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(REPO / "src/claude/bin/spec.py"), *args],
                          capture_output=True, text=True)


def test_node_mode_passes_a_sound_file_on_its_own(spec_root):
    done = run_node("--node", "domain/troubleshooting/case.md", str(spec_root))
    assert done.returncode == 0, done.stdout + done.stderr
    assert "sound on its own" in done.stdout
    assert "Cross-node checks did not run" in done.stdout


def test_node_mode_still_refuses_a_malformed_file(spec_root):
    path = spec_root / "domain/troubleshooting/case.md"
    path.write_text(path.read_text(encoding="utf-8").replace("type: aggregate-root", "type: bogus"),
                    encoding="utf-8")
    done = run_node("--node", "domain/troubleshooting/case.md", str(spec_root))
    assert done.returncode == 1
    assert "bogus" in done.stdout


def test_node_mode_ignores_a_dangling_reference(spec_root):
    """A reference that only cross-node checks resolve does not fail a file checked alone —
    the same discipline graph.py, plan.py and deliver.py already hold their --node modes to."""
    path = spec_root / "domain/troubleshooting/case.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("attributes:", "attributes:\n  - name: nothing\n"
                                 "    type: does-not-exist\n", 1), encoding="utf-8")
    done = run_node("--node", "domain/troubleshooting/case.md", str(spec_root))
    assert done.returncode == 0, done.stdout + done.stderr


def test_node_mode_reports_no_identity_for_a_path_outside_the_layout(spec_root):
    (spec_root / "stray.md").write_text("---\ntype: value-object\n---\n\n## Description\n\nX.\n",
                                        encoding="utf-8")
    done = run_node("--node", "stray.md", str(spec_root))
    assert done.returncode == 1
    assert "the path computes to no identity" in done.stdout


def test_node_mode_and_project_are_mutually_exclusive(spec_root):
    done = run_node("--node", "domain/troubleshooting/case.md", "--project", str(spec_root))
    assert done.returncode == spec.CANNOT_RUN
    assert "facts about the whole specification" in done.stderr


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


def test_a_transition_out_of_a_terminal_state_is_refused(spec_root):
    """`terminal` is defined as states that accept no further trigger, and that declaration is
    the whole of what exempts them from the totality check. A transition leaving one contradicted
    the declaration that exempted it, validated clean, and made the projected diagram draw both
    `resolved --> [*]` and `resolved --> open`."""
    rewrite(spec_root, "rules/troubleshooting/case-transitions.md",
            lambda front: front["transitions"].insert(
                0, {"from": "resolved", "trigger": "reopen", "to": "open"}))
    found = hits(problems_of(spec_root), "accepts no further trigger")
    assert found, "a transition out of a declared terminal state was accepted"


def test_a_rejection_from_a_terminal_state_is_refused(spec_root):
    """The same rule from the other side: a terminal state decides no pairing, so it declares no
    rejection either. Without this the transition check above could be satisfied by moving the
    pairing into `rejections`."""
    rewrite(spec_root, "rules/troubleshooting/case-transitions.md",
            lambda front: front.setdefault("rejections", []).insert(
                0, {"from": "cancelled", "trigger": "reopen", "refusal": "a cancelled case "
                    "does not reopen"}))
    found = hits(problems_of(spec_root), "accepts no further trigger")
    assert found, "a rejection from a declared terminal state was accepted"


# ------------------------------------------------------------------ the parse funnel


def test_an_unquoted_colon_in_frontmatter_names_its_own_fix(tmp_path):
    """Every node file in this framework parses through `parse_node`, so the hint lands once and
    reaches spec.py, plan.py and deliver.py alike. PyYAML's `mapping values are not allowed here`
    names the grammar and not the fix; three refusals in one consumer window were this error
    worked out from the grammar each time."""
    path = tmp_path / "node.md"
    path.write_text("---\ntitle: Sound\nsummary: One rule: the colon breaks it\n---\n"
                    "## Description\nProse.\n", encoding="utf-8")
    front, _, problem = spec.parse_node(path)
    assert front is None
    assert "does not parse" in problem
    assert "quote the whole string" in problem
    assert "yaml.safe_dump" in problem


def test_a_parse_failure_that_is_not_the_colon_carries_no_hint(tmp_path):
    """The hint is for one error; stapled to every parse failure it would misdiagnose the rest."""
    path = tmp_path / "node.md"
    path.write_text("---\ntitle: [unclosed\n---\n## Description\nProse.\n", encoding="utf-8")
    front, _, problem = spec.parse_node(path)
    assert front is None
    assert "does not parse" in problem
    assert "yaml.safe_dump" not in problem


# -------------------------------------------------------------------- --impact


def test_impact_closes_one_hop_in_both_directions(spec_root):
    """The closure a plan's situate step and an analysis both owe, read rather than assembled by
    hand. Outward is what the node declares; inward is what declares one at it — including the
    back-references a hand-run grep finds one identity at a time."""
    done = run_node("--impact", "domain/troubleshooting/case", str(spec_root))
    assert done.returncode == 0, done.stderr
    assert "one hop, both directions" in done.stdout
    assert "declares  -> domain/troubleshooting/case-status" in done.stdout
    assert "named by  <- rules/troubleshooting/case-transitions" in done.stdout
    assert "named by  <- domain/troubleshooting/investigation" in done.stdout, \
        "an aggregate back-reference is an edge, and the closure that misses it under-reports"
    assert str(spec_root / "rules/troubleshooting/case-transitions.md") in done.stdout, \
        "the read set is printed as paths, which is what the delegations are handed"


def test_impact_carries_the_decision_log(spec_root):
    """A log entry locating a node is a reverse link the grep this replaces finds today, and the
    binder is told to consult the log before settling a claim of succession. A closure that
    dropped it would be narrower than the procedure it replaces, silently."""
    done = run_node("--impact", "domain/troubleshooting/evidence", str(spec_root))
    assert done.returncode == 0, done.stderr
    assert "named by  <- decision-log" in done.stdout
    assert str(spec_root / "decision-log.md") in done.stdout


def test_impact_answers_over_a_specification_with_problems(spec_root):
    """A reading, never a derived artifact — `/analyse` closes an impact set while it is still
    authoring the files, so a closure refused until the last file parses arrives after the
    decisions it was for. What did not resolve is marked, and the problems are named."""
    rewrite(spec_root, "rules/troubleshooting/case-transitions.md",
            lambda front: front.update(subject="domain/troubleshooting/nonexistent"))
    done = run_node("--impact", "rules/troubleshooting/case-transitions", str(spec_root))
    assert done.returncode == 0, done.stderr
    assert "read over a specification with" in done.stdout
    assert "the specification does not hold this" in done.stdout
    assert "domain/troubleshooting/nonexistent" in done.stdout


def test_impact_reads_the_same_edges_the_validator_checks(spec_root):
    """The canary. Two readings of one specification — the check and the report — walk the same
    `landing`, so a field that gains a reference is seen by both or by neither. This fails if the
    report ever grows its own list of which fields carry a reference."""
    nodes, _ = spec.collect(spec_root, spec.contracts())
    seen: list[tuple[str, str, str]] = []
    spec.cross_problems(nodes, spec_root,
                        lambda owner, at, target, resolved: seen.append((owner, at, target)))
    every = {(owner, target) for owner, _, target in seen}
    assert ("rules/troubleshooting/case-transitions", "domain/troubleshooting/case") in every
    assert ("decision-log", "domain/troubleshooting/evidence") in every
    outward, inward, _ = spec.impact_of(nodes, spec_root, ["domain/troubleshooting/case"])
    reported = {(owner, target) for owner, edges in outward.items()
                for _, target, _ in edges}
    assert reported == every, \
        "the report walks edges the validator does not, or misses edges it checks; both are the " \
        "same walk and there is no third place to keep them agreeing"


def test_impact_refuses_an_identity_that_names_no_file(spec_root):
    done = run_node("--impact", "domain/troubleshooting/nope", str(spec_root))
    assert done.returncode == 2
    assert "names no file" in done.stderr


def test_impact_stands_beside_no_other_flag(spec_root):
    """`--project` and `--digest` are derived artifacts refused over a broken specification;
    `--impact` answers over one. Letting them share an invocation would make one of the two
    answers wrong."""
    done = run_node("--impact", "domain/troubleshooting/case", "--digest", str(spec_root))
    assert done.returncode == 2
    assert "derives nothing" in done.stderr
