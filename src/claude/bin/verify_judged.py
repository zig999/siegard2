#!/usr/bin/env python3
"""Run a judged artifact against the conformance suite its knowledge object generates.

`the judged track is verified against a conformance suite generated from the
knowledge base, and "a judged artifact with no covering suite is not accepted output". R2 keeps
byte identity for the deterministic track only, so this is what replaces it — and R5 forbids
reporting one as the other.

The suite is not authored. It comes from `rule.examples` and from `lifecycle` totality (R36), so
the cases a validator is held to are the cases the knowledge object already states. A suite
written beside the validator would be written by whoever wrote the validator.

Declared dependencies: PyYAML and jsonschema, via bin/knowledge_graph_lib.py.

Usage: bin/verify_judged.py --run PATH
Exit: 0 every judged artifact passes its suite, 1 a failure or a missing suite, 2 cannot run
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

from cli import cannot_run
from knowledge_graph_lib import load

# A run file names its paths relative to the repository that owns the run, which is the
# directory the command is invoked from. It is not the plugin root: this script ships, so
# resolving against its own tree would look for a consumer's knowledge base inside the
# framework's installed files.
INVOCATION_ROOT = Path.cwd()


def cases(node: dict) -> list[tuple[dict, str]]:
    """The conformance cases a knowledge object states.

    A rule states them as examples. A lifecycle states them as totality: every recorded rejection
    is a case, because R11 of every state-and-trigger pair either a transition or
    a rejection and a validator that permitted one would be wrong about a decided fact.
    """
    if node["type"] == "rule":
        return [(example["given"], example["then"]["outcome"]) for example in node.get("examples", [])]
    return [
        ({"from": entry["from"], "trigger": trigger}, "rejected")
        for entry in node.get("rejections", [])
        for trigger in (entry["trigger"] if isinstance(entry["trigger"], list) else [entry["trigger"]])
    ]


def load_artifact(path: Path):
    spec = importlib.util.spec_from_file_location("judged_artifact", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify(run: dict) -> tuple[list[str], int]:
    graph = load(INVOCATION_ROOT / run["knowledge_root"])
    problems: list[str] = []
    checked = 0

    for entry in run["judged"]:
        node = graph.nodes.get(entry["ko"])
        if node is None:
            problems.append(f"{entry['ko']}: names no knowledge object")
            continue
        suite = cases(node.data)
        if not suite:
            problems.append(
                f"{entry['ko']}: the knowledge object generates no conformance case, so this "
                f"artifact has no covering suite — that unaccepted output"
            )
            continue
        artifact = load_artifact(INVOCATION_ROOT / entry["artifact"])
        for given, expected in suite:
            checked += 1
            actual = artifact.check(given)
            if actual != expected:
                problems.append(
                    f"{entry['ko']}: given {given}, the artifact returned {actual!r} and the "
                    f"knowledge object states {expected!r}"
                )
    return problems, checked


def main() -> int:
    parser = argparse.ArgumentParser(prog="verify_judged.py")
    parser.add_argument("--run", type=Path, required=True)
    args = parser.parse_args()
    if not args.run.is_file():
        cannot_run(f"cannot run: {args.run} does not exist")

    run = json.loads(args.run.read_text())
    if not run.get("judged"):
        cannot_run(f"cannot run: {args.run} declares no judged artifact to verify")

    problems, checked = verify(run)
    print(f"judged artifacts verified: {len(run['judged'])} conformance cases: {checked}")
    if problems:
        print(f"FAILED: {len(problems)} problem(s)\n")
        for problem in problems:
            print(f" {problem}")
        return 1
    print("every judged artifact satisfies the suite its knowledge object generates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
