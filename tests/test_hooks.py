"""The first shipped hook, in both directions and on every way it can fail.

`docs/bootstrap.md` open question 5 asked for "the first hook or script exercising 'validate
before acting' and 'reject rather than repair' under test". `specs/0006` condition 3 asked for a
hook enforcing a guarantee with both outcomes covered.

The guarantee is `specs/0003` R42 and R51: a knowledge projection is derived and never
hand-edited. It existed only as `project_knowledge.py --check`, in a Makefile a consumer may
never run.

`decide()` is pure, so the denial logic is tested without a harness. The process boundary is
tested separately, because `specs/0010` R2 makes the *exit code* the decision — a hook that
reasoned correctly and exited 1 would permit exactly what it was written to prevent.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HOOK = REPO_ROOT / "dist" / ".claude" / "hooks" / "reject-derived-write.py"
HOOKS_JSON = REPO_ROOT / "dist" / ".claude" / "hooks" / "hooks.json"

sys.path.insert(0, str(REPO_ROOT / "src" / "claude" / "hooks"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import derived_artifacts
import project_knowledge


def payload(tool: str = "Write", path: str | None = "knowledge/index.md") -> dict:
    entry: dict = {"hook_event_name": "PreToolUse", "tool_name": tool}
    if path is not None:
        entry["tool_input"] = {"file_path": path}
    return entry


def invoke(body, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-B", str(HOOK)],
        input=body if isinstance(body, str) else json.dumps(body),
        capture_output=True,
        text=True,
        cwd=cwd,
    )


class DerivedSet(unittest.TestCase):
    """One authority for what is derived — the hook and the materializer must not each hold one."""

    def test_the_materializer_produces_exactly_the_declared_set(self) -> None:
        graph = project_knowledge.load(REPO_ROOT / "fixtures" / "knowledge-two-context" / "knowledge")
        self.assertEqual(derived_artifacts.DERIVED_NAMES, set(project_knowledge.outputs(graph)))

    def test_a_derived_name_inside_knowledge_is_derived(self) -> None:
        for name in derived_artifacts.DERIVED_NAMES:
            self.assertTrue(derived_artifacts.is_derived(f"knowledge/{name}"), name)

    def test_the_same_name_elsewhere_is_not(self) -> None:
        """A repository's own `index.md` is not a projection, and refusing it would be a nuisance."""
        self.assertFalse(derived_artifacts.is_derived("docs/index.md"))
        self.assertFalse(derived_artifacts.is_derived("index.md"))

    def test_an_authored_knowledge_object_is_not_derived(self) -> None:
        self.assertFalse(derived_artifacts.is_derived("knowledge/rule/sales/x.md"))

    def test_a_nested_knowledge_root_still_counts(self) -> None:
        self.assertTrue(derived_artifacts.is_derived("services/billing/knowledge/graph.json"))


class Decision(unittest.TestCase):
    """The pure half."""

    def setUp(self) -> None:
        import importlib

        self.hook = importlib.import_module("reject-derived-write".replace("-", "_")) if False else None
        # The module name has hyphens, so it is loaded by path rather than by import.
        import importlib.util

        spec = importlib.util.spec_from_file_location("reject_derived_write", HOOK)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.hook = module
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__("shutil").rmtree(self.root, ignore_errors=True))

    def decide(self, body: dict) -> tuple[int, str]:
        return self.hook.decide(body, self.root)

    def test_a_write_to_a_projection_is_denied(self) -> None:
        code, reason = self.decide(payload())
        self.assertEqual(self.hook.DENY, code)
        self.assertIn("knowledge/index.md", reason)

    def test_a_write_to_an_authored_object_is_allowed(self) -> None:
        code, _ = self.decide(payload(path="knowledge/rule/sales/x.md"))
        self.assertEqual(self.hook.ALLOW, code)

    def test_every_writing_tool_is_covered(self) -> None:
        for tool in sorted(self.hook.WRITING_TOOLS):
            with self.subTest(tool=tool):
                code, _ = self.decide(payload(tool=tool))
                self.assertEqual(self.hook.DENY, code)

    def test_a_non_writing_tool_is_not_this_hook_s_business(self) -> None:
        """specs/0006 R7: one hook, one guarantee."""
        code, _ = self.decide(payload(tool="Read"))
        self.assertEqual(self.hook.ALLOW, code)

    def test_a_missing_tool_name_is_denied(self) -> None:
        """R9: the matcher is a filter, not a guarantee."""
        code, _ = self.decide({"tool_input": {"file_path": "knowledge/index.md"}})
        self.assertEqual(self.hook.DENY, code)

    def test_a_writing_tool_with_no_path_is_denied(self) -> None:
        code, reason = self.decide(payload(path=None))
        self.assertEqual(self.hook.DENY, code)
        self.assertIn("no file path", reason)

    def test_a_path_escaping_the_tree_is_denied(self) -> None:
        """R8: every field is untrusted, including the path."""
        code, reason = self.decide(payload(path="../../../etc/knowledge/index.md"))
        self.assertEqual(self.hook.DENY, code)
        self.assertIn("does not resolve inside", reason)

    def test_an_absolute_path_outside_the_tree_is_denied(self) -> None:
        code, _ = self.decide(payload(path="/etc/knowledge/index.md"))
        self.assertEqual(self.hook.DENY, code)

    def test_an_absolute_path_inside_the_tree_is_judged(self) -> None:
        code, _ = self.decide(payload(path=str(self.root / "knowledge" / "index.md")))
        self.assertEqual(self.hook.DENY, code)

    def test_the_reason_is_a_statement_and_not_an_instruction(self) -> None:
        """specs/0010 R14: instruction-shaped text is a prompt-injection surface."""
        _code, reason = self.decide(payload())
        opener = reason.split()[0]
        self.assertNotIn(opener.lower(), {"change", "edit", "run", "do", "use", "regenerate", "please"})

    def test_the_reason_names_the_artifact_rather_than_embedding_it(self) -> None:
        """specs/0010 R13."""
        _code, reason = self.decide(payload())
        self.assertLess(len(reason), self.hook.MAX_REASON)


class Process(unittest.TestCase):
    """The exit code is the decision — specs/0010 R2."""

    def setUp(self) -> None:
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        self.cwd = Path(holder.name)
        (self.cwd / "knowledge").mkdir()

    def test_denial_exits_two_and_not_one(self) -> None:
        result = invoke(payload(), self.cwd)
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertIn("derived projection", result.stderr)

    def test_an_allowed_write_exits_zero_and_says_nothing(self) -> None:
        result = invoke(payload(path="knowledge/rule/x.md"), self.cwd)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("", result.stderr)

    def test_malformed_input_fails_closed(self) -> None:
        """R3: an unreadable payload is not a permitted one."""
        result = invoke("this is not json", self.cwd)
        self.assertEqual(2, result.returncode)

    def test_a_json_array_fails_closed(self) -> None:
        result = invoke("[]", self.cwd)
        self.assertEqual(2, result.returncode)

    def test_empty_input_fails_closed(self) -> None:
        result = invoke("", self.cwd)
        self.assertEqual(2, result.returncode)

    def test_it_repairs_nothing(self) -> None:
        """R4 and CLAUDE.md Security: it rejects, it does not fix."""
        before = sorted(p.name for p in self.cwd.rglob("*"))
        invoke(payload(), self.cwd)
        self.assertEqual(before, sorted(p.name for p in self.cwd.rglob("*")))

    def test_it_writes_nothing_to_stdout(self) -> None:
        """stdout is the harness's channel; a decision belongs on stderr with the exit code."""
        self.assertEqual("", invoke(payload(), self.cwd).stdout)


class Shipped(unittest.TestCase):
    """What the distribution carries, against what specs/0010 requires of it."""

    def setUp(self) -> None:
        self.document = json.loads(HOOKS_JSON.read_text())

    def test_hooks_json_ships(self) -> None:
        """specs/0008 R3: in force while the plugin is enabled."""
        self.assertTrue(HOOKS_JSON.is_file())

    def test_every_handler_is_a_command(self) -> None:
        """specs/0010 R1: prompt and agent handlers evaluate with a model."""
        for entries in self.document["hooks"].values():
            for entry in entries:
                for handler in entry["hooks"]:
                    self.assertEqual("command", handler["type"])

    def test_every_hook_states_its_own_timeout(self) -> None:
        """specs/0010 R11: the 600-second default is long enough to look like a hung session."""
        for entries in self.document["hooks"].values():
            for entry in entries:
                for handler in entry["hooks"]:
                    self.assertIn("timeout", handler)
                    self.assertLess(handler["timeout"], 600)

    def test_it_binds_an_event_that_can_block(self) -> None:
        """specs/0010 R12: a guarantee bound to an event that cannot deny is one that logs."""
        self.assertEqual(["PreToolUse"], sorted(self.document["hooks"]))

    def test_the_command_resolves_through_the_plugin_root(self) -> None:
        handler = self.document["hooks"]["PreToolUse"][0]["hooks"][0]
        self.assertTrue(handler["command"].startswith("${CLAUDE_PLUGIN_ROOT}/hooks/"))

    def test_the_matcher_covers_every_tool_the_hook_judges(self) -> None:
        """R9 says the hook re-validates; the matcher should still not under-select."""
        import importlib.util

        spec = importlib.util.spec_from_file_location("reject_derived_write", HOOK)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        matcher = self.document["hooks"]["PreToolUse"][0]["matcher"]
        self.assertEqual(module.WRITING_TOOLS, set(matcher.split("|")))


class ConsumerKeepsTheGuarantee(unittest.TestCase):
    """specs/0010 R16 and R17: the hook is a checkpoint, not a proof."""

    def test_the_check_still_fails_on_a_hand_edited_projection_with_no_hook(self) -> None:
        import shutil

        with tempfile.TemporaryDirectory() as holder:
            root = Path(holder) / "knowledge"
            shutil.copytree(REPO_ROOT / "fixtures" / "knowledge-two-context" / "knowledge", root)
            (root / "index.md").write_text("hand edited, with no hook anywhere near it\n")
            code, problems = project_knowledge.run(root, check=True)
        self.assertEqual(1, code)
        self.assertTrue(problems)


if __name__ == "__main__":
    unittest.main()
