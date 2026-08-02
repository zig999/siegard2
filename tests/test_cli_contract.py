"""The exit-code convention every script documents, held to what it says.

Fourteen scripts state `Exit: ... 2 cannot run`, and every one reached that path through
`sys.exit("cannot run: ...")`, which exits **1** — the same code they use for "I ran, and what I
checked is wrong". The documented distinction did not exist anywhere.

`make validate` never noticed, because it treats any non-zero as a failure. That is the argument
for fixing it rather than deleting it from the docstrings: this repository does not keep a stated
contract that nothing honours — until a
condition holds, report a rule as not run rather than as satisfied.

The last test is the one that keeps this from rotting: it reads every script's own docstring and
asserts that a script claiming exit 2 has a route to it.
"""

from __future__ import annotations

import ast
import subprocess
import sys
import unittest
from pathlib import Path

from cli import CANNOT_RUN, cannot_run

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "scripts"


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", *args], capture_output=True, text=True)


class Helper(unittest.TestCase):
    def test_it_exits_two(self) -> None:
        with self.assertRaises(SystemExit) as caught:
            cannot_run("cannot run: nothing is installed")
        self.assertEqual(CANNOT_RUN, caught.exception.code)

    def test_it_prefixes_a_message_that_lacks_the_marker(self) -> None:
        result = run("-c", "import sys; sys.path.insert(0, sys.argv[1]); "
                           "from cli import cannot_run; cannot_run('the root is absent')",
                     str(SCRIPTS))
        self.assertEqual(CANNOT_RUN, result.returncode)
        self.assertTrue(result.stderr.startswith("cannot run:"), result.stderr)

    def test_it_does_not_double_the_marker(self) -> None:
        result = run("-c", "import sys; sys.path.insert(0, sys.argv[1]); "
                           "from cli import cannot_run; cannot_run('cannot run: already said')",
                     str(SCRIPTS))
        self.assertEqual(1, result.stderr.count("cannot run"), result.stderr)

    def test_it_writes_to_stderr_and_not_stdout(self) -> None:
        result = run("-c", "import sys; sys.path.insert(0, sys.argv[1]); "
                           "from cli import cannot_run; cannot_run('gone')",
                     str(SCRIPTS))
        self.assertEqual("", result.stdout)


class RealScripts(unittest.TestCase):
    """The three exit codes, distinguished, on scripts that actually run."""

    def test_a_clean_run_exits_zero(self) -> None:
        result = run(str(SCRIPTS / "validate_concepts.py"), str(REPO_ROOT / "docs" / "concepts"))
        self.assertEqual(0, result.returncode, result.stderr)

    def test_a_failed_check_exits_one(self) -> None:
        """Distinct from 2: something ran and found a problem."""
        result = run(str(SCRIPTS / "verify_dist.py"), str(REPO_ROOT / "schemas"))
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)

    def test_an_absent_root_exits_two(self) -> None:
        result = run(str(SCRIPTS / "validate_concepts.py"), "/definitely/not/here")
        self.assertEqual(CANNOT_RUN, result.returncode, result.stderr)
        self.assertIn("cannot run", result.stderr)

    def test_an_absent_distribution_exits_two(self) -> None:
        result = run(str(SCRIPTS / "verify_dist.py"), "/definitely/not/here")
        self.assertEqual(CANNOT_RUN, result.returncode, result.stderr)

    def test_a_bad_argument_exits_two(self) -> None:
        result = run(str(SCRIPTS / "check_contract_versions.py"), "--nonsense")
        self.assertEqual(CANNOT_RUN, result.returncode, result.stderr)


class DocstringAgreement(unittest.TestCase):
    """A script claiming exit 2 must have a route to it."""

    def scripts_claiming_two(self) -> list[Path]:
        found = []
        for path in sorted(SCRIPTS.glob("*.py")):
            doc = ast.get_docstring(ast.parse(path.read_text())) or ""
            if "2 cannot run" in doc:
                found.append(path)
        return found

    def test_the_claim_is_widespread_enough_to_be_worth_checking(self) -> None:
        self.assertGreaterEqual(len(self.scripts_claiming_two()), 10)

    def test_every_script_claiming_exit_two_can_reach_it(self) -> None:
        without = []
        for path in self.scripts_claiming_two():
            text = path.read_text()
            if "cannot_run(" not in text and "SystemExit(CANNOT_RUN)" not in text:
                without.append(path.name)
        self.assertEqual([], without, "these document exit 2 and have no route to it")

    def test_no_script_still_exits_one_while_saying_cannot_run(self) -> None:
        """Read by AST, not by grep: `cli.py` quotes the defective form in its own docstring."""
        offenders = []
        for path in sorted(SCRIPTS.glob("*.py")):
            for node in ast.walk(ast.parse(path.read_text())):
                if not isinstance(node, ast.Call) or not node.args:
                    continue
                target = node.func
                is_sys_exit = (
                    isinstance(target, ast.Attribute)
                    and target.attr == "exit"
                    and isinstance(target.value, ast.Name)
                    and target.value.id == "sys"
                )
                if not is_sys_exit:
                    continue
                first = node.args[0]
                text = (
                    first.value
                    if isinstance(first, ast.Constant) and isinstance(first.value, str)
                    else "".join(
                        v.value
                        for v in getattr(first, "values", [])
                        if isinstance(v, ast.Constant) and isinstance(v.value, str)
                    )
                    if isinstance(first, ast.JoinedStr)
                    else ""
                )
                if text.startswith("cannot run"):
                    offenders.append(f"{path.name}:{node.lineno}")
        self.assertEqual([], offenders, "sys.exit(str) exits 1, not 2")


if __name__ == "__main__":
    unittest.main()
