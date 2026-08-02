#!/usr/bin/env python3
"""Hold every schema in schemas/ to its declared contract version.

Two checks, and each exists because .claude/rules/compatibility.md states a rule that
nothing verified.

**Declaration.** A schema file is named `<name>.json` and declares `<name>/<version>` as the
const of its own `contract_version` property. The filename carries identity and the document
carries the version: one contract has one file, and which version that file currently is lives
in the file rather than in its name. A consumer selects behaviour on the declared value and
"must not infer version from shape", so a document declaring a name its file does not match is
a contradiction the consumer would resolve the wrong way.

**Integrity.** A schema whose *constraints* changed while its version did not is the
breaking change that rule names first: "alters a schema so that previously valid instances
become invalid, or previously invalid instances become valid". Every version's constraint
digest is recorded in schemas/contract-versions.json, and a mismatch is reported against
the file that moved.

The digest covers the assertion vocabulary and excludes the annotation keywords — `title`,
`description`, `$comment`, `examples`, `default`, `deprecated`, `readOnly`, `writeOnly`.
Hashing the whole file would demand a version bump for a typo in a description, which the
rule does not call breaking and which would train a maintainer to bump without meaning it.
The stripping is structural rather than textual: inside `properties`, `$defs`, and their
siblings, a key is a *name*, so a property legitimately called `description` — the concept
contract has one — is preserved while the annotation of the same spelling is dropped.

Three schemas carry no `contract_version` property, and the exemption is verified rather than
trusted. The harness owns those vocabularies: a Claude Code component's frontmatter and the
plugin manifest. Each contract sets `additionalProperties: false` because Claude Code silently
ignores an unknown field, so a Siegard-added version field could not be carried without making
every conforming component invalid. This script asserts that each exempt schema really does
forbid additional properties, so the stated reason has to hold for the exemption to apply. Any
*other* schema missing the field fails.

**No migration coverage.** One contract has one file, so two versions never sit side by side and
the trace a bump used to leave — a second version file — no longer exists. The check that required a
registered migration beside such a pair is gone rather than kept unreachable. `foundation/0013` R11 asks
for a migration tested against the old behavior; nothing here verifies that it exists, and that gap
is stated rather than covered by a check that cannot fire.

Regeneration is `--update`, which is never wired into `make validate`: a check that repairs
what it was meant to detect reports success on a defect. The polarity is inverted relative to
project_knowledge.py and measure_ontology.py, whose bare invocation regenerates and whose
`--check` verifies. The name is why — a script called `check_...` that checked only when asked
would be the surprising one.

Declared dependencies: none beyond the standard library.

Usage:  scripts/check_contract_versions.py [--update]
Exit:   0 every contract agrees with its lock, 1 a disagreement, 2 cannot run
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

from cli import cannot_run


REPO_ROOT = Path(__file__).resolve().parent.parent
# Contracts sit in two trees now: the ones the framework ships, under src/claude/schemas/,
# and the ones that govern this repository's own artifacts, under schemas/. Both are locked
# here, because a constraint that moves is a break whichever side it sits on. The lock itself
# is the generator's bookkeeping and never ships.
SCHEMA_DIRS = (REPO_ROOT / "src" / "claude" / "schemas", REPO_ROOT / "schemas")
SCHEMA_DIR = REPO_ROOT / "schemas"
LOCK_PATH = SCHEMA_DIR / "contract-versions.json"


def schema_files():
    """Every contract file across both trees, deterministically ordered."""
    return sorted(
        (p for d in SCHEMA_DIRS if d.is_dir() for p in d.glob("*.json") if p != LOCK_PATH),
        key=lambda p: p.name,
    )

# Files in schemas/ that are not contracts. Named rather than pattern-matched: a file that fails
# the `<name>.vN.json` shape is either an instance like this one or a mistake, and letting the
# pattern decide would silently forgive the second.
#
# `knowledge-notation.json` is the third kind: neither a contract nor an instance of one, but the
# declaration of the envelope every knowledge profile writes in. No document declares it, nothing
# validates against it, and it does not ship — `scripts/check_notation_agreement.py` is what reads
# it, and holds each shipped profile to carrying what it states.
NOT_A_CONTRACT = frozenset(
    {"contract-versions.json", "artifact-classes.json", "knowledge-notation.json"}
)

FILENAME = re.compile(r"^(?P<name>[a-z0-9]+(?:-[a-z0-9]+)*)\.json$")

# JSON Schema keywords that annotate rather than assert. Dropping them is what lets a
# clarified description ship without a version bump.
ANNOTATIONS = frozenset(
    {"title", "description", "$comment", "examples", "default", "deprecated", "readOnly", "writeOnly"}
)

# Keywords whose immediate children are *names* mapped to schemas, not schemas themselves.
# Descending into these without knowing that would delete a property called `description`.
NAME_MAPS = frozenset({"properties", "patternProperties", "$defs", "definitions", "dependentSchemas"})

# Contracts whose artifact cannot carry a `contract_version` field, with the condition that
# has to hold for the exemption to be real. Claude Code owns component frontmatter and ignores
# unknown fields silently, so both contracts close the object; see ADR-0009.
HARNESS_OWNED = frozenset({"skill", "agent", "plugin"})


def previous_lock() -> dict[str, dict]:
    """The lock as it stands, or an empty mapping when there is none to carry forward."""
    if not LOCK_PATH.is_file():
        return {}
    try:
        return json.loads(LOCK_PATH.read_text()).get("contracts", {})
    except json.JSONDecodeError:
        # `--update` over an unparseable lock writes a fresh one rather than refusing. The
        # check path reports the parse error; this path is what repairs it.
        return {}


def carry_superseded(previous: dict[str, dict], digests: dict[str, str]) -> dict[str, dict]:
    """Entries no schema declares any more, marked with what became of each.

    A contract is superseded when a later version of the same name is present, and `--update`
    derives the pointer rather than trusting the old one: the latest declared version of that
    name is the successor by construction.

    A contract carrying `retired_by` is kept verbatim. Its producer was removed, so no later
    version exists to derive a pointer from, and dropping the entry is exactly what
    `docs/adr/0020-retire-the-generation-contracts.md` refuses — a contract that once existed
    would become indistinguishable from one that never did. `--update` may not decide a
    retirement either: the field names a record a person wrote, and inventing one would be the
    regeneration this lock exists to make visible.

    An entry that is neither — no successor and no retirement — is still dropped, because a
    removal the caller has not stated is a breaking change rather than a record to preserve.
    """
    carried: dict[str, dict] = {}
    for contract, entry in previous.items():
        if contract in digests or "/" not in contract:
            continue
        if entry.get("retired_by"):
            carried[contract] = dict(entry)
            continue
        name, version = contract.rsplit("/", 1)
        # The *next* version, not the latest. A chain reaches `/3` through `/2`, and each hop is
        # what `migrate_contracts.py` registers: pointing `/1` straight at `/3` would name a
        # boundary no function crosses. Candidates come from the lock as well as from the schema
        # files, because one file per contract leaves an intermediate version with no file.
        candidates = sorted(
            (int(other.rsplit("/", 1)[1]), other)
            for other in set(digests) | set(previous)
            if other.rsplit("/", 1)[0] == name and other != contract
            and other.rsplit("/", 1)[1].isdigit()
        )
        later = [other for number, other in candidates if number > int(version)] if version.isdigit() else []
        if not later:
            continue
        carried[contract] = {
            "schema": entry.get("schema", f"{name}.json"),
            "constraint_digest": entry.get("constraint_digest", ""),
            "superseded_by": later[0],
        }
    return carried


def registered_migrations() -> set[tuple[str, str]]:
    """The hops `scripts/migrate_contracts.py` can actually perform."""
    import migrate_contracts

    return set(migrate_contracts.MIGRATIONS)


def check_superseded(contract: str, locked: dict[str, dict], digests: dict[str, str]) -> list[str]:
    """A locked contract no schema declares is legitimate as a supersession or a retirement.

    This is the coverage check the second-version-file convention used to carry. It is keyed on
    the lock rather than on two files sitting side by side, so it survives one file per contract,
    and it fires on a missing migration rather than on a missing file.

    Two exits, and `docs/adr/0020-retire-the-generation-contracts.md` separates them. A
    **superseded** contract has a successor, so an artifact declaring it has somewhere to go and
    the compatibility rule owes it a registered hop. A **retired** one has no successor because
    its producer was removed, and demanding a migration for it would demand a function with no
    codomain. What a retirement owes instead is the record that removed the producer, named in
    `retired_by` and verified to exist here — a retirement pointing at nothing is the drift the
    field exists to end.
    """
    entry = locked.get(contract, {})
    retired_by = entry.get("retired_by")
    if retired_by:
        if not (REPO_ROOT / retired_by).is_file():
            return [
                f"{contract}: retired_by names '{retired_by}', which resolves to no file — a "
                f"retirement whose record does not exist states nothing"
            ]
        return []
    successor = entry.get("superseded_by")
    if not successor:
        return [
            f"{contract}: recorded in schemas/{LOCK_PATH.name} but no schema file declares it, and the "
            f"entry names neither superseded_by nor retired_by — a removed contract is a breaking "
            f"change, not a deletion"
        ]
    if successor not in digests and successor not in locked:
        return [
            f"{contract}: superseded_by names '{successor}', which neither a schema file nor the lock "
            f"declares — the record points at a version that does not exist"
        ]
    if successor not in digests:
        # An intermediate hop in a chain: one file per contract means only the current version has
        # one, so `/1 -> /2 -> /3` leaves `/2` fileless by construction. The lock entry is its
        # record, and the migration below is what the chain still owes.
        pass
    if (contract, successor) not in registered_migrations():
        return [
            f"{contract}: superseded by '{successor}' with no migration registered in "
            f"scripts/migrate_contracts.py — .claude/rules/compatibility.md requires an executable "
            f"path, and a bump without one leaves a persisted artifact no way forward"
        ]
    return []


def strip_annotations(node):
    """Return `node` with annotation keywords removed, respecting name maps."""
    if isinstance(node, list):
        return [strip_annotations(item) for item in node]
    if not isinstance(node, dict):
        return node
    out = {}
    for key, value in node.items():
        if key in ANNOTATIONS:
            continue
        if key in NAME_MAPS and isinstance(value, dict):
            out[key] = {name: strip_annotations(subschema) for name, subschema in value.items()}
        else:
            out[key] = strip_annotations(value)
    return out


def constraint_digest(schema: dict) -> str:
    """A stable hash of everything in the schema that can reject an instance."""
    canonical = json.dumps(strip_annotations(schema), sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def contracts() -> tuple[dict[str, dict], list[str]]:
    """Every schema keyed by `<name>/<version>`, plus the problems found reading them."""
    found: dict[str, dict] = {}
    problems: list[str] = []
    for path in schema_files():
        if path.name in NOT_A_CONTRACT:
            continue
        match = FILENAME.match(path.name)
        if not match:
            problems.append(
                f"schemas/{path.name}: filename must be '<name>.json', lower-case and hyphenated"
            )
            continue
        try:
            schema = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            problems.append(f"schemas/{path.name}: not valid JSON: {exc}")
            continue
        name = match["name"]
        declared = schema.get("properties", {}).get("contract_version")
        const = declared.get("const") if isinstance(declared, dict) else None
        if const is None:
            # A harness-owned contract carries no version field; check_declaration decides
            # whether the exemption is real, and keys it by name alone.
            found[name] = {"file": path.name, "schema": schema, "name": name}
            continue
        if not isinstance(const, str) or const.count("/") != 1 or const.split("/")[0] != name:
            problems.append(
                f"schemas/{path.name}: declares contract_version const {const!r}, which does not "
                f"name this file — expected '{name}/<version>'"
            )
            continue
        found[const] = {"file": path.name, "schema": schema, "name": name}
    return found, problems


def check_declaration(contract: str, entry: dict) -> list[str]:
    """The schema's own `contract_version` const must equal what its filename says."""
    file, schema, name = entry["file"], entry["schema"], entry["name"]
    declared = schema.get("properties", {}).get("contract_version")

    if declared is None:
        if name not in HARNESS_OWNED:
            return [
                f"schemas/{file}: declares no `contract_version` property, so a consumer would have "
                f"to infer '{contract}' from shape"
            ]
        if schema.get("additionalProperties") is not False:
            return [
                f"schemas/{file}: exempt from declaring `contract_version` only because Claude Code "
                f"owns this frontmatter and ignores unknown fields, which requires "
                f"`additionalProperties: false` — this schema does not set it"
            ]
        return []

    if "contract_version" not in (schema.get("required") or []):
        return [
            f"schemas/{file}: declares `contract_version` but does not require it, so an instance "
            f"omitting it would pass and carry no version at all"
        ]
    return []




def check(update: bool) -> tuple[int, list[str]]:
    found, problems = contracts()

    for contract, entry in sorted(found.items()):
        problems.extend(check_declaration(contract, entry))


    digests = {contract: constraint_digest(entry["schema"]) for contract, entry in found.items()}

    if update:
        # A superseded entry is carried forward rather than recomputed. `.claude/rules/compatibility.md`
        # keeps one file per contract holding the current version only, so the lock is where a bump
        # leaves its trace; dropping the entry here would make a superseded contract look deleted,
        # which is the finding below that a migration is allowed to answer.
        carried = carry_superseded(previous_lock(), digests)
        entries = {
            contract: {"schema": found[contract]["file"], "constraint_digest": digest}
            for contract, digest in digests.items()
        }
        entries.update(carried)
        LOCK_PATH.write_text(
            json.dumps(
                {
                    "$comment": (
                        "Constraint digest per contract version, written by "
                        "scripts/check_contract_versions.py --update. A digest covers the assertion "
                        "vocabulary only: annotation keywords are stripped, so clarifying a "
                        "description is not a version bump and changing what a schema accepts is. "
                        "Regenerating this file to silence a mismatch discards the only record that "
                        "a contract moved. An entry carrying superseded_by names the version that "
                        "replaced it and is kept for as long as a persisted artifact may declare it."
                    ),
                    "contracts": {c: entries[c] for c in sorted(entries)},
                },
                indent=2,
            )
            + "\n"
        )
        return len(problems), problems

    if not LOCK_PATH.is_file():
        problems.append(
            f"schemas/{LOCK_PATH.name}: missing — run scripts/check_contract_versions.py --update "
            f"to record the current contracts"
        )
        return len(problems), problems

    try:
        locked = json.loads(LOCK_PATH.read_text()).get("contracts", {})
    except json.JSONDecodeError as exc:
        problems.append(f"schemas/{LOCK_PATH.name}: not valid JSON: {exc}")
        return len(problems), problems

    for contract in sorted(set(locked) | set(digests)):
        if contract not in digests:
            problems.extend(check_superseded(contract, locked, digests))
            continue
        file = found[contract]["file"]
        if contract not in locked:
            problems.append(
                f"schemas/{file}: contract '{contract}' is not recorded in schemas/{LOCK_PATH.name} — "
                f"a new contract is recorded with --update, deliberately"
            )
            continue
        if locked[contract].get("constraint_digest") != digests[contract]:
            problems.append(
                f"schemas/{file}: constraints changed but the version is still '{contract}'. "
                f".claude/rules/compatibility.md requires a new version file, a migration path, and a "
                f"migration test — not an edit in place"
            )

    return len(problems), problems


def main() -> int:
    args = sys.argv[1:]
    if args not in ([], ["--update"]):
        cannot_run(f"cannot run: unexpected arguments {args}; usage: check_contract_versions.py [--update]")
    if not SCHEMA_DIR.is_dir():
        cannot_run(f"cannot run: {SCHEMA_DIR} does not exist")

    update = args == ["--update"]
    count, problems = check(update)
    found, _ = contracts()

    verb = "recorded" if update else "checked"
    print(f"contract versions {verb}: {len(found)}  lock: schemas/{LOCK_PATH.name}")
    if problems:
        print(f"FAILED: {count} problem(s)\n")
        for problem in problems:
            print(f"  {problem}")
        return 1
    print("every schema agrees with its declared contract version")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
