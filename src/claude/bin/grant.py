#!/usr/bin/env python3
"""Record the person's grant, and answer what it lets a session do at a stop without asking.

A grant is the person's own words, decided in advance, for the stops the framework would hand
back: «A grant is armed only by the person's own invocation of `/siegard-grant`, a skill closed to
the model, whose arguments are the person's words.» (SPEC-011 R1) It lets a session take a door a
handoff hands, make the commits a route owes, and close the initiative, each held to a gate this
script decides from disk and git alone. A run that asked itself whether an act was inside what
the person granted would answer from its own reading; this script answers from the record and the
tree.

**`--arm` records the words, then the grant.** The words are copied whole, by `ask.py --record`,
to a file under the telemetry root and named by their digest; the grant record sits inside the
repository's git directory beside the armed goal's, never in the tree. A project holds one armed
grant. «A grant holds at least one clause: `doors`, a list from `plan-work`, `implement-task`,
`review-change`, `reconcile` and `deliver-scope`, with a budget of judged doors, a whole number;
`commits`, which lets a session commit what the route wrote; `close`, the person's reason for
closing the initiative, in their words, which lets a session close it where R7 holds.» (SPEC-011 R2) The words a person types after the flags are the closing reason: they are recorded verbatim and
no other text is.

**`--decide` answers a stop's handoff record, one line per decision.** `stop: <why>`, `take: <door>
— precondition unmet — <fact>`, or `judge:` followed by the doors, the budget left and the
record's report, which the door decider reads. «A decision that carries `settles` is `stop`: the
choice is the person's.» (SPEC-011 R4) A door whose check answered `refuses` is excluded, and where
exactly one door remains, its entry point is in the grant's `doors` and its check accepted, it is
taken; where the recommended door's check accepted beside an open door, the decider chooses, within
the budget: «The budget left is the grant's budget less the judged `decided:` lines the
initiative's log gained since the grant armed, and a judged choice met with it spent is `stop`.»
(SPEC-011 R5)

**`--commit` and `--close` are the gates.** «`bin/grant.py --commit`, over the paths a commit
names, answers `accepts` only where the grant holds `commits` and every path is one the route
writes» (SPEC-011 R7). The first line of each answer is `accepts` or `refuses`, a `refused:` line
follows for every refusal and a `checked:` line for every check that passed.

Declared dependencies: PyYAML and jsonschema (through goal.py and spec.py, its siblings, which this
script imports; it runs ask.py and project.py as commands).

Usage:  grant.py --arm <project-root> --slug <slug> [--target <key>] [--doors <skill>[,<skill>...]] [--budget <n>] [--commits] [--close] --words-file <file|->
                                    record the person's words and arm the grant; --words-file is
                                    the text the person typed after the flags, copied verbatim
        grant.py --disarm <project-root>
                                    end the armed grant
        grant.py --read <project-root>
                                    print the armed grant, or say none is armed
        grant.py --decide <project-root> --record <file>
                                    answer each decision of a handoff record
        grant.py --commit <project-root> --file <path>...
                                    answer whether the grant lets a session commit these paths,
                                    spelled from the project root
        grant.py --close <project-root>
                                    answer whether the grant lets a session close the initiative
        grant.py --help             print this text and stop
Exit:   0 answered, armed, disarmed or read
        1 refused: an arming the checks refuse, with every reason, or a gate that answers `refuses`
        2 cannot run
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BIN = Path(__file__).resolve().parent
sys.path.insert(0, str(BIN))

from jsonschema import Draft202012Validator  # noqa: E402

import goal  # noqa: E402

CANNOT_RUN = 2
REFUSED = 1
ALLOWED = ("plan-work", "implement-task", "review-change", "reconcile", "deliver-scope")
CONTRACT = "grant-armed/1"
ARMED_FILE = "grant.json"
ENDED_FILE = "grants-ended.jsonl"
ASK_LINE = re.compile(r"^ask: (\S+) \(sha256 ([0-9a-f]{16})\)")
CREDENTIALS = re.compile(r"(^\.env|\.(pem|key|p12|pfx|jks)$|^id_(rsa|dsa|ecdsa|ed25519)|"
                         r"credential|secret|(^|/)\.ssh/|(^|/)\.aws/)", re.I)
CLOSED_AFTER = ("records", "review", "criteria", "delivery", "plan", "specification")


def grant_path(home: Path) -> Path:
    return goal.armed_path(home).with_name(ARMED_FILE)


def read_grant(path: Path) -> dict | None:
    record = goal.read_armed(path)
    return record if record is not None and record.get("contract") == CONTRACT else None


def end_grant(path: Path, record: dict, ended: str, reason: str) -> None:
    done = {**record, "ended": ended, "reason": reason,
            "ended_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    with (path.parent / ENDED_FILE).open("a", encoding="utf-8") as log:
        log.write(json.dumps(done) + "\n")
    path.unlink(missing_ok=True)


def fields_of(project_root: Path, target: str | None) -> dict:
    return goal.resolve(project_root, target)


def live_initiative(fields: dict, slug: str) -> list[str]:
    work = fields["work_root"] / slug
    found = []
    if not (work / "plan.json").is_file():
        found.append(f"{slug} names no live initiative: {work / 'plan.json'} does not exist")
    if (work / "closure.md").is_file():
        found.append(f"{slug} is closed: {work / 'closure.md'} exists")
    return found


def record_words(project_root: Path, text: str) -> tuple[Path, str]:
    done = subprocess.run([sys.executable, "-B", str(BIN / "ask.py"), "--record",
                           str(project_root), "--text-file", "-"],
                          input=text, capture_output=True, text=True)
    found = ASK_LINE.match(done.stdout) if done.returncode == 0 else None
    if found is None:
        raise goal.Refused(f"ask.py --record did not record the words: "
                           f"{(done.stdout + done.stderr).strip()}")
    return Path(found.group(1)), found.group(2)


def arm(project_root: Path, slug: str, target: str | None, doors: list[str], budget: int,
        commits: bool, close: bool, words: str) -> tuple[list[str], dict | None]:
    refused = []
    unknown = [door for door in doors if door not in ALLOWED]
    if unknown:
        refused.append(f"{', '.join(unknown)} is outside `doors`, which names only "
                       f"{', '.join(ALLOWED)}")
    if not doors and not commits and not close:
        refused.append("no clause is named: `doors`, `commits` or `close`")
    if budget and not doors:
        refused.append("a budget of judged doors needs `doors`")
    if close and not words.strip():
        refused.append("`close` is the person's reason in their words, and the words are empty")
    fields = fields_of(project_root, target)
    refused += live_initiative(fields, slug)
    path = grant_path(fields["home"])
    if path.exists():
        held = read_grant(path) or {}
        refused.append(f"a grant is armed already in this project — {held.get('slug', 'unreadable')}"
                       f", armed at {held.get('armed_at', 'unknown')}; `grant.py --disarm "
                       f"{project_root}` ends it")
    if refused:
        return refused, None
    words_path, digest = record_words(project_root, words)
    record = {"contract": CONTRACT, "project_root": str(project_root), "slug": slug,
              "target": fields["target"], "doors": doors, "budget": budget, "commits": commits,
              "close": close, "words": {"path": goal.relative(fields, words_path),
                                        "sha256": digest},
              "version": goal.plugin_version(),
              "since": goal.git(fields["home"], "rev-parse", "HEAD"),
              "armed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    held_contract = json.loads((BIN.parent / "schemas" / "grant.json").read_text(encoding="utf-8"))
    broken = sorted(error.message for error in Draft202012Validator(held_contract).iter_errors(record))
    if broken:
        return [f"the record does not satisfy schemas/grant.json: {reason}" for reason in broken], None
    goal.write_armed(path, record)
    return [f"armed: {path}", f"words: {record['words']['path']} (sha256 {digest})"], record


def standing(project_root: Path) -> tuple[dict, dict, Path, str | None]:
    """The armed grant and its project, with the reason it no longer stands where one applies."""
    home = Path(goal.command(["git", "-C", str(project_root), "rev-parse", "--show-toplevel"])[1])
    path = grant_path(home)
    held = read_grant(path) if path.exists() else None
    if held is None:
        raise goal.Refused("no grant is armed in this project")
    fields = goal.resolve(project_root, held["target"])
    ended = None
    if held["version"] != goal.plugin_version():
        ended = (f"the plugin runs {goal.plugin_version()}; the grant was armed under "
                 f"{held['version']}")
    elif (fields["work_root"] / held["slug"] / "closure.md").is_file():
        ended = f"{held['slug']} holds a closure.md"
    return held, fields, path, ended


def log_file(fields: dict, held: dict) -> Path:
    return fields["delivery_root"] / held["slug"] / "orchestration.md"


def budget_left(fields: dict, held: dict) -> int:
    path = log_file(fields, held)
    taken = goal.judged_taken(fields, held["since"], path) if path.is_file() else 0
    return max(0, held["budget"] - taken)


def skill_of(door: dict) -> str | None:
    entry = door.get("entry")
    return entry.lstrip("/") if isinstance(entry, str) else None


def decide_one(number: int, decision: dict, held: dict, fields: dict) -> list[str]:
    head = f"decision {number}:"
    if decision.get("settles"):
        return [f"{head} stop: the choice is the person's, and the record says what would settle "
                f"it"]
    offered = ([decision["recommended"]] if decision.get("recommended") else []) \
        + list(decision.get("others") or [])
    excluded = [door for door in offered if (door.get("check") or {}).get("answer") == "refuses"]
    remaining = [door for door in offered if door not in excluded]
    if not remaining:
        return [f"{head} stop: every door the handoff hands is excluded"]
    if len(remaining) == 1 and excluded:
        door = remaining[0]
        skill = skill_of(door)
        answer = (door.get("check") or {}).get("answer")
        if skill not in held["doors"]:
            return [f"{head} stop: the one door left, {skill or 'with no entry point'}, is not in "
                    f"the grant's doors"]
        if answer != "accepts":
            return [f"{head} stop: the one door left was not checked by `door.py --check`"]
        facts = "; ".join(f"{item}" for item in
                          (fact for gone in excluded for fact in
                           (gone.get("check") or {}).get("refused", [])))[:300]
        return [f"{head} take: {door['reply_word']} /{skill} — precondition unmet — "
                f"{facts or 'every other door is excluded by its own check'} "
                f"(grant sha256 {held['words']['sha256']})"]
    recommended = decision.get("recommended")
    if recommended is None or skill_of(recommended) not in held["doors"]:
        return [f"{head} stop: no recommended door is in the grant's doors"]
    if (recommended.get("check") or {}).get("answer") != "accepts":
        return [f"{head} stop: the recommended door was not accepted by `door.py --check`"]
    left = budget_left(fields, held)
    if left <= 0:
        return [f"{head} stop: the grant's budget of judged doors is spent"]
    lines = [f"{head} judge: spawn the door decider over these doors, budget left {left}"]
    for door in remaining:
        entry = door.get("entry") or "no entry point"
        what = door.get("what_it_does") or door.get("door") or ""
        lines.append(f"  door {door['reply_word']}: {entry} — {what}")
    return lines


def decide(project_root: Path, record: dict) -> tuple[list[str], int]:
    held, fields, path, ended = standing(project_root)
    if ended:
        end_grant(path, held, "ended", ended)
        return [f"stop: the grant ended — {ended}"], REFUSED
    decisions = record.get("decisions") or []
    lines = [f"grant: {held['slug']} (sha256 {held['words']['sha256']})"]
    for number, decision in enumerate(decisions, 1):
        lines += decide_one(number, decision, held, fields)
    if record.get("report"):
        lines.append(f"report: {record['report']}")
    return lines, 0


def owned_paths(fields: dict, held: dict) -> set[str]:
    owned: set[str] = set()
    home = fields["home"].resolve()
    for root in ("implementation", "proof"):
        base = fields["delivery_root"] / held["slug"] / root
        for record in sorted(base.rglob("*.md")) if base.is_dir() else []:
            front = goal.front_of(record)
            target = fields["targets"].get(front.get("target") or held["target"])
            if target is None:
                continue
            named = [entry.get("path") for entry in front.get("files") or []
                     if isinstance(entry, dict)]
            named += [entry.get("file") for entry in front.get("tests") or []
                      if isinstance(entry, dict)]
            for name in named:
                if isinstance(name, str):
                    full = (target / name).resolve()
                    if full.is_relative_to(home):
                        owned.add(full.relative_to(home).as_posix())
    return owned


def route_roots(fields: dict, held: dict) -> list[str]:
    home = fields["home"].resolve()
    chosen = [fields["delivery_root"] / held["slug"], fields["work_root"] / held["slug"],
              fields["telemetry_root"], home / "siegard-reconcile", home / "siegard-trace.json"]
    return [goal.relative(fields, item).rstrip("/") for item in chosen]


def commit_gate(project_root: Path, files: list[str]) -> tuple[list[str], bool]:
    held, fields, path, ended = standing(project_root)
    if ended:
        end_grant(path, held, "ended", ended)
        return [f"refused: the grant ended — {ended}"], False
    found: list[str] = []
    if not held["commits"]:
        found.append("refused: the grant holds no `commits` clause")
    if not files:
        found.append("refused: no path is named; a commit is held to the paths it names")
    home = fields["home"].resolve()
    standards = {goal.relative(fields, item) for item in fields["standards"]}
    roots_ = route_roots(fields, held)
    owned = owned_paths(fields, held)
    specification = goal.relative(fields, fields["specification_root"]).rstrip("/")
    for raw in files:
        spelled = (home / raw).resolve()
        if not spelled.is_relative_to(home):
            found.append(f"refused: {raw} is outside the project")
            continue
        name = spelled.relative_to(home).as_posix()
        base = spelled.name
        if name == "siegard.json" or name in standards:
            found.append(f"refused: {name} is the person's own file: the project file or a "
                         f"standard it declares")
        elif base == "CLAUDE.md":
            found.append(f"refused: {name} is CLAUDE.md, which only the person changes")
        elif CREDENTIALS.search(base) or CREDENTIALS.search(name):
            found.append(f"refused: {name} names a file that holds credentials")
        elif base == "closure.md" and not held["close"]:
            found.append(f"refused: {name} closes the initiative, and the grant holds no `close` "
                         f"clause")
        elif name == specification or name.startswith(specification + "/"):
            node = name[:-len(".log.md")] + ".md" if name.endswith(".log.md") else name
            held_at_head = subprocess.run(["git", "-C", str(home), "cat-file", "-e",
                                           f"HEAD:{node}"], capture_output=True).returncode == 0
            if name.endswith(".log.md") and held_at_head:
                continue
            if held_at_head and name not in owned:
                found.append(f"refused: {name} is a specification file HEAD already holds, and "
                             f"the commit modifies it")
            elif not held_at_head and name not in owned and not any(
                    name == root or name.startswith(root + "/") for root in roots_):
                found.append(f"refused: {name} is no path the route writes")
        elif not (name in owned or any(name == root or name.startswith(root + "/")
                                       for root in roots_)):
            found.append(f"refused: {name} is no path the route writes: no record of "
                         f"{held['slug']} names it, and it is under none of its roots")
    if not found:
        found = [f"checked: the grant holds `commits` for {held['slug']}",
                 f"checked: {len(files)} path(s), each one the route writes, none a standard, "
                 f"CLAUDE.md, a credential, a closure or a modified specification file"]
    return found, not any(line.startswith("refused:") for line in found)


def close_gate(project_root: Path) -> tuple[list[str], bool]:
    held, fields, path, ended = standing(project_root)
    if ended:
        end_grant(path, held, "ended", ended)
        return [f"refused: the grant ended — {ended}"], False
    if not held["close"]:
        return ["refused: the grant holds no `close` clause"], False
    try:
        found, _ = goal.checks(fields, held["slug"], held["since"], held["version"], [], [], None)
    except goal.Refused as refusal:
        return [f"refused: the initiative's state could not be read: {refusal}"], False
    lines = []
    for name in CLOSED_AFTER:
        ok, out = found.get(name, (False, "no answer"))
        if ok:
            lines.append(f"checked: {name} — {out.splitlines()[0] if out else 'passes'}")
        else:
            lines.append(f"refused: {name}")
            lines += [f"  {line}" for line in out.splitlines()]
    return lines, not any(line.startswith("refused:") for line in lines)


def take(args: list[str], flag: str) -> str | None:
    if flag not in args:
        return None
    at = args.index(flag)
    if at + 1 >= len(args) or args[at + 1].startswith("--"):
        raise goal.Refused(f"{flag} takes a value")
    value = args[at + 1]
    del args[at:at + 2]
    return value


def words_from(source: str) -> str:
    if source == "-":
        return sys.stdin.read()
    return Path(source).read_text(encoding="utf-8")


def main(argv: list[str]) -> int:
    args = list(argv)
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    flag = args.pop(0)
    try:
        if flag == "--arm":
            if not args:
                raise goal.Refused("--arm takes the project root first")
            project_root = Path(args.pop(0)).resolve()
            slug = take(args, "--slug")
            target = take(args, "--target")
            doors_text = take(args, "--doors")
            budget_text = take(args, "--budget")
            source = take(args, "--words-file")
            commits, close = "--commits" in args, "--close" in args
            for word in ("--commits", "--close"):
                if word in args:
                    args.remove(word)
            if args or slug is None or source is None:
                raise goal.Refused("--arm takes <project-root> --slug <slug> --words-file <file|-> "
                                   "and the clauses; nothing else")
            doors = [door for door in (doors_text or "").split(",") if door]
            if budget_text is not None and not budget_text.isdigit():
                raise goal.Refused("--budget is a whole number")
            lines, record = arm(project_root, slug, target, doors, int(budget_text or 0),
                                commits, close, words_from(source))
            print("\n".join(lines))
            return 0 if record else REFUSED
        if flag in ("--disarm", "--read", "--close", "--decide", "--commit"):
            if not args:
                raise goal.Refused(f"{flag} takes the project root first")
            project_root = Path(args.pop(0)).resolve()
            if flag == "--disarm":
                held, _, path, _ = standing(project_root)
                end_grant(path, held, "disarmed", "the person disarmed it")
                print(f"disarmed: {held['slug']}, armed at {held['armed_at']}")
                return 0
            if flag == "--read":
                try:
                    held, _, path, ended = standing(project_root)
                except goal.Refused:
                    print("no grant is armed in this project")
                    return 0
                print(json.dumps(held, indent=2))
                if ended:
                    print(f"ended: {ended}")
                return 0
            if flag == "--close":
                lines, ok = close_gate(project_root)
                print("accepts" if ok else "refuses")
                print("\n".join(lines))
                return 0 if ok else REFUSED
            if flag == "--commit":
                files = []
                while "--file" in args:
                    files.append(take(args, "--file"))
                if args:
                    raise goal.Refused("--commit takes <project-root> and --file <path>...")
                lines, ok = commit_gate(project_root, files)
                print("accepts" if ok else "refuses")
                print("\n".join(lines))
                return 0 if ok else REFUSED
            source = take(args, "--record")
            if source is None or args:
                raise goal.Refused("--decide takes <project-root> --record <file>")
            try:
                record = json.loads(Path(source).read_text(encoding="utf-8"))
            except (OSError, ValueError) as broken:
                raise goal.Refused(f"{source} is no handoff record: {broken}")
            lines, code = decide(project_root, record)
            print("\n".join(lines))
            return code
    except goal.Refused as refusal:
        print(f"cannot run: {refusal}", file=sys.stderr)
        return CANNOT_RUN
    print(f"cannot run: {flag} is no flag of this script; --help prints them", file=sys.stderr)
    return CANNOT_RUN


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
