"""An enriched prompt is held to its contract: sections, order, provenance, bracketed fields.

The validator decides what is decidable. Whether an addition is worth keeping is not, so it is
reported (count and longest) and refused on nothing.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

import enrich

REPO = Path(__file__).resolve().parent.parent
CONTRACT = json.loads((REPO / "src/claude/schemas/enriched-prompt.json").read_text("utf-8"))
VALID = """ROLE: Senior application-security reviewer.
OBJECTIVE: Review pull request [PR number] for vulnerabilities.
CONTEXT:
- Stack: [language and framework].
CONSTRAINTS:
- Do not modify code.
TOOLS:
- OWASP ASVS 4.0, static analysis with [SAST tool].
STEPS:
- Read the diff.
- Rate each finding by severity.
ADDITIONS:
- Model threats for the changed surface — a finding outside the diff usually starts at a new input.
EXTERNAL_VALIDATION:
- Each finding cites the OWASP ASVS item that supports it.
RESPONSE_FORMAT:
- Table: file, line, severity, ASVS item, fix.
ASSUMPTIONS:
- The diff is the current pull request's — the person wrote "this PR".
"""


def problems(text: str) -> list[str]:
    return enrich.check(text, CONTRACT)


def run(*args: str, stdin: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(REPO / "src/claude/bin/enrich.py"), *args],
                          input=stdin, capture_output=True, text=True)


def without(section: str) -> str:
    out, skip = [], False
    for line in VALID.splitlines(keepends=True):
        if line.split(":")[0] == section and line[0].isupper():
            skip = True
            continue
        if skip and line[0].isupper() and ":" in line.split()[0]:
            skip = False
        if not skip:
            out.append(line)
    return "".join(out)


def test_a_well_formed_prompt_has_no_problem():
    assert problems(VALID) == []


def test_the_optional_sections_may_be_absent():
    assert problems(without("ADDITIONS")) == []
    assert problems(without("ASSUMPTIONS")) == []


@pytest.mark.parametrize("section", [
    "ROLE", "OBJECTIVE", "CONTEXT", "CONSTRAINTS", "TOOLS", "STEPS",
    "EXTERNAL_VALIDATION", "RESPONSE_FORMAT",
])
def test_every_required_section_is_refused_when_absent(section):
    found = problems(without(section))
    assert any(section in line for line in found), found


@pytest.mark.parametrize("text,fragment", [
    ("Sure, here it is:\n" + VALID, "text before the first section"),
    (VALID + "NOTE: be careful\n", "not one the contract names"),
    (VALID + "ROLE: outro\n", "appears twice"),
    (VALID.replace("STEPS:", "ASSUMPTIONS:\n- x — y\nSTEPS:", 1), "canonical order"),
    (VALID.replace("ROLE: Senior application-security reviewer.\n", "ROLE:\n"), "ROLE"),
    ("```\n" + VALID + "```\n", "text before the first section"),
    (VALID.replace(" — a finding outside the diff usually starts at a new input", ""), "ADDITIONS: a line is"),
    (VALID.replace(' — the person wrote "this PR"', ""), "ASSUMPTIONS: a line is"),
    (VALID.replace("[PR number]", "[]"), "bracket"),
    (VALID.replace("[PR number]", "[PR [number]]"), "bracket"),
    (VALID.replace("[PR number]", "[PR number"), "bracket"),
])
def test_a_malformed_prompt_is_refused_naming_the_defect(text, fragment):
    found = problems(text)
    assert found and any(fragment in line for line in found), found


def test_a_prompt_with_no_field_and_no_addition_is_well_formed():
    text = without("ADDITIONS").replace("[PR number]", "42").replace("[language and framework]", "Python") \
        .replace("[SAST tool]", "Bandit")
    assert problems(text) == []
    assert enrich.report(text, CONTRACT) == ["additions: 0; longest: -", "fields: 0; in: -"]


def test_the_report_counts_additions_and_fields_and_refuses_nothing():
    first, second = enrich.report(VALID, CONTRACT)
    assert first.startswith("additions: 1; longest: Model threats")
    assert second == "fields: 3; in: OBJECTIVE 1, CONTEXT 1, TOOLS 1"


def test_the_command_reads_standard_input_and_exits_by_the_verdict():
    good = run("-", stdin=VALID)
    assert good.returncode == 0 and good.stdout.splitlines()[0] == "ok"
    assert len(good.stdout.splitlines()) == 3
    refused = run("-", stdin="ROLE: x\n")
    assert refused.returncode == 1 and "OBJECTIVE" in refused.stdout


def test_the_command_cannot_run_without_a_readable_input():
    assert run("no-such-file").returncode == 2
    assert run().returncode == 2


def test_the_schema_names_each_justified_section_it_declares():
    assert set(CONTRACT["x-justified-sections"]["values"]) <= set(CONTRACT["properties"])


SKILL = REPO / "src/claude/skills/enrich-request"
FENCE = re.compile(r"^<!-- prompt -->\n```\n(.*?)^```", re.S | re.M)


def examples() -> list[str]:
    return FENCE.findall((SKILL / "references/examples.md").read_text("utf-8"))


def test_the_skill_ships_examples():
    assert len(examples()) >= 4, "the examples teach the contract; the guard lost its subject"


@pytest.mark.parametrize("index", range(len(examples())))
def test_every_example_prompt_is_well_formed(index):
    assert problems(examples()[index]) == []


def test_an_example_adds_nothing_so_the_section_is_taught_as_optional():
    assert any("ADDITIONS:" not in text for text in examples())
