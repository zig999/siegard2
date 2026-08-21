#!/usr/bin/env python3
"""Run the caller's build and test commands, capture what they printed, and record the outcome.

This exists so that nothing which judges a run also performs it. The review reads what this
writes and executes nothing, which is what keeps a run reproducible independently of the
judgment about it: a reviewer that ran its own suite would be the only witness to what happened,
and an implementer that could run its own tests would be the only witness to whether its work
passed. The mechanical half — invoke, capture, record the exit status — is decidable, so it is a
script's and not an agent's.

**It holds no knowledge of any technology.** The commands are the caller's: this composes none of
them, infers none from what it finds in the repository, and has no notion of which step is a
compile and which is a test. A runner that guessed the test command would be answering a
question about the consumer's project, and the guess would be wrong in the project that
mattered.

**The path is the identity.** A run is named by the caller and lands at `run/<slug>/` under the
delivery root, beside the nodes, kept the way `intake/` is kept under a work root: it is the
material a judgment was read from, never a node and never validated as one. A slug that already
exists is a refusal — evidence is not overwritten, and a second run says so with a second name.

**No shell.** Each command is split into an argument vector with `shlex.split` and executed
directly. Nothing expands `&&`, `|`, `>`, `$VAR`, or a glob, and nothing a command prints can
start another one. A caller who needs a pipeline writes it into a file and names that file as
the command.

**No default timeout, and no default working directory.** A number this framework ships is a
number nobody calibrated, and an unbounded run is worse — so the timeout is a required input,
stated per run by whoever knows how long the suite takes, and recorded with the run. The directory
is required for the same reason: the commands only mean anything where the project sits, and a
directory this script chose in silence would produce a run against a tree nobody named, whose
every step failed for a reason the record could not show.

**A step that fails stops the run.** Later steps are recorded as not run rather than executed,
because a suite run against a tree that did not compile reports failures about a binary nobody
built. Which step compiles is not known here; that a failed step invalidates what follows it is.

**What lands on disk is whatever the commands printed, verbatim.** The environment is neither
recorded nor logged, but a command that prints a secret puts it in the log this writes. Nothing
here can tell a secret from a string shaped like one, and a redaction heuristic that guessed
would remove evidence a diagnosis needs while still missing the secret it was written for. Run
commands that do not print secrets.

**This script counts no tests.** It records what each command exited with and what it printed;
how many tests failed and why is read out of that output by whoever diagnoses it. Parsing a
reporter's format is knowledge of a stack, and this holds none.

**Each attempted step records when it started and when it ended.** Until siegard-run/2 the
record carried no clock on purpose, so two records of one command differed only where the
command did — and what that byte-comparability cost was that nobody, inside a session or after
it, could say what any step of any run took. When a run happened and how long each step held
the wall is the one fact that cannot be reconstructed once the run is over, so the record is
where it lives. A step never attempted carries null for both: nothing happened, and a clock
reading would claim something did.

Declared dependencies: none beyond the standard library.

Usage:  run.py <delivery-root> --run <slug> --cwd DIR --timeout-seconds N
               --step NAME="COMMAND" [--step NAME="COMMAND" ...]
        run.py --help    print this text and stop
Exit:   0 every step passed
        1 a step failed, timed out, or could not be found
        2 cannot run
"""

from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import NoReturn

CANNOT_RUN = 2
CONTRACT = "siegard-run/2"
RUN_DIR = "run"
COMBINED_LOG = "run.log"
SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def cannot_run(message: str) -> NoReturn:
    """Refuse before anything is executed or created. A bad input is never repaired into a
    default."""
    print(f"cannot run: {message}", file=sys.stderr)
    raise SystemExit(CANNOT_RUN)


def now() -> str:
    """The wall clock, UTC, to the millisecond — the resolution a step's duration is read at.
    UTC because a record is read on machines the run never saw, and an offset that moved with
    the runner's locale would make two steps of one run appear to overlap."""
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def parse_steps(raw: list[str]) -> list[tuple[str, list[str]]]:
    """Turn each NAME=COMMAND into a name and an argument vector, refusing anything ambiguous."""
    steps: list[tuple[str, list[str]]] = []
    seen: set[str] = set()
    for item in raw:
        name, separator, command = item.partition("=")
        if not separator:
            cannot_run(f"step {item!r} is not NAME=COMMAND")
        if not SLUG.fullmatch(name):
            cannot_run(f"step name {name!r} must be lowercase words joined by hyphens")
        if f"{name}.log" == COMBINED_LOG:
            cannot_run(f"step {name!r} would write {COMBINED_LOG}, which is the combined log of "
                       f"every step; the run would overwrite this step's own output — name it "
                       f"differently")
        if name in seen:
            cannot_run(f"step {name!r} is named twice; a run records one outcome per step")
        try:
            argv = shlex.split(command)
        except ValueError as broken:
            cannot_run(f"step {name!r}: {broken}")
        if not argv:
            cannot_run(f"step {name!r} has an empty command")
        seen.add(name)
        steps.append((name, argv))
    return steps


def run_step(argv: list[str], cwd: Path, timeout: int, log: Path) -> tuple[str, int | None]:
    """Execute one command, write everything it printed to log, and return how it ended."""
    try:
        completed = subprocess.run(argv, cwd=cwd, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, timeout=timeout, check=False)
    except FileNotFoundError:
        log.write_text(f"command not found: {argv[0]}\n", encoding="utf-8")
        return "not_found", None
    except OSError as broken:
        # The command exists and still could not be invoked: not executable, a directory, a
        # binary this kernel cannot load. Letting it escape would end the run in a traceback
        # after the run directory was created — burning the name for a run with no record.
        log.write_text(f"cannot invoke {argv[0]}: {broken}\n", encoding="utf-8")
        return "not_found", None
    except subprocess.TimeoutExpired as expired:
        log.write_bytes(expired.output or b"")
        with log.open("a", encoding="utf-8") as handle:
            handle.write(f"\n[run] terminated after {timeout}s; what it printed up to then "
                         f"is above\n")
        return "timed_out", None
    log.write_bytes(completed.stdout)
    return ("passed" if completed.returncode == 0 else "failed"), completed.returncode


def main() -> int:
    # add_help was always here; the description is what makes `--help` answer with this
    # script's own docstring, the same text its six siblings print, rather than a bare
    # flag list that says nothing about what a run records or refuses.
    parser = argparse.ArgumentParser(
        add_help=True, description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("delivery_root")
    parser.add_argument("--run", required=True, metavar="SLUG")
    parser.add_argument("--timeout-seconds", required=True, type=int)
    parser.add_argument("--step", action="append", required=True, metavar="NAME=COMMAND")
    parser.add_argument("--cwd", required=True)
    args = parser.parse_args()

    root = Path(args.delivery_root)
    if not root.is_dir():
        cannot_run(f"delivery root {root} is not a directory")
    if not SLUG.fullmatch(args.run):
        cannot_run(f"run name {args.run!r} must be lowercase words joined by hyphens; "
                   f"the path is the identity and this one computes to none")
    if args.timeout_seconds <= 0:
        cannot_run("--timeout-seconds must be a positive whole number of seconds")
    cwd = Path(args.cwd).resolve()
    if not cwd.is_dir():
        cannot_run(f"working directory {cwd} does not exist")

    # Every input is validated before anything is created. A refusal that had already made the
    # run directory would leave an empty one behind and, worse, burn the name: the next run
    # under it would be refused for a run that never happened.
    steps = parse_steps(args.step)

    where = f"{RUN_DIR}/{args.run}"
    run_dir = root / where
    if run_dir.exists():
        cannot_run(f"{run_dir} already exists; a second run under one name would overwrite "
                   f"the evidence of the first — name this one differently")
    try:
        run_dir.mkdir(parents=True)
    except FileExistsError:
        # The check above is advisory; this is the guard. A dangling symlink slips past
        # `exists()`, and two concurrent runs can both reach here — only one mkdir wins.
        cannot_run(f"{run_dir} already exists; a second run under one name would overwrite "
                   f"the evidence of the first — name this one differently")
    except OSError as broken:
        cannot_run(f"cannot create {run_dir}: {broken}")

    recorded: list[dict[str, object]] = []
    stopped = False
    for name, argv in steps:
        if stopped:
            recorded.append({"name": name, "command": shlex.join(argv), "outcome": "not_run",
                             "exit_code": None, "output": None,
                             "started_at": None, "ended_at": None})
            continue
        log = run_dir / f"{name}.log"
        started = now()
        outcome, code = run_step(argv, cwd, args.timeout_seconds, log)
        recorded.append({"name": name, "command": shlex.join(argv), "outcome": outcome,
                         "exit_code": code, "output": f"{name}.log",
                         "started_at": started, "ended_at": now()})
        if outcome != "passed":
            stopped = True

    combined = run_dir / COMBINED_LOG
    with combined.open("w", encoding="utf-8") as handle:
        for step in recorded:
            handle.write(f"===== {step['name']} :: {step['command']} :: "
                         f"{step['outcome']} =====\n")
            if step["output"]:
                # The encoding is stated: a step log holds whatever bytes the command printed,
                # and reading it under the machine's locale would make one run's combined log
                # differ between two machines.
                handle.write((run_dir / str(step["output"]))
                             .read_text(encoding="utf-8", errors="replace"))
            handle.write("\n")

    failed = next((s for s in recorded if s["outcome"] not in ("passed", "not_run")), None)
    record = {
        "contract_version": CONTRACT,
        "run": where,
        "cwd": str(cwd),
        "timeout_seconds": args.timeout_seconds,
        "outcome": "passed" if failed is None else str(failed["outcome"]),
        "failed_step": None if failed is None else failed["name"],
        "steps": recorded,
        "combined_output": COMBINED_LOG,
    }
    (run_dir / "run.json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n",
                                      encoding="utf-8")
    print(json.dumps(record, indent=2, ensure_ascii=False))
    return 0 if failed is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
