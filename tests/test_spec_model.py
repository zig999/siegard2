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
from jsonschema import Draft202012Validator

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


def test_a_root_without_logs_is_sound(spec_root):
    """SPEC-003 R5: a log is «present where a decision was made, absent where none was». A root
    whose material answered everything holds no log, and that is not a problem."""
    for log in spec_root.rglob("*.log.md"):
        log.unlink()
    assert problems_of(spec_root) == []
    done = run_node(str(spec_root))
    assert done.returncode == 0 and "0 decision(s) disclosed" in done.stdout


def test_a_root_decision_log_file_is_refused(spec_root):
    """The one-file-per-root log is no longer a node: a leftover `decision-log.md` computes to
    no identity, which is the signal a consumer has not migrated."""
    (spec_root / "decision-log.md").write_text("---\nentries: []\n---\n", encoding="utf-8")
    assert hits(problems_of(spec_root), "decision-log.md: the path computes to no identity")


# ------------------------------------------------- decide-and-disclose (SPEC-001)


def test_a_provenance_meta_field_is_refused_by_name(spec_root):
    rewrite(spec_root, "domain/troubleshooting/case.md",
            lambda f: f.update(gaps=[{"field": "attributes", "why": "old style"}]))
    found = hits(problems_of(spec_root), "provenance meta-field")
    assert found and "decision log" in found[0]


CASE_LOG = "domain/troubleshooting/case.log.md"
GHOST_LOG = "domain/troubleshooting/ghost.log.md"
DECIDED = {"field": "type", "unstated": "x", "decided": "y", "why": "z"}
RETIRED = {"field": "type", "retired": "held nowhere: the element left the specification"}
READ_ENTRY = {"field": "type", "unstated": "No node said what class a case is.",
              "found": "work/x/intake/scope.md: a case is the unit an operator opens and closes."}


def log_beside(root: Path, relative: str, entries: list[dict]) -> None:
    """Write a decision log holding exactly these entries, the way the writer lays them out."""
    blocks = "".join(yaml.safe_dump([e], sort_keys=False, width=float("inf")) for e in entries)
    (root / relative).write_text(f"---\nentries:\n{blocks}---\n", encoding="utf-8")


def log_problems(root: Path) -> list[str]:
    return [p for p in problems_of(root) if ".log" in p]


def test_a_log_without_its_node_is_refused(spec_root):
    """SPEC-001 R9: «A log whose node does not exist fails validation unless its last entry
    retires a field» — a log beside nothing, still deciding, is a decision about a node the
    specification does not hold."""
    log_beside(spec_root, GHOST_LOG, [dict(DECIDED)])
    found = hits(problems_of(spec_root), "sits beside no node domain/troubleshooting/ghost")
    assert found and "retires a field" in found[0]


def test_a_log_entry_naming_a_field_the_node_lacks_is_refused(spec_root):
    log_beside(spec_root, CASE_LOG, [{**DECIDED, "field": "values.open"}])
    found = hits(problems_of(spec_root), "which domain/troubleshooting/case does not declare")
    assert found and "`values.open`" in found[0]


def test_a_log_with_a_body_is_refused(spec_root):
    """The file is frontmatter alone. An entry written past the closing fence is read by nothing,
    and a validator that ignored the body would call a log sound while under-counting it."""
    path = spec_root / CASE_LOG
    log_beside(spec_root, CASE_LOG, [dict(DECIDED)])
    path.write_text(path.read_text(encoding="utf-8")
                    + "- field: type\n  unstated: lost\n  decided: lost\n  why: lost\n",
                    encoding="utf-8")
    found = hits(problems_of(spec_root), "carries text after its frontmatter fence")
    assert found and found[0].startswith("domain/troubleshooting/case.log:")
    single = run_node("--node", CASE_LOG, str(spec_root))
    assert single.returncode == 1 and "after its frontmatter fence" in single.stdout


def test_a_log_beside_a_context_descriptor_validates(spec_root):
    log_beside(spec_root, "domain/troubleshooting/_context.log.md",
               [{**DECIDED, "field": "strategic"}])
    assert log_problems(spec_root) == []
    done = run_node(str(spec_root))
    assert done.returncode == 0 and "3 decision(s) disclosed" in done.stdout


def test_a_log_stem_that_is_no_node_computes_to_nothing(spec_root):
    """`<slug>.log.md` is the log of `<slug>.md` and of nothing else: a log beside a path no
    class owns is not a node of any class, and the dot keeps a slug from ever reading as a log."""
    assert spec.classify(Path("domain/troubleshooting/case.log.md")) == \
        ("log", "troubleshooting", "case")
    assert spec.classify(Path("constraints/asynchronous-events.log.md")) == \
        ("log", None, "asynchronous-events")
    assert spec.classify(Path("domain/troubleshooting/_context.log.md")) == \
        ("log", "troubleshooting", "troubleshooting")
    assert spec.classify(Path("decision-log.md")) is None
    assert spec.classify(Path("nowhere/case.log.md")) is None
    assert spec.classify(Path("domain/troubleshooting/case.log.log.md")) is None


def test_a_log_entry_recorded_as_read_validates(spec_root):
    """SPEC-001 R9: a fact a planning step read from the intake is recorded as read — field,
    unstated and where it was found — with no value and no `why`. The field still resolves
    exactly as a decided entry's does."""
    log_beside(spec_root, CASE_LOG, [dict(READ_ENTRY)])
    assert log_problems(spec_root) == []


def test_a_read_entry_carrying_a_decided_value_is_refused(spec_root):
    """Both shapes on one entry disclose two provenances for one fact. The schema refuses it and
    the validator names it, so the report says which keys collided rather than which branch of
    a conditional failed."""
    log_beside(spec_root, CASE_LOG, [{**READ_ENTRY, "decided": "aggregate-root"}])
    found = hits(problems_of(spec_root), "carries `found` beside decided")
    assert found and "decides no value" in found[0]
    validator = Draft202012Validator(json.loads((SCHEMA_DIR / "decision-log.json").read_text()))
    assert list(validator.iter_errors({"entries": [{**READ_ENTRY, "why": "because"}]}))


def test_a_decided_entry_without_why_is_refused(spec_root):
    log_beside(spec_root, CASE_LOG, [{"field": "type", "unstated": "x", "decided": "y"}])
    assert hits(problems_of(spec_root), "'why' is a required property")


def test_an_entry_carrying_a_location_is_refused(spec_root):
    """The log sits beside the node it discloses, so an entry naming a file would name it twice
    and could disagree with where it sits; the schema admits no `location`."""
    log_beside(spec_root, CASE_LOG, [{**DECIDED, "location": "domain/troubleshooting/case.md"}])
    assert hits(problems_of(spec_root), "'location' was unexpected")


def test_the_sound_line_counts_read_facts_apart_from_decisions(spec_root):
    """A read entry chose nothing; counted as a decision it would report a choice nobody made.
    A log holding decisions alone prints exactly as before, so no consumer's quoted output moves."""
    before = run_node(str(spec_root))
    assert before.returncode == 0 and "2 decision(s) disclosed" in before.stdout
    assert "recorded as read" not in before.stdout
    log_beside(spec_root, CASE_LOG, [dict(READ_ENTRY)])
    done = run_node(str(spec_root))
    assert done.returncode == 0, done.stdout + done.stderr
    assert "2 decision(s) disclosed, 1 fact(s) recorded as read" in done.stdout


def test_project_writes_no_decisions_by_node_and_removes_a_stale_one(spec_root):
    """The logs beside the nodes are the grouping a `decisions-by-node` projection used to
    derive; a derived copy of what the tree already states is a second home for one fact."""
    (spec_root / "projections").mkdir()
    (spec_root / "projections" / "decisions-by-node.md").write_text("stale\n", encoding="utf-8")
    done = run_node("--project", str(spec_root))
    assert done.returncode == 0, done.stdout + done.stderr
    assert not (spec_root / "projections" / "decisions-by-node.md").exists()
    overview = (spec_root / "projections" / "overview.md").read_text(encoding="utf-8")
    assert "2 decision(s) disclosed in the decision logs." in overview


def test_a_tombstone_log_without_its_node_is_sound(spec_root):
    """SPEC-001 R9: «An entry is never edited or removed»; a node that left is answered by an
    entry retiring the field, and its log stands beside nothing as the record of where the fact
    went."""
    log_beside(spec_root, GHOST_LOG, [dict(DECIDED), dict(RETIRED)])
    assert log_problems(spec_root) == []


def test_a_tombstone_log_must_retire_every_field_it_filled(spec_root):
    """SPEC-001 R9: an entry whose field does not resolve fails validation unless a later entry
    retires that field. A node that left resolves no field, so a log closing on one retirement
    while another field's decision stands unanswered is not a tombstone, it is a decision about
    a node the specification no longer holds."""
    other = {**DECIDED, "field": "attributes"}
    log_beside(spec_root, GHOST_LOG, [dict(DECIDED), other, dict(RETIRED)])
    found = hits(problems_of(spec_root), "entries[1] fills `attributes`")
    assert found and "still unanswered" in found[0]
    log_beside(spec_root, GHOST_LOG,
               [dict(DECIDED), other, dict(RETIRED), {"field": "attributes", "retired": "gone"}])
    assert log_problems(spec_root) == []


def test_a_field_a_later_entry_retires_may_stop_resolving(spec_root):
    entry = {**DECIDED, "field": "values.open"}
    retired = {"field": "values.open", "retired": "rules/troubleshooting/x.md statement"}
    log_beside(spec_root, CASE_LOG, [entry, retired])
    assert log_problems(spec_root) == []


def test_a_retirement_before_the_entry_retires_nothing(spec_root):
    """Only a later entry retires: an entry appended after a retirement of its field is a
    decision made about a node that must exist."""
    log_beside(spec_root, GHOST_LOG, [dict(RETIRED), dict(DECIDED)])
    found = problems_of(spec_root)
    assert hits(found, "which no earlier entry of this log filled")
    assert hits(found, "sits beside no node")


def test_a_retirement_of_a_field_no_entry_filled_is_refused(spec_root):
    log_beside(spec_root, CASE_LOG, [dict(RETIRED)])
    assert hits(problems_of(spec_root), "which no earlier entry of this log filled")


def test_a_retirement_carries_no_decided_value(spec_root):
    validator = Draft202012Validator(json.loads((SCHEMA_DIR / "decision-log.json").read_text()))
    assert list(validator.iter_errors({"entries": [{**RETIRED, "decided": "y"}]}))
    assert list(validator.iter_errors({"entries": [{**RETIRED, "unstated": "x"}]}))
    assert not list(validator.iter_errors({"entries": [dict(DECIDED), dict(RETIRED)]}))


def test_the_sound_line_counts_retirements_apart(spec_root):
    log_beside(spec_root, GHOST_LOG, [dict(DECIDED), dict(RETIRED)])
    done = run_node(str(spec_root))
    assert done.returncode == 0, done.stdout + done.stderr
    assert "3 decision(s) disclosed, 1 location(s) retired" in done.stdout


# ------------------------------------------------------ one home per fact (SPEC-002)


def test_an_attribute_pointing_at_an_entity_is_refused(spec_root):
    rewrite(spec_root, "domain/troubleshooting/case.md",
            lambda f: f["attributes"].append({"name": "work", "type": "investigation"}))
    assert hits(problems_of(spec_root), "is a relationship» (SPEC-002 R8), never an attribute")


def test_a_relationship_pointing_at_a_value_is_refused(spec_root):
    rewrite(spec_root, "domain/troubleshooting/case.md",
            lambda f: f["relationships"].append(
                {"target": "case-id", "type": "association", "cardinality": "1"}))
    assert hits(problems_of(spec_root), "is an attribute» (SPEC-002 R8), never a relationship")


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
    assert hits(problems_of(spec_root), "is bloat and fails validation» (SPEC-001 R6)")


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


DESK = "contracts/troubleshooting/case-desk.md"


def write_desk(root: Path, answers: list) -> None:
    """An api answering its operations — the fixture holds no api, and adding one to it would
    move every count the other suites read off the sound fixture."""
    front = {"type": "api", "direction": "published",
             "operations": ["resolve-case", "read-case"], "answers": answers}
    (root / DESK).write_text("---\n" + yaml.safe_dump(front, sort_keys=False)
                             + "---\n\n## Description\n\nThe desk operators work cases through.\n",
                             encoding="utf-8")


SOUND_ANSWERS = [
    {"operation": "resolve-case", "accepted": "HTTP 200 carrying the resolved case",
     "refusals": [{"rule": "rules/troubleshooting/hypothesis-requires-evidence",
                   "answer": "HTTP 422 reporting hypothesis-without-evidence"}]},
    {"operation": "read-case",
     "refusals": [{"when": "No case is held at the requested identity.",
                   "answer": "HTTP 404 reporting case-not-found"}]},
]


def test_an_api_declaring_answers_is_sound(spec_root):
    write_desk(spec_root, SOUND_ANSWERS)
    assert problems_of(spec_root) == []


def test_an_answer_to_an_undeclared_operation_is_refused(spec_root):
    write_desk(spec_root, [{"operation": "reopen-case", "accepted": "HTTP 200"}])
    assert hits(problems_of(spec_root), "answers `reopen-case`, which `operations` does not declare")


def test_an_operation_answered_twice_is_refused(spec_root):
    write_desk(spec_root, SOUND_ANSWERS + [{"operation": "read-case", "accepted": "HTTP 200"}])
    assert hits(problems_of(spec_root), "answers `read-case` a second time")


def test_a_refusal_naming_an_absent_rule_is_refused(spec_root):
    write_desk(spec_root, [{"operation": "resolve-case", "refusals": [
        {"rule": "rules/troubleshooting/case-needs-a-customer", "answer": "HTTP 422"}]}])
    assert hits(problems_of(spec_root),
                "names rules/troubleshooting/case-needs-a-customer, which the specification "
                "does not hold")


@pytest.mark.parametrize("refusal,message", [
    ({"rule": "rules/troubleshooting/hypothesis-requires-evidence",
      "when": "The hypothesis holds no evidence.", "answer": "HTTP 422"}, "is valid under each of"),
    ({"answer": "HTTP 422"}, "is not valid under any of the given schemas"),
])
def test_a_refusal_carries_exactly_one_of_rule_and_when(spec_root, refusal, message):
    write_desk(spec_root, [{"operation": "resolve-case", "refusals": [refusal]}])
    assert hits(problems_of(spec_root), f"answers.0.refusals.0: {refusal!r} {message}")


def test_one_rule_refused_twice_in_one_operation_is_refused(spec_root):
    refusal = {"rule": "rules/troubleshooting/hypothesis-requires-evidence", "answer": "HTTP 422"}
    write_desk(spec_root, [{"operation": "resolve-case", "refusals": [refusal, dict(refusal)]}])
    assert hits(problems_of(spec_root), "a second time; one condition takes one answer")


def test_a_when_of_two_sentences_is_refused(spec_root):
    write_desk(spec_root, [{"operation": "read-case", "refusals": [
        {"when": "No case is held there. The identity is malformed.", "answer": "HTTP 404"}]}])
    assert hits(problems_of(spec_root), ".when carries 2 sentences")


def test_answers_are_an_api_field_only(spec_root):
    rewrite(spec_root, "contracts/troubleshooting/case-resolved.md",
            lambda f: f.update(answers=SOUND_ANSWERS))
    assert hits(problems_of(spec_root), "frontmatter: 'answers' is not one of")


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
    (spec_root / "domain/troubleshooting/_context.md").unlink()
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

    (spec_root / "domain/troubleshooting/evidence.md").unlink()
    run = subprocess.run(
        [sys.executable, "-B", str(REPO / "src/claude/bin/spec.py"), str(spec_root)],
        capture_output=True, text=True)
    assert run.returncode == 1
    assert "sits beside no node domain/troubleshooting/evidence" in run.stdout


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


def test_a_parse_failure_names_the_file_s_line_and_not_the_frontmatter_s(tmp_path):
    path = tmp_path / "node.md"
    path.write_text("---\ntitle: Sound\na: &id011 x\nb: &id011 y\n---\n## Description\n",
                    encoding="utf-8")
    front, _, problem = spec.parse_node(path)
    assert front is None
    # Both loaders say "duplicate anchor"; only the pure-Python one names the anchor. The line
    # is what this test guards, and it is the file's either way.
    assert "duplicate anchor" in problem
    assert "line 3" in problem and "line 4" in problem, \
        "a line counted from inside the fence sends the reader one line above the error"


def test_spec_py_on_a_project_root_hands_the_specification_root(spec_root):
    home = spec_root.parent
    (home / "siegard.json").write_text(json.dumps({"specification_root": spec_root.name}),
                                       encoding="utf-8")
    done = run_node(str(home))
    assert done.returncode == 2
    assert f"spec.py {spec_root}" in done.stderr, \
        "every markdown file of a repository read as a node is a problem per file"
    assert run_node(str(spec_root)).returncode == 0


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
    assert "named by  <- domain/troubleshooting/evidence.log" in done.stdout
    assert str(spec_root / "domain/troubleshooting/evidence.log.md") in done.stdout


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
    assert ("domain/troubleshooting/evidence.log", "domain/troubleshooting/evidence") in every
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


# ------------------------------------------------------------------ shape


def test_shape_reports_and_never_refuses(spec_root):
    """The one property that separates this from every other check in this module: a
    specification whose prose has drifted is still a sound specification, and a word count that
    refused would be a limit invented in `spec.py` rather than stated in a specification."""
    done = run_node("--shape", str(spec_root))
    assert done.returncode == 0, done.stderr
    assert "shape:" in done.stdout
    (spec_root / "rules/troubleshooting/case-transitions.md").write_text(
        (spec_root / "rules/troubleshooting/case-transitions.md").read_text(encoding="utf-8")
        + "\nA sentence naming nothing, appended a hundred times over.\n" * 100,
        encoding="utf-8")
    done = run_node("--shape", str(spec_root))
    assert done.returncode == 0, "a node grown tenfold is reported, never refused"


def test_shape_answers_over_a_specification_that_does_not_hold(spec_root):
    """`--impact`'s own reason: the analysis authoring these files needs the reading while it is
    authoring them, and one refused until the last file parses arrives after the decisions it
    was for."""
    (spec_root / "domain/monitoring/_context.md").unlink()
    done = run_node("--shape", str(spec_root))
    assert done.returncode == 0
    assert "problem(s)" in done.stdout


def test_shape_names_a_statement_carrying_more_than_one_sentence(spec_root):
    rewrite(spec_root, "rules/troubleshooting/case-transitions.md",
            lambda front: front.update(
                statement="A case moves only along the declared transitions. "
                          "And a second sentence is a second condition."))
    done = run_node("--shape", str(spec_root))
    assert "2 sentences" in done.stdout
    assert "rules/troubleshooting/case-transitions" in done.stdout


def test_shape_names_a_prose_name_that_resolves_to_no_node(spec_root):
    """The finding this report exists to surface: what has no definition is named, not omitted. A name a specification uses in prose and holds
    in no node is an operation, a table or a set with nowhere to be."""
    path = spec_root / "rules/troubleshooting/case-transitions.md"
    path.write_text(path.read_text(encoding="utf-8")
                    + "\nThe refusal `read-case-by-identity` answers is the registry's own.\n",
                    encoding="utf-8")
    done = run_node("--shape", str(spec_root))
    assert "resolve to no node" in done.stdout
    assert "read-case-by-identity" in done.stdout


def test_shape_closes_a_nodes_prose_transitively(spec_root):
    """A node naming a node that names a third is a node whose reader opens all three; the
    closure is what says how much must be read to conform to one rule."""
    (spec_root / "rules/troubleshooting/case-transitions.md").write_text(
        (spec_root / "rules/troubleshooting/case-transitions.md").read_text(encoding="utf-8")
        + "\nThis stands beside `domain/troubleshooting/hypothesis`.\n", encoding="utf-8")
    (spec_root / "domain/troubleshooting/hypothesis.md").write_text(
        (spec_root / "domain/troubleshooting/hypothesis.md").read_text(encoding="utf-8")
        + "\nAnd that one beside `domain/troubleshooting/resolution`.\n", encoding="utf-8")
    nodes, _ = spec.collect(spec_root, spec.contracts())
    read = spec.shape_of(nodes)
    closure = read["rules/troubleshooting/case-transitions"]["closure"]
    assert "domain/troubleshooting/hypothesis" in closure
    assert "domain/troubleshooting/resolution" in closure, \
        "the closure stopped at one hop; a reader does not"


def test_shape_stands_beside_no_other_derived_flag(spec_root):
    done = run_node("--shape", "--digest", str(spec_root))
    assert done.returncode == 2
    assert "mutually exclusive" in done.stderr


def test_shape_names_an_expression_that_outgrew_its_statement(spec_root):
    """`statement` governs (SPEC-003). Nothing can decide by reading whether an `expression`
    added an obligation, but a restatement longer than what it restates is the shape that does,
    and naming it is what makes the precedence reviewable instead of merely declared."""
    rewrite(spec_root, "rules/troubleshooting/hypothesis-requires-evidence.md",
            lambda front: front.update(
                expression="For every hypothesis h of a case c, h holds at least one piece of "
                            "evidence before c resolves, and the resolution is refused "
                            "otherwise with an error the caller can act on."))
    done = run_node("--shape", str(spec_root))
    assert "expression longer than the statement" in done.stdout
    assert "rules/troubleshooting/hypothesis-requires-evidence" in done.stdout


def test_shape_fires_on_nothing_over_a_sound_specification(spec_root):
    """The floor that makes every section above a finding rather than a baseline: over the sound
    fixture, each judgment section reports `(none)`. A report that always says something is one
    nobody reads twice."""
    done = run_node("--shape", str(spec_root))
    assert done.returncode == 0, done.stderr
    for section in ("statement carrying more than one sentence",
                    "expression longer than the statement",
                    "normative field speaking about the specification",
                    "longest phrase each set of nodes shares",
                    "prose naming more sibling nodes",
                    "resolve to no node",
                    "bare names two nodes answer to",
                    "constraint: statement at or past this class's p90",
                    "rule: statement at or past this class's p90",
                    "decision log:"):
        at = done.stdout.index(section)
        assert "(none)" in done.stdout[at:at + 700], \
            f"'{section}' reports something over a sound specification; it is a floor, not a find"


def test_the_committed_projections_are_what_project_writes():
    """The fixture's `projections/` is kept as the output `--project` writes over it, file for
    file: a projection that changes shape leaves this red until the committed copy follows, so
    the directory is a record of the output and never a stale example of one."""
    nodes, problems = spec.collect(FIXTURE, spec.contracts())
    assert problems + spec.cross_problems(nodes, FIXTURE) == []
    expected = spec.project(nodes)
    committed = {path.name: path.read_text(encoding="utf-8")
                 for path in (FIXTURE / "projections").iterdir()}
    assert committed == expected


def test_the_full_text_projection_restates_every_node_verbatim(spec_root):
    """SPEC-003 R6's full text: one header per node, in identity order, each followed by the
    node's own file unchanged — so a grep over it locates and the node is what gets opened."""
    nodes, _ = spec.collect(spec_root, spec.contracts())
    text = spec.project(nodes)["full-text.md"]
    headers = [line[4:] for line in text.splitlines() if line.startswith("=== ")]
    assert headers == sorted(nodes)
    for identity, node in nodes.items():
        assert node["path"].read_text(encoding="utf-8").rstrip("\n") in text
    rewrite(spec_root, "rules/troubleshooting/alert-opens-case.md",
            lambda front: front.update(statement="An alert unresolved for 48 hours MUST open a case."))
    nodes, _ = spec.collect(spec_root, spec.contracts())
    assert "48 hours" in spec.project(nodes)["full-text.md"]


def test_shape_names_a_clause_two_rules_both_carry(spec_root):
    """R3 and R7 leave restatement to judgment and nothing looked for it. A clause two rules both
    carry is one definition kept in two places, and no reference resolves it because neither node
    declares anything about the other."""
    shared = ("A hypothesis MUST hold at least one piece of evidence before its case resolves, "
              "and the resolution is refused with a validation error naming the hypothesis.")
    for relative in ("rules/troubleshooting/hypothesis-requires-evidence.md",
                     "rules/troubleshooting/case-transitions.md"):
        rewrite(spec_root, relative, lambda front: front.update(statement=shared))
    done = run_node("--shape", str(spec_root))
    at = done.stdout.index("longest phrase each set of nodes shares")
    found = done.stdout[at:at + 900]
    assert "2 node(s)" in found
    assert "rules/troubleshooting/case-transitions" in found


def test_shape_names_prose_that_outnumbers_the_declared_references(spec_root):
    """SPEC-001 R14's own reading. The declared count comes from the walk that validates it —
    `cross_problems`'s `record` — so the two cannot disagree about which fields carry one."""
    path = spec_root / "rules/troubleshooting/case-transitions.md"
    path.write_text(path.read_text(encoding="utf-8") + "\nIt sits beside "
                    "`domain/troubleshooting/hypothesis`, `domain/troubleshooting/evidence`, "
                    "`domain/troubleshooting/resolution` and `domain/troubleshooting/diagnostics`, "
                    "and contradicts none of them.\n", encoding="utf-8")
    done = run_node("--shape", str(spec_root))
    at = done.stdout.index("prose naming more sibling nodes")
    assert "rules/troubleshooting/case-transitions" in done.stdout[at:at + 900]


def widen_rules(root: Path, count: int) -> None:
    """Copies of the fixture's policy under new slugs, so the rule class holds a distribution:
    under `DISTRIBUTION` statements the p90 is the maximum and a ranking names the largest of any
    sample, so the far-end sections are a floor there and say so instead."""
    for n in range(count):
        (root / f"rules/troubleshooting/stale-alert-copy-{n}.md").write_text(
            f"---\ntype: policy\nstatement: An alert unresolved for {n + 25} hours MUST open a "
            "case.\nconstrains:\n  - domain/monitoring/alert\n  - domain/troubleshooting/case\n"
            "consistency: eventual\n---\n\n## Description\n\nA copy that widens the class.\n",
            encoding="utf-8")


def test_shape_names_a_long_statement_no_scenario_pins(spec_root):
    """Named against the class's own p90, never an invented word count: the threshold is what
    this specification's own rules run to, so the list is the far end of one corpus rather than
    a limit `spec.py` holds — and only where the class holds enough statements to have a far
    end apart from its maximum."""
    long_one = " ".join(["A case version released while its manifest still holds a draft "
                         "revision is refused by name"] * 12)
    rewrite(spec_root, "rules/troubleshooting/alert-opens-case.md",
            lambda front: front.update(statement=long_one))
    done = run_node("--shape", str(spec_root))
    at = done.stdout.index("rule: statement at or past this class's p90")
    found = done.stdout[at:at + 900]
    assert "(none) — 3 statement(s) is below the 10 a distribution needs" in found
    assert "rules/troubleshooting/alert-opens-case" not in found, \
        "the largest of three was named as a far end; three values have no p90 but their maximum"
    widen_rules(spec_root, spec.DISTRIBUTION - 3)
    done = run_node("--shape", str(spec_root))
    at = done.stdout.index("rule: statement at or past this class's p90")
    found = done.stdout[at:at + 900]
    assert "with no scenario anchored — 1" in found
    assert "rules/troubleshooting/alert-opens-case" in found


def test_shape_names_a_normative_field_talking_about_itself(spec_root):
    rewrite(spec_root, "rules/troubleshooting/case-transitions.md",
            lambda front: front.update(
                statement="A case moves only along the declared transitions, and every claim "
                          "that statement makes this specification already holds elsewhere."))
    done = run_node("--shape", str(spec_root))
    at = done.stdout.index("normative field speaking about the specification")
    assert "that statement" in done.stdout[at:at + 500]


def test_a_bare_slug_two_nodes_answer_to_resolves_to_neither(spec_root):
    """Silently picking whichever sorts first puts a node in the reader's closure the prose may
    never have meant: one word with two senses is two entries named apart."""
    (spec_root / "contracts/troubleshooting/evidence-type.md").write_text(
        "---\ntype: domain-event\ndirection: published\n"
        "payload: domain/troubleshooting/evidence\n---\n\n"
        "## Description\n\nA collision on purpose: the enumeration and the event share a slug.\n",
        encoding="utf-8")
    path = spec_root / "rules/troubleshooting/case-transitions.md"
    path.write_text(path.read_text(encoding="utf-8")
                    + "\nThis reads `evidence-type` without saying which.\n", encoding="utf-8")
    nodes, _ = spec.collect(spec_root, spec.contracts())
    read = spec.shape_of(nodes)
    entry = read["rules/troubleshooting/case-transitions"]
    assert "evidence-type" in entry["ambiguous"]
    assert not any(name.endswith("/evidence-type") for name in entry["names"]), \
        "an ambiguous bare slug was resolved to one of its holders"
    done = run_node("--shape", str(spec_root))
    at = done.stdout.index("bare names two nodes answer to")
    assert "`evidence-type`" in done.stdout[at:at + 400]


def test_shape_reports_how_far_the_logs_why_runs(spec_root):
    """SPEC-001 R9 bounds `why` to one claim a reviewer can reject. The concord argument R14
    keeps out of a node's prose has no entry of its own, so the only way it reaches the log is
    inside the `why` of an entry about something else — which is where the report points."""
    argued = {**DECIDED, "decided": "aggregate-root",
              "why": " ".join(["This rule is the home rather than a sibling's clause"] * 40)}
    log_beside(spec_root, CASE_LOG, [argued])
    done = run_node("--shape", str(spec_root))
    assert done.returncode == 0
    at = done.stdout.index("decision log:")
    found = done.stdout[at:at + 700]
    assert "3 decided entry(ies) across 3 log(s)" in found and "`why` median" in found
    assert "(none) — 3 decided entry(ies) is below the 10 a distribution needs" in found
    assert "domain/troubleshooting/case.log" not in found, \
        "the longest of three was named as a far end; three values have no p90 but their maximum"
    log_beside(spec_root, CASE_LOG,
               [argued] + [dict(DECIDED) for _ in range(spec.DISTRIBUTION - 3)])
    done = run_node("--shape", str(spec_root))
    assert done.returncode == 0
    at = done.stdout.index("decision log:")
    found = done.stdout[at:at + 700]
    assert f"{spec.DISTRIBUTION} decided entry(ies) across 3 log(s)" in found
    assert "1 log(s) with an entry at or past that p90" in found
    assert "domain/troubleshooting/case.log" in found, \
        "the log holding the far end is named, not only counted"


def test_shape_lists_fields_a_log_decided_more_than_once(spec_root):
    """SPEC-001 R9: «The latest entry over a field is the disclosure that stands». Two decided
    entries over one field are two answers to one question, and the report names where."""
    sound = run_node("--shape", str(spec_root))
    at = sound.stdout.index("fields a log decided more than once")
    assert "(none)" in sound.stdout[at:at + 400]
    log_beside(spec_root, CASE_LOG, [dict(DECIDED), {**DECIDED, "decided": "entity"}])
    done = run_node("--shape", str(spec_root))
    at = done.stdout.index("fields a log decided more than once — 1")
    assert "2x  type  in  domain/troubleshooting/case.log" in done.stdout[at:at + 400]


def test_shape_counts_the_fields_a_log_decided_per_node(spec_root):
    """SPEC-001 R4 and R8: a decided field reads like a stated one in the node, and the log is
    the only place the two are told apart. This section is the one line a reviewer reads before
    any node — which node the material barely described — so it is a count, never `(none)` over a
    root that holds decisions, ranked with the far end first; a read entry and a retirement are
    not decisions and are not counted, and a scoped node is marked past the cut."""
    sound = run_node("--shape", str(spec_root))
    at = sound.stdout.index("decided fields per node — 2 node(s) carry a decision, 2 decided")
    section = sound.stdout[at:sound.stdout.index("\n\n", at)]
    assert "1 decided /  10 declared  domain/troubleshooting/evidence" in section
    assert "1 decided /  23 declared  rules/troubleshooting/case-transitions" in section
    assert "domain/troubleshooting/case" not in section, "a node with no log is not listed"
    log_beside(spec_root, CASE_LOG, [dict(DECIDED), {**DECIDED, "field": "attributes"},
                                     {**READ_ENTRY, "field": "operations"},
                                     {**DECIDED, "field": "relationships"},
                                     {"field": "relationships", "retired": "held nowhere"}])
    done = run_node("--shape", "--of", "domain/troubleshooting/case", str(spec_root))
    assert done.returncode == 0, done.stderr
    at = done.stdout.index("decided fields per node — 3 node(s) carry a decision, 4 decided")
    section = done.stdout[at:done.stdout.index("\n\n", at)]
    rows = [line for line in section.splitlines()[1:]]
    assert rows[0].startswith(">   2 decided /") and rows[0].endswith("domain/troubleshooting/case"), \
        "the node with most decided fields leads, and the scoped node is marked"
    assert "4 decided field(s) over" in section, \
        "a read entry and a retired field were counted as decisions"
    for log in spec_root.rglob("*.log.md"):
        log.unlink()
    done = run_node("--shape", str(spec_root))
    at = done.stdout.index("decided fields per node — 0 node(s)")
    assert "(none)" in done.stdout[at:at + 400]


def test_shape_shows_a_scoped_node_past_the_cut(spec_root):
    """The failure this closes: three sections rank and cut, and over a populated root the far
    end belongs to what was written before — so a node written now sits below the cut and never
    reaches the one reader obliged to fix it. Ranked last here on purpose."""
    six = ("`domain/troubleshooting/case`, `domain/troubleshooting/evidence`, "
           "`domain/troubleshooting/hypothesis`, `domain/troubleshooting/resolution`, "
           "`domain/troubleshooting/diagnostics` and `domain/troubleshooting/case-status`")
    mine = spec_root / "rules/troubleshooting/case-transitions.md"
    for other in sorted(p for p in spec_root.rglob("*.md")
                        if p != mine and not p.name.endswith(".log.md")):
        other.write_text(other.read_text(encoding="utf-8")
                         + f"\nIt stands beside {six}, contradicting none.\n", encoding="utf-8")
    mine.write_text(mine.read_text(encoding="utf-8")
                    + "\nIt stands beside `domain/troubleshooting/case`, "
                      "`domain/troubleshooting/evidence` and "
                      "`domain/troubleshooting/hypothesis`.\n", encoding="utf-8")

    def rows(out: str) -> str:
        at = out.index("prose naming more sibling nodes")
        return out[at:out.index("\n\n", at)]

    at_large = rows(run_node("--shape", str(spec_root)).stdout)
    done = run_node("--shape", "--of", "rules/troubleshooting/case-transitions", str(spec_root))
    assert done.returncode == 0, done.stderr
    scoped = rows(done.stdout)
    assert "rules/troubleshooting/case-transitions" not in at_large,         "the fixture no longer ranks the scoped node below the cut; the test has lost its subject"
    assert "rules/troubleshooting/case-transitions" in scoped,         "a scoped node was cut from the ranking it was written into"
    assert ">" in scoped.split("rules/troubleshooting/case-transitions")[0].splitlines()[-1],         "a scoped row is not marked"


def test_shape_keeps_the_totals_of_the_whole_root_when_scoped(spec_root):
    """Scoping changes what is shown and never what is counted: a report narrowing its counts to
    the slice would call a node unremarkable by comparing it only to its own siblings."""
    at_large = run_node("--shape", str(spec_root))
    scoped = run_node("--shape", "--of", "rules/troubleshooting/case-transitions",
                      str(spec_root))
    for line in at_large.stdout.splitlines():
        if line.startswith("shape:") or line.startswith("rule "):
            assert line in scoped.stdout, f"scoping moved a total: {line!r}"


def test_shape_names_the_far_end_of_each_class(spec_root):
    """`percentile` prints a number a node actually has; this is the rest of that sentence. A
    distribution nobody can open is the measurement this reading exists to replace."""
    done = run_node("--shape", str(spec_root))
    header = done.stdout.index("class ")
    table = done.stdout[header:done.stdout.index("statement carrying")]
    assert "at or past p90" in table
    assert "log " in table and "at or past p90: 45428w" not in table, \
        "a class of one node has no distribution to sit at the far end of"


def test_of_refuses_an_identity_that_names_no_file(spec_root):
    done = run_node("--shape", "--of", "rules/troubleshooting/nope", str(spec_root))
    assert done.returncode == 2 and "names no file" in done.stderr


def test_of_scopes_shape_and_stands_beside_nothing_else(spec_root):
    done = run_node("--of", "rules/troubleshooting/case-transitions", str(spec_root))
    assert done.returncode == 2 and "stands beside nothing else" in done.stderr


# --------------------------------------------------- one condition, one sentence (SPEC-003)


def test_a_statement_carrying_two_sentences_is_refused(spec_root):
    """The half of "one falsifiable condition" a sentence count decides. No escape hatch: a
    second sentence is a definition, an example, or a second condition, and each has a home."""
    rewrite(spec_root, "rules/troubleshooting/case-transitions.md",
            lambda front: front.update(
                statement="A case moves only along the declared transitions. "
                          "A transition asked of a terminal state is refused."))
    found = hits(problems_of(spec_root), "«One condition is one sentence» (SPEC-003 §Rule)")
    assert found and "rules/troubleshooting/case-transitions" in found[0]
    assert "2 sentences" in found[0]


def test_a_constraint_statement_is_held_to_one_sentence_too(spec_root):
    rewrite(spec_root, "constraints/asynchronous-events.md",
            lambda front: front.update(
                statement="Contexts exchange events asynchronously. No context blocks on "
                          "another's acknowledgement."))
    assert hits(problems_of(spec_root), "constraints/asynchronous-events: statement carries 2")


def test_a_two_sentence_statement_is_refused_in_node_mode_too(spec_root):
    """`--node` is the per-file half of the whole run, and a file mid-authoring is where the
    author meets this first — refusing it there is the speed bump doing its work."""
    rewrite(spec_root, "rules/troubleshooting/case-transitions.md",
            lambda front: front.update(
                statement="A case moves only along the declared transitions. "
                          "Nothing else moves it."))
    done = run_node("--node", "rules/troubleshooting/case-transitions.md", str(spec_root))
    assert done.returncode == 1
    assert "«One condition is one sentence» (SPEC-003 §Rule)" in done.stdout


def test_a_semicolon_passes_the_sentence_check(spec_root):
    """Stated so nobody mistakes the check for a wall: one sentence carrying two conditions on a
    semicolon passes, and the metamodel says so. What catches it is `--shape` naming the far
    end of the class, which is judgment and always was."""
    rewrite(spec_root, "rules/troubleshooting/case-transitions.md",
            lambda front: front.update(
                statement="A case moves only along the declared transitions; a transition "
                          "asked of a terminal state is refused."))
    assert not hits(problems_of(spec_root), "«One condition is one sentence» (SPEC-003 §Rule)")


def test_yaml_is_read_through_libyaml_where_the_interpreter_has_it():
    """The same documents either way; what differs is an order of magnitude over a corpus of
    reconciliation records, which is the difference between a status that answers now and one
    a person waits for."""
    import yaml
    if yaml.__with_libyaml__:
        assert spec.YAML_LOADER is yaml.CSafeLoader
    else:
        assert spec.YAML_LOADER is yaml.SafeLoader
    assert spec.load_yaml("a: [1, 2]\nb: {c: d}\n") == {"a": [1, 2], "b": {"c": "d"}}
    with pytest.raises(yaml.YAMLError):
        spec.load_yaml("a: b: c\n")
