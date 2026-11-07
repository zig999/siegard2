#!/usr/bin/env python3
"""Set up, prompt and grade a model run of `/reconcile` over a recorded benchmark case.

The cases live under tests/fixtures/benchmarks/reconcile/cases/<name>/case.json and reconcile one
hand edit: the fixture project the implement-task benchmark delivers into
(tests/fixtures/benchmarks/implement-task/project/), with that benchmark's recorded first
delivery (iteration-2/first-delivery) laid over it and committed, exactly as the review-change
benchmark seeds it — then a second commit that edits `app/lending/fees.py` after the bind, so the
trace reports `code` drift on it. `setup` builds that repository, `prompt` prints what the running
agent is handed, and `record` copies what the run left into an iteration directory and grades it;
`tests/test_benchmarks.py` recomputes every expectation from the record.

A resumed case is a compaction: `setup` runs the reconciliation through step 4 with the
framework's own writers — the staging, the returns the case's `pre/` holds saved through
`--save-return`, the fold and the record's validation — leaves it uncommitted, and cuts the skill
where Claude Code re-attaches it. A `quiz` case runs nothing, exactly as the implement-task
benchmark's.

Usage:
    python3 tools/bench_reconcile.py setup  <case> <project-dir> [--skill <SKILL.md>]
    python3 tools/bench_reconcile.py prompt <case> <project-dir> <out-dir> [--skill <SKILL.md>]
    python3 tools/bench_reconcile.py record <case> <project-dir> <out-dir> <record-dir>
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
from bench_implement_task import (CACHES, LETTERS, bin_run, git,  # noqa: E402
                                  quiz_options)
from bench_review_change import (DELIVERED, FIXTURE, sound_copy,  # noqa: E402
                                 transcript_of, workspace_of)

REPO = Path(__file__).resolve().parent.parent
PLUGIN = REPO / "src/claude"
SKILL = PLUGIN / "skills/reconcile/SKILL.md"
BENCH = REPO / "tests/fixtures/benchmarks/reconcile"
CASES = BENCH / "cases"
NODE = "rules/lending/late-fee-per-overdue-day"
SLUG = "fees-hand-edit"
FILE = "lending/fees.py"
RECONCILIATION = f"siegard-reconcile/{SLUG}.md"
RETURNS = f"siegard-reconcile/{SLUG}.returns"
AGENTS = ("coverage-auditor", "specification-conformance-reviewer")
EDITED = '''from lending.loans import Loan

FEE_CENTS_PER_OVERDUE_DAY = 100


def late_fee_cents(loan: Loan) -> int:
    # A loan returned after its due date pays 100 cents for each overdue day.
    overdue_days = (loan.returned_on - loan.due_on).days
    if overdue_days <= 0:
        return 0
    return overdue_days * FEE_CENTS_PER_OVERDUE_DAY
'''
SAID = ("renamed the late fee constant in lending/fees.py by hand and added a comment; the "
        "behavior did not change and the code is correct")
COMMANDS = {"stage": r"trace\.py[^\n]*--stage", "save_return": r"trace\.py[^\n]*--save-return",
            "fold": r"trace\.py[^\n]*--fold",
            "reconciliation": r"trace\.py[^\n]*--reconciliation",
            "bind_record": r"trace\.py[^\n]*--bind-record[^\n]*--workspace",
            "save_report": r"handoff\.py[^\n]*--save-report",
            "render": r"handoff\.py[^\n]*--render"}
OWN_ROOTS = ("siegard-reconcile/", "siegard-trace.json")


def case(name: str) -> dict:
    data = json.loads((CASES / name / "case.json").read_text(encoding="utf-8"))
    data["dir"] = CASES / name
    return data


def resume_after_fold(c: dict, project: Path) -> None:
    """Steps 1-4 through the framework's writers: staged, every return saved, folded, validated."""
    bins, work = PLUGIN / "bin", workspace_of(project)
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    name = FILE.replace("/", "__")
    reply = (c["dir"] / "pre" / f"{name}.yaml").read_text(encoding="utf-8")
    steps = [(bins / "trace.py", "--stage", "app", "spec", SLUG, work, FILE),
             (bins / "trace.py", "--save-return", "app", work, FILE,
              transcript_of(reply, work / f"{name}.jsonl")),
             (bins / "trace.py", "--fold", "app", work, c["dir"] / "pre/premise.yaml",
              RECONCILIATION),
             (bins / "trace.py", "--reconciliation", RECONCILIATION)]
    for step in steps:
        code, said = bin_run(*step, cwd=project)
        assert code == 0, f"{step[1]}: {said}"
    for cache in project.rglob("__pycache__"):
        shutil.rmtree(cache)


def setup(name: str, project: Path, skill: Path) -> None:
    c = case(name)
    if project.exists():
        shutil.rmtree(project)
    if c.get("kind") == "quiz":
        project.mkdir(parents=True)
        return
    shutil.copytree(FIXTURE, project, ignore=CACHES)
    for part in ("app", "work"):
        shutil.rmtree(project / part)
    for part in ("delivery", "app", "work"):
        shutil.copytree(DELIVERED / part, project / part, ignore=CACHES)
    shutil.copy(DELIVERED / "siegard-trace.json", project / "siegard-trace.json")
    git(project, "init", "-q")
    who = ("-c", "user.name=bench", "-c", "user.email=bench@localhost")
    git(project, "add", "--", ".")
    git(project, *who, "commit", "-qm", "seed")
    (project / "app" / FILE).write_text(EDITED, encoding="utf-8")
    git(project, "add", "--", f"app/{FILE}")
    git(project, *who, "commit", "-qm", "Rename the late fee constant and say the rule")
    if c.get("resume_after_step"):
        resume_after_fold(c, project)
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
            f"of the `/reconcile` skill of a plugin, and of the two subagents it spawns. Answer "
            f"each question below by what those files require — not by what you would do "
            f"otherwise, and not by what another file might say. Each question has exactly one "
            f"answer the files decide.\n\n" + "\n".join(lines) +
            f"\n\nWrite {out}/answers.json: one JSON object mapping each question's number, as a "
            f"string, to its letter, e.g. {{\"1\": \"a\"}}. Write {out}/files-read.txt: every file "
            f"you read, one per line. Return the answers on one line.")


def invocation(project: Path) -> str:
    return f"/reconcile {project} files {FILE} target app slug {SLUG} — {SAID}"


def prompt(name: str, project: Path, out: Path, skill: Path) -> str:
    c = case(name)
    if c.get("kind") == "quiz":
        return quiz_prompt(c, out, skill)
    keep = ("Never commit or change git state. Do not modify anything under "
            f"{REPO}.\n\nWhen done, save to {out}/: `report.md` (the full report and the handoff "
            "you would hand the person, verbatim), `files-read.txt` (every file you read, in "
            "order, one per line) and `commands.txt` (every bin/*.py command you ran, one per "
            "line, with its exit code). Return a 5-line summary.")
    root = f"`${{CLAUDE_PLUGIN_ROOT}}` = {skill.parent.parent.parent}."
    inline = ("No agent of this plugin is registered in this session, so every spawn the skill "
              "asks for fails: say so as the spawn failure, and apply the inline route the skill "
              "states.")
    if c.get("resume_after_step"):
        cut = project.parent / f"{project.name}.skill-after-compaction.md"
        work = workspace_of(project)
        return (f"You are resuming a Claude Code skill invocation right after a context "
                f"compaction. Act exactly as a session in that state would.\n\nWhat you hold of "
                f"the skill: the file {cut} is the text of the `/reconcile` skill that Claude "
                f"Code re-attached after compaction — truncated, as Claude Code does. Read it "
                f"first. It is all of the skill you remember. Read other files only where that "
                f"text tells you to, or where the work itself plainly needs it; do not go looking "
                f"for a fuller copy of the skill unless that text tells you to. {root} {inline}"
                f"\n\nCompaction summary of the session so far: the user invoked "
                f"`{invocation(project)}` (session language pt-BR). Done before compaction: every "
                f"input present; `project.py` resolved specification_root `spec` and target `app` "
                f"(from siegard.json); `git status --porcelain -- app/{FILE} spec` printed "
                f"nothing and siegard-trace.json was clean; the contract "
                f"`schemas/reconciliation.json` was read. Step 1: `spec.py spec` passed, "
                f"`trace.py app` passed, `{RECONCILIATION}` was free. Step 2: `trace.py --check "
                f"app` reported `code` drift on app/{FILE} staling {NODE}; `trace.py --stage` "
                f"into the workspace {work} staged 1 file over 1 node, one wave, nothing omitted, "
                f"nothing under `mechanical` or `rewritten`, no certification. Step 3: the spawn "
                f"failed (no agent registered) and the conformance judgment ran inline, the "
                f"session having written no node; its return is saved under `{RETURNS}/`, and "
                f"`--save-return` reported `0 pending`. Step 3b: skipped, nothing mechanical and "
                f"nothing rewritten. Step 4: the premise was written in the workspace, "
                f"`trace.py --fold` wrote `{RECONCILIATION}`, and `trace.py --reconciliation` "
                f"accepted it. Continue the invocation from where it stands to its end."
                f"\n\nYou cannot ask the user anything. {keep}")
    return (f"Execute this task by following a skill file exactly as if the user had invoked "
            f"it.\n\n- Skill: read {skill} and follow it. {root} Read only what the skill tells "
            f"you to read. {inline}\n- The user's invocation (session language pt-BR): "
            f"`{invocation(project)}`\n- You cannot ask the user anything; where the skill says "
            f"stop, stop and report. {keep}")


def drift_on(copy: Path) -> tuple[bool, str]:
    code, said = bin_run(PLUGIN / "bin/trace.py", "--check", "app", cwd=copy)
    return (f"app/{FILE}" in said and code != 0), said.splitlines()[0] if said else ""


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
    for check in c["checks"]:
        kind, _, arg = check.partition(":")
        if kind == "reconciliation_sound":
            with tempfile.TemporaryDirectory() as tmp:
                copy = sound_copy(record, Path(tmp))
                code, said = bin_run(PLUGIN / "bin/trace.py", "--reconciliation", RECONCILIATION,
                                     cwd=copy) if (copy / RECONCILIATION).is_file() \
                    else (1, f"no {RECONCILIATION}")
            out.append((f"mechanical: trace.py --reconciliation accepts {RECONCILIATION}",
                        code == 0, said.splitlines()[0] if said else ""))
        elif kind == "returns_saved":
            saved = sorted(p.name for p in (record / RETURNS).glob("*.yaml")) \
                if (record / RETURNS).is_dir() else []
            ok = "lending__fees.py.yaml" in saved
            out.append((f"mechanical: the return for {FILE} is saved under {RETURNS}/", ok,
                        str(saved)))
        elif kind == "trace_bound":
            trace = record / "siegard-trace.json"
            data = json.loads(trace.read_text(encoding="utf-8")) if trace.is_file() else {}
            files = [f for b in data.get("bindings", []) if b["node"] == NODE for f in b["files"]
                     if f["path"] == f"app/{FILE}"]
            ok = bool(files) and bool(files[0].get("judged"))
            out.append((f"mechanical: the trace binds {NODE} to app/{FILE} as judged", ok,
                        json.dumps(files[0])[:200] if files else "no binding"))
        elif kind == "no_drift":
            with tempfile.TemporaryDirectory() as tmp:
                drifted, said = drift_on(sound_copy(record, Path(tmp)))
            out.append((f"mechanical: trace.py --check reports no drift on app/{FILE}",
                        not drifted, said))
        elif kind == "handoff_saved":
            saved = record / "handoff.md"
            ok = saved.exists() and bool(saved.read_text(encoding="utf-8").strip())
            out.append(("mechanical: the report was saved through handoff.py --save-report", ok,
                        "handoff.md" if saved.exists() else "nothing under .git/siegard/handoff/"))
        elif kind == "report_says":
            ok = arg.lower() in report.lower()
            out.append((f"mechanical: the report says {arg}", ok, arg if ok else ""))
        elif kind == "no_commit":
            out.append(("reported: the run made no commit", facts.get("commits_added") == 0,
                        f"commits added: {facts.get('commits_added')}"))
        elif kind == "writes_only_its_roots":
            stray = facts.get("changed_outside_roots", [])
            out.append(("reported: the run wrote nothing outside siegard-reconcile/ and "
                        "siegard-trace.json",
                        not stray and "changed_outside_roots" in facts, f"outside: {stray}"))
        elif kind == "reported":
            hit = re.search(COMMANDS[arg], commands)
            out.append((f"reported: commands.txt shows {COMMANDS[arg]}", bool(hit),
                        hit.group(0)[:200] if hit else ""))
        else:
            raise SystemExit(f"cannot run: {name} names an unknown check {check!r}")
    return [{"text": t, "passed": bool(p), "evidence": e} for t, p, e in out]


SEED_COMMITS = 2


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
        for part in ("delivery", "work", "app", "siegard-reconcile"):
            if (project / part).is_dir():
                shutil.copytree(project / part, dest / part, ignore=CACHES)
        if (project / "siegard-trace.json").is_file():
            shutil.copy(project / "siegard-trace.json", dest / "siegard-trace.json")
        saved = sorted((project / ".git/siegard/handoff").glob("*.md")) \
            if (project / ".git/siegard/handoff").is_dir() else []
        if saved:
            shutil.copy(saved[-1], dest / "handoff.md")
        status = git(project, "status", "--porcelain", "--untracked-files=all")
        changed = [line[3:] for line in status.splitlines()
                   if "__pycache__" not in line and ".pytest_cache" not in line]
        facts = {"commits_added": int(git(project, "rev-list", "--count", "HEAD").strip())
                 - SEED_COMMITS,
                 "changed_outside_roots": sorted(p for p in changed if not p.startswith(OWN_ROOTS))}
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
