#!/usr/bin/env python3
"""Set up, prompt and grade a model run of `/review-change` over a recorded benchmark case.

The cases live under tests/fixtures/benchmarks/review-change/cases/<name>/case.json and review
one delivery: the fixture project the implement-task benchmark delivers into
(tests/fixtures/benchmarks/implement-task/project/), with that benchmark's recorded first
delivery (iteration-2/first-delivery) laid over it and committed — its delivery root, its target,
its work root and the trace its bind wrote. `setup` builds that repository, `prompt` prints what
the running agent is handed, and `record` copies what the run left into an iteration directory
and grades it; `tests/test_benchmarks.py` recomputes every expectation from the record.

A resumed case is a compaction: `setup` runs the review through step 3b with the framework's own
writers — the staging, the captured run, the conformance returns the case's `pre/` holds saved
through `--save-return`, the fold and the bind — leaves it uncommitted, and cuts the skill where
Claude Code re-attaches it. A `quiz` case runs nothing, exactly as the implement-task
benchmark's.

Usage:
    python3 tools/bench_review_change.py setup  <case> <project-dir> [--skill <SKILL.md>]
    python3 tools/bench_review_change.py prompt <case> <project-dir> <out-dir> [--skill <SKILL.md>]
    python3 tools/bench_review_change.py record <case> <project-dir> <out-dir> <record-dir>
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
SKILL = PLUGIN / "skills/review-change/SKILL.md"
BENCH = REPO / "tests/fixtures/benchmarks/review-change"
CASES = BENCH / "cases"
FIXTURE = REPO / "tests/fixtures/benchmarks/implement-task/project"
DELIVERED = REPO / "tests/fixtures/benchmarks/implement-task/iteration-2/first-delivery"
SLUG = "lending"
TASK = "task/fees/compute-late-fee"
NODE = "rules/lending/late-fee-per-overdue-day"
REVIEW = "fees-review"
FILES = ("lending/fees.py", "tests/test_fees.py")
PROOF = f"delivery/{SLUG}/proof/fees/compute-late-fee.md"
RECONCILIATION = f"siegard-reconcile/{REVIEW}.md"
REVIEW_RECORD = f"delivery/{SLUG}/review/{REVIEW}.md"
AGENTS = ("coverage-auditor", "specification-conformance-reviewer",
          "standard-conformance-reviewer", "failure-diagnostician")
COMMANDS = {"stage": r"trace\.py[^\n]*--stage[^\n]*--review", "fold": r"trace\.py[^\n]*--fold",
            "bind_record": r"trace\.py[^\n]*--bind-record[^\n]*--workspace",
            "review": r"deliver\.py[^\n]*--review", "findings": r"deliver\.py[^\n]*--findings",
            "render": r"handoff\.py[^\n]*--render"}
OWN_ROOTS = ("delivery/", "siegard-reconcile/", "siegard-trace.json")


def case(name: str) -> dict:
    data = json.loads((CASES / name / "case.json").read_text(encoding="utf-8"))
    data["dir"] = CASES / name
    return data


def workspace_of(project: Path) -> Path:
    return project.parent / f"{project.name}.workspace"


def transcript_of(text: str, path: Path) -> Path:
    """A subagent transcript holding one final reply, the shape `--save-return` reads."""
    entry = {"type": "assistant", "message": {"role": "assistant",
                                              "content": [{"type": "text", "text": text}]}}
    path.write_text(json.dumps(entry) + "\n", encoding="utf-8")
    return path


def resume_after_fold(c: dict, project: Path) -> None:
    """Steps 1-3b through the framework's writers: staged, captured, returns saved, folded, bound."""
    bins, work = PLUGIN / "bin", workspace_of(project)
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    steps = [
        (bins / "trace.py", "--stage", "app", "spec", REVIEW, work, *FILES, "--review", "--node",
         NODE, "--demonstrated", PROOF),
        (bins / "run.py", f"delivery/{SLUG}", "--run", REVIEW, "--cwd", "app", "--timeout-seconds",
         "120", "--step", "build=python3 -m compileall -q lending", "--step",
         "test=python3 -m pytest -q tests")]
    for path in FILES:
        name = path.replace("/", "__")
        reply = (c["dir"] / "pre" / f"{name}.yaml").read_text(encoding="utf-8")
        steps.append((bins / "trace.py", "--save-return", "app", work, path,
                      transcript_of(reply, work / f"{name}.jsonl")))
    steps += [(bins / "trace.py", "--fold", "app", work, c["dir"] / "pre/premise.yaml",
               RECONCILIATION),
              (bins / "trace.py", "--reconciliation", RECONCILIATION),
              (bins / "trace.py", "--bind-record", "app", "spec", RECONCILIATION, "--workspace",
               work)]
    for step in steps:
        code, said = bin_run(*step, cwd=project)
        assert code == 0, f"{step[1]}: {said}"
    for cache in project.rglob("__pycache__"):
        shutil.rmtree(cache)
    shutil.rmtree(project / "app/.pytest_cache", ignore_errors=True)


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
    git(project, "add", "--", ".")
    git(project, "-c", "user.name=bench", "-c", "user.email=bench@localhost", "commit", "-qm", "seed")
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
            f"of the `/review-change` skill of a plugin, and of the four subagents it spawns. "
            f"Answer each question below by what those files require — not by what you would do "
            f"otherwise, and not by what another file might say. Each question has exactly one "
            f"answer the files decide.\n\n" + "\n".join(lines) +
            f"\n\nWrite {out}/answers.json: one JSON object mapping each question's number, as a "
            f"string, to its letter, e.g. {{\"1\": \"a\"}}. Write {out}/files-read.txt: every file "
            f"you read, one per line. Return the answers on one line.")


def invocation(project: Path) -> str:
    return (f"/review-change {project} tasks {TASK} files {' '.join(FILES)} target app slug "
            f"{SLUG} review {REVIEW}")


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
        passes = (c["dir"] / "pre/passes.md").read_text(encoding="utf-8").strip()
        return (f"You are resuming a Claude Code skill invocation right after a context "
                f"compaction. Act exactly as a session in that state would.\n\nWhat you hold of "
                f"the skill: the file {cut} is the text of the `/review-change` skill that Claude "
                f"Code re-attached after compaction — truncated, as Claude Code does. Read it "
                f"first. It is all of the skill you remember. Read other files only where that "
                f"text tells you to, or where the work itself plainly needs it; do not go looking "
                f"for a fuller copy of the skill unless that text tells you to. {root} {inline}"
                f"\n\nCompaction summary of the session so far: the user invoked "
                f"`{invocation(project)}` (session language pt-BR). Done before compaction: every "
                f"input present; `project.py` resolved specification_root `spec`, target `app`, "
                f"work_root `work`, delivery_root `delivery` and standard `app/standard.yaml` "
                f"(from siegard.json; the invocation named none); `plan.py --check` printed `plan "
                f"checked: work/lending/plan.json matches 3 node(s)` and `deliver.py --check` "
                f"printed `delivery checked: delivery/lending/delivery.json matches 2 node(s)`, "
                f"both exit 0; `git status --porcelain -- delivery/lending` printed nothing; the "
                f"three contract slices were printed. Step 1: the task's two criteria read from "
                f"`work/{SLUG}/{TASK}.md`; `deliver.py --standard app/standard.yaml --against app "
                f"--specification spec` was clean — PY-01 decided by reading, PY-02 by the tool "
                f"step `build`, steps build and test declared, nothing absent; the standard's pin "
                f"is `sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6`; "
                f"`trace.py --check app` printed `no drift: 1 binding(s) match the specification "
                f"and the code as both stand now`, no suppression receipt; `trace.py --stage "
                f"--review` into the workspace {work} staged 2 files over 1 node, one wave, no "
                f"certification (the proof's tests carry no `demonstrates`; its `untested` names "
                f"the node). Step 2: `run.py` captured `run/{REVIEW}` with the registry's steps "
                f"build and test, outcome passed. Step 3: every spawn failed, and the coverage, "
                f"conformance and standard passes ran inline; the failures pass did not run "
                f"because the run passed. The coverage and standard returns:\n\n{passes}\n\n"
                f"The conformance returns are saved under "
                f"`siegard-reconcile/{REVIEW}.returns/`. Step 3b: the premise was written, "
                f"`trace.py --fold` wrote `{RECONCILIATION}`, `trace.py --reconciliation` "
                f"accepted it, and `trace.py --bind-record … --workspace {work}` printed `bound "
                f"{NODE} to 1 file(s)`. Continue the invocation from where it stands to its end."
                f"\n\nYou cannot ask the user anything. {keep}")
    return (f"Execute this task by following a skill file exactly as if the user had invoked "
            f"it.\n\n- Skill: read {skill} and follow it. {root} Read only what the skill tells "
            f"you to read. {inline}\n- The user's invocation (session language pt-BR): "
            f"`{invocation(project)}`\n- You cannot ask the user anything; where the skill says "
            f"stop, stop and report. {keep}")


def sound_copy(record: Path, tmp: Path) -> Path:
    """The recorded tree laid over the fixture's specification, as a git repository."""
    for part in ("delivery", "work", "app", "siegard-reconcile"):
        if (record / part).is_dir():
            shutil.copytree(record / part, tmp / part)
    if (record / "siegard-trace.json").is_file():
        shutil.copy(record / "siegard-trace.json", tmp / "siegard-trace.json")
    shutil.copytree(FIXTURE / "spec", tmp / "spec")
    shutil.copy(FIXTURE / "siegard.json", tmp / "siegard.json")
    git(tmp, "init", "-q")
    return tmp


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
    review = front(record / REVIEW_RECORD) if (record / REVIEW_RECORD).is_file() else {}
    for check in c["checks"]:
        kind, _, arg = check.partition(":")
        if kind == "review_sound":
            with tempfile.TemporaryDirectory() as tmp:
                copy = sound_copy(record, Path(tmp))
                code, said = bin_run(PLUGIN / "bin/deliver.py", "--review", REVIEW,
                                     f"delivery/{SLUG}", f"work/{SLUG}", "app", "spec", cwd=copy) \
                    if (copy / REVIEW_RECORD).is_file() else (1, "no review record")
            out.append((f"mechanical: deliver.py --review {REVIEW} over the recorded delivery exits 0",
                        code == 0, said.splitlines()[-1] if said else ""))
        elif kind == "review_written":
            ok = (record / REVIEW_RECORD).is_file()
            out.append((f"mechanical: {REVIEW_RECORD} exists", ok, "present" if ok else "absent"))
        elif kind == "reconciliation_sound":
            with tempfile.TemporaryDirectory() as tmp:
                copy = sound_copy(record, Path(tmp))
                code, said = bin_run(PLUGIN / "bin/trace.py", "--reconciliation", RECONCILIATION,
                                     cwd=copy) if (copy / RECONCILIATION).is_file() \
                    else (1, f"no {RECONCILIATION}")
            out.append((f"mechanical: trace.py --reconciliation accepts {RECONCILIATION}",
                        code == 0, said.splitlines()[0] if said else ""))
        elif kind == "review_names_reconciliation":
            ok = review.get("reconciliation") == RECONCILIATION
            out.append((f"mechanical: the review record names {RECONCILIATION}", ok,
                        str(review.get("reconciliation"))))
        elif kind == "conformance_finding_recorded":
            hits = [f for f in review.get("findings") or [] if f.get("pass") == "conformance"
                    and f.get("kind") == "unstated" and f.get("file") == "lending/fees.py"]
            out.append(("mechanical: the review records the fold's unstated finding on "
                        "lending/fees.py, stamped conformance", bool(hits), str(len(hits))))
        elif kind == "run_captured":
            data = record / f"delivery/{SLUG}/run/{REVIEW}/run.json"
            ran = json.loads(data.read_text(encoding="utf-8")) if data.is_file() else {}
            steps = [s["name"] for s in ran.get("steps", [])]
            ok = ran.get("outcome") == "passed" and steps == ["build", "test"]
            out.append((f"mechanical: run/{REVIEW} ran the registry's build and test steps", ok,
                        f"{ran.get('outcome')} {steps}" if ran else "no run.json"))
        elif kind == "trace_bound":
            trace = record / "siegard-trace.json"
            data = json.loads(trace.read_text(encoding="utf-8")) if trace.is_file() else {}
            files = [f for b in data.get("bindings", []) if b["node"] == NODE for f in b["files"]
                     if f["path"] == "app/lending/fees.py"]
            ok = bool(files) and bool(files[0].get("judged"))
            out.append((f"mechanical: the trace binds {NODE} to app/lending/fees.py as judged", ok,
                        json.dumps(files[0])[:200] if files else "no binding"))
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
            out.append(("reported: the run wrote nothing outside the delivery root, "
                        "siegard-reconcile/ and siegard-trace.json",
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
        facts = {"commits_added": int(git(project, "rev-list", "--count", "HEAD").strip()) - 1,
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
