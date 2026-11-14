#!/usr/bin/env python3
"""Compose a goal's condition, and answer the state a goal ends on, from disk and git alone.

A goal is the harness's own mechanism: a condition the person sets once, repeated whenever the
session tries to stop, until a model reading the transcript judges it met. A condition written
as prose leaves that judgment to a reading — an order of steps, "follow the standards", a step
only a person may take — and a reading that cannot see the end re-prompts the session without
end. This script removes the reading: the condition names one command, and the command's first
line is the answer.

**`--state` answers one of three lines first** — «A goal's state is a script's answer, read from
disk and git alone: its first line is `state A`, `state B` or `not yet`, and every check it ran
follows with its output verbatim.» (SPEC-008 R1)

- `state A` — every task of the scope is delivered, proven — or delivered as the substrate alone,
  which owes no proof — and reviewed, and the run is measured
  and committed: the records (`deliver.py --outstanding`, restricted to the
  scope where one is named), no implementation record of the scope recording a criterion unmet
  that R12 does not answer,
  a review record naming each task whose records changed since the
  goal began and committed after them, `deliver.py --check`, `plan.py --check`, `spec.py`, a
  commit under the telemetry root after the last record and review, a tree holding only the
  changes the condition declared untouched, every commit since the goal began naming a skill and
  the slug, none of them on a remote, and the plugin at the version the goal began under.
- `state B` — the initiative's orchestration log, changed since the goal began, ends with a stop
  line — «State B holds when the initiative's orchestration log, changed since the goal began,
  ends with a stop line whose class is one of `blocking`, `silence`, `rebind`, `producers`,
  `gave-up`, `infrastructure`, `project-file`, `pending-change`, `specification`,
  `contradiction`, `budget`, `stands`, `analyse`, `outside-task`, `already-met`,
  `unclassified`, and the measure, commit and remote conditions of R2
  hold» (SPEC-008 R3) — what the tree still holds is listed as left for the person — or the
  plugin's version changed since the goal began, or a commit since then touched `siegard.json`
  or a standard it declares, which only the person authors — or the run took more judged doors
  than the condition's budget: «A run that took more judged doors since the goal began than the
  condition's budget is state B on its own» (SPEC-008 R3) — or a commit since then names no
  skill and the slug: «A commit since the goal began that names no skill and the slug, and is no
  reconciliation R2 admits, is state B on its own: the route never rewrites history, so that
  commit stands until a person reads it, and a goal waiting for it to disappear never ends.»
  (SPEC-008 R11) — or the scope holds everything state A asks but criteria recorded unmet: «A
  scope that holds every condition of R2 but one — an implementation record of it records a
  criterion unmet — is state B, each such criterion named beside its task: the record says the
  source does not satisfy the criterion, and state A would say the scope is delivered.»
  (SPEC-008 R12) — a criterion recorded unmet is answered where a review since the goal began
  gives it `covered` by a test in a file the task's own proof names: «The answer names each
  criterion so answered beside the test that answers it.» (SPEC-008 R12)
- `not yet` — neither; the checks that failed say what is left.

Whatever the state, the `criteria` check also names what the reviews left unproven: «The answer
names every criterion that a review committed since the goal began, naming a task of the scope,
left other than covered, beside that review; the list fails no check, because a criterion no
suite reaches is a reading for a person, not a state.» (SPEC-008 R13)

**`--compose` writes the condition, and refuses what the route would refuse first.** It checks
that the specification is sound, that nothing is pending under the specification, work, delivery
or target root, nor in the trace or `siegard-reconcile/` beside it — paths the route commits
(the first stop `/deliver-scope` raises), that the slug names no closed plan, and
that every scope id names an epic or a task of the live plan. It pins where `HEAD` stands, the
plugin's version and every change already pending outside those roots, and prints the condition:
the route, the authorization, the scope, and the `--state` invocation that answers it — «A goal
condition names the route, the authorization, the scope and the invocation that answers its
state, and states no rule: the rules are those of the plugin version the invocation pins.»
(SPEC-008 R6). An objective in prose is written to `goal-<stamp>-<slug>.md` under the telemetry
root, the one file this writes, and the condition names it by path and digest — one line the
person pastes whole, whatever the objective's length. It never sets a goal: the condition is the
person's once the person pastes it.

**`--arm` records the same condition as the framework's own goal, and `--disarm` ends it.** It
runs every check `--compose` runs and refuses where they refuse, refuses a project that already
holds an armed goal, and writes one record — `siegard/goal.json` under the repository's git
directory, never in the tree the state reads. The plugin's `Stop` hook then answers each stop of
the session from `--state`'s own computation over that record: «A goal the person arms through
the framework ends on the state script's answer at the session's stop, never on a model's
reading: `state A` or `state B` ends the goal and lets the session stop, `not yet` blocks the
stop with the checks that failed, and a fourth consecutive `not yet` whose whole answer repeats
the last ends the goal paused.» (SPEC-008 R14) Arming is the person's act: only `/siegard-goal`
runs this, where the person's invocation opens with `--arm` — the skill is closed to the model's
invocation, so its arguments are the person's own words, which no script can read. An `--objective-file` naming the file an earlier `--compose` wrote for the slug is
named as it stands rather than written again; `--objective-file -` reads the objective from stdin,
byte for byte, so a caller holding the text writes no file of its own.

Every root comes from `project.py`, run as a command, so `siegard.json` keeps its one reader. Every
check runs the framework's own command and quotes what it printed; nothing is re-derived here.

Declared dependencies: PyYAML, jsonschema (this script also imports deliver.py, plan.py and
spec.py, its siblings, and runs them and project.py as commands).

Usage:  goal.py --state <project-root> --slug <slug> --since <commit> --version <version> [--target <key>] [--scope <id>]... [--untouched <path>]... [--budget <n>]
                                    answer state A, state B or not yet, then every check
        goal.py --compose <project-root> --slug <slug> (--scope <id>... | --objective <text> | --objective-file <file|->) [--target <key>] [--budget <n>] [--correct contradicts] [--no-specify]
                                    check what the route would refuse first, then print the goal
                                    condition to paste after /goal
        goal.py --arm <project-root> (the arguments --compose takes)
                                    check as --compose does, then record the condition armed for
                                    the Stop hook to answer
        goal.py --disarm <project-root>
                                    end the armed goal, if one is
        goal.py --help              print this text and stop
        A scope id is epic/<name> or task/<epic>/<name> of the slug's live plan; with no --scope,
        the scope is the whole plan. --target may be left out where siegard.json declares one
        target. --untouched names a path `git status --porcelain` may list without the goal
        having failed it; --compose writes them from the tree as it stands. --budget is how many
        judged doors the run may take, each as the door decider returns it (none where left
        out); --compose pins it into the state command, and --state then counts the judged
        `decided:` lines the log gained since the goal began against it — a state command with
        no --budget counts nothing; --correct names the conformance findings the run answers by a corrective increment,
        and `contradicts` is the one kind a route corrects. An objective in prose
        asks /deliver-scope to run /analyse once over it before the plan unless --no-specify
        says otherwise; --specify says the default aloud, and either over a scope of epics or
        tasks is refused — «Under a goal whose
        condition asks to specify a prose objective, the orchestrating entry point invokes
        `/analyse` once, before the plan, over the objective as the person armed it»
        (SPEC-008 R10)
Exit:   0 state A or state B; a condition composed or armed; a goal disarmed, or none armed
        1 not yet; a composition or an arming refused, with every reason
        2 cannot run
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
import shlex
import subprocess
import sys
from pathlib import Path

BIN = Path(__file__).resolve().parent
sys.path.insert(0, str(BIN))

CANNOT_RUN = 2
PLUGIN_MANIFEST = BIN.parent / ".claude-plugin" / "plugin.json"
SKILLS = BIN.parent / "skills"
STOP_CLASSES = ("blocking", "silence", "rebind", "producers", "gave-up", "infrastructure",
                "project-file", "pending-change", "specification", "contradiction", "budget",
                "stands", "analyse", "outside-task", "already-met", "unclassified")
RECONCILED = ("siegard-trace.json", "siegard-reconcile/")
CORRECTABLE = ("contradicts",)
STOP_LINE = re.compile(r"^(?:- )?stop: (\S+) — (.+)$")
DERIVED = ("precondition unmet", "rule violated", "already done", "reading paid twice")
JUDGED = ("keeps the route", "serves the stated goal", "can be undone", "costs less")
CRITERIA = DERIVED + JUDGED
DOOR_LINE = re.compile(r"^(?P<verb>recommended|decided): (?P<door>.+?) — (?P<criterion>"
                       + "|".join(CRITERIA) + r") — (?P<fact>.+)$")
DOOR_VERBS = ("recommended:", "decided:")
TAKEN_JUDGED = re.compile(r"^(?:- )?`?decided: .+? — (?:" + "|".join(JUDGED) + r") — ")
CONDITION_LIMIT = 4000
ARMED_DIR = "siegard"
ARMED_FILE = "goal.json"
ENDED_FILE = "goals-ended.jsonl"
ARMED_CONTRACT = "goal-armed/1"
PAUSE_AFTER = 3
RECORDS_DONE = ("every task has a record, and every record its proof",
                "every task in the scope has a record, and every record its proof")


class Refused(Exception):
    pass


def command(args: list[str], cwd: Path | None = None) -> tuple[int, str]:
    done = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    return done.returncode, (done.stdout + done.stderr).rstrip("\n")


def script(name: str, *args: str) -> tuple[int, str]:
    return command([sys.executable, "-B", str(BIN / name), *args])


def git(root: Path, *args: str) -> str:
    code, out = command(["git", "-C", str(root), *args])
    if code != 0:
        raise Refused(f"git {' '.join(args)}: {out}")
    return out


def plugin_version() -> str:
    return json.loads(PLUGIN_MANIFEST.read_text(encoding="utf-8"))["version"]


def resolve(project_root: Path, target: str | None) -> dict:
    """The roots `project.py` prints, read from its own lines: `<field>: <path>` and
    `target <key>: <path>`."""
    code, out = script("project.py", str(project_root))
    if code != 0 or out.startswith("no project file"):
        raise Refused(f"project.py {project_root} did not resolve the project:\n{out}")
    fields: dict = {"targets": {}, "standards": []}
    for line in out.splitlines():
        found = re.match(r"^standard(?: \S+)?: (.+)$", line)
        if found and found.group(1) != "declared none":
            fields["standards"].append(Path(found.group(1)))
            continue
        found = re.match(r"^target (\S+): (.+)$", line)
        if found:
            fields["targets"][found.group(1)] = Path(found.group(2))
            continue
        found = re.match(r"^(specification_root|work_root|delivery_root|telemetry_root): (.+)$",
                         line)
        if found:
            fields[found.group(1)] = Path(found.group(2))
    missing = [name for name in ("specification_root", "work_root", "delivery_root",
                                 "telemetry_root") if name not in fields]
    if missing or not fields["targets"]:
        raise Refused(f"siegard.json declares no {', '.join(missing or ['targets'])}; "
                      f"/siegard-config declares it")
    if target is None:
        if len(fields["targets"]) != 1:
            raise Refused(f"siegard.json declares {len(fields['targets'])} targets; name one "
                          f"with --target ({', '.join(sorted(fields['targets']))})")
        target = next(iter(fields["targets"]))
    if target not in fields["targets"]:
        raise Refused(f"siegard.json declares no target {target}")
    fields["target"] = target
    code, top = command(["git", "-C", str(project_root), "rev-parse", "--show-toplevel"])
    if code != 0:
        raise Refused(f"{project_root} is not under git: {top}")
    fields["home"] = Path(top)
    return fields


def roots(fields: dict, slug: str) -> tuple[Path, Path, Path, Path]:
    return (fields["delivery_root"] / slug, fields["work_root"] / slug,
            fields["targets"][fields["target"]], fields["specification_root"])


def relative(fields: dict, path: Path) -> str:
    try:
        return path.resolve().relative_to(fields["home"].resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def scope_tasks(work: Path, specification: Path, scope: list[str]) -> tuple[list[str], list[str]]:
    """The tasks a goal carries: the scope's and what it depends on, or the whole plan."""
    import deliver
    closed = (work / "closure.md").is_file()
    nodes, problems = deliver.load_plan(work, None if closed else specification)
    if problems:
        raise Refused("the plan does not hold together:\n" + "\n".join(problems))
    if not scope:
        return sorted(tid for tid, node in nodes.items() if node["kind"] == "task"), []
    chosen, carried, refused = deliver.scope_of(nodes, scope)
    if refused:
        raise Refused("\n".join(refused))
    return chosen + carried, carried


def last_commit(fields: dict, since: str, *paths: Path) -> str | None:
    out = git(fields["home"], "log", "-1", "--format=%H", f"{since}..HEAD", "--",
              *[relative(fields, p) for p in paths])
    return out or None


def after(fields: dict, later: str, earlier: str) -> bool:
    code, _ = command(["git", "-C", str(fields["home"]), "merge-base", "--is-ancestor", earlier,
                       later])
    return code == 0


def reconciliation_only(fields: dict, commit: str, line: str) -> bool:
    """A `/reconcile` commit names its own record's slug, never the goal's, and touches the
    trace and that record alone — the route a delivery's drift is answered by."""
    named = re.match(r"^\S+ reconcile ([^\s:]+)(?=[:\s]|$)", line)
    if not named:
        return False
    record = RECONCILED[1] + named.group(1)
    paths = git(fields["home"], "show", "--name-only", "--format=", commit).splitlines()
    return bool(paths) and all(p in (RECONCILED[0], f"{record}.md")
                               or p.startswith(f"{record}.returns/") for p in paths)


def front_of(record: Path) -> dict:
    import spec
    text = record.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    front = spec.load_yaml(text.split("---", 2)[1])
    return front if isinstance(front, dict) else {}


def entries(front: dict, field: str) -> list[dict]:
    import spec
    return [e for e in spec.listed(front, field)
            if isinstance(e, dict) and isinstance(e.get("criterion"), str)]


def review_tasks(record: Path) -> list[str]:
    import spec
    return [t for t in spec.listed(front_of(record), "tasks") if isinstance(t, str)]


def answering_tests(fields: dict, since: str, delivery: Path, tid: str, criterion: str,
                    named: dict[Path, list[str]]) -> list[str]:
    """The tests, in files the task's own proof names, that a review committed since the goal
    began, naming the task, gives the criterion `covered` by: «A criterion recorded `met: false` is
    answered, and no longer one recorded unmet, where a review committed since the goal began names
    the criterion's task and gives the criterion `covered` by a test in a file the task's own proof
    record names» (SPEC-008 R12). A review and a proof quote one test by different names where it
    is parametrized, so the file is what they share."""
    proof = front_of(delivery / "proof" / f"{tid[len('task/'):]}.md")
    held = {t.get("file") for t in (proof.get("tests") or []) if isinstance(t, dict)}
    found: list[str] = []
    for path in sorted(named):
        if tid not in named[path] or last_commit(fields, since, path) is None:
            continue
        for entry in entries(front_of(path), "coverage"):
            if entry.get("criterion") != criterion or entry.get("state") != "covered":
                continue
            for test in entry.get("tests") or []:
                if isinstance(test, dict) and test.get("file") in held:
                    label = f"{test['file']}::{test.get('name')}"
                    if label not in found:
                        found.append(label)
    return found


def criteria_answer(fields: dict, since: str, delivery: Path, tasks: list[str],
                    named: dict[Path, list[str]]) -> tuple[bool, str]:
    """The criteria the scope's implementation records say are unmet and no review answers by a
    test of the task's own proof, which fail the check, those it names as answered, and the
    criteria this goal's reviews of the scope left other than covered, which it names and never
    fails on."""
    unmet, answered = [], []
    for tid in tasks:
        record = delivery / "implementation" / f"{tid[len('task/'):]}.md"
        if record.is_file():
            for e in entries(front_of(record), "criteria"):
                if e.get("met") is not False:
                    continue
                by = answering_tests(fields, since, delivery, tid, e["criterion"], named)
                if by:
                    answered += [f"  {tid}: {e['criterion']}", *[f"    answered by {b}" for b in by]]
                else:
                    unmet.append(f"  {tid}: {e['criterion']}")
    lines = ([f"{len(unmet)} criterion(s) recorded unmet:", *unmet] if unmet else
             ["no implementation record of the scope records a criterion unmet"])
    if answered:
        lines += [f"{len([a for a in answered if not a.startswith('    ')])} criterion(s) recorded "
                  f"unmet and answered by a test file of the task's own proof that a review "
                  f"gives covered:", *answered]
    scope = set(tasks)
    for path in sorted(named):
        if not scope & set(named[path]) or last_commit(fields, since, path) is None:
            continue
        left = [f"  {e.get('state')}: {e['criterion']}" for e in entries(front_of(path), "coverage")
                if e.get("state") != "covered"]
        if left:
            lines += [f"{relative(fields, path)} left {len(left)} criterion(s) other than "
                      f"covered:", *left]
    return not unmet, "\n".join(lines)


def log_line(raw: str) -> str:
    """An orchestration log's line as its form is read: past an opening `- ` and backticks."""
    line = raw.strip()
    if line.startswith("- "):
        line = line[2:].strip()
    return line.strip("`").strip()


GRANT_MARK = "(grant sha256 "


def judged_taken(fields: dict, since: str, log_file: Path, grant: str | None = None) -> int:
    """The judged doors the run took since the goal began: `decided:` lines whose criterion is a
    rung of the ladder, in the log as committed at HEAD and not in it at `since`. A line that ends
    `(grant sha256 <digest>)` was taken under a grant, which counts it and no goal does: «A
    `decided:` line a grant took ends `(grant sha256 <digest>)`; the grant's budget counts it and
    the goal's budget does not.» (SPEC-011 R10) Where `grant` names a digest, only the lines that
    carry it are counted."""
    at = relative(fields, log_file)
    now = git(fields["home"], "show", f"HEAD:{at}") if log_file.is_file() else ""
    before = subprocess.run(["git", "-C", str(fields["home"]), "show", f"{since}:{at}"],
                            capture_output=True, text=True).stdout
    earlier = [line.strip() for line in before.splitlines()]
    taken = 0
    for line in (line.strip() for line in now.splitlines()):
        if line in earlier:
            earlier.remove(line)
        elif TAKEN_JUDGED.match(line):
            granted = GRANT_MARK in line
            if grant is None and not granted:
                taken += 1
            elif grant is not None and f"{GRANT_MARK}{grant})" in line:
                taken += 1
    return taken


def checks(fields: dict, slug: str, since: str, version: str, scope: list[str],
           untouched: list[str],
           budget: int | None = None) -> tuple[dict[str, tuple[bool, str]], str | None]:
    delivery, work, target, specification = roots(fields, slug)
    closed = (work / "closure.md").is_file()
    found: dict[str, tuple[bool, str]] = {}

    running = plugin_version()
    found["version"] = (running == version,
                        f"the plugin runs {running}; the goal began under {version}")

    scoped = [arg for ref in scope for arg in ("--scope", ref)]
    code, out = script("deliver.py", "--outstanding", str(delivery), str(work), str(target),
                       *([] if closed else [str(specification)]), *scoped)
    found["records"] = (code == 0 and any(line in RECORDS_DONE for line in out.splitlines()), out)

    try:
        tasks, _ = scope_tasks(work, specification, scope)
        reviews = sorted((delivery / "review").glob("*.md"))
        named = {path: review_tasks(path) for path in reviews}
        unreviewed = []
        for tid in tasks:
            name = tid[len("task/"):]
            touched = last_commit(fields, since, delivery / "implementation" / f"{name}.md",
                                  delivery / "proof" / f"{name}.md")
            if touched is None:
                continue
            covering = [path for path, held in named.items() if tid in held
                        and (stamp := last_commit(fields, since, path)) is not None
                        and after(fields, stamp, touched)]
            if not covering:
                unreviewed.append(tid)
        found["review"] = (not unreviewed,
                           "every task whose records changed since the goal began is named by a "
                           "review committed after them" if not unreviewed else
                           "no review committed after the records names: " + ", ".join(unreviewed))
        found["criteria"] = criteria_answer(fields, since, delivery, tasks, named)
    except Refused as refusal:
        found["review"] = (False, str(refusal))
        found["criteria"] = (False, str(refusal))

    code, out = script("deliver.py", "--check", str(delivery), str(work), str(target),
                       *([] if closed else [str(specification)]))
    found["delivery"] = (code == 0, out)
    code, out = script("plan.py", "--check", str(work), *([] if closed else [str(specification)]))
    found["plan"] = (code == 0, out)
    code, out = script("spec.py", str(specification))
    found["specification"] = (code == 0 and "specification sound" in out, out)

    measured = last_commit(fields, since, fields["telemetry_root"])
    delivered = last_commit(fields, since, delivery / "implementation", delivery / "proof",
                            delivery / "review")
    found["measure"] = (measured is not None and (delivered is None
                                                  or after(fields, measured, delivered)),
                        f"last commit under the telemetry root: {measured or 'none'}; last "
                        f"commit of a record or a review: {delivered or 'none'}")

    status = git(fields["home"], "status", "--porcelain", "--untracked-files=all")
    pending = [line[3:] for line in status.splitlines() if line.strip()]
    stray = [path for path in pending if path not in untouched]
    found["tree"] = (not stray, status or "clean")

    log = git(fields["home"], "log", "--format=%H %s", f"{since}..HEAD")
    skills = {p.name for p in SKILLS.iterdir() if p.is_dir()}
    foreign = [line for line in log.splitlines()
               if not ((m := re.match(rf"^\S+ ([a-z-]+) {re.escape(slug)}(?=[:\s]|$)", line))
                       and m.group(1) in skills)
               and not reconciliation_only(fields, line.split()[0], line)]
    found["commits"] = (not foreign, "naming no skill and the slug:\n" + "\n".join(foreign)
                        if foreign else log or "no commit since the goal began")

    authored = [fields["home"] / "siegard.json", *fields["standards"]]
    touched = git(fields["home"], "log", "--format=%h %s", f"{since}..HEAD", "--",
                  *[relative(fields, path) for path in authored])
    found["authored"] = (not touched, touched or "no commit since the goal began touches "
                         "siegard.json or a standard it declares")

    shipped = [line.split()[0] for line in log.splitlines()
               if git(fields["home"], "branch", "-r", "--contains", line.split()[0])]
    found["remote"] = (not shipped, "on a remote: " + ", ".join(shipped) if shipped
                       else "no commit since the goal began is on a remote")

    log_file = delivery / "orchestration.md"
    if budget is not None:
        taken = judged_taken(fields, since, log_file)
        found["budget"] = (taken <= budget, f"{taken} judged door(s) taken since the goal began; "
                                            f"the condition's budget is {budget}")

    stop = None
    if log_file.is_file() and last_commit(fields, since, log_file):
        committed = git(fields["home"], "show", f"HEAD:{relative(fields, log_file)}")
        lines = [line for line in committed.splitlines() if line.strip()]
        matched = STOP_LINE.match(lines[-1]) if lines else None
        if matched and matched.group(1) in STOP_CLASSES:
            stop = lines[-1]
    return found, stop


def state(fields: dict, slug: str, since: str, version: str, scope: list[str],
          untouched: list[str], budget: int | None = None) -> tuple[str, list[str]]:
    found, stop = checks(fields, slug, since, version, scope, untouched, budget)
    common = ("measure", "commits", "remote")
    if not found["version"][0]:
        first = "state B — the plugin's version changed since the goal began"
    elif not found["authored"][0]:
        first = ("state B — a commit since the goal began touched siegard.json or a standard, "
                 "which only the person authors")
    elif not found["commits"][0]:
        first = ("state B — a commit since the goal began names no skill and the slug, which the "
                 "route never rewrites")
    elif "budget" in found and not found["budget"][0]:
        first = f"state B — {found['budget'][1]}, which the person did not grant"
    elif all(ok for ok, _ in found.values()):
        first = f"state A — {slug}: the scope is delivered, proven, reviewed and measured"
    elif stop and all(found[name][0] for name in common):
        first = f"state B — {stop.removeprefix('- ')}" + (
            "" if found["tree"][0] else "; the uncommitted files below are left for the person")
    elif all(ok for name, (ok, _) in found.items() if name != "criteria"):
        first = (f"state B — {slug}: the scope is delivered, reviewed and measured, and its "
                 f"records name criteria unmet")
    else:
        failed = [name for name, (ok, _) in found.items() if not ok]
        first = f"not yet — failing: {', '.join(failed)}" + (
            f"; the log ends with a stop line, and {', '.join(n for n in common if not found[n][0])} "
            f"must hold before it ends the goal" if stop else "")
    body = []
    for name, (ok, out) in found.items():
        body.append(f"check {name}: {'pass' if ok else 'FAIL'}")
        body += [f"  {line}" for line in out.splitlines()]
    return first, body


def compose(project_root: Path, fields: dict, slug: str, scope: list[str],
            objective: str | None, budget: int = 0,
            correct: list[str] | None = None,
            specify: bool = False,
            kept: Path | None = None) -> tuple[list[str], str | None, dict]:
    """The condition, and what it pins. `kept` is an objective file this script already wrote
    under the telemetry root for this slug: it is named as it stands rather than written again."""
    delivery, work, target, specification = roots(fields, slug)
    said: list[str] = []
    refused: list[str] = []

    if not specification.is_dir():
        refused.append(
            f"the specification root {relative(fields, specification)} does not exist yet — "
            "/deliver-scope's gate reads it before its first step. Where material states the "
            "domain, /analyse over that material writes it, and the root is committed before the "
            "goal; where the objective is all the material there is, the root created holding "
            "only a .gitkeep and committed passes the gate, and composing again over the objective "
            "runs /analyse over it before the plan, which a prose objective asks by default")
    else:
        code, out = script("spec.py", str(specification))
        if code == 0 and "specification sound" in out:
            said.append(f"specification: {out.splitlines()[-1]}")
        else:
            refused.append("the specification is not sound — /deliver-scope stops on it first, "
                           f"and spec.py names what to correct:\n{out}")

    pending = git(fields["home"], "status", "--porcelain", "--untracked-files=all", "--",
                  *[relative(fields, p) for p in (specification, work, delivery, target)])
    if pending:
        refused.append("changes are pending under the specification, work, delivery or target "
                       "root — /deliver-scope stops on a change it did not make; commit or "
                       f"discard them first:\n{pending}")
    import project
    top = project.toplevel_of(target) if target.is_dir() else fields["home"]
    reconciled = git(top, "status", "--porcelain", "--untracked-files=all", "--", *RECONCILED)
    if reconciled:
        refused.append("the trace or siegard-reconcile/ holds a change pending — every delivery "
                       "commits the trace and the review commits both, so /deliver-scope stops "
                       "on a change it did not make there too, and a goal leaving it untouched "
                       "could never reach state A; commit or discard it first:\n" + reconciled)

    if (work / "closure.md").is_file():
        refused.append(f"{relative(fields, work)} holds closure.md: a closed plan is history, and "
                       f"a new scope names a new slug")
    elif scope:
        if not (work / "plan.json").is_file():
            refused.append(f"{relative(fields, work)} holds no plan; a scope of epics or tasks "
                           f"names a live plan, and a new one is an objective")
        else:
            try:
                tasks, carried = scope_tasks(work, specification, scope)
                said.append(f"scope: {len(tasks) - len(carried)} task(s) named"
                            + (f", and {len(carried)} they depend on: {', '.join(carried)}"
                               if carried else ""))
            except Refused as refusal:
                refused.append(str(refusal))
    if refused:
        return refused, None, {}

    since = git(fields["home"], "rev-parse", "--short=12", "HEAD")
    branch = git(fields["home"], "branch", "--show-current") or "a detached HEAD"
    version = plugin_version()
    status = git(fields["home"], "status", "--porcelain", "--untracked-files=all")
    untouched = [line[3:] for line in status.splitlines() if line.strip()
                 and (kept is None or line[3:] != relative(fields, kept))]
    said += [f"HEAD: {since} on {branch}", f"plugin: {version}",
             f"untouched: {', '.join(untouched) if untouched else 'nothing'}"]

    invocation = ["python3", "-B", str(BIN / "goal.py"), "--state", str(project_root),
                  "--target", fields["target"], "--slug", slug,
                  *[arg for ref in scope for arg in ("--scope", ref)],
                  "--since", since, "--version", version, "--budget", str(budget),
                  *[arg for path in untouched for arg in ("--untouched", path)]]
    written = None
    digest = None
    if objective:
        # The objective travels by reference: a condition is one line the person pastes whole,
        # and an objective inlined in it is what an evaluator reads instead of the state command.
        if kept is not None:
            written = kept
            content = kept.read_bytes()
        else:
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            written = fields["telemetry_root"] / f"goal-{stamp}-{slug}.md"
            content = (objective.rstrip("\n") + "\n").encode("utf-8")
        digest = hashlib.sha256(content).hexdigest()[:16]
        said.append(f"objective: {relative(fields, written)} (sha256 {digest}), "
                    + ("named as it stands" if kept is not None else "written here verbatim")
                    + "; the measure commits it with the telemetry root")
    carried = (f"Scope: {', '.join(scope)}, with every task it depends on." if scope else
               f"Scope: the objective in {relative(fields, written)} (sha256 {digest}) — the "
               f"person's own words, verbatim — planned under this slug.")
    condition = " ".join(filter(None, [
        "Carry this scope end to end through /siegard:deliver-scope. This condition is the ask, "
        "in the person's words, for the whole route, and it authorizes for the whole goal — after "
        "every compaction too — the commits that skill defines.",
        f"Project: {project_root}. Target: {fields['target']}. Slug: {slug}. {carried}",
        "Specify: run /analyse once over the objective, before the plan, and commit the "
        "specification apart; I review it after the goal." if specify else None,
        f"Budget: {budget} judged door(s), each taken only as the door decider returns it."
        if budget else "Budget: no judged door; a choice a fact does not decide ends the run.",
        f"Findings: correct {', '.join(correct)} by a corrective increment, once; report the rest."
        if correct else "Findings: report them all; correct none.",
        "Leave untouched — never edit, commit or discard: "
        + (", ".join(untouched) if untouched else "nothing") + ".",
        "The goal ends when this command prints `state A` or `state B` as its first line; both "
        "end it, and in state B do not insist. Run it last and show its whole output:",
        " ".join(shlex.quote(part) for part in invocation),
    ]))
    if len(condition) > CONDITION_LIMIT:
        return [f"the condition is {len(condition)} characters, and the harness refuses one "
                f"over {CONDITION_LIMIT}; shorten the objective, or name its epic"], None, {}
    if written is not None and kept is None:
        written.parent.mkdir(parents=True, exist_ok=True)
        written.write_bytes(content)
    pinned = {"since": since, "version": version, "untouched": untouched, "budget": budget,
              "objective": relative(fields, written) if written is not None else None,
              "objective_sha256": digest}
    return said, condition, pinned


def armed_path(home: Path) -> Path:
    """Where a project's armed goal is recorded: inside the repository's git directory, shared by
    every worktree of it and never in the tree — the tree is what the state reads, and the
    measure commits the telemetry root whole."""
    common = Path(git(home, "rev-parse", "--git-common-dir"))
    return (common if common.is_absolute() else home / common) / ARMED_DIR / ARMED_FILE


def read_armed(path: Path) -> dict | None:
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return record if isinstance(record, dict) else None


def write_armed(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    held = path.with_suffix(".tmp")
    held.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    held.replace(path)


def end_armed(path: Path, record: dict, ended: str, reason: str) -> None:
    """The armed record leaves its place and is appended, ended, to the log beside it."""
    done = {**record, "ended": ended, "reason": reason,
            "ended_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    with (path.parent / ENDED_FILE).open("a", encoding="utf-8") as log:
        log.write(json.dumps(done) + "\n")
    path.unlink(missing_ok=True)


def arm(project_root: Path, fields: dict, slug: str, scope: list[str], objective: str | None,
        budget: int, correct: list[str], specify: bool,
        kept: Path | None) -> tuple[list[str], str | None]:
    """Compose the condition under every check `--compose` runs, and record it armed."""
    path = armed_path(fields["home"])
    if path.exists():
        held = read_armed(path) or {}
        return [f"a goal is armed already in this project — {held.get('slug', 'unreadable')}, "
                f"armed at {held.get('armed_at', 'unknown')}, recorded at {path}; a project "
                f"holds one armed goal, and `goal.py --disarm {project_root}` ends it"], None
    said, condition, pinned = compose(project_root, fields, slug, scope, objective, budget,
                                      correct, specify, kept)
    if condition is None:
        return said, None
    record = {"contract": ARMED_CONTRACT, "project_root": str(project_root), "slug": slug,
              "target": fields["target"], "scope": scope, **pinned, "condition": condition,
              "armed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
              "session_id": None, "blocks": 0, "last_state": None}
    write_armed(path, record)
    said.append(f"armed: {path}")
    return said, condition


def disarm(home: Path, reason: str) -> str:
    path = armed_path(home)
    if not path.exists():
        return "no goal is armed in this project"
    record = read_armed(path) or {}
    end_armed(path, record, "disarmed", reason)
    return f"disarmed: {record.get('slug', 'an unreadable record')}, armed at " \
           f"{record.get('armed_at', 'unknown')}"


def answer_stop(record: dict, path: Path) -> tuple[str, str]:
    """What a stop of the session the armed goal is bound to is answered with: `ended`,
    `paused` or `block`, and the text that says it. The state is `state()`'s own, over the
    record's pins; a `not yet` whose whole answer repeats the last one `PAUSE_AFTER` times in a
    row ends the goal paused, because the session answered each of those blocks with nothing a
    check could see."""
    project_root = Path(record["project_root"])
    fields = resolve(project_root, record["target"])
    budget = record.get("budget")
    first, body = state(fields, record["slug"], record["since"], record["version"],
                        list(record.get("scope") or []), list(record.get("untouched") or []),
                        budget if isinstance(budget, int) and not isinstance(budget, bool)
                        else None)
    if not first.startswith("not yet"):
        end_armed(path, record, first.split(" — ", 1)[0], first)
        return "ended", f"Siegard ended the armed goal {record['slug']}: {first}"
    digest = hashlib.sha256("\n".join([first, *body]).encode("utf-8")).hexdigest()[:16]
    blocks = int(record.get("blocks") or 0)
    if digest == record.get("last_state") and blocks >= PAUSE_AFTER:
        reason = (f"{blocks} consecutive stops were answered `not yet` with nothing a check "
                  f"could see changed; the last answer: {first}")
        end_armed(path, record, "paused", reason)
        return "paused", (f"Siegard paused the armed goal {record['slug']}: {reason}. It is "
                          f"disarmed; `/siegard:siegard-goal --arm` over the same scope arms it again")
    record = {**record, "blocks": blocks + 1 if digest == record.get("last_state") else 1,
              "last_state": digest}
    write_armed(path, record)
    failed, keep = [], False
    for line in body:
        if line.startswith("check "):
            keep = line.endswith(": FAIL")
        if keep:
            failed.append(line)
    return "block", "\n".join([first, *failed, "",
                               "The goal the person armed, repeated:", record["condition"]])


def take(args: list[str], flag: str, many: bool = False):
    values = []
    while flag in args:
        at = args.index(flag)
        if at + 1 >= len(args) or args[at + 1].startswith("--"):
            raise Refused(f"{flag} takes a value")
        values.append(args[at + 1])
        del args[at:at + 2]
        if not many:
            if flag in args:
                raise Refused(f"{flag} is named twice")
            break
    return values if many else (values[0] if values else None)


def main() -> int:
    args = sys.argv[1:]
    if "--help" in args:
        # The docstring is this script's one home of what it does and how it is called,
        # so `--help` prints that rather than a second copy of it that could drift.
        print(__doc__.strip())
        return 0
    modes = [m for m in ("--state", "--compose", "--arm", "--disarm") if m in args]
    if len(modes) != 1:
        print("cannot run: expected --state, --compose, --arm or --disarm, one of them",
              file=sys.stderr)
        return CANNOT_RUN
    mode = modes[0]
    args.remove(mode)
    if mode == "--disarm":
        if len(args) != 1 or args[0].startswith("--") or not Path(args[0]).is_dir():
            print("cannot run: --disarm takes <project-root> alone", file=sys.stderr)
            return CANNOT_RUN
        try:
            home = Path(git(Path(args[0]).resolve(), "rev-parse", "--show-toplevel"))
            print(disarm(home, "disarmed by goal.py --disarm"))
        except (Refused, OSError) as refusal:
            print(f"cannot run: {refusal}", file=sys.stderr)
            return CANNOT_RUN
        return 0
    try:
        slug = take(args, "--slug")
        target = take(args, "--target")
        scope = take(args, "--scope", many=True)
        since = take(args, "--since")
        version = take(args, "--version")
        untouched = take(args, "--untouched", many=True)
        objective = take(args, "--objective")
        objective_file = take(args, "--objective-file")
        budget_raw = take(args, "--budget")
        correct = take(args, "--correct", many=True)
        specify_said = "--specify" in args
        no_specify = "--no-specify" in args
        for flag in ("--specify", "--no-specify"):
            if flag in args:
                args.remove(flag)
    except Refused as refusal:
        print(f"cannot run: {refusal}", file=sys.stderr)
        return CANNOT_RUN
    if len(args) != 1 or args[0].startswith("--") or not slug:
        print("cannot run: expected <project-root> and --slug <slug>", file=sys.stderr)
        return CANNOT_RUN
    project_root = Path(args[0]).resolve()
    if not project_root.is_dir():
        print(f"cannot run: {project_root} is not a directory", file=sys.stderr)
        return CANNOT_RUN
    try:
        fields = resolve(project_root, target)
    except Refused as refusal:
        print(f"cannot run: {refusal}", file=sys.stderr)
        return CANNOT_RUN

    if mode == "--state":
        if not since or not version or objective or objective_file or correct or specify_said \
                or no_specify \
                or (budget_raw and not budget_raw.isdigit()):
            print("cannot run: --state takes --since and --version, a whole --budget where the "
                  "condition pinned one, and none of --objective or --correct, which are the "
                  "condition's", file=sys.stderr)
            return CANNOT_RUN
        try:
            first, body = state(fields, slug, since, version, scope, untouched,
                                int(budget_raw) if budget_raw else None)
        except Refused as refusal:
            print(f"cannot run: {refusal}", file=sys.stderr)
            return CANNOT_RUN
        print("\n".join([first, *body]))
        return 1 if first.startswith("not yet") else 0

    if objective_file is not None:
        if objective is not None:
            print("cannot run: --objective and --objective-file name one objective twice",
                  file=sys.stderr)
            return CANNOT_RUN
        try:
            objective = (sys.stdin.buffer.read().decode("utf-8") if objective_file == "-"
                         else Path(objective_file).read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError) as broken:
            print(f"cannot run: {broken}", file=sys.stderr)
            return CANNOT_RUN
        if not objective.strip():
            print(f"cannot run: {'stdin' if objective_file == '-' else objective_file} is empty",
                  file=sys.stderr)
            return CANNOT_RUN
    if not budget_raw or budget_raw.isdigit():
        budget = int(budget_raw or 0)
    else:
        print("cannot run: --budget takes a whole number of judged doors", file=sys.stderr)
        return CANNOT_RUN
    uncorrectable = sorted(set(correct) - set(CORRECTABLE))
    if uncorrectable:
        print(f"cannot run: --correct names {', '.join(uncorrectable)}; no route corrects it — "
              f"only {', '.join(CORRECTABLE)}, which the corrective increment answers",
              file=sys.stderr)
        return CANNOT_RUN
    if specify_said and no_specify:
        print("cannot run: --specify and --no-specify say opposite things", file=sys.stderr)
        return CANNOT_RUN
    if (specify_said or no_specify) and not objective:
        print(f"cannot run: {'--specify' if specify_said else '--no-specify'} speaks of /analyse "
              "over a prose objective, and a scope of epics or tasks is already planned",
              file=sys.stderr)
        return CANNOT_RUN
    specify = bool(objective) and not no_specify
    if since or version or untouched or bool(scope) == bool(objective):
        print("cannot run: --compose takes --scope or --objective, one of them, and pins "
              "--since, --version and --untouched itself", file=sys.stderr)
        return CANNOT_RUN
    kept = None
    if objective_file is not None:
        named = Path(objective_file).resolve()
        if named.parent == fields["telemetry_root"].resolve() \
                and re.fullmatch(rf"goal-\d{{8}}T\d{{6}}Z-{re.escape(slug)}\.md", named.name):
            kept = named
    try:
        if mode == "--arm":
            said, condition = arm(project_root, fields, slug, scope, objective, budget, correct,
                                  specify, kept)
        else:
            said, condition, _ = compose(project_root, fields, slug, scope, objective, budget,
                                         correct, specify, kept)
    except Refused as refusal:
        print(f"cannot run: {refusal}", file=sys.stderr)
        return CANNOT_RUN
    if condition is None:
        print("refused — " + ("nothing was armed:" if mode == "--arm" else
                              "the route would stop before its first step:"))
        print("\n".join(f"- {line}" for line in said))
        return 1
    print("checked:")
    print("\n".join(f"- {line}" for line in said))
    if mode == "--arm":
        print("\ngoal armed — the next stop of this session is answered by the state command, "
              "and the condition below is repeated with every `not yet`:\n")
    else:
        print("\ncondition — paste after /goal:\n")
    print(condition)
    return 0


if __name__ == "__main__":
    sys.exit(main())
