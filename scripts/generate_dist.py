#!/usr/bin/env python3
"""Assemble the Siegard distribution from framework source.

foundation/0008 fixes the output contract and leaves the assembly free. What it fixes: the
distribution is a plugin root holding `.claude-plugin/plugin.json` (R1); running this twice
over the same committed source produces byte-identical output (R4); every installed file
originates in framework source and no file survives whose source was removed (R5); the
directory set is closed and an empty one is omitted rather than shipped (R7); only
`plugin.json` goes inside `.claude-plugin/` (R8); a shipped executable lives in `bin/` (R9);
no `rules/` (R10) and no `packs/` (R23).

**What ships is decided by location, not by this script.** `src/claude/` is the framework
source and assembly copies it; nothing outside it can reach the output. Classifying a mixed
tree file by file would put the fact in two places — the table and the filesystem — and a
misfiled contract would then govern two audiences at once with nothing to catch it.

**Determinism has one requirement and one consequence.** Every iteration is sorted, and the
manifest carries no timestamp: a value minted at generation time would differ between two runs
over identical source, which R4 calls a defect rather than an acceptable variation. foundation/0008
R12 lists what the manifest records and a timestamp is not among them.

**`source_revision` is a content digest, not a commit SHA.** A SHA would make the committed
distribution unverifiable: generating at commit N-1 records N-1, committing the result produces
commit N, and the next `make dist-check` would regenerate, read HEAD as N, and report a
difference nobody introduced. A digest over the framework source inputs identifies the source
exactly, is stable across commits that do not touch it, and needs no VCS at all.

**Capability status is derived, never labelled.** foundation/0006 R17 requires exactly that, and R14
states `proposed` ships nothing. What ships is what `src/claude/` holds, so every capability
assembled here is `active` by derivation. A fixture is evidence and never a gate: gating on one
lets an optional support tool decide what a consumer receives.

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

import generator_lib  # noqa: F401  (puts src/claude/bin on the import path)
from cli import cannot_run

REPO_ROOT = Path(__file__).resolve().parent.parent
# Everything that ships lives under one root, and nothing else does. That is the whole of
# the boundary: assembly copies this tree, so a file ships because of where it sits rather
# than because a table in this script says so. A table would be a second place for a fact the
# filesystem already holds, and the two diverge silently.
SOURCE_ROOT = REPO_ROOT / "src" / "claude"
SCHEMA_ROOT = SOURCE_ROOT / "schemas"
SCRIPT_ROOT = SOURCE_ROOT / "bin"
TEMPLATE_ROOT = SOURCE_ROOT / "templates"
DEFAULT_TARGET = REPO_ROOT / "dist" / ".claude"

# Bumped whenever this script's output changes for unchanged source. foundation/0008 R4 makes the
# distribution a function of the source *and* the generator, so a consumer that sees a
# difference can attribute it to one or the other.
GENERATOR_VERSION = "1.0.0"

MANIFEST_NAME = "siegard-manifest.json"
PLUGIN_DIR = ".claude-plugin"

# Which capability class each source subtree carries, per foundation/0006 R1.
CLASS_BY_TREE = {"skills": "skill", "agents": "specialized-agent"}

HOOK_DECLARATION = "hooks.declaration.json"

# The authored declaration set. It stays behind for the reason hooks.declaration.json does:
# foundation/0007 R23 keeps a declaration out of the distribution, and R12a there makes the
# manifest the surface a consumer reads instead.
CAPABILITY_DECLARATION = "capabilities.declaration.json"


def hook_declaration() -> list[dict]:
    """The authored hook declarations, or an empty list when no hook ships.

    Read rather than hardcoded: `foundation/0010` R10 and R11 require a hook to state its event,
    matcher, guarantee, and timeout, and a registry living inside this script would be a rule only
    a script could see. `schemas/hook.json` is its contract and `validate_components.py` checks
    it, so the generator consumes something already validated.
    """
    path = SOURCE_ROOT / "hooks" / HOOK_DECLARATION
    if not path.is_file():
        return []
    return json.loads(path.read_text())["hooks"]


def contract_of(source: Path) -> str:
    """The contract version a shipped schema file declares.

    From the document, which is the only place it lives: a filename carries the contract's
    identity and never its version, so one contract has one file and the version inside it moves
    without anything being renamed. `artifact-classes.json` is an instance rather than a contract
    and declares its own `contract_version` at the top level, which is why both shapes are read.
    """
    document = json.loads(source.read_text())
    declared = document.get("properties", {}).get("contract_version", {}).get("const")
    return declared or document["contract_version"]


class Refused(Exception):
    """The generator will not assemble a distribution it cannot justify."""


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def assert_imports_ship() -> None:
    """A shipped script may only import modules that ship beside it.

    Found the hard way: `orchestrate.py` gained `from cli import cannot_run`, and nothing
    noticed that `cli.py` did not ship with it. The distribution still built, still
    verified, and would have failed on the consumer's first invocation with an ImportError —
    the worst place to discover it, because `foundation/0008` R9 exists so a shipped executable
    "exits with a named error" rather than breaking in a way nobody can read.

    Only a module the generator holds is checked. A standard-library or third-party import is
    R9's other half, which each script declares in its own docstring. The direction is the whole
    check: the generator may import from the shipped tree, and the shipped tree may not import
    back.
    """
    shipped = {p.stem for p in SCRIPT_ROOT.glob("*.py")}
    generator_only = {p.stem for p in (REPO_ROOT / "scripts").glob("*.py")} - shipped
    for source in sorted(SCRIPT_ROOT.glob("*.py")):
        name = source.name
        for node in ast.walk(ast.parse(source.read_text())):
            if isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                imported = node.module.split(".")[0]
            elif isinstance(node, ast.Import):
                imported = node.names[0].name.split(".")[0]
            else:
                continue
            if imported in generator_only:
                raise Refused(
                    f"{name} imports {imported}, which is the generator's and does not ship — "
                    f"the installed copy would fail with an ImportError on the consumer's "
                    f"first invocation"
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
            f"foundation/0008 R5: no file survives whose source was removed"
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

    def add(dest: str, source: Path) -> bytes:
        body = source.read_bytes()
        files.append(
            {"path": dest, "source": str(source.relative_to(REPO_ROOT)), "digest": digest(body)}
        )
        return body

    # The plugin manifest. foundation/0008 R1 makes its presence what defines a plugin root.
    manifest_source = SOURCE_ROOT / PLUGIN_DIR / "plugin.json"
    if not manifest_source.is_file():
        raise Refused(f"{manifest_source} is missing; foundation/0008 R1 requires it at the plugin root")
    add(f"{PLUGIN_DIR}/plugin.json", manifest_source)

    # Skills: one directory per skill, SKILL.md the entrypoint.
    skills_root = SOURCE_ROOT / "skills"
    if skills_root.is_dir():
        for skill in sorted(p for p in skills_root.iterdir() if p.is_dir()):
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
    for source in sorted(SCHEMA_ROOT.glob("*.json")):
        add(f"schemas/{source.name}", source)

    # Hooks. foundation/0008 R3 puts them in force while the plugin is enabled, which is what makes a
    # session-wide guarantee installable at all.
    hooks_root = SOURCE_ROOT / "hooks"
    if hooks_root.is_dir():
        declared = {entry["file"] for entry in hook_declaration()}
        present = {p.name for p in hooks_root.iterdir() if p.is_file() and p.name != HOOK_DECLARATION}
        assert_total(present, declared, "src/claude/hooks/", HOOK_DECLARATION)
        for name in sorted(declared):
            add(f"hooks/{name}", hooks_root / name)
            capabilities.append(
                {"name": Path(name).stem, "class": "hook", "status": "active",
                 "path": f"hooks/{name}"}
            )

    # Scaffolds a consumer expands. foundation/0008 names `templates/` in the closed set.
    for source in sorted(TEMPLATE_ROOT.glob("*.md")):
        add(f"templates/{source.name}", source)

    # Executables. Their own directory is the import root, which is why a shipped module importing a
    # sibling resolves it and one importing the generator's own tree does not.
    assert_imports_ship()
    for source in sorted(SCRIPT_ROOT.glob("*.py")):
        add(f"bin/{source.name}", source)
        capabilities.append(
            {"name": source.stem.replace("_", "-"), "class": "script", "status": "active",
             "path": f"bin/{source.name}"}
        )

    attach_declarations(capabilities)
    return files, capabilities, skipped


def attach_declarations(capabilities: list[dict]) -> None:
    """Fold the authored declaration set into the catalog the manifest carries.

    `foundation/0008` R12 puts a declaration in the manifest and R12a makes the manifest the only
    way one reaches a consumer, because `foundation/0007` R23 keeps the authored file out of the
    distribution. Derived rather than authored a second time: an entry that disagreed with the
    declaration it came from would be the generator defect R12a names, so nothing here edits a
    field the declaration already carries.

    `identifier` and `class` are dropped from what is attached. The manifest entry already holds
    both, and copying them in would put the same fact twice inside one record.
    """
    path = SOURCE_ROOT / CAPABILITY_DECLARATION
    if not path.is_file():
        return
    document = json.loads(path.read_text())
    by_identifier = {entry["identifier"]: entry for entry in document["declarations"]}
    for capability in capabilities:
        entry = by_identifier.get(capability["name"])
        if entry is None:
            continue
        capability["declaration"] = {
            key: value for key, value in entry.items() if key not in ("identifier", "class")
        }


def hooks_document() -> str | None:
    """`hooks/hooks.json`, or None when nothing ships a hook.

    Computed rather than authored: `foundation/0010` R10 requires each hook to state its event, its
    matcher, and its guarantee, and R11 requires it to state its own timeout. Those facts live in
    `SHIPPED_HOOKS` beside the decision to ship, so a hook cannot be installed with a matcher
    nobody wrote down. `${CLAUDE_PLUGIN_ROOT}` is what makes the command path resolve wherever the
    consumer installed the plugin — ADR-0012 cites the documentation that establishes it.
    """
    declared = hook_declaration()
    if not declared:
        return None
    events = sorted({entry["event"] for entry in declared})
    return json.dumps(
        {
            "hooks": {
                event: [
                    {
                        "matcher": entry["matcher"],
                        "hooks": [
                            {
                                "type": "command",
                                "command": "${CLAUDE_PLUGIN_ROOT}/hooks/" + entry["file"],
                                "timeout": entry["timeout"],
                            }
                        ],
                    }
                    for entry in sorted(declared, key=lambda e: e["file"])
                    if entry["event"] == event
                ]
                for event in events
            }
        },
        indent=2,
    ) + "\n"


def build(target: Path) -> tuple[list[dict], list[str]]:
    """Write the planned distribution into `target`, replacing whatever was there.

    Two files have no source of their own and are recorded against the generator: `hooks/hooks.json`
    and the manifest. Everything else is copied byte for byte from framework source.
    """
    files, capabilities, skipped = plan()

    computed: dict[str, str] = {}
    hooks_json = hooks_document() if any(e["path"].startswith("hooks/") for e in files) else None
    if hooks_json is not None:
        computed["hooks/hooks.json"] = hooks_json
        files.append(
            {
                "path": "hooks/hooks.json",
                "source": "scripts/generate_dist.py",
                "digest": digest(hooks_json.encode("utf-8")),
            }
        )

    source_digest = digest(
        json.dumps(
            [[e["source"], e["digest"]] for e in sorted(files, key=lambda e: e["path"])],
            separators=(",", ":"),
        ).encode("utf-8")
    )

    manifest = {
        "contract_version": "distribution-manifest/2",
        "source_revision": source_digest,
        "generator_version": GENERATOR_VERSION,
        "installed": sorted(files, key=lambda e: e["path"]),
        "schemas": sorted(
            (
                {
                    "contract_version": contract_of(REPO_ROOT / entry["source"]),
                    "path": entry["path"],
                }
                for entry in files
                if entry["path"].startswith("schemas/")
            ),
            key=lambda s: s["path"],
        ),
        "capabilities": sorted(capabilities, key=lambda c: (c["class"], c["name"])),
        "overrides": [],
    }

    # The manifest records itself, so its digest is taken over the body without the self-entry and
    # the body is then rendered again with it. Any other order would need the digest of a document
    # that contains its own digest.
    body = json.dumps(manifest, indent=2) + "\n"
    manifest["installed"] = sorted(
        manifest["installed"]
        + [{"path": MANIFEST_NAME, "source": "scripts/generate_dist.py",
            "digest": digest(body.encode("utf-8"))}],
        key=lambda e: e["path"],
    )
    body = json.dumps(manifest, indent=2) + "\n"

    if target.exists():
        shutil.rmtree(target)
    for entry in files:
        destination = target / entry["path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        if entry["path"] in computed:
            destination.write_text(computed[entry["path"]])
        else:
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
