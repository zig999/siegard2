"""Every command this framework ships answers `--help`, and answers it with its own docstring.

Six of the first seven parsed their arguments by hand and exposed no `--help` at all: the syntax lived
in the module docstring, so a person reaching for `trace.py --replace` — an operation this
framework states is theirs to run directly, never a skill's — got `cannot run: expected [--check
[--all]] <target-root>` and had to open the source to find the form. That is friction a consumer
reported paying repeatedly.

What is asserted here is not that a flag exists but that it prints the docstring: a `--help` that
grew its own text would be a second home for the usage, and the day the two disagree the one a
person reads is the one nobody validates.
"""
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import pytest

BIN = Path(__file__).resolve().parent.parent / "src/claude/bin"
COMMANDS = sorted(p.name for p in BIN.glob("*.py"))


def docstring_of(name: str) -> str:
    return ast.get_docstring(ast.parse((BIN / name).read_text(encoding="utf-8"))) or ""


def run(name: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(BIN / name), *args],
                          capture_output=True, text=True)


def test_every_shipped_command_is_covered_here():
    # The parametrisation reads the directory, so a script added later is held to this without
    # anyone remembering to list it. This asserts the directory is not empty and not surprising —
    # a glob that silently matched nothing would make every test below vacuously green.
    assert len(COMMANDS) == 9, COMMANDS


@pytest.mark.parametrize("name", COMMANDS)
def test_help_exits_zero(name):
    result = run(name, "--help")
    assert result.returncode == 0, f"{name} --help: {result.stderr or result.stdout}"


@pytest.mark.parametrize("name", COMMANDS)
def test_help_prints_the_docstring_rather_than_a_second_copy(name):
    doc = docstring_of(name)
    assert "Usage:" in doc, f"{name} states no usage in its docstring"
    printed = run(name, "--help").stdout
    assert doc.splitlines()[0] in printed, \
        f"{name} --help does not print its own docstring; a second usage text is a second home"
    for line in doc.splitlines():
        if line.startswith("Usage:") or line.startswith("Exit:"):
            assert line in printed, f"{name} --help omits {line!r} from its own docstring"


@pytest.mark.parametrize("name", COMMANDS)
def test_help_answers_before_the_arguments_are_judged(name):
    # A person reaching for --help has, by definition, not got the arguments right yet. Answering
    # `cannot run` to someone asking what to run is the friction this exists to end.
    result = run(name, "--help", "--check", "no-such-directory")
    assert result.returncode == 0, f"{name}: {result.stderr or result.stdout}"
    # Read on stderr, not stdout: every refusal this framework prints goes there, and the
    # docstring being printed carries the words "cannot run" in its own Exit: block.
    assert result.stderr == "", f"{name} refused the arguments instead of answering: {result.stderr}"
