#!/usr/bin/env python3
"""Replay `backlog-decomposer` and `unstated-fact-decider` over a consumer's history, handed the
impact set as paths or as a pack.

The binder's replay (`tools/bench_binder_replay.py`) measures the one agent that reads a
candidate set per task; these two read the plan's impact set, the decomposer once per plan and the
decider once per fact. A case is frozen from git: the specification as it stood before the plan
(or before the decision), the scope, intake and inventory as the plan recorded them, and the impact
set as the union of the plan's epic claims — `covers` and `uncovered` — that the snapshot holds. A
decider case carries the fact as the decision log entry that later recorded it stated it under
`unstated`, and the node that entry belongs to, so a run can be read against what was decided.

Usage:
    python3 tools/bench_pack_agents.py freeze <consumer> <spec-commit> <plan-commit> <work-slug> <out>
                                       [--fact <log-path>@<entry-index> ...]
    python3 tools/bench_pack_agents.py run <out> --arm <label> --plugin-dir <dir> --inputs paths|pack
                                       --reps N [--parallel P]
    python3 tools/bench_pack_agents.py grade <out>
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import io
import json
import subprocess
import sys
import tarfile
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bench_binder_replay import load_run  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
SPEC_PY = REPO / "src/claude/bin/spec.py"
PLAN_PY = REPO / "src/claude/bin/plan.py"
SCHEMAS = REPO / "src/claude/schemas/spec"
AGENTS = {"decomposer": "siegard:backlog-decomposer", "decider": "siegard:unstated-fact-decider"}

DECOMPOSER = """Cut this development scope into epics and task skeletons.

The scope: read {scope}.
The impact set: {impact}
The inventory: read {inventory}.
The plan-node contract slices: read {epic_slice} (epic) and {task_slice} (task, without implements).

Return what your instructions define: the epics, complete, and the task skeletons without `implements`.
"""
DECIDER = """Decide this fact the specification does not state.

The fact: {fact}
The impact set: {impact}
The intake scope paths: {intake}
The specification schema paths: {schemas}

Return what your instructions define.
"""
IMPACT = {"paths": "file paths under the specification root, one per line, in {paths} (each node "
                   "followed by its decision log, `<slug>.log.md`, where one exists).",
          "pack": "read {pack} (`spec.py --pack` output: every node verbatim under its identity "
                  "and digest, and the decision log beside each listed by path at the end)."}


def git_tree(consumer: Path, commit: str, paths: list[str], dest: Path) -> None:
    archive = subprocess.run(["git", "-C", str(consumer), "archive", commit, *paths],
                             check=True, capture_output=True).stdout
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(dest, filter="data")


def front(text: str) -> dict:
    return yaml.safe_load(text.split("---", 2)[1]) or {}


def freeze(consumer: Path, spec_commit: str, plan_commit: str, slug: str, out: Path,
           facts: list[str]) -> None:
    project, inputs = out / "project", out / "inputs"
    project.mkdir(parents=True, exist_ok=True)
    inputs.mkdir(parents=True, exist_ok=True)
    git_tree(consumer, spec_commit, ["siegard.json", "siegard/specification"], project)
    git_tree(consumer, plan_commit, [f"siegard/work/{slug}"], inputs)
    work = inputs / "siegard/work" / slug
    spec = project / "siegard/specification"
    claimed: list[str] = []
    for epic in sorted((work / "epic").glob("*.md")):
        fm = front(epic.read_text(encoding="utf-8"))
        for node in [*(fm.get("covers") or []),
                     *[u["node"] if isinstance(u, dict) else u for u in fm.get("uncovered") or []]]:
            if node not in claimed:
                claimed.append(node)
    impact = [n for n in claimed if (spec / f"{n}.md").is_file()]
    lines = []
    for node in impact:
        lines.append(str(spec / f"{node}.md"))
        log = spec / f"{node}.log.md"
        if log.is_file():
            lines.append(str(log))
    (inputs / "impact_paths.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (inputs / "impact_pack.txt").write_text(subprocess.run(
        [sys.executable, "-B", str(SPEC_PY), "--pack", ",".join(impact), str(spec)],
        check=True, capture_output=True, text=True).stdout, encoding="utf-8")
    for name, args in (("epic_slice.json", ["--contract", "epic"]),
                       ("task_slice.json", ["--contract", "task", "--without", "implements"])):
        (inputs / name).write_text(subprocess.run([sys.executable, "-B", str(PLAN_PY), *args],
                                                  check=True, capture_output=True,
                                                  text=True).stdout, encoding="utf-8")
    cases = {"decomposer": {"agent": "decomposer"}}
    for given in facts:
        log_path, _, index = given.partition("@")
        text = subprocess.run(["git", "-C", str(consumer), "show", f"{plan_commit}:{log_path}"],
                              capture_output=True, text=True).stdout
        if not text:
            text = (consumer / log_path).read_text(encoding="utf-8")
        entry = (front(text).get("entries") or [])[int(index or 0)]
        node = log_path.removeprefix("siegard/specification/").removesuffix(".log.md")
        cases[f"decider__{Path(node).name}"] = {"agent": "decider", "fact": entry["unstated"],
                                                "decided_node": node,
                                                "decided": entry.get("decided")}
    intake = sorted(str(p) for p in (work / "intake").glob("*.md"))
    schemas = sorted(str(p) for p in SCHEMAS.glob("*.json"))
    for key, case in cases.items():
        for mode in ("paths", "pack"):
            impact_text = IMPACT[mode].format(paths=inputs / "impact_paths.txt",
                                              pack=inputs / "impact_pack.txt")
            if case["agent"] == "decomposer":
                prompt = DECOMPOSER.format(scope=work / "intake/scope.md", impact=impact_text,
                                           inventory=next((work / "inventory").glob("*.md")),
                                           epic_slice=inputs / "epic_slice.json",
                                           task_slice=inputs / "task_slice.json")
            else:
                prompt = DECIDER.format(fact=case["fact"], impact=impact_text,
                                        intake=", ".join(intake), schemas=", ".join(schemas))
            (inputs / f"prompt_{mode}_{key}.txt").write_text(prompt, encoding="utf-8")
    manifest = {"consumer": str(consumer), "spec_commit": spec_commit, "plan_commit": plan_commit,
                "impact": impact, "impact_missing": [n for n in claimed if n not in impact],
                "pack_lines": len((inputs / "impact_pack.txt").read_text().splitlines()),
                "cases": cases}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"froze {len(cases)} case(s); impact set {len(impact)} node(s), "
          f"{len(manifest['impact_missing'])} claimed nodes absent at {spec_commit}; "
          f"pack {manifest['pack_lines']} lines")


def run_one(out: Path, arm: str, key: str, agent: str, mode: str, rep: int, plugin: Path) -> str:
    dest = out / "runs" / arm / f"{key}--{rep}.jsonl"
    if dest.exists():
        return f"skip {dest.name}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    prompt = (out / "inputs" / f"prompt_{mode}_{key}.txt").read_text(encoding="utf-8")
    cmd = ["claude", "-p", "--agent", AGENTS[agent], "--plugin-dir", str(plugin),
           "--output-format", "stream-json", "--verbose", "--add-dir", str(out / "inputs"),
           "--add-dir", str(SCHEMAS), "--allowedTools", "Read", "Grep", "Glob",
           "--no-session-persistence"]
    proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                          cwd=out / "project", timeout=3600)
    if proc.returncode != 0:
        dest.with_suffix(".err").write_text(proc.stdout + proc.stderr, encoding="utf-8")
        return f"FAIL {dest.name}: exit {proc.returncode}"
    dest.write_text(proc.stdout, encoding="utf-8")
    return f"ok {dest.name}"


def run(out: Path, arm: str, plugin: Path, mode: str, reps: int, parallel: int) -> None:
    cases = json.loads((out / "manifest.json").read_text())["cases"]
    jobs = [(k, c["agent"], r) for r in range(1, reps + 1) for k, c in cases.items()]
    with cf.ThreadPoolExecutor(max_workers=parallel) as pool:
        for line in pool.map(lambda j: run_one(out, arm, j[0], j[1], mode, j[2], plugin), jobs):
            print(line, flush=True)


def grade(out: Path) -> None:
    manifest = json.loads((out / "manifest.json").read_text())
    spec = str(out / "project/siegard/specification")
    pack = str(out / "inputs/impact_pack.txt")
    total = manifest["pack_lines"]
    report = {}
    for arm_dir in sorted((out / "runs").iterdir()):
        for f in sorted(arm_dir.glob("*.jsonl")):
            data, reads = load_run(f)
            covered = {n for r in reads or [] if r["path"] == pack and not r["error"]
                       for n in r.get("lines") or [] if 1 <= n <= total}
            report.setdefault(arm_dir.name, {})[f.stem] = {
                "cost_usd": round(data.get("total_cost_usd") or 0, 3),
                "turns": data.get("num_turns"),
                "seconds": round((data.get("duration_ms") or 0) / 1000),
                "node_files_opened": sum(1 for r in reads or [] if (r["path"] or "").startswith(spec)
                                         and not r["path"].endswith(".log.md")),
                "logs_opened": sum(1 for r in reads or [] if (r["path"] or "").endswith(".log.md")),
                "pack_lines_read": f"{len(covered)}/{total}" if any(
                    r["path"] == pack for r in reads or []) else None,
                "result_head": (data.get("result") or "")[:400]}
    (out / "grade.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for arm, runs in report.items():
        for name, r in runs.items():
            print(arm, name, {k: v for k, v in r.items() if k != "result_head"})


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("freeze")
    for name in ("consumer", "spec_commit", "plan_commit", "slug", "out"):
        f.add_argument(name)
    f.add_argument("--fact", action="append", default=[])
    r = sub.add_parser("run")
    r.add_argument("out")
    r.add_argument("--arm", required=True)
    r.add_argument("--plugin-dir", required=True)
    r.add_argument("--inputs", choices=("paths", "pack"), required=True)
    r.add_argument("--reps", type=int, default=2)
    r.add_argument("--parallel", type=int, default=4)
    g = sub.add_parser("grade")
    g.add_argument("out")
    a = ap.parse_args()
    if a.cmd == "freeze":
        freeze(Path(a.consumer).resolve(), a.spec_commit, a.plan_commit, a.slug,
               Path(a.out).resolve(), a.fact)
    elif a.cmd == "run":
        run(Path(a.out).resolve(), a.arm, Path(a.plugin_dir).resolve(), a.inputs, a.reps,
            a.parallel)
    else:
        grade(Path(a.out).resolve())
    return 0


if __name__ == "__main__":
    sys.exit(main())
