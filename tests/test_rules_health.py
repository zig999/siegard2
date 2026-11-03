"""The session rules stay small, well-formed and true to what ships.

`src/claude/hooks/rules.md` is placed in every session and every agent of a consumer project, at
start and after every compaction; every line of it is paid in thousands of contexts. The rules
this repository's `CLAUDE.md` states for it under "The session rules" are held here where a test
can hold them: the size is a ratchet — the counts below are the file's own, a change that grows it
raises them in the same change and says why in its commit message, a change that shrinks it lowers
them — never past the 200 lines Anthropic's guidance for instruction files targets; each bullet
opens with its rule in bold; and every script, flag and schema the rules name ships. What no test
decides — whether a rule belongs in a skill, whether a bullet carries a why — is read by the change
that touches the file, starting from the longest bullet this file reports.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
RULES = REPO / "src/claude/hooks/rules.md"
BIN = REPO / "src/claude/bin"
SCHEMAS = REPO / "src/claude/schemas"

PINNED_LINES = 158
PINNED_CHARACTERS = 12407
GUIDANCE_CEILING_LINES = 200

SCRIPT_SPAN = re.compile(r"`bin/([a-z_]+)\.py([^`]*)`")
FLAG = re.compile(r"(?<![\w-])(--[a-z][a-z-]*)")
SCHEMA = re.compile(r"`schemas/([a-z0-9-]+\.json)`")


def text() -> str:
    return RULES.read_text(encoding="utf-8")


def bullets(body: str) -> list[tuple[int, str]]:
    """Each top-level bullet with the line it starts on, its continuation lines joined."""
    found: list[tuple[int, list[str]]] = []
    for number, line in enumerate(body.splitlines(), start=1):
        if line.startswith("- "):
            found.append((number, [line]))
        elif found and line.startswith("  ") and line.strip():
            found[-1][1].append(line)
        elif found and not line.strip():
            found.append((0, []))
    return [(number, "\n".join(lines)) for number, lines in found if number]


def test_the_size_is_the_pinned_one():
    body = text()
    lines, characters = len(body.splitlines()), len(body)
    assert (lines, characters) == (PINNED_LINES, PINNED_CHARACTERS), (
        f"rules.md holds {lines} lines and {characters} characters, pinned at {PINNED_LINES} and "
        f"{PINNED_CHARACTERS}: move the pin in this change, and say in the commit message what the "
        f"growth bought and what was removed or weighed for removal")


def test_the_pin_stays_under_the_guidance_ceiling():
    assert PINNED_LINES <= GUIDANCE_CEILING_LINES


def test_each_bullet_opens_with_its_rule_in_bold():
    unbold = [(number, bullet.splitlines()[0][:70]) for number, bullet in bullets(text())
              if not bullet.startswith("- **")]
    assert unbold == [], f"bullets that do not open with their rule in bold: {unbold}"


def test_every_script_the_rules_name_ships():
    named = {name for name, _ in SCRIPT_SPAN.findall(text())}
    assert named, "no `bin/<script>.py` parsed; the guard lost its subject"
    missing = sorted(name for name in named if not (BIN / f"{name}.py").is_file())
    assert missing == [], f"the rules name scripts that ship nowhere: {missing}"


def help_of(script: str) -> str:
    done = subprocess.run([sys.executable, "-B", str(BIN / f"{script}.py"), "--help"],
                          capture_output=True, text=True, timeout=60)
    return done.stdout


def test_every_flag_the_rules_name_is_one_its_script_prints():
    spans: dict[str, set[str]] = {}
    for script, rest in SCRIPT_SPAN.findall(text()):
        spans.setdefault(script, set()).update(FLAG.findall(rest))
    unknown = sorted((script, flag) for script, flags in spans.items()
                     for flag in flags if flag not in help_of(script))
    assert unknown == [], f"flags the rules name that the script's --help never prints: {unknown}"


def test_every_schema_the_rules_name_ships():
    missing = sorted(name for name in SCHEMA.findall(text()) if not (SCHEMAS / name).is_file())
    assert missing == [], f"the rules name schemas that ship nowhere: {missing}"


def test_the_longest_bullets_are_reported(capsys):
    """A report, never a refusal: the reading a change owes the file starts at the far end."""
    sized = sorted(((len(bullet.splitlines()), number, bullet.splitlines()[0][:72])
                    for number, bullet in bullets(text())), reverse=True)
    with capsys.disabled():
        print("\nrules.md bullets by length (lines, starting line, opening):")
        for count, number, opening in sized[:5]:
            print(f"  {count:3d}  line {number:3d}  {opening}")
    assert sized
