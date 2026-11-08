#!/usr/bin/env python3
"""Replay `execution-contract-binder` over frozen inputs from a consumer's delivered plan.

The binder is the specification's heaviest reader, and a change to the specification's format
is judged by whether the binder still names what it named before. Its own variance is the floor
any such judgment is read against: a format change whose divergence from the current format is
no larger than the current format's divergence from itself has changed nothing the binder
decides. This tool measures that floor and, later, the arms against it.

`freeze` copies a consumer's `siegard.json` and specification into a snapshot directory and
writes, per task, the four inputs `/plan-work` step 4 hands the binder: the skeleton (title,
summary, objective, criteria), the candidates (the epic's `covers` less its `uncovered`, each
node followed by its decision log where one exists), the binding slice (`plan.py --contract task
--fields implements`) and the prompt. `run` spawns the binder headless through `claude -p
--agent` with the plugin at `--plugin-dir`, once per task and repetition, and keeps each run's
JSON result. `grade` parses every run's `implements`, and reports per task the pairwise Jaccard
similarity between repetitions, the recorded `implements` of the delivered task, and tokens.

Usage:
    python3 tools/bench_binder_replay.py freeze <consumer-root> <work-slug> <out> --tasks <[slug:]epic/task,...>
    python3 tools/bench_binder_replay.py pack   <out>
    python3 tools/bench_binder_replay.py run    <out> --arm <label> --plugin-dir <dir> --reps N
                                                [--model M] [--parallel P] [--inputs paths|pack]
    python3 tools/bench_binder_replay.py grade  <out> [--arm <label>...]
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import itertools
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
PLAN_PY = REPO / "src/claude/bin/plan.py"
AGENT = "siegard:execution-contract-binder"
SKELETON_FIELDS = ("title", "summary", "objective", "criteria")
IDENTITY = re.compile(r"\b(?:constraints/[a-z0-9-]+|(?:domain|rules|scenarios|contracts)/[a-z0-9-]+/[a-z0-9-]+)\b")
PROMPT = """Decide which specification nodes govern this task and return its `implements`, with a classified note for every divergence.

Skeleton (title, summary, objective, criteria): read {skeleton} and use only those four fields.
Candidates: file paths, one per line, in {candidates} (each node followed by its .log.md where one exists; the decision log settles whether one rule replaced another).
Binding slice (the contract of the implements field): read {slice}.

Return the YAML your instructions define: `implements` and `notes`.
"""
PACK_PROMPT = """Decide which specification nodes govern this task and return its `implements`, with a classified note for every divergence.

Skeleton (title, summary, objective, criteria): read {skeleton} and use only those four fields.
Candidate pack: read {pack} (`spec.py --pack` output: every candidate node verbatim under its identity and digest, and the decision log beside each listed by path at the end).
Binding slice (the contract of the implements field): read {slice}.

Return the YAML your instructions define: `implements` and `notes`.
"""
SPEC_PY = REPO / "src/claude/bin/spec.py"


def front(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    return yaml.safe_load(text.split("---", 2)[1]) or {}


def tree_digest(root: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(root.rglob("*")):
        if p.is_file():
            h.update(str(p.relative_to(root)).encode())
            h.update(p.read_bytes())
    return h.hexdigest()


def freeze(consumer: Path, slug: str, out: Path, tasks: list[str]) -> None:
    project = out / "project"
    spec_src = consumer / "siegard/specification"
    if project.exists():
        shutil.rmtree(project)
    (project / "siegard").mkdir(parents=True)
    shutil.copy2(consumer / "siegard.json", project / "siegard.json")
    shutil.copytree(spec_src, project / "siegard/specification")
    spec = project / "siegard/specification"
    work = consumer / "siegard/work" / slug
    inputs = out / "inputs"
    inputs.mkdir(parents=True, exist_ok=True)
    slice_text = subprocess.run([sys.executable, "-B", str(PLAN_PY), "--contract", "task",
                                 "--fields", "implements"], check=True, capture_output=True,
                                text=True).stdout
    (inputs / "slice.json").write_text(slice_text, encoding="utf-8")
    manifest = {"consumer": str(consumer), "work_slug": slug,
                "specification_digest": tree_digest(spec), "tasks": {}}
    for name in tasks:
        plan_slug, _, name = name.rpartition(":")
        work = consumer / "siegard/work" / (plan_slug or slug)
        epic, task = name.split("/")
        tfm = front(work / "task" / epic / f"{task}.md")
        efm = front(work / "epic" / f"{epic}.md")
        uncovered = {u["node"] if isinstance(u, dict) else u for u in efm.get("uncovered") or []}
        claimed = [n for n in efm.get("covers") or [] if n not in uncovered]
        nodes = [n for n in claimed if (spec / f"{n}.md").is_file()]
        missing = [n for n in claimed if n not in nodes]
        lines = []
        for n in nodes:
            node = spec / f"{n}.md"
            lines.append(str(node))
            log = node.with_name(node.stem + ".log.md")
            if log.exists():
                lines.append(str(log))
        key = f"{epic}__{task}"
        skel = inputs / f"skel_{key}.yaml"
        skel.write_text(yaml.safe_dump({f: tfm[f] for f in SKELETON_FIELDS if f in tfm},
                                       sort_keys=False, allow_unicode=True), encoding="utf-8")
        cand = inputs / f"cand_{key}.txt"
        cand.write_text("\n".join(lines) + "\n", encoding="utf-8")
        prompt = PROMPT.format(skeleton=skel, candidates=cand, slice=inputs / "slice.json")
        (inputs / f"prompt_{key}.txt").write_text(prompt, encoding="utf-8")
        write_pack(inputs, spec, key, nodes, skel)
        manifest["tasks"][key] = {"plan": plan_slug or slug,
                                  "recorded_implements": sorted(tfm.get("implements") or []),
                                  "candidates": nodes,
                                  "missing_candidates": missing,
                                  "candidate_files": len(lines)}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"froze {len(tasks)} tasks; specification digest {manifest['specification_digest'][:12]}")


def write_pack(inputs: Path, spec: Path, key: str, nodes: list[str], skel: Path) -> None:
    """The candidate set as `spec.py --pack` prints it, and the prompt that hands it."""
    pack = inputs / f"pack_{key}.txt"
    pack.write_text(subprocess.run([sys.executable, "-B", str(SPEC_PY), "--pack", ",".join(nodes),
                                    str(spec)], check=True, capture_output=True,
                                   text=True).stdout, encoding="utf-8")
    (inputs / f"prompt_pack_{key}.txt").write_text(
        PACK_PROMPT.format(skeleton=skel, pack=pack, slice=inputs / "slice.json"),
        encoding="utf-8")


def pack_inputs(out: Path) -> None:
    """Write the pack inputs over an existing freeze, from the snapshot it already holds."""
    manifest = json.loads((out / "manifest.json").read_text())
    spec = out / "project/siegard/specification"
    for key, meta in manifest["tasks"].items():
        write_pack(out / "inputs", spec, key, meta["candidates"], out / "inputs" / f"skel_{key}.yaml")


def run_one(out: Path, arm: str, key: str, rep: int, plugin_dir: Path, model: str | None,
            inputs: str = "paths") -> str:
    dest = out / "runs" / arm / f"{key}--{rep}.jsonl"
    if dest.exists() or dest.with_suffix(".json").exists():
        return f"skip {dest.name}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    name = f"prompt_{key}.txt" if inputs == "paths" else f"prompt_pack_{key}.txt"
    prompt = (out / "inputs" / name).read_text(encoding="utf-8")
    cmd = ["claude", "-p", "--agent", AGENT, "--plugin-dir", str(plugin_dir),
           "--output-format", "stream-json", "--verbose", "--add-dir", str(out / "inputs"),
           "--allowedTools", "Read", "Grep", "Glob", "--no-session-persistence"]
    if model:
        cmd += ["--model", model]
    proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                          cwd=out / "project", timeout=1800)
    if proc.returncode != 0:
        (dest.with_suffix(".err")).write_text(proc.stdout + proc.stderr, encoding="utf-8")
        return f"FAIL {dest.name}: exit {proc.returncode}"
    dest.write_text(proc.stdout, encoding="utf-8")
    return f"ok {dest.name}"


def run(out: Path, arm: str, plugin_dir: Path, reps: int, model: str | None, parallel: int,
        inputs: str = "paths") -> None:
    keys = list(json.loads((out / "manifest.json").read_text())["tasks"])
    jobs = [(k, r) for r in range(1, reps + 1) for k in keys]
    with cf.ThreadPoolExecutor(max_workers=parallel) as pool:
        for line in pool.map(lambda j: run_one(out, arm, j[0], j[1], plugin_dir, model, inputs), jobs):
            print(line, flush=True)


def implements_of(result: str) -> set[str] | None:
    text = result.split("```yaml")[-1] if "```yaml" in result else result
    match = re.search(r"(?ms)^\s*implements:\s*\n(.*?)(?=^\S|^\s*notes:|\Z)", text)
    if not match:
        return None
    return set(IDENTITY.findall(match.group(1)))


def load_run(f: Path) -> tuple[dict, list[dict] | None]:
    """A run's result, and — where it was captured as a stream — every Read it made, with the
    file, the window asked for and whether the tool refused it."""
    if f.suffix == ".json":
        return json.loads(f.read_text()), None
    result: dict = {}
    calls: dict[str, dict] = {}
    for line in f.read_text().splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "result":
            result = event
        for block in (event.get("message") or {}).get("content") or []:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_use" and block.get("name") == "Read":
                given = block.get("input") or {}
                calls[block["id"]] = {"path": given.get("file_path"), "offset": given.get("offset"),
                                      "limit": given.get("limit"), "error": None}
            elif block.get("type") == "tool_result" and block.get("tool_use_id") in calls:
                content = block.get("content")
                text = content if isinstance(content, str) else "".join(
                    part.get("text", "") for part in content or [] if isinstance(part, dict))
                if block.get("is_error"):
                    calls[block["tool_use_id"]]["error"] = text[:300]
                else:
                    calls[block["tool_use_id"]]["lines"] = [
                        int(n) for n in re.findall(r"(?m)^\s*(\d+)\t", text)]
    return result, list(calls.values())


def read_summary(reads: list[dict] | None, out: Path, key: str) -> dict | None:
    """How a run read its candidates: the share of the pack's lines its successful Reads covered,
    the refused Reads, and how many node files it opened beside the pack."""
    if reads is None:
        return None
    pack = out / "inputs" / f"pack_{key}.txt"
    total = len(pack.read_text(encoding="utf-8").splitlines()) if pack.is_file() else 0
    covered: set[int] = set()
    errors = []
    for read in reads:
        if read["path"] != str(pack):
            continue
        if read["error"]:
            errors.append(read["error"])
            continue
        covered.update(n for n in read.get("lines") or [] if 1 <= n <= total)
    spec = str(out / "project/siegard/specification")
    return {"pack_lines": total, "pack_lines_read": len(covered),
            "pack_reads": sum(1 for r in reads if r["path"] == str(pack)),
            "pack_read_errors": errors,
            "node_files_opened": sum(1 for r in reads if (r["path"] or "").startswith(spec)
                                     and not (r["path"] or "").endswith(".log.md")),
            "logs_opened": sum(1 for r in reads if (r["path"] or "").endswith(".log.md"))}


def jaccard(a: set[str], b: set[str]) -> float:
    return 1.0 if not a and not b else len(a & b) / len(a | b)


def grade(out: Path, arms: list[str] | None) -> dict:
    manifest = json.loads((out / "manifest.json").read_text())
    arms = arms or sorted(p.name for p in (out / "runs").iterdir() if p.is_dir())
    report = {"specification_digest": manifest["specification_digest"], "arms": {}}
    for arm in arms:
        tasks = {}
        for key, meta in manifest["tasks"].items():
            runs = []
            for f in sorted([*(out / "runs" / arm).glob(f"{key}--*.json"),
                             *(out / "runs" / arm).glob(f"{key}--*.jsonl")]):
                data, reads = load_run(f)
                usage = data.get("usage") or {}
                runs.append({"file": f.name, "implements": implements_of(data.get("result", "")),
                             "cost_usd": data.get("total_cost_usd"),
                             "input_tokens": sum(usage.get(k, 0) for k in (
                                 "input_tokens", "cache_creation_input_tokens",
                                 "cache_read_input_tokens")),
                             "output_tokens": usage.get("output_tokens", 0),
                             "models": sorted((data.get("modelUsage") or {}).keys()),
                             "turns": data.get("num_turns"),
                             "reads": reads})
            parsed = [r["implements"] for r in runs if r["implements"] is not None]
            pairs = [jaccard(a, b) for a, b in itertools.combinations(parsed, 2)]
            recorded = set(meta["recorded_implements"])
            tasks[key] = {
                "runs": len(runs), "parsed": len(parsed),
                "identical_all": len(parsed) > 1 and all(p == parsed[0] for p in parsed),
                "pairwise_jaccard": [round(p, 3) for p in pairs],
                "vs_recorded_jaccard": [round(jaccard(p, recorded), 3) for p in parsed],
                "union_minus_intersection": sorted(set().union(*parsed) - set.intersection(*parsed))
                if parsed else [],
                "cost_usd": [r["cost_usd"] for r in runs],
                "input_tokens": [r["input_tokens"] for r in runs],
                "models": sorted({m for r in runs for m in r["models"]}),
                "implements": [sorted(p) for p in parsed],
                "turns": [r["turns"] for r in runs],
                "reading": [read_summary(r["reads"], out, key) for r in runs],
            }
        allpairs = [p for t in tasks.values() for p in t["pairwise_jaccard"]]
        allrec = [p for t in tasks.values() for p in t["vs_recorded_jaccard"]]
        costs = [c for t in tasks.values() for c in t["cost_usd"] if c is not None]
        report["arms"][arm] = {
            "tasks": tasks,
            "summary": {
                "tasks_identical_across_reps": sum(t["identical_all"] for t in tasks.values()),
                "tasks": len(tasks),
                "mean_pairwise_jaccard": round(sum(allpairs) / len(allpairs), 3) if allpairs else None,
                "min_pairwise_jaccard": min(allpairs) if allpairs else None,
                "mean_vs_recorded_jaccard": round(sum(allrec) / len(allrec), 3) if allrec else None,
                "total_cost_usd": round(sum(costs), 2),
                "runs": sum(t["runs"] for t in tasks.values()),
            }}
    (out / "grade.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for arm, r in report["arms"].items():
        print(arm, json.dumps(r["summary"]))
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("freeze")
    f.add_argument("consumer", type=Path)
    f.add_argument("slug")
    f.add_argument("out", type=Path)
    f.add_argument("--tasks", required=True)
    r = sub.add_parser("run")
    r.add_argument("out", type=Path)
    r.add_argument("--arm", required=True)
    r.add_argument("--plugin-dir", type=Path, required=True)
    r.add_argument("--reps", type=int, default=3)
    r.add_argument("--model")
    r.add_argument("--parallel", type=int, default=5)
    r.add_argument("--inputs", choices=("paths", "pack"), default="paths")
    k = sub.add_parser("pack")
    k.add_argument("out", type=Path)
    g = sub.add_parser("grade")
    g.add_argument("out", type=Path)
    g.add_argument("--arm", action="append")
    a = ap.parse_args()
    if a.cmd == "freeze":
        freeze(a.consumer.resolve(), a.slug, a.out.resolve(), a.tasks.split(","))
    elif a.cmd == "run":
        run(a.out.resolve(), a.arm, a.plugin_dir.resolve(), a.reps, a.model, a.parallel, a.inputs)
    elif a.cmd == "pack":
        pack_inputs(a.out.resolve())
    else:
        grade(a.out.resolve(), a.arm)
    return 0


if __name__ == "__main__":
    sys.exit(main())
