#!/usr/bin/env python3
"""Refuse a write to a file the knowledge materializer owns.

One hook, one guarantee — `specs/0006` R7, so a denial names a single condition and this can be
retired without taking another guarantee with it. The guarantee is `specs/0003` R42 and R51: a
projection is derived and never hand-edited.

Until now that rule existed only as `project_knowledge.py --check` in a Makefile a consumer may
never run. Reporting a hand edit afterwards is a different thing from preventing it, and
`CLAUDE.md` **Security** requires a guarantee that must hold regardless of model judgment to be
enforced by a hook or a script rather than by a prompt.

What `specs/0010` fixes, and where each requirement lands:

- **R1** — a `command` handler. `prompt` and `agent` evaluate with a model, and a guarantee a
  model decides is not enforced.
- **R2** — denial is exit code 2. Any other non-zero code is a non-blocking error, so a hook that
  signalled failure by exiting 1 would permit exactly what it was written to prevent.
- **R3** — fails closed. Unparseable input, a payload missing what it needs, a path that will not
  resolve, an internal error: each denies with the reason on stderr. Nothing exits 0 on an
  unhandled condition.
- **R4** — no `updatedInput`. This rejects; it does not repair.
- **R8** — every field is untrusted, including the path. The path is resolved and confirmed to
  fall inside the tree this hook governs before it is judged.
- **R9** — preconditions are re-validated rather than trusted to the matcher, which can select
  this hook on input the filter was written to exclude.
- **R13** — the reason is capped rather than assumed short.
- **R14** — the denial reason is a factual statement, never an instruction. Instruction-shaped
  text is a prompt-injection surface and is liable to be filtered.
- **R16, R17** — this is a checkpoint, not a proof. A consumer may disable it, so
  `project_knowledge.py --check` holds the same guarantee in the consuming path. The hook makes
  the failure early and cheap rather than late and expensive.

Declared dependencies: none beyond the standard library. `derived_artifacts` ships in `bin/` at
the plugin root, which is the sibling directory this file resolves.

Input:  a PreToolUse payload on stdin.
Exit:   0 the write is not this hook's business, 2 denied with the reason on stderr.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

DENY = 2
ALLOW = 0

# R13 caps a hook's output. The reason below is far shorter, and the cap is applied rather than
# assumed so a later message cannot quietly exceed it.
MAX_REASON = 10_000

# The tools that can put bytes in a file. A tool absent from this set is not this hook's
# business, which is what keeps one hook to one guarantee.
WRITING_TOOLS = frozenset({"Write", "Edit", "MultiEdit", "NotebookEdit"})

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "bin"))

try:
    from derived_artifacts import DERIVED_NAMES, is_derived
except ImportError:
    print(
        "derived_artifacts is not resolvable beside this hook, so a derived file cannot be told "
        "from an authored one. The write is denied rather than judged on a guess.",
        file=sys.stderr,
    )
    raise SystemExit(DENY)


def target_path(payload: dict) -> str | None:
    """The path a writing tool is about to touch, or None if the payload names none."""
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return None
    for key in ("file_path", "notebook_path", "path"):
        value = tool_input.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def within(path: str, root: Path) -> Path | None:
    """Resolve `path` against `root`, or None if it escapes — R8.

    A relative path resolves against the tree this hook governs; an absolute one is accepted only
    if it already falls inside it. Anything else is outside this hook's business and undecidable
    here, which R3 makes a denial rather than a pass.
    """
    try:
        candidate = Path(path)
        resolved = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
    except (OSError, ValueError, RuntimeError):
        return None
    try:
        resolved.relative_to(root)
    except ValueError:
        return None
    return resolved


def decide(payload: dict, root: Path) -> tuple[int, str]:
    """Allow or deny, with the reason. Pure, so both directions are testable without a harness."""
    tool = payload.get("tool_name")
    if not isinstance(tool, str):
        return DENY, (
            "The payload names no tool, so what is about to happen cannot be determined. The "
            "action is denied because an undecidable case is not an allowed one."
        )
    # R9: the matcher is a filter, not a guarantee. A hook can be invoked on input its filter was
    # written to exclude, so the tool is checked here rather than trusted.
    if tool not in WRITING_TOOLS:
        return ALLOW, ""

    raw = target_path(payload)
    if raw is None:
        return DENY, (
            f"{tool} was called with no file path in its input, so the target cannot be checked "
            f"against the derived set. The action is denied because the check could not run."
        )

    resolved = within(raw, root)
    if resolved is None:
        return DENY, (
            f"The path in the {tool} input does not resolve inside the working tree this hook "
            f"governs, so it cannot be judged. The action is denied because the check could not "
            f"run. The field is tool_input.file_path."
        )

    relative = resolved.relative_to(root).as_posix()
    if not is_derived(relative):
        return ALLOW, ""

    return DENY, (
        f"{relative} is a derived projection. specs/0003 R42 and R51 make it the knowledge "
        f"materializer's output rather than an authored file, so an edit to it is discarded by "
        f"the next regeneration and is not a change to the knowledge it projects. The derived "
        f"names are {', '.join(sorted(DERIVED_NAMES))}, and the knowledge objects a projection "
        f"is derived from are the authored source."
    )


def main() -> int:
    try:
        raw = sys.stdin.read()
    except OSError:
        print("The hook input could not be read. The action is denied.", file=sys.stderr)
        return DENY

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        print(
            "The hook input is not valid JSON, so no write can be judged. The action is denied "
            "because an unreadable payload is not a permitted one.",
            file=sys.stderr,
        )
        return DENY
    if not isinstance(payload, dict):
        print(
            f"The hook input is a {type(payload).__name__} rather than an object, so no write can "
            f"be judged. The action is denied.",
            file=sys.stderr,
        )
        return DENY

    try:
        code, reason = decide(payload, Path.cwd().resolve())
    except Exception as exc:  # R3: an uncaught failure reads as permission.
        print(
            f"The hook failed while deciding: {type(exc).__name__}. The action is denied because "
            f"an internal error is not a permission.",
            file=sys.stderr,
        )
        return DENY

    if code != ALLOW:
        print(reason[:MAX_REASON], file=sys.stderr)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
