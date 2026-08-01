"""The generator's output contract, and the invariants that survive a bug in the generator.

`foundation/0008` fixes what the distribution may contain and leaves the assembly free. These tests
are the fixed half. They fall into two groups on purpose:

- what the generator produces, asserted against a freshly built tree;
- what any tree must hold, asserted by `verify_dist.check_invariants` against trees this suite
  breaks deliberately. A comparison against a regenerated tree cannot catch a generator that is
  *consistently* wrong — it produces the same defect twice and reports agreement — so the
  invariants are computed from the tree and never from the plan.

Four conditions were named for the generator: a generator `make dist` runs, two runs
producing identical output, a test that no source-only path reaches the output, and a test that no
secret or environment-specific value does. Each has a case here.
"""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
import unittest.mock
from pathlib import Path

import generate_dist

from . import (
    GENERATOR_SCHEMAS,
    GENERATOR_SCRIPTS,
    GENERATOR_TEMPLATES,
    SHIPPED_BIN,
    SHIPPED_SCHEMAS,
    SHIPPED_TEMPLATES,
)
import verify_dist

REPO_ROOT = Path(__file__).resolve().parent.parent
COMMITTED = REPO_ROOT / "dist" / ".claude"


class Built(unittest.TestCase):
    """One assembled tree, built once for the whole class."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._holder = tempfile.TemporaryDirectory()
        cls.root = Path(cls._holder.name) / "dist"
        cls.installed, cls.skipped = generate_dist.build(cls.root)
        cls.files = verify_dist.tree(cls.root)
        cls.manifest = json.loads((cls.root / "siegard-manifest.json").read_text())

    @classmethod
    def tearDownClass(cls) -> None:
        cls._holder.cleanup()


class Determinism(unittest.TestCase):
    def test_two_runs_over_the_same_source_are_byte_identical(self) -> None:
        """foundation/0008 R4: a difference is a defect in the generator, not a variation."""
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            generate_dist.build(Path(a) / "dist")
            generate_dist.build(Path(b) / "dist")
            self.assertEqual(verify_dist.tree(Path(a) / "dist"), verify_dist.tree(Path(b) / "dist"))

    def test_the_manifest_carries_no_timestamp(self) -> None:
        """The one field that would break R4; foundation/0008 R12 does not ask for it."""
        with tempfile.TemporaryDirectory() as holder:
            generate_dist.build(Path(holder) / "dist")
            manifest = json.loads((Path(holder) / "dist" / "siegard-manifest.json").read_text())
        self.assertNotIn("generated_at", manifest)

    def test_rebuilding_replaces_rather_than_accumulates(self) -> None:
        with tempfile.TemporaryDirectory() as holder:
            root = Path(holder) / "dist"
            generate_dist.build(root)
            (root / "agents" / "stale.md").write_text("left over from a previous build\n")
            generate_dist.build(root)
            self.assertFalse((root / "agents" / "stale.md").exists())


class Layout(Built):
    def test_the_plugin_manifest_is_present(self) -> None:
        """foundation/0008 R1: a plugin root is a directory holding `.claude-plugin/plugin.json`."""
        self.assertIn(".claude-plugin/plugin.json", self.files)

    def test_the_plugin_manifest_sets_an_explicit_version(self) -> None:
        """foundation/0008 R2: without one, every commit becomes a release."""
        plugin = json.loads(self.files[".claude-plugin/plugin.json"])
        self.assertTrue(plugin.get("version"))

    def test_only_plugin_json_is_inside_the_plugin_directory(self) -> None:
        inside = [p for p in self.files if p.startswith(".claude-plugin/")]
        self.assertEqual([".claude-plugin/plugin.json"], inside)

    def test_every_root_entry_is_in_the_closed_directory_set(self) -> None:
        roots = {p.split("/")[0] for p in self.files if "/" in p}
        self.assertLessEqual(roots, verify_dist.ALLOWED_ROOT)

    def test_no_empty_directory_ships(self) -> None:
        """foundation/0008 R7: an empty directory is omitted rather than shipped."""
        for directory in {p.parent for p in self.root.rglob("*") if p.is_file()}:
            self.assertTrue(any(directory.iterdir()))

    def test_a_directory_in_the_closed_set_with_no_occupant_is_absent(self) -> None:
        """foundation/0008 R7, derived rather than listed.

        This named `hooks` and `templates` until a hook shipped. The property is that every
        directory the closed set allows is either populated or absent — never present and empty —
        so occupying one should not mean editing this.
        """
        occupied = {p.split("/")[0] for p in self.files if "/" in p}
        for name in sorted(verify_dist.ALLOWED_ROOT - occupied):
            self.assertFalse((self.root / name).exists(), f"{name}/ shipped with nothing in it")

    def test_the_closed_set_is_fully_occupied(self) -> None:
        """Every directory foundation/0008 R7 allows now ships with something in it.

        This inverts what stood here. The old assertion required at least one allowed directory to
        be unoccupied, so that the emptiness check above had something to check; `templates/` was
        the last one empty, and populating it on 2026-07-31 made that guard fail. It failed
        correctly: the distribution now fills its whole declared layout, and the emptiness check
        is vacuous *because there is nothing left to omit*. Stating that here keeps the vacuity
        recorded rather than silent — if a future R7 adds a directory, this fails until it ships.
        """
        occupied = {p.split("/")[0] for p in self.files if "/" in p}
        self.assertEqual(set(), verify_dist.ALLOWED_ROOT - occupied)

    def test_no_rules_and_no_packs(self) -> None:
        """foundation/0008 R10 and R23."""
        self.assertFalse((self.root / "rules").exists())
        self.assertFalse((self.root / "packs").exists())


class Provenance(Built):
    def test_every_installed_file_names_a_source_that_exists(self) -> None:
        """foundation/0008 R5: no file is introduced that has no source."""
        for entry in self.manifest["installed"]:
            self.assertTrue(
                (REPO_ROOT / entry["source"]).is_file(), f"{entry['path']} names {entry['source']}"
            )

    def test_the_manifest_names_exactly_the_files_that_exist(self) -> None:
        self.assertEqual({e["path"] for e in self.manifest["installed"]}, set(self.files))

    def test_every_digest_matches_the_file_it_records(self) -> None:
        for entry in self.manifest["installed"]:
            if entry["path"] == "siegard-manifest.json":
                continue
            self.assertEqual(entry["digest"], generate_dist.digest(self.files[entry["path"]]))

    def test_a_removed_source_disappears_from_the_output(self) -> None:
        """foundation/0008 R5: no file survives whose source was removed."""
        with tempfile.TemporaryDirectory() as holder:
            moved = Path(holder) / "concept-author.md"
            live = REPO_ROOT / "src" / "claude" / "agents" / "concept-author.md"
            shutil.move(live, moved)
            try:
                root = Path(holder) / "dist"
                generate_dist.build(root)
                files = verify_dist.tree(root)
            finally:
                shutil.move(moved, live)
        self.assertNotIn("agents/concept-author.md", files)
        self.assertFalse((root / "agents").exists(), "agents/ shipped empty after its only file left")

    def test_the_source_revision_is_content_addressed(self) -> None:
        """Not a commit SHA: committing the distribution would otherwise invalidate it."""
        self.assertRegex(self.manifest["source_revision"], r"^sha256:[0-9a-f]{64}$")


class ShippedSelection(unittest.TestCase):
    """What ships is decided by location, and these are the properties that makes true.

    The trees do not overlap, and the generator's own artifacts stay out of the one that
    ships. Classifying a mixed tree file by file would assert the same thing against a table
    instead, which is a second place for a fact the filesystem already holds.
    """

    def test_the_two_trees_are_disjoint(self) -> None:
        for tree, shipped, generator in (
            ("schemas", SHIPPED_SCHEMAS, GENERATOR_SCHEMAS),
            ("templates", SHIPPED_TEMPLATES, GENERATOR_TEMPLATES),
            ("scripts", SHIPPED_BIN, GENERATOR_SCRIPTS),
        ):
            with self.subTest(tree=tree):
                a = {p.name for p in shipped.iterdir() if p.is_file()}
                b = {p.name for p in generator.iterdir() if p.is_file()}
                self.assertEqual(set(), a & b, f"{tree}: a file sits in both trees")

    def test_the_generators_own_contracts_stay_out_of_the_shipped_tree(self) -> None:
        """A governed repository writes no specification, ADR, or framework component."""
        for name in ("spec.json", "adr.json", "skill.json", "agent.json"):
            with self.subTest(schema=name):
                self.assertFalse((SHIPPED_SCHEMAS / name).exists(), name)
                self.assertTrue((GENERATOR_SCHEMAS / name).is_file(), name)

    def test_every_shipped_schema_reaches_the_distribution(self) -> None:
        """Location is the decision, so the source tree and the output must agree exactly."""
        files, _capabilities, _skipped = generate_dist.plan()
        installed = {p["path"] for p in files if p["path"].startswith("schemas/")}
        self.assertEqual({f"schemas/{p.name}" for p in SHIPPED_SCHEMAS.glob("*.json")}, installed)


class CapabilityStatus(Built):
    def test_every_recorded_capability_is_active(self) -> None:
        """foundation/0006 R14: proposed ships nothing and retired is absent from the distribution."""
        for capability in self.manifest["capabilities"]:
            self.assertEqual("active", capability["status"], capability["name"])

    def test_every_capability_points_at_an_installed_file(self) -> None:
        for capability in self.manifest["capabilities"]:
            self.assertIn(capability["path"], self.files, capability["name"])

    def test_a_component_with_no_fixture_still_ships(self) -> None:
        """foundation/0006 R11: a fixture is evidence, never a gate.

        Gating on a fixture would let an optional support tool decide what a consumer receives:
        authoring a component and forgetting a fixture would produce a distribution missing it,
        reported as a skip nobody watches for.
        """
        stray = REPO_ROOT / "src" / "claude" / "agents" / "no-fixture-names-this.md"
        stray.write_text(
            "---\nname: no-fixture-names-this\n"
            "description: Present only so a test can assert the generator ships it regardless.\n"
            "tools: Read\n---\n\nBody.\n"
        )
        self.addCleanup(stray.unlink)
        with tempfile.TemporaryDirectory() as holder:
            root = Path(holder) / "dist"
            _installed, skipped = generate_dist.build(root)
            files = verify_dist.tree(root)
        self.assertIn("agents/no-fixture-names-this.md", files)
        self.assertEqual([], skipped)


class Invariants(Built):
    """Deliberate defects, asserted against checks that never consult the generator."""

    def broken(self, mutate) -> list[str]:
        with tempfile.TemporaryDirectory() as holder:
            root = Path(holder) / "dist"
            shutil.copytree(self.root, root)
            mutate(root)
            return verify_dist.check_invariants(root, verify_dist.tree(root))

    def test_a_clean_tree_reports_nothing(self) -> None:
        self.assertEqual([], verify_dist.check_invariants(self.root, self.files))

    def test_a_source_only_path_is_reported(self) -> None:
        def plant(root: Path) -> None:
            (root / "foundation").mkdir()
            (root / "foundation" / "leaked.md").write_text("this belongs to the repository\n")

        self.assertTrue(any("source-only path" in p for p in self.broken(plant)))

    def test_a_credential_is_reported(self) -> None:
        def plant(root: Path) -> None:
            (root / "bin" / "leak.py").write_text('api_key = "AKIAIOSFODNN7EXAMPLE"\n')

        self.assertTrue(any("credential" in p for p in self.broken(plant)))

    def test_a_private_key_is_reported(self) -> None:
        def plant(root: Path) -> None:
            (root / "bin" / "id.pem").write_text("-----BEGIN PRIVATE KEY-----\nabc\n")

        self.assertTrue(any("credential" in p for p in self.broken(plant)))

    def test_an_environment_specific_path_is_reported(self) -> None:
        def plant(root: Path) -> None:
            (root / "bin" / "leak.py").write_text('ROOT = "/home/somebody/projects/thing"\n')

        self.assertTrue(any("environment-specific" in p for p in self.broken(plant)))

    def test_a_stray_file_in_the_plugin_directory_is_reported(self) -> None:
        def plant(root: Path) -> None:
            (root / ".claude-plugin" / "settings.json").write_text("{}\n")

        self.assertTrue(any("only plugin.json" in p for p in self.broken(plant)))

    def test_a_forbidden_directory_is_reported(self) -> None:
        def plant(root: Path) -> None:
            (root / "packs").mkdir()
            (root / "packs" / "one.json").write_text("{}\n")

        problems = self.broken(plant)
        self.assertTrue(any("R23" in p for p in problems), problems)

    def test_runtime_bytecode_is_not_reported_as_unmanaged(self) -> None:
        """A consumer who runs a shipped executable once has __pycache__ beside it. Reporting
        that as an unmanaged file would make every upgrade check fail after first use."""
        with tempfile.TemporaryDirectory() as holder:
            root = Path(holder) / "dist"
            shutil.copytree(self.root, root)
            (root / "bin" / "__pycache__").mkdir()
            (root / "bin" / "__pycache__" / "workflow_lib.cpython-312.pyc").write_bytes(b"\x00")
            files = verify_dist.tree(root)
            self.assertEqual([], verify_dist.check_invariants(root, files))
            self.assertEqual([], verify_dist.check_manifest(root, files))

    def test_a_directory_outside_the_closed_set_is_reported(self) -> None:
        def plant(root: Path) -> None:
            (root / "workers").mkdir()
            (root / "workers" / "one.md").write_text("x\n")

        self.assertTrue(any("closed directory set" in p for p in self.broken(plant)))


class CommittedDistribution(unittest.TestCase):
    """The tree in the repository, not a freshly built one."""

    def test_it_exists(self) -> None:
        self.assertTrue(COMMITTED.is_dir(), "run `make dist`")

    def test_it_matches_what_the_generator_produces(self) -> None:
        with tempfile.TemporaryDirectory() as holder:
            fresh = Path(holder) / "dist"
            generate_dist.build(fresh)
            self.assertEqual(verify_dist.tree(fresh), verify_dist.tree(COMMITTED))

    def test_it_holds_every_invariant(self) -> None:
        self.assertEqual([], verify_dist.check_invariants(COMMITTED, verify_dist.tree(COMMITTED)))

    def test_its_manifest_validates_and_agrees_with_the_tree(self) -> None:
        self.assertEqual([], verify_dist.check_manifest(COMMITTED, verify_dist.tree(COMMITTED)))


class ShippedExecutables(unittest.TestCase):
    """A shipped script must resolve its own schemas from the plugin root, not from this repo."""

    def test_a_shipped_module_resolves_schemas_beside_bin(self) -> None:
        """`bin/` and `schemas/` sit at the plugin root exactly as `scripts/` and `schemas/` do
        at the repository root, so `parent.parent / "schemas"` lands correctly in both. That is a
        structural correspondence rather than a coincidence, and this test is what keeps it one."""
        import subprocess
        import sys

        result = subprocess.run(
            [
                sys.executable,
                "-B",  # no bytecode: the distribution is verified byte for byte
                "-c",
                "import sys; sys.path.insert(0, sys.argv[1]); import knowledge_graph_lib as k; "
                "print(k.KO_SCHEMA_PATH.is_file())",
                str(COMMITTED / "bin"),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual("True", result.stdout.strip(), result.stderr)


if __name__ == "__main__":
    unittest.main()


class ShippedImports(unittest.TestCase):
    """A shipped script may only import modules that ship beside it.

    This check exists because the suite caught its absence: `orchestrate.py` gained
    `from cli import cannot_run` while `cli.py` was not shipped. The distribution built,
    verified, and would have failed on the consumer's first invocation.
    """

    def test_the_current_selection_is_closed_under_import(self) -> None:
        generate_dist.assert_imports_ship()  # raises Refused if it is not

    def test_importing_the_generators_own_module_is_refused(self) -> None:
        """The direction is the check: the generator may import the shipped tree, not back.

        Simulated by adding a module to the generator-only set rather than by writing a file
        into `src/claude/bin/`, so the assertion runs against the real tree and leaves it
        exactly as it found it.
        """
        target = SHIPPED_BIN / "knowledge_graph_lib.py"
        original = target.read_text()
        target.write_text("import verify_dist\n" + original)
        self.addCleanup(target.write_text, original)
        with self.assertRaises(generate_dist.Refused) as caught:
            generate_dist.assert_imports_ship()
        self.assertIn("ImportError", str(caught.exception))

    def test_every_shipped_script_imports_cleanly_from_the_distribution(self) -> None:
        """The end the check protects: the shipped copy actually loads."""
        import subprocess
        import sys

        for source in sorted(SHIPPED_BIN.glob("*.py")):
            name, module = source.name, source.stem
            result = subprocess.run(
                [sys.executable, "-B", "-c",
                 f"import sys; sys.path.insert(0, sys.argv[1]); import {module}",
                 str(COMMITTED / "bin")],
                capture_output=True, text=True,
            )
            self.assertEqual(0, result.returncode, f"{name}: {result.stderr}")
