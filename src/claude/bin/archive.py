#!/usr/bin/env python3
"""Decide which closed initiatives may leave the working tree, and remove exactly those.

An initiative's plan and its delivery are evidence: once the plan is closed, nothing writes into
either again, and git history holds both. Archiving removes that evidence from the working tree so
it survives in git alone. Understanding never leaves — the specification with the decision logs
beside its nodes, `siegard-trace.json`, `siegard-reconcile/` and the source — because what those
justify outlives every plan and delivery root. This script touches nothing outside the pairs it
names.

**Every criterion is read from disk and git, in order, and the first that fails skips that
initiative.** A skipped initiative is reported with the criterion and the command's own words;
the others still proceed.

1. **Closed.** `closure.md` stands at `<work_root>/<slug>`. A live initiative is never eligible:
   closing is its own act, and archiving is not a way to end work.
2. **Committed.** `git status --porcelain --ignored` prints nothing over the pair. Removed means
   recoverable only where the history about to leave the tree is already in a commit; a file git
   ignores or does not track would leave with no copy anywhere.
3. **Valid history.** `plan.py --check` holds the closed plan to its index, and `deliver.py --check`
   holds the delivery to its index and records, once per target the records name. History that
   does not validate is reported while it is still in front of somebody, never archived. Where
   the problem is an index never derived or no longer current, the report names the derivation
   that answers it — a script's act, after which the pair is committed and checked again; any
   other problem belongs to the entry point that owns it, and nothing here repairs it.
4. **The pair, whole.** `<work_root>/<slug>` and `<delivery_root>/<slug>` leave together and
   entire, never one without the other and never in part: a delivery's records name the run
   directories beside them, and a plan kept live under a removed delivery would read every task
   as undelivered. Where the initiative has no delivery root on disk, the plan leaves alone and
   the report says so.

**The target is each delivery's own.** Every record names its target; `deliver.py --check` runs
against the source root `siegard.json` declares for each target the delivery's records name.
`--target` answers only a delivery whose records name none, in a project declaring more than one
target; with one target declared, that one answers.

**`--check` changes nothing. `--remove` reads every criterion again** — a listing printed earlier
is never trusted — removes the eligible pairs, and prints, ready to run and in this order, the
person's two git acts: a tag on the commit the removal starts from, and the removal's own commit,
pathspec-scoped to the pairs removed; then the line that brings any pair back, whether `HEAD` sits
on a remote branch, and what still answers from what remains: `spec.py` over the specification
root and the drift summary of `trace.py --check` over each target. This script runs no git command
that writes.

Declared dependencies: none beyond the standard library (this script runs project.py, plan.py,
deliver.py, spec.py and trace.py, its siblings, as commands, and reads door.py's resolution of
the project file).

Usage:  archive.py --check <project-root> (--all | <slug> [<slug> ...]) [--target <key>]
        archive.py --remove <project-root> (--all | <slug> [<slug> ...]) [--target <key>]
        archive.py --help    print this text and stop
Exit:   0 every initiative in scope is eligible (--check), or was removed (--remove)
        1 an initiative in scope was skipped, or the scope reached none
        2 cannot run
"""

from __future__ import annotations

import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import door

CANNOT_RUN = 2
CLOSURE = "closure.md"
RECORD_KINDS = ("implementation", "proof", "review")
TARGET_LINE = re.compile(r"^target:\s*['\"]?([^'\"\s]+)['\"]?\s*$", re.MULTILINE)
DERIVATION = re.compile(r"^STALE:", re.MULTILINE)
SHOWN = 4
WIDTH = 300


class CannotRun(Exception):
    pass


def take(args: list[str], flag: str) -> str | None:
    if flag not in args:
        return None
    at = args.index(flag)
    if at + 1 >= len(args) or args[at + 1].startswith("--"):
        raise CannotRun(f"{flag} needs a value")
    value = args[at + 1]
    del args[at:at + 2]
    if flag in args:
        raise CannotRun(f"{flag} is named twice")
    return value


def targets_named(delivery: Path) -> set[str]:
    """The target every record under this delivery names in its front matter."""
    named: set[str] = set()
    for kind in RECORD_KINDS:
        for record in sorted((delivery / kind).rglob("*.md")) if (delivery / kind).is_dir() else []:
            text = record.read_text(encoding="utf-8", errors="replace")
            if not text.startswith("---"):
                continue
            front = text.split("---", 2)[1] if text.count("---") >= 2 else ""
            named |= set(TARGET_LINE.findall(front))
    return named


def lines_of(text: str) -> str:
    kept = [line for line in text.splitlines() if line.strip()]
    shown = kept[:SHOWN]
    more = len(kept) - len(shown)
    shown = [line if len(line) <= WIDTH else line[:WIDTH] + " …" for line in shown]
    return "\n".join(f"      {line}" for line in shown) + (f"\n      … {more} more line(s)"
                                                           if more > 0 else "")


def files_in(path: Path) -> int:
    return sum(1 for p in path.rglob("*") if p.is_file()) if path.is_dir() else 0


def judge(slug: str, fields: dict, top: Path, chosen: str | None) -> dict:
    """One initiative against the four criteria, in order: eligible, or the first that failed."""
    work = fields["work_root"] / slug
    delivery = fields["delivery_root"] / slug
    pair = [p for p in (work, delivery) if p.exists()]
    verdict = {"slug": slug, "work": work, "delivery": delivery if delivery.exists() else None}
    if not work.is_dir():
        return dict(verdict, failed="1 closed", said=f"{work} does not exist")
    if not (work / CLOSURE).is_file():
        return dict(verdict, failed="1 closed", said=f"{work / CLOSURE} does not exist — the "
                    f"initiative is live, and closing it is /plan-work's act")
    code, pending = door.command(["git", "-C", str(top), "status", "--porcelain", "--ignored",
                                  "--", *map(str, pair)])
    if code != 0 or pending:
        return dict(verdict, failed="2 committed", said=pending or f"git status exits {code}")
    code, said = door.script("plan.py", "--check", str(work))
    if code != 0:
        door_line = (f"python3 -B {door.BIN / 'plan.py'} {work} — then commit what it wrote "
                     f"and check again" if DERIVATION.search(said) else None)
        return dict(verdict, failed="3 valid history: plan.py --check", said=said, door=door_line)
    if delivery.exists():
        roots = fields["targets"]
        named = targets_named(delivery)
        unknown = sorted(named - set(roots))
        if unknown:
            return dict(verdict, failed="3 valid history: targets", said=f"records name "
                        f"{', '.join(unknown)}, which siegard.json's `targets` does not declare")
        if not named:
            if chosen is not None:
                named = {chosen}
            elif len(roots) == 1:
                named = set(roots)
            else:
                return dict(verdict, failed="3 valid history: targets", said="no record names a "
                            "target and siegard.json declares " + ", ".join(sorted(roots)),
                            door="--target <key>, naming the one it delivered into")
        for key in sorted(named):
            code, said = door.script("deliver.py", "--check", str(delivery), str(work),
                                     str(roots[key]))
            if code != 0:
                door_line = (f"python3 -B {door.BIN / 'deliver.py'} {delivery} {work} "
                             f"{roots[key]} — then commit what it wrote and check again"
                             if DERIVATION.search(said) else None)
                return dict(verdict, failed=f"3 valid history: deliver.py --check against {key}",
                            said=said, door=door_line)
    return dict(verdict, failed=None)


def scope_of(fields: dict, slugs: list[str], every: bool) -> tuple[list[str], list[str]]:
    """The slugs in scope, and — under `--all` — the live ones left out of it."""
    if not every:
        return slugs, []
    work_root = fields["work_root"]
    held = sorted(p.name for p in work_root.iterdir() if p.is_dir()) if work_root.is_dir() else []
    return ([s for s in held if (work_root / s / CLOSURE).is_file()],
            [s for s in held if not (work_root / s / CLOSURE).is_file()])


def report(verdicts: list[dict], live: list[str]) -> None:
    for v in verdicts:
        if v["failed"] is None:
            sides = f"work {files_in(v['work'])} file(s)" + (
                f", delivery {files_in(v['delivery'])} file(s)" if v["delivery"]
                else ", no delivery root on disk — the plan leaves alone")
            print(f"eligible {v['slug']}: {sides}")
            continue
        print(f"skipped {v['slug']}: criterion {v['failed']}")
        print(lines_of(v["said"]))
        if v.get("door"):
            print(f"    answers it: {v['door']}")
        elif v["failed"].startswith("3"):
            print("    nothing here repairs it; the entry point that owns it does")
    if live:
        print(f"live, left as they are: {', '.join(live)}")
    eligible = sum(1 for v in verdicts if v["failed"] is None)
    print(f"{eligible} eligible, {len(verdicts) - eligible} skipped, of {len(verdicts)} in scope")


def remote_line(top: Path) -> str:
    _, remotes = door.command(["git", "-C", str(top), "remote"])
    if not remotes:
        return "this repository has no remote: the archive's only copy is this machine's git"
    _, held = door.command(["git", "-C", str(top), "branch", "-r", "--contains", "HEAD"])
    if not held:
        return "HEAD is on no remote branch: until it is pushed, this machine holds the only copy"
    return f"HEAD is on {', '.join(line.strip() for line in held.splitlines())}"


def remaining(fields: dict) -> None:
    spec_root = fields.get("specification_root")
    if spec_root is not None:
        code, said = door.script("spec.py", str(spec_root))
        print(f"spec.py {spec_root} (exit {code}):")
        print(lines_of(said))
    for key, root in sorted(fields["targets"].items()):
        if not root.is_dir():
            continue
        code, said = door.script("trace.py", "--check", str(root))
        lines = said.splitlines()
        head = next((i for i, line in enumerate(lines) if "drift finding" in line), None)
        summary = lines[head:head + 5] if head is not None else lines[-1:]
        print(f"trace.py --check {root} (exit {code}):")
        print("\n".join(f"      {line}" for line in summary))


def remove(verdicts: list[dict], fields: dict, top: Path) -> None:
    archived = [v for v in verdicts if v["failed"] is None]
    if not archived:
        return
    _, head = door.command(["git", "-C", str(top), "rev-parse", "HEAD"])
    for v in archived:
        for side in (v["work"], v["delivery"]):
            if side is not None:
                shutil.rmtree(side)
    paths = " ".join(str(p.relative_to(top)) for v in archived
                     for p in (v["work"], v["delivery"]) if p is not None)
    slugs = ", ".join(v["slug"] for v in archived)
    tag = f"archive/{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    print(f"removed from the tree: {slugs}")
    print("the person's git acts, in this order:")
    print(f"  git -C {top} tag -a {tag} -m \"last tree holding: {slugs}\" {head}")
    print(f"  git -C {top} add -A -- {paths} && git -C {top} commit -m \"siegard-archive: {slugs}\"")
    print(f"brings any of it back: git -C {top} checkout {tag} -- <path>  (from: {paths})")
    print(remote_line(top))
    remaining(fields)


def main() -> int:
    args = sys.argv[1:]
    if "--help" in args:
        print(__doc__.strip())
        return 0
    try:
        checking = take(args, "--check")
        removing = take(args, "--remove")
        chosen = take(args, "--target")
        every = "--all" in args
        if every:
            args.remove("--all")
        if (checking is None) == (removing is None):
            raise CannotRun("expected --check or --remove, followed by the project root")
        if every == bool(args):
            raise CannotRun("the scope is --all or the slugs, exactly one of the two"
                            + (f"; not understood: {' '.join(args)}" if every and args else ""))
        if any(a.startswith("--") for a in args):
            raise CannotRun(f"not understood: {' '.join(a for a in args if a.startswith('--'))}")
        project_root = Path(checking or removing).resolve()
        fields, unresolved, said = door.resolve(project_root)
        if unresolved:
            raise CannotRun(f"{unresolved}\n{said}")
        absent = [f for f in ("work_root", "delivery_root") if f not in fields]
        if absent or not fields["targets"]:
            raise CannotRun(f"siegard.json declares no {', '.join(absent or ['targets'])}; "
                            f"/siegard-config declares it")
        if chosen is not None and chosen not in fields["targets"]:
            raise CannotRun(f"--target {chosen}: siegard.json's `targets` declares "
                            f"{', '.join(sorted(fields['targets']))}")
        top = door.toplevel(fields["work_root"])
        if top is None:
            raise CannotRun(f"{fields['work_root']} is under no git repository: without git "
                            f"there is no archive, only deletion")
        slugs, live = scope_of(fields, args, every)
        verdicts = [judge(slug, fields, top, chosen) for slug in slugs]
    except CannotRun as refusal:
        print(f"cannot run: {refusal}", file=sys.stderr)
        return CANNOT_RUN
    report(verdicts, live)
    if removing is not None:
        remove(verdicts, fields, top)
    return 0 if verdicts and all(v["failed"] is None for v in verdicts) else 1


if __name__ == "__main__":
    sys.exit(main())
