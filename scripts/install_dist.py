#!/usr/bin/env python3
"""Install and upgrade the Siegard distribution in a repository it governs.

specs/0008 states three behaviours nothing implemented. R16: enabling the same version twice
leaves the repository in the same state as enabling it once. R17: an upgrade does not silently
overwrite an installed file that diverges from what the distribution manifest records — it
detects the divergence, names the file, and stops. R21: a consumer's own agent definition
overrides a same-named plugin agent, and the framework reports that shadowing rather than
trying to prevent it by choosing an unlikely name.

**Where a plugin lives is the harness's business, not this script's.** The target is an explicit
argument. specs/0008 R22 states the framework claims no path outside its own plugin root, and a
script that guessed an installation convention would be claiming one — so it refuses a target it
was not given and writes nothing outside it.

**Upgrade compares against the manifest, never against the incoming files.** A file that differs
from the *new* distribution might simply be old; a file that differs from what the *installed*
manifest recorded was changed by someone. Only the second is a divergence, and conflating them
would either overwrite a consumer's work or refuse every legitimate upgrade.

**A divergence stops the whole upgrade, not just the file.** A partial upgrade leaves an
installation matching no manifest at all, which is a worse state than the one it started in.

Declared dependencies: none beyond the standard library.

Usage:
  install_dist.py install --source DIST --target DIR [--project DIR]
  install_dist.py upgrade --source DIST --target DIR [--project DIR]
  install_dist.py status  --target DIR [--project DIR]
Exit: 0 done, 1 refused (divergence, or an installation that is not one), 2 cannot run
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

from cli import cannot_run

MANIFEST_NAME = "siegard-manifest.json"


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


# Bytecode the interpreter writes beside a shipped executable. Not installed, has no source, and
# present in any installation whose scripts have run once — see scripts/verify_dist.py.
RUNTIME_ARTIFACTS = ("__pycache__",)


def tree(root: Path) -> dict[str, bytes]:
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in sorted(root.rglob("*"))
        if p.is_file() and not any(part in RUNTIME_ARTIFACTS for part in p.relative_to(root).parts)
    }


def read_manifest(root: Path) -> dict:
    path = root / MANIFEST_NAME
    if not path.is_file():
        cannot_run(f"cannot run: {path} does not exist; this is not a Siegard distribution")
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        cannot_run(f"cannot run: {path} is not valid JSON: {exc}")


def divergences(target: Path) -> list[str]:
    """Files the installed manifest recorded that no longer match what is on disk.

    This is R17's detection. It reads only the installed manifest, so it answers "what changed
    since installation" without any reference to what is being installed next.
    """
    manifest = read_manifest(target)
    installed = tree(target)
    problems: list[str] = []
    for entry in manifest["installed"]:
        path, recorded = entry["path"], entry["digest"]
        if path == MANIFEST_NAME:
            continue
        if path not in installed:
            problems.append(f"{path}: recorded in the installed manifest and missing from disk")
        elif digest(installed[path]) != recorded:
            problems.append(f"{path}: changed since installation")
    for path in sorted(set(installed) - {e["path"] for e in manifest["installed"]}):
        problems.append(f"{path}: present in the installation and named by no manifest entry")
    return problems


def shadowed(source: Path, project: Path) -> list[str]:
    """Plugin agents a project-level definition of the same name would override.

    specs/0008 R21: the precedence resolves in the consumer's favour, which is correct, and the
    exposure is a capability silently lost. ADR-0012 records the choice to report it rather than
    pick an improbable name — a name chosen to be unlikely is a convention hoped to work.
    """
    manifest = read_manifest(source)
    shipped = {
        Path(c["path"]).stem
        for c in manifest["capabilities"]
        if c["class"] == "specialized-agent"
    }
    local = project / ".claude" / "agents"
    if not local.is_dir():
        return []
    return sorted(
        f"{p.stem}: a project agent at {p.relative_to(project)} overrides the plugin agent of the "
        f"same name, so the shipped capability is not reachable"
        for p in local.rglob("*.md")
        if p.stem in shipped
    )


def write(source: Path, target: Path) -> int:
    """Replace `target` with `source`, writing nothing outside it."""
    if target.exists():
        shutil.rmtree(target)
    files = tree(source)
    for path, body in files.items():
        destination = target / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(body)
    return len(files)


def report(notes: list[str], heading: str) -> None:
    print(f"{heading}: {len(notes)}")
    for note in notes:
        print(f"  {note}")


def main() -> int:
    parser = argparse.ArgumentParser(prog="install_dist.py", add_help=True)
    parser.add_argument("action", choices=["install", "upgrade", "status"])
    parser.add_argument("--source", type=Path, help="the distribution to install")
    parser.add_argument("--target", type=Path, required=True, help="where the plugin lives")
    parser.add_argument("--project", type=Path, help="the governed repository, for shadowing checks")
    args = parser.parse_args()

    if args.action in ("install", "upgrade"):
        if args.source is None:
            cannot_run("cannot run: --source is required to install or upgrade")
        if not (args.source / MANIFEST_NAME).is_file():
            cannot_run(f"cannot run: {args.source} holds no {MANIFEST_NAME}")

    if args.action == "status":
        problems = divergences(args.target)
        report(problems, "divergences")
        if args.project:
            report(shadowed(args.target, args.project), "shadowed agents")
        return 1 if problems else 0

    if args.action == "install":
        if args.target.exists() and any(args.target.iterdir()):
            print(
                f"refused: {args.target} is not empty. Installing over an existing tree would "
                f"discard whatever is there; use `upgrade`, which detects a consumer's changes "
                f"and stops (specs/0008 R17).",
                file=sys.stderr,
            )
            return 1
        count = write(args.source, args.target)
        version = json.loads((args.target / ".claude-plugin" / "plugin.json").read_text())["version"]
        print(f"installed {count} file(s) into {args.target}  version: {version}")
        if args.project:
            report(shadowed(args.target, args.project), "shadowed agents")
        return 0

    # upgrade
    if not (args.target / MANIFEST_NAME).is_file():
        print(
            f"refused: {args.target} holds no {MANIFEST_NAME}, so there is nothing to upgrade "
            f"from. Use `install`.",
            file=sys.stderr,
        )
        return 1

    changed = divergences(args.target)
    if changed:
        print(
            f"refused: {len(changed)} installed file(s) changed since installation. specs/0008 "
            f"R17: a consumer's local change is theirs to keep or theirs to discard, never the "
            f"framework's to erase without saying so.",
            file=sys.stderr,
        )
        for note in changed:
            print(f"  {note}", file=sys.stderr)
        return 1

    before = read_manifest(args.target)["source_revision"]
    after = read_manifest(args.source)["source_revision"]
    if before == after:
        print(f"already at {after}; nothing to do")
        if args.project:
            report(shadowed(args.target, args.project), "shadowed agents")
        return 0

    count = write(args.source, args.target)
    print(f"upgraded {count} file(s) in {args.target}\n  from {before}\n  to   {after}")
    if args.project:
        report(shadowed(args.target, args.project), "shadowed agents")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
