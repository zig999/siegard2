#!/usr/bin/env python3
"""Refuses a commit that adds a door line out of form to an orchestration log, or that records a stop
alongside more than the measure, in a Siegard project.

The harness runs this on `PreToolUse` for the Bash tool, as `hooks/hooks.json` declares. Every
door an orchestrating run takes or recommends is one line of its orchestration log, and that line
is what the grant's budget, telemetry and the person reading the run count by: «Each door taken is
one line of the run's orchestration log, `decided: <door> — <criterion> — <deciding fact>`, and a
door R3 reserves is never taken.» (SPEC-006 R7) A line out of that form is counted by nothing, and
a judged door taken where no grant armed one is a choice the person never handed over. The one
act every run performs is the commit, so the line is read there:

«A `git commit` a session runs in a project that declares `siegard.json` is refused by the
plugin's `PreToolUse` hook where a line it adds to an orchestration log opens with `decided:` or
`recommended:` and is not of the form R5 and R7 state with a criterion R2 names, or opens with
`decided:` over a judged criterion while no grant armed through the framework names that log's
initiative or names none.» (SPEC-006 R12) An armed goal arms no judged door: «a line over a rung
of the ladder is taken where a grant names the log's initiative or names none, and refused where
none is armed, an armed goal notwithstanding» (SPEC-011 R6)

- **Which commands.** A command holding `git … commit`; everything else is allowed before
  anything is read, so the hook costs nothing on the commands that are not commits.
- **Which logs.** `orchestration.md` under the delivery root — each initiative's and the root's
  own — and under `siegard-survey/`, changed against `HEAD`. A commit reaches one the index holds
  changed, one a path the command names is or holds, and every changed one where the command
  stages or commits all that is tracked (`-a`, `--all`, `-A`, `-u`).
- **Which lines.** Those the log holds on disk beyond what it holds at `HEAD`, each read past an
  opening `- ` and its backticks; a log `HEAD` does not hold is read whole. A line opening with
  neither word is no door line and is never read for form.
- **Which stop commits.** A commit that adds to such a log a line `goal.STOP_LINE` matches, of a
  class in `goal.STOP_CLASSES`, and carries a path other than an orchestration log, a path under
  the telemetry root or a captured run of that initiative that ended `passed`: «the commit that records a stop is the measure alone» (SPEC-008 R19). The
  paths it carries are those the command names, else the ones the index holds staged, and every
  tracked path that differs from `HEAD` where it commits all that is tracked. A commit that adds
  no stop line is never read for this.
- **What refuses.** A door line `goal.DOOR_LINE` does not match — the one form telemetry and the
  grant's budget read — and a `decided:` line whose criterion is one of `goal.JUDGED` while the
  grant armed by `grant.py --arm` is absent or names another initiative. A derived `decided:` line
  passes here: whether its door's entry point accepted it is `bin/door.py --check`'s to say.

The refusal is the harness's `permissionDecision: deny`, its reason said to the session: each
line, the log it is in, and the form it misses. It never fails a session and never traps one:
every path out exits 0, and where the command, the project or a log cannot be read the commit
goes ahead — a hook that refused on its own failure would hold every commit of every project on a
reason no session can repair.
"""
from __future__ import annotations

import contextlib
import io
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

HOOKS = Path(__file__).resolve().parent
EVENT = "PreToolUse"
TOOL = "Bash"
GIT_TIMEOUT_SECONDS = 10
LOG_FILE = "orchestration.md"
SURVEY_ROOT = "siegard-survey"
COMMIT = re.compile(r"\bgit\b[^\n;&|]*?\bcommit\b")
GIT_VALUED = {"-C", "-c", "--git-dir", "--work-tree", "--namespace"}
COMMIT_VALUED = {"-m", "--message", "-F", "--file", "-C", "--reuse-message", "-c",
                 "--reedit-message", "--author", "--date", "-t", "--template", "--cleanup",
                 "--fixup", "--squash", "--trailer", "-S", "--gpg-sign"}
WHOLE = {"-a", "--all", "-A", "-u", "--update"}


def git(home: Path, *args: str) -> tuple[int, str]:
    done = subprocess.run(["git", "-C", str(home), *args], capture_output=True, text=True,
                          timeout=GIT_TIMEOUT_SECONDS)
    return done.returncode, done.stdout


def tokens_of(command: str) -> list[str]:
    """The command's words and separators; a command shlex cannot split is read by whitespace."""
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|()")
        lexer.whitespace_split = True
        return list(lexer)
    except ValueError:
        return re.findall(r"[;&|()]+|[^\s;&|()]+", command)


def reach_of(command: str, start: Path) -> tuple[bool, bool, list[Path]]:
    """Whether the command runs `git commit`, whether it stages or commits all that is tracked,
    and the paths it names to `git add` or `git commit`, each resolved where git would resolve
    it."""
    commits, whole, named = False, False, []
    segment: list[str] = []
    for token in [*tokens_of(command), ";"]:
        if not set(token) <= set(";&|()"):
            segment.append(token)
            continue
        if len(segment) == 2 and segment[0] == "cd":
            start = (start / segment[1]).resolve()
        if "git" in segment:
            at = segment.index("git") + 1
            base = start
            while at < len(segment) and segment[at].startswith("-"):
                if segment[at] == "-C" and at + 1 < len(segment):
                    base = (start / segment[at + 1]).resolve()
                at += 1 + (segment[at] in GIT_VALUED)
            verb = segment[at] if at < len(segment) else None
            if verb in ("add", "commit"):
                commits = commits or verb == "commit"
                skip = False
                for word in segment[at + 1:]:
                    if skip:
                        skip = False
                    elif word == "--":
                        continue
                    elif word.startswith("-"):
                        flag = word.split("=", 1)[0]
                        cluster = "" if word.startswith("--") else word[1:]
                        if flag in WHOLE or (verb == "commit" and "a" in cluster):
                            whole = True
                        skip = "=" not in word and verb == "commit" and (
                            flag in COMMIT_VALUED or (cluster != "" and cluster[-1] in "mFCct"))
                    else:
                        named.append((base / word).resolve())
        segment = []
    return commits, whole, named


def changed_logs(home: Path, roots: list[Path]) -> list[tuple[Path, bool]]:
    """Every orchestration log under the roots that differs from `HEAD`, with whether the index
    holds it changed."""
    present = [str(root) for root in roots if root.is_dir()]
    if not present:
        return []
    code, out = git(home, "status", "--porcelain", "--untracked-files=all", "--", *present)
    if code != 0:
        raise OSError(out)
    logs = []
    for line in out.splitlines():
        if len(line) < 4:
            continue
        path = line[3:].split(" -> ")[-1].strip('"')
        if Path(path).name == LOG_FILE:
            logs.append(((home / path).resolve(), line[0] not in (" ", "?")))
    return logs


def added_lines(home: Path, log: Path) -> list[str]:
    """The lines the log holds on disk beyond those it holds at `HEAD`."""
    relative = log.relative_to(home).as_posix()
    code, before = git(home, "show", f"HEAD:{relative}")
    earlier = before.splitlines() if code == 0 else []
    remaining = [line.strip() for line in earlier]
    added = []
    for raw in log.read_text(encoding="utf-8").splitlines():
        if raw.strip() in remaining:
            remaining.remove(raw.strip())
        else:
            added.append(raw)
    return added


def problems_of(goal, log: Path, lines: list[str], delivery: Path,
                granted: dict | None) -> list[str]:
    initiative = log.parent.name if log.parent != delivery else None
    found = []
    for raw in lines:
        line = goal.log_line(raw)
        if not line.startswith(goal.DOOR_VERBS):
            continue
        match = goal.DOOR_LINE.match(line)
        if match is None:
            found.append(f"{log}: `{line}` — not `<verb>: <door> — <criterion> — <deciding "
                         f"fact>` with a criterion of: {', '.join(goal.CRITERIA)}")
        elif match.group("verb") == "decided" and match.group("criterion") in goal.JUDGED:
            if not granted:
                found.append(f"{log}: `{line}` — a judged door, and no grant is armed; a judged "
                             f"door is taken only under a grant the person armed with "
                             f"/siegard-grant, an armed goal notwithstanding")
            elif initiative is not None and granted.get("slug") not in (initiative, None):
                found.append(f"{log}: `{line}` — a judged door, and the armed grant names "
                             f"{granted.get('slug')}, not {initiative}")
            elif initiative is None and not granted.get("routes"):
                found.append(f"{log}: `{line}` — a judged route in the delivery root's own log, "
                             f"and the armed grant holds no `routes`; a judged route is taken "
                             f"only under a grant the person armed with /siegard-grant --routes")
    return found


def carried(home: Path, named: list[Path], whole: bool) -> list[Path]:
    """The paths the commit carries: those the command names, else the ones the index holds
    staged, and every tracked path that differs from `HEAD` where it commits all that is
    tracked."""
    if named:
        paths = list(named)
    else:
        code, out = git(home, "diff", "--cached", "--name-only")
        paths = [(home / line).resolve() for line in out.splitlines() if line.strip()] \
            if code == 0 else []
    if whole:
        code, out = git(home, "diff", "HEAD", "--name-only")
        paths += [(home / line).resolve() for line in out.splitlines() if line.strip()] \
            if code == 0 else []
    return paths


def stop_commit_refusals(goal, door, home: Path, telemetry: Path, paths: list[Path],
                         reached: list[Path]) -> list[str]:
    """A commit that adds a stop line to an initiative's orchestration log carries the log, the
    telemetry root and the runs that passed, and nothing else: «A run whose orchestration log
    closes on a stop line commits nothing after it but the measure: the telemetry root, the log
    that carries the stop line, and the captured runs of the initiative that ended `passed`.»
    (SPEC-008 R18)"""
    found = []
    for log in reached:
        stops = [line for line in added_lines(home, log)
                 if (match := goal.STOP_LINE.match(goal.log_line(line)))
                 and match.group(1) in goal.STOP_CLASSES]
        if not stops:
            continue
        beyond = [path for path in paths if path != log and telemetry not in path.parents
                  and path != telemetry and path.name != LOG_FILE
                  and not door.passed_run(path, log.parent)]
        if beyond:
            found.append(f"{log}: `{goal.log_line(stops[-1])}` closes the log on a stop, and "
                         f"this commit also carries {', '.join(str(p) for p in beyond[:3])}"
                         f"{' and more' if len(beyond) > 3 else ''} — after a stop the "
                         f"measure alone is committed: the telemetry root, the log and the runs that passed")
    return found


def refusals(record: dict) -> list[str]:
    """What refuses the command, or nothing; any failure to read is nothing."""
    command = (record.get("tool_input") or {}).get("command")
    if not isinstance(command, str) or not COMMIT.search(command):
        return []
    where = record.get("cwd")
    start = Path(where) if isinstance(where, str) and where else Path.cwd()
    if not start.is_dir():
        return []
    sys.path.insert(0, str(HOOKS.parent / "bin"))
    from project import PROJECT_FILE, toplevel_of
    home = toplevel_of(start, timeout=GIT_TIMEOUT_SECONDS)
    if not (home / PROJECT_FILE).is_file():
        return []
    with contextlib.redirect_stderr(io.StringIO()):
        import door
        import goal
    fields, unresolved, _ = door.resolve(home)
    if unresolved or "delivery_root" not in fields:
        return []
    delivery = fields["delivery_root"].resolve()
    commits, whole, named = reach_of(command, start)
    if not commits:
        return []
    reached = []
    for log, staged in changed_logs(home, [delivery, home / SURVEY_ROOT]):
        if staged or whole or any(path == log or path in log.parents for path in named):
            reached.append(log)
    found = []
    if reached:
        held_path = goal.armed_path(home).with_name("grant.json")
        granted = goal.read_armed(held_path) if held_path.exists() else None
        for log in reached:
            found += problems_of(goal, log, added_lines(home, log), delivery, granted)
    telemetry = fields.get("telemetry_root")
    if telemetry is not None and reached:
        found += stop_commit_refusals(goal, door, home, telemetry.resolve(),
                                      carried(home, named, whole), reached)
    return found


def main() -> int:
    try:
        record = json.loads(sys.stdin.read() or "{}")
    except (ValueError, OSError):
        return 0
    if not isinstance(record, dict) or record.get("hook_event_name") not in (EVENT, None) \
            or record.get("tool_name") != TOOL:
        return 0
    try:
        found = refusals(record)
    except (Exception, SystemExit):
        return 0
    if not found:
        return 0
    reason = ("Siegard refuses this commit: it adds door lines to an orchestration log that "
              "nothing can count or that no grant armed, or it records a stop alongside files "
              "that are not the measure. Rewrite or remove each line, or commit the stop line "
              "with the log, the telemetry root and the runs that passed alone, then commit again. A judged door with "
              "no grant armed is not taken: hand it to the person instead.\n"
              + "\n".join(f"- {line}" for line in found))
    print(json.dumps({"hookSpecificOutput": {"hookEventName": EVENT,
                                             "permissionDecision": "deny",
                                             "permissionDecisionReason": reason}}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException:
        raise SystemExit(0)
