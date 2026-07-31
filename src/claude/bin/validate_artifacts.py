#!/usr/bin/env python3
"""Hold every pack and every produced artifact to the framework-owned class contract.

`specs/0012` R4 keeps the schema a template's output validates against in the framework, because
a pack shipping one would extend a vocabulary R6 reserves. `specs/0004` R8 closes the vocabulary.
`schemas/artifact-classes.json` is the instance and this is what enforces it.

Three checks, and each is a rule that existed only as prose.

**The vocabulary is closed in one place.** Every schema that names an artifact class enumerates the
same twelve. Four contracts spell that list out, and a fifth would have drifted from them eventually
— comparing them here is cheaper than noticing later.

**A pack's `from` column must be coherent.** `specs/0004` R10 leaves the node-type mapping to the
pack because it presumes a technology, but a pack claiming to produce a `state-machine` from a
`definition` is not presuming a technology, it is contradicting what the class is.

**Produced output names its source.** `specs/0004` R42 binds produced source to knowledge through
the manifest, and an artifact that did not name the object it came from would make a diff
unreadable without one. `conformance-test` additionally carries the declaration R36 requires.

Declared dependencies: jsonschema.

Usage:  scripts/validate_artifacts.py
Exit:   0 valid, 1 problems, 2 cannot run
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from cli import cannot_run

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTRACT = REPO_ROOT / "schemas" / "artifact-class.json"
INSTANCE = REPO_ROOT / "schemas" / "artifact-classes.json"

# Every schema that spells the vocabulary out, and where. One closed set, four copies of the list.
VOCABULARY_SITES = (
    ("pack-declaration.json", ("properties", "produces", "items", "properties", "class", "enum")),
    ("placement-decision.json", ("properties", "entries", "items", "properties", "class", "enum")),
    ("generation-plan.json", ("properties", "entries", "items", "properties", "class", "enum")),
    ("generation-manifest.json", ("properties", "artifacts", "items", "properties", "class", "enum")),
)

try:
    from jsonschema import Draft202012Validator
except ImportError:
    cannot_run("cannot run: jsonschema is not installed (pip install jsonschema)")


def dig(document: dict, path: tuple):
    for key in path:
        document = document[key]
    return document


def check_vocabulary(classes: set[str]) -> list[str]:
    problems = []
    for name, pointer in VOCABULARY_SITES:
        schema = json.loads((REPO_ROOT / "schemas" / name).read_text())
        declared = set(dig(schema, pointer))
        if declared != classes:
            problems.append(
                f"schemas/{name}: names {sorted(declared ^ classes)} differently from "
                f"schemas/artifact-classes.json — specs/0004 R8 closes the vocabulary once"
            )
    return problems


def check_packs(contract: dict, root: Path) -> list[str]:
    problems = []
    for declaration_path in sorted(root.glob("*/pack-declaration.json")):
        declaration = json.loads(declaration_path.read_text())
        rel = declaration_path.relative_to(root).as_posix()
        for entry in declaration["produces"]:
            allowed = set(contract["classes"][entry["class"]]["from"])
            claimed = set(entry["from"])
            if not claimed <= allowed:
                problems.append(
                    f"{rel}: declares {entry['class']} from {sorted(claimed - allowed)}, which the "
                    f"class contract does not admit — it may come from {sorted(allowed)}"
                )
    return problems


def check_produced(contract: dict, root: Path) -> list[str]:
    problems = []
    for manifest_path in sorted(root.glob("*/generation-manifest.json")):
        manifest = json.loads(manifest_path.read_text())
        run_path = manifest_path.parent / "run.json"
        if not run_path.is_file():
            continue
        out = Path.cwd() / json.loads(run_path.read_text())["output_root"]
        for artifact in manifest["artifacts"]:
            path = out / artifact["path"]
            if not path.is_file():
                continue
            body = path.read_text()
            spec = contract["classes"][artifact["class"]]
            if spec["declares_source"] and artifact["ko"] not in body:
                problems.append(
                    f"{artifact['path']}: does not name {artifact['ko']}, the knowledge object it "
                    f"was produced from — specs/0004 R42 binds produced source through the manifest"
                )
            for marker in spec.get("requires_markers", []):
                if marker not in body:
                    problems.append(
                        f"{artifact['path']}: a {artifact['class']} must carry {marker!r} "
                        f"(specs/0004 R36)"
                    )
    return problems


def main() -> int:
    """Hold every declared pack and produced artifact to the class contract.

    The search root is named, never defaulted: this script shipped with the generator's
    own `fixtures/` as its fallback, a path absent from an installation, so the default
    searched nothing and the run reported success over an empty set.
    """
    if len(sys.argv) < 2:
        cannot_run("cannot run: name the root holding packs and generation runs; there is no default")
    root = Path(sys.argv[1])
    if not root.is_dir():
        cannot_run(f"cannot run: root {root} does not exist")
    if not INSTANCE.is_file():
        cannot_run(f"cannot run: {INSTANCE} does not exist")
    contract = json.loads(INSTANCE.read_text())
    schema = json.loads(CONTRACT.read_text())

    problems = [
        f"schemas/artifact-classes.json: {'.'.join(str(p) for p in err.path) or '(root)'}: {err.message}"
        for err in sorted(Draft202012Validator(schema).iter_errors(contract), key=lambda e: list(e.path))
    ]
    if not problems:
        classes = set(contract["classes"])
        problems = check_vocabulary(classes) + check_packs(contract, root) + check_produced(contract, root)

    print(f"artifact classes checked: {len(contract['classes'])}  contract: schemas/{CONTRACT.name}")
    if problems:
        print(f"FAILED: {len(problems)} problem(s)\n")
        for problem in problems:
            print(f"  {problem}")
        return 1
    print("every pack and every produced artifact conforms to its class contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
