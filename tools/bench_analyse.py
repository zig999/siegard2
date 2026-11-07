#!/usr/bin/env python3
"""Set up, prompt and grade a model run of `/analyse` over a recorded benchmark case.

The cases live under tests/fixtures/benchmarks/analyse/cases/<name>/case.json. A run is a model
run recorded once: `setup` builds the case's project, `prompt` prints what the running agent is
handed, and `record` copies what the run left into an iteration directory and grades it.
`tests/test_benchmarks.py` recomputes every `mechanical:` expectation from the record with the
same `checks` this module defines, so a grading is never trusted, only re-read; a `reported:`
expectation rests on what the agent wrote in `commands.txt` and is recorded, not recomputed.

Usage:
    python3 tools/bench_analyse.py setup  <case> <project-dir> [--skill <SKILL.md>]
    python3 tools/bench_analyse.py prompt <case> <project-dir> <out-dir> [--skill <SKILL.md>]
    python3 tools/bench_analyse.py record <case> <project-dir> <out-dir> <record-dir>
                                          --arm <label> [--tokens N] [--seconds S]
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PLUGIN = REPO / "src/claude"
SKILL = PLUGIN / "skills/analyse/SKILL.md"
CASES = REPO / "tests/fixtures/benchmarks/analyse/cases"
OPEN_MARKER = re.compile(r"\bTODO\b|\bTBD\b|\?\?\?|^\s*\w+:\s*unknown\s*$", re.M)
PORTUGUESE_SLUG = re.compile(r"emprest|socio|livro|exemplar|reservas?\b|multa|prazo|caso|reabert")
NOT_A_FILE = re.compile(r"not a file|não como arquivo|não (?:era|foi|é) (?:um )?arquivo|"
                        r"na conversa", re.I)


def case(name: str) -> dict:
    data = json.loads((CASES / name / "case.json").read_text(encoding="utf-8"))
    data["dir"] = CASES / name
    return data


def git(project: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(project), *args], capture_output=True, text=True,
                          check=True).stdout


def bin_run(*args: str | Path) -> tuple[int, str]:
    done = subprocess.run([sys.executable, "-B", *map(str, args)], capture_output=True, text=True)
    return done.returncode, (done.stdout + done.stderr).strip()


def setup(name: str, project: Path, skill: Path) -> None:
    """The case's project: `siegard.json`, the material under `docs/`, the seed specification,
    one commit — and, for a resumed case, the seed left uncommitted and the skill cut where a
    compaction re-attaches it."""
    c = case(name)
    if project.exists():
        shutil.rmtree(project)
    (project / "docs").mkdir(parents=True)
    git(project, "init", "-q")
    (project / "siegard.json").write_text(
        json.dumps({"targets": {"app": "."}, "specification_root": "spec"}) + "\n", encoding="utf-8")
    if c["material"]:
        shutil.copy(c["dir"] / c["material"], project / "docs/material.md")
    spec = project / "spec"
    seed = c.get("seed")
    committed = c.get("seed_committed", True)
    if seed and committed:
        shutil.copytree(REPO / seed if "/" in seed else c["dir"] / seed, spec)
    else:
        spec.mkdir()
        (spec / ".gitkeep").write_text("", encoding="utf-8")
    git(project, "add", "--", ".")
    git(project, "-c", "user.name=bench", "-c", "user.email=bench@localhost", "commit", "-qm", "seed")
    if seed and not committed:
        shutil.copytree(c["dir"] / seed, spec, dirs_exist_ok=True)
    if c.get("truncate_chars"):
        text = skill.read_text(encoding="utf-8")[: c["truncate_chars"]]
        (project.parent / f"{project.name}.skill-after-compaction.md").write_text(
            text[: text.rfind("\n")], encoding="utf-8")


def prompt(name: str, project: Path, out: Path, skill: Path) -> str:
    c = case(name)
    invocation = c["invocation"].format(project=project, conversation=c.get("conversation") or "")
    keep = ("Never commit or change git state. Do not modify anything under "
            f"{REPO}.\n\nWhen done, save to {out}/: `report.md` (the full report and the handoff "
            "you would hand the person, verbatim), `files-read.txt` (every file you read, in "
            "order, one per line) and `commands.txt` (every bin/*.py command you ran, one per "
            "line, with its exit code). Return a 5-line summary.")
    root = f"`${{CLAUDE_PLUGIN_ROOT}}` = {PLUGIN}."
    if c.get("resume_after_step"):
        cut = project.parent / f"{project.name}.skill-after-compaction.md"
        return (f"You are resuming a Claude Code skill invocation right after a context "
                f"compaction. Act exactly as a session in that state would.\n\nWhat you hold of "
                f"the skill: the file {cut} is the text of the `/analyse` skill that Claude Code "
                f"re-attached after compaction — truncated, as Claude Code does. Read it first. "
                f"It is all of the skill you remember. Read other files only where that text "
                f"tells you to, or where the work itself plainly needs it; do not go looking for "
                f"a fuller copy of the skill unless that text tells you to. {root}\n\nCompaction "
                f"summary of the session so far: the user invoked `{invocation}` (session "
                f"language pt-BR). Done before compaction: inputs present, `project.py` resolved "
                f"specification_root `spec`, the tree check printed nothing, the seven spec "
                f"schemas were read, the root was empty so situate was skipped, the analysis was "
                f"made and every node was written under `spec/` with its decision logs through "
                f"`spec.py --decide`; the last full `spec.py spec` run was sound. Continue the "
                f"invocation from where it stands to its end.\n\nYou cannot ask the user "
                f"anything. {keep}")
    return (f"Execute this task by following a skill file exactly as if the user had invoked "
            f"it.\n\n- Skill: read {skill} and follow it. {root} Read only what the skill tells "
            f"you to read.\n- The user's invocation (session language pt-BR): `{invocation}`\n"
            f"- You cannot ask the user anything; where the skill says stop, stop and report. "
            f"{keep}")


def checks(name: str, record: Path) -> list[dict]:
    """Every expectation of the case, recomputed from the record alone."""
    c = case(name)
    spec = record / "spec"
    report = (record / "report.md").read_text(encoding="utf-8") if (record / "report.md").exists() else ""
    commands = (record / "commands.txt").read_text(encoding="utf-8") if (record / "commands.txt").exists() else ""
    facts = json.loads((record / "facts.json").read_text(encoding="utf-8")) if (record / "facts.json").exists() else {}
    ledger = record / "docs/ledger.md"
    ledger_text = ledger.read_text(encoding="utf-8") if ledger.exists() else ""
    out: list[dict] = []

    def entry(line: int) -> str:
        return " | ".join(b for b in re.split(r"\n(?=- )", ledger_text) if f"material.md:{line}" in b)

    for check in c["checks"]:
        kind, _, arg = check.partition(":")
        if kind == "spec_sound":
            code, said = bin_run(PLUGIN / "bin/spec.py", spec)
            out.append(("mechanical: spec.py exits 0", code == 0, said.splitlines()[-1] if said else ""))
        elif kind == "no_open_marker":
            hits = [str(p.relative_to(record)) for p in spec.rglob("*.md")
                    if "projections" not in p.parts and OPEN_MARKER.search(p.read_text(encoding="utf-8"))]
            out.append(("mechanical: no node carries an open marker", not hits, ", ".join(hits) or "none"))
        elif kind == "identities_english":
            names = [p.relative_to(spec).as_posix() for p in spec.rglob("*.md") if "projections" not in p.parts]
            pt = [n for n in names if PORTUGUESE_SLUG.search(n)]
            out.append(("mechanical: every identity is English", bool(names) and not pt,
                        f"{len(names)} file(s); Portuguese: {pt}"))
        elif kind == "ledger_sound":
            code, said = bin_run(PLUGIN / "bin/trace.py", "--ledger", ledger, spec) if ledger.exists() else (1, "no docs/ledger.md")
            out.append(("mechanical: docs/ledger.md beside the material and trace.py --ledger exits 0",
                        code == 0, said.splitlines()[0] if said else ""))
        elif kind == "line_outside":
            e = entry(int(arg))
            out.append((f"mechanical: material line {arg} (the screen) is answered outside", "outside" in e, e[:300]))
        elif kind == "line_answered":
            e = entry(int(arg))
            out.append((f"mechanical: material line {arg} (the open question) has a ledger entry", bool(e), e[:300]))
        elif kind == "projections_written":
            held = sorted(p.name for p in (spec / "projections").glob("*")) if (spec / "projections").is_dir() else []
            out.append(("mechanical: spec.py --project wrote the projections", bool(held), ", ".join(held)))
        elif kind == "handoff_saved":
            saved = record / "handoff.md"
            out.append(("mechanical: the report was saved through handoff.py --save-report",
                        saved.exists() and bool(saved.read_text(encoding="utf-8").strip()),
                        "handoff.md" if saved.exists() else "nothing under .git/siegard/handoff/"))
        elif kind == "report_hands":
            out.append((f"mechanical: the report hands {arg}", arg in report, ""))
        elif kind == "report_says_not_a_file":
            m = NOT_A_FILE.search(report)
            out.append(("mechanical: the report says the material was not a file", bool(m), m.group(0) if m else ""))
        elif kind == "transition":
            src, dst = arg.split("->")
            sm = next(iter(spec.rglob("case-transitions.md"))).read_text(encoding="utf-8")
            ok = re.search(rf"from: {src}\n\s+trigger: \S+\n\s+to: {dst}", sm)
            out.append((f"mechanical: the state machine gains {src} -> {dst}", bool(ok), ok.group(0) if ok else ""))
        elif kind == "terminal":
            sm = next(iter(spec.rglob("case-transitions.md"))).read_text(encoding="utf-8")
            terminal = sm.split("terminal:", 1)[1].split("transitions:", 1)[0]
            leaves = re.search(rf"from: {arg}\n\s+trigger: \S+\n\s+to:", sm)
            out.append((f"mechanical: {arg} stays terminal with no transition out",
                        arg in terminal and not leaves, " ".join(terminal.split())))
        elif kind == "new_decisions":
            changed = facts.get("logs_changed", [])
            out.append(("reported: decision logs changed by the run", bool(changed), ", ".join(changed)))
        elif kind == "no_commit":
            out.append(("reported: the run made no commit", facts.get("commits_added") == 0,
                        f"commits added: {facts.get('commits_added')}"))
        elif kind == "reported":
            pattern = {"shape_of": r"--shape[^\n]*--of", "prepare_ledger": r"--prepare[^\n]*--ledger",
                       "render": r"--render"}[arg]
            hit = re.search(pattern, commands)
            out.append((f"reported: commands.txt shows {pattern}", bool(hit), hit.group(0)[:200] if hit else ""))
        else:
            raise SystemExit(f"cannot run: {name} names an unknown check {check!r}")
    return [{"text": t, "passed": bool(p), "evidence": e} for t, p, e in out]


def record(name: str, project: Path, out: Path, dest: Path, arm: str,
           tokens: int | None, seconds: float | None) -> dict:
    """Copy what the run left into `dest` and grade it there."""
    if dest.exists():
        raise SystemExit(f"cannot run: {dest} exists; a recorded run is never overwritten")
    dest.mkdir(parents=True)
    shutil.copytree(project / "spec", dest / "spec", ignore=shutil.ignore_patterns(".gitkeep"))
    if (project / "docs").is_dir():
        shutil.copytree(project / "docs", dest / "docs")
    for f in ("report.md", "files-read.txt", "commands.txt"):
        if (out / f).exists():
            shutil.copy(out / f, dest / f)
    saved = sorted((project / ".git/siegard/handoff").glob("*.md")) if (project / ".git/siegard/handoff").is_dir() else []
    if saved:
        shutil.copy(saved[-1], dest / "handoff.md")
    status = git(project, "status", "--porcelain", "--untracked-files=all", "--", "spec")
    facts = {"commits_added": int(git(project, "rev-list", "--count", "HEAD").strip()) - 1,
             "logs_changed": sorted(l[3:] for l in status.splitlines() if l.endswith(".log.md"))}
    (dest / "facts.json").write_text(json.dumps(facts, indent=1) + "\n", encoding="utf-8")
    code, said = bin_run(PLUGIN / "bin/spec.py", "--shape", dest / "spec")
    at = said.find("decided fields per node")
    (dest / "shape-decided.txt").write_text(said[at:said.find("\n\n", at)] + "\n" if at >= 0 else "",
                                            encoding="utf-8")
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
