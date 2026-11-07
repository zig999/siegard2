#!/usr/bin/env python3
"""Set up, prompt and grade a model run of `/plan-work` over a recorded benchmark case.

The cases live under tests/fixtures/benchmarks/plan-work/cases/<name>/case.json and plan over the
fixture project the implement-task benchmark delivers into
(tests/fixtures/benchmarks/implement-task/project/), its plan removed: the lending specification,
the Python target `app` and its standard. The scope every planning case hands is `scope.md`
beside the cases. `setup` copies the project into a fresh git repository, `prompt` prints what
the running agent is handed, and `record` copies what the run left into an iteration directory
and grades it; `tests/test_benchmarks.py` recomputes every expectation from the record.

A resumed case is a compaction: `setup` writes the work root as step 4 leaves it — intake,
inventory, epic and tasks, no plan.json — from the case's `pre/`, uncommitted, and cuts the skill
where Claude Code re-attaches it. A `quiz` case runs nothing, exactly as the implement-task
benchmark's.

Usage:
    python3 tools/bench_plan_work.py setup  <case> <project-dir> [--skill <SKILL.md>]
    python3 tools/bench_plan_work.py prompt <case> <project-dir> <out-dir> [--skill <SKILL.md>]
    python3 tools/bench_plan_work.py record <case> <project-dir> <out-dir> <record-dir>
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

REPO = Path(__file__).resolve().parent.parent
PLUGIN = REPO / "src/claude"
SKILL = PLUGIN / "skills/plan-work/SKILL.md"
BENCH = REPO / "tests/fixtures/benchmarks/plan-work"
CASES = BENCH / "cases"
FIXTURE = REPO / "tests/fixtures/benchmarks/implement-task/project"
SLUG = "lending"
SCOPE_NODES = ("rules/lending/loan-due-fourteen-days-after-borrowing",
               "rules/lending/loan-renewed-at-most-once",
               "rules/lending/renewal-extends-due-date-fourteen-days",
               "rules/lending/reserved-copy-blocks-renewal")
AGENTS = ("backlog-decomposer", "codebase-surveyor", "execution-contract-binder",
          "unstated-fact-decider")
COMMANDS = {"impact": r"spec\.py[^\n]*--impact", "digest": r"spec\.py[^\n]*--digest",
            "derive_with_standard": r"plan\.py[^\n]*--standard[^\n]*--against",
            "render": r"handoff\.py[^\n]*--render"}


def case(name: str) -> dict:
    data = json.loads((CASES / name / "case.json").read_text(encoding="utf-8"))
    data["dir"] = CASES / name
    return data


def setup(name: str, project: Path, skill: Path) -> None:
    c = case(name)
    if project.exists():
        shutil.rmtree(project)
    if c.get("kind") == "quiz":
        project.mkdir(parents=True)
        return
    shutil.copytree(FIXTURE, project, ignore=CACHES)
    shutil.rmtree(project / "work" / SLUG)
    (project / "work" / ".gitkeep").write_text("", encoding="utf-8")
    git(project, "init", "-q")
    git(project, "add", "--", ".")
    git(project, "-c", "user.name=bench", "-c", "user.email=bench@localhost", "commit", "-qm", "seed")
    if c.get("resume_after_step"):
        shutil.copytree(c["dir"] / "pre", project / "work" / SLUG)
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
            f"of the `/plan-work` skill of a plugin, and of the four subagents it spawns. Answer "
            f"each question below by what those files require — not by what you would do "
            f"otherwise, and not by what another file might say. Each question has exactly one "
            f"answer the files decide.\n\n" + "\n".join(lines) +
            f"\n\nWrite {out}/answers.json: one JSON object mapping each question's number, as a "
            f"string, to its letter, e.g. {{\"1\": \"a\"}}. Write {out}/files-read.txt: every file "
            f"you read, one per line. Return the answers on one line.")


def prompt(name: str, project: Path, out: Path, skill: Path) -> str:
    c = case(name)
    if c.get("kind") == "quiz":
        return quiz_prompt(c, out, skill)
    scope = (BENCH / "scope.md").read_text(encoding="utf-8").strip()
    invocation = f"/plan-work {project} target app slug {SLUG} — {scope}"
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
        return (f"You are resuming a Claude Code skill invocation right after a context "
                f"compaction. Act exactly as a session in that state would.\n\nWhat you hold of "
                f"the skill: the file {cut} is the text of the `/plan-work` skill that Claude Code "
                f"re-attached after compaction — truncated, as Claude Code does. Read it first. It "
                f"is all of the skill you remember. Read other files only where that text tells you "
                f"to, or where the work itself plainly needs it; do not go looking for a fuller "
                f"copy of the skill unless that text tells you to. {root} {inline}\n\nCompaction "
                f"summary of the session so far: the user invoked `{invocation}` (session language "
                f"pt-BR). Done before compaction: inputs present; `project.py` resolved "
                f"specification_root `spec`, target `app`, work_root `work` and standard "
                f"`app/standard.yaml`; `spec.py` was clean; the tree check printed nothing; step 1 "
                f"ran `spec.py --digest` and `spec.py --impact` over the four lending rules the "
                f"scope names (grepped for: loan, due, renew, reservation) and `deliver.py "
                f"--standard … --against`, which found nothing absent; steps 2-4 ran inline after "
                f"each spawn failed: the scope is under `work/{SLUG}/intake/scope.md`, the "
                f"inventory, the epic `epic/renewals` and the tasks `task/renewals/compute-due-date` "
                f"and `task/renewals/renew-loan` are written, every binder returned no note, and "
                f"`plan.py --node` passed on each task. Continue the invocation from where it "
                f"stands to its end.\n\nYou cannot ask the user anything. {keep}")
    return (f"Execute this task by following a skill file exactly as if the user had invoked "
            f"it.\n\n- Skill: read {skill} and follow it. {root} Read only what the skill tells "
            f"you to read. {inline}\n- The user's invocation (session language pt-BR): "
            f"`{invocation}`\n- You cannot ask the user anything; where the skill says stop, stop "
            f"and report. {keep}")


def plan_nodes(work: Path, kind: str) -> list[Path]:
    return sorted((work / kind).rglob("*.md")) if (work / kind).is_dir() else []


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
    work = record / "work" / SLUG
    report = (record / "report.md").read_text(encoding="utf-8") if (record / "report.md").exists() else ""
    commands = (record / "commands.txt").read_text(encoding="utf-8") if (record / "commands.txt").exists() else ""
    facts = json.loads((record / "facts.json").read_text(encoding="utf-8")) if (record / "facts.json").exists() else {}
    for check in c["checks"]:
        kind, _, arg = check.partition(":")
        if kind == "plan_sound":
            with tempfile.TemporaryDirectory() as tmp:
                copy = Path(tmp)
                if work.is_dir():
                    shutil.copytree(work, copy / "work")
                shutil.copytree(record / "spec" if (record / "spec").is_dir() else FIXTURE / "spec",
                                copy / "spec")
                code, said = (bin_run(PLUGIN / "bin/plan.py", "--check", copy / "work", copy / "spec")
                              if (copy / "work/plan.json").is_file() else (1, "no plan.json"))
            out.append(("mechanical: plan.py --check over the recorded plan exits 0", code == 0,
                        said.splitlines()[0] if said else ""))
        elif kind == "tasks_written":
            tasks = plan_nodes(work, "task")
            bound = [t for t in tasks if front(t).get("implements") or front(t).get("rationale")]
            out.append(("mechanical: the plan holds tasks, each implementing a node or saying why",
                        bool(tasks) and len(bound) == len(tasks), f"{len(bound)}/{len(tasks)}"))
        elif kind == "scope_covered":
            covered = {n for e in plan_nodes(work, "epic") for n in front(e).get("covers") or []}
            missing = [n for n in SCOPE_NODES if n not in covered]
            out.append(("mechanical: every rule the scope names is covered by an epic", not missing,
                        f"missing {missing}" if missing else f"{len(covered)} covered"))
        elif kind == "inventory_written":
            held = plan_nodes(work, "inventory")
            out.append(("mechanical: an inventory node is written", bool(held), str(len(held))))
        elif kind == "intake_holds_scope":
            files = sorted((work / "intake").rglob("*")) if (work / "intake").is_dir() else []
            ok = any(f.is_file() and "renew" in f.read_text(encoding="utf-8").lower() for f in files)
            out.append(("mechanical: the scope is persisted under intake/", ok, str(len(files))))
        elif kind == "handoff_saved":
            saved = record / "handoff.md"
            ok = saved.exists() and bool(saved.read_text(encoding="utf-8").strip())
            out.append(("mechanical: the report was saved through handoff.py --save-report", ok,
                        "handoff.md" if saved.exists() else "nothing under .git/siegard/handoff/"))
        elif kind == "report_hands":
            out.append((f"mechanical: the report hands {arg}", arg in report, arg if arg in report else ""))
        elif kind == "report_offers_outstanding":
            ok = "deliver.py --outstanding" in report
            out.append(("mechanical: the handoff offers deliver.py --outstanding for the task slot",
                        ok, "present" if ok else ""))
        elif kind == "no_commit":
            out.append(("reported: the run made no commit", facts.get("commits_added") == 0,
                        f"commits added: {facts.get('commits_added')}"))
        elif kind == "writes_only_its_roots":
            stray = facts.get("changed_outside_roots", [])
            out.append(("reported: the run wrote nothing outside the work root and the specification",
                        not stray and "changed_outside_roots" in facts, f"outside: {stray}"))
        elif kind == "reported":
            hit = re.search(COMMANDS[arg], commands)
            out.append((f"reported: commands.txt shows {COMMANDS[arg]}", bool(hit),
                        hit.group(0)[:200] if hit else ""))
        else:
            raise SystemExit(f"cannot run: {name} names an unknown check {check!r}")
    return [{"text": t, "passed": bool(p), "evidence": e} for t, p, e in out]


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
        if (project / "work" / SLUG).is_dir():
            shutil.copytree(project / "work" / SLUG, dest / "work" / SLUG, ignore=CACHES)
        shutil.copytree(project / "spec", dest / "spec", ignore=CACHES)
        saved = sorted((project / ".git/siegard/handoff").glob("*.md")) \
            if (project / ".git/siegard/handoff").is_dir() else []
        if saved:
            shutil.copy(saved[-1], dest / "handoff.md")
        status = git(project, "status", "--porcelain", "--untracked-files=all")
        changed = [line[3:] for line in status.splitlines()]
        facts = {"commits_added": int(git(project, "rev-list", "--count", "HEAD").strip()) - 1,
                 "changed_outside_roots": sorted(p for p in changed
                                                 if not p.startswith(("work/", "spec/")))}
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
