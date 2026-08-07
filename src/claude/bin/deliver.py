#!/usr/bin/env python3
"""Derive the delivery graph from the markdown delivery nodes, and refuse what breaks it.

The path is the identity. `implementation/<epic>/<slug>.md` and `proof/<epic>/<slug>.md` sit at
the path of the task they answer — `task/<epic>/<slug>` — and `review/<slug>.md` names one
review. No node carries an id, a type or a task field, so none of the three can disagree with
where the file sits, and the task a record answers is not something anybody types.

**The schema decides one file; this script decides what needs two — and what needs the plan.**
Per-node validation is `schemas/delivery-node.json` applied as written, plus the contradictions
one file can hold: a finding attributed to a pass that did not run, a `cause` on a pass that is
not the failures pass or missing from one that is, and a coverage or run reference that
disagrees with whether its pass ran. On top of that run the checks no per-file schema can
express: the task exists, a proof sits beside an implementation, every criterion of the task is
answered exactly once and nothing else is, every base node the task binds is answered, the
plan pin matches the plan as it stands, a task the plan leaves unresolved has no record at all,
and no task is delivered before the tasks it declares it builds on. `run/` under the delivery
root holds what the commands printed: kept for a review to point at, never validated as a node.

**The plan is read through plan.py's own pipeline, never through its plan.json** — an index this
script did not just derive could be stale, and a delivery validated against a stale index reports
a soundness nobody has. A plan that does not hold together is a refusal to run: fix it with
plan.py first. The pin each record carries is the SHA-256 of its own task's file, so
`sha256sum <work-root>/task/<epic>/<slug>.md` computes the same value by hand — a record answers
one task, and that is what it is held to.

**There is no status here.** What is delivered is what has a record, and the record's presence
in git is the whole of that state — this script stores nothing about progress and no node
carries a field for it. `--outstanding` answers the question a status field would have answered,
from the tasks that have no record and the dependencies they declare, so the answer is derived
from the files every time and can never be stale or wrong.

**A project's own standard is the project's, and it is read from inside the delivery root.** Where
a review answers for the standard pass, it points at a copy of the registry under `standards/` and
pins its text — kept the way `run/` is kept, because a record that pointed at a file no root holds
could not be checked once the project's copy moved on. So no invocation of this script needs an
extra argument to validate a review: the correct command line stays a function of the roots and
never of what a node happens to say. `--standard <file>` validates a registry on its own, which is
what a consumer runs before any review reads it.

**delivery.json is derived, never edited.** It is refused entirely while the delivery has
problems: an index over a broken delivery reports a shape nobody decided. `--check` compares and
never repairs. This script answers pointed questions itself (`--outstanding`) and never reads
delivery.json to do it: both the index and the report derive from the nodes by the same
pipeline, so neither can disagree with the other, and neither can be stale. Nothing a standard
decides reaches the index, so the derivation stays a function of the delivery root alone.

Declared dependencies: PyYAML, jsonschema.

Usage:  deliver.py <delivery-root> <work-root> [<knowledge-root>]
                                                        validate everything, then write
                                                        delivery.json
        deliver.py --check <delivery-root> <work-root> [<knowledge-root>]
                                                        validate and compare; write nothing
        deliver.py --outstanding <delivery-root> <work-root> [<knowledge-root>]
                                                        validate, then print every task with no
                                                        record and what it waits on; write
                                                        nothing
        deliver.py --node <file> <delivery-root> <work-root> [<knowledge-root>]
                                                        validate one file (cross-node checks,
                                                        plan checks and standard checks do not
                                                        run)
        deliver.py --standard <file> [--against DIR]    validate one project standard on its own;
                                                        stands alone, needs no root. With a tree
                                                        named, also say whether it holds what the
                                                        registry presupposes — exit 1 while any
                                                        of it is absent
        The knowledge root is required while the plan is live, and ignored once closure.md
        marks it closed — the same rule plan.py applies, because the plan is read through it.
Exit:   0 sound (and, with --check, current)
        1 problems, or --check and delivery.json is stale
        2 cannot run (including a plan that does not hold together)
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

CANNOT_RUN = 2

try:
    import yaml
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover - exercised by the environment, not the suite
    print("cannot run: PyYAML and jsonschema are required (pip install pyyaml jsonschema)",
          file=sys.stderr)
    raise SystemExit(CANNOT_RUN)

import plan

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
DELIVERY_CONTRACT = PLUGIN_ROOT / "schemas" / "delivery-node.json"
DELIVERY_GRAPH_CONTRACT = PLUGIN_ROOT / "schemas" / "delivery.json"
STANDARD_CONTRACT = PLUGIN_ROOT / "schemas" / "standard.json"
DELIVERY_FILE = "delivery.json"
RUN_DIR = "run"
STANDARDS_DIR = "standards"

KINDS = ("implementation", "proof", "review")
PAIRED = ("implementation", "proof")
HEADINGS = ["## What it is", "## Notes"]

SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
FENCE = re.compile(r"^---\n(.*?)\n---\n?", re.S)


def id_of(relative: Path) -> str | None:
    """The identifier this path computes to, or None where it computes to nothing."""
    if relative.suffix != ".md":
        return None
    parts = relative.with_suffix("").parts
    if len(parts) == 3 and parts[0] in PAIRED:
        pass
    elif len(parts) == 2 and parts[0] == "review":
        pass
    else:
        return None
    if not all(SLUG.match(p) for p in parts[1:]):
        return None
    return "/".join(parts)


def task_of(nid: str) -> str | None:
    """The task a paired record answers, read from its path — never from a field."""
    parts = nid.split("/")
    return f"task/{parts[1]}/{parts[2]}" if parts[0] in PAIRED else None


def contract() -> tuple[Draft202012Validator, dict[str, set[str]]]:
    """The delivery-node validator, and the per-kind field table read out of the contract rather
    than restated here."""
    if not DELIVERY_CONTRACT.is_file():
        raise FileNotFoundError(
            f"{DELIVERY_CONTRACT} is missing; nothing can be validated without it")
    schema = json.loads(DELIVERY_CONTRACT.read_text(encoding="utf-8"))
    allowed: dict[str, set[str]] = {}
    for branch in schema.get("allOf", []):
        kind = branch["if"]["properties"]["kind"]["const"]
        allowed[kind] = set(branch["then"]["propertyNames"]["enum"])
    return Draft202012Validator(schema), allowed


def pass_names() -> list[str]:
    """The passes a review answers for, read out of the contract rather than restated here."""
    schema = json.loads(DELIVERY_CONTRACT.read_text(encoding="utf-8"))
    return list(schema["$defs"]["passName"]["enum"])


def listed(front: dict, field: str) -> list:
    """A list field read defensively: anything but a list reads as empty, because the schema
    already reported the shape and iterating a string would report its characters."""
    value = front.get(field)
    return value if isinstance(value, list) else []


def texts(entries: list, field: str) -> list[str]:
    """The string values one field carries across a list of mappings, read defensively."""
    return [e[field] for e in entries
            if isinstance(e, dict) and isinstance(e.get(field), str)]


def ran_passes(front: dict, names: list[str]) -> set[str]:
    """The passes a review recorded as having run: an entry naming no missing input."""
    return {e["pass"] for e in listed(front, "passes")
            if isinstance(e, dict) and e.get("pass") in names and "missing" not in e}


def review_problems(front: dict, names: list[str]) -> list[str]:
    """One review against itself: the passes are total, and every field that depends on a pass
    having run agrees with whether it ran. A review reported as clean over a pass that never ran
    is the failure these checks refuse."""
    problems: list[str] = []
    entries = [e for e in listed(front, "passes") if isinstance(e, dict)]
    declared = [e["pass"] for e in entries if isinstance(e.get("pass"), str)]
    for name in names:
        if declared.count(name) == 0:
            problems.append(f"passes names no entry for `{name}`; every pass is answered for, "
                            f"and one that did not run says which input was missing")
        elif declared.count(name) > 1:
            problems.append(f"passes names `{name}` {declared.count(name)} times; "
                            f"a review records one answer per pass")

    ran = ran_passes(front, names)
    reviewed = [p for p in listed(front, "reviewed") if isinstance(p, str)]
    for index, finding in enumerate(listed(front, "findings")):
        if not isinstance(finding, dict) or not isinstance(finding.get("pass"), str):
            continue  # the schema already reported the shape
        name = finding["pass"]
        if name in names and name not in ran:
            problems.append(f"findings[{index}] is attributed to `{name}`, which did not run; "
                            f"a pass that did not run found nothing")
        # A pass that scans the file set is held to it. The failures pass is not: its subject is a
        # captured run, and a change breaks tests it never touched.
        if (name != "failures" and isinstance(finding.get("file"), str)
                and finding["file"] not in reviewed):
            problems.append(f"findings[{index}] is in {finding['file']}, which `reviewed` does "
                            f"not list; a finding outside the file set is a finding over "
                            f"something nobody said was under review")
        # Each of these fields belongs to exactly one pass, and both halves are held: a pass that
        # states nothing where its own field is required, and a pass that states another's.
        for field, owner, absent, foreign in (
                ("cause", "failures",
                 "a failure with no cause named is a failure nobody read",
                 "cause explains why a captured run failed and nothing else"),
                ("cites", "standard",
                 "a finding citing no rule is taste with a location attached",
                 "only a rule of the project's standard is cited, and only that pass reads one")):
            if name == owner and field not in finding:
                problems.append(f"findings[{index}] belongs to the {owner} pass and states no "
                                f"`{field}`; {absent}")
            if name != owner and field in finding:
                problems.append(f"findings[{index}] states `{field}` outside the {owner} pass; "
                                f"{foreign}")

    for field, name, want in (("coverage", "coverage", "the criteria it paired with tests"),
                              ("run", "failures", "the captured run it read"),
                              ("failures_counted", "failures",
                               "how many failures the run reported"),
                              ("standard", "standard",
                               "the standard it read and the rules that were in scope")):
        if field in front and name not in ran:
            problems.append(f"`{field}` is present and the {name} pass did not run; "
                            f"a pass that did not run holds {want} over nothing")
        if field not in front and name in ran:
            problems.append(f"the {name} pass ran and `{field}` is absent; a pass that ran "
                            f"records {want}")

    if "coverage" in ran and not listed(front, "tasks"):
        problems.append("the coverage pass ran and this review names no task; the criteria it "
                        "pairs tests with are the tasks', and without them it would be pairing "
                        "tests with criteria nobody wrote")

    counted = front.get("failures_counted")
    if isinstance(counted, int) and not isinstance(counted, bool):
        recorded = sum(1 for f in listed(front, "findings")
                       if isinstance(f, dict) and f.get("pass") == "failures")
        if counted != recorded:
            problems.append(f"failures_counted is {counted} and the failures pass recorded "
                            f"{recorded} finding(s); the two disagreeing is how a failure goes "
                            f"unexamined while the record still looks complete — read the run "
                            f"again and find out which is wrong, never lower the count or drop "
                            f"a finding to make the two agree")
    return problems


def standard_contract() -> Draft202012Validator:
    """The validator for a project's own standard. The registry is the project's artifact, so this
    framework holds it to a contract and authors none of its content."""
    if not STANDARD_CONTRACT.is_file():
        raise FileNotFoundError(
            f"{STANDARD_CONTRACT} is missing; a standard cannot be validated without it")
    return Draft202012Validator(json.loads(STANDARD_CONTRACT.read_text(encoding="utf-8")))


def load_standard(path: Path, validator) -> tuple[dict | None, list[str]]:
    """One standard, read and held to its contract. Returns nothing usable while it has problems:
    a review is never checked against a registry that does not hold together."""
    if not path.is_file():
        return None, [f"{path} does not exist"]
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as broken:
        return None, [f"{path} cannot be read: {broken}"]
    if not isinstance(data, dict):
        return None, [f"{path} is a {type(data).__name__}, not a mapping"]

    problems = []
    for error in sorted(validator.iter_errors(data), key=str):
        where = ".".join(str(part) for part in error.absolute_path) or "the standard"
        problems.append(f"{where}: {error.message}")
    ids = [r["id"] for r in listed(data, "rules")
           if isinstance(r, dict) and isinstance(r.get("id"), str)]
    for value in sorted({i for i in ids if ids.count(i) > 1}):
        problems.append(f"declares `{value}` {ids.count(value)} times; two rules under one id "
                        f"cannot be told apart by the finding that cites it")
    for rule in listed(data, "rules"):
        if isinstance(rule, dict) and rule.get("decided_by") == "reading" and "tool" in rule:
            problems.append(f"{rule.get('id')} is decided by reading and names the tool "
                            f"`{rule['tool']}`; a rule is one or the other, and a rule a tool "
                            f"decides is not a review's to read")
    for field in ("presupposes", "dependencies"):
        for index, entry in enumerate(listed(data, field)):
            if not isinstance(entry, dict):
                continue
            for cited in listed(entry, "rules"):
                if isinstance(cited, str) and cited not in ids:
                    problems.append(f"{field}[{index}] names {cited}, which this registry does "
                                    f"not declare; naming a rule is how an entry says what it "
                                    f"costs, and one citing nothing that resolves is a cost "
                                    f"nobody can weigh")
    problems += command_problems(data) + package_problems(data)
    return (None if problems else data), problems


def command_problems(data: dict) -> list[str]:
    """One registry's commands, against itself and against the rules that expect them. The join is
    the step name: a rule says a tool decides it, a command says how that tool is run, and
    `bin/run.py` records the outcome under the same name. A registry that declares no command at
    all is held to none of this — it behaves the way every registry did before the field, with
    nothing running on its own and a review saying which rules went unanswered."""
    problems: list[str] = []
    entries = [c for c in listed(data, "commands") if isinstance(c, dict)]
    if not entries:
        return problems

    names = [c["step"] for c in entries if isinstance(c.get("step"), str)]
    for value in sorted({n for n in names if names.count(n) > 1}):
        problems.append(f"declares the step `{value}` {names.count(value)} times; a run records "
                        f"one outcome per step, and two commands under one name cannot both be it")

    for role in ("install", "suite"):
        carrying = [c["step"] for c in entries if c.get("role") == role
                    and isinstance(c.get("step"), str)]
        if len(carrying) > 1:
            problems.append(f"{', '.join(sorted(carrying))} all carry the role `{role}`; a "
                            f"delivery runs one of them at a named moment, and which one is not "
                            f"something a caller may pick")

    declared = set(names)
    for rule in listed(data, "rules"):
        if not isinstance(rule, dict) or not isinstance(rule.get("tool"), str):
            continue
        if rule["tool"] not in declared:
            problems.append(f"{rule.get('id')} says the step `{rule['tool']}` decides it, and this "
                            f"registry declares no such command; a rule declared mechanical with "
                            f"nothing named to decide it is a rule nobody applies, which is worse "
                            f"than one nobody wrote")

    return problems


def package_problems(data: dict) -> list[str]:
    """One registry's authorized packages, against themselves. Checked whether or not the registry
    declares a command, because the list is an allowlist first and an install second: a name
    written twice is a record that resolves against one of two entries with no way to say which."""
    packages = [d["package"] for d in listed(data, "dependencies")
                if isinstance(d, dict) and isinstance(d.get("package"), str)]
    return [f"authorizes `{value}` {packages.count(value)} times; a record naming it resolves "
            f"against one entry, and two cannot both be the reason it was admitted"
            for value in sorted({p for p in packages if packages.count(p) > 1})]


def pin_of(path: Path) -> str:
    """The pin of a file's bytes, computable by hand as `sha256sum <path>`."""
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def reaches(scope, path: str) -> bool:
    """Whether one scope of a standard rule reaches one path. The scope is stated in parts rather
    than as a glob pattern deliberately: one tool's single star crosses a separator and another's
    double star means exactly one directory, and that difference would decide whether a finding is
    refused."""
    if not isinstance(scope, dict):
        return False
    under, suffix = scope.get("under"), scope.get("suffix")
    if not isinstance(under, str) or not isinstance(suffix, str):
        return False
    prefix = f"{under.rstrip('/')}/"
    if not path.startswith(prefix) or not path.endswith(suffix):
        return False
    return bool(scope.get("nested")) or "/" not in path[len(prefix):]


def in_scope(rule: dict, paths: list[str]) -> bool:
    return any(reaches(scope, path)
               for scope in listed(rule, "applies_to") for path in paths)


def standard_of(nid: str, front: dict, root: Path,
                validator) -> tuple[dict | None, str | None, list[str]]:
    """The standard a record read, loaded from the copy this root holds and held to its pin. The
    copy is why a citation can be resolved at all: the project's registry lives in the project's
    tree and moves on, and a record pointing outside every root could not be checked afterwards."""
    declared = front.get("standard")
    if not isinstance(declared, dict) or not isinstance(declared.get("at"), str):
        return None, None, []  # the schema already reported the shape

    at = declared["at"]
    path = root / at
    data, found = load_standard(path, validator)
    problems = [f"{nid}: {at}: {p}" for p in found]
    if data is None:
        return None, at, problems

    if declared.get("pin") != pin_of(path):
        problems.append(f"{nid}: the standard's pin is not the text at {at} ({pin_of(path)}); the "
                        f"copy this record points at is not the one it was written against")
    return data, at, problems


def rules_of(data: dict) -> dict[str, dict]:
    return {r["id"]: r for r in listed(data, "rules")
            if isinstance(r, dict) and isinstance(r.get("id"), str)}


def record_run_problems(nid: str, front: dict, root: Path) -> list[str]:
    """One record that wrote something, against the run it points at. A record and its run are one
    act: the run is what the delivery saw before it wrote, so a record over a run that did not pass
    claims what the run denied. It is the exact mirror of `run_problems`, which refuses a review's
    run that passed — there, a green run is a diagnosis nobody should have asked for; here, a red
    one is a delivery that should not exist. The failure is not erased by either: the run that
    failed keeps its directory, and `bin/run.py` refuses to let any later run take its name."""
    where = front.get("run")
    if not isinstance(where, str):
        return []
    record = root / where / "run.json"
    if not record.is_file():
        return [f"{nid}: run names {where}, which holds no run.json; the runner writes one for "
                f"every run, so a directory without it is not a run this framework captured"]
    try:
        captured = json.loads(record.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as broken:
        return [f"{nid}: {where}/run.json cannot be read: {broken}"]
    if not isinstance(captured, dict):
        return [f"{nid}: {where}/run.json is not a mapping"]
    if captured.get("outcome") != "passed":
        failed = captured.get("failed_step")
        return [f"{nid}: {where} ended `{captured.get('outcome')}` at the step `{failed}`, and "
                f"this record was written anyway; what a record says was delivered is what the "
                f"run it points at showed, and this one showed the opposite — fix what failed and "
                f"run again under a name of its own, or leave the record unwritten"]
    return []


def record_standard_problems(nid: str, front: dict, root: Path, validator,
                             tfront: dict) -> list[str]:
    """Every rule a record that wrote something says it departed from — an implementation or a
    proof alike — resolved against the standard it pins, plus every package it says it installed
    and whether the run its kind owes was captured at all. Unlike a review's citation a departure
    may name a rule a tool decides: a record obeys the whole standard, and departing from a rule
    the compiler owns is a real departure that the run will show. The validator holds the citation
    and says nothing about whether departing was right, which is a reader's to judge."""
    data, at, problems = standard_of(nid, front, root, validator)
    if data is None:
        return problems
    rules = rules_of(data)
    problems += installed_problems(nid, front, data, at)
    problems += owed_run_problems(nid, front, data, at, root, tfront)

    for index, entry in enumerate(listed(front, "divergences")):
        if not isinstance(entry, dict) or not isinstance(entry.get("cites"), str):
            continue  # reported by the shape checks, or a departure from something else
        cited, where = entry["cites"], entry.get("file")
        rule = rules.get(cited)
        if rule is None:
            problems.append(f"{nid}: divergences[{index}] cites {cited}, which {at} does not "
                            f"declare")
        elif isinstance(where, str) and not in_scope(rule, [where]):
            problems.append(f"{nid}: divergences[{index}] cites {cited} against {where}, which "
                            f"that rule's scope does not reach")
    return problems


def installed_problems(nid: str, front: dict, data: dict, at: str) -> list[str]:
    """Every package a record says it installed, against the list its standard authorizes. The
    list is where a human's approval of a package lives — the only place it survives the session it
    was given in — so a delivery that could install past it would make the approval decorative.
    The check is over names and never over a manifest: reading one would be reading a stack this
    framework ships no knowledge of."""
    authorized = {d["package"] for d in listed(data, "dependencies")
                  if isinstance(d, dict) and isinstance(d.get("package"), str)}
    return [f"{nid}: installed names {package}, which {at} does not authorize; a package this "
            f"registry has not admitted is one nobody approved, and the approval that admits it is "
            f"the registry gaining an entry — not an answer given while it was being installed"
            for package in listed(front, "installed")
            if isinstance(package, str) and package not in authorized]


def steps_that_passed(root: Path, where: str) -> set[str] | None:
    """The steps one captured run recorded as passed, or `None` where the run cannot be read at
    all. The `None` matters: `record_run_problems` already refuses a record whose run holds no
    run.json or will not parse, and a second refusal here would name one missing file twice."""
    try:
        captured = json.loads((root / where / "run.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(captured, dict):
        return None
    return {step["name"] for step in listed(captured, "steps")
            if isinstance(step, dict) and isinstance(step.get("name"), str)
            and step.get("outcome") == "passed"}


def substrate_only(front: dict, tfront: dict, data: dict) -> bool:
    """Whether this record delivered the substrate and nothing any rule can reach.

    Two conditions, and neither alone is enough. The task declares `produces` — the same field,
    read the same way, that exempts it from the substrate check at the plan gate and at the situate
    step: the task building the artifacts every rule needs is the one task their absence cannot
    stop, and with no exemption nothing could ever build them. And nothing this record wrote sits in
    the scope of any rule the registry declares, which is what makes the other steps vacuous rather
    than merely inconvenient — a step decides a rule over a file, and there is no such file yet.

    The second condition is what keeps the first from being a licence. A task may declare `produces`
    and also write source, and source is not exempt from the steps that decide the rules reaching
    it. For a genuine substrate the condition holds by construction: `presupposes` exists for the
    artifacts no rule can ask for, a scope names a directory and an ending, and a path at the root
    of the tree has no separator to match one. So this refuses nothing anybody meant to write."""
    if not listed(tfront, "produces"):
        return False
    written, _ = wrote(front)
    return not any(in_scope(rule, sorted(written))
                   for rule in listed(data, "rules") if isinstance(rule, dict))


def owed_run_problems(nid: str, front: dict, data: dict, at: str, root: Path,
                      tfront: dict) -> list[str]:
    """Whether a record captured the run its kind owes, and whether that run covered it. A registry
    declaring how the project is installed and checked is a registry whose delivery could be run,
    and a delivery that could be run and was not is the state this whole arrangement exists to end:
    source handed over having never been executed, with every rule a tool decides unanswered by
    anything. What each kind owes differs because of when it is written — an implementation is
    written before any test exists, so it owes the checks that do not need one; a proof is written
    after, so it owes them all.

    Presence was never the whole question, and until the coverage below existed it was the whole
    check: a record pointing at a run of one step out of four is the same source nobody executed,
    declared executed, and the docstring above claimed a guarantee the code did not hold.

    One exemption, and it is `substrate_only`'s. It is an implementation's alone: a proof exists
    because tests exist, and a suite held back is the one thing a proof is for."""
    commands = [c for c in listed(data, "commands") if isinstance(c, dict)]
    kind = "proof" if "tests" in front else "implementation"
    owed = commands if kind == "proof" else [c for c in commands if c.get("role") != "suite"]
    if kind == "implementation" and substrate_only(front, tfront, data):
        owed = [c for c in owed if c.get("role") == "install"]
    if not owed:
        return []

    named = ", ".join(str(c.get("step")) for c in owed)
    where = front.get("run")
    if not isinstance(where, str):
        return [f"{nid}: {at} declares the step(s) {named} and this record captured no run; a "
                f"delivery whose project could be installed and checked and was not is source "
                f"nobody executed, which is exactly what a record pointing at a green run says "
                f"did not happen"]

    passed = steps_that_passed(root, where)
    if passed is None:
        return []  # record_run_problems names the run that cannot be read
    missing = [str(c.get("step")) for c in owed if c.get("step") not in passed]
    if not missing:
        return []

    covered = f"passed only {', '.join(sorted(passed))}" if passed else "passed no step of it"
    said = (f"{nid}: {at} declares the step(s) {named} and {where} {covered}; nothing decided the "
            f"rules {', '.join(missing)} own. A delivery that ran a fraction of the checks its own "
            f"registry declares is the same source nobody executed — run them and point at that "
            f"run")
    if listed(tfront, "produces"):
        said += (f". This task declares `produces` and would owe the install alone, but it wrote a "
                 f"file a rule of {at} reaches: what builds the substrate is exempt, and the "
                 f"source written beside it is not")
    return [said]


def review_standard_problems(nid: str, front: dict, root: Path, validator) -> list[str]:
    """Every citation a review makes, resolved against the standard it pins. A review may only cite
    a rule the standard leaves to a reading — judging one a tool decides exactly would re-decide it
    in a model at worse recall, and would make the tool's own findings look like opinions. Which
    rules were in scope is not read from the record: it is a function of the copy and `reviewed`,
    and both sit in this root."""
    data, at, problems = standard_of(nid, front, root, validator)
    if data is None:
        return problems
    rules = rules_of(data)

    for index, finding in enumerate(listed(front, "findings")):
        if not isinstance(finding, dict) or finding.get("pass") != "standard":
            continue
        cited, where = finding.get("cites"), finding.get("file")
        if not isinstance(cited, str):
            continue  # the schema already reported it
        rule = rules.get(cited)
        if rule is None:
            problems.append(f"{nid}: findings[{index}] cites {cited}, which {at} does not declare")
        elif rule.get("decided_by") != "reading":
            problems.append(f"{nid}: findings[{index}] cites {cited}, which {at} says a tool "
                            f"decides; a rule a linter or a compiler decides exactly runs as a "
                            f"step of the project's own suite, and what it finds arrives through "
                            f"the failures pass instead")
        elif isinstance(where, str) and not in_scope(rule, [where]):
            problems.append(f"{nid}: findings[{index}] cites {cited} against {where}, which that "
                            f"rule's scope does not reach")
    return problems


def wrote(front: dict) -> tuple[set[str], str]:
    """Every path one record says it wrote, and the field that said so. An implementation writes
    `files` and a proof writes `tests`; no record carries both, so one expression serves either and
    a departure is checked against the same rule whichever wrote it."""
    files = {f["path"] for f in listed(front, "files")
             if isinstance(f, dict) and isinstance(f.get("path"), str)}
    tests = {t["file"] for t in listed(front, "tests")
             if isinstance(t, dict) and isinstance(t.get("file"), str)}
    return (files | tests), ("files" if "files" in front else "tests")


def divergence_problems(front: dict) -> list[str]:
    """One record's disclosed departures, against itself. A departure names exactly one thing it
    departed from, and where a standard's rule is what it names, it says which file — so the
    citation can be checked against the scope the rule declares and a reader can open the place.
    Whether the departure was justified is nobody's here to decide."""
    problems: list[str] = []
    written, field = wrote(front)
    for index, entry in enumerate(listed(front, "divergences")):
        if not isinstance(entry, dict):
            continue  # the schema already reported the shape
        names_from, cites, where = "from" in entry, "cites" in entry, entry.get("file")
        if names_from and cites:
            problems.append(f"divergences[{index}] names both `from` and `cites`; one departure "
                            f"departs from one thing, and a rule of the standard is cited rather "
                            f"than described")
        elif not names_from and not cites:
            problems.append(f"divergences[{index}] names neither `from` nor `cites`; a departure "
                            f"from nothing stated is a departure nobody can pair with anything")
        if cites and not isinstance(where, str):
            problems.append(f"divergences[{index}] cites {entry['cites']} and names no `file`; a "
                            f"citation is checked against the scope its rule declares, and "
                            f"without a path there is nothing to check it against")
        if isinstance(where, str) and not cites:
            problems.append(f"divergences[{index}] names the file {where} and cites no rule; "
                            f"`file` locates a citation, and a departure described in prose is "
                            f"located in that prose")
        if isinstance(where, str) and where not in written:
            problems.append(f"divergences[{index}] names {where}, which `{field}` does not list; a "
                            f"departure sits in a file this record says it wrote")
        if cites and "standard" not in front:
            problems.append(f"divergences[{index}] cites {entry['cites']} and this record names no "
                            f"standard; a citation resolves against the copy the record pins, and "
                            f"without one it names nothing")
    return problems


def node_problems(front, kind: str, validator, allowed, names: list[str]) -> list[str]:
    """Everything wrong with one delivery node on its own: the schema, applied as written, plus
    the contradictions a single file can hold."""
    if not isinstance(front, dict):
        return [f"frontmatter is a {type(front).__name__}, not a mapping"]
    if any(not isinstance(key, str) for key in front):
        return ["frontmatter carries a non-string key"]

    problems: list[str] = []
    data = {**front, "kind": kind}
    for error in validator.iter_errors(data):
        where = ".".join(str(part) for part in error.absolute_path) or "frontmatter"
        problems.append(f"{where}: {error.message}")

    for field, quoted in (("criteria", "criterion"), ("coverage", "criterion"),
                          ("nodes", "node")):
        seen = texts(listed(front, field), quoted)
        for value in sorted({v for v in seen if seen.count(v) > 1}):
            problems.append(f"{field} answers for `{value}` {seen.count(value)} times; "
                            f"a record answers each of them once")

    if kind == "review":
        problems.extend(review_problems(front, names))
    if kind in PAIRED:
        problems.extend(divergence_problems(front))
        if "installed" in front and "standard" not in front:
            problems.append("`installed` names packages and this record names no standard; what "
                            "authorizes a package is a registry's own list, and without one the "
                            "names resolve against nothing")
    return problems


def body_problems(body: str) -> list[str]:
    headings = [line.rstrip() for line in body.splitlines() if line.startswith("## ")]
    if headings != HEADINGS:
        return [f"body headings are {headings if headings else 'absent'}; "
                f"every delivery node carries exactly {HEADINGS}"]
    return []


def references(nid: str, front: dict, kind: str) -> list[tuple[str, str, str]]:
    """Every reference this node declares: (target, edge kind, locator). `implements` and
    `reviews` point at tasks of the plan, `proves` at the implementation this proof sits beside,
    and `encodes` at the base nodes the source now holds a fact of. Read defensively, because
    this also runs over nodes the schema has already reported."""
    refs: list[tuple[str, str, str]] = []
    if kind == "implementation":
        refs.append((task_of(nid), "implements", "the path"))
        for index, entry in enumerate(listed(front, "nodes")):
            if isinstance(entry, dict) and isinstance(entry.get("node"), str) \
                    and entry.get("encoded_at"):
                refs.append((entry["node"], "encodes", f"nodes[{index}]"))
    if kind == "proof":
        refs.append((f"implementation/{nid.split('/', 1)[1]}", "proves", "the path"))
    if kind == "review":
        for index, target in enumerate(listed(front, "tasks")):
            if isinstance(target, str):
                refs.append((target, "reviews", f"tasks[{index}]"))
    return refs


def implementation_problems(nid: str, front: dict, task: dict, work: Path,
                            delivered: set[str]) -> list[str]:
    """One implementation against the task it answers: the plan's own triage decides whether the
    task could be implemented at all, the criteria and the binding are each answered in full,
    the dependencies it declares are delivered first, and the pin matches the plan as it
    stands."""
    problems: list[str] = []
    tfront = task["front"]

    open_entries = listed(tfront, "unresolved")
    if open_entries:
        problems.append(
            f"{nid}: {task_of(nid)} carries {len(open_entries)} unresolved entry(ies), and this "
            f"record delivers it anyway; an unresolved entry is a fact the base does not hold "
            f"that bears on the objective or a criterion, so implementing over it writes an "
            f"invention where nobody will look for a decision — settle it through "
            f"/analyse-domain and re-plan the task")

    stated = [c for c in listed(tfront, "criteria") if isinstance(c, str)]
    answered = texts(listed(front, "criteria"), "criterion")
    for criterion in stated:
        if criterion not in answered:
            problems.append(f"{nid}: the task states the criterion `{criterion}`, and this "
                            f"record answers for no such criterion; a record answering only "
                            f"some of them cannot be read as complete")
    for criterion in answered:
        if criterion not in stated:
            problems.append(f"{nid}: criteria answers for `{criterion}`, which the task does "
                            f"not state; the criterion is quoted as the task states it, or it "
                            f"is a criterion nobody wrote")

    written, _ = wrote(front)
    for path in listed(tfront, "produces"):
        if isinstance(path, str) and path not in written:
            problems.append(f"{nid}: the task says it produces {path}, and `files` does not list "
                            f"it; what a task produces is what its own standard presupposes — the "
                            f"artifact no rule can ask for and every rule needs — so a record "
                            f"claiming the task and not the artifact leaves the next delivery "
                            f"stopped on an absence this one was cut to end")

    bound = sorted(plan.bound_of(tfront))
    accounted = texts(listed(front, "nodes"), "node")
    for node_ref in bound:
        if node_ref not in accounted:
            problems.append(f"{nid}: the task binds {node_ref}, and this record does not say "
                            f"how the source answers to it; a bound node passed over in "
                            f"silence is the base going unanswered in code — answer it in "
                            f"`nodes`, or re-bind the task through /plan-work if it does not "
                            f"govern this work")
    for node_ref in accounted:
        if node_ref not in bound:
            problems.append(f"{nid}: nodes answers for {node_ref}, which the task does not "
                            f"bind; a record reaches exactly what the plan bound, and more is "
                            f"work the plan does not declare")

    for index, target in enumerate(listed(tfront, "depends_on")):
        if isinstance(target, str) and target not in delivered:
            problems.append(f"{nid}: the task declares it builds on {target}, which no "
                            f"implementation record answers; the dependency is what has to be "
                            f"delivered first, and the records are how that is known")

    declared, actual = front.get("task"), task_pin(work, task_of(nid))
    if isinstance(declared, str) and actual is not None and declared != actual:
        problems.append(f"{nid}: task pin {declared} is not {task_of(nid)} as it stands ({actual}); "
                        f"the record answers a task that has since changed. Three ways out, and "
                        f"which one is right turns on what this record describes, not on the pin: "
                        f"deliver it again against the task as it now stands; restate the pin "
                        f"deliberately, where the change left what this record says untouched; or, "
                        f"where the source it describes no longer exists, delete the record, "
                        f"because a record of a delivery nothing holds has no subject, the way a "
                        f"review of a task nothing delivered has none. Only the source settles the "
                        f"third, and no root named here holds it. It is never the way past a pin "
                        f"that merely moved: a record deleted to clear a refusal is a test "
                        f"weakened to clear a suite, performed one root over")
    return problems


def review_plan_problems(nid: str, front: dict, plan_nodes: dict[str, dict],
                         delivered: set[str], names: list[str], root: Path) -> list[str]:
    """One review against the plan and the delivery: the tasks it names are delivered tasks, the
    coverage pass answers for every criterion of them, and the run it read exists."""
    problems: list[str] = []
    tasks = [t for t in listed(front, "tasks") if isinstance(t, str)]

    for index, target in enumerate(tasks):
        if target not in plan_nodes or plan_nodes[target]["kind"] != "task":
            problems.append(f"{nid}: tasks[{index}] names {target}, which the plan does not "
                            f"hold as a task")
        elif target not in delivered:
            problems.append(f"{nid}: tasks[{index}] names {target}, which no implementation "
                            f"record answers; a review of a task nothing delivered has no "
                            f"subject")

    if "coverage" in ran_passes(front, names) and tasks:
        stated = [c for target in tasks if target in plan_nodes
                  for c in listed(plan_nodes[target]["front"], "criteria")
                  if isinstance(c, str)]
        audited = texts(listed(front, "coverage"), "criterion")
        for criterion in stated:
            if criterion not in audited:
                problems.append(f"{nid}: the review names a task stating the criterion "
                                f"`{criterion}`, and coverage answers for no such criterion; "
                                f"an omitted criterion reads as one that passed")
        for criterion in audited:
            if criterion not in stated:
                problems.append(f"{nid}: coverage answers for `{criterion}`, which no task "
                                f"this review names states; the criterion is quoted as the "
                                f"task states it")

    problems.extend(run_problems(nid, front, root))
    return problems


def run_problems(nid: str, front: dict, root: Path) -> list[str]:
    """One review against the run it read. The record says a run failed and says how many failures
    it counted; this opens the run and holds both to it. Without that, every fact a review states
    about a run is the reviewer's own, and a review claiming the failures pass ran and found
    nothing over a run that failed passes every other check — which is exactly the failure the
    count was written to expose."""
    problems: list[str] = []
    where = front.get("run")
    if not isinstance(where, str):
        return problems
    directory = root / where
    if not directory.is_dir():
        return [f"{nid}: run names {where}, which the delivery root does not hold; "
                f"the captured run is the evidence a diagnosis was read from"]

    record = directory / "run.json"
    if not record.is_file():
        return [f"{nid}: {where} holds no run.json; the runner writes one for every run, so a "
                f"directory without it is not a run this framework captured"]
    try:
        captured = json.loads(record.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as broken:
        return [f"{nid}: {where}/run.json cannot be read: {broken}"]
    if not isinstance(captured, dict):
        return [f"{nid}: {where}/run.json is not a mapping"]

    outcome = captured.get("outcome")
    if outcome == "passed":
        problems.append(f"{nid}: {where} passed, and the failures pass reads a run to say why it "
                        f"failed; a run holding no failure is a pass that should not have been "
                        f"asked for, and the entry says so instead")
    counted = front.get("failures_counted")
    if outcome != "passed" and counted == 0:
        problems.append(f"{nid}: {where} ended `{outcome}` and this review counted no failures; a "
                        f"run that did not pass reported something, and a count of none over it "
                        f"is how a failure goes unexamined while the record still looks complete")
    return problems


def cross_problems(nodes: dict[str, dict], plan_nodes: dict[str, dict], work: Path,
                   names: list[str], root: Path,
                   standard: Draft202012Validator | None = None) -> list[str]:
    """The rules that need to see more than one node at once — or the plan, or the copy of a
    standard the delivery root holds."""
    problems: list[str] = []
    delivered = {task_of(nid) for nid, node in nodes.items()
                 if node["kind"] == "implementation"}

    for nid in sorted(nodes):
        node, front = nodes[nid], nodes[nid]["front"]
        task = task_of(nid)
        if task is not None:
            if task not in plan_nodes or plan_nodes[task]["kind"] != "task":
                problems.append(f"{nid}: answers {task}, which the plan does not hold as a "
                                f"task; the path is the identity and this one names nothing")
                continue
            problems.extend(record_standard_problems(
                nid, front, root, standard or standard_contract(),
                plan_nodes[task]["front"]))
            problems.extend(record_run_problems(nid, front, root))
            if node["kind"] == "implementation":
                problems.extend(implementation_problems(nid, front, plan_nodes[task], work,
                                                        delivered))
            else:
                pair = f"implementation/{nid.split('/', 1)[1]}"
                if pair not in nodes:
                    problems.append(f"{nid}: proves a task with no implementation record at "
                                    f"{pair}; what a proof holds up has to exist first")
                else:
                    declared = front.get("implementation")
                    actual = pin_of(root / f"{pair}.md")
                    if isinstance(declared, str) and declared != actual:
                        problems.append(
                            f"{nid}: the implementation pin is not {pair} as it stands ({actual}); "
                            f"the record these tests were written against has been rewritten and "
                            f"the proof has not — write the proof again, or restate the pin "
                            f"deliberately")
        if node["kind"] == "review":
            problems.extend(review_plan_problems(nid, front, plan_nodes, delivered,
                                                 names, root))
            problems.extend(review_standard_problems(nid, front, root,
                                                     standard or standard_contract()))
    return problems


def collect(root: Path, validator, allowed, names: list[str]) -> tuple[dict[str, dict],
                                                                      list[str]]:
    """Every node in the delivery, and everything wrong with the files as files."""
    nodes: dict[str, dict] = {}
    problems: list[str] = []
    for path in sorted(root.rglob("*.md")):
        relative = path.relative_to(root)
        if relative.parts[0] in (RUN_DIR, STANDARDS_DIR):
            continue  # what a run printed, and the standard a review read: material, never a node
        nid = id_of(relative)
        if nid is None:
            problems.append(f"{relative.as_posix()}: not implementation/<epic>/<slug>.md, "
                            f"proof/<epic>/<slug>.md or review/<slug>.md; the path is the "
                            f"identity and this one computes to none. Material a judgment was "
                            f"read from belongs under run/ or standards/, which are never "
                            f"validated as nodes")
            continue
        text = path.read_text(encoding="utf-8")
        match = FENCE.match(text)
        if not match:
            problems.append(f"{nid}: carries no frontmatter fence")
            continue
        try:
            front = yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError as broken:
            problems.append(f"{nid}: frontmatter does not parse: {broken}")
            continue
        kind = relative.parts[0]
        problems += [f"{nid}: {p}"
                     for p in node_problems(front, kind, validator, allowed, names)]
        problems += [f"{nid}: {p}" for p in body_problems(text[match.end():])]
        if isinstance(front, dict):
            nodes[nid] = {"front": front, "kind": kind}
    return nodes, problems


def load_plan(work: Path, knowledge: Path | None) -> tuple[dict[str, dict], list[str]]:
    """The plan, read through plan.py's own pipeline — never through a plan.json that could be
    stale. A closed plan is read the way plan.py reads it: without opening today's base."""
    validator, allowed = plan.contract()
    if (work / plan.CLOSURE_FILE).is_file():
        base_nodes = None
    else:
        base_nodes, base_problems = plan.load_base(knowledge)
        if base_problems:
            return {}, base_problems
    nodes, problems = plan.collect(work, validator, allowed)
    problems += plan.cross_problems(nodes, base_nodes)
    return nodes, sorted(set(problems))


def task_pin(work: Path, tid: str) -> str | None:
    """The pin of one task as it stands: the SHA-256 of its file's text, so
    `sha256sum <work-root>/<tid>.md` computes the same value by hand. None where the file is gone,
    which the plan checks report before this is consulted.

    It pins the task rather than the plan's derived index deliberately. The index carries the
    plan's shape and not each task's criteria, so pinning it left the one thing a record answers
    for uncovered while making every record in the root stale the moment any unrelated task was
    added — and no entry point owns re-pinning records it was forbidden to read."""
    path = work / f"{tid}.md"
    return pin_of(path) if path.is_file() else None


def derive(nodes: dict[str, dict], names: list[str]) -> dict:
    """The delivery graph a sound delivery derives to. Sorted throughout, so identical input is
    byte-identical output."""
    out_nodes, out_edges = [], []
    for nid in sorted(nodes):
        node, front = nodes[nid], nodes[nid]["front"]
        entry = {
            "id": nid,
            "kind": node["kind"],
            "file": f"{nid}.md",
            "title": front.get("title", ""),
            "summary": front.get("summary", ""),
        }
        task = task_of(nid)
        if task is not None:
            entry["task"] = task
        if node["kind"] == "implementation":
            unmet = sorted(e["criterion"] for e in listed(front, "criteria")
                           if isinstance(e, dict) and e.get("met") is False
                           and isinstance(e.get("criterion"), str))
            if unmet:
                entry["unmet"] = unmet
        if node["kind"] == "review":
            ran = sorted(ran_passes(front, names), key=names.index)
            if ran:
                entry["ran"] = ran
            unproven = sorted(e["criterion"] for e in listed(front, "coverage")
                              if isinstance(e, dict) and e.get("state") != "covered"
                              and isinstance(e.get("criterion"), str))
            if unproven:
                entry["unproven"] = unproven
            findings = len(listed(front, "findings"))
            if findings:
                entry["findings"] = findings
        out_nodes.append(entry)
        for target, edge_kind, at in references(nid, front, node["kind"]):
            out_edges.append({"from": nid, "to": target, "kind": edge_kind, "at": at})
    out_edges.sort(key=lambda e: (e["from"], e["kind"], e["at"], e["to"]))
    return {"contract_version": "siegard-delivery/1", "nodes": out_nodes, "edges": out_edges}


def check_single(root: Path, named: str, validator, allowed, names: list[str]) -> int:
    path = Path(named)
    if not path.is_absolute():
        path = (root / named) if (root / named).is_file() else Path.cwd() / named
    try:
        relative = path.resolve().relative_to(root.resolve())
    except ValueError:
        print(f"cannot run: {named} is not under {root}", file=sys.stderr)
        return CANNOT_RUN
    if relative.parts[0] in (RUN_DIR, STANDARDS_DIR):
        held = ("what the commands printed" if relative.parts[0] == RUN_DIR
                else "the standard a review read")
        print(f"{relative.as_posix()}: sits under {relative.parts[0]}/, which holds {held} "
              f"and is never validated as a node")
        return 0
    nid = id_of(relative)
    if nid is None:
        print(f"{relative.as_posix()}: the path computes to no identifier")
        return 1
    if not path.is_file():
        print(f"cannot run: {path} does not exist", file=sys.stderr)
        return CANNOT_RUN
    text = path.read_text(encoding="utf-8")
    match = FENCE.match(text)
    if not match:
        print(f"{nid}: carries no frontmatter fence")
        return 1
    try:
        front = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as broken:
        print(f"{nid}: frontmatter does not parse: {broken}")
        return 1
    problems = node_problems(front, relative.parts[0], validator, allowed, names)
    problems += body_problems(text[match.end():])
    for problem in problems:
        print(f"{nid}: {problem}")
    if problems:
        return 1
    print(f"{nid}: sound on its own. Cross-node checks and plan checks did not run; "
          f"they run on the whole delivery.")
    return 0


def standards_held(nodes: dict[str, dict]) -> list[str]:
    """The standards this root's records were written against, and how many pin each. It is here
    because the one thing that silences the whole standard half of this framework is nobody naming
    a registry, and that is invisible from inside an invocation: a delivery written against no
    rules and one written against rules nobody handed over produce the same clean output. The root
    is what remembers. A copy under `standards/` that earlier records pin, beside an invocation
    naming none, is the regression this line exists to make visible."""
    pinned: dict[str, int] = {}
    for node in nodes.values():
        declared = node["front"].get("standard")
        if isinstance(declared, dict) and isinstance(declared.get("at"), str):
            pinned[declared["at"]] = pinned.get(declared["at"], 0) + 1
    return [f"{at}: pinned by {count} record(s); an invocation naming no standard now writes "
            f"source these rules will still be read against"
            for at, count in sorted(pinned.items())]


def outstanding_report(nodes: dict[str, dict], plan_nodes: dict[str, dict]) -> str:
    """What the plan still holds and the delivery does not — derived from the records every
    time, which is why no field records it. A task waits on the dependencies it declares and
    on the entries the base leaves unresolved; both are facts of the plan, read here rather
    than tracked."""
    delivered = {task_of(nid) for nid, node in nodes.items()
                 if node["kind"] == "implementation"}
    proven = {task_of(nid) for nid, node in nodes.items() if node["kind"] == "proof"}
    lines = []
    for tid in sorted(plan_nodes):
        if plan_nodes[tid]["kind"] != "task":
            continue
        front = plan_nodes[tid]["front"]
        if tid in delivered:
            if tid not in proven:
                lines.append(f"{tid}: implemented, and no proof record holds it up")
            continue
        waits = [t for t in listed(front, "depends_on")
                 if isinstance(t, str) and t not in delivered]
        open_entries = len(listed(front, "unresolved"))
        said = [f"no record"]
        if open_entries:
            said.append(f"{open_entries} unresolved entry(ies), which /analyse-domain settles")
        if waits:
            said.append(f"waits on {', '.join(sorted(waits))}")
        lines.append(f"{tid}: {'; '.join(said)}")
    if not lines:
        lines = ["every task has a record, and every record its proof"]
    return "\n".join(lines + standards_held(nodes))


def substrate_report(data: dict, tree: Path) -> tuple[list[str], int]:
    """Which artifacts this registry presupposes the tree holds, and which it does not. Existence
    is the whole of the question: whether a manifest declares the right script is decided by
    running it, and a framework that read one would be reading a stack it ships no knowledge of.
    The absent ones carry the rules they take with them, because a refusal saying an artifact is
    missing tells nobody what it costs, and one naming eleven rules that cannot be applied tells
    them exactly."""
    lines, absent = [], 0
    for entry in listed(data, "presupposes"):
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            continue  # the contract already reported the shape
        where = entry["path"]
        rules = ", ".join(r for r in listed(entry, "rules") if isinstance(r, str))
        if (tree / where).exists():
            lines.append(f"  {where}: stands, and {rules} can be applied")
            continue
        absent += 1
        lines.append(f"  {where}: ABSENT — {entry.get('provides', '')}".rstrip())
        lines.append(f"      unanswerable while it is: {rules}")
    return lines, absent


def check_standard(named: str, against: str | None = None) -> int:
    """Validate one project standard on its own, so a consumer can hold a registry to its contract
    before any review reads it. Every root this framework validates has a validator; a standard is
    not a root, and this is the closest thing it gets. With a tree named, it also answers whether
    that tree holds what the registry presupposes — the one question about a standard that cannot
    be answered from the registry alone, and the one whose wrong answer is discovered a file at a
    time in a review instead of once, before the first of them."""
    try:
        validator = standard_contract()
    except (FileNotFoundError, json.JSONDecodeError) as broken:
        print(f"cannot run: {broken}", file=sys.stderr)
        return CANNOT_RUN
    path = Path(named)
    data, problems = load_standard(path, validator)
    for problem in problems:
        print(f"{path.name}: {problem}")
    if data is None:
        print(f"\n{len(problems)} problem(s). A review is never checked against a standard that "
              f"does not hold together.")
        return 1
    rules = [r for r in listed(data, "rules") if isinstance(r, dict)]
    reading = sum(1 for r in rules if r.get("decided_by") == "reading")
    tools = [r["tool"] for r in rules if isinstance(r.get("tool"), str)]
    load = sorted({step: tools.count(step) for step in tools}.items())
    print(f"standard checked: {path} declares {len(rules)} rule(s) — {reading} decided by "
          f"reading, {len(rules) - reading} by a tool")
    print(f"  pin {pin_of(path)}")
    print(f"  the rules a tool decides run as step(s) "
          + (", ".join(f"{step} ({count} rule(s))" for step, count in load) or "named nothing")
          + f"; a review reads only the {reading} decided by reading")
    if load:
        # The counts are printed rather than the names because the number is what makes an author
        # look. A step exits 0 when it decided every rule resting on it and when it decided none —
        # a linter with no rule loaded for the files it read exits 0 over every one of them — and
        # nothing here can tell those apart without reading a stack it ships no knowledge of. What
        # it can do is show the weight, at the one moment somebody is in a position to check it.
        print("  what a step exits 0 over is the command exiting 0. Whether it is configured to "
              "decide the rule(s) resting on it is this registry's to know: nothing here reads a "
              "stack, and a step deciding nothing passes exactly like one deciding all of them")

    commands = [c for c in listed(data, "commands") if isinstance(c, dict)]
    if commands:
        roles = {c.get("role"): c.get("step") for c in commands if c.get("role")}
        print(f"  it declares {len(commands)} command(s): "
              + ", ".join(f"{c.get('step')} = {c.get('command')}" for c in commands))
        print(f"    installs with {roles.get('install') or 'nothing'}, "
              f"proves with {roles.get('suite') or 'nothing'}, "
              f"and the rest run as checks on both sides of the tests")
    else:
        print("  it declares no command: nothing runs on its own, and a review says which rules "
              "went unanswered")

    packages = [d for d in listed(data, "dependencies") if isinstance(d, dict)]
    print(f"  it authorizes {len(packages)} direct dependency(ies)"
          + (": " + ", ".join(str(d.get("package")) for d in packages) if packages else
             "; a package a delivery needs and this list omits is a stop that names it")
          + ". What they pull in transitively is nobody's approval and the lockfile's record")

    presupposed = listed(data, "presupposes")
    if against is None:
        print(f"  it presupposes {len(presupposed)} artifact(s)"
              + ("; --against <target-source-root> says whether they stand" if presupposed else
                 ": every rule is a condition over a file, and none needs one to exist first"))
        return 0

    tree = Path(against)
    if not tree.is_dir():
        print(f"cannot run: {tree} is not a directory", file=sys.stderr)
        return CANNOT_RUN
    if not presupposed:
        print(f"  it presupposes nothing, so {tree} holds everything it needs to")
        return 0
    lines, absent = substrate_report(data, tree)
    print(f"  against {tree}:")
    print("\n".join(lines))
    if absent:
        print(f"\n{absent} presupposed artifact(s) absent. Source written now answers to a "
              f"registry that cannot be applied to it: the rules above go unanswered, and the "
              f"absence is found once per file in a review instead of once here. The artifact is "
              f"built by a task that declares it in `produces`, planned through /plan-work.")
    return 1 if absent else 0


def main() -> int:
    args = sys.argv[1:]
    verify = "--check" in args
    args = [a for a in args if a != "--check"]
    report = "--outstanding" in args
    args = [a for a in args if a != "--outstanding"]
    single = None
    if "--node" in args:
        at = args.index("--node")
        if at + 1 >= len(args):
            print("cannot run: --node takes a file", file=sys.stderr)
            return CANNOT_RUN
        single = args[at + 1]
        del args[at:at + 2]
    against = None
    if "--against" in args:
        at = args.index("--against")
        if at + 1 >= len(args):
            print("cannot run: --against takes a directory", file=sys.stderr)
            return CANNOT_RUN
        against = args[at + 1]
        del args[at:at + 2]
    if "--standard" in args:
        at = args.index("--standard")
        if at + 1 >= len(args):
            print("cannot run: --standard takes a file", file=sys.stderr)
            return CANNOT_RUN
        named = args[at + 1]
        del args[at:at + 2]
        if verify or report or single is not None or args:
            print("cannot run: --standard stands alone, with --against at most",
                  file=sys.stderr)
            return CANNOT_RUN
        return check_standard(named, against)
    if against is not None:
        print("cannot run: --against says which tree a standard is held against, and only "
              "--standard holds one", file=sys.stderr)
        return CANNOT_RUN
    if report and (verify or single is not None):
        print("cannot run: --outstanding stands alone", file=sys.stderr)
        return CANNOT_RUN
    if len(args) not in (2, 3) or any(a.startswith("--") for a in args):
        print("cannot run: expected [--check | --outstanding | --node <file>] "
              "<delivery-root> <work-root> [<knowledge-root>], "
              "or --standard <file> on its own", file=sys.stderr)
        return CANNOT_RUN

    root = Path(args[0])
    if not root.is_dir():
        print(f"cannot run: delivery root {root} is not a directory", file=sys.stderr)
        return CANNOT_RUN
    work = Path(args[1])
    if not work.is_dir():
        print(f"cannot run: work root {work} is not a directory", file=sys.stderr)
        return CANNOT_RUN
    closed = (work / plan.CLOSURE_FILE).is_file()
    knowledge = Path(args[2]) if len(args) == 3 else None
    if not closed:
        if knowledge is None:
            print("cannot run: a live plan validates against its base, and this validates "
                  "against the plan; name the knowledge root", file=sys.stderr)
            return CANNOT_RUN
        if not knowledge.is_dir():
            print(f"cannot run: knowledge root {knowledge} is not a directory", file=sys.stderr)
            return CANNOT_RUN

    try:
        validator, allowed = contract()
        names = pass_names()
        standard = standard_contract()
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as broken:
        print(f"cannot run: {broken}", file=sys.stderr)
        return CANNOT_RUN

    if single is not None:
        return check_single(root, single, validator, allowed, names)

    plan_nodes, plan_problems = load_plan(work, knowledge)
    if plan_problems:
        for problem in plan_problems:
            print(problem, file=sys.stderr)
        print(f"cannot run: the plan at {work} does not hold together "
              f"({len(plan_problems)} problem(s) above); fix it with plan.py before "
              f"delivering against it", file=sys.stderr)
        return CANNOT_RUN
    nodes, problems = collect(root, validator, allowed, names)
    problems += cross_problems(nodes, plan_nodes, work, names, root, standard)
    if problems:
        for problem in sorted(set(problems)):
            print(problem)
        refused = "the outstanding report" if report else DELIVERY_FILE
        print(f"\n{len(set(problems))} problem(s) over {len(nodes)} node(s). "
              f"{refused} is not derived over a delivery that does not hold together.")
        return 1

    if report:
        print(outstanding_report(nodes, plan_nodes))
        return 0

    delivery = derive(nodes, names)
    graph_contract = json.loads(DELIVERY_GRAPH_CONTRACT.read_text(encoding="utf-8"))
    broken = sorted(Draft202012Validator(graph_contract).iter_errors(delivery), key=str)
    if broken:  # a derivation this script produced and cannot ship is a defect in this script
        print(f"cannot run: the derived delivery does not satisfy "
              f"{DELIVERY_GRAPH_CONTRACT.name}: {broken[0].message}", file=sys.stderr)
        return CANNOT_RUN
    text = json.dumps(delivery, indent=2, ensure_ascii=False) + "\n"
    target = root / DELIVERY_FILE

    if verify:
        if not target.is_file():
            print(f"STALE: {target} does not exist; the delivery has never been derived")
            return 1
        if target.read_text(encoding="utf-8") != text:
            print(f"STALE: {target} is not what the nodes derive to. Run without --check to "
                  f"rewrite it; do not edit it, because every fact in it lives in a node file")
            return 1
        print(f"delivery checked: {target} matches {len(delivery['nodes'])} node(s)")
        return 0

    target.write_text(text, encoding="utf-8")
    by_kind = [f"{count} {kind}" for kind in KINDS
               if (count := sum(1 for n in nodes.values() if n["kind"] == kind))]
    tasks = sum(1 for n in plan_nodes.values() if n["kind"] == "task")
    done = len({task_of(nid) for nid, node in nodes.items()
                if node["kind"] == "implementation"})
    unmet = sum(len(n.get("unmet", [])) for n in delivery["nodes"])
    unproven = sum(len(n.get("unproven", [])) for n in delivery["nodes"])
    findings = sum(n.get("findings", 0) for n in delivery["nodes"])
    print(f"derived {target}: {len(delivery['nodes'])} node(s), "
          f"{len(delivery['edges'])} edge(s), contract {delivery['contract_version']}")
    print(f"  {', '.join(by_kind) or 'no nodes'}; {done} of {tasks} task(s) hold a record; "
          f"{unmet} criterion(s) recorded unmet; {unproven} recorded unproven; "
          f"{findings} finding(s)"
          + ("; the plan is closed" if closed else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
