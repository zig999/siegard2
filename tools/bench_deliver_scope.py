#!/usr/bin/env python3
"""Set up, prompt and grade a model run of `/deliver-scope` over a recorded benchmark case.

The cases live under tests/fixtures/benchmarks/deliver-scope/cases/<name>/case.json and carry
one epic end to end: the fixture project the implement-task benchmark delivers into
(tests/fixtures/benchmarks/implement-task/project/), plan `lending` with epic `epic/fees` and its
one task `task/fees/compute-late-fee` undelivered, committed as the seed with a `telemetry_root`
declared. The ask is the person's own words naming the reach `epic/fees`, so step 1 plans
nothing. `setup` builds that repository, `prompt` prints what the running agent is handed, and
`record` copies what the run left into an iteration directory, reads every commit the run added
above the seed, and grades it; `tests/test_benchmarks.py` recomputes every expectation from the
record.

This skill commits. Where the other benchmarks hold that a run made no commit, this one reads
each commit: its subject opens `deliver-scope lending: `, its paths lie inside the roots the skill
declares, and the run created no branch and no remote, so nothing could be pushed.

A resumed case is a compaction after step 4: `setup` commits the implement-task benchmark's
recorded first delivery (`iteration-2/first-delivery`) as the delivery step and the review-change
benchmark's recorded review (`iteration-1/full-review`, its name `fees-review` renamed to the slug
`lending`, as step 4 names a review) as the review step, each with the log's lines, and cuts the
skill where Claude Code re-attaches it. A `quiz` case runs nothing, exactly as the implement-task
benchmark's.

Usage:
    python3 tools/bench_deliver_scope.py setup  <case> <project-dir> [--skill <SKILL.md>]
    python3 tools/bench_deliver_scope.py prompt <case> <project-dir> <out-dir> [--skill <SKILL.md>]
    python3 tools/bench_deliver_scope.py record <case> <project-dir> <out-dir> <record-dir>
                                              --arm <label> [--tokens N] [--seconds S]
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bench_implement_task import (CACHES, LETTERS, bin_run, front, git,  # noqa: E402
                                  quiz_options)
from bench_review_change import (DELIVERED, FIXTURE, sound_copy,  # noqa: E402,F401
                                 transcript_of, workspace_of)

REPO = Path(__file__).resolve().parent.parent
PLUGIN = REPO / "src/claude"
SKILL = PLUGIN / "skills/deliver-scope/SKILL.md"
BENCH = REPO / "tests/fixtures/benchmarks/deliver-scope"
CASES = BENCH / "cases"
REVIEWED = REPO / "tests/fixtures/benchmarks/review-change/iteration-1/full-review"
SLUG = "lending"
EPIC = "epic/fees"
TASK = "task/fees/compute-late-fee"
NODE = "rules/lending/late-fee-per-overdue-day"
REVIEW = SLUG
REVIEW_RECORD = f"delivery/{SLUG}/review/{REVIEW}.md"
LOG = f"delivery/{SLUG}/orchestration.md"
PREFIX = f"deliver-scope {SLUG}: "
ASK = ("Quero o épico epic/fees do plano lending entregue de ponta a ponta: implementa a tarefa "
       "que falta, revisa e comita cada passo, sem parar no meio pra me perguntar.")
WHO = ("-c", "user.name=bench", "-c", "user.email=bench@localhost")
ROOTS = ("delivery/", "app/", "work/", "spec/", "telemetry/", "siegard-reconcile/",
         "siegard-trace.json")
OWNED = {"deliver": ("delivery/", "app/", "siegard-trace.json"),
         "review": ("delivery/", "siegard-reconcile/", "siegard-trace.json"),
         "measure": ("telemetry/", "delivery/")}
COMMANDS = {"outstanding": r"deliver\.py[^\n]*--outstanding",
            "probe": r"telemetry\.py[^\n]*--probe",
            "prepare": r"handoff\.py[^\n]*--prepare",
            "save_report": r"handoff\.py[^\n]*--save-report",
            "render": r"handoff\.py[^\n]*--render"}
AGENTS = ("door-decider",)


def case(name: str) -> dict:
    data = json.loads((CASES / name / "case.json").read_text(encoding="utf-8"))
    data["dir"] = CASES / name
    return data


def seed(project: Path) -> None:
    """The fixture project with a telemetry root declared, committed once with a git identity."""
    shutil.copytree(FIXTURE, project, ignore=CACHES)
    declared = json.loads((project / "siegard.json").read_text(encoding="utf-8"))
    declared["telemetry_root"] = "telemetry"
    (project / "siegard.json").write_text(json.dumps(declared, indent=2) + "\n", encoding="utf-8")
    git(project, "init", "-q", "-b", "main")
    git(project, "config", "user.name", "bench")
    git(project, "config", "user.email", "bench@localhost")
    git(project, "add", "--", ".")
    git(project, *WHO, "commit", "-qm", "seed")


def lay(source: Path, project: Path, parts: tuple[str, ...], rename: tuple[str, str] | None) -> None:
    """Copy a recorded run's roots over the project, renaming one review name in paths and text."""
    for part in parts:
        src = source / part
        if src.is_file():
            shutil.copy(src, project / part)
            continue
        for path in sorted(p for p in src.rglob("*") if p.is_file() and "__pycache__" not in p.parts):
            rel = path.relative_to(source).as_posix()
            if rename:
                rel = rel.replace(*rename)
            dest = project / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            data = path.read_bytes()
            if rename:
                data = data.replace(rename[0].encode(), rename[1].encode())
            dest.write_bytes(data)
    if rename and (project / "siegard-trace.json").is_file():
        trace = project / "siegard-trace.json"
        trace.write_text(trace.read_text(encoding="utf-8").replace(*rename), encoding="utf-8")


def log_line(project: Path, line: str) -> None:
    log = project / LOG
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as out:
        out.write(line + "\n")


def commit(project: Path, message: str, *paths: str) -> str:
    git(project, "add", "--", *paths)
    git(project, *WHO, "commit", "-qm", message, "--", *paths)
    return git(project, "rev-parse", "--short", "HEAD").strip()


def resume_after_review(project: Path) -> None:
    """Steps 1-4 as the skill leaves them: the plan skipped, the delivery committed, the review
    committed, each step's line in the log; the review's line not yet committed."""
    log_line(project, f"plan: skipped — the ask names {EPIC}, which the live plan {SLUG} holds; "
                      f"--outstanding listed {TASK} deliverable.")
    lay(DELIVERED, project, ("delivery", "app", "siegard-trace.json"), None)
    delivered = commit(project, f"{PREFIX}deliver {TASK}", "delivery", "app", "siegard-trace.json")
    log_line(project, f"/implement-task {TASK}: commit {delivered} — delivered, the "
                      f"implementation and the proof written, suite green.")
    lay(REVIEWED, project, ("delivery", "siegard-reconcile", "siegard-trace.json"),
        ("fees-review", REVIEW))
    reviewed = commit(project, f"{PREFIX}review", "delivery", "siegard-reconcile",
                      "siegard-trace.json")
    log_line(project, f"/review-change {REVIEW}: commit {reviewed} — review written, 2 "
                      f"findings (conformance unstated 2), no certification staged.")
    for cache in project.rglob("__pycache__"):
        shutil.rmtree(cache)


def record_ask(project: Path, plugin: Path) -> None:
    """The ask recorded as the session rules have it recorded in the turn it is given, left
    untracked under the telemetry root the measure commits; `ask.py`'s `read:` line beside the
    project for the prompt to carry."""
    import subprocess
    done = subprocess.run([sys.executable, "-B", str(plugin / "bin/ask.py"), "--record",
                           str(project), "--text-file", "-"], input=ASK, capture_output=True,
                          text=True, check=True)
    read = next(line for line in done.stdout.splitlines() if line.startswith("read: "))
    (project.parent / f"{project.name}.ask-read.txt").write_text(read + "\n", encoding="utf-8")


def setup(name: str, project: Path, skill: Path) -> None:
    c = case(name)
    if project.exists():
        shutil.rmtree(project)
    if c.get("kind") == "quiz":
        project.mkdir(parents=True)
        return
    seed(project)
    if c.get("record_ask"):
        record_ask(project, skill.parent.parent.parent)
    if c.get("resume_after_step"):
        resume_after_review(project)
    if c.get("truncate_chars"):
        text = skill.read_text(encoding="utf-8")[: c["truncate_chars"]]
        (project.parent / f"{project.name}.skill-after-compaction.md").write_text(
            text[: text.rfind("\n")], encoding="utf-8")


def quiz_prompt(c: dict, out: Path, skill: Path) -> str:
    plugin = skill.parent.parent.parent
    files = [skill, *sorted((skill.parent / "references").glob("*.md")),
             *(plugin / "agents" / f"{a}.md" for a in AGENTS)]
    lines = []
    for q in c["questions"]:
        options, _ = quiz_options(q)
        lines.append(f"{q['id']}. {q['q']}")
        lines += [f"   {LETTERS[i]}) {o}" for i, o in enumerate(options)]
    listing = "\n".join(f"- {f}" for f in files)
    return (f"Read these files, whole, and nothing else:\n{listing}\n\nThey are the instructions "
            f"of the `/deliver-scope` skill of a plugin, and of the one subagent it spawns. "
            f"Answer each question below by what those files require — not by what you would do "
            f"otherwise, and not by what another file might say. Each question has exactly one "
            f"answer the files decide.\n\n" + "\n".join(lines) +
            f"\n\nWrite {out}/answers.json: one JSON object mapping each question's number, as a "
            f"string, to its letter, e.g. {{\"1\": \"a\"}}. Write {out}/files-read.txt: every file "
            f"you read, one per line. Return the answers on one line.")


def invocation(project: Path) -> str:
    return f"/deliver-scope {project} target app slug {SLUG} scope {EPIC} — \"{ASK}\""


def prompt(name: str, project: Path, out: Path, skill: Path) -> str:
    c = case(name)
    if c.get("kind") == "quiz":
        return quiz_prompt(c, out, skill)
    keep = (f"Commit only as the skill states, inside {project}; never push, never create a "
            f"branch, never add a remote. Do not modify anything under {REPO}.\n\nWhen done, "
            f"save to {out}/: `report.md` (the full report and the handoff you would hand the "
            "person, verbatim), `files-read.txt` (every file you read, in order, one per line) "
            "and `commands.txt` (every bin/*.py and git command you ran, one per line, with its "
            "exit code). Return a 5-line summary.")
    root = f"`${{CLAUDE_PLUGIN_ROOT}}` = {skill.parent.parent.parent}."
    inline = ("No agent of this plugin is registered in this session, so every spawn a skill "
              "asks for fails: say so as the spawn failure, and apply the inline route that "
              "skill states. Invoking another skill of the plugin means reading its SKILL.md "
              f"under {skill.parent.parent} and carrying it out inline, whole.")
    if c.get("resume_after_step"):
        cut = project.parent / f"{project.name}.skill-after-compaction.md"
        head = git(project, "rev-list", "--max-parents=0", "HEAD").strip()[:7]
        hashes = git(project, "log", "--format=%h %s", "-2").strip()
        said = project.parent / f"{project.name}.ask-read.txt"
        asked = (f" The ask was recorded in the turn it was given; `ask.py --record` printed "
                 f"`{said.read_text(encoding='utf-8').strip()}`.") if said.is_file() else ""
        return (f"You are resuming a Claude Code skill invocation right after a context "
                f"compaction. Act exactly as a session in that state would.\n\nWhat you hold of "
                f"the skill: the file {cut} is the text of the `/deliver-scope` skill that Claude "
                f"Code re-attached after compaction — truncated, as Claude Code does. Read it "
                f"first. It is all of the skill you remember. Read other files only where that "
                f"text tells you to, or where the work itself plainly needs it; do not go looking "
                f"for a fuller copy of the skill unless that text tells you to. {root} {inline}"
                f"\n\nCompaction summary of the session so far: the user invoked "
                f"`{invocation(project)}` (session language pt-BR). Done before compaction: every "
                f"input present — the ask quoted verbatim above, target `app` and slug `{SLUG}` "
                f"named, the reach `{EPIC}` held by the live plan; `project.py` resolved "
                f"specification_root `spec`, work_root `work`, delivery_root `delivery`, "
                f"telemetry_root `telemetry` and standard `app/standard.yaml`.{asked} The gate: `spec.py "
                f"spec` passed over a committed root; every `git status --porcelain` printed "
                f"nothing; HEAD stood at {head} on `main` when the run began (step 1 began at "
                f"2026-11-07T12:00:00Z). `schemas/plan.json` was read. Step 1: skipped, the ask "
                f"names a reach; nothing committed. Step 3: `deliver.py --outstanding delivery/{SLUG} "
                f"work/{SLUG} app spec --scope {EPIC}` listed {TASK} deliverable; `/implement-task` "
                f"delivered it (implementation and proof written, suite green, no stop) and it "
                f"was committed. Step 4: `--outstanding` listed nothing left; `/review-change` "
                f"was invoked over {TASK}, files lending/fees.py and tests/test_fees.py, review "
                f"name `{REVIEW}` (the slug, free); its record is written with 2 conformance "
                f"findings (`unstated`), no certification staged or refused, and it was "
                f"committed. The two commits, newest first:\n{hashes}\nThe log "
                f"`{LOG}` holds one line per step so far; the review's line is not yet committed. "
                f"Continue the invocation from where it stands to its end."
                f"\n\nYou cannot ask the user anything. {keep}")
    return (f"Execute this task by following a skill file exactly as if the user had invoked "
            f"it.\n\n- Skill: read {skill} and follow it. {root} Read only what the skill tells "
            f"you to read. {inline}\n- The user's invocation (session language pt-BR): "
            f"`{invocation(project)}`\n- You cannot ask the user anything; where the skill says "
            f"stop, stop and report. {keep}")


def under(path: str, roots: tuple[str, ...]) -> bool:
    return path.startswith(roots) or path in roots


def checks(name: str, record: Path) -> list[dict]:
    c = case(name)
    out: list[tuple[str, bool, str]] = []
    if c.get("kind") == "quiz":
        answers = json.loads((record / "answers.json").read_text(encoding="utf-8")) \
            if (record / "answers.json").is_file() else {}
        for q in c["questions"]:
            _, key = quiz_options(q)
            given = str(answers.get(str(q["id"]), "")).strip().lower()
            out.append((f"mechanical: question {q['id']} is answered {key}", given == key,
                        f"answered {given or 'nothing'}"))
        return [{"text": t, "passed": p, "evidence": e} for t, p, e in out]
    report = (record / "report.md").read_text(encoding="utf-8") if (record / "report.md").exists() else ""
    commands = (record / "commands.txt").read_text(encoding="utf-8") if (record / "commands.txt").exists() else ""
    facts = json.loads((record / "facts.json").read_text(encoding="utf-8")) if (record / "facts.json").exists() else {}
    commits = facts.get("commits", [])
    review = front(record / REVIEW_RECORD) if (record / REVIEW_RECORD).is_file() else {}
    for check in c["checks"]:
        kind, _, arg = check.partition(":")
        if kind == "delivery_sound":
            with tempfile.TemporaryDirectory() as tmp:
                copy = sound_copy(record, Path(tmp))
                code, said = bin_run(PLUGIN / "bin/deliver.py", "--check", f"delivery/{SLUG}",
                                     f"work/{SLUG}", "app", "spec", cwd=copy)
            out.append(("mechanical: deliver.py --check accepts the recorded delivery", code == 0,
                        said.splitlines()[-1] if said else ""))
        elif kind == "review_sound":
            with tempfile.TemporaryDirectory() as tmp:
                copy = sound_copy(record, Path(tmp))
                code, said = bin_run(PLUGIN / "bin/deliver.py", "--review", REVIEW,
                                     f"delivery/{SLUG}", f"work/{SLUG}", "app", "spec", cwd=copy) \
                    if (copy / REVIEW_RECORD).is_file() else (1, f"no {REVIEW_RECORD}")
            out.append((f"mechanical: deliver.py --review {REVIEW} accepts the recorded review",
                        code == 0, said.splitlines()[-1] if said else ""))
        elif kind == "committed":
            subject = PREFIX + arg
            hits = [k for k in commits if k["subject"] == subject]
            step = arg.split()[0]
            stray = [f for k in hits for f in k["files"] if not under(f, OWNED[step])]
            ok = len(hits) == 1 and bool(hits[0]["files"]) and not stray
            out.append((f"mechanical: one commit '{subject}' with a pathspec inside "
                        f"{', '.join(OWNED[step])}", ok,
                        f"{len(hits)} commit(s); outside: {stray}"))
        elif kind == "measure_committed":
            written = sorted(p.relative_to(record).as_posix()
                             for p in (record / "telemetry").rglob("*") if p.is_file()) \
                if (record / "telemetry").is_dir() else []
            hits = [k for k in commits if k["subject"] == PREFIX + "measure"]
            stray = [f for k in hits for f in k["files"] if not under(f, OWNED["measure"])]
            carried = [f for k in hits for f in k["files"] if f.startswith("telemetry/")]
            ok = (len(hits) == 1 and not stray and bool(carried)) if written \
                else (len(hits) <= 1 and not stray and not carried)
            out.append(("mechanical: the measure is committed where the probe wrote, and only "
                        "there", ok, f"written {written}; measure commits {len(hits)}"))
        elif kind == "commits_named":
            off = [k["subject"] for k in commits if not k["subject"].startswith(PREFIX)]
            out.append((f"mechanical: every commit the run added opens '{PREFIX}'",
                        bool(commits) and not off, f"{len(commits)} commit(s); off: {off}"))
        elif kind == "commits_inside_roots":
            stray = sorted({f for k in commits for f in k["files"] if not under(f, ROOTS)})
            out.append(("mechanical: every commit names paths inside the declared roots",
                        bool(commits) and not stray, f"outside: {stray}"))
        elif kind == "no_branch_no_remote":
            ok = facts.get("branches") == ["main"] and facts.get("remotes") == []
            out.append(("mechanical: the run created no branch and no remote", ok,
                        f"branches {facts.get('branches')}, remotes {facts.get('remotes')}"))
        elif kind == "log_lines":
            log = record / LOG
            lines = [x for x in log.read_text(encoding="utf-8").splitlines() if x.strip()] \
                if log.is_file() else []
            text = "\n".join(lines).lower()
            named = [w for w in arg.split(",") if w not in text]
            ok = len(lines) >= len(arg.split(",")) and not named
            out.append((f"mechanical: {LOG} holds a line per step naming {arg}", ok,
                        f"{len(lines)} line(s); missing {named}"))
        elif kind == "review_named":
            folder = record / f"delivery/{SLUG}/review"
            names = sorted(p.name for p in folder.glob("*.md")) if folder.is_dir() else []
            ok = names == [f"{REVIEW}.md"] and review.get("reconciliation") in \
                (None, f"siegard-reconcile/{REVIEW}.md")
            out.append((f"mechanical: the review is named {REVIEW}, the slug, by step 4's rule", ok,
                        f"{names}; reconciliation {review.get('reconciliation')}"))
        elif kind == "handoff_saved":
            saved = record / "handoff.md"
            ok = saved.exists() and bool(saved.read_text(encoding="utf-8").strip())
            out.append(("mechanical: the report was saved through handoff.py --save-report", ok,
                        "handoff.md" if saved.exists() else "nothing under .git/siegard/handoff/"))
        elif kind == "report_says":
            ok = arg.lower() in report.lower()
            out.append((f"mechanical: the report says {arg}", ok, arg if ok else ""))
        elif kind == "writes_only_its_roots":
            stray = facts.get("changed_outside_roots", [])
            out.append(("reported: the run wrote nothing outside the declared roots",
                        not stray and "changed_outside_roots" in facts, f"outside: {stray}"))
        elif kind == "reported":
            hit = re.search(COMMANDS[arg], commands)
            out.append((f"reported: commands.txt shows {COMMANDS[arg]}", bool(hit),
                        hit.group(0)[:200] if hit else ""))
        else:
            raise SystemExit(f"cannot run: {name} names an unknown check {check!r}")
    return [{"text": t, "passed": bool(p), "evidence": e} for t, p, e in out]


def commits_above_seed(project: Path) -> list[dict]:
    seed_hash = git(project, "rev-list", "--max-parents=0", "HEAD").strip()
    hashes = git(project, "rev-list", "--reverse", f"{seed_hash}..HEAD").split()
    return [{"hash": h[:7], "subject": git(project, "log", "-1", "--format=%s", h).strip(),
             "files": git(project, "show", "--name-only", "--format=", h).split()}
            for h in hashes]


def record(name: str, project: Path, out: Path, dest: Path, arm: str,
           tokens: int | None, seconds: float | None) -> dict:
    if dest.exists():
        raise SystemExit(f"cannot run: {dest} exists; a recorded run is never overwritten")
    dest.mkdir(parents=True)
    quiz = case(name).get("kind") == "quiz"
    files = ("answers.json", "files-read.txt") if quiz else ("report.md", "files-read.txt", "commands.txt")
    for f in files:
        if (out / f).exists():
            shutil.copy(out / f, dest / f)
    if not quiz:
        for part in ("delivery", "work", "app", "siegard-reconcile", "telemetry"):
            if (project / part).is_dir():
                shutil.copytree(project / part, dest / part, ignore=CACHES)
        if (project / "siegard-trace.json").is_file():
            shutil.copy(project / "siegard-trace.json", dest / "siegard-trace.json")
        saved = sorted((project / ".git/siegard/handoff").glob("*.md")) \
            if (project / ".git/siegard/handoff").is_dir() else []
        if saved:
            shutil.copy(saved[-1], dest / "handoff.md")
        commits = commits_above_seed(project)
        status = git(project, "status", "--porcelain", "--untracked-files=all")
        changed = {line[3:] for line in status.splitlines()
                   if "__pycache__" not in line and ".pytest_cache" not in line}
        changed |= {f for k in commits for f in k["files"]}
        facts = {"commits": commits,
                 "branches": sorted(git(project, "branch", "--format=%(refname:short)").split()),
                 "remotes": git(project, "remote").split(),
                 "changed_outside_roots": sorted(p for p in changed if not under(p, ROOTS))}
        (dest / "facts.json").write_text(json.dumps(facts, indent=1) + "\n", encoding="utf-8")
    grading = {"run": dest.name, "case": name, "arm": arm, "subagent_tokens": tokens,
               "seconds": seconds, "expectations": checks(name, dest)}
    (dest / "grading.json").write_text(json.dumps(grading, indent=1, ensure_ascii=False) + "\n",
                                       encoding="utf-8")
    return grading


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("command", choices=("setup", "prompt", "record"))
    parser.add_argument("case")
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--skill", type=Path, default=SKILL)
    parser.add_argument("--arm", default="")
    parser.add_argument("--tokens", type=int)
    parser.add_argument("--seconds", type=float)
    a = parser.parse_args()
    if a.command == "setup":
        setup(a.case, a.paths[0].resolve(), a.skill.resolve())
    elif a.command == "prompt":
        print(prompt(a.case, a.paths[0].resolve(), a.paths[1].resolve(), a.skill.resolve()))
    else:
        g = record(a.case, a.paths[0].resolve(), a.paths[1].resolve(), a.paths[2].resolve(),
                   a.arm, a.tokens, a.seconds)
        for e in g["expectations"]:
            print(("PASS " if e["passed"] else "FAIL ") + e["text"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
