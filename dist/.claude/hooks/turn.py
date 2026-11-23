"""The session's turn record, in a Siegard project: what the plugin's `PostToolUse` hook saw a
session do since its last allowed stop, read by the one `Stop` hook. «The turn record is what the
plugin's `PostToolUse` hook wrote since the session's last allowed stop, from the calls the
harness hands it and never from the transcript» (SPEC-008 R15).

One file per session under the repository's git directory, `siegard/turn/<session>.json`, never
in the tree a state reads. It holds the instant of the last `Skill` invocation of a skill whose run
ends on `bin/handoff.py --render` — the turn's `route` — and, under a live grant, the obligations
the grant's last answer left and the blocks already spent on them. Whether the turn
rendered is read at the stop from the records `--render` keeps, never from a command's output.

Every read of a missing or unreadable file is an empty record: a hook that failed on its own
state would hold the session on a reason the session cannot repair.
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

TURN_DIR = "turn"
KEPT_DIR = "handoff"
RENDERING = ("adopt-scope", "analyse", "deliver-scope", "implement-task", "plan-work",
             "reconcile", "review-change", "siegard-goal", "siegard-grant", "siegard-status")


def path(siegard_dir: Path, session: str) -> Path:
    return siegard_dir / TURN_DIR / f"{re.sub(r'[^A-Za-z0-9_-]', '_', session)}.json"


def read(siegard_dir: Path, session: str) -> dict:
    try:
        held = json.loads(path(siegard_dir, session).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        held = None
    if not isinstance(held, dict):
        held = {}
    route_at = held.get("route_at")
    return {"session_id": session,
            "route_at": route_at if isinstance(route_at, (int, float)) else None,
            "obligations": held.get("obligations") or [],
            "blocked": held.get("blocked") or []}


def write(siegard_dir: Path, state: dict) -> None:
    where = path(siegard_dir, state["session_id"])
    where.parent.mkdir(parents=True, exist_ok=True)
    where.write_text(json.dumps(state, indent=1) + "\n", encoding="utf-8")


def clear(siegard_dir: Path, session: str) -> None:
    path(siegard_dir, session).unlink(missing_ok=True)


def skill_of(given: dict) -> str:
    """A `Skill` call's skill, by its bare name: `siegard:plan-work` and `/plan-work` read alike."""
    return str(given.get("skill") or "").split(":")[-1].lstrip("/")


def after_skill(siegard_dir: Path, session: str, given: dict, now: float | None = None) -> None:
    """A `Skill` call to a skill whose run ends on a render marks the turn a route, at that
    instant; a call to any other skill leaves the record as it was."""
    if skill_of(given) not in RENDERING:
        return
    state = read(siegard_dir, session)
    state["route_at"] = time.time() if now is None else now
    write(siegard_dir, state)


def rendered(siegard_dir: Path, route_at: float | None) -> bool:
    """Whether a record `bin/handoff.py --render` keeps is newer than the turn's route: the render
    keeps one only where it printed, so a refused render reads as none."""
    if route_at is None:
        return False
    kept = siegard_dir / KEPT_DIR
    try:
        return any(record.stat().st_mtime >= route_at for record in kept.glob("*.json"))
    except OSError:
        return False
