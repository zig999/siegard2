#!/usr/bin/env python3
"""Derive every capability's lifecycle status, and refuse an uncalibrated threshold.

Two rules that were maintained by reading until this script existed.

**`foundation/0005` R17: a capability's status is derived from checkable facts** — whether the
distribution installs it, and whether it is documented as going away — "never from a label
maintained by hand". The distribution manifest carries the status, so a hand-written one would be a
label in the one place a consumer is told to trust. Both facts are computed here from the same
inputs the generator uses, and disagreeing with the generator is a failure.

This docstring claimed a third fact, "whether a fixture exercises it", and the code never read one:
the status comes from the generator's selection and from nothing else. R11 has always said a
fixture is "never a condition of shipping", and `fixtures/` no longer exists, so the claim is
removed rather than corrected into a check nothing would satisfy.

R14 fixes the vocabulary and what each value means for an installation: `proposed` ships nothing,
`active` is installed, `deprecated` is installed and going away, `retired` is absent. R15 requires the move through `deprecated` before `retired`, so a capability
that vanishes between two versions is a breaking change made silently — which the release record
in `docs/` would have to catch, and cannot if nothing lists what was installed before.

**`foundation/0007` R19: no numeric threshold ships uncalibrated.** R20 draws the line this check
enforces: a value the caller supplies per run is not a framework threshold, and a value the
framework *ships* needs the evidence that calibrated it. A shipped component naming a bare number
as a limit, a budget, or a retry count is the route R20 names — a value chosen once to get a first
run moving becoming a default nobody decided to ship.

Declared dependencies: none beyond the standard library, plus the generator's own selection logic.

Usage:  scripts/check_capabilities.py
Exit:   0 every status is derivable and no uncalibrated threshold ships, 1 otherwise, 2 cannot run
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cli import cannot_run
from generate_dist import DEFAULT_TARGET, MANIFEST_NAME, plan

REPO_ROOT = Path(__file__).resolve().parent.parent

# A bare number presented as a limit. Deliberately narrow: it looks for a *value*, not a mention,
# so prose describing why a caller supplies one does not trip it. `foundation/0007` R20's distinction
# is between a value the framework ships and one the caller supplies, and only the first is here.
THRESHOLD = re.compile(
    r"(?i)\b(timeout|limit|max[_ ]?\w*|min[_ ]?\w*|budget|retries|retry[_ ]?count|attempts?)\b"
    r"\s*(?:[:=]|is)\s*(\d[\d_]*)"
)

# Where a number is a framework fact rather than a threshold, with the reason. A hook's timeout is
# the case `foundation/0010` R11 requires to be stated rather than inherited, so it is a value the
# framework ships *by requirement* — and R11 is the evidence R19 asks for.
CALIBRATED = {
    "timeout": "foundation/0010 R11 requires a hook to state its own timeout rather than inherit 600",
    "max_reason": "foundation/0010 R13 caps a hook's output at 10,000 characters",
    "max_skill_body_lines": "ADR-0009 records the documented 500-line guidance made a hard limit",
}


def derived_statuses() -> dict[str, str]:
    """What the generator's own selection implies, keyed by capability name."""
    _files, capabilities, _skipped = plan()
    return {capability["name"]: capability["status"] for capability in capabilities}


def installed_statuses(root: Path) -> dict[str, str]:
    manifest = json.loads((root / MANIFEST_NAME).read_text())
    return {capability["name"]: capability["status"] for capability in manifest["capabilities"]}


def check_statuses(root: Path) -> list[str]:
    derived, installed = derived_statuses(), installed_statuses(root)
    problems: list[str] = []
    for name in sorted(set(derived) | set(installed)):
        if name not in installed:
            problems.append(f"{name}: derived as {derived[name]!r} and absent from the manifest")
        elif name not in derived:
            problems.append(
                f"{name}: recorded in the manifest and derivable from nothing — foundation/0006 R17 "
                f"forbids a status maintained by hand"
            )
        elif derived[name] != installed[name]:
            problems.append(
                f"{name}: the manifest says {installed[name]!r} and the facts derive "
                f"{derived[name]!r}"
            )
    for name, status in sorted(installed.items()):
        if status in ("proposed", "retired"):
            problems.append(
                f"{name}: status {status!r} must not appear in an installation — foundation/0006 R14, "
                f"proposed ships nothing and retired is absent from the distribution"
            )
    return problems


def check_thresholds(root: Path) -> list[str]:
    """foundation/0007 R19 and R20, over what the distribution actually ships."""
    problems: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        try:
            text = path.read_text()
        except (UnicodeDecodeError, OSError):
            continue
        for match in THRESHOLD.finditer(text):
            field = match.group(1).lower().replace(" ", "_")
            if field in CALIBRATED:
                continue
            line = text[: match.start()].count("\n") + 1
            problems.append(
                f"{path.relative_to(root).as_posix()}:{line}: ships {match.group(0)!r}. "
                f"foundation/0007 R19 admits a framework value only with the evidence that calibrated "
                f"it, and R20 makes a caller-supplied value the other route — neither is a bare "
                f"number in a shipped file"
            )
    return problems


def main() -> int:
    root = DEFAULT_TARGET
    if not (root / MANIFEST_NAME).is_file():
        cannot_run(f"cannot run: {root / MANIFEST_NAME} does not exist — run `make dist`")

    problems = check_statuses(root) + check_thresholds(root)
    installed = installed_statuses(root)
    print(
        f"capabilities checked: {len(installed)}  derived from the distribution"
    )
    if problems:
        print(f"FAILED: {len(problems)} problem(s)\n")
        for problem in problems:
            print(f"  {problem}")
        return 1
    print("every status is derived, and no uncalibrated threshold ships")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# --- lifecycle across releases -----------------------------------------------------------


LIFECYCLE_ORDER = {"proposed": 0, "active": 1, "deprecated": 2, "retired": 3}


def check_release_sequence(releases: list[dict]) -> list[str]:
    """Every reason a capability's observed history violates foundation/0006 R14 through R16.

    R15's clause is the one that needs a mechanism: a capability moves to `deprecated` before
    `retired`, and removing an installed one without that step is "a breaking change made
    silently". Silent is the operative word — nothing observes it unless something compares two
    releases, which is what this does.
    """
    problems: list[str] = []
    previous: dict | None = None
    for release in releases:
        status = release["status"]
        if status not in LIFECYCLE_ORDER:
            problems.append(f"{release['version']}: status {status!r} is outside foundation/0006 R14")
            continue
        if previous is not None:
            before, after = LIFECYCLE_ORDER[previous["status"]], LIFECYCLE_ORDER[status]
            if after < before:
                problems.append(
                    f"{release['version']}: moves from {previous['status']!r} back to {status!r}; "
                    f"the lifecycle of foundation/0006 R14 does not run backwards"
                )
            if previous["status"] == "active" and status == "retired":
                problems.append(
                    f"{release['version']}: retires a capability that was active in "
                    f"{previous['version']} without passing through 'deprecated' — foundation/0006 R15 "
                    f"calls that a breaking change made silently"
                )
        if status == "deprecated" and not release.get("replacement"):
            problems.append(
                f"{release['version']}: deprecated without naming a replacement or stating plainly "
                f"that none exists (foundation/0006 R15)"
            )
        if status == "retired" and not release.get("migration"):
            problems.append(
                f"{release['version']}: retired with no migration recorded — foundation/0006 R16 requires "
                f"the migration .claude/rules/compatibility.md demands"
            )
        previous = release
    return problems
