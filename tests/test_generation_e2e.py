"""One generation, executed, verified, and measured — the last step of `foundation/0004`.

Fifty-nine artifacts produced from a real knowledge base through a real pack, into
`fixtures/generation-run/out`. Committed, because R34's verification is a diff against a
committed tree and there is nothing to diff against otherwise.

The measurement class is the one that can make the framework claim less. R6 requires the
deterministic share to be measured and reported, and where it does not cover the structural code,
the promise reduced to what the mechanism delivers rather than restated.
"""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

import generate_code as gc
import generation_lib as gl

REPO_ROOT = Path(__file__).resolve().parent.parent
RUN = REPO_ROOT / "fixtures" / "generation-run" / "run.json"


class GenerationCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.recipe = json.loads(RUN.read_text())
        cls.out = REPO_ROOT / cls.recipe["output_root"]
        cls.manifest = json.loads((REPO_ROOT / cls.recipe["manifest"]).read_text())
        cls.declaration, cls.graph, cls.scope, cls.placement = gc.prepare(cls.recipe)
        cls.plan, _ = gl.derive_plan(
            cls.recipe["plan_id"], cls.scope, cls.declaration,
            {"contract_version": "generation-manifest/1", "pack": cls.declaration["pack"],
             "pack_version": cls.declaration["version"], "artifacts": []},
            cls.placement,
        )


class Produced(GenerationCase):
    def test_the_manifest_conforms(self) -> None:
        from jsonschema import Draft202012Validator

        schema = json.loads((REPO_ROOT / "src" / "claude" / "schemas" / "generation-manifest.json").read_text())
        self.assertEqual([], list(Draft202012Validator(schema).iter_errors(self.manifest)))

    def test_every_recorded_artifact_exists_with_its_recorded_hash(self) -> None:
        """foundation/0004 R30, and the half that makes R35's attribution possible."""
        for artifact in self.manifest["artifacts"]:
            path = self.out / artifact["path"]
            self.assertTrue(path.is_file(), artifact["path"])
            self.assertEqual(artifact["content_hash"], gl.content_hash(path))

    def test_every_produced_file_is_recorded(self) -> None:
        recorded = {a["path"] for a in self.manifest["artifacts"]}
        on_disk = {p.relative_to(self.out).as_posix() for p in self.out.rglob("*") if p.is_file()}
        self.assertEqual(recorded, on_disk)

    def test_every_artifact_traces_to_a_knowledge_object_in_the_scope(self) -> None:
        """foundation/0004 R30: reproducing a generation names what produced each file."""
        members = {member["id"] for member in self.scope["members"]}
        for artifact in self.manifest["artifacts"]:
            self.assertIn(artifact["ko"], members)

    def test_every_artifact_names_the_pack_version_that_produced_it(self) -> None:
        for artifact in self.manifest["artifacts"]:
            self.assertEqual(self.declaration["version"], artifact["pack_version"])

    def test_the_manifest_names_the_framework_version(self) -> None:
        """One of the four pinned identities foundation/0004 R4 requires of a claim."""
        installed = json.loads(
            (REPO_ROOT / "src" / "claude" / ".claude-plugin" / "plugin.json").read_text()
        )
        self.assertEqual(installed["version"], self.manifest["framework_version"])

    def test_every_produced_file_carries_its_provenance(self) -> None:
        for artifact in self.manifest["artifacts"]:
            self.assertIn(artifact["ko"], (self.out / artifact["path"]).read_text())


class RegenerateAndDiff(GenerationCase):
    """foundation/0004 R34 and R35."""

    def fresh(self, mutate=None) -> list[str]:
        with tempfile.TemporaryDirectory() as holder:
            copy = Path(holder) / "committed"
            shutil.copytree(self.out, copy)
            if mutate:
                mutate(copy)
            regenerated = Path(holder) / "fresh"
            gc.produce(self.recipe, regenerated)
            return gc.findings(copy, regenerated, self.manifest)

    def test_the_committed_tree_matches_a_fresh_generation(self) -> None:
        self.assertEqual([], self.fresh())

    def test_verification_mutates_nothing(self) -> None:
        """R34: a check that repairs what it detects reports success on a defect."""
        before = {
            p.relative_to(self.out).as_posix(): p.read_bytes()
            for p in self.out.rglob("*") if p.is_file()
        }
        self.fresh()
        after = {
            p.relative_to(self.out).as_posix(): p.read_bytes()
            for p in self.out.rglob("*") if p.is_file()
        }
        self.assertEqual(before, after)

    def test_a_hand_edit_is_named_as_a_hand_edit(self) -> None:
        """R35: the report names which of three causes, because they call for opposite actions."""
        target = self.manifest["artifacts"][0]["path"]

        def edit(root: Path) -> None:
            (root / target).write_text((root / target).read_text() + "\n// edited\n")

        problems = self.fresh(edit)
        self.assertTrue(any(target in p and "hand edit" in p for p in problems), problems)

    def test_a_deleted_produced_file_is_reported(self) -> None:
        target = self.manifest["artifacts"][0]["path"]
        problems = self.fresh(lambda root: (root / target).unlink())
        self.assertTrue(any("hand deletion" in p for p in problems), problems)

    def test_a_change_in_knowledge_is_distinguished_from_a_hand_edit(self) -> None:
        """The file matches the manifest and the generator now produces something else."""
        with tempfile.TemporaryDirectory() as holder:
            mirror = Path(holder) / "repo"
            for part in ("fixtures",):
                shutil.copytree(REPO_ROOT / part, mirror / part)
            target = mirror / self.recipe["knowledge_root"] / "definition" / "billing" / "invoice.md"
            target.write_text(target.read_text().replace("name: amount", "name: total", 1))
            regenerated = Path(holder) / "fresh"
            gc.produce(self.recipe, regenerated, repo_root=mirror)
            problems = gc.findings(self.out, regenerated, self.manifest)
        self.assertTrue(
            any("change in knowledge or a producer regression" in p for p in problems), problems
        )


class BlockedRuns(GenerationCase):
    """Nothing is written when the plan does not validate — R25."""

    def test_a_collision_blocks_and_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as holder:
            mirror = Path(holder) / "repo"
            shutil.copytree(REPO_ROOT / "fixtures", mirror / "fixtures")
            decision_path = mirror / self.recipe["pack_root"] / "placement-decision.json"
            decision = json.loads(decision_path.read_text())
            decision["entries"][1]["path"] = decision["entries"][0]["path"]
            decision_path.write_text(json.dumps(decision, indent=2) + "\n")
            # The manifest has to go: once every entry is locked, R31 reads the path back and a
            # collision in the placement decision has no effect at all. Which is R31 working —
            # and it means a collision is only reachable on a first generation.
            (mirror / self.recipe["manifest"]).unlink()
            target = Path(holder) / "out"
            with self.assertRaises(gl.Blocked) as caught:
                gc.produce(self.recipe, target, repo_root=mirror)
            message = str(caught.exception)
            self.assertIn("the plan does not validate", message)
            self.assertIn("rather than repairing it", message)
            self.assertFalse(target.exists(), "a blocked plan wrote files")


class Measurement(GenerationCase):
    """foundation/0004 R6 — the requirement that can reduce what the framework promises."""

    def test_the_deterministic_share_is_computable(self) -> None:
        deterministic, total = gc.deterministic_share(self.manifest, self.plan)
        self.assertGreater(total, 0)
        self.assertLessEqual(deterministic, total)

    def test_the_recorded_share_matches_what_the_code_produces(self) -> None:
        """A figure in prose that nothing derives is the drift this repository has had twice."""
        deterministic, total = gc.deterministic_share(self.manifest, self.plan)
        recorded = (REPO_ROOT / "foundation" / "0004-generation-and-reproducibility.md").read_text()
        self.assertIn(f"{deterministic} of {total}", recorded)

    def test_every_produced_artifact_is_locked_on_the_next_run(self) -> None:
        """R31 reads the path back, which is why a collision is only reachable on a first run.

        The two judged entries stay `new`: nothing produced them, so the manifest holds no path
        for them and there is nothing to lock. A run that ends without producing an artifact
        locks no path for it — foundation/0004 R53's fourth condition, visible here.
        """
        plan, _ = gl.derive_plan(
            self.recipe["plan_id"], self.scope, self.declaration, self.manifest, self.placement
        )
        produced = {(a["ko"], a["class"]) for a in self.manifest["artifacts"]}
        for entry in plan["entries"]:
            expected = "locked" if (entry["ko"], entry["class"]) in produced else "new"
            self.assertEqual(expected, entry["state"], f"{entry['ko']}/{entry['class']}")
        self.assertEqual(
            {"validator"}, {e["class"] for e in plan["entries"] if e["state"] == "new"}
        )

    def test_the_judged_track_is_not_silently_absent(self) -> None:
        """The two judged entries are reported as not produced here, never dropped."""
        _manifest, _gaps, skipped = gc.produce(self.recipe, Path(tempfile.mkdtemp()))
        self.assertTrue(any("validator" in note for note in skipped), skipped)


class BindingIndexes(GenerationCase):
    """foundation/0004 R42 and R44 — derived, never authored."""

    def test_produced_source_binds_through_the_manifest(self) -> None:
        index = gc.binding_indexes(self.manifest, self.out)
        for artifact in self.manifest["artifacts"]:
            self.assertIn(artifact["path"], index["produced"][artifact["ko"]])

    def test_reverse_impact_is_answered_from_the_index(self) -> None:
        """R44: a hand-maintained mapping from knowledge to code must not exist."""
        index = gc.binding_indexes(self.manifest, self.out)
        one = self.manifest["artifacts"][0]
        self.assertIn(one["path"], index["reverse"][one["ko"]])

    def test_hand_authored_source_binds_through_its_own_declaration(self) -> None:
        with tempfile.TemporaryDirectory() as holder:
            tree = Path(holder) / "out"
            shutil.copytree(self.out, tree)
            (tree / "extension.ts").write_text(
                "// siegard:binds ko.rule.billing.invoice-amount\nexport const extra = 1;\n"
            )
            index = gc.binding_indexes(self.manifest, tree)
        self.assertIn("extension.ts", index["authored"]["ko.rule.billing.invoice-amount"])

    def test_no_index_file_is_committed(self) -> None:
        """Both are derived. A committed one would be the hand-maintained map R44 forbids."""
        for name in ("binding-index.json", "reverse-index.json"):
            self.assertFalse((REPO_ROOT / "fixtures" / "generation-run" / name).exists())


if __name__ == "__main__":
    unittest.main()


class JudgedTrack(GenerationCase):
    """foundation/0004 R3 — what replaces byte identity where a model produces the artifact.

    The artifact is *recorded* rather than produced by an agent, exactly as the results in
    `fixtures/knowledge-change-loop/` are. What that leaves testable is the half R3 specifies: a
    judged artifact is verified against a conformance suite generated from the knowledge base, and
    one with no covering suite is not accepted output.
    """

    def setUp(self) -> None:
        import verify_judged

        self.verify_judged = verify_judged

    def test_the_recorded_validator_satisfies_its_suite(self) -> None:
        problems, checked = self.verify_judged.verify(self.recipe)
        self.assertEqual([], problems)
        self.assertGreater(checked, 0, "a suite with no cases proves nothing")

    def test_the_suite_comes_from_the_knowledge_object(self) -> None:
        """foundation/0004 R36: generated from rule.examples, never authored beside the validator."""
        from knowledge_graph_lib import load

        graph = load(REPO_ROOT / self.recipe["knowledge_root"])
        node = graph.nodes[self.recipe["judged"][0]["ko"]]
        self.assertEqual(len(node.data["examples"]), len(self.verify_judged.cases(node.data)))

    def test_a_validator_contradicting_the_knowledge_fails(self) -> None:
        with tempfile.TemporaryDirectory() as holder:
            wrong = Path(holder) / "wrong.py"
            wrong.write_text("def check(given):\n    return 'allowed'\n")
            altered = dict(self.recipe)
            altered["judged"] = [dict(self.recipe["judged"][0], artifact=str(wrong))]
            problems, _ = self.verify_judged.verify(altered)
        self.assertTrue(any("states 'rejected'" in p for p in problems), problems)

    def test_a_judged_artifact_with_no_covering_suite_is_refused(self) -> None:
        """R3: an artifact with no covering suite is not accepted output."""
        altered = dict(self.recipe)
        altered["judged"] = [
            dict(self.recipe["judged"][0], ko="ko.rule.sales.proposal-validity")
        ]
        problems, _ = self.verify_judged.verify(altered)
        self.assertTrue(any("no covering suite" in p for p in problems), problems)

    def test_a_lifecycle_generates_its_suite_from_totality(self) -> None:
        """R36's second source: every recorded rejection is a decided fact a validator must hold."""
        from knowledge_graph_lib import load

        graph = load(REPO_ROOT / self.recipe["knowledge_root"])
        lifecycle = graph.nodes["ko.lifecycle.billing.invoice"].data
        suite = self.verify_judged.cases(lifecycle)
        self.assertTrue(suite)
        self.assertTrue(all(expected == "rejected" for _given, expected in suite))

    def test_the_recorded_status_of_the_artifact_is_stated(self) -> None:
        """No agent ran. A fixture that let that be assumed would be the wrong kind of evidence."""
        self.assertIn("no agent ran", self.recipe["judged"][0]["recorded"])
