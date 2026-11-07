#!/usr/bin/env python3
"""Set up, prompt and grade a model run of `/implement-task` over a recorded benchmark case.

The cases live under tests/fixtures/benchmarks/implement-task/cases/<name>/case.json, and every
case delivers the one task of the fixture project beside them, `project/`. A run is a model run
recorded once: `setup` copies the project into a fresh git repository, `prompt` prints what the
running agent is handed, and `record` copies what the run left into an iteration directory and
grades it. `tests/test_benchmarks.py` recomputes every `mechanical:` expectation from the record
with the same `checks` this module defines, so a grading is never trusted, only re-read; a
`reported:` expectation rests on what the agent wrote in `commands.txt`, or on `facts.json`
written when the run was recorded, and is recorded, not recomputed.

A `quiz` case runs nothing: the agent reads the skill, its references and its three agents, and
answers each question by letter in `answers.json`. Every question's first option is the one the
text decides; `quiz_options` shuffles them by the question's id, so the letter is fixed per
question and never the same position throughout.

A resumed case is a compaction: `setup` runs the skill's steps up to the one the case names
through the framework's own writers, and cuts the skill where Claude Code re-attaches it. Its
`facts.json` records whether the run's `files-read.txt` names the whole `SKILL.md` — the read the
checklist asks for past the cut.

Usage:
    python3 tools/bench_implement_task.py setup  <case> <project-dir> [--skill <SKILL.md>]
    python3 tools/bench_implement_task.py prompt <case> <project-dir> <out-dir> [--skill <SKILL.md>]
    python3 tools/bench_implement_task.py record <case> <project-dir> <out-dir> <record-dir>
                                                 --arm <label> [--tokens N] [--seconds S]
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PLUGIN = REPO / "src/claude"
SKILL = PLUGIN / "skills/implement-task/SKILL.md"
BENCH = REPO / "tests/fixtures/benchmarks/implement-task"
CASES = BENCH / "cases"
FIXTURE = BENCH / "project"
SLUG = "lending"
TASK = "task/fees/compute-late-fee"
NODE = "rules/lending/late-fee-per-overdue-day"
IMPLEMENTATION = f"delivery/{SLUG}/implementation/fees/compute-late-fee.md"
PROOF = f"delivery/{SLUG}/proof/fees/compute-late-fee.md"
BUILD_RUN = "fees-compute-late-fee-build"
SUITE_RUN = "fees-compute-late-fee-suite"
CACHES = shutil.ignore_patterns("__pycache__", ".pytest_cache", "*.pyc")
COMMANDS = {"write_implementation": r"--write-implementation", "write_proof": r"--write-proof",
            "unrecorded": r"--unrecorded", "bind_record": r"--bind-record", "render": r"--render"}


def case(name: str) -> dict:
    data = json.loads((CASES / name / "case.json").read_text(encoding="utf-8"))
    data["dir"] = CASES / name
    return data


def git(project: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(project), *args], capture_output=True, text=True,
                          check=True).stdout


def bin_run(*args: str | Path, cwd: Path | None = None) -> tuple[int, str]:
    done = subprocess.run([sys.executable, "-B", *map(str, args)], capture_output=True, text=True,
                          cwd=cwd)
    return done.returncode, (done.stdout + done.stderr).strip()


def front(path: Path) -> dict:
    import yaml
    text = path.read_text(encoding="utf-8")
    return yaml.safe_load(text.split("---", 2)[1]) if text.startswith("---") else {}


AGENTS = ("task-implementer", "test-author", "failure-diagnostician")
LETTERS = "abcd"


def quiz_options(question: dict) -> tuple[list[str], str]:
    """The question's options in the order the agent reads them, and the letter of the answer."""
    import random
    order = list(range(len(question["options"])))
    random.Random(question["id"]).shuffle(order)
    return [question["options"][i] for i in order], LETTERS[order.index(0)]


def setup(name: str, project: Path, skill: Path) -> None:
    """The fixture project, committed once; for a resumed case, the steps up to the one it names
    run through the framework's writers and left uncommitted, and the skill cut where a compaction
    re-attaches it."""
    c = case(name)
    if project.exists():
        shutil.rmtree(project)
    if c.get("kind") == "quiz":
        project.mkdir(parents=True)
        return
    shutil.copytree(FIXTURE, project, ignore=CACHES)
    git(project, "init", "-q")
    git(project, "add", "--", ".")
    git(project, "-c", "user.name=bench", "-c", "user.email=bench@localhost", "commit", "-qm", "seed")
    if c.get("resume_after_step"):
        (project / f"delivery/{SLUG}").mkdir(parents=True)
        shutil.copy(c["dir"] / "pre/fees.py", project / "app/lending/fees.py")
        code, said = bin_run(PLUGIN / "bin/run.py", project / f"delivery/{SLUG}", "--run", BUILD_RUN,
                             "--cwd", project / "app", "--excerpt", "40", "--timeout-seconds", "60",
                             "--step", "build=python3 -m compileall -q lending")
        assert code == 0, said
        code, said = bin_run(
            PLUGIN / "bin/deliver.py", "--write-implementation", project / f"delivery/{SLUG}", TASK,
            "--target", "app", "--task-file", project / f"work/{SLUG}/{TASK}.md",
            "--run", f"run/{BUILD_RUN}", "--standard", "standard.yaml",
            "--standard-file", project / "app/standard.yaml",
            "--from-text", c["dir"] / "pre/implementer-return.yaml")
        assert code == 0, said
        if c["resume_after_step"] >= 6:
            shutil.copy(c["dir"] / "pre/test_fees.py", project / "app/tests/test_fees.py")
            code, said = bin_run(PLUGIN / "bin/run.py", project / f"delivery/{SLUG}", "--run",
                                 SUITE_RUN, "--cwd", project / "app", "--excerpt", "40",
                                 "--timeout-seconds", "120",
                                 "--step", "build=python3 -m compileall -q lending",
                                 "--step", "test=python3 -m pytest -q tests")
            assert code == 0, said
            code, said = bin_run(
                PLUGIN / "bin/deliver.py", "--write-proof", project / f"delivery/{SLUG}", TASK,
                "--target", "app", "--run", f"run/{SUITE_RUN}", "--standard", "standard.yaml",
                "--standard-file", project / "app/standard.yaml",
                "--from-text", c["dir"] / "pre/test-author-return.yaml")
            assert code == 0, said
        for cache in project.rglob("__pycache__"):
            shutil.rmtree(cache)
        for cache in project.rglob(".pytest_cache"):
            shutil.rmtree(cache)
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
            f"of the `/implement-task` skill of a plugin, and of the three subagents it spawns. "
            f"Answer each question below by what those files require — not by what you would do "
            f"otherwise, and not by what another file might say. Each question has exactly one "
            f"answer the files decide.\n\n" + "\n".join(lines) +
            f"\n\nWrite {out}/answers.json: one JSON object mapping each question's number, as "
            f"a string, to its letter, e.g. {{\"1\": \"a\"}}. Write {out}/files-read.txt: every "
            f"file you read, one per line. Return the answers on one line.")


PAST_STEP_4 = (f" Prove ran inline: the tests are `app/tests/test_fees.py`, and they name "
               f"`{NODE}` on the test that demonstrates it. Suite: run `run/{SUITE_RUN}` passed, "
               f"build then test, on its first attempt. The proof record was written through "
               f"`deliver.py --write-proof` at `{PROOF}`. Steps 1-6 are closed.")


def read_again(record: Path) -> bool | None:
    """Whether the run's files-read.txt names the arm's SKILL.md, whole or in part — the file a
    resumed session reads again past the cut; None where the run left no list. A line may carry
    the run's own note after the path, as `SKILL.md (lines 340-end)`."""
    listed = record / "files-read.txt"
    if not listed.is_file():
        return None
    return any(line.split(" (", 1)[0].strip().endswith("skills/implement-task/SKILL.md")
               for line in listed.read_text(encoding="utf-8").splitlines())


def prompt(name: str, project: Path, out: Path, skill: Path) -> str:
    c = case(name)
    if c.get("kind") == "quiz":
        return quiz_prompt(c, out, skill)
    invocation = c["invocation"].format(project=project)
    keep = ("Never commit or change git state. Do not modify anything under "
            f"{REPO}.\n\nWhen done, save to {out}/: `report.md` (the full report and the handoff "
            "you would hand the person, verbatim), `files-read.txt` (every file you read, in "
            "order, one per line) and `commands.txt` (every bin/*.py command you ran, one per "
            "line, with its exit code). Return a 5-line summary.")
    root = f"`${{CLAUDE_PLUGIN_ROOT}}` = {skill.parent.parent.parent}."
    inline = ("This session cannot spawn subagents: where the skill delegates, apply the inline "
              "fallback the skill states.")
    if c.get("resume_after_step"):
        cut = project.parent / f"{project.name}.skill-after-compaction.md"
        return (f"You are resuming a Claude Code skill invocation right after a context "
                f"compaction. Act exactly as a session in that state would.\n\nWhat you hold of "
                f"the skill: the file {cut} is the text of the `/implement-task` skill that Claude "
                f"Code re-attached after compaction — truncated, as Claude Code does. Read it "
                f"first. It is all of the skill you remember. Read other files only where that "
                f"text tells you to, or where the work itself plainly needs it; do not go looking "
                f"for a fuller copy of the skill unless that text tells you to. {root} {inline}\n\n"
                f"Compaction summary of the session so far: the user invoked `{invocation}` "
                f"(session language pt-BR). Done before compaction: inputs present (target `app`, "
                f"slug `{SLUG}`, task `{TASK}`); `project.py` resolved specification_root `spec`, "
                f"work_root `work`, delivery_root `delivery` and standard `app/standard.yaml`; "
                f"`plan.py --check` was clean; the tree check printed nothing; the three contract "
                f"slices were printed; `--outstanding` listed the task as deliverable, with no "
                f"BLOCKING note and no record at its path; `deliver.py --standard` was clean and "
                f"printed the phases — setup: nothing runs; build: `--timeout-seconds 60 --step "
                f"'build=python3 -m compileall -q lending'`; suite: `--timeout-seconds 120 --step "
                f"'build=python3 -m compileall -q lending' --step 'test=python3 -m pytest -q "
                f"tests'`. Set up was skipped (no install). Implement ran inline: the source is "
                f"`app/lending/fees.py`. Build: run `run/{BUILD_RUN}` passed. The implementation "
                f"record was written through `deliver.py --write-implementation` at "
                f"`{IMPLEMENTATION}`." + (PAST_STEP_4 if c["resume_after_step"] >= 6 else "") +
                f" Continue the invocation from where it stands to its end."
                f"\n\nYou cannot ask the user anything. {keep}")
    return (f"Execute this task by following a skill file exactly as if the user had invoked "
            f"it.\n\n- Skill: read {skill} and follow it. {root} Read only what the skill tells "
            f"you to read. {inline}\n- The user's invocation (session language pt-BR): "
            f"`{invocation}`\n- You cannot ask the user anything; where the skill says stop, stop "
            f"and report. {keep}")


def recorded_paths(record: Path) -> set[str]:
    """Every path under the target the two records name, spelled from the target source root."""
    named: set[str] = set()
    for rel in (IMPLEMENTATION, PROOF):
        if (record / rel).is_file():
            data = front(record / rel)
            named |= {f["path"] for f in data.get("files") or []}
            named |= {t["file"] for t in data.get("tests") or []}
    return named


def checks(name: str, record: Path) -> list[dict]:
    """Every expectation of the case, recomputed from the record alone."""
    c = case(name)
    report = (record / "report.md").read_text(encoding="utf-8") if (record / "report.md").exists() else ""
    commands = (record / "commands.txt").read_text(encoding="utf-8") if (record / "commands.txt").exists() else ""
    facts = json.loads((record / "facts.json").read_text(encoding="utf-8")) if (record / "facts.json").exists() else {}
    proof = front(record / PROOF) if (record / PROOF).is_file() else {}
    out: list[tuple[str, bool, str]] = []
    if c.get("kind") == "quiz":
        answers = json.loads((record / "answers.json").read_text(encoding="utf-8")) \
            if (record / "answers.json").is_file() else {}
        for q in c["questions"]:
            _, key = quiz_options(q)
            given = str(answers.get(str(q["id"]), "")).strip().lower()
            out.append((f"mechanical: question {q['id']} is answered {key}", given == key,
                        f"answered {given or 'nothing'}"))
        return [{"text": t, "passed": bool(p), "evidence": e} for t, p, e in out]
    for check in c["checks"]:
        kind, _, arg = check.partition(":")
        if kind == "implementation_written":
            ok = (record / IMPLEMENTATION).is_file()
            out.append(("mechanical: the implementation record exists", ok, IMPLEMENTATION if ok else "absent"))
        elif kind == "proof_written":
            ok = (record / PROOF).is_file()
            out.append(("mechanical: the proof record exists", ok, PROOF if ok else "absent"))
        elif kind == "delivery_sound":
            with tempfile.TemporaryDirectory() as tmp:
                copy = Path(tmp)
                for part in ("delivery", "work", "app"):
                    if (record / part).is_dir():
                        shutil.copytree(record / part, copy / part)
                shutil.copytree(FIXTURE / "spec", copy / "spec")
                shutil.copy(FIXTURE / "siegard.json", copy / "siegard.json")
                git(copy, "init", "-q")
                code, said = (bin_run(PLUGIN / "bin/deliver.py", copy / f"delivery/{SLUG}",
                                      copy / f"work/{SLUG}", copy / "app", copy / "spec")
                              if (copy / f"delivery/{SLUG}").is_dir() else (1, "no delivery root"))
            out.append(("mechanical: deliver.py over the recorded delivery exits 0", code == 0,
                        said.splitlines()[0] if said else ""))
        elif kind == "delivery_derived":
            ok = (record / f"delivery/{SLUG}/delivery.json").is_file()
            out.append(("mechanical: deliver.py derived delivery.json at the delivery root", ok,
                        "delivery.json" if ok else "absent"))
        elif kind == "suite_passed":
            run = proof.get("run", "")
            data = record / f"delivery/{SLUG}" / run / "run.json"
            ran = json.loads(data.read_text(encoding="utf-8")) if run and data.is_file() else {}
            steps = [s["name"] for s in ran.get("steps", [])]
            ok = ran.get("outcome") == "passed" and "test" in steps
            out.append(("mechanical: the proof's run passed and ran the suite step", ok,
                        f"{run}: {ran.get('outcome')} {steps}" if ran else "no run the proof names"))
        elif kind == "trace_bound":
            trace = record / "siegard-trace.json"
            data = json.loads(trace.read_text(encoding="utf-8")) if trace.is_file() else {}
            files = [f["path"] for b in data.get("bindings", []) if b["node"] == NODE for f in b["files"]]
            ok = "app/lending/fees.py" in files
            out.append((f"mechanical: the trace binds {NODE} to app/lending/fees.py", ok,
                        ", ".join(files) or "no binding"))
        elif kind == "tests_written":
            tests = proof.get("tests") or []
            held = [t["file"] for t in tests if (record / "app" / t["file"]).is_file()]
            demonstrates = [t["name"] for t in tests if t.get("demonstrates") == NODE]
            ok = bool(held) and len(held) == len(tests)
            out.append(("mechanical: every test the proof names sits in the target", ok,
                        f"{len(held)}/{len(tests)} held; demonstrates {NODE}: {len(demonstrates)}"))
        elif kind == "existing_test_untouched":
            before = (FIXTURE / "app/tests/test_loans.py").read_text(encoding="utf-8")
            path = record / "app/tests/test_loans.py"
            ok = path.is_file() and path.read_text(encoding="utf-8") == before
            out.append(("mechanical: the test an earlier delivery wrote is unchanged", ok,
                        "identical" if ok else "changed or absent"))
        elif kind == "handoff_saved":
            saved = record / "handoff.md"
            ok = saved.exists() and bool(saved.read_text(encoding="utf-8").strip())
            out.append(("mechanical: the report was saved through handoff.py --save-report", ok,
                        "handoff.md" if saved.exists() else "nothing under .git/siegard/handoff/"))
        elif kind == "report_hands":
            out.append((f"mechanical: the report hands {arg}", arg in report, arg if arg in report else ""))
        elif kind == "every_change_recorded":
            changed = set(facts.get("changed_under_target", []))
            missing = sorted(changed - recorded_paths(record))
            out.append(("reported: every path the run changed under the target is named by a record",
                        bool(changed) and not missing, f"changed {sorted(changed)}; unnamed {missing}"))
        elif kind == "no_commit":
            out.append(("reported: the run made no commit", facts.get("commits_added") == 0,
                        f"commits added: {facts.get('commits_added')}"))
        elif kind == "reported":
            hit = re.search(COMMANDS[arg] + r"[^\n]*", commands)
            out.append((f"reported: commands.txt shows {COMMANDS[arg]}", bool(hit),
                        hit.group(0)[:200] if hit else ""))
        else:
            raise SystemExit(f"cannot run: {name} names an unknown check {check!r}")
    return [{"text": t, "passed": bool(p), "evidence": e} for t, p, e in out]


def record(name: str, project: Path, out: Path, dest: Path, arm: str,
           tokens: int | None, seconds: float | None) -> dict:
    """Copy what the run left into `dest` and grade it there."""
    if dest.exists():
        raise SystemExit(f"cannot run: {dest} exists; a recorded run is never overwritten")
    dest.mkdir(parents=True)
    if case(name).get("kind") == "quiz":
        for f in ("answers.json", "files-read.txt"):
            if (out / f).exists():
                shutil.copy(out / f, dest / f)
        grading = {"run": dest.name, "case": name, "arm": arm, "subagent_tokens": tokens,
                   "seconds": seconds, "expectations": checks(name, dest)}
        (dest / "grading.json").write_text(json.dumps(grading, indent=1, ensure_ascii=False) + "\n",
                                           encoding="utf-8")
        return grading
    for part in ("delivery", "work", "app"):
        if (project / part).is_dir():
            shutil.copytree(project / part, dest / part, ignore=CACHES)
    if (project / "siegard-trace.json").is_file():
        shutil.copy(project / "siegard-trace.json", dest / "siegard-trace.json")
    for f in ("report.md", "files-read.txt", "commands.txt"):
        if (out / f).exists():
            shutil.copy(out / f, dest / f)
    saved = sorted((project / ".git/siegard/handoff").glob("*.md")) if (project / ".git/siegard/handoff").is_dir() else []
    if saved:
        shutil.copy(saved[-1], dest / "handoff.md")
    status = git(project, "status", "--porcelain", "--untracked-files=all", "--", "app")
    changed = sorted(line[3:].removeprefix("app/") for line in status.splitlines()
                     if "__pycache__" not in line and ".pytest_cache" not in line)
    facts = {"commits_added": int(git(project, "rev-list", "--count", "HEAD").strip()) - 1,
             "changed_under_target": changed,
             "spec_changed": bool(git(project, "status", "--porcelain", "--", "spec").strip())}
    if case(name).get("resume_after_step"):
        facts["skill_read_again"] = read_again(dest)
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
