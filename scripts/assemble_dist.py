#!/usr/bin/env python3
"""Assemble the distribution from framework source, and check the committed one against it.

`dist/.claude/` is the product. `src/claude/` is what it is assembled from, and nothing outside
that tree can reach a consumer.

**What ships is decided by location.** The set of installed directories is closed and listed
below: a file ships because it sits in one of them, not because a table here names it. Two files
at the root of `src/claude/` are outside every one of them and so do not ship —
`capabilities.declaration.json`, which is authored input to this script, and `CLAUDE.md`, which
governs work in a repository that installs the framework rather than being installed by it.

**Deterministic, or it cannot be checked.** Every iteration is sorted and the manifest carries no
timestamp. A value minted at assembly time would differ between two runs over identical source,
and then `--check` could never tell a stale distribution from a fresh one.

**`source_revision` is a digest of the inputs, not a commit.** A commit SHA would make the
committed distribution unverifiable: assembling at commit N-1 records N-1, committing the result
produces commit N, and the next check regenerates, reads HEAD as N, and reports a difference
nobody introduced. A digest over the source identifies it exactly, is stable across commits that
do not touch it, and needs no version control at all.

**It refuses rather than shipping something broken.** A shipped module importing a file that does
not ship would fail with an ImportError in the consumer's hands, so the import graph is checked
before anything is written. A manifest that does not satisfy its own contract stops the run.

**`--check` compares and never writes**, for the reason every other check here does not repair: a
check that fixes what it was meant to detect reports success on a defect.

Declared dependencies: jsonschema.

Usage:  assemble_dist.py [--check] [--into=<dir>]
Exit:   0 assembled, or the committed distribution matches
        1 --check and the distribution is stale
        2 cannot run — source is missing, an import would not ship, the manifest is invalid
"""

from __future__ import annotations

import ast
import hashlib
import json
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SOURCE = REPO / "src" / "claude"
DEFAULT_TARGET = REPO / "dist" / ".claude"
MANIFEST_NAME = "siegard-manifest.json"
MANIFEST_CONTRACT = SOURCE / "schemas" / "distribution-manifest.json"
DECLARATION = SOURCE / "capabilities.declaration.json"

# Bumped when this script's output changes for unchanged source. The distribution is a function of
# the source *and* the assembler, so a consumer seeing a difference can attribute it to one or the
# other. `1.0.0` was the generator this replaces; its output is not reproduced byte for byte.
GENERATOR_VERSION = "2.0.0"

CANNOT_RUN = 2

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover - exercised by the environment, not the suite
    print("cannot run: jsonschema is not installed (pip install jsonschema)", file=sys.stderr)
    raise SystemExit(CANNOT_RUN)


class Refused(Exception):
    """The distribution is not assembled, and nothing is written."""


def shown(path: Path) -> str:
    """A path as a reader recognises it: relative to the repository where it sits inside one.

    `--into` may point anywhere, and a target outside the repository has no relative form. Naming
    it absolutely is right there; crashing while reporting a successful assembly is not, and that
    is what asking for the relative form unconditionally did.
    """
    try:
        return path.relative_to(REPO).as_posix()
    except ValueError:
        return str(path)


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def is_runnable(source: Path) -> bool:
    """Whether a shipped module is a capability or a library a sibling imports.

    Read from the file rather than from a list. A module with an entry-point guard is run; one
    without is imported, and a list of exemptions kept beside them would be a second place for a
    fact the file already states.
    """
    return 'if __name__ == "__main__":' in source.read_text(encoding="utf-8")


def imported_names(source: Path) -> set[str]:
    """Every top-level module name this file imports."""
    found: set[str] = set()
    for node in ast.walk(ast.parse(source.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            found |= {alias.name.split(".")[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            found.add(node.module.split(".")[0])
    return found


def assert_imports_ship(scripts: list[Path]) -> None:
    """Refuse where a shipped module imports a file this repository holds and does not ship.

    Their own directory is the import root once installed, so a sibling under `bin/` resolves and
    anything else does not. An import of the generator's own tree is the case that matters: it
    works in this repository, where both are on the path, and raises ImportError in the consumer's
    hands, where only one was installed. Names that resolve to no file here are environment
    dependencies, which each module declares in its own docstring.
    """
    shipped = {path.stem for path in scripts}
    for path in scripts:
        for name in sorted(imported_names(path) - shipped):
            elsewhere = [p for p in REPO.rglob(f"{name}.py")
                         if "__pycache__" not in p.parts and SOURCE not in p.parents]
            if elsewhere:
                raise Refused(
                    f"{path.relative_to(REPO)} imports `{name}`, which this repository holds at "
                    f"{elsewhere[0].relative_to(REPO)} and does not ship. The installed copy would "
                    f"fail with an ImportError the moment it ran"
                )


def declarations() -> dict[str, dict]:
    if not DECLARATION.is_file():
        return {}
    return {entry["identifier"]: entry
            for entry in json.loads(DECLARATION.read_text(encoding="utf-8"))["declarations"]}


def plan() -> tuple[list[dict], list[dict], list[str]]:
    """Every file to install, every capability, and every capability nothing declares.

    Returns before anything is written, so a refusal costs nothing and a caller can inspect the
    assembly without a distribution existing.
    """
    if not SOURCE.is_dir():
        raise Refused(f"{SOURCE} does not exist; there is no framework source to assemble")

    files: list[dict] = []
    capabilities: list[dict] = []
    declared = declarations()

    def add(dest: str, source: Path) -> None:
        files.append({"path": dest, "source": source.relative_to(REPO).as_posix(),
                      "digest": digest(source.read_bytes())})

    def capability(name: str, klass: str, path: str) -> None:
        entry = {"name": name, "class": klass, "status": "active", "path": path}
        if name in declared:
            # Folded in rather than authored twice. `identifier` and `class` are dropped because
            # this entry already holds both.
            entry["declaration"] = {k: v for k, v in declared[name].items()
                                    if k not in ("identifier", "class")}
        capabilities.append(entry)

    plugin = SOURCE / ".claude-plugin" / "plugin.json"
    if not plugin.is_file():
        raise Refused(f"{plugin} is missing; its presence at the plugin root is what defines one")
    add(".claude-plugin/plugin.json", plugin)

    skills = SOURCE / "skills"
    if skills.is_dir():
        for skill in sorted(p for p in skills.iterdir() if p.is_dir()):
            for source in sorted(p for p in skill.rglob("*") if p.is_file()):
                add(f"skills/{skill.name}/{source.relative_to(skill).as_posix()}", source)
            capability(skill.name, "skill", f"skills/{skill.name}/SKILL.md")

    agents = SOURCE / "agents"
    if agents.is_dir():
        for source in sorted(agents.glob("*.md")):
            add(f"agents/{source.name}", source)
            capability(source.stem, "specialized-agent", f"agents/{source.name}")

    schemas: list[dict] = []
    for source in sorted((SOURCE / "schemas").glob("*.json")):
        add(f"schemas/{source.name}", source)
        const = json.loads(source.read_text(encoding="utf-8")) \
            .get("properties", {}).get("contract_version", {}).get("const")
        if const:
            schemas.append({"contract_version": const, "path": f"schemas/{source.name}"})

    for source in sorted((SOURCE / "templates").glob("*.md")):
        add(f"templates/{source.name}", source)

    scripts = sorted((SOURCE / "bin").glob("*.py"))
    assert_imports_ship(scripts)
    for source in scripts:
        add(f"bin/{source.name}", source)
        if is_runnable(source):
            capability(source.stem.replace("_", "-"), "script", f"bin/{source.name}")

    undeclared = sorted(c["name"] for c in capabilities if "declaration" not in c)
    return files, sorted(capabilities, key=lambda c: (c["class"], c["name"])), undeclared, schemas


def build() -> tuple[dict[str, bytes], dict, list[str]]:
    """The bytes of every installed file, the manifest, and what nothing declares."""
    files, capabilities, undeclared, schemas = plan()

    # Over the inputs, sorted, so the same source always produces the same revision and a change
    # to any one file changes it.
    revision = hashlib.sha256()
    for entry in sorted(files, key=lambda f: f["path"]):
        revision.update(f"{entry['path']}\0{entry['digest']}\0".encode())

    manifest = {
        "contract_version": "distribution-manifest/2",
        "source_revision": "sha256:" + revision.hexdigest(),
        "generator_version": GENERATOR_VERSION,
        "installed": sorted(files, key=lambda f: f["path"]),
        "schemas": schemas,
        "capabilities": capabilities,
        "overrides": [],
    }

    contract = json.loads(MANIFEST_CONTRACT.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(contract).iter_errors(manifest), key=str)
    if errors:
        raise Refused(
            f"the manifest does not satisfy {shown(MANIFEST_CONTRACT)}: "
            f"{errors[0].message}"
        )

    written = {entry["path"]: (REPO / entry["source"]).read_bytes() for entry in files}
    written[MANIFEST_NAME] = json.dumps(manifest, indent=2, ensure_ascii=False).encode() + b"\n"
    return written, manifest, undeclared


def main() -> int:
    verify = "--check" in sys.argv[1:]
    target = Path(next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--into=")),
                       DEFAULT_TARGET))
    if [a for a in sys.argv[1:] if not a.startswith("--")]:
        print("cannot run: expected [--check] [--into=<dir>]", file=sys.stderr)
        return CANNOT_RUN

    try:
        written, manifest, undeclared = build()
    except Refused as refused:
        print(f"cannot run: {refused}", file=sys.stderr)
        return CANNOT_RUN

    present = {p.relative_to(target).as_posix() for p in target.rglob("*") if p.is_file()} \
        if target.is_dir() else set()

    if verify:
        stale = sorted({name for name, body in written.items()
                        if name not in present or (target / name).read_bytes() != body}
                       | (present - set(written)))
        print(f"distribution checked: {len(written)} file(s) against {shown(target)}")
        if stale:
            print(f"STALE: {len(stale)} file(s) differ or should not be there — "
                  f"{', '.join(stale[:6])}{' …' if len(stale) > 6 else ''}")
            print("Run without --check to reassemble; do not edit the distribution, because every "
                  "file in it originates in src/claude/.")
            return 1
        return 0

    for name in sorted(present - set(written)):
        # A file whose source was removed does not survive an assembly, or the distribution would
        # keep shipping what the framework no longer holds.
        (target / name).unlink()
    for name, body in sorted(written.items()):
        path = target / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.is_file() or path.read_bytes() != body:
            path.write_bytes(body)
    for directory in sorted((p for p in target.rglob("*") if p.is_dir()), reverse=True):
        if not any(directory.iterdir()):
            directory.rmdir()

    removed = len(present - set(written))
    print(f"assembled {shown(target)}: {len(written)} file(s), "
          f"{len(manifest['capabilities'])} capabilit(ies), {len(manifest['schemas'])} schema(s)"
          + (f", {removed} removed" if removed else ""))
    print(f"source revision {manifest['source_revision']}")
    if undeclared:
        # Reported and not refused: the declaration set is authored, and a capability newly added
        # to `bin/` has none until somebody writes it. Shipping it silently is what must not
        # happen — a capability with no declaration reaches a consumer with no contract.
        print(f"\n{len(undeclared)} capabilit(ies) reach a consumer with no declaration: "
              f"{', '.join(undeclared)}")
        print(f"Each is installed and governed by nothing. Declare them in "
              f"{shown(DECLARATION)}.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
