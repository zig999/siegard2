#!/usr/bin/env python3
"""Decide, from disk and git alone, whether a door's own entry point refuses its inputs.

A handoff that recommends a door, or hands one as open, makes a claim about the tree: that the
entry point behind the door runs over its inputs as they stand. A derived recommendation rests on
exactly that fact — «`precondition unmet`, the door's own entry point refuses its inputs as the
tree stands» (SPEC-006 R2) — and a door excluded on it is named excluded: «A door excluded on one
of the four grounds is said to be excluded, beside it and with its fact» (SPEC-006 R2). A session
that read the entry point's file partially guesses at that fact; this script reads it. Each door
is checked by the refusals its entry point's own file states before its first write, and every
refusal a script already decides is answered by running that script and quoting what it printed —
`project.py`, `spec.py`, `plan.py --check`, `deliver.py --check`, `deliver.py --outstanding`,
`deliver.py --standard`, `trace.py` — or by the one function that decides it, imported. Nothing
here is a second reading of what those decide.

**The first line is the answer**: `accepts` or `refuses`. Every line after it opens with one word
saying what it is:

- `refused: <fact>` — one per refusal, the fact by path or by the command that printed it, with
  that command's output beneath it, indented two spaces, verbatim;
- `checked: <what>` — a check that ran and passed, so a door said to be open carries the checks
  it was said open on;
- `decided: <what>` — an input the entry point decides itself where a set of one holds no choice
  (the one target, the one live initiative, the one deliverable task), as its file states;
- `not decided: <what the entry point's file says>` — a refusal the entry point's file states and
  no script on disk decides: a person's words, a mode only the person names, a reading. It is
  never guessed here, and `accepts` never answers for it.

**The doors checked are the five a handoff hands**, each over what its file states before any
write:

- `implement-task` — the project file's roots; the plan's `closure.md`; `plan.py --check`; the
  tree under the delivery root, the target source root, the task's file and the trace; `deliver.py
  --outstanding`, and in it the task's own line — not in the plan, waiting on a dependency or a
  re-bind, a standing BLOCKING note — or, where no task is named, the deliverable set holding
  exactly one; and the standard for the target, held by `deliver.py --standard` with `--against`
  unless the task declares `produces`.
- `plan-work` — the roots; `closure.md`; `spec.py`; the tree under the work and specification
  roots; the standard for the target, held by `deliver.py --standard`.
- `review-change` — the roots; `plan.py --check`; `deliver.py --check`; the tree under the
  delivery root and the trace; each named task holding an implementation record, or the delivery holding at
  least one where none is named; the review's name free under `review/`, `run/` and
  `siegard-reconcile/`; the standard for the target, held by `deliver.py --standard`.
- `deliver-scope` — the roots, the telemetry root among them; the specification root existing
  and `spec.py` sound; the tree under the specification, work, delivery and target roots, and the
  trace and `siegard-reconcile/` at the target's toplevel; `closure.md`; each scope id an epic or
  a task of the live plan, read through `goal.scope_tasks`; the standard for the target declared.
- `reconcile` — the roots; `spec.py`; the target under git; `trace.py` over the target holding a
  trace file; the record's path `siegard-reconcile/<slug>.md` free; the named files, the
  specification root and the trace committed.

**One act is checked beside the doors: `commit`**, the commit a session is about to make of an
initiative's delivery. «A run whose orchestration log closes on a stop line commits nothing after
it but the measure: the telemetry root, and the log that carries the stop line.» (SPEC-008 R18)
The log is read as it stands on disk — its last line that is not blank, matched against the stop
line `goal.py` reads a goal's state from — and a commit is held to that by the paths it names with
`--file`, spelled from the project root; with none named, the commit is read as one of the
delivery, which a stop line refuses. The runs are read as `deliver.py` reads them, `run.json`
under `run/` at the initiative's delivery root: «A captured run that ended other than `passed`,
that git does not hold, and that no record under the initiative's delivery root names, is refused
to a commit that reaches that delivery root» (SPEC-008 R18) — a red attempt a record names beside
its retry is the delivery's own evidence, and one no record names is a red nothing answered.
Whether the person's words authorize the commit at all is no file's answer: it is listed as not
decided, and `ask.py --read` prints the ask recorded verbatim.

Every root comes from `project.py`, run as a command, so `siegard.json` keeps its one reader.

Declared dependencies: PyYAML, jsonschema (this script imports goal.py, deliver.py and plan.py,
its siblings, and runs them and project.py, spec.py and trace.py as commands).

Usage:  door.py --check <skill> [--project <dir>] [--target <key>] [--slug <slug>] [--task <id>]... [--name <review-name>] [--scope <id>]... [--file <path>]... [--standard <file>]
                                    decide whether <skill>'s entry point refuses these inputs as
                                    the tree stands: implement-task, plan-work, review-change,
                                    deliver-scope or reconcile. --project defaults to the working
                                    directory. --slug is required by plan-work, deliver-scope and
                                    reconcile, whose slug no tree decides; implement-task and
                                    review-change infer the one live initiative. --task names the
                                    task (implement-task, one) or the tasks under review
                                    (review-change, any). --name is the review's name, the slug
                                    where left out. --scope is deliver-scope's reach. --file is
                                    reconcile's file set, spelled from the target source root, and
                                    at least one is required. --standard names the registry where
                                    the invocation would, and wins over siegard.json as it does
                                    there
        door.py --check commit [--project <dir>] [--slug <slug>] [--file <path>]...
                                    decide whether a commit of the slug's delivery is refused as
                                    the tree stands: a log closing on a stop line, or a red run no
                                    record names. --slug is inferred where one initiative is live.
                                    --file is the commit's pathspec, spelled from the project root
        door.py --help              print this text and stop
Exit:   0 accepts
        1 refuses, with every refusal
        2 cannot run
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

BIN = Path(__file__).resolve().parent
sys.path.insert(0, str(BIN))

CANNOT_RUN = 2
DOORS = ("implement-task", "plan-work", "review-change", "deliver-scope", "reconcile", "commit")
ROOTS = {
    "implement-task": ("specification_root", "work_root", "delivery_root"),
    "plan-work": ("specification_root", "work_root"),
    "review-change": ("specification_root", "work_root", "delivery_root"),
    "deliver-scope": ("specification_root", "work_root", "delivery_root", "telemetry_root"),
    "reconcile": ("specification_root",),
    "commit": ("work_root", "delivery_root", "telemetry_root"),
}
STANDARD_HELD = ("implement-task", "plan-work", "review-change", "deliver-scope")
NAMED_SLUG = ("plan-work", "deliver-scope", "reconcile")
CLOSURE_FILE = "closure.md"
TRACE_FILE = "siegard-trace.json"
RECONCILE_DIR = "siegard-reconcile"
LOG_FILE = "orchestration.md"
RUN_DIR = "run"
RECORD_DIRS = ("implementation", "proof", "review")

NOT_DECIDED = {
    "implement-task": [
        "a request naming several tasks is a stop — the request's words, which no file holds",
        "a proof-only re-delivery, or a task carrying `stands`: a binding of a node the task "
        "implements out of date on a file the mode names is a stop, read by `trace.py --check "
        "--all`; another node's is not",
    ],
    "plan-work": [
        "the scope — what the person wants developed, in prose — is a required input no file holds",
        "a corrective, decided-fact or proof increment each takes inputs only the person names: "
        "the file the wrong behavior lives in, the fact a delivery stopped over, the facts to prove",
    ],
    "review-change": [
        "the file set is the person's or the delivering invocation's, and `deliver.py --review` "
        "holds it to the records only once the review's record is written",
    ],
    "deliver-scope": [
        "the ask — the person's own words stating that the scope is carried end to end — is a "
        "required input no file holds",
        "under a goal naming its objective by a file and a digest, a digest that no longer "
        "matches is a stop, read against the condition the person armed",
    ],
    "reconcile": [
        "certifications and a rewrite are the person's statements; each proof a certification "
        "names must be committed too",
        "adoption is a mode the person names, and begins without a trace file",
    ],
    "commit": [
        "whether the person's own words in this session authorize this commit — `ask.py --read` "
        "prints the ask recorded verbatim, and what its words cover is the session rules' reading",
        "that the pathspec holds only what the invoked skill wrote — the skill's own report names "
        "what it wrote",
    ],
}


class CannotRun(Exception):
    pass


class Answer:
    def __init__(self) -> None:
        self.refused: list[tuple[str, str]] = []
        self.checked: list[str] = []
        self.decided: list[str] = []

    def refuse(self, fact: str, output: str = "") -> None:
        self.refused.append((fact, output))

    def lines(self, door: str) -> list[str]:
        out = ["refuses" if self.refused else "accepts"]
        for fact, output in self.refused:
            out.append(f"refused: {fact}")
            out += [f"  {line}" for line in output.splitlines()]
        out += [f"decided: {line}" for line in self.decided]
        out += [f"checked: {line}" for line in self.checked]
        out += [f"not decided: {line}" for line in NOT_DECIDED[door]]
        return out


def command(args: list[str]) -> tuple[int, str]:
    done = subprocess.run(args, capture_output=True, text=True)
    return done.returncode, (done.stdout + done.stderr).rstrip("\n")


def script(name: str, *args: str) -> tuple[int, str]:
    return command([sys.executable, "-B", str(BIN / name), *args])


def toplevel(path: Path) -> Path | None:
    """The git toplevel holding `path`, or None where git does not hold it. A root that does not
    exist yet is asked through the nearest directory that does."""
    probe = path
    while not probe.is_dir() and probe != probe.parent:
        probe = probe.parent
    code, out = command(["git", "-C", str(probe), "rev-parse", "--show-toplevel"])
    return Path(out) if code == 0 and out else None


def resolve(project_root: Path) -> tuple[dict, str | None, str]:
    """The roots `project.py` prints, read from its own lines, with each target's standard line
    kept by target; or the reason it resolved nothing, and what it printed."""
    code, out = script("project.py", str(project_root))
    if code != 0:
        return {}, f"project.py {project_root} exits {code}: siegard.json does not hold together", out
    if out.startswith("no project file") or "\nno project file" in out:
        return {}, "no siegard.json declares this project — /siegard-config declares it", out
    fields: dict = {"targets": {}, "standards": {}}
    for line in out.splitlines():
        found = re.match(r"^standard(?: (\S+))?: (.+)$", line)
        if found:
            fields["standards"][found.group(1)] = (None if found.group(2) == "declared none"
                                                   else Path(found.group(2)))
            continue
        found = re.match(r"^target (\S+): (.+)$", line)
        if found:
            fields["targets"][found.group(1)] = Path(found.group(2))
            continue
        found = re.match(r"^(specification_root|work_root|delivery_root|telemetry_root): (.+)$",
                         line)
        if found:
            fields[found.group(1)] = Path(found.group(2))
    return fields, None, out


def pending(paths: list[Path]) -> str:
    """What `git status --porcelain` prints over these paths, each asked of the repository that
    holds it."""
    out = []
    for path in paths:
        top = toplevel(path)
        if top is None:
            continue
        code, said = command(["git", "-C", str(top), "status", "--porcelain", "--", str(path)])
        if said:
            out.append(said)
    return "\n".join(out)


def live_initiatives(work_root: Path) -> list[str]:
    if not work_root.is_dir():
        return []
    return sorted(p.name for p in work_root.iterdir()
                  if p.is_dir() and not (p / CLOSURE_FILE).is_file())


def standard_of(fields: dict, target: str, named: str | None, answer: Answer) -> Path | None:
    """The registry for the target as the entry point resolves it: a naming wins, then the
    target's line; no line at all joins the entry point's stop of absent inputs."""
    if named:
        return Path(named).resolve()
    held = fields["standards"]
    key = target if target in held else None if len(fields["targets"]) == 1 else target
    if key in held:
        if held[key] is None:
            answer.checked.append(f"standard for target {target}: null in siegard.json — none, "
                                  f"deliberately")
        return held[key]
    answer.refuse(f"siegard.json declares no standard for target {target}, and none is named — "
                  f"the entry point stops on the absent input; /siegard-config declares it, or "
                  f"null for none")
    return None


def hold_standard(registry: Path, *extra: str, answer: Answer) -> None:
    code, out = script("deliver.py", "--standard", str(registry), *extra)
    shown = " ".join(["deliver.py --standard", str(registry), *extra])
    if code != 0:
        answer.refuse(f"{shown} exits {code}", out)
    else:
        answer.checked.append(f"{shown} — exit 0")


def check_tree(paths: list[Path], answer: Answer) -> None:
    said = pending(paths)
    shown = " ".join(str(p) for p in paths)
    if said:
        answer.refuse(f"git status --porcelain -- {shown} is not empty — the entry point writes "
                      f"there, and stops on a change it did not make", said)
    else:
        answer.checked.append(f"git status --porcelain -- {shown} — clean")


def run_check(answer: Answer, shown: str, code: int, out: str, sound: bool | None = None) -> bool:
    ok = code == 0 if sound is None else sound
    if ok:
        answer.checked.append(f"{shown} — exit {code}")
    else:
        answer.refuse(f"{shown} exits {code}", out)
    return ok


def check_specification(specification: Path, answer: Answer) -> None:
    if not specification.is_dir():
        answer.refuse(f"the specification root {specification} does not exist")
        return
    code, out = script("spec.py", str(specification))
    run_check(answer, f"spec.py {specification}", code, out,
              sound=code == 0 and "specification sound" in out)


def outstanding_lines(out: str, task: str) -> list[str]:
    """The task's own line of `deliver.py --outstanding`, with the entries indented beneath it."""
    lines = out.splitlines()
    for at, line in enumerate(lines):
        if line.startswith(f"{task}: "):
            held = [line]
            for later in lines[at + 1:]:
                if not later.startswith("  "):
                    break
                held.append(later.strip())
            return held
    return []


def deliverable(out: str) -> list[str]:
    for line in out.splitlines():
        if line.startswith("deliverable now: "):
            named = line[len("deliverable now: "):].split(" — ", 1)[0]
            return [] if named == "none" else [t.strip() for t in named.split(",")]
    return []


def door_implement_task(fields: dict, target: str, slug: str, args: dict, answer: Answer) -> None:
    import plan
    import spec
    work = fields["work_root"] / slug
    delivery = fields["delivery_root"] / slug
    source = fields["targets"][target]
    specification = fields["specification_root"]
    if (work / CLOSURE_FILE).is_file():
        answer.refuse(f"{work / CLOSURE_FILE} exists — the plan is history, and writing new source "
                      f"against it is a stop")
        return
    if not (work / "plan.json").is_file():
        answer.refuse(f"{work} holds no plan.json — the task must already be planned; /plan-work "
                      f"plans it")
        return
    code, out = script("plan.py", "--check", str(work), str(specification))
    run_check(answer, f"plan.py --check {work} {specification}", code, out)

    tasks = args["task"]
    if len(tasks) > 1:
        answer.refuse(f"{len(tasks)} tasks named ({', '.join(tasks)}) — one invocation delivers "
                      f"one task")
        return
    if source.is_dir() and toplevel(source) is None:
        answer.refuse(f"the target source root {source} is not under git")

    # An absent delivery root is created empty by the entry point, and --outstanding over an
    # empty one answers the same: every task without a record.
    with tempfile.TemporaryDirectory() as empty:
        over = delivery if delivery.is_dir() else Path(empty)
        code, out = script("deliver.py", "--outstanding", str(over), str(work), str(source),
                           str(specification))
    shown = f"deliver.py --outstanding {delivery} {work} {source} {specification}"
    ran = run_check(answer, shown, code, out)
    if tasks:
        task = tasks[0]
    elif not ran:
        task = None
    else:
        ready = deliverable(out)
        if len(ready) == 1:
            task = ready[0]
            answer.decided.append(f"task {task} — the one task deliverable now")
        else:
            answer.refuse("no task named, and the deliverable set does not hold exactly one — "
                          "name the task", "\n".join(line for line in out.splitlines()
                                                     if line.startswith("deliverable now: ")))
            task = None

    paths = [delivery, source]
    top = toplevel(source) if source.is_dir() else None
    if top is not None:
        paths.append(Path(top) / TRACE_FILE)
    if task:
        task_file = work / f"{task}.md"
        if not task_file.is_file():
            answer.refuse(f"{task} is not in the plan: {task_file} does not exist — /plan-work "
                          f"plans it into the plan")
            task = None
        else:
            paths.append(task_file)
    check_tree(paths, answer)

    produces = False
    if task:
        record = delivery / "implementation" / f"{task.removeprefix('task/')}.md"
        if record.is_file():
            answer.decided.append(f"{record} exists — a re-delivery, which is no stop; its runs "
                                  f"take the next free -N suffix under run/")
        held = outstanding_lines(out, task)
        if held:
            line = held[0]
            if "waits on " in line:
                answer.refuse(f"deliver.py --outstanding: {task} waits — the entry point stops on "
                              f"what it waits on", "\n".join(held))
            if "standing BLOCKING note" in line:
                answer.refuse(f"deliver.py --outstanding: {task} carries a standing BLOCKING note "
                              f"— only a person settles it", "\n".join(held))
        front, body, _ = spec.parse_node(work / f"{task}.md")
        if isinstance(front, dict):
            produces = bool(spec.listed(front, "produces"))
            # A task already delivered is absent from --outstanding, and a re-delivery over it
            # stops on the same note, read here from the task's own file.
            blocking = plan.blocking_notes_of(plan.notes_of(body))
            if not held and blocking:
                answer.refuse(f"{work / f'{task}.md'} carries a standing BLOCKING note — only a "
                              f"person settles it", "\n".join(blocking))

    registry = standard_of(fields, target, args["standard"], answer)
    if registry is not None:
        extra = ([] if produces else ["--against", str(source)]) + [
            "--specification", str(specification)]
        hold_standard(registry, *extra, answer=answer)


def door_plan_work(fields: dict, target: str, slug: str, args: dict, answer: Answer) -> None:
    work = fields["work_root"] / slug
    specification = fields["specification_root"]
    if (work / CLOSURE_FILE).is_file():
        answer.refuse(f"{work / CLOSURE_FILE} exists — planning over a closed plan is a stop; a "
                      f"new initiative names a new slug")
    check_specification(specification, answer)
    if toplevel(work) is None:
        answer.refuse(f"the work root {work} is not under git")
    check_tree([work, specification], answer)
    registry = standard_of(fields, target, args["standard"], answer)
    if registry is not None:
        hold_standard(registry, answer=answer)


def door_review_change(fields: dict, target: str, slug: str, args: dict, answer: Answer) -> None:
    work = fields["work_root"] / slug
    delivery = fields["delivery_root"] / slug
    source = fields["targets"][target]
    specification = fields["specification_root"]
    live = [] if (work / CLOSURE_FILE).is_file() else [str(specification)]
    code, out = script("plan.py", "--check", str(work), *live)
    run_check(answer, " ".join(["plan.py --check", str(work), *live]), code, out)
    code, out = script("deliver.py", "--check", str(delivery), str(work), str(source), *live)
    run_check(answer, " ".join(["deliver.py --check", str(delivery), str(work), str(source),
                                *live]), code, out)
    top = toplevel(source) if source.is_dir() else None
    check_tree([delivery, *([Path(top) / TRACE_FILE] if top is not None else [])], answer)

    records = sorted(p.relative_to(delivery / "implementation").with_suffix("").as_posix()
                     for p in (delivery / "implementation").rglob("*.md")) \
        if (delivery / "implementation").is_dir() else []
    if args["task"]:
        for task in args["task"]:
            record = delivery / "implementation" / f"{task.removeprefix('task/')}.md"
            if not record.is_file():
                answer.refuse(f"{task} holds no implementation record: {record} does not exist — "
                              f"a review of a task nothing delivered has no subject")
    elif not records:
        answer.refuse(f"{delivery / 'implementation'} holds no record — nothing is delivered, so "
                      f"a review has no subject")
    else:
        answer.checked.append(f"{len(records)} implementation record(s) under "
                              f"{delivery / 'implementation'}")

    name = args["name"] or slug
    home = toplevel(source) or source
    taken = [path for path in (delivery / "review" / f"{name}.md", delivery / "run" / name,
                               home / RECONCILE_DIR / f"{name}.md") if path.exists()]
    if taken:
        answer.refuse(f"the review's name {name} is taken: {', '.join(str(p) for p in taken)} — "
                      f"a second review names itself")
    else:
        answer.checked.append(f"the review's name {name} is free under review/, run/ and "
                              f"{RECONCILE_DIR}/")
    registry = standard_of(fields, target, args["standard"], answer)
    if registry is not None:
        hold_standard(registry, answer=answer)


def door_deliver_scope(fields: dict, target: str, slug: str, args: dict, answer: Answer) -> None:
    import goal
    work = fields["work_root"] / slug
    delivery = fields["delivery_root"] / slug
    source = fields["targets"][target]
    specification = fields["specification_root"]
    check_specification(specification, answer)
    check_tree([specification, work, delivery, source], answer)
    home = toplevel(source) if source.is_dir() else None
    if home is not None:
        check_tree([home / goal.RECONCILED[0], home / goal.RECONCILED[1]], answer)
    if (work / CLOSURE_FILE).is_file():
        answer.refuse(f"{work / CLOSURE_FILE} exists — a closed plan is history, and a new scope "
                      f"names a new slug")
    elif args["scope"]:
        if not (work / "plan.json").is_file():
            answer.refuse(f"{work} holds no plan — a reach of epics or tasks names a live plan, and "
                          f"a new plan is planned from prose")
        else:
            try:
                tasks, carried = goal.scope_tasks(work, specification, args["scope"])
                answer.checked.append(f"scope: {len(tasks) - len(carried)} task(s) named, "
                                      f"{len(carried)} carried")
            except goal.Refused as refusal:
                answer.refuse("the scope does not name the live plan", str(refusal))
    elif (work / "plan.json").is_file():
        answer.decided.append(f"{work} holds a live plan — a resume from the deliverable set")
    standard_of(fields, target, args["standard"], answer)


def door_reconcile(fields: dict, target: str, slug: str, args: dict, answer: Answer) -> None:
    source = fields["targets"][target]
    specification = fields["specification_root"]
    check_specification(specification, answer)
    home = toplevel(source) if source.is_dir() else None
    if home is None:
        answer.refuse(f"the target source root {source} is not under git")
        return
    code, out = script("trace.py", str(source))
    if code != 0 or out.startswith("no trace file"):
        answer.refuse(f"trace.py {source} exits {code}" + (
            " — nothing has been bound in this target; a delivery, or an adoption, is the route"
            if out.startswith("no trace file") else ""), out)
    else:
        answer.checked.append(f"trace.py {source} — exit 0")
    record = home / RECONCILE_DIR / f"{slug}.md"
    if record.exists():
        answer.refuse(f"{record} exists — the slug is taken, and the record it would overwrite is "
                      f"the justification for a binding still in the trace")
    else:
        answer.checked.append(f"{record} is free")
    check_tree([*(source / path for path in args["file"]), specification, home / TRACE_FILE],
               answer)


def named_by_a_record(delivery: Path, name: str) -> bool:
    """Whether a record under the initiative's delivery root — an implementation, a proof or a
    review — names the run, by its directory or by its `run/` path alike, as a proof's notes name
    a red attempt. The orchestration log is a marker, never a record, and is not read."""
    pattern = re.compile(rf"(?<![\w-]){re.escape(name)}(?![\w-])")
    return any(pattern.search(path.read_text(encoding="utf-8", errors="replace"))
               for kind in RECORD_DIRS if (delivery / kind).is_dir()
               for path in (delivery / kind).rglob("*.md"))


def under(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def door_commit(fields: dict, slug: str, args: dict, answer: Answer) -> None:
    import deliver
    import goal
    delivery = fields["delivery_root"].resolve() / slug
    telemetry = fields["telemetry_root"].resolve()
    log = delivery / LOG_FILE
    named = [(fields["home"] / path).resolve() for path in args["file"]]

    lines = [line for line in log.read_text(encoding="utf-8").splitlines() if line.strip()] \
        if log.is_file() else []
    matched = goal.STOP_LINE.match(lines[-1]) if lines else None
    if matched and matched.group(1) in goal.STOP_CLASSES:
        beyond = [path for path in named if path != log and not under(path, telemetry)]
        if not named:
            answer.refuse(f"{log} closes on a stop line, and no --file names the commit — after a "
                          f"stop nothing of the delivery is committed but the measure: the "
                          f"telemetry root {telemetry} and the log itself", lines[-1])
        elif beyond:
            answer.refuse(f"{log} closes on a stop line, and the commit names paths outside the "
                          f"telemetry root {telemetry} and the log — after a stop the measure "
                          f"alone is committed, and the delivery's files are left for the person",
                          "\n".join([lines[-1], *(str(path) for path in beyond)]))
        else:
            answer.checked.append(f"{log} closes on a stop line, and every path named lies under "
                                  f"the telemetry root or is the log — the measure")
    elif lines:
        answer.checked.append(f"{log} does not close on a stop line: {lines[-1]}")
    else:
        answer.checked.append(f"{log} holds no line — no run of /deliver-scope wrote one")

    runs = delivery / RUN_DIR
    if named and not any(under(path, delivery) or under(delivery, path) for path in named):
        answer.checked.append(f"no path named reaches {delivery}, so no run under it is read")
        return
    red = []
    for directory in sorted(runs.iterdir()) if runs.is_dir() else []:
        record = directory / "run.json"
        if not record.is_file() or not pending([directory]):
            continue
        captured, unreadable = deliver.read_run(record, f"{RUN_DIR}/{directory.name}")
        outcome = None if captured is None else captured.get("outcome")
        if outcome != "passed" and not named_by_a_record(delivery, directory.name):
            red.append(f"{RUN_DIR}/{directory.name}: " + (
                unreadable or f"ended `{outcome}` at the step `{captured.get('failed_step')}`"))
    if red:
        answer.refuse(f"{runs} holds a red run git does not hold and no record under {delivery} "
                      f"names — the delivery did not answer it, and committing it commits a red "
                      f"as delivered", "\n".join(red))
    else:
        answer.checked.append(f"every run under {runs} git does not hold passed, or a record "
                              f"names it")


CHECKS = {
    "implement-task": door_implement_task,
    "plan-work": door_plan_work,
    "review-change": door_review_change,
    "deliver-scope": door_deliver_scope,
    "reconcile": door_reconcile,
}


def check(door: str, project_root: Path, args: dict) -> Answer:
    answer = Answer()
    fields, unresolved, out = resolve(project_root)
    if unresolved:
        answer.refuse(unresolved, out)
        return answer
    missing = [name for name in ROOTS[door] if name not in fields]
    if missing or (not fields["targets"] and door != "commit"):
        answer.refuse(f"siegard.json declares no {', '.join(missing or ['targets'])} — the entry "
                      f"point stops on it; /siegard-config declares it")
        return answer

    if door == "commit":
        slug = slug_of(fields, args, answer)
        if slug is not None:
            fields["home"] = toplevel(project_root) or project_root
            door_commit(fields, slug, args, answer)
        return answer

    target = args["target"]
    if target is None:
        if len(fields["targets"]) != 1:
            answer.refuse(f"no target named, and siegard.json declares "
                          f"{len(fields['targets'])} ({', '.join(sorted(fields['targets']))}) — "
                          f"name one")
            return answer
        target = next(iter(fields["targets"]))
        answer.decided.append(f"target {target} — the one siegard.json declares")
    elif target not in fields["targets"]:
        answer.refuse(f"siegard.json declares no target {target} "
                      f"({', '.join(sorted(fields['targets']))})")
        return answer

    slug = slug_of(fields, args, answer)
    if slug is not None:
        CHECKS[door](fields, target, slug, args, answer)
    return answer


def slug_of(fields: dict, args: dict, answer: Answer) -> str | None:
    """The slug named, or the one live initiative, or None with the refusal said."""
    if args["slug"] is not None:
        return args["slug"]
    live = live_initiatives(fields["work_root"])
    if len(live) != 1:
        answer.refuse(f"no slug named, and {fields['work_root']} holds {len(live)} live "
                      f"initiative(s){': ' + ', '.join(live) if live else ''} — name one")
        return None
    answer.decided.append(f"slug {live[0]} — the one live initiative under {fields['work_root']}")
    return live[0]


def take(args: list[str], flag: str, many: bool = False):
    values = []
    while flag in args:
        at = args.index(flag)
        if at + 1 >= len(args) or args[at + 1].startswith("--"):
            raise CannotRun(f"{flag} takes a value")
        values.append(args[at + 1])
        del args[at:at + 2]
        if not many:
            if flag in args:
                raise CannotRun(f"{flag} is named twice")
            break
    return values if many else (values[0] if values else None)


def main() -> int:
    args = sys.argv[1:]
    if "--help" in args:
        # The docstring is this script's one home of what it does and how it is called,
        # so `--help` prints that rather than a second copy of it that could drift.
        print(__doc__.strip())
        return 0
    try:
        door = take(args, "--check")
        given = {
            "project": take(args, "--project"),
            "target": take(args, "--target"),
            "slug": take(args, "--slug"),
            "task": take(args, "--task", many=True),
            "name": take(args, "--name"),
            "scope": take(args, "--scope", many=True),
            "file": take(args, "--file", many=True),
            "standard": take(args, "--standard"),
        }
    except CannotRun as refusal:
        print(f"cannot run: {refusal}", file=sys.stderr)
        return CANNOT_RUN
    if args or door is None:
        print(f"cannot run: expected --check <skill> and the inputs it takes"
              + (f"; not understood: {' '.join(args)}" if args else ""), file=sys.stderr)
        return CANNOT_RUN
    door = door.removeprefix("/").removeprefix("siegard:")
    if door not in DOORS:
        print(f"cannot run: {door} is no door this checks — {', '.join(DOORS)}", file=sys.stderr)
        return CANNOT_RUN
    if door in NAMED_SLUG and not given["slug"]:
        print(f"cannot run: {door} takes --slug; its slug is named, and no tree decides it",
              file=sys.stderr)
        return CANNOT_RUN
    if door == "reconcile" and not given["file"]:
        print("cannot run: reconcile takes its file set, one --file per path", file=sys.stderr)
        return CANNOT_RUN
    unused = [flag for flag, doors in (("task", ("implement-task", "review-change")),
                                       ("name", ("review-change",)),
                                       ("scope", ("deliver-scope",)),
                                       ("file", ("reconcile", "commit")),
                                       ("target", DOORS[:-1]),
                                       ("standard", DOORS[:-1]))
              if given[flag] and door not in doors]
    if unused:
        print(f"cannot run: {door} takes no --{', --'.join(unused)}", file=sys.stderr)
        return CANNOT_RUN
    project_root = Path(given["project"] or ".").resolve()
    if not project_root.is_dir():
        print(f"cannot run: {project_root} is not a directory", file=sys.stderr)
        return CANNOT_RUN
    answer = check(door, project_root, given)
    print("\n".join(answer.lines(door)))
    return 1 if answer.refused else 0


if __name__ == "__main__":
    sys.exit(main())
