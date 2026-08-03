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

**C03 — an agent's description states a prerequisite a selector can evaluate.** A first form of this
rule asked whether any skill named the agent, and that was the wrong criterion in both directions.
`foundation/0005` R3 puts selection with Claude Code: an agent is found through its declaration and
chosen by the model, not by a skill naming it. And every skill this framework ships declares
`disable-model-invocation`, because each writes outside the session — so skills are the user's doors
and agents are the only layer a model selects. An agent no skill mentions can be perfectly
selectable, and one a skill mentions can carry a description nothing can act on.

What decides it is the description, which is the whole of what a selector sees: the declaration does
not reach the distribution. So the rule is what the description routes on. Four agents said
"delegate at the impact-analysis phase" and its kin — and `foundation/0001` R2 demoted the phase order
to guidance, so they named a moment the framework no longer has. The three that routed on an artifact
instead were the three whose contracts had recently changed, which is accident rather than design.

`PHASE_ROUTED` is a regex over the shapes that route on a moment rather than on a prerequisite. An
agent matching one fails; the repair is to say what must exist before it runs, which is what
`foundation/0005` R10 makes the only thing that fixes an order.

**C04 — a component that tells its executor to run a shipped script names the script.** Origin:
`ingest-domain` said "Run the knowledge validator" and "regenerate the derived files with the
materializer", naming neither file. An installation has eleven executables under `bin/` and nothing
that says which is which, so the instruction resolves only for a reader who already knows. It is C01
one level up — a component naming a thing that the consumer cannot resolve — and it was invisible for
the same reason: the sentence is grammatical and no schema covers prose.

The rule fires on a component that instructs an executor and names no path. It does not require every
shipped script to have a caller: a library is imported rather than run, and demanding a citation for
one would push components to cite files they do not invoke.

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

# Shapes that route a selector to a moment rather than to a prerequisite. The phase vocabulary was a
# closed set a persisted event branched on; it is guidance now, and an agent that waits for one waits
# for something nothing announces.
PHASE_ROUTED = re.compile(
    r"\bat the [a-z-]+ phase\b"
    r"|\bduring the [a-z-]+ phase\b"
    r"|\bwhen a workflow needs\b"
    r"|\bat the implementation phase\b",
    re.IGNORECASE,
)

# The clause a description uses to tell a selector when to choose the agent.
DELEGATE = re.compile(r"\bDelegate\b[^.]*\.")

# An instruction to execute something, in the shapes this repository's procedures use.
RUNS_SOMETHING = re.compile(
    r"^\s*(?:[-*]|\d+\.)?\s*(?:Then )?(Run|Regenerate|Expand|Validate|Execute) (?:the )?([a-z][^.]*)",
    re.MULTILINE,
)

# A shipped executable named by path. `bin/x.py` or a bare `x.py` both resolve for a consumer.
NAMED_SCRIPT = re.compile(r"`(?:[a-z_/]*/)?([a-z_]+\.py)(?:[^`]*)`")

# Modules a component imports rather than runs. Naming one as a command would be wrong.
LIBRARIES = frozenset({"cli.py", "frontmatter_lib.py", "generation_lib.py", "knowledge_graph_lib.py"})


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


def check_named_scripts(source: Path, findings: list[str]) -> None:
    """C04, over every component that instructs an executor."""
    components = sorted((source / "skills").glob("*/SKILL.md")) + sorted(
        (source / "agents").glob("*.md")
    )
    runnable = {
        p.name for p in (source / "bin").glob("*.py") if p.name not in LIBRARIES
    }
    for path in components:
        rel = path.relative_to(source).as_posix()
        body = path.read_text()
        for verb, instruction in RUNS_SOMETHING.findall(body):
            sentence = f"{verb} {instruction}"
            if NAMED_SCRIPT.search(sentence):
                continue
            findings.append(
                f"C04 {rel}: {sentence[:70]!r} tells the executor to run something and names no "
                f"shipped script in the same instruction. An installation holds {len(runnable)} "
                f"executables and nothing that says which one this is"
            )


def check_selectability(source: Path, findings: list[str]) -> None:
    """C03, over each agent's description — the whole of what a selector sees."""
    for path in sorted((source / "agents").glob("*.md")):
        rel = path.relative_to(source).as_posix()
        line = next(
            (l for l in path.read_text().splitlines() if l.startswith("description: ")), None
        )
        if line is None:
            findings.append(f"C03 {rel}: no description, so nothing can select this agent")
            continue
        description = line[len("description: ") :]

        clause = DELEGATE.search(description)
        if clause is None:
            findings.append(
                f"C03 {rel}: the description states no `Delegate ...` clause. A selector is told what "
                f"this agent does and never when to choose it"
            )
            continue

        routed = PHASE_ROUTED.search(clause.group(0))
        if routed:
            findings.append(
                f"C03 {rel}: the delegation clause routes on {routed.group(0)!r} — a moment rather "
                f"than a prerequisite. The phase order is guidance, so nothing announces that moment "
                f"to a selector. Say what must exist before this agent runs"
            )


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

    check_selectability(source, findings)
    check_named_scripts(source, findings)

    print(f"component prose checked: {checked} agent(s)  rules: C01, C02, C03, C04")
    if findings:
        print(f"FAILED: {len(findings)} violation(s)\n")
        for finding in findings:
            print(f"  {finding}")
        return 1
    print(
        "every field the prose names exists, every worked example conforms, every agent says when to "
        "choose it, and every script a component runs is named"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
