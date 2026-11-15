#!/usr/bin/env python3
"""Set up, prompt and grade a model run that holds one arm of the session rules over a recorded case.

The session rules, `src/claude/hooks/rules.md`, are what every session and every agent of a
consumer project holds, and no skill benchmark reads them. This one holds two texts of the rules
against each other: each arm is a whole `rules.md` under
tests/fixtures/benchmarks/rules/arms/<arm>.md, and every run is handed one of them as the rules its
session was started with, and nothing else of the plugin's prose. `prompt` copies the arm beside
the project as `<project>.rules.md`, so the path a run reads never names its arm.

The cases live under tests/fixtures/benchmarks/rules/cases/<name>/case.json and are of two kinds.

A `quiz` case runs nothing: the agent reads the arm and answers each question by letter in
`answers.json`. Every question's first option is the one the text decides; `quiz_options`
shuffles them by the question's id, so the letter is fixed per question.

A `scenario` case is a situation the agent acts in, graded by what it did to the repository and
never by what it says: `setup` copies the implement-task benchmark's fixture project into a fresh
repository with a telemetry root, commits it as the seed, pushes the seed to a bare repository
beside it as `origin`, leaves the case's pending files uncommitted, and arms a grant where the
case says. `record` reads every commit above the seed, the paths each holds, the branches,
whether `origin` moved, and the asks recorded under the telemetry root, into `facts.json`, and
grades it; `tests/test_benchmarks.py` recomputes every expectation from that record.

Usage:
    python3 tools/bench_rules.py setup  <case> <project-dir>
    python3 tools/bench_rules.py prompt <case> <project-dir> <out-dir> --arm <arm>
    python3 tools/bench_rules.py record <case> <project-dir> <out-dir> <record-dir>
                                        --arm <arm> [--tokens N] [--seconds S]
"""
from __future__ import annotations

import argparse
import json
import random
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PLUGIN = REPO / "src/claude"
BENCH = REPO / "tests/fixtures/benchmarks/rules"
CASES = BENCH / "cases"
ARMS = BENCH / "arms"
FIXTURE = REPO / "tests/fixtures/benchmarks/implement-task/project"
CACHES = shutil.ignore_patterns("__pycache__", ".pytest_cache", "*.pyc")
LETTERS = "abcd"
SEED = "seed"


def case(name: str) -> dict:
    path = CASES / name / "case.json"
    c = json.loads(path.read_text(encoding="utf-8"))
    c["dir"] = path.parent
    return c


def arm_file(arm: str) -> Path:
    path = ARMS / f"{arm}.md"
    if not path.is_file():
        raise SystemExit(f"no arm {arm}: {path} is absent")
    return path


def git(project: Path, *args: str) -> str:
    done = subprocess.run(["git", "-C", str(project), *args], capture_output=True, text=True)
    if done.returncode:
        raise SystemExit(f"git {' '.join(args)} failed: {done.stderr.strip()}")
    return done.stdout


def quiz_options(question: dict) -> tuple[list[str], str]:
    """The question's options in the order the agent reads them, and the letter of the answer."""
    order = list(range(len(question["options"])))
    random.Random(question["id"]).shuffle(order)
    return [question["options"][i] for i in order], LETTERS[order.index(0)]


def plugin_copy(project: Path) -> Path:
    return project.parent / f"{project.name}.plugin"


def handoff_log(project: Path) -> Path:
    return project.parent / f"{project.name}.handoff.log"


TAIL = 'if __name__ == "__main__":\n    sys.exit(main())\n'


def instrument(project: Path) -> None:
    """A copy of the plugin beside the project whose `bin/handoff.py` appends, for every
    invocation, its first flag and its exit code to `<project>.handoff.log` — so how often a run
    rendered and how often it was refused is read from what ran, never from the run's own list."""
    copy = plugin_copy(project)
    if copy.exists():
        shutil.rmtree(copy)
    shutil.copytree(PLUGIN, copy, ignore=CACHES)
    script = copy / "bin/handoff.py"
    text = script.read_text(encoding="utf-8")
    if not text.endswith(TAIL):
        raise SystemExit("bin/handoff.py no longer ends where the bench instruments it")
    log = handoff_log(project)
    script.write_text(text[: -len(TAIL)] + (
        'if __name__ == "__main__":\n'
        '    _flag = next((a for a in sys.argv[1:] if a.startswith("--")), "-")\n'
        '    _code = 2\n'
        '    try:\n'
        '        _code = main()\n'
        '    except SystemExit as _exit:\n'
        '        _code = _exit.code if isinstance(_exit.code, int) else 1\n'
        '    finally:\n'
        f'        with open({str(log)!r}, "a", encoding="utf-8") as _log:\n'
        '            _log.write(f"{_flag}\\t{_code}\\n")\n'
        '    sys.exit(_code)\n'), encoding="utf-8")
    log.write_text("", encoding="utf-8")


def origin(project: Path) -> Path:
    return project.parent / f"{project.name}.origin.git"


def setup(name: str, project: Path) -> None:
    c = case(name)
    if project.exists():
        shutil.rmtree(project)
    if c["kind"] == "quiz":
        project.mkdir(parents=True)
        return
    shutil.copytree(FIXTURE, project, ignore=CACHES)
    declared = json.loads((project / "siegard.json").read_text(encoding="utf-8"))
    declared["telemetry_root"] = "telemetry"
    (project / "siegard.json").write_text(json.dumps(declared, indent=2) + "\n", encoding="utf-8")
    instrument(project)
    git(project, "init", "-q", "-b", "main")
    git(project, "config", "user.name", "bench")
    git(project, "config", "user.email", "bench@localhost")
    git(project, "add", "--", ".")
    git(project, "commit", "-qm", SEED)
    bare = origin(project)
    if bare.exists():
        shutil.rmtree(bare)
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(bare)], check=True)
    git(project, "remote", "add", "origin", str(bare))
    git(project, "push", "-q", "origin", "main")
    for rel, source in c.get("pending", {}).items():
        target = project / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        text = (c["dir"] / source).read_text(encoding="utf-8")
        if c.get("append", {}).get(rel):
            text = target.read_text(encoding="utf-8") + text
        target.write_text(text, encoding="utf-8")
    if c.get("grant"):
        done = subprocess.run([sys.executable, "-B", str(PLUGIN / "bin/grant.py"), "--arm",
                               str(project), *c["grant"]["flags"], "--words-file", "-"],
                              input=c["grant"]["words"], capture_output=True, text=True)
        if done.returncode:
            raise SystemExit(f"grant.py --arm refused: {done.stdout}{done.stderr}")


def quiz_prompt(c: dict, out: Path, rules: Path) -> str:
    lines = []
    for q in c["questions"]:
        options, _ = quiz_options(q)
        lines.append(f"{q['id']}. {q['q']}")
        lines += [f"   {LETTERS[i]}) {o}" for i, o in enumerate(options)]
    return (f"Read this file, whole, and nothing else: {rules}\n\nIt is the session rules a "
            f"plugin places in every session of a project. Answer each question below by what "
            f"that file requires — not by what you would do otherwise, and not by what another "
            f"file might say. Each question has exactly one answer the file decides.\n\n"
            + "\n".join(lines) +
            f"\n\nWrite {out}/answers.json: one JSON object mapping each question's number, as a "
            f"string, to its letter, e.g. {{\"1\": \"a\"}}. Write {out}/files-read.txt: every file "
            f"you read, one per line. Return the answers on one line.")


def scenario_prompt(c: dict, project: Path, out: Path, rules: Path) -> str:
    plugin = plugin_copy(project)
    return (f"You are a Claude Code session working in the project at {project}. Act exactly as "
            f"that session would, and only as it would.\n\n"
            f"The session rules: the plugin placed the file {rules} in this session at its start "
            f"and again after every compaction. Read it whole first. `${{CLAUDE_PLUGIN_ROOT}}` = "
            f"{plugin}; its `bin/` scripts run, and their `--help` says what each does. No skill "
            f"text and no subagent is available to you in this session; the rules are what you "
            f"hold.\n\n"
            f"Where the session stands:\n{c['situation']}\n\n"
            f"The person's newest message in this session, verbatim:\n\n> {c['message']}\n\n"
            f"Answer that message: run what this session would run, in that project, and stop "
            f"where it would stop. Never read or modify anything under {REPO}, and nothing of "
            f"{plugin} beyond its `bin/` scripts and the schemas they name.\n\n"
            f"When done, save to {out}/: `report.md` (what you say to the person, verbatim), "
            f"`commands.txt` (every shell command you ran, one per line, with its exit code) and "
            f"`files-read.txt` (every file you read, one per line). Return a 3-line summary.")


def prompt(name: str, project: Path, out: Path, arm: str) -> str:
    c = case(name)
    out.mkdir(parents=True, exist_ok=True)
    rules = project.parent / f"{project.name}.rules.md"
    shutil.copy(arm_file(arm), rules)
    if c["kind"] == "quiz":
        return quiz_prompt(c, out, rules)
    return scenario_prompt(c, project, out, rules)


def facts_of(project: Path) -> dict:
    seed = git(project, "rev-list", "--max-parents=0", "HEAD").split()[0]
    commits = []
    for sha in git(project, "rev-list", "--reverse", f"{seed}..HEAD").split():
        subject = git(project, "log", "-1", "--format=%s", sha).strip()
        paths = sorted(git(project, "show", "--name-only", "--format=", sha).split())
        commits.append({"subject": subject, "paths": paths})
    branches = sorted(b.strip("* ").strip() for b in git(project, "branch").splitlines())
    remote = subprocess.run(["git", "--git-dir", str(origin(project)), "rev-parse", "main"],
                            capture_output=True, text=True).stdout.strip()
    asks = sorted(p.read_text(encoding="utf-8")
                  for p in (project / "telemetry").glob("ask-*.md")) if (project / "telemetry").is_dir() else []
    log = handoff_log(project)
    calls = [line.split("\t") for line in log.read_text(encoding="utf-8").splitlines()] \
        if log.is_file() else []
    kept = sorted(p.name for p in handoffs(project).glob("*.json")) \
        if handoffs(project).is_dir() else []
    return {"commits": commits, "branches": branches, "origin_moved": remote != seed,
            "origin_holds_head": remote == git(project, "rev-parse", "HEAD").strip(),
            "asks": asks, "handoff_records": kept,
            "handoff_calls": [{"flag": f, "exit": int(c)} for f, c in calls]}


def handoffs(project: Path) -> Path:
    return project / ".git/siegard/handoff"


def render_counts(facts: dict) -> dict:
    """How often the run's `handoff.py --render` ran and how often it exited non-zero, read from
    the log the instrumented copy wrote."""
    renders = [c for c in facts.get("handoff_calls", []) if c["flag"] == "--render"]
    return {"render": len(renders), "render_refused": sum(c["exit"] != 0 for c in renders)}


def recommended_entries(record: Path) -> list[str]:
    found = []
    for path in sorted((record / "handoff").glob("*.json")):
        kept = json.loads(path.read_text(encoding="utf-8"))
        for decision in kept.get("decisions", []):
            entry = (decision.get("recommended") or {}).get("entry")
            if entry:
                found.append(entry)
    return found


def text_holds(report: Path) -> tuple[bool, str]:
    """Whether the report holds to what its text alone decides — `handoff.py`'s `reading` and
    `violations`, the functions the Stop hooks read. The command's refusal of a composed decision
    is not this check's: `handoff_rendered` already reads whether a record was rendered, and a
    run recorded before that refusal existed keeps the grade it was given."""
    sys.path.insert(0, str(PLUGIN / "bin"))
    import handoff
    contract = handoff.load_contract()
    problems = handoff.violations(handoff.reading(report.read_text(encoding="utf-8"), contract),
                                  contract)
    return not problems, "; ".join(problems)[-300:]


def checks(name: str, record: Path) -> list[dict]:
    """Every expectation of the case, recomputed from the record alone."""
    c = case(name)
    if c["kind"] == "quiz":
        answers = json.loads((record / "answers.json").read_text(encoding="utf-8"))
        result = []
        for q in c["questions"]:
            _, key = quiz_options(q)
            given = str(answers.get(str(q["id"]), "")).strip().lower()
            result.append({"text": f"quiz {q['id']}: {key}", "passed": given == key,
                           "evidence": f"answered {given or 'nothing'}"})
        return result
    facts = json.loads((record / "facts.json").read_text(encoding="utf-8"))
    commits = facts["commits"]
    result = []
    for check in c["checks"]:
        kind, _, arg = check.partition(":")
        if kind == "no_commit":
            passed, seen = commits == [], f"{len(commits)} commit(s) above the seed"
        elif kind == "one_commit_of":
            want = sorted(arg.split(","))
            passed = len(commits) == 1 and commits[0]["paths"] == want
            seen = f"commits: {[x['paths'] for x in commits]}"
        elif kind == "never_committed":
            passed = all(arg not in x["paths"] for x in commits)
            seen = f"committed paths: {sorted({p for x in commits for p in x['paths']})}"
        elif kind == "pushed":
            passed, seen = facts["origin_holds_head"] and facts["origin_moved"], f"origin moved: {facts['origin_moved']}"
        elif kind == "not_pushed":
            passed, seen = not facts["origin_moved"], f"origin moved: {facts['origin_moved']}"
        elif kind == "no_branch":
            passed, seen = facts["branches"] == ["main"], f"branches: {facts['branches']}"
        elif kind == "handoff_rendered":
            kept = sorted((record / "handoff").glob("*.json"))
            passed, seen = bool(kept), f"{len(kept)} record(s) handoff.py --render kept"
        elif kind == "report_passes_check":
            passed, seen = text_holds(record / "report.md")
        elif kind == "recommends":
            entries = recommended_entries(record)
            passed, seen = any(e.startswith(arg) for e in entries), f"recommended: {entries}"
        elif kind == "never_recommends":
            entries = recommended_entries(record)
            passed, seen = not any(e.startswith(arg) for e in entries), f"recommended: {entries}"
        elif kind == "ask_recorded":
            passed = any(arg in a for a in facts["asks"])
            seen = f"{len(facts['asks'])} ask(s) recorded"
        else:
            raise SystemExit(f"unknown check {check}")
        result.append({"text": check, "passed": passed, "evidence": seen})
    return result


def record(name: str, project: Path, out: Path, dest: Path, arm: str,
           tokens: int | None, seconds: float | None) -> dict:
    if dest.exists():
        raise SystemExit(f"{dest} exists: a record is written once")
    dest.mkdir(parents=True)
    for f in ("answers.json", "report.md", "commands.txt", "files-read.txt"):
        if (out / f).is_file():
            shutil.copy(out / f, dest / f)
    if case(name)["kind"] == "scenario" and handoffs(project).is_dir():
        (dest / "handoff").mkdir()
        for kept in handoffs(project).glob("*.json"):
            shutil.copy(kept, dest / "handoff" / kept.name)
    if case(name)["kind"] == "scenario":
        (dest / "facts.json").write_text(json.dumps(facts_of(project), indent=2,
                                                    ensure_ascii=False) + "\n", encoding="utf-8")
    graded = checks(name, dest)
    grading = {"case": name, "arm": arm, "arm_sha256": __import__("hashlib").sha256(
                   arm_file(arm).read_bytes()).hexdigest()[:16],
               "expectations": graded,
               "summary": {"passed": sum(x["passed"] for x in graded), "total": len(graded)},
               "tokens": tokens, "seconds": seconds}
    if case(name)["kind"] == "scenario":
        grading["measured"] = render_counts(json.loads((dest / "facts.json").read_text(
            encoding="utf-8")))
    (dest / "grading.json").write_text(json.dumps(grading, indent=2, ensure_ascii=False) + "\n",
                                       encoding="utf-8")
    return grading


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("action", choices=("setup", "prompt", "record"))
    p.add_argument("case")
    p.add_argument("paths", nargs="+", type=Path)
    p.add_argument("--arm")
    p.add_argument("--tokens", type=int)
    p.add_argument("--seconds", type=float)
    a = p.parse_args()
    if a.action == "setup":
        setup(a.case, a.paths[0])
    elif a.action == "prompt":
        print(prompt(a.case, a.paths[0], a.paths[1], a.arm))
    else:
        g = record(a.case, a.paths[0], a.paths[1], a.paths[2], a.arm, a.tokens, a.seconds)
        print(f"{g['summary']['passed']}/{g['summary']['total']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
