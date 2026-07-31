"""Installation and upgrade, over the three behaviours `foundation/0008` states and nothing held.

R16 makes enabling the same version twice leave the repository as one enabling did. R17 forbids
an upgrade from silently overwriting a file the consumer changed — it detects, names, and stops.
R21 requires the framework to *report* a project agent shadowing a plugin agent rather than to
prevent it by choosing an unlikely name.

Each is asserted in both directions, because the rejection alone would pass over a script that
refuses everything. The clean installation is checked first in every class for that reason.

What this suite does not claim: that Claude Code loads any of it. Installing the tree and having
the harness resolve a capability from it are different facts, and only the second closes ADR-0009
condition 2. Nothing here is evidence for it.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import install_dist

REPO_ROOT = Path(__file__).resolve().parent.parent
DIST = REPO_ROOT / "dist" / ".claude"
SCRIPT = REPO_ROOT / "src" / "claude" / "bin" / "install_dist.py"


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-B", str(SCRIPT), *args], capture_output=True, text=True
    )


class Consumer(unittest.TestCase):
    """A disposable repository with nowhere for the plugin yet."""

    def setUp(self) -> None:
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        self.project = Path(holder.name) / "consumer"
        self.plugin = self.project / ".claude" / "plugins" / "siegard"
        self.project.mkdir(parents=True)

    def install(self) -> subprocess.CompletedProcess:
        return run("install", "--source", str(DIST), "--target", str(self.plugin))

    def upgrade(self, source: Path = DIST) -> subprocess.CompletedProcess:
        return run("upgrade", "--source", str(source), "--target", str(self.plugin))

    def snapshot(self) -> dict[str, bytes]:
        return install_dist.tree(self.plugin)


class Installation(Consumer):
    def test_a_clean_install_places_the_whole_distribution(self) -> None:
        result = self.install()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(install_dist.tree(DIST), self.snapshot())

    def test_it_reports_the_version_it_installed(self) -> None:
        """foundation/0008 R13: a consumer reads the installed version from plugin.json."""
        result = self.install()
        version = json.loads((DIST / ".claude-plugin" / "plugin.json").read_text())["version"]
        self.assertIn(version, result.stdout)

    def test_nothing_is_written_outside_the_target(self) -> None:
        """foundation/0008 R22: the framework claims no path outside its own plugin root."""
        self.install()
        outside = {p for p in self.project.rglob("*") if p.is_file()}
        self.assertTrue(all(str(p).startswith(str(self.plugin)) for p in outside))

    def test_installing_over_a_populated_target_is_refused(self) -> None:
        self.install()
        result = self.install()
        self.assertEqual(1, result.returncode)
        self.assertIn("not empty", result.stderr)

    def test_a_refused_install_changes_nothing(self) -> None:
        self.install()
        before = self.snapshot()
        self.install()
        self.assertEqual(before, self.snapshot())

    def test_a_source_without_a_manifest_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as holder:
            result = run("install", "--source", holder, "--target", str(self.plugin))
        self.assertEqual(2, result.returncode)
        self.assertIn("siegard-manifest.json", result.stderr)


class Idempotence(Consumer):
    """foundation/0008 R16."""

    def test_upgrading_to_the_same_version_is_a_no_op(self) -> None:
        self.install()
        before = self.snapshot()
        result = self.upgrade()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("nothing to do", result.stdout)
        self.assertEqual(before, self.snapshot())

    def test_two_installs_into_separate_targets_agree(self) -> None:
        self.install()
        with tempfile.TemporaryDirectory() as holder:
            other = Path(holder) / "plugin"
            run("install", "--source", str(DIST), "--target", str(other))
            self.assertEqual(self.snapshot(), install_dist.tree(other))


class Divergence(Consumer):
    """foundation/0008 R17."""

    def diverge(self) -> Path:
        path = self.plugin / "agents" / "concept-author.md"
        path.write_text(path.read_text() + "\n<!-- the consumer's own note -->\n")
        return path

    def test_an_untouched_installation_reports_none(self) -> None:
        self.install()
        self.assertEqual([], install_dist.divergences(self.plugin))

    def test_a_changed_file_is_detected_and_named(self) -> None:
        self.install()
        self.diverge()
        found = install_dist.divergences(self.plugin)
        self.assertTrue(
            any("agents/concept-author.md" in note for note in found), found
        )

    def test_an_upgrade_stops_on_divergence(self) -> None:
        self.install()
        self.diverge()
        result = self.upgrade()
        self.assertEqual(1, result.returncode)
        self.assertIn("agents/concept-author.md", result.stderr)

    def test_the_consumer_change_survives_the_refusal(self) -> None:
        """A refusal that erased the thing it refused to erase would be the defect R17 names."""
        self.install()
        path = self.diverge()
        expected = path.read_text()
        self.upgrade()
        self.assertEqual(expected, path.read_text())

    def test_a_deleted_file_is_detected(self) -> None:
        self.install()
        (self.plugin / "agents" / "concept-author.md").unlink()
        found = install_dist.divergences(self.plugin)
        self.assertTrue(any("missing from disk" in note for note in found), found)

    def test_an_added_file_is_detected(self) -> None:
        self.install()
        (self.plugin / "agents" / "smuggled.md").write_text("---\nname: smuggled\n---\nx\n")
        found = install_dist.divergences(self.plugin)
        self.assertTrue(any("smuggled" in note for note in found), found)

    def test_runtime_bytecode_is_not_a_divergence(self) -> None:
        """A consumer who runs a shipped executable once must still be able to upgrade."""
        self.install()
        cache = self.plugin / "bin" / "__pycache__"
        cache.mkdir()
        (cache / "workflow_lib.cpython-312.pyc").write_bytes(b"\x00")
        self.assertEqual([], install_dist.divergences(self.plugin))

    def test_an_upgrade_to_a_newer_revision_replaces_the_tree(self) -> None:
        self.install()
        with tempfile.TemporaryDirectory() as holder:
            newer = Path(holder) / "dist"
            shutil.copytree(DIST, newer)
            manifest = json.loads((newer / install_dist.MANIFEST_NAME).read_text())
            manifest["source_revision"] = "sha256:" + "0" * 64
            (newer / install_dist.MANIFEST_NAME).write_text(json.dumps(manifest, indent=2) + "\n")
            result = self.upgrade(newer)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("upgraded", result.stdout)

    def test_upgrading_an_absent_installation_is_refused(self) -> None:
        result = self.upgrade()
        self.assertEqual(1, result.returncode)
        self.assertIn("nothing to upgrade", result.stderr)


class Shadowing(Consumer):
    """foundation/0008 R21, and ADR-0012's choice to report rather than rename."""

    def add_project_agent(self, name: str) -> None:
        agents = self.project / ".claude" / "agents"
        agents.mkdir(parents=True, exist_ok=True)
        (agents / f"{name}.md").write_text(
            f"---\nname: {name}\ndescription: The consumer's own.\ntools: Read\n---\n\nLocal.\n"
        )

    def test_no_project_agents_means_no_shadowing(self) -> None:
        self.install()
        self.assertEqual([], install_dist.shadowed(self.plugin, self.project))

    def test_an_unrelated_project_agent_is_not_shadowing(self) -> None:
        self.install()
        self.add_project_agent("something-else-entirely")
        self.assertEqual([], install_dist.shadowed(self.plugin, self.project))

    def test_a_same_named_project_agent_is_reported(self) -> None:
        self.install()
        self.add_project_agent("concept-author")
        found = install_dist.shadowed(self.plugin, self.project)
        self.assertEqual(1, len(found), found)
        self.assertIn("concept-author", found[0])
        self.assertIn("not reachable", found[0])

    def test_every_shipped_agent_can_be_shadowed(self) -> None:
        self.install()
        manifest = json.loads((self.plugin / install_dist.MANIFEST_NAME).read_text())
        shipped = [c["name"] for c in manifest["capabilities"] if c["class"] == "specialized-agent"]
        self.assertGreaterEqual(len(shipped), 2, "the fixture should cover more than one agent")
        for name in shipped:
            self.add_project_agent(name)
        self.assertEqual(len(shipped), len(install_dist.shadowed(self.plugin, self.project)))


class ShippedAgents(unittest.TestCase):
    """The two agents the distribution now carries, and what their contracts require."""

    def setUp(self) -> None:
        self.manifest = json.loads((DIST / install_dist.MANIFEST_NAME).read_text())
        self.agents = {
            c["name"]: c for c in self.manifest["capabilities"] if c["class"] == "specialized-agent"
        }

    def test_every_authored_agent_ships(self) -> None:
        """Derived rather than listed: authoring an agent with a fixture should not edit a test.

        This read `== {"concept-author", "impact-analyst"}` until `knowledge-author` arrived. The
        property worth holding is that the distribution carries every agent a fixture exercises,
        not that it carries a particular two.
        """
        authored = {p.stem for p in (REPO_ROOT / "src" / "claude" / "agents").glob("*.md")}
        self.assertEqual(authored, set(self.agents))

    def test_more_than_one_agent_ships(self) -> None:
        """A derived assertion over an empty set would pass; this is what keeps it honest."""
        self.assertGreaterEqual(len(self.agents), 2)

    def test_no_agent_has_a_shell(self) -> None:
        """foundation/0006 R6, and the reason: a guarantee a producer self-reports is not one."""
        for name in self.agents:
            body = (DIST / "agents" / f"{name}.md").read_text()
            tools = next(l for l in body.splitlines() if l.startswith("tools:"))
            self.assertNotIn("Bash", tools, name)

    def test_the_impact_analyst_is_read_only(self) -> None:
        body = (DIST / "agents" / "impact-analyst.md").read_text()
        tools = next(l for l in body.splitlines() if l.startswith("tools:"))
        for writer in ("Write", "Edit", "NotebookEdit"):
            self.assertNotIn(writer, tools)


if __name__ == "__main__":
    unittest.main()
