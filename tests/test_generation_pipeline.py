"""The four steps between a knowledge base and a written file, and the refusals at each.

`foundation/0004` puts a scope, a placement decision, a plan, and a manifest between knowledge and
source. The property that makes the whole thing testable is R23: no model participates in
deriving the plan, so R28's byte identity is checkable on its own — and R29 requires it to be
checked here rather than only at the output, because a test covering produced source cannot
distinguish a nondeterministic plan from a nondeterministic template.

Exercised against `fixtures/pack-minimal/`, a pack declaration with no producers behind it. That
is deliberate: the pipeline is framework-owned and stack-independent (`foundation/0012` R4), and
testing it against a real pack would conflate "the pipeline works" with "the pack works".
"""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

import generation_lib as gl
from knowledge_graph_lib import load

REPO_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE = REPO_ROOT / "fixtures" / "knowledge-two-context" / "knowledge"
PACK = REPO_ROOT / "fixtures" / "pack-minimal"
SCHEMAS = REPO_ROOT / "src" / "claude" / "schemas"
ROOT_KO = "ko.rule.sales.proposal-validity"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def validator(name: str) -> Draft202012Validator:
    return Draft202012Validator(load_json(SCHEMAS / name))


class Fixture(unittest.TestCase):
    def setUp(self) -> None:
        self.graph = load(KNOWLEDGE)
        self.declaration = load_json(PACK / "pack-declaration.json")
        self.scope = load_json(PACK / "generation-scope.json")
        self.placement = load_json(PACK / "placement-decision.json")
        self.plan = load_json(PACK / "generation-plan.json")
        self.manifest = load_json(PACK / "generation-manifest.json")
        self.empty_manifest = {
            "contract_version": "generation-manifest/1",
            "pack": self.declaration["pack"],
            "pack_version": self.declaration["version"],
            "artifacts": [],
        }


class Conformance(Fixture):
    def test_each_artifact_conforms_to_its_contract(self) -> None:
        for name, document in (
            ("pack-declaration.json", self.declaration),
            ("generation-scope.json", self.scope),
            ("placement-decision.json", self.placement),
            ("generation-plan.json", self.plan),
            ("generation-manifest.json", self.manifest),
        ):
            with self.subTest(contract=name):
                self.assertEqual([], list(validator(name).iter_errors(document)))

    def test_the_class_vocabulary_is_the_same_in_every_contract(self) -> None:
        """foundation/0004 R8 closes it once; four contracts naming it must not drift apart."""
        def classes(name: str, pointer) -> set:
            return set(pointer(load_json(SCHEMAS / name)))

        declared = classes(
            "pack-declaration.json",
            lambda s: s["properties"]["produces"]["items"]["properties"]["class"]["enum"],
        )
        for name, pointer in (
            ("placement-decision.json",
             lambda s: s["properties"]["entries"]["items"]["properties"]["class"]["enum"]),
            ("generation-plan.json",
             lambda s: s["properties"]["entries"]["items"]["properties"]["class"]["enum"]),
            ("generation-manifest.json",
             lambda s: s["properties"]["artifacts"]["items"]["properties"]["class"]["enum"]),
        ):
            with self.subTest(contract=name):
                self.assertEqual(declared, classes(name, pointer))

    def test_the_vocabulary_has_twelve_classes(self) -> None:
        self.assertEqual(
            12,
            len(load_json(SCHEMAS / "pack-declaration.json")
                ["properties"]["produces"]["items"]["properties"]["class"]["enum"]),
        )

    def test_a_traversing_placement_path_is_rejected_by_the_contract(self) -> None:
        document = json.loads(json.dumps(self.placement))
        document["entries"][0]["path"] = "/etc/passwd"
        self.assertTrue(list(validator("placement-decision.json").iter_errors(document)))


class Scope(Fixture):
    """foundation/0004 R19 through R22."""

    def test_it_recomputes_from_its_roots(self) -> None:
        fresh = gl.resolve_scope(
            self.graph, self.scope["scope_id"], self.scope["request_id"], self.scope["roots"]
        )
        self.assertEqual(self.scope, fresh)

    def test_it_is_deterministic(self) -> None:
        first = gl.resolve_scope(self.graph, "gs_1a2b3c4d", "cr_2b4f6a80", [ROOT_KO])
        second = gl.resolve_scope(self.graph, "gs_1a2b3c4d", "cr_2b4f6a80", [ROOT_KO])
        self.assertEqual(first, second)

    def test_it_holds_only_knowledge_objects(self) -> None:
        """An ADR is reachable in the graph and is not something a pack generates from."""
        types = {member["type"] for member in self.scope["members"]}
        self.assertNotIn("adr", types)

    def test_an_unresolvable_root_blocks_rather_than_degrades(self) -> None:
        """A generation scope fails closed; fail-soft belongs to context resolution.

        Asserted on what the message says rather than on a requirement id. A shipped component
        cites no requirement, because the specification it would cite is the generator's and
        never reaches the repository the message is read in.
        """
        with self.assertRaises(gl.Blocked) as caught:
            gl.resolve_scope(self.graph, "gs_1a2b3c4d", "cr_2b4f6a80", ["ko.rule.sales.absent"])
        message = str(caught.exception)
        self.assertIn("resolve to no knowledge object", message)
        self.assertIn("blocks generation", message)

    def test_an_unresolvable_member_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as holder:
            copy = Path(holder) / "knowledge"
            shutil.copytree(KNOWLEDGE, copy)
            target = copy / "rule" / "sales" / "proposal-validity.md"
            target.write_text(
                target.read_text().replace("depends_on: [", "depends_on: [ko.definition.sales.gone, ", 1)
            )
            with self.assertRaises(gl.Blocked):
                gl.resolve_scope(load(copy), "gs_1a2b3c4d", "cr_2b4f6a80", [ROOT_KO])

    def test_a_changed_member_invalidates_the_scope(self) -> None:
        """foundation/0004 R20: a change invalidates rather than alters."""
        self.assertEqual([], gl.scope_is_stale(self.scope, self.graph))
        with tempfile.TemporaryDirectory() as holder:
            copy = Path(holder) / "knowledge"
            shutil.copytree(KNOWLEDGE, copy)
            target = copy / "rule" / "sales" / "proposal-validity.md"
            target.write_text(target.read_text() + "\nAn added line.\n")
            stale = gl.scope_is_stale(self.scope, load(copy))
        self.assertIn(ROOT_KO, stale)

    def test_the_frozen_digest_changes_with_the_members(self) -> None:
        other = gl.resolve_scope(self.graph, "gs_1a2b3c4d", "cr_2b4f6a80", ["ko.definition.billing.invoice"])
        self.assertNotEqual(self.scope["frozen_digest"], other["frozen_digest"])


class Demand(Fixture):
    """foundation/0004 R14's `from` column, which is what makes the plan derivable without a model."""

    def test_every_demanded_artifact_names_a_declared_class(self) -> None:
        declared = {entry["class"] for entry in self.declaration["produces"]}
        demanded, _ = gl.demand(self.scope, self.declaration)
        self.assertTrue(demanded)
        for _ko, artifact_class, _track in demanded:
            self.assertIn(artifact_class, declared)

    def test_a_node_type_yielding_nothing_is_reported(self) -> None:
        """foundation/0004 R11: silence about it reads as coverage that does not exist."""
        _demanded, uncovered = gl.demand(self.scope, self.declaration)
        self.assertIn("boundary", uncovered)

    def test_it_is_deterministic(self) -> None:
        self.assertEqual(gl.demand(self.scope, self.declaration), gl.demand(self.scope, self.declaration))


class Placement(Fixture):
    """foundation/0004 R52. Rejects, never repairs."""

    def broken(self, mutate) -> list[str]:
        document = json.loads(json.dumps(self.placement))
        mutate(document)
        return gl.validate_placement(document, self.scope, self.declaration, REPO_ROOT)

    def test_the_fixture_decision_validates(self) -> None:
        self.assertEqual([], gl.validate_placement(self.placement, self.scope, self.declaration, REPO_ROOT))

    def test_a_path_outside_the_repository_is_rejected(self) -> None:
        problems = self.broken(lambda d: d["entries"][0].update(path="../../elsewhere/x.ts"))
        self.assertTrue(any("outside the governed repository" in p for p in problems), problems)

    def test_two_entries_claiming_one_path_are_rejected(self) -> None:
        problems = self.broken(lambda d: d["entries"][1].update(path=d["entries"][0]["path"]))
        self.assertTrue(any("already claimed by" in p for p in problems), problems)

    def test_a_class_the_pack_does_not_declare_is_rejected(self) -> None:
        problems = self.broken(lambda d: d["entries"][0].update(**{"class": "migration"}))
        self.assertTrue(any("does not declare" in p for p in problems), problems)

    def test_a_knowledge_object_outside_the_scope_is_rejected(self) -> None:
        problems = self.broken(lambda d: d["entries"][0].update(ko="ko.definition.billing.invoice"))
        self.assertTrue(any("the scope does not hold" in p for p in problems), problems)

    def test_a_decision_frozen_against_another_scope_is_rejected(self) -> None:
        problems = self.broken(lambda d: d.update(scope_id="gs_deadbeef"))
        self.assertTrue(any("another scope" in p for p in problems), problems)

    def test_a_decision_naming_another_pack_is_rejected(self) -> None:
        problems = self.broken(lambda d: d.update(pack="someone-else"))
        self.assertTrue(any("active pack" in p for p in problems), problems)


class Plan(Fixture):
    """foundation/0004 R23 through R29."""

    def derive(self, manifest=None, placement=None) -> dict:
        plan, _ = gl.derive_plan(
            "gp_4f5a6b7c", self.scope, self.declaration,
            manifest or self.empty_manifest, placement or self.placement,
        )
        return plan

    def test_the_fixture_plan_recomputes(self) -> None:
        self.assertEqual(self.plan, self.derive())

    def test_identical_inputs_yield_a_byte_identical_plan(self) -> None:
        """foundation/0004 R28, and R29 requires it tested here rather than only at the output."""
        self.assertEqual(
            json.dumps(self.derive(), indent=2, sort_keys=True),
            json.dumps(self.derive(), indent=2, sort_keys=True),
        )

    def test_a_first_generation_is_entirely_new(self) -> None:
        self.assertTrue(all(entry["state"] == "new" for entry in self.derive()["entries"]))

    def test_a_regeneration_is_entirely_locked(self) -> None:
        """foundation/0004 R31: the path is read on every later run and never decided again."""
        second = self.derive(manifest=self.manifest)
        self.assertTrue(all(entry["state"] == "locked" for entry in second["entries"]))

    def test_the_locked_paths_equal_the_first_run_s(self) -> None:
        self.assertEqual(
            [entry["path"] for entry in self.derive()["entries"]],
            [entry["path"] for entry in self.derive(manifest=self.manifest)["entries"]],
        )

    def test_a_regeneration_ignores_a_changed_placement_decision(self) -> None:
        """R31 has nothing to read if a later placement could override the lock."""
        moved = json.loads(json.dumps(self.placement))
        for entry in moved["entries"]:
            entry["path"] = "somewhere/else/" + Path(entry["path"]).name
        self.assertEqual(
            [entry["path"] for entry in self.derive(manifest=self.manifest)["entries"]],
            [entry["path"] for entry in self.derive(manifest=self.manifest, placement=moved)["entries"]],
        )

    def test_a_demanded_artifact_with_no_path_blocks(self) -> None:
        """foundation/0004 R24: an entry with no target path cannot be validated under R25."""
        short = json.loads(json.dumps(self.placement))
        short["entries"] = short["entries"][1:]
        with self.assertRaises(gl.Blocked) as caught:
            self.derive(placement=short)
        self.assertIn("R24", str(caught.exception))

    def test_every_entry_carries_the_track_the_pack_declared(self) -> None:
        tracks = {e["class"]: e["track"] for e in self.declaration["produces"]}
        for entry in self.plan["entries"]:
            self.assertEqual(tracks[entry["class"]], entry["track"])

    def test_both_tracks_are_present(self) -> None:
        """A pack declaring only one track would leave half the plan's vocabulary unexercised."""
        self.assertEqual({"deterministic", "judged"}, {e["track"] for e in self.plan["entries"]})

    def test_no_model_is_reachable_from_the_derivation(self) -> None:
        """foundation/0004 R23, read off the module rather than asserted in prose."""
        source = (REPO_ROOT / "src" / "claude" / "bin" / "generation_lib.py").read_text()
        for forbidden in ("subprocess", "urllib", "socket", "requests", "http"):
            self.assertNotIn(f"import {forbidden}", source)


class PlanValidation(Fixture):
    """foundation/0004 R25 and R27 — before any file is written."""

    def test_the_fixture_plan_validates(self) -> None:
        plan = json.loads(json.dumps(self.plan))
        for entry in plan["entries"]:
            entry["state"] = "new"
        self.assertEqual([], gl.validate_plan(plan, self.scope, self.declaration, REPO_ROOT))

    def test_a_collision_is_reported_as_a_defect(self) -> None:
        plan = json.loads(json.dumps(self.plan))
        plan["entries"][1]["path"] = plan["entries"][0]["path"]
        problems = gl.validate_plan(plan, self.scope, self.declaration, REPO_ROOT)
        self.assertTrue(any("R27" in p for p in problems), problems)

    def test_a_locked_path_that_no_longer_exists_is_reported(self) -> None:
        plan = json.loads(json.dumps(self.plan))
        plan["entries"][0]["state"] = "locked"
        plan["entries"][0]["path"] = "src/sales/types/gone-for-good.ts"
        problems = gl.validate_plan(plan, self.scope, self.declaration, REPO_ROOT)
        self.assertTrue(any("no longer exists" in p for p in problems), problems)

    def test_validation_writes_nothing(self) -> None:
        """foundation/0004 R26: a plan is producible and inspectable without writing any file."""
        before = {p for p in REPO_ROOT.rglob("*") if p.is_file() and ".git" not in p.parts}
        gl.derive_plan("gp_4f5a6b7c", self.scope, self.declaration, self.empty_manifest, self.placement)
        gl.validate_plan(self.plan, self.scope, self.declaration, REPO_ROOT)
        after = {p for p in REPO_ROOT.rglob("*") if p.is_file() and ".git" not in p.parts}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()


class CommittedFixture(unittest.TestCase):
    """The four artifacts in `fixtures/pack-minimal/`, recomputed from what the run records.

    Committed because a fixture is evidence a reader inspects, and safe to commit only while it
    is asserted to equal what the recorded inputs produce. `generation-run.json` is the analogue
    of a workflow fixture's `inputs/run.json`: every identifier is stated rather than minted, so
    the artifacts can be regenerated and compared at all.
    """

    def setUp(self) -> None:
        self.run = load_json(PACK / "generation-run.json")
        self.graph = load(REPO_ROOT / self.run["knowledge_root"])
        self.declaration = load_json(PACK / "pack-declaration.json")

    def test_the_scope_recomputes(self) -> None:
        fresh = gl.resolve_scope(
            self.graph, self.run["scope_id"], self.run["request_id"], self.run["roots"]
        )
        self.assertEqual(load_json(PACK / "generation-scope.json"), fresh)

    def test_the_plan_recomputes_from_the_committed_inputs(self) -> None:
        scope = load_json(PACK / "generation-scope.json")
        empty = {
            "contract_version": "generation-manifest/1",
            "pack": self.declaration["pack"],
            "pack_version": self.declaration["version"],
            "artifacts": [],
        }
        plan, _ = gl.derive_plan(
            self.run["plan_id"], scope, self.declaration, empty,
            load_json(PACK / "placement-decision.json"),
        )
        self.assertEqual(load_json(PACK / "generation-plan.json"), plan)

    def test_the_manifest_locks_every_planned_path(self) -> None:
        """foundation/0004 R53: the run transcribes the decision into the manifest before it ends."""
        plan = load_json(PACK / "generation-plan.json")
        manifest = load_json(PACK / "generation-manifest.json")
        self.assertEqual(
            {(e["ko"], e["class"], e["path"]) for e in plan["entries"]},
            {(a["ko"], a["class"], a["path"]) for a in manifest["artifacts"]},
        )

    def test_the_manifest_names_the_framework_it_was_produced_under(self) -> None:
        """foundation/0004 R4 names four pinned identities a reproducibility claim must carry."""
        installed = load_json(REPO_ROOT / "src" / "claude" / ".claude-plugin" / "plugin.json")
        self.assertEqual(installed["version"], load_json(PACK / "generation-manifest.json")["framework_version"])

    def test_the_run_names_the_skill_that_drives_it(self) -> None:
        """foundation/0004 R18: the entry point that runs generation is a skill."""
        self.assertEqual("generate", self.run["producer"])
