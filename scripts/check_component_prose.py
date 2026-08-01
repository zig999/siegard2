#!/usr/bin/env python3
"""Hold a component's prose to the contracts it declares, and to being reachable at all.

Three rules, each numbered, each carrying the case that put it here. The numbering exists so a
violation cites `C01` and a reader finds the rule and its origin; a validator that emits only a
sentence makes its own history ungreppable.

Every finding this script reports was found by hand first, which is the argument for the script.

**C01 — a field the prose names exists in a contract the component declares.** Origin:
`agents/impact-analyst.md` told its producer to record an ambiguity `in `notes``, and
`impact-analysis/2` has no `notes` property and is a closed object. Following the prose produced an
artifact the boundary rejects, and the prose is what the producer reads. Nothing caught it — the
schema was valid, the declaration agreed with the component, the worked example conformed, and the
one sentence that mattered pointed at a field that does not exist.

**C02 — a component carries one worked example, and it conforms to its output contract.** The same
defect from the other side: a producer that is never shown what to emit omits a required field and
fails the boundary after doing the work. A first form of this rule required each required field to
appear in backticks somewhere in the prose, and it reported twenty violations that were all present —
inside the fenced JSON example, which is where this repository's agents actually show their output.
Requiring the example and validating it is the same guarantee with none of that noise: every required
field is in a conforming example by construction. Exactly one example, because a second is a second
shape to imitate.

**C03 — an agent no skill names is unreachable.** Origin: the workflow removal left four agents
installed, conforming, declared — and invocable by nothing, because a skill is the only class a user
reaches. `validate_components.py` passed on all four: each was individually valid. Reachability is a
property of the set, not of a component, so nothing that checks components one at a time can see it.

A recorded debt is not a pass. `UNREACHABLE` carries a reason per agent and this script prints every
entry on every run, so the debt stays visible rather than becoming silent — the same shape as the
`CALIBRATED` table in `check_capabilities.py` and as an **Outstanding evidence** section. An agent
missing from both the skills and the table fails.

Declared dependencies: jsonschema — C02 validates a worked example against its contract.

Usage:  scripts/check_component_prose.py [--source DIR]
Exit:   0 every rule passes, 1 a violation, 2 cannot run
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import generator_lib  # noqa: F401  (puts src/claude/bin on the import path)
from cli import cannot_run

try:
    from jsonschema import Draft202012Validator
except ImportError:
    cannot_run("cannot run: jsonschema is not installed (pip install jsonschema)")

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = REPO_ROOT / "src" / "claude"
DECLARATION = "capabilities.declaration.json"

# The fenced JSON block an agent uses to show its result. Exactly one is expected.
FENCED_JSON = re.compile(r"```json\n(.*?)\n```", re.DOTALL)

# A backtick-quoted lowercase identifier — the shape a field reference takes in this repository's
# prose. Deliberately narrow: `Read`, `SKILL.md` and `ko.rule.sales.x` are not field-shaped and are
# not candidates.
FIELD = re.compile(r"`([a-z][a-z0-9_]*)`")

# A schema the prose names by filename. Citing one is how a component declares that it is talking
# about that contract's vocabulary, which `domain-analyst` legitimately does for the ontology.
CITED_SCHEMA = re.compile(r"schemas/([a-z0-9-]+)\.json")

# Tokens that are field-shaped and are never fields. Kept short on purpose: a long allowlist is how
# C01 stops catching anything.
NOT_A_FIELD = frozenset({"json", "yaml", "md", "true", "false", "null"})

# Agents no skill invokes, with why each is admitted. A reason is required; an agent absent from both
# the skills and this table is a violation. Every entry is printed on every run.
UNREACHABLE: dict[str, str] = {
    "impact-analyst": (
        "recorded debt, not an entry point. It lost its caller when the workflow machinery was "
        "removed (docs/adr/0016). Its ordering is derivable from its declaration, so reconnecting it "
        "means giving it a skill rather than rebuilding anything"
    ),
    "root-selector": (
        "recorded debt, not an entry point. Same origin as impact-analyst; it produces a context "
        "package that no procedure currently consumes"
    ),
    "spec-delta-author": (
        "recorded debt, not an entry point. Same origin; the delta it produces has no mechanical "
        "consumer since the orchestrator that read one was removed"
    ),
    "concept-author": (
        "recorded debt, not an entry point. It is the vocabulary layer, and ingest-domain does not "
        "call it because that procedure authors domain facts. A concept change has no entry point"
    ),
}


def load(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        cannot_run(f"cannot run: {path} is not readable JSON: {exc}")


def vocabulary(schema_dir: Path, artifact: str) -> set[str]:
    """Every property name, enum value, const and required entry a contract holds.

    Enum values and consts are in the set because prose legitimately names them — a state, a verdict,
    a `ddd` value — and excluding them made C01 report every closed field it saw.
    """
    path = schema_dir / f"{artifact}.json"
    if not path.is_file():
        return set()
    found: set[str] = set()

    def walk(node: object) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "properties" and isinstance(value, dict):
                    found.update(value.keys())
                elif key == "enum" and isinstance(value, list):
                    found.update(str(item) for item in value)
                elif key == "const":
                    found.add(str(value))
                elif key == "required" and isinstance(value, list):
                    found.update(str(item) for item in value)
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(load(path))
    return found


def declared_artifacts(entry: dict, body: str) -> set[str]:
    """Every contract this component may speak the vocabulary of.

    The union of what it declares — outputs, inputs, produced, consumed — and what its prose names by
    filename. The second source is not a loophole: citing `schemas/x.json` is the component saying it
    is talking about that contract, which is exactly the claim C01 needs to check against.
    """
    names = {output["artifact"] for output in entry.get("outputs", [])}
    names |= {i["artifact"] for i in entry.get("inputs", []) if "artifact" in i}
    names |= set(entry.get("produced_artifacts", []))
    names |= {c["artifact"] for c in entry.get("consumed_artifacts", [])}
    names |= set(CITED_SCHEMA.findall(body))
    return names


def check_fields(source: Path, entry: dict, path: Path, findings: list[str]) -> None:
    """C01 and C02, over one component."""
    body = path.read_text()
    rel = path.relative_to(source).as_posix()
    schema_dir = source / "schemas"

    legitimate = set(NOT_A_FIELD)
    for artifact in declared_artifacts(entry, body):
        legitimate |= vocabulary(schema_dir, artifact)

    unknown = sorted(
        token
        for token in set(FIELD.findall(body))
        if token not in legitimate and not token.endswith("_")
    )
    for token in unknown:
        findings.append(
            f"C01 {rel}: prose names `{token}`, which is not a property, enum value or const of any "
            f"contract this component declares or cites. Either the field does not exist — following "
            f"the prose would produce an artifact the boundary rejects — or the contract it belongs "
            f"to is undeclared"
        )

    for output in entry.get("outputs", []):
        schema = source / "schemas" / f"{output['artifact']}.json"
        if not schema.is_file():
            continue
        blocks = FENCED_JSON.findall(body)
        if len(blocks) != 1:
            findings.append(
                f"C02 {rel}: carries {len(blocks)} fenced JSON example(s) and must carry exactly one. "
                f"A producer shown no example is a producer guessing the shape of {output['contract']}; "
                f"shown two, it has two shapes to imitate"
            )
            continue
        try:
            example = json.loads(blocks[0])
        except json.JSONDecodeError as exc:
            findings.append(f"C02 {rel}: the worked example is not valid JSON: {exc}")
            continue
        errors = sorted(
            Draft202012Validator(load(schema)).iter_errors(example),
            key=lambda e: list(e.path),
        )
        for err in errors:
            where = ".".join(str(part) for part in err.path) or "(root)"
            findings.append(
                f"C02 {rel}: the worked example fails {output['contract']} at {where}: {err.message}. "
                f"The example is what a producer reproduces, so one that does not conform teaches a "
                f"shape the boundary then rejects"
            )


def check_reachability(source: Path, findings: list[str]) -> list[str]:
    """C03, over the set. Returns the recorded debts, which the caller prints."""
    agents = sorted(p.stem for p in (source / "agents").glob("*.md"))
    skills = list((source / "skills").glob("*/SKILL.md"))
    invoked = {agent for agent in agents if any(agent in s.read_text() for s in skills)}

    recorded = []
    for agent in agents:
        if agent in invoked:
            continue
        if agent in UNREACHABLE:
            recorded.append(f"{agent}: {UNREACHABLE[agent]}")
            continue
        findings.append(
            f"C03 agents/{agent}.md: no skill names this agent, and a skill is the only class a user "
            f"invokes. It is installed, declared, and reachable by nothing. Give it an entry point, or "
            f"record it in UNREACHABLE with the reason it is admitted"
        )
    return recorded


def main() -> int:
    parser = argparse.ArgumentParser(prog="check_component_prose.py", add_help=True)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    args = parser.parse_args()

    source = args.source
    if not (source / "agents").is_dir():
        cannot_run(f"cannot run: {source} holds no agents/ to check")
    declaration = source / DECLARATION
    if not declaration.is_file():
        cannot_run(f"cannot run: {declaration} does not exist")

    entries = {e["identifier"]: e for e in load(declaration)["declarations"]}
    findings: list[str] = []
    checked = 0

    for path in sorted((source / "agents").glob("*.md")):
        entry = entries.get(path.stem)
        if entry is None:
            continue
        check_fields(source, entry, path, findings)
        checked += 1

    recorded = check_reachability(source, findings)

    print(f"component prose checked: {checked} agent(s)  rules: C01, C02, C03")
    if recorded:
        print(f"unreachable, recorded ({len(recorded)}):")
        for line in recorded:
            print(f"  {line}")
    if findings:
        print(f"FAILED: {len(findings)} violation(s)\n")
        for finding in findings:
            print(f"  {finding}")
        return 1
    print("every field the prose names exists, every required field is named, every agent is reached")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
