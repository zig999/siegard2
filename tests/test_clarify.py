"""A clarified request is held to its contract, and every example the skill ships passes it.

The validator decides what is decidable: the sections, their order, their content, the mode's
bound. The examples are the skill's own demonstration of the contract, so a contract change that
leaves one stale is red here rather than shipped as an instruction the validator would refuse.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

import clarify

REPO = Path(__file__).resolve().parent.parent
SKILL = REPO / "src/claude/skills/clarify-request"
CONTRACT = json.loads((REPO / "src/claude/schemas/clarified-request.json").read_text("utf-8"))
FENCE = re.compile(r"^<!-- instruction -->\n```\n(.*?)^```", re.S | re.M)
VALID = "MODE: ANALYZE\nTASK: Validate the module.\nCONSTRAINTS:\n- Do not modify code.\n"
READ_ONLY = CONTRACT["x-read-only-modes"]["values"]
IN_TURN = CONTRACT["x-executes-in-turn"]


def problems(text: str) -> list[str]:
    return clarify.check(text, CONTRACT)


def examples() -> list[str]:
    return FENCE.findall((SKILL / "references/examples.md").read_text("utf-8"))


def test_the_skill_ships_examples():
    assert len(examples()) >= 6, "the examples are what teaches the contract; the guard lost its subject"


@pytest.mark.parametrize("index", range(len(examples())))
def test_every_example_instruction_is_well_formed(index):
    assert problems(examples()[index]) == []


def test_a_well_formed_instruction_has_no_problem():
    assert problems(VALID) == []


@pytest.mark.parametrize("text,fragment", [
    ("Sure, here it is:\n" + VALID, "text before the first section"),
    (VALID.replace("MODE: ANALYZE\n", ""), "MODE"),
    (VALID.replace("TASK: Validate the module.\n", ""), "TASK"),
    (VALID + "NOTE: be careful\n", "not one the contract names"),
    (VALID.replace("ANALYZE", "REVIEW"), "MODE"),
    (VALID.replace("ANALYZE", "ANALYZE\n- PLAN"), "MODE"),
    ("TASK: Validate the module.\nMODE: ANALYZE\nCONSTRAINTS:\n- Do not modify code.\n",
     "canonical order"),
    (VALID + "SCOPE:\n", "SCOPE"),
    (VALID + "CONSTRAINTS:\n- Do not modify code.\n", "appears twice"),
    (VALID.replace("- Do not modify code.", "- Be careful."), "authorizes no change"),
    ("MODE: PLAN\nTASK: Propose a design.\n", "authorizes no change"),
    (VALID.replace("Do not modify code.", "Do not modify the CSS file."), "authorizes no change"),
    (VALID.replace("ANALYZE", "OPERATE").replace("- Do not modify code.", "- Send to the local gateway only."),
     "authorizes no change"),
    ("MODE: IMPLEMENT\nTASK: Add the endpoint.\nCONSTRAINTS:\n- Do not modify code.\n",
     "authorizes a change"),
    ("```\n" + VALID + "```\n", "text before the first section"),
])
def test_a_malformed_instruction_is_refused_naming_the_defect(text, fragment):
    found = problems(text)
    assert found and any(fragment in line for line in found), found


def test_a_mode_that_authorizes_a_change_needs_no_bound():
    assert problems("MODE: IMPLEMENT\nTASK: Add the endpoint.\n") == []


def run(*args: str, stdin: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(REPO / "src/claude/bin/clarify.py"), *args],
                          input=stdin, capture_output=True, text=True)


@pytest.mark.parametrize("mode,verdict", [
    ("ANALYZE", "in-turn"), ("PLAN", "in-turn"), ("OPERATE", "hand-over"),
    ("IMPLEMENT", "hand-over"), ("IMPLEMENT_AND_VALIDATE", "hand-over"),
])
def test_the_mode_alone_decides_whether_the_instruction_is_carried_out_in_turn(mode, verdict):
    bound = "CONSTRAINTS:\n- Do not modify the project.\n" if mode in READ_ONLY else ""
    text = f"MODE: {mode}\nTASK: Do the thing.\n{bound}"
    assert problems(text) == []
    assert clarify.handoff(text, CONTRACT) == verdict
    assert run("-", stdin=text).stdout.strip() == verdict


def test_a_mode_carried_out_in_turn_changes_nothing():
    """In-turn execution skips the person's reading of the instruction, which is only cheap where
    nothing acts: every such mode is one that changes no file, and OPERATE — which changes no file
    but calls something with an effect — is not one of them."""
    in_turn = set(IN_TURN["values"])
    assert in_turn and in_turn <= set(READ_ONLY)
    assert "OPERATE" not in in_turn


def test_the_tools_of_an_in_turn_execution_are_the_ones_the_skill_already_holds():
    """The execution runs inside the skill's turn: a tool the frontmatter withholds could not be
    used, and one it does not pre-approve would stop the turn on a permission prompt."""
    import yaml
    front = yaml.safe_load(re.match(r"^---\n(.*?)\n---\n", (SKILL / "SKILL.md").read_text("utf-8"),
                                    re.S).group(1))
    granted = set(front["allowed-tools"].split())
    withheld = set(front["disallowed-tools"].split())
    for tool in IN_TURN["tools"]:
        assert tool in granted and tool not in withheld, tool


def test_the_command_reads_standard_input_and_exits_by_the_verdict():
    assert run("-", stdin=VALID).returncode == 0
    refused = run("-", stdin="TASK: x\n")
    assert refused.returncode == 1 and "MODE" in refused.stdout


def test_the_command_cannot_run_without_a_readable_input():
    assert run("no-such-file").returncode == 2
    assert run().returncode == 2
