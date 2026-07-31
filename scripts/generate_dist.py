#!/usr/bin/env python3
"""Assemble the Siegard distribution from framework source.

specs/0008 fixes the output contract and leaves the assembly free. What it fixes: the
distribution is a plugin root holding `.claude-plugin/plugin.json` (R1); running this twice
over the same committed source produces byte-identical output (R4); every installed file
originates in framework source and no file survives whose source was removed (R5); the
directory set is closed and an empty one is omitted rather than shipped (R7); only
`plugin.json` goes inside `.claude-plugin/` (R8); a shipped executable lives in `bin/` (R9);
no `rules/` (R10) and no `packs/` (R23).

**What ships is decided here, and every candidate is classified.** A schema or a script that
is neither shipped nor excluded would be shipped or dropped by whichever branch happened to
run, so `SHIPPED_SCHEMAS` and `SHIPPED_EXECUTABLES` are asserted total against the trees they
select from — adding a schema forces a decision instead of inheriting one.

**Determinism has one requirement and one consequence.** Every iteration is sorted, and the
manifest carries no timestamp: a value minted at generation time would differ between two runs
over identical source, which R4 calls a defect rather than an acceptable variation. specs/0008
R12 lists what the manifest records and a timestamp is not among them.

**`source_revision` is a content digest, not a commit SHA.** A SHA would make the committed
distribution unverifiable: generating at commit N-1 records N-1, committing the result produces
commit N, and the next `make dist-check` would regenerate, read HEAD as N, and report a
difference nobody introduced. A digest over the framework source inputs identifies the source
exactly, is stable across commits that do not touch it, and needs no VCS at all.

**Capability status is derived, never labelled.** specs/0006 R17 requires exactly that, and R14
states `proposed` ships nothing. The checkable fact R17 names is whether a fixture exercises the
capability, read here as its name appearing as a value in fixture data — `.json` and `.jsonl`,
not prose in a README, because a name in a paragraph is a mention and a name in a recorded event
is use. A capability that fails the test is reported as skipped rather than dropped quietly.

Declared dependencies: none beyond the standard library.

Usage:  scripts/generate_dist.py [--into DIR]   (default: dist/.claude)
Exit:   0 assembled, 1 refused to assemble, 2 cannot run
"""

from __future__ import annotations

import ast
import hashlib
import json
import shutil
import sys
from pathlib import Path

from cli import cannot_run

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_ROOT = REPO_ROOT / "src" / "claude"
SCHEMA_ROOT = REPO_ROOT / "schemas"
SCRIPT_ROOT = REPO_ROOT / "scripts"
FIXTURE_ROOT = REPO_ROOT / "fixtures"
DEFAULT_TARGET = REPO_ROOT / "dist" / ".claude"

# Bumped whenever this script's output changes for unchanged source. specs/0008 R4 makes the
# distribution a function of the source *and* the generator, so a consumer that sees a
# difference can attribute it to one or the other.
GENERATOR_VERSION = "1.0.0"

MANIFEST_NAME = "siegard-manifest.json"
PLUGIN_DIR = ".claude-plugin"

# Every schema in schemas/, and whether a governed repository needs it. A schema ships when a
# shipped component or executable validates against it downstream; the rest govern this
# repository's own artifacts and would be dead weight a consumer could mistake for a contract
# it must satisfy. The reason is recorded per entry because a bare boolean would be a decision
# with no argument attached.
SHIPPED_SCHEMAS = {
    "workflow-event.v1.json": "the governed repository's event log; workflow_lib.py validates against it",
    "impact-analysis.v1.json": "consumed at the boundary by orchestrate.py",
    "concept-authoring-result.v1.json": "consumed at the boundary by orchestrate.py",
    "knowledge-authoring-result.v1.json": "consumed at the boundary by orchestrate.py",
    "knowledge-object.v1.json": "the governed repository's knowledge base",
    "knowledge-graph.v1.json": "the materialized graph derived from that base",
    "concept.v1.json": "the bundle concept-author writes into",
    "distribution-manifest.v1.json": "so a consumer can validate the manifest it is told to read",
    # Not shipped, and why.
    "spec.v1.json": None,  # governs specs/ in this repository; a governed repository writes none
    "adr.v1.json": None,  # same, and kept readable only for fixtures/migration-adr-v1-v2/
    "adr.v2.json": None,  # same
    "skill.v1.json": None,  # a governed repository does not author framework components
    "agent.v1.json": None,  # same
    "plugin.v1.json": None,  # same; the harness reads plugin.json, the consumer does not validate it
}

# Scripts that ship as executables. specs/0008 R9 gives them `bin/`. workflow_lib.py is a
# library rather than an executable and ships beside them because Python resolves an import
# from the importing script's own directory; splitting it elsewhere would need a path shim
# that R9's "declares the runtime dependencies it requires" is meant to make unnecessary.
SHIPPED_EXECUTABLES = {
    "orchestrate.py": "the transition lookup the knowledge-change skill invokes",
    "replay_workflow.py": "state reconstruction from the event log",
    "workflow_lib.py": "imported by both; ships beside them so the import resolves",
    "cli.py": "the exit-code convention orchestrate.py imports; a shipped import must ship",
}

# Which capability class each source subtree carries, per specs/0006 R1.
CLASS_BY_TREE = {"skills": "skill", "agents": "specialized-agent"}


class Refused(Exception):
    """The generator will not assemble a distribution it cannot justify."""


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def exercised_names() -> set[str]:
    """Every string value appearing in fixture data, as the checkable half of specs/0006 R17.

    Data only. A README naming a component records an intention; an event log naming it records
    that something ran, and R11 draws the line in the same place.
    """
    names: set[str] = set()

    def walk(node) -> None:
        if isinstance(node, str):
            names.add(node)
        elif isinstance(node, list):
            for item in node:
                walk(item)
        elif isinstance(node, dict):
            for value in node.values():
                walk(value)

    if not FIXTURE_ROOT.is_dir():
        return names
    for path in sorted(FIXTURE_ROOT.rglob("*")):
        if path.suffix not in (".json", ".jsonl") or not path.is_file():
            continue
        text = path.read_text()
        lines = text.splitlines() if path.suffix == ".jsonl" else [text]
        for line in lines:
            if line.strip():
                try:
                    walk(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return names


def assert_imports_ship() -> None:
    """A shipped script may only import modules that ship beside it.

    Found the hard way: `orchestrate.py` gained `from cli import cannot_run`, and nothing
    noticed that `cli.py` was not in `SHIPPED_EXECUTABLES`. The distribution still built, still
    verified, and would have failed on the consumer's first invocation with an ImportError —
    the worst place to discover it, because `specs/0008` R9 exists so a shipped executable
    "exits with a named error" rather than breaking in a way nobody can read.

    Only modules that live in `scripts/` are checked. A standard-library or third-party import
    is R9's other half, which each script declares in its own docstring.
    """
    available = {p.stem for p in SCRIPT_ROOT.glob("*.py")}
    shipped = {Path(name).stem for name in SHIPPED_EXECUTABLES}
    for name in sorted(SHIPPED_EXECUTABLES):
        source = SCRIPT_ROOT / name
        if not source.is_file():
            continue
        for node in ast.walk(ast.parse(source.read_text())):
            if isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                imported = node.module.split(".")[0]
            elif isinstance(node, ast.Import):
                imported = node.names[0].name.split(".")[0]
            else:
                continue
            if imported in available and imported not in shipped:
                raise Refused(
                    f"{name} imports {imported}, which scripts/ holds and SHIPPED_EXECUTABLES "
                    f"does not — the shipped copy would fail with an ImportError on the "
                    f"consumer's first invocation"
                )


def assert_total(actual: set[str], classified: set[str], tree: str, constant: str) -> None:
    missing = sorted(actual - classified)
    if missing:
        raise Refused(
            f"{tree} holds {', '.join(missing)}, which {constant} does not classify — decide "
            f"whether each ships before it can be assembled either way"
        )
    stale = sorted(classified - actual)
    if stale:
        raise Refused(
            f"{constant} classifies {', '.join(stale)}, which {tree} no longer holds — "
            f"specs/0008 R5: no file survives whose source was removed"
        )


def plan() -> tuple[list[dict], list[dict], list[str]]:
    """Every file to install, every capability, and what was skipped and why.

    Returns before writing anything, so a refusal costs nothing and so a caller can inspect the
    assembly without a distribution existing.
    """
    if not SOURCE_ROOT.is_dir():
        raise Refused(f"{SOURCE_ROOT} does not exist; there is no framework source to assemble")

    files: list[dict] = []
    capabilities: list[dict] = []
    skipped: list[str] = []
    exercised = exercised_names()

    def add(dest: str, source: Path) -> bytes:
        body = source.read_bytes()
        files.append(
            {"path": dest, "source": str(source.relative_to(REPO_ROOT)), "digest": digest(body)}
        )
        return body

    # The plugin manifest. specs/0008 R1 makes its presence what defines a plugin root.
    manifest_source = SOURCE_ROOT / PLUGIN_DIR / "plugin.json"
    if not manifest_source.is_file():
        raise Refused(f"{manifest_source} is missing; specs/0008 R1 requires it at the plugin root")
    add(f"{PLUGIN_DIR}/plugin.json", manifest_source)

    # Skills: one directory per skill, SKILL.md the entrypoint.
    skills_root = SOURCE_ROOT / "skills"
    if skills_root.is_dir():
        for skill in sorted(p for p in skills_root.iterdir() if p.is_dir()):
            if skill.name not in exercised:
                skipped.append(f"skill {skill.name}: no fixture exercises it (specs/0006 R11, R14)")
                continue
            for source in sorted(p for p in skill.rglob("*") if p.is_file()):
                add(f"skills/{skill.name}/{source.relative_to(skill).as_posix()}", source)
            capabilities.append(
                {
                    "name": skill.name,
                    "class": CLASS_BY_TREE["skills"],
                    "status": "active",
                    "path": f"skills/{skill.name}/SKILL.md",
                }
            )

    # Agents: one file per agent, the stem equal to its name.
    agents_root = SOURCE_ROOT / "agents"
    if agents_root.is_dir():
        for source in sorted(agents_root.rglob("*.md")):
            name = source.stem
            if name not in exercised:
                skipped.append(f"agent {name}: no fixture exercises it (specs/0006 R11, R14)")
                continue
            add(f"agents/{name}.md", source)
            capabilities.append(
                {
                    "name": name,
                    "class": CLASS_BY_TREE["agents"],
                    "status": "active",
                    "path": f"agents/{name}.md",
                }
            )

    # Schemas Siegard resolves through ${CLAUDE_PLUGIN_ROOT}; the harness never reads these.
    present = {p.name for p in SCHEMA_ROOT.glob("*.json") if p.name != "contract-versions.json"}
    assert_total(present, set(SHIPPED_SCHEMAS), "schemas/", "SHIPPED_SCHEMAS")
    schemas: list[dict] = []
    for name in sorted(n for n, reason in SHIPPED_SCHEMAS.items() if reason):
        source = SCHEMA_ROOT / name
        add(f"schemas/{name}", source)
        stem, _, _ = name.partition(".v")
        version = name.split(".v")[1].split(".json")[0]
        schemas.append({"contract_version": f"{stem}/{version}", "path": f"schemas/{name}"})

    # Executables. Their own directory is the import root, which is why workflow_lib.py is here.
    assert_imports_ship()
    for name in sorted(SHIPPED_EXECUTABLES):
        source = SCRIPT_ROOT / name
        if not source.is_file():
            raise Refused(f"SHIPPED_EXECUTABLES names {name}, which scripts/ does not hold")
        add(f"bin/{name}", source)
        capabilities.append(
            {"name": source.stem.replace("_", "-"), "class": "script", "status": "active",
             "path": f"bin/{name}"}
        )

    return files, capabilities, skipped


def build(target: Path) -> tuple[list[dict], list[str]]:
    """Write the planned distribution into `target`, replacing whatever was there."""
    files, capabilities, skipped = plan()

    source_digest = digest(
        json.dumps(
            [[entry["source"], entry["digest"]] for entry in sorted(files, key=lambda e: e["path"])],
            separators=(",", ":"),
        ).encode("utf-8")
    )

    manifest = {
        "contract_version": "distribution-manifest/1",
        "source_revision": source_digest,
        "generator_version": GENERATOR_VERSION,
        "installed": sorted(files, key=lambda e: e["path"]),
        "schemas": sorted(
            (
                {"contract_version": s["contract_version"], "path": s["path"]}
                for s in (
                    {
                        "contract_version": f"{n.partition('.v')[0]}/{n.split('.v')[1].split('.json')[0]}",
                        "path": f"schemas/{n}",
                    }
                    for n, reason in SHIPPED_SCHEMAS.items()
                    if reason
                )
            ),
            key=lambda s: s["path"],
        ),
        "capabilities": sorted(capabilities, key=lambda c: (c["class"], c["name"])),
        "overrides": [],
    }
    body = json.dumps(manifest, indent=2) + "\n"
    manifest_entry = {
        "path": MANIFEST_NAME,
        "source": "scripts/generate_dist.py",
        "digest": digest(body.encode("utf-8")),
    }
    manifest["installed"] = sorted(manifest["installed"] + [manifest_entry], key=lambda e: e["path"])
    body = json.dumps(manifest, indent=2) + "\n"

    if target.exists():
        shutil.rmtree(target)
    for entry in files:
        destination = target / entry["path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((REPO_ROOT / entry["source"]).read_bytes())
    (target / MANIFEST_NAME).write_text(body)

    return manifest["installed"], skipped


def main() -> int:
    args = sys.argv[1:]
    if args and (len(args) != 2 or args[0] != "--into"):
        cannot_run("cannot run: usage: generate_dist.py [--into DIR]")
    target = Path(args[1]) if args else DEFAULT_TARGET

    try:
        installed, skipped = build(target)
    except Refused as exc:
        print(f"refused to assemble: {exc}", file=sys.stderr)
        return 1

    try:
        shown = target.relative_to(REPO_ROOT)
    except ValueError:
        shown = target
    print(f"assembled {len(installed)} file(s) into {shown}  generator: {GENERATOR_VERSION}")
    for note in skipped:
        print(f"  skipped: {note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
