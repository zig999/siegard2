#!/usr/bin/env python3
"""Run the caller's build and test commands, capture what they printed, and record the outcome.

This exists so that nothing which judges a test run also performs it. `test-failure-diagnostician`
reads what this writes and never executes anything, which is what keeps a run reproducible
independently of the judgement about it: a diagnostician that ran its own suite would be the only
witness to what happened. `foundation/0004` R6 puts the mechanical half — invoke, capture, record the
exit status — in a script, and this is that script.

It holds no knowledge of any technology. The commands are the caller's; this composes none of them,
infers none from what it finds in the repository, and has no notion of which step is a compile and
which is a test. That is deliberate: a runner that guessed the test command would be a target pack
wearing a framework's clothes, and the guess would be wrong in the repository that mattered.

**No shell.** Each command is split into an argument vector with `shlex.split` and executed directly.
Nothing expands `&&`, `|`, `>`, `$VAR`, or a glob, and nothing a command prints can start another one.
A caller who needs a pipeline writes it into a file and names that file as the command.

**No default timeout.** `foundation/0006` R21 admits a numeric threshold only where it was calibrated
from executed runs and recorded with the evidence that calibrated it, and no such calibration exists
for how long a suite may take. `foundation/0004` R14 refuses a value a component supplies silently. So
the timeout is a required input rather than a shipped constant, and there is no unbounded run.

**A step that fails stops the run.** Later steps are recorded as `not_run` rather than executed,
because a suite run against a tree that did not compile reports failures about a binary nobody built.
Which step compiles is not known here; that a failed step invalidates what follows it is.

**What lands on disk.** Whatever the commands printed, verbatim. The environment is neither recorded
nor logged, but a command that prints a secret puts it in the log this writes. The framework cannot
tell a secret from a string shaped like one, and a redaction heuristic that guessed would remove
evidence a diagnosis needs while still missing the secret it was written for. Callers run commands
that do not print secrets.

Declared dependencies: none beyond the standard library.

Usage:  run_suite.py --run-id tr_xxxxxxxx --artifact-dir DIR --timeout-seconds N
                     --step NAME="COMMAND" [--step NAME="COMMAND" ...] [--cwd DIR]
Exit:   0 every step passed, 1 a step failed or timed out, 2 cannot run
"""

from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

CANNOT_RUN = 2
CONTRACT = "test-run/1"
RUN_ID = re.compile(r"^tr_[0-9a-f]{8}$")
STEP_NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def cannot_run(message: str) -> None:
    """Refuse before anything is executed. A bad input is never repaired into a default."""
    print(f"cannot run: {message}", file=sys.stderr)
    raise SystemExit(CANNOT_RUN)


def parse_steps(raw: list[str]) -> list[tuple[str, list[str]]]:
    """Turn each NAME=COMMAND into a name and an argument vector, refusing anything ambiguous."""
    steps: list[tuple[str, list[str]]] = []
    seen: set[str] = set()
    for item in raw:
        name, separator, command = item.partition("=")
        if not separator:
            cannot_run(f"step {item!r} is not NAME=COMMAND")
        if not STEP_NAME.match(name):
            cannot_run(f"step name {name!r} must be lowercase words joined by hyphens")
        if name in seen:
            cannot_run(f"step {name!r} is named twice; a run records one outcome per step")
        try:
            argv = shlex.split(command)
        except ValueError as error:
            cannot_run(f"step {name!r}: {error}")
        if not argv:
            cannot_run(f"step {name!r} has an empty command")
        seen.add(name)
        steps.append((name, argv))
    return steps


def run_step(argv: list[str], cwd: Path, timeout: int, log: Path) -> tuple[str, int | None]:
    """Execute one command, write everything it printed to log, and return its outcome."""
    try:
        completed = subprocess.run(
            argv,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError:
        log.write_text(f"command not found: {argv[0]}\n", encoding="utf-8")
        return "not_found", None
    except subprocess.TimeoutExpired as expired:
        captured = expired.output or b""
        log.write_bytes(captured)
        with log.open("a", encoding="utf-8") as handle:
            handle.write(f"\n[run_suite] no output after {timeout}s; the step was terminated\n")
        return "timed_out", None
    log.write_bytes(completed.stdout)
    return ("passed" if completed.returncode == 0 else "failed"), completed.returncode


def main() -> int:
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--artifact-dir", required=True)
    parser.add_argument("--timeout-seconds", required=True, type=int)
    parser.add_argument("--step", action="append", required=True, metavar="NAME=COMMAND")
    parser.add_argument("--cwd", default=".")
    args = parser.parse_args()

    if not RUN_ID.match(args.run_id):
        cannot_run(f"run id {args.run_id!r} must be tr_ followed by eight hex digits")
    if args.timeout_seconds <= 0:
        cannot_run("timeout-seconds must be a positive whole number of seconds")

    cwd = Path(args.cwd).resolve()
    if not cwd.is_dir():
        cannot_run(f"working directory {cwd} does not exist")

    # Every input is validated before anything is created. A refusal that had already made the run
    # directory would leave an empty one behind and, worse, burn the identifier: the next invocation
    # with that id would be refused for a run that never happened.
    steps = parse_steps(args.step)

    run_dir = Path(args.artifact_dir).resolve() / args.run_id
    if run_dir.exists():
        cannot_run(f"{run_dir} already exists; a second run under one id would overwrite its evidence")
    try:
        run_dir.mkdir(parents=True)
    except OSError as error:
        cannot_run(f"cannot create {run_dir}: {error}")

    recorded: list[dict[str, object]] = []
    stopped = False
    for name, argv in steps:
        log = run_dir / f"{name}.log"
        if stopped:
            recorded.append({"name": name, "command": shlex.join(argv), "outcome": "not_run",
                             "exit_code": None, "output": None})
            continue
        outcome, code = run_step(argv, cwd, args.timeout_seconds, log)
        recorded.append({"name": name, "command": shlex.join(argv), "outcome": outcome,
                         "exit_code": code, "output": str(log.relative_to(run_dir.parent))})
        if outcome != "passed":
            stopped = True

    combined = run_dir / "run.log"
    with combined.open("w", encoding="utf-8") as handle:
        for step in recorded:
            handle.write(f"===== {step['name']} :: {step['command']} :: {step['outcome']} =====\n")
            if step["output"]:
                handle.write((run_dir.parent / str(step["output"])).read_text(errors="replace"))
            handle.write("\n")

    failed = next((s for s in recorded if s["outcome"] not in ("passed", "not_run")), None)
    artifact = {
        "contract_version": CONTRACT,
        "run_id": args.run_id,
        "producer": "run-suite",
        "outcome": "passed" if failed is None else str(failed["outcome"]),
        "failed_step": None if failed is None else failed["name"],
        "steps": recorded,
        "combined_output": str(combined.relative_to(run_dir.parent)),
    }
    (run_dir / "test-run.json").write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(artifact, indent=2))
    return 0 if failed is None else 1


if __name__ == "__main__":
    sys.exit(main())
