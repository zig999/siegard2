#!/usr/bin/env python3
"""Record the person's grant, and answer what it lets a session do at a stop without asking.

A grant is the person's own words, decided in advance, for the stops the framework would hand
back: «A grant is armed only by the person's own invocation of `/siegard-grant`, a skill closed to
the model, whose arguments are the person's words.» (SPEC-011 R1) It lets a session take a door a
handoff hands, make the commits a route owes, and close the initiative, each held to a gate this
script decides from disk and git alone. A run that asked itself whether an act was inside what
the person granted would answer from its own reading; this script answers from the record and the
tree.

**`--arm` records the words, then the grant.** The words are the person's invocation of
`/siegard-grant` as typed — its flags, and any sentence after them — and are copied whole, by
`ask.py --record`, to a file under the telemetry root and named by their digest; an invocation
that names nothing is refused and arms nothing. The grant is told apart by its mark, the words'
digest taken with the instant it was armed, so two grants armed with the same invocation never
share one. The grant record sits inside the
repository's git directory beside the armed goal's, never in the tree. A project holds one armed
grant. «A grant holds at least one clause: `doors`, a list from `plan-work`, `implement-task`,
`review-change`, `reconcile`, `deliver-scope` and `analyse`, which is all six where the person names
none, with a budget of judged doors for each initiative it covers, a whole number, which is
zero where the person names none;
`commits`, which lets a session commit, short of the paths R7 keeps; `close`, which lets a session
close an initiative where R7 holds, the grant's words being the reason it is closed under.»
(SPEC-011 R2) The recorded invocation is the closing reason: it is recorded verbatim and no
other text is. `routes`, named alone by `--routes`, lets the grant hold the choice of route for a
request that names none: «The route a finding deserves, an end-to-end route (`/deliver-scope`,
`/adopt-scope`) and a corrective increment are never a grant's route (R8).» (SPEC-011 R14) A
routing record `handoff.py --prepare --route` wrote is answered like a stop's, over `/analyse` and
`/plan-work` alone, within a budget the grant counts in the delivery root's own log; a grant
without it answers every routing decision `stop`.

**`--decide` answers a stop's handoff record, one line per decision.** `stop: <why>`, `take: <door>
— precondition unmet — <fact>`, or `judge:` followed by the doors, the budget left and the
record's report, which the door decider reads. «A decision that carries `settles` is `stop`: the
choice is the person's.» (SPEC-011 R4) «A decision over an initiative the grant does not cover is
`stop`» (SPEC-011 R4): under a grant naming one initiative, a record over another, or naming
none, is answered `stop: the grant covers <slug>, not <initiative>`. A door whose check answered `refuses` is excluded, and where
exactly one door remains, the only one a handoff hands included, its entry point is in the grant's
`doors` and its check accepted, it is taken; where the recommended door's check accepted beside an open door, the decider chooses, within
the budget of the stopped initiative: «The budget left is the grant's budget less the judged
`decided:` lines the stopped initiative's log gained since the grant armed, each covered
initiative counted apart, and a judged choice met with it spent is `stop`.» (SPEC-011 R5)

**`--commit` and `--close` are the gates.** «`bin/grant.py --commit`, over the paths a commit
names, answers `accepts` where the grant holds `commits` and no path is outside the project, a path
of `siegard.json`, a declared standard, `CLAUDE.md`, a file that holds credentials (an `.env` example, sample or template file holds none), a
`closure.md` while the close clause does not hold, or the routing log while the grant holds no `routes` clause»
(SPEC-011 R7). The first line of each answer is `accepts` or `refuses`, a `refused:` line
follows for every refusal and a `checked:` line for every check that passed.

Declared dependencies: PyYAML and jsonschema (through goal.py and spec.py, its siblings, which this
script imports; it runs ask.py and project.py as commands).

Usage:  grant.py --arm <project-root> [--slug <slug>] [--target <key>] [--doors <skill>[,<skill>...]|none] [--budget <n>] [--commits] [--close] [--routes] --words-file <file|->
                                    record the person's words and arm the grant for the project, or
                                    for one initiative where --slug names it; --words-file is the
                                    text the person typed after the flags, copied verbatim; --doors
                                    names the entry points a stop may take, all six where it is
                                    absent, and `none` where the grant is for commits or a closing
                                    alone; --routes lets it hold the choice of route for a request,
                                    never with --slug, and only where --doors holds analyse or
                                    plan-work
        grant.py --disarm <project-root>
                                    end the armed grant, which is what /siegard-grant --clear runs
        grant.py --read <project-root>
                                    print the armed grant, or say none is armed
        grant.py --decide <project-root> (--record <file> | --latest <skill> --after <commit>) --slug <slug>
                                    answer each decision of a handoff record; --latest reads the
                                    newest record `handoff.py --render` kept for that skill after
                                    that commit, and refuses where none was; --slug names the
                                    stopped initiative, whose budget a judged choice draws on,
                                    where the grant names none
        grant.py --commit <project-root> --file <path>...
                                    answer whether the grant lets a session commit these paths,
                                    spelled from the project root
        grant.py --close <project-root> [--slug <slug>]
                                    answer whether the grant lets a session close one initiative;
                                    --slug names it where the grant names none
        grant.py --help             print this text and stop
Exit:   0 answered, armed, disarmed or read
        1 refused: an arming the checks refuse, with every reason, or a gate that answers `refuses`
        2 cannot run
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BIN = Path(__file__).resolve().parent
sys.path.insert(0, str(BIN))
sys.path.insert(0, str(BIN.parent / "hooks"))

from jsonschema import Draft202012Validator  # noqa: E402

import goal  # noqa: E402
import turn  # noqa: E402

CANNOT_RUN = 2
REFUSED = 1
ALLOWED = ("plan-work", "implement-task", "review-change", "reconcile", "deliver-scope", "analyse")
CONTRACT = "grant-armed/1"
ARMED_FILE = "grant.json"
ENDED_FILE = "grants-ended.jsonl"
ASK_LINE = re.compile(r"^ask: (\S+) \(sha256 ([0-9a-f]{16})\)")
CREDENTIALS = re.compile(r"(^\.env|\.(pem|key|p12|pfx|jks)$|^id_(rsa|dsa|ecdsa|ed25519)|"
                         r"credential|secret|(^|/)\.ssh/|(^|/)\.aws/)", re.I)
EXAMPLE_ENV = re.compile(r"^\.env(\.[\w-]+)*\.(example|sample|template)$", re.I)
CLOSED_AFTER = ("records", "review", "criteria", "delivery", "plan", "specification")
ROUTE_DOORS = ("analyse", "plan-work")


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


def mark_of(held: dict) -> str:
    """The digest a grant is told apart by: its words' digest taken with the instant it was
    armed, so two grants armed with the same invocation never share one. «A `decided:` line a
    grant took ends `(grant sha256 <digest>)`, and the grant's budget counts it.» (SPEC-011 R10)
    A record from before the mark existed is told apart by its words."""
    return held.get("mark") or held["words"]["sha256"]


def fields_of(project_root: Path, target: str | None) -> tuple[dict, str | None]:
    """The project's roots, and a line saying which target was taken where the person named none
    and the project declares several: the target only names where a record's own target is
    missing, and a grant takes nothing from it that a record does not carry."""
    said = None
    if target is None:
        code, out = goal.script("project.py", str(project_root))
        keys = sorted(re.findall(r"^target (\S+):", out, re.M)) if code == 0 else []
        if len(keys) > 1:
            said = (f"target: {keys[0]} — decided: the first of {', '.join(keys)}; a record's own "
                    f"target is read where it names one")
        target = keys[0] if keys else None
    return goal.resolve(project_root, target), said


def live_initiative(fields: dict, slug: str) -> list[str]:
    work = fields["work_root"] / slug
    found = []
    if not (work / "plan.json").is_file():
        found.append(f"{slug} names no live initiative: {work / 'plan.json'} does not exist")
    if (work / "closure.md").is_file():
        found.append(f"{slug} is closed: {work / 'closure.md'} exists")
    return found


def closed(fields: dict, slug: str) -> bool:
    """Whether an initiative's closure has landed: «An initiative holds its `closure.md` once
    `HEAD` holds it» (SPEC-011 R3). A closure written and not yet committed is the commit the
    closing still owes, and the gate that answers it reads the initiative as covered until then."""
    marker = goal.relative(fields, fields["work_root"] / slug / "closure.md")
    return goal.command(["git", "-C", str(fields["home"]), "cat-file", "-e",
                         f"HEAD:{marker}"])[0] == 0


def covered(fields: dict, held: dict) -> list[str]:
    """The initiatives a grant covers: the one it names, or every live one of the project."""
    if held.get("slug"):
        return [held["slug"]]
    base = fields["work_root"]
    return sorted(path.parent.name for path in base.glob("*/plan.json")
                  if not closed(fields, path.parent.name)) if base.is_dir() else []


def record_words(project_root: Path, text: str) -> tuple[Path, str]:
    done = subprocess.run([sys.executable, "-B", str(BIN / "ask.py"), "--record",
                           str(project_root), "--text-file", "-"],
                          input=text, capture_output=True, text=True)
    found = ASK_LINE.match(done.stdout) if done.returncode == 0 else None
    if found is None:
        raise goal.Refused(f"ask.py --record did not record the words: "
                           f"{(done.stdout + done.stderr).strip()}")
    return Path(found.group(1)), found.group(2)


def replaced_line(held: dict) -> str:
    """What the arming over a standing grant ended, so that a narrower or wider grant never
    replaces another unread: «An arming over a grant that still stands ends it in that log as
    `replaced`, says what it held» (SPEC-011 R3)"""
    held_doors = ", ".join(held.get("doors") or []) or "none"
    return (f"the grant armed at {held.get('armed_at', 'unknown')} is replaced by this arming — it "
            f"covered {held.get('slug') or 'every live initiative of the project'}, doors "
            f"{held_doors}, budget {held.get('budget', 0)}, commits "
            f"{'yes' if held.get('commits') else 'no'}, close {'yes' if held.get('close') else 'no'}, "
            f"routes {'yes' if held.get('routes') else 'no'}, "
            f"mark (grant sha256 {mark_of(held) if held else 'unknown'})")


def arm(project_root: Path, slug: str | None, target: str | None, doors: list[str] | None,
        budget: int, commits: bool, close: bool, words: str,
        routes: bool = False) -> tuple[list[str], dict | None]:
    doors = list(ALLOWED) if doors is None else doors
    refused = []
    unknown = [door for door in doors if door not in ALLOWED]
    if unknown:
        refused.append(f"{', '.join(unknown)} is outside `doors`, which names only "
                       f"{', '.join(ALLOWED)}")
    if not doors and not commits and not close:
        refused.append("no clause is named: `doors` is none, and neither `commits` nor `close` "
                       "is named")
    if budget and not doors:
        refused.append("a budget of judged doors needs `doors`")
    if routes and slug:
        refused.append("`routes` never covers one initiative: a request's route opens a new "
                       "initiative or changes the specification, so a grant naming --slug holds "
                       "no `routes`")
    if routes and not any(door in doors for door in ROUTE_DOORS):
        refused.append(f"`routes` needs `doors` to hold {' or '.join(ROUTE_DOORS)}, the only "
                       f"entry points a grant's route takes")
    if not words.strip():
        refused.append("the invocation names nothing: a grant is armed by the person's own "
                       "arguments — at least one of --doors, --budget, --commits, --close or --routes — "
                       "recorded as typed, and an invocation with none arms nothing")
    fields, said = fields_of(project_root, target)
    refused += live_initiative(fields, slug) if slug else []
    path = grant_path(fields["home"])
    held = read_grant(path) if path.exists() else None
    over = no_longer_stands(fields, held) if held is not None else None
    if refused:
        return refused, None
    if path.exists():
        held = held or {}
        gone = (f"the grant armed at {held.get('armed_at', 'unknown')} — {over}" if over is not None
                else replaced_line(held))
        said = "\n".join(line for line in (said, f"ended: {gone}") if line)
    words_path, digest = record_words(project_root, words)
    armed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    record = {"contract": CONTRACT, "project_root": str(project_root), "slug": slug,
              "target": fields["target"], "doors": doors, "budget": budget, "commits": commits,
              "close": close, "routes": routes, "words": {"path": goal.relative(fields, words_path),
                                        "sha256": digest},
              "version": goal.plugin_version(),
              "since": goal.git(fields["home"], "rev-parse", "HEAD"),
              "armed_at": armed_at,
              "mark": hashlib.sha256(f"{digest} {armed_at}".encode("utf-8")).hexdigest()[:16]}
    held_contract = json.loads((BIN.parent / "schemas" / "grant.json").read_text(encoding="utf-8"))
    broken = sorted(error.message for error in Draft202012Validator(held_contract).iter_errors(record))
    if broken:
        return [f"the record does not satisfy schemas/grant.json: {reason}" for reason in broken], None
    if path.exists():
        end_grant(path, held, "ended" if over is not None else "replaced",
                  over if over is not None else "replaced by a new arming")
    goal.write_armed(path, record)
    summary = [f"armed: {path}", f"words: {record['words']['path']} (sha256 {digest})",
               f"mark: (grant sha256 {record['mark']}) — the words with the instant armed",
               f"covers: {slug or 'every live initiative of the project'}",
               f"doors: {', '.join(doors) or 'none'}", f"budget of judged doors for each initiative: {budget}",
               f"commits: {'yes' if commits else 'no'}", f"close: {'yes' if close else 'no'}",
               f"routes: {'yes' if routes else 'no'}",
               f"plugin: {record['version']}"] + ([goal.GRANT_COMMITS_LINE] if commits else []) \
        + ([goal.GRANT_ROUTES_LINE] if routes else [])
    return ([said] if said else []) + summary, record


def standing(project_root: Path) -> tuple[dict, dict, Path, str | None]:
    """The armed grant and its project, with the reason it no longer stands where one applies."""
    home = Path(goal.command(["git", "-C", str(project_root), "rev-parse", "--show-toplevel"])[1])
    path = grant_path(home)
    held = read_grant(path) if path.exists() else None
    if held is None:
        raise goal.Refused("no grant is armed in this project")
    fields = goal.resolve(project_root, held["target"])
    return held, fields, path, no_longer_stands(fields, held)


def no_longer_stands(fields: dict, held: dict) -> str | None:
    """Why an armed grant has ended though its record is still in place, or None where it
    stands: «A grant ends when the person clears it and, where it names an initiative, when that
    initiative holds a `closure.md`. A change of the plugin's version ends no grant»
    (SPEC-011 R3)."""
    if held.get("slug") and closed(fields, held["slug"]):
        return f"{held['slug']} holds a closure.md"
    return None


def budget_left(fields: dict, held: dict, slug: str | None) -> int:
    """The judged doors the grant may still take over one initiative: its budget less the lines
    carrying its mark that the initiative's own log gained since it armed. A stop that names no
    initiative the grant covers has no budget to draw on."""
    if slug is None or slug not in covered(fields, held):
        return 0
    path = fields["delivery_root"] / slug / "orchestration.md"
    taken = goal.judged_taken(fields, held["since"], path, mark_of(held)) if path.is_file() else 0
    return max(0, held["budget"] - taken)


def routing_log(fields: dict) -> Path:
    return fields["delivery_root"] / "orchestration.md"


def routing_budget_left(fields: dict, held: dict) -> int:
    """The judged routes the grant may still take: its budget less the judged `decided:` lines
    carrying its mark that the delivery root's own log holds beyond what it held when the grant
    armed, read on disk, so a line written and not yet committed is counted too: «The routing
    budget is the grant's budget less the judged `decided:` lines carrying its mark that the
    delivery root's own `orchestration.md` holds on disk beyond what it held when the grant armed»
    (SPEC-011 R14)."""
    path = routing_log(fields)
    if not path.is_file():
        return held["budget"]
    at = goal.relative(fields, path)
    before = subprocess.run(["git", "-C", str(fields["home"]), "show", f"{held['since']}:{at}"],
                            capture_output=True, text=True).stdout
    earlier = [line.strip() for line in before.splitlines()]
    taken = 0
    for line in (line.strip() for line in path.read_text(encoding="utf-8").splitlines()):
        found = goal.log_line(line)
        if line in earlier:
            earlier.remove(line)
        elif goal.TAKEN_JUDGED.match(found) and f"{goal.GRANT_MARK}{mark_of(held)})" in found:
            taken += 1
    return max(0, held["budget"] - taken)


def is_routing(record: dict) -> bool:
    """Whether a handoff record is a routing record `handoff.py --prepare --route` wrote, as the
    script that writes it tells one apart."""
    import handoff
    return handoff.is_routing(record)


def skill_of(door: dict) -> str | None:
    entry = door.get("entry")
    return entry.lstrip("/") if isinstance(entry, str) else None


def decide_one(number: int, decision: dict, held: dict, fields: dict,
               slug: str | None = None, routing: bool = False) -> list[str]:
    head = f"decision {number}:"
    if routing and not held.get("routes"):
        return [f"{head} stop: the grant holds no `routes`, so the route is the person's to name "
                f"or to accept"]
    if decision.get("settles"):
        return [f"{head} stop: the choice is the person's, and the record says what would settle "
                f"it"]
    offered = ([decision["recommended"]] if decision.get("recommended") else []) \
        + list(decision.get("others") or [])
    if routing:
        chosen = decision.get("recommended")
        if chosen and skill_of(chosen) not in ROUTE_DOORS:
            return [f"{head} stop: the recommended route, "
                    f"{skill_of(chosen) or 'with no entry point'}, is the person's: a grant's "
                    f"route takes only {' or '.join('/' + door for door in ROUTE_DOORS)}"]
        offered = [door for door in offered if skill_of(door) in ROUTE_DOORS]
    excluded = [door for door in offered if (door.get("check") or {}).get("answer") == "refuses"]
    remaining = [door for door in offered if door not in excluded]
    if not remaining:
        return [f"{head} stop: every door the handoff hands is excluded"]
    if len(remaining) == 1:
        door = remaining[0]
        skill = skill_of(door)
        answer = (door.get("check") or {}).get("answer")
        if skill not in held["doors"]:
            return [f"{head} stop: the one door left, {skill or 'with no entry point'}, is not in "
                    f"the grant's doors"]
        if answer != "accepts":
            return [f"{head} stop: the one door left was not checked by `door.py --check`"]
        if not excluded:
            return [f"{head} take: {door['reply_word']} /{skill}",
                    f"  decided: /{skill} — precondition unmet — the handoff hands no other door "
                    f"and its own check accepted (grant sha256 {mark_of(held)})"]
        facts = "; ".join(f"{item}" for item in
                          (fact for gone in excluded for fact in
                           (gone.get("check") or {}).get("refused", [])))[:300]
        return [f"{head} take: {door['reply_word']} /{skill}",
                f"  decided: /{skill} — precondition unmet — the other door was refused by its "
                f"own check: {facts or 'every other door is excluded'} "
                f"(grant sha256 {mark_of(held)})"]
    recommended = decision.get("recommended")
    if recommended is None or skill_of(recommended) not in held["doors"]:
        return [f"{head} stop: no recommended door is in the grant's doors"]
    if (recommended.get("check") or {}).get("answer") != "accepts":
        return [f"{head} stop: the recommended door was not accepted by `door.py --check`"]
    if not routing and (slug is None or slug not in covered(fields, held)):
        return [f"{head} stop: "
                + (f"{slug} is no initiative the grant covers" if slug else
                   "the stop names no initiative, and a judged door draws on one initiative's "
                   "budget; `--slug` names it")
                + " — no budget is drawn on, none is spent"]
    left = routing_budget_left(fields, held) if routing else budget_left(fields, held, slug)
    if left <= 0:
        return [f"{head} stop: the grant's budget of judged "
                + ("routes is spent" if routing else f"doors for {slug} is spent")]
    lines = [f"{head} judge: spawn the door decider over these doors, budget left {left}; end the "
             f"deciding fact of the `decided:` line with `(grant sha256 {mark_of(held)})`"]
    for door in remaining:
        entry = door.get("entry") or "no entry point"
        what = door.get("what_it_does") or door.get("door") or ""
        inferred = (door.get("check") or {}).get("inferred_slug")
        lines.append(f"  door {door['reply_word']}: {entry} — {what}"
                     + (f" (its check ran over {inferred}, which the record did not name)"
                        if inferred else ""))
    return lines


CARRY = ("carry: each decision line below is carried out by its kind — a take is taken, its door "
         "invoked and the `decided` line under it written in the run's orchestration log, or for a "
         "route in the delivery root's own orchestration.md, the route invoked over the record's "
         "slug with the recorded request's file as its material, never a paraphrase; a judge "
         "goes to `siegard:door-decider` over the doors it prints and nothing else; a stop is "
         "handed to the person; a note is carried as it says, and the handoff rendered again")


def new_initiative(fields: dict, decision: dict) -> str | None:
    """The initiative with no plan a decision's `/plan-work` invocation names, or None: «A grant
    never takes `/plan-work` over an initiative that holds no plan outside a routing record»
    (SPEC-011 R4)."""
    import handoff
    invocation = str(decision.get("invocation") or "")
    opening = handoff.INVOCATION_ENTRY.match(invocation)
    if not opening or opening.group(1) != "plan-work":
        return None
    armed = handoff.armed_goal(fields["home"])
    for named in handoff.INVOCATION_SLUG.findall(invocation):
        slug = named.strip("`'\".,;:)(")
        if not slug or slug.startswith("<") or (armed and armed.get("slug") == slug):
            continue
        if not (fields["work_root"] / slug / "plan.json").is_file():
            return slug
    return None


def reconcile_taken(fields: dict, held: dict, slug: str | None) -> bool:
    """Whether the initiative's log, as committed since the grant armed, holds the scope's end
    `/reconcile` this grant took: «A scope's end whose `/reconcile` this grant already took in the
    initiative is answered `stop`» (SPEC-011 R4), so the report's render never takes it again; a
    `/reconcile` taken mid-run is not that one."""
    if not slug:
        return False
    path = fields["delivery_root"] / slug / "orchestration.md"
    if not path.is_file():
        return False
    at = goal.relative(fields, path)
    now = subprocess.run(["git", "-C", str(fields["home"]), "show", f"HEAD:{at}"],
                         capture_output=True, text=True).stdout
    before = subprocess.run(["git", "-C", str(fields["home"]), "show", f"{held['since']}:{at}"],
                            capture_output=True, text=True).stdout
    earlier = [line.strip() for line in before.splitlines()]
    for line in (line.strip() for line in now.splitlines()):
        if line in earlier:
            earlier.remove(line)
        elif goal.log_line(line).startswith("decided: /reconcile") and "at the scope's end" in line \
                and f"{goal.GRANT_MARK}{mark_of(held)})" in line:
            return True
    return False


def uncovered(held: dict, named: list[str | None], decision: dict) -> str | None:
    """The initiative outside a grant naming one that a decision is over, or None where the grant
    covers it: «A decision over an initiative the grant does not cover is `stop`» (SPEC-011 R4) —
    the caller's `--slug`, the record's initiative, the `--slug` of the decision's invocation, or
    the initiative a door's check ran over, any one outside; a record naming none is outside too.
    A `/reconcile` door's slug names a reconciliation, never an initiative, and is not read."""
    import handoff
    if not held.get("slug"):
        return None
    named = [name for name in named if name]
    if not named:
        return "an initiative the record does not name"
    invocation = str(decision.get("invocation") or "")
    if not invocation.lstrip().startswith(("/reconcile", "/siegard:reconcile")):
        named += handoff.INVOCATION_SLUG.findall(invocation)
    for door in ([decision.get("recommended")] if decision.get("recommended") else []) \
            + list(decision.get("others") or []):
        inferred = (door.get("check") or {}).get("inferred_slug") if isinstance(door, dict) else None
        if isinstance(inferred, str) and skill_of(door) != "reconcile":
            named.append(inferred)
    return next((name for name in named if name != held["slug"]), None)


def decide(project_root: Path, record: dict, slug: str | None = None) -> tuple[list[str], int]:
    held, fields, path, ended = standing(project_root)
    if ended:
        end_grant(path, held, "ended", ended)
        return [f"stop: the grant ended — {ended}"], REFUSED
    decisions = record.get("decisions") or []
    lines = [f"grant: {held.get('slug') or 'every live initiative'} (sha256 {mark_of(held)})",
             CARRY]
    routing = is_routing(record)
    import handoff
    initiative = None if routing else handoff.record_initiative(project_root,
                                                                record.get("state_from"))
    scope_end = handoff.is_scope_end(record)
    for number, decision in enumerate(decisions, 1):
        outside = None if routing else uncovered(held, [slug, initiative], decision)
        if outside is not None:
            lines.append(f"decision {number}: stop: the grant covers {held['slug']}, not "
                         f"{outside}")
            continue
        opened = new_initiative(fields, decision)
        if opened is not None and not routing:
            lines.append(f"decision {number}: stop: /plan-work over {opened}, an initiative with no "
                         f"plan, opens a route, which the person names or a grant holding "
                         f"`routes` answers through a routing record")
            continue
        if scope_end and any(skill_of(door) == "reconcile" for door in
                             ([decision.get("recommended")] if decision.get("recommended") else [])
                             + list(decision.get("others") or []) if isinstance(door, dict)) \
                and reconcile_taken(fields, held, held.get("slug") or slug or initiative):
            lines.append(f"decision {number}: stop: /reconcile was already taken at this "
                         f"initiative's scope's end under this grant")
            continue
        if scope_end and any(skill_of(door) == "plan-work" for door in
                             ([decision.get("recommended")] if decision.get("recommended") else [])
                             + list(decision.get("others") or []) if isinstance(door, dict)) \
                and not close_readiness(project_root, held.get("slug") or slug or initiative)[1]:
            lines.append(f"decision {number}: stop: the closing is not one this grant's close gate "
                         f"accepts as the tree stands")
            continue
        answered = decide_one(number, decision, held, fields, None if routing else
                              held.get("slug") or slug or initiative, routing)
        if scope_end:
            answered = [line.replace(" — precondition unmet — ", " — precondition unmet — at the "
                                     "scope's end, ", 1)
                        if line.strip().startswith(("decided: /reconcile", "decided: /plan-work"))
                        else line for line in answered]
        lines += answered
    if record.get("report"):
        lines.append(f"report: {record['report']}")
    return lines, 0


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
    routing = goal.relative(fields, routing_log(fields)).rstrip("/")
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
        elif (CREDENTIALS.search(name[:-len(base)]) if EXAMPLE_ENV.match(base)
              else CREDENTIALS.search(base) or CREDENTIALS.search(name)):
            found.append(f"refused: {name} names a file that holds credentials")
        elif base == "closure.md" and not held["close"]:
            found.append(f"refused: {name} closes the initiative, and the grant holds no `close` "
                         f"clause")
        elif name == routing and not held.get("routes"):
            found.append(f"refused: {name} is the routing log, and the grant holds no `routes` "
                         f"clause")
    if not found:
        found = [f"checked: the grant holds `commits` for {held.get('slug') or 'every live initiative'}",
                 f"checked: {len(files)} path(s), none outside the project, a standard, "
                 f"CLAUDE.md, a credential, a closure without `close` or the routing log "
                 f"without `routes`"]
    return found, not any(line.startswith("refused:") for line in found)


def close_readiness(project_root: Path, slug: str | None) -> tuple[list[str], bool, str | None]:
    """`close_gate`'s answer read and never acted on — no grant is ended here: the lines, whether
    the closing is accepted, and, where it is refused for the grant's scope rather than the
    initiative's state, why: «A scope's end checks the closing as `bin/grant.py --close` answers it,
    read-only» (SPEC-011 R10)."""
    held, fields, path, ended = standing(project_root)
    slug = slug or held.get("slug")
    if slug is not None and (fields["work_root"] / slug / "closure.md").is_file():
        return [f"refused: {slug} holds a closure.md"], False, None
    if ended:
        return [f"refused: the grant ended — {ended}"], False, f"the grant ended — {ended}"
    if not held["close"]:
        return ["refused: the grant holds no `close` clause"], False, "the grant holds no `close` clause"
    if slug is None:
        return ["refused: the grant names no initiative, so --close takes --slug <slug>"], False, \
            "no initiative named"
    if slug not in covered(fields, held):
        return [f"refused: {slug} is no live initiative the grant covers"], False, \
            f"{slug} is no live initiative the grant covers"
    try:
        found, _ = goal.checks(fields, slug, held["since"], held["version"], [], [])
    except goal.Refused as refusal:
        return [f"refused: the initiative's state could not be read: {refusal}"], False, None
    lines = []
    for name in CLOSED_AFTER:
        ok, out = found.get(name, (False, "no answer"))
        if ok:
            lines.append(f"checked: {name} — {out.splitlines()[0] if out else 'passes'}")
        else:
            lines.append(f"refused: {name}")
            lines += [f"  {line}" for line in out.splitlines()]
    return lines, not any(line.startswith("refused:") for line in lines), None


def close_gate(project_root: Path, slug: str | None) -> tuple[list[str], bool]:
    held, fields, path, ended = standing(project_root)
    if ended:
        end_grant(path, held, "ended", ended)
        return [f"refused: the grant ended — {ended}"], False
    lines, ok, _ = close_readiness(project_root, slug)
    return lines, ok

def newest_record(project_root: Path, skill: str, after: str) -> str:
    """The newest record `handoff.py --render` kept for a skill's report, in the git directory,
    written after the commit named: a run asks over the report of the step it just invoked, never
    over one an earlier stop left."""
    home = Path(goal.command(["git", "-C", str(project_root), "rev-parse", "--show-toplevel"])[1])
    code, out = goal.command(["git", "-C", str(home), "show", "-s", "--format=%ct", after])
    if code != 0 or not out.strip().isdigit():
        raise goal.Refused(f"--after names no commit: {out.strip()}")
    base = goal.armed_path(home).parent / "handoff"
    found = sorted(path for path in base.glob(f"*-{skill}.json")
                   if path.stat().st_mtime > int(out.strip())) if base.is_dir() else []
    if not found:
        raise goal.Refused(f"no record of a {skill} report was kept under {base} after {after}")
    return str(found[-1])


CHECKS_FILE = "grant-checks.jsonl"
GATE_VARIABLE = "SIEGARD_GRANT_STOP"
GATE_MEASURE, GATE_ENFORCE = "measure", "enforce"
GRANT_HEAD = re.compile(r"^grant: .*\(sha256 ([0-9a-f]{16})\)\s*$")
ANSWER = re.compile(r"^decision (\d+): (take|judge): (.+)$")
JUDGED_DOOR = re.compile(r"^door (\S+): (\S+)")
DECIDED = re.compile(r"^decided: .+$")


def obligations_from(text: str) -> list[dict]:
    """What a grant's answer binds a session to, read from the lines `handoff.py --render` or
    `grant.py --decide` printed: one obligation per `take:` or `judge:` decision, each with the
    grant's mark. A `stop:` or `note:` line binds nothing."""
    lines = [line.strip() for line in text.splitlines()]
    mark, found = None, []
    for at, line in enumerate(lines):
        head = GRANT_HEAD.match(line)
        if head:
            mark = head.group(1)
            continue
        answer = ANSWER.match(line)
        if not answer:
            continue
        number, kind, rest = int(answer.group(1)), answer.group(2), answer.group(3)
        if kind == "take":
            entry = rest.split()[-1].lstrip("/")
            decided = next((x for x in lines[at + 1:at + 2] if DECIDED.match(x)), None)
            found.append({"decision": number, "kind": "take", "entry": entry, "line": line,
                          "decided": decided})
        else:
            doors = []
            for following in lines[at + 1:]:
                door = JUDGED_DOOR.match(following)
                if not door:
                    break
                doors.append({"reply_word": door.group(1), "entry": door.group(2)})
            found.append({"decision": number, "kind": "judge", "doors": doors, "line": line})
    for obligation in found:
        obligation["mark"] = mark
    return found


def live_grant(siegard_dir: Path) -> dict | None:
    """The grant armed beside the goal record, under whatever version it was armed: «A change of
    the plugin's version ends no grant» (SPEC-011 R3). None where none is armed. Nothing is
    written: ending a grant is `--decide`'s, at the render."""
    path = siegard_dir / ARMED_FILE
    return read_grant(path) if path.is_file() else None


def gate_mode(environment: dict) -> str:
    """The mode a grant's stop is answered under: `measure` where `SIEGARD_GRANT_STOP` says so,
    `enforce` for every other value and for none."""
    return GATE_MEASURE if (environment.get(GATE_VARIABLE) or "").strip().lower() == GATE_MEASURE \
        else GATE_ENFORCE


def gate_log(siegard_dir: Path, session: str, event: str, mode: str, **more) -> None:
    """One line of `grant-checks.jsonl`: «Each recording, carrying out, block and release is one
    line of `grant-checks.jsonl` beside the grant, carrying the `mode` it was answered under.»
    (SPEC-011 R12)"""
    entry = {"at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
             "session_id": session, "event": event, "mode": mode, **more}
    with (siegard_dir / CHECKS_FILE).open("a", encoding="utf-8") as log:
        log.write(json.dumps(entry) + "\n")


def answered_by(command: str) -> bool:
    """Whether a shell command is one that prints a grant's answer."""
    return ("handoff.py" in command and "--render" in command) or \
        ("grant.py" in command and "--decide" in command)


def after_tool(siegard_dir: Path, session: str, tool: str, given: dict, output: str,
               mode: str = GATE_ENFORCE) -> None:
    """What one tool call does to the session's obligations under a live grant: a command that
    printed a grant's answer replaces them with what it printed; a `Skill` invocation of a door a
    `take:` named, or an `Agent` spawn of the door decider over a `judge:`, carries that
    obligation out. The obligations live in the session's turn record."""
    state = turn.read(siegard_dir, session)
    if tool == "Bash" and answered_by(str(given.get("command") or "")):
        state["obligations"], state["blocked"] = obligations_from(output), []
        turn.write(siegard_dir, state)
        if state["obligations"]:
            gate_log(siegard_dir, session, "recorded", mode,
                     lines=[o["line"] for o in state["obligations"]])
        return
    if tool == "Skill":
        name = turn.skill_of(given)
        done = [o for o in state["obligations"] if o["kind"] == "take" and o["entry"] == name]
    elif tool in ("Agent", "Task"):
        named = str(given.get("subagent_type") or "")
        done = [o for o in state["obligations"] if o["kind"] == "judge"
                and named.split(":")[-1] == "door-decider"]
    else:
        return
    if done:
        state["obligations"] = [o for o in state["obligations"] if o not in done]
        turn.write(siegard_dir, state)
        gate_log(siegard_dir, session, "fulfilled", mode, lines=[o["line"] for o in done])


def obligation_reason(obligation: dict) -> str:
    if obligation["kind"] == "take":
        return (f"`{obligation['line']}` — invoke `/siegard:{obligation['entry']}` as the "
                f"handoff's line ready to paste names it, and write the line the render printed "
                f"under it, `{obligation.get('decided') or 'decided: …'}`, in the run's "
                f"orchestration log.")
    doors = ", ".join(f"{d['reply_word']} ({d['entry']})" for d in obligation["doors"]) \
        or "the doors it printed"
    return (f"`{obligation['line']}` — spawn `siegard:door-decider` over {doors}, handing it what "
            f"`/deliver-scope`'s doors reference names and nothing else; take the door it "
            f"returns, its `decided:` line ending `(grant sha256 {obligation.get('mark')})`; a "
            f"`reserved` or `none` return is the stop it was.")


def stop_answer(siegard_dir: Path, session: str, environment: dict) -> dict | None:
    """What a session's stop is answered with under a live grant: blocked once where the grant
    answered this session's stop and the answer was not carried out, the next stop allowed
    whatever it holds; under `measure` the line is logged and the stop allowed. The turn record
    is left for the `Stop` hook, which clears it once the stop is allowed."""
    mode = gate_mode(environment)
    state = turn.read(siegard_dir, session)
    if not state["obligations"]:
        return None
    key, lines = "obligation", [o["line"] for o in state["obligations"]]
    reason = ("The grant armed in this project answered this session's stop, and its answer "
              "was not carried out:\n" + "\n".join(f"- {obligation_reason(o)}"
                                                    for o in state["obligations"]))
    if key in state["blocked"]:
        gate_log(siegard_dir, session, "released", mode, kind=key, lines=lines)
        return None
    if mode == GATE_MEASURE:
        gate_log(siegard_dir, session, "measured", mode, kind=key, lines=lines)
        return None
    state["blocked"].append(key)
    turn.write(siegard_dir, state)
    gate_log(siegard_dir, session, "blocked", mode, kind=key, lines=lines)
    return {"decision": "block",
            "reason": reason + "\nThe next stop of this session is allowed whatever it holds."}


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
            routes = "--routes" in args
            for word in ("--commits", "--close", "--routes"):
                if word in args:
                    args.remove(word)
            if args or source is None:
                raise goal.Refused("--arm takes <project-root> --words-file <file|-> and the "
                                   "clauses, and --slug <slug> to name one initiative; nothing else")
            doors = None if doors_text is None else (
                [] if doors_text == "none" else [door for door in doors_text.split(",") if door])
            if budget_text is not None and not budget_text.isdigit():
                raise goal.Refused("--budget is a whole number")
            lines, record = arm(project_root, slug, target, doors, int(budget_text or 0),
                                commits, close, words_from(source), routes)
            print("\n".join(lines))
            return 0 if record else REFUSED
        if flag in ("--disarm", "--read", "--close", "--decide", "--commit"):
            if not args:
                raise goal.Refused(f"{flag} takes the project root first")
            project_root = Path(args.pop(0)).resolve()
            if flag == "--disarm":
                try:
                    held, _, path, _ = standing(project_root)
                except goal.Refused:
                    print("no grant is armed in this project")
                    return 0
                end_grant(path, held, "disarmed", "the person disarmed it")
                print(f"disarmed: {held.get('slug') or 'every live initiative'}, armed at {held['armed_at']}")
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
                slug = take(args, "--slug")
                if args:
                    raise goal.Refused("--close takes <project-root> and --slug <slug>")
                lines, ok = close_gate(project_root, slug)
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
            latest = take(args, "--latest")
            after = take(args, "--after")
            slug = take(args, "--slug")
            if (source is None) == (latest is None) or args or (latest is None) != (after is None):
                raise goal.Refused("--decide takes <project-root> and --record <file>, or "
                                   "--latest <skill> with --after <commit>, and --slug <slug>")
            if latest is not None:
                source = newest_record(project_root, latest, after)
            try:
                record = json.loads(Path(source).read_text(encoding="utf-8"))
            except (OSError, ValueError) as broken:
                raise goal.Refused(f"{source} is no handoff record: {broken}")
            lines, code = decide(project_root, record, slug)
            print("\n".join(lines))
            return code
    except goal.Refused as refusal:
        print(f"cannot run: {refusal}", file=sys.stderr)
        return CANNOT_RUN
    print(f"cannot run: {flag} is no flag of this script; --help prints them", file=sys.stderr)
    return CANNOT_RUN


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
