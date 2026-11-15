#!/usr/bin/env python3
"""Refuses, in a Siegard project, a repository act no armed run may take and a hand write of a file a script owns.

The harness runs this on `PreToolUse`, as `hooks/hooks.json` declares: for the Bash tool, and for
the tools that write a file. Two bounds a session's rules state are decidable from the command and
from disk, so a script holds them rather than a prompt:

«A push, a branch or a history rewrite is never a skill's, a goal's or a grant's. Where a goal or
a grant is armed through the framework, the plugin's `PreToolUse` hook refuses a shell command
that runs `git push`; creates, renames or deletes a branch; rewrites history — `git rebase`, `git
commit --amend`, `git reset --hard`, `git filter-branch`, `git filter-repo`; stashes; or stages or
commits all that is tracked.» (SPEC-010 R8)

«In a project that declares `siegard.json`, the plugin's `PreToolUse` hook refuses a `Write` or an
`Edit` of `siegard-trace.json`, of `plan.json` in an initiative under the work root, of
`delivery.json` in an initiative under the delivery root, and of any path under an initiative's
`run/` under the delivery root» (SPEC-010 R9)

- **Which commands.** The command is split into its shell commands — at `;`, `&&`, `||`, `|`, `&`
  and line ends, every heredoc's body left out — and a command is read where `git` is its first
  word, past variable assignments and the wrappers `env`, `command`, `nohup`, `time`, `nice` and
  `timeout`; the command handed to `bash -c` or `sh -c` is read the same way. A `git` word inside
  a quoted argument, a heredoc or another command's arguments is never read as one.
- **Which acts.** `push`; `checkout` with `-b`, `-B` or `--orphan`; `switch` with `-c`, `-C`,
  `--create`, `--force-create` or `--orphan`; `worktree add` with `-b` or `-B`; `branch` naming a
  branch, or with a flag that deletes, moves, copies or forces one; `rebase`; `commit --amend`;
  `reset --hard`; `filter-branch` and `filter-repo`; `stash` but `list` and `show`; `add` with
  `-A`, `--all`, `-u` or `--update` and no path, or with `.`, `:/` or `*` as its path; `commit`
  with `-a` or `--all`.
- **When.** Only where a goal armed by `goal.py --arm` or a grant armed by `grant.py --arm` is
  recorded for the repository the command runs in, read from the record's presence: outside both,
  the person's own words decide and nothing here reads them.
- **Which writes.** A `Write`, an `Edit` or a `MultiEdit` whose path is `siegard-trace.json`
  anywhere in the project, `<work-root>/<initiative>/plan.json`,
  `<delivery-root>/<initiative>/delivery.json`, or under `<delivery-root>/<initiative>/run/`, as
  `bin/project.py` resolves the roots. Refused in every state, armed or not.

The refusal is the harness's `permissionDecision: deny`, its reason said to the session. It never
fails a session and never traps one: every path out exits 0, and where the event, the project or
a record cannot be read the act goes ahead — a hook that refused on its own failure would hold
every command of every project on a reason no session can repair.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import re
import shlex
import sys
from pathlib import Path

HOOKS = Path(__file__).resolve().parent
EVENT = "PreToolUse"
SHELL = "Bash"
WRITERS = ("Write", "Edit", "MultiEdit")
GIT_TIMEOUT_SECONDS = 10
SEPARATORS = {";", "&&", "||", "|", "&", ";;", "|&", "(", ")", "{", "}"}
WRAPPERS = {"env", "command", "nohup", "time", "nice", "builtin", "exec"}
SHELLS = {"bash", "sh", "zsh", "dash"}
GIT_VALUED = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}
HEREDOC = re.compile(r"<<-?[ \t]*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1[^\n]*\n.*?\n[ \t]*\2[ \t]*(?=\n|$)",
                     re.S)
ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
ALL_PATHS = {".", ":/", "*", ":(top)"}
BRANCH_CHANGES = {"-d", "-D", "--delete", "-m", "-M", "--move", "-c", "-C", "--copy", "-f",
                  "--force"}
BRANCH_LISTS = {"-l", "--list", "-a", "--all", "-r", "--remotes", "-v", "-vv", "--verbose",
                "--show-current", "--contains", "--no-contains", "--merged", "--no-merged",
                "--points-at", "--format", "--sort", "--column", "--no-column", "--color",
                "--no-color", "-q", "--quiet"}
WRITTEN_BY = {"siegard-trace.json": "bin/trace.py", "plan.json": "bin/plan.py",
              "delivery.json": "bin/deliver.py", "run": "bin/run.py"}


def shell_commands(command: str) -> list[list[str]]:
    """The command's shell commands, each as its words, heredoc bodies left out."""
    text = HEREDOC.sub("", command)
    try:
        lexer = shlex.shlex(text, posix=True, punctuation_chars=";&|(){}`\n")
        lexer.whitespace = " \t\r"
        lexer.whitespace_split = True
        words = list(lexer)
    except ValueError:
        words = re.findall(r"[;&|(){}`\n]+|[^\s;&|(){}`]+", text)
    found, current = [], []
    for word in [*words, ";"]:
        if word in SEPARATORS or (word and set(word) <= set(";&|(){}`\n")):
            if current:
                found.append(current)
            current = []
        else:
            current.append(word)
    return found


def invoked(words: list[str]) -> list[str]:
    """The words from the command's first word on, past assignments and wrappers."""
    at = 0
    while at < len(words):
        word = words[at]
        if ASSIGNMENT.match(word):
            at += 1
        elif os.path.basename(word) in WRAPPERS:
            at += 1
            while at < len(words) and (words[at].startswith("-") or ASSIGNMENT.match(words[at])):
                at += 1
        elif os.path.basename(word) == "timeout":
            at += 1
            while at < len(words) and words[at].startswith("-"):
                at += 1
            at += 1
        elif word == "sudo":
            at += 1
            while at < len(words) and words[at].startswith("-"):
                at += 1
        else:
            break
    return words[at:]


def acts_of(command: str, start: Path, depth: int = 0) -> list[tuple[str, Path]]:
    """Every act the shell bound names that the command runs, each as one short phrase beside the
    directory git runs it in: the working directory, moved by a `cd` before it or a `-C`."""
    found = []
    for words in shell_commands(command):
        words = invoked(words)
        if not words:
            continue
        name = os.path.basename(words[0])
        if name == "cd" and len(words) == 2:
            start = start / os.path.expanduser(words[1])
            continue
        if name in SHELLS and depth < 3:
            for at, word in enumerate(words[1:], start=1):
                if word == "-c" or (word.startswith("-") and not word.startswith("--")
                                    and "c" in word[1:]):
                    if at + 1 < len(words):
                        found += acts_of(words[at + 1], start, depth + 1)
                    break
            continue
        if name != "git":
            continue
        at, where = 1, start
        while at < len(words) and words[at].startswith("-"):
            if words[at] == "-C" and at + 1 < len(words):
                where = where / os.path.expanduser(words[at + 1])
            at += 1 + (words[at] in GIT_VALUED)
        if at >= len(words):
            continue
        act = act_of(words[at], words[at + 1:])
        if act:
            found.append((act, where))
    return found


def act_of(verb: str, rest: list[str]) -> str | None:
    flags = {word.split("=", 1)[0] for word in rest if word.startswith("-")}
    paths = [word for word in rest if not word.startswith("-")]
    if verb == "push":
        return "`git push`"
    if verb in ("rebase", "filter-branch", "filter-repo"):
        return f"`git {verb}`, which rewrites history"
    if verb == "commit" and "--amend" in flags:
        return "`git commit --amend`, which rewrites history"
    if verb == "reset" and "--hard" in flags:
        return "`git reset --hard`, which rewrites history"
    if verb == "checkout" and flags & {"-b", "-B", "--orphan"}:
        return "`git checkout` creating a branch"
    if verb == "switch" and flags & {"-c", "-C", "--create", "--force-create", "--orphan"}:
        return "`git switch` creating a branch"
    if verb == "worktree" and rest[:1] == ["add"] and flags & {"-b", "-B"}:
        return "`git worktree add` creating a branch"
    if verb == "branch":
        if flags & BRANCH_CHANGES:
            return "`git branch` changing a branch"
        if paths and not flags & BRANCH_LISTS:
            return "`git branch` creating a branch"
        return None
    if verb == "stash" and (not rest or rest[0] not in ("list", "show")):
        return "`git stash`"
    if verb == "add":
        named = [word for word in rest if not word.startswith("-")]
        if any(word in ALL_PATHS for word in named):
            return "`git add` of the whole tree"
        if flags & {"-A", "--all", "-u", "--update"} and not named:
            return "`git add` of all that is tracked"
        return None
    if verb == "commit":
        clusters = [word[1:] for word in rest if word.startswith("-") and not word.startswith("--")]
        for cluster in clusters:
            for letter in cluster:
                if letter == "a":
                    return "`git commit -a`, which commits all that is tracked"
                if letter in "mFCct":
                    break
        if "--all" in flags:
            return "`git commit --all`, which commits all that is tracked"
    return None


def armed_state(start: Path) -> str | None:
    """Which run is armed for the repository the directory is in, read from the records' presence:
    `a goal`, `a grant`, `a goal and a grant`, or nothing."""
    sys.path.insert(0, str(HOOKS.parent / "bin"))
    from project import PROJECT_FILE, toplevel_of
    home = toplevel_of(start, timeout=GIT_TIMEOUT_SECONDS)
    if not (home / PROJECT_FILE).is_file():
        return None
    with contextlib.redirect_stderr(io.StringIO()):
        import goal
    path = goal.armed_path(home)
    held = [what for what, file in (("a goal", path), ("a grant", path.with_name("grant.json")))
            if file.is_file()]
    return " and ".join(held) or None


def start_of(record: dict) -> Path | None:
    where = record.get("cwd")
    start = Path(where) if isinstance(where, str) and where else Path.cwd()
    return start if start.is_dir() else None


def shell_refusal(record: dict) -> str | None:
    command = (record.get("tool_input") or {}).get("command")
    if not isinstance(command, str) or "git" not in command:
        return None
    start = start_of(record)
    if start is None:
        return None
    acts = acts_of(command, start)
    armed, refused = None, []
    for act, where in acts:
        if not where.is_dir():
            continue
        state = armed_state(where)
        if state is not None:
            armed = armed or state
            refused.append(act)
    if not refused:
        return None
    return (f"Siegard refuses this command: {armed} is armed for this project, and a push, a "
            f"branch or a history rewrite is never a skill's, a goal's or a grant's. It runs "
            f"{'; '.join(dict.fromkeys(refused))}. Leave it out and go on with the route; where "
            f"the act is needed, hand it to the person, who runs it or ends the goal or the grant.")


def owner_of(path: Path, fields: dict) -> str | None:
    """Which script writes the file, or nothing where none of R9's files is it."""
    if path.name == "siegard-trace.json":
        return WRITTEN_BY["siegard-trace.json"]
    work = fields.get("work_root")
    delivery = fields.get("delivery_root")
    if work is not None and path.name == "plan.json" and path.parent.parent == work:
        return WRITTEN_BY["plan.json"]
    if delivery is not None and path.is_relative_to(delivery):
        parts = path.relative_to(delivery).parts
        if len(parts) == 2 and parts[1] == "delivery.json":
            return WRITTEN_BY["delivery.json"]
        if len(parts) >= 3 and parts[1] == "run":
            return WRITTEN_BY["run"]
    return None


def write_refusal(record: dict) -> str | None:
    named = (record.get("tool_input") or {}).get("file_path")
    if not isinstance(named, str) or not named:
        return None
    path = Path(named)
    if not path.is_absolute():
        start = start_of(record)
        if start is None:
            return None
        path = start / path
    path = Path(os.path.normpath(path))
    if path.name not in ("siegard-trace.json", "plan.json", "delivery.json") \
            and "run" not in path.parts:
        return None
    existing = path.parent
    while not existing.is_dir() and existing != existing.parent:
        existing = existing.parent
    sys.path.insert(0, str(HOOKS.parent / "bin"))
    from project import PROJECT_FILE, toplevel_of
    home = toplevel_of(existing, timeout=GIT_TIMEOUT_SECONDS)
    if not (home / PROJECT_FILE).is_file():
        return None
    with contextlib.redirect_stderr(io.StringIO()):
        import door
    fields, unresolved, _ = door.resolve(home)
    if unresolved:
        return None
    roots = {key: Path(os.path.normpath(fields[key].resolve()))
             for key in ("work_root", "delivery_root") if key in fields}
    resolved = Path(os.path.normpath(path.parent.resolve() / path.name))
    owner = owner_of(resolved, roots)
    if owner is None:
        return None
    return (f"Siegard refuses this write: {resolved} is written by {owner} alone, and a file a "
            f"script derives or captures is never written by hand. Change what the script reads "
            f"and run it again.")


def main() -> int:
    try:
        record = json.loads(sys.stdin.read() or "{}")
    except (ValueError, OSError):
        return 0
    if not isinstance(record, dict) or record.get("hook_event_name") not in (EVENT, None):
        return 0
    tool = record.get("tool_name")
    try:
        if tool == SHELL:
            reason = shell_refusal(record)
        elif tool in WRITERS:
            reason = write_refusal(record)
        else:
            reason = None
    except (Exception, SystemExit):
        return 0
    if not reason:
        return 0
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
