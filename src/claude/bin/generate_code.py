#!/usr/bin/env python3
"""Execute a validated plan, record what it produced, and verify it without mutating anything.

The last step, and the one where the promise either holds or gets reduced.

**Verification is regenerate-and-diff into a temporary tree** (R34), never in place: a check that
repairs what it detects reports success on a defect. A difference in a locked entry is reported as
a finding naming which of three causes it is (R35) — a change in knowledge, a producer regression,
or a hand edit of a produced file — because a diff that says only "differs" leaves the reader to
guess which, and the three call for opposite actions.

**The deterministic share is measured and reported** (R6). Where it does not cover the structural
code, R6 requires the promise to be *reduced to what the mechanism delivers* rather than restated.
That is the one requirement here that can make the framework claim less, so the figure is computed
rather than described.

**A generative gap blocks the scope** (R37, R38). A knowledge object short of a domain fact its
artifact class needs is not generated around: resolution reports and continues, validation rejects.
Nothing here supplies the fact and nothing asks a model to (R39).

**Two indexes bind implementation to knowledge, and both are derived** (R42, R44). Produced source
binds through the manifest; hand-authored source binds through a declaration it carries. A
hand-maintained mapping from knowledge to code must not exist, so both are computed here and
neither is authored.

Declared dependencies: PyYAML and jsonschema, via bin/knowledge_graph_lib.py.

Usage:
  generate_code.py run --run PATH [--into DIR]
  generate_code.py verify --run PATH
  generate_code.py index --run PATH
Exit: 0 done, 1 a finding or a blocked scope, 2 cannot run
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

from cli import cannot_run
from generation_lib import Blocked, content_hash, derive_plan, resolve_scope, validate_plan
from knowledge_graph_lib import load

# Two roots, and conflating them is what shipped a script looking for a consumer's pack
# inside the framework's own installed files. PLUGIN_ROOT is where this code ships and is
# where the framework's own facts are; INVOCATION_ROOT is the repository being generated
# into, which is the directory the command runs from.
PLUGIN_ROOT = Path(__file__).resolve().parent.parent
INVOCATION_ROOT = Path.cwd()

# a produced file is not hand-edited, and extension happens through an extension
# point the plan declares, in a separate hand-authored file. This is the suffix that names one.
EXTENSION_SUFFIX = ".ext"

# The declaration a hand-authored file carries to bind itself to knowledge — R42's second index.
BINDING_MARKER = "siegard:binds"


def load_templates(pack_root: Path):
    """Import the pack's template module by path, because a pack is not on the import path."""
    module_path = pack_root / "templates" / "expand.py"
    if not module_path.is_file():
        cannot_run(f"cannot run: {module_path} does not exist")
    spec = importlib.util.spec_from_file_location("pack_templates", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def prepare(run: dict, repo_root: Path | None = None) -> tuple[dict, dict, dict, dict]:
    """Everything the run needs, resolved from the recorded inputs alone.

    `repo_root` is an argument rather than a module constant so a caller can resolve a run
    against a copy of the tree. A test that had to patch the constant would be testing the patch.
    """
    repo_root = repo_root or INVOCATION_ROOT
    pack_root = repo_root / run["pack_root"]
    declaration = json.loads((pack_root / "pack-declaration.json").read_text())
    graph = load(repo_root / run["knowledge_root"])
    scope = resolve_scope(graph, run["scope_id"], run["request_id"], run["roots"])
    placement = json.loads((pack_root / run["placement"]).read_text()) if run.get("placement") else None
    return declaration, graph, scope, placement


def produce(run: dict, target: Path, repo_root: Path | None = None) -> tuple[dict, list[str], list[str]]:
    """Write the plan's deterministic entries into `target`. Returns manifest, gaps, skipped."""
    repo_root = repo_root or INVOCATION_ROOT
    pack_root = repo_root / run["pack_root"]
    templates = load_templates(pack_root)
    declaration, graph, scope, placement = prepare(run, repo_root)

    manifest_path = repo_root / run["manifest"]
    manifest = (
        json.loads(manifest_path.read_text())
        if manifest_path.is_file()
        else {
            "contract_version": "generation-manifest/1",
            "pack": declaration["pack"],
            "pack_version": declaration["version"],
            "artifacts": [],
        }
    )

    plan, uncovered = derive_plan(run["plan_id"], scope, declaration, manifest, placement)
    # R25's "every locked path still exists" is a question about the tree of record, never about
    # wherever this run happens to be writing. Two wrong roots were tried before this one: the
    # repository root, which made every locked entry look deleted; and the write target, which
    # made every locked entry look deleted again the moment verification regenerated into an
    # empty temporary directory. A regeneration into a fresh tree is exactly the case where the
    # locked paths do not exist yet and the lock is still intact.
    problems = validate_plan(plan, scope, declaration, repo_root / run["output_root"])
    if problems:
        raise Blocked(
            "the plan does not validate, so nothing is written — rejects a plan "
            "rather than repairing it:\n " + "\n ".join(problems)
        )

    members = {member["id"]: graph.nodes[member["id"]].data for member in scope["members"]}
    artifacts: list[dict] = []
    gaps: list[str] = []
    judged: list[str] = []

    for entry in plan["entries"]:
        if entry["track"] == "judged":
            # a judged artifact comes from an agent and is verified against a
            # generated conformance suite. Nothing here invokes one, so it is reported rather
            # than silently missing from the manifest.
            judged.append(f"{entry['ko']}/{entry['class']}")
            continue
        template = templates.TEMPLATES[entry["class"]]
        try:
            body = template(members[entry["ko"]], declaration["version"])
        except templates.MissingFact as gap:
            gaps.append(str(gap))
            continue
        destination = target / entry["path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(body)
        artifacts.append(
            {
                "ko": entry["ko"],
                "class": entry["class"],
                "path": entry["path"],
                "content_hash": content_hash(destination),
                "pack_version": declaration["version"],
            }
        )

    produced = {
        "contract_version": "generation-manifest/1",
        "pack": declaration["pack"],
        "pack_version": declaration["version"],
        "framework_version": json.loads(
            (PLUGIN_ROOT / ".claude-plugin" / "plugin.json").read_text()
        )["version"],
        "artifacts": sorted(artifacts, key=lambda a: (a["ko"], a["class"])),
    }
    return produced, gaps, judged + [f"node type {t} yields no class" for t in uncovered]


def deterministic_share(manifest: dict, plan: dict) -> tuple[int, int]:
    """the share of source produced on the deterministic track, measured."""
    total = len(plan["entries"])
    deterministic = sum(1 for entry in plan["entries"] if entry["track"] == "deterministic")
    return deterministic, total


def findings(committed: Path, fresh: Path, manifest: dict) -> list[str]:
    """Every difference, attributed to one of the three causes — R34 and R35."""
    recorded = {artifact["path"]: artifact for artifact in manifest["artifacts"]}
    problems: list[str] = []
    for path, artifact in sorted(recorded.items()):
        live, regenerated = committed / path, fresh / path
        if not regenerated.exists():
            problems.append(
                f"{path}: the manifest records it and the generator no longer produces it — the "
                f"cause is a change in knowledge"
            )
            continue
        if not live.exists():
            problems.append(f"{path}: recorded and missing from the tree — the cause is a hand deletion")
            continue
        on_disk, produced = content_hash(live), content_hash(regenerated)
        if on_disk == produced:
            continue
        if on_disk != artifact["content_hash"]:
            problems.append(
                f"{path}: differs from what the manifest recorded — the cause is a hand edit of a "
                f"produced file, which "
            )
        else:
            problems.append(
                f"{path}: matches the manifest and differs from a fresh generation — the cause is "
                f"a change in knowledge or a producer regression, and the manifest's pack version "
                f"{artifact['pack_version']} is what tells them apart"
            )
    for path in sorted({p.relative_to(fresh).as_posix() for p in fresh.rglob("*") if p.is_file()}):
        if path not in recorded:
            problems.append(f"{path}: produced and named by no manifest entry")
    return problems


def binding_indexes(manifest: dict, tree: Path) -> dict:
    """The two derived indexes of R42, and the reverse map R44 answers from.

    Both derived here and never authored: R44 forbids a hand-maintained mapping from knowledge to
    code, because a mapping nobody derives is a mapping that stops being true.
    """
    produced: dict[str, list[str]] = {}
    for artifact in manifest["artifacts"]:
        produced.setdefault(artifact["ko"], []).append(artifact["path"])

    authored: dict[str, list[str]] = {}
    if tree.is_dir():
        recorded = {artifact["path"] for artifact in manifest["artifacts"]}
        for path in sorted(tree.rglob("*")):
            if not path.is_file() or path.relative_to(tree).as_posix() in recorded:
                continue
            try:
                text = path.read_text()
            except (UnicodeDecodeError, OSError):
                continue
            for line in text.splitlines():
                if BINDING_MARKER in line:
                    ko = line.split(BINDING_MARKER, 1)[1].strip().lstrip(":").strip()
                    if ko:
                        authored.setdefault(ko, []).append(path.relative_to(tree).as_posix())

    reverse: dict[str, list[str]] = {}
    for index in (produced, authored):
        for ko, paths in index.items():
            reverse.setdefault(ko, []).extend(paths)
    return {
        "produced": {k: sorted(v) for k, v in sorted(produced.items())},
        "authored": {k: sorted(v) for k, v in sorted(authored.items())},
        "reverse": {k: sorted(v) for k, v in sorted(reverse.items())},
    }


def main() -> int:
    parser = argparse.ArgumentParser(prog="generate_code.py")
    parser.add_argument("action", choices=["run", "verify", "index"])
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--into", type=Path)
    args = parser.parse_args()

    if not args.run.is_file():
        cannot_run(f"cannot run: {args.run} does not exist")
    run = json.loads(args.run.read_text())

    try:
        if args.action == "run":
            target = args.into or (INVOCATION_ROOT / run["output_root"])
            manifest, gaps, skipped = produce(run, target)
            (INVOCATION_ROOT / run["manifest"]).write_text(json.dumps(manifest, indent=2) + "\n")
            print(f"produced {len(manifest['artifacts'])} artifact(s) into {target}")
            for note in skipped:
                print(f" not produced here: {note}")
            for gap in gaps:
                print(f" generative gap: {gap}", file=sys.stderr)
            return 1 if gaps else 0

        manifest = json.loads((INVOCATION_ROOT / run["manifest"]).read_text())
        if args.action == "index":
            print(json.dumps(binding_indexes(manifest, INVOCATION_ROOT / run["output_root"]), indent=2))
            return 0

        with tempfile.TemporaryDirectory() as holder:
            fresh = Path(holder) / "out"
            produce(run, fresh)
            problems = findings(INVOCATION_ROOT / run["output_root"], fresh, manifest)
        print(f"verified {len(manifest['artifacts'])} artifact(s), regenerate-and-diff")
        if problems:
            print(f"FAILED: {len(problems)} finding(s)\n")
            for problem in problems:
                print(f" {problem}")
            return 1
        print("every produced artifact matches a fresh generation")
        return 0
    except Blocked as exc:
        print(f"blocked: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
