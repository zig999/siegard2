#!/usr/bin/env python3
"""Verify the committed distribution without touching it.

foundation/0007 R6: "Verification is separate from production. The command that checks regenerates
into a temporary location and compares; it never writes into the distribution it is checking,
because a check that repairs what it was meant to detect reports success on a defect."

Two layers, and the second is why this is not just a diff.

**Comparison.** Regenerate into a temporary tree and compare byte for byte. This catches a
distribution that drifted from its source: a hand-edited file, a component whose source was
removed, a schema that changed without the tree being rebuilt.

**Invariants.** Everything below is computed from the committed tree itself, never from the
generator's plan. A comparison alone cannot catch a generator that is *consistently* wrong —
it would produce the same defect twice and report agreement. These checks fail on the tree no
matter what produced it, which is the part that survives a bug in the thing being verified.

The invariants are the requirements that name an output rather than a process: no source-only
path reaches the distribution (`.claude/rules/distribution.md`), no secret or environment-specific
value does, no empty directory ships (R7), only `plugin.json` sits inside `.claude-plugin/` (R8),
there is no `rules/` (R10) and no `packs/` (R23), and the manifest names exactly the files that
exist with the digests they actually have (R12, R17).

Declared dependencies: jsonschema, for validating the manifest against its own contract.

Usage:  scripts/verify_dist.py [dist_root]   (default: dist/.claude)
Exit:   0 the distribution matches its source and holds every invariant, 1 it does not, 2 cannot run
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path

from cli import cannot_run

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TARGET = REPO_ROOT / "dist" / ".claude"
MANIFEST_NAME = "siegard-manifest.json"
MANIFEST_SCHEMA = REPO_ROOT / "src" / "claude" / "schemas" / "distribution-manifest.json"

# foundation/0007 R7 closes the directory set; anything else at the plugin root is unshippable.
ALLOWED_ROOT = {".claude-plugin", "skills", "agents", "hooks", "bin", "schemas", "templates"}

# .claude/rules/distribution.md names these. `packs/` is foundation/0007 R22 and `rules/` is R10.
FORBIDDEN_PREFIXES = ("foundation/", "tests/", "fixtures/", "docs/", ".claude/")
FORBIDDEN_DIRS = {"rules", "packs"}

# A credential-shaped value, and an absolute path that would only be true on the build machine.
SECRET_PATTERNS = (
    re.compile(r"(?i)\b(api[_-]?key|secret[_-]?key|access[_-]?token|password|passwd)\b\s*[:=]\s*\S"),
    re.compile(r"(?i)\b(aws_secret_access_key|bearer\s+[A-Za-z0-9._-]{20,})"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
)
HOST_PATH = re.compile(r"(?:^|[\s\"'=(])(/home/[a-z0-9._-]+|/Users/[a-z0-9._-]+)/", re.IGNORECASE)

try:
    from jsonschema import Draft202012Validator
except ImportError:
    cannot_run("cannot run: jsonschema is not installed (pip install jsonschema)")


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


# Bytecode the interpreter writes beside a script it runs. It is not an installed file and has
# no source, so the manifest cannot name it — but a consumer who runs a shipped executable once
# will have it, and reporting it as an unmanaged file would make every upgrade check fail after
# first use. Ignored here rather than in the manifest, because the manifest records what was
# installed and this was not.
RUNTIME_ARTIFACTS = ("__pycache__",)


def tree(root: Path) -> dict[str, bytes]:
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in sorted(root.rglob("*"))
        if p.is_file() and not any(part in RUNTIME_ARTIFACTS for part in p.relative_to(root).parts)
    }


def check_invariants(root: Path, files: dict[str, bytes]) -> list[str]:
    """Everything checkable from the tree alone, independent of what assembled it."""
    problems: list[str] = []

    for entry in sorted(root.iterdir()):
        if entry.name == MANIFEST_NAME:
            continue
        if entry.name not in ALLOWED_ROOT:
            problems.append(
                f"{entry.name}: not in the closed directory set of foundation/0007 R7 — a component "
                f"fitting none of them is not shipped until that specification names a home"
            )
        if entry.name in FORBIDDEN_DIRS:
            problems.append(
                f"{entry.name}/: foundation/0007 forbids it in the distribution "
                f"({'R10' if entry.name == 'rules' else 'R22'})"
            )

    for path in sorted({Path(p).parent for p in files} - {Path(".")}):
        if not any(p.startswith(f"{path.as_posix()}/") for p in files):
            problems.append(f"{path}/: empty, and foundation/0007 R7 omits an empty directory")

    for path in sorted(files):
        if path.startswith(".claude-plugin/") and path != ".claude-plugin/plugin.json":
            problems.append(
                f"{path}: only plugin.json goes inside .claude-plugin/ (foundation/0007 R8) — a "
                f"component placed there is not loaded"
            )
        if any(path.startswith(prefix) for prefix in FORBIDDEN_PREFIXES):
            problems.append(f"{path}: a source-only path reached the distribution")

    for path, body in sorted(files.items()):
        try:
            text = body.decode("utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in SECRET_PATTERNS:
            match = pattern.search(text)
            if match:
                problems.append(f"{path}: looks like a credential at {match.group(0)[:40]!r}")
        match = HOST_PATH.search(text)
        if match:
            problems.append(
                f"{path}: holds the environment-specific path {match.group(1)!r}, which is true "
                f"only on the machine that built this"
            )

    return problems


def check_manifest(root: Path, files: dict[str, bytes]) -> list[str]:
    """The manifest names exactly what exists, with the digests those files actually have."""
    problems: list[str] = []
    manifest_path = root / MANIFEST_NAME
    if not manifest_path.is_file():
        return [f"{MANIFEST_NAME}: missing — foundation/0007 R11 requires it"]

    try:
        manifest = json.loads(manifest_path.read_text())
    except json.JSONDecodeError as exc:
        return [f"{MANIFEST_NAME}: not valid JSON: {exc}"]

    validator = Draft202012Validator(json.loads(MANIFEST_SCHEMA.read_text()))
    for err in sorted(validator.iter_errors(manifest), key=lambda e: list(e.path)):
        where = ".".join(str(p) for p in err.path) or "(root)"
        problems.append(f"{MANIFEST_NAME}: {where}: {err.message}")
    if problems:
        return problems

    recorded = {entry["path"]: entry for entry in manifest["installed"]}
    for path in sorted(set(recorded) | set(files)):
        if path not in files:
            problems.append(f"{path}: recorded in the manifest and absent from the tree")
        elif path not in recorded:
            problems.append(
                f"{path}: present in the tree and absent from the manifest — foundation/0007 R5, no "
                f"file is introduced that has no source"
            )
        elif path != MANIFEST_NAME and recorded[path]["digest"] != digest(files[path]):
            problems.append(
                f"{path}: content does not match the digest the manifest records — either the "
                f"file was hand-edited or the distribution was not regenerated"
            )

    for entry in manifest["installed"]:
        if entry["path"] == MANIFEST_NAME:
            continue
        source = REPO_ROOT / entry["source"]
        if not source.is_file():
            problems.append(
                f"{entry['path']}: its source {entry['source']} no longer exists — foundation/0007 R5, "
                f"no file survives whose source was removed"
            )

    for schema in manifest["schemas"]:
        if schema["path"] not in files:
            problems.append(f"{schema['path']}: recorded as a shipped schema and not installed")

    for capability in manifest["capabilities"]:
        if capability["path"] not in files:
            problems.append(
                f"{capability['path']}: capability {capability['name']!r} is recorded and its "
                f"component is not installed"
            )
        if capability["status"] in ("proposed", "retired"):
            problems.append(
                f"{capability['name']}: status {capability['status']!r} must not appear in an "
                f"installation — foundation/0006 R14, proposed ships nothing and retired is absent"
            )

    return problems


def compare(root: Path) -> list[str]:
    """Regenerate into a temporary tree and diff. Never writes into `root`."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from generate_dist import build  # imported here so the invariants run even if this fails

    with tempfile.TemporaryDirectory() as holder:
        fresh_root = Path(holder) / "dist"
        build(fresh_root)
        fresh, committed = tree(fresh_root), tree(root)

    problems: list[str] = []
    for path in sorted(set(fresh) | set(committed)):
        if path not in committed:
            problems.append(f"{path}: the generator produces it and the committed tree lacks it")
        elif path not in fresh:
            problems.append(f"{path}: committed and the generator no longer produces it")
        elif fresh[path] != committed[path]:
            problems.append(f"{path}: differs from what the generator produces from current source")
    return problems


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_TARGET
    if not root.is_dir():
        print(
            f"cannot run: {root} does not exist — run `make dist` to assemble it",
            file=sys.stderr,
        )
        return 2

    files = tree(root)
    problems = check_invariants(root, files) + check_manifest(root, files) + compare(root)

    try:
        shown = root.relative_to(REPO_ROOT)
    except ValueError:
        shown = root
    print(f"distribution checked: {len(files)} file(s) in {shown}")
    if problems:
        print(f"FAILED: {len(problems)} problem(s)\n")
        for problem in problems:
            print(f"  {problem}")
        return 1
    print("the distribution matches its source and holds every invariant")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
