# The adr/1 → adr/2 migration

The input a migration test needs and `docs/adr/` cannot supply.

`.claude/rules/compatibility.md` requires a breaking change to define a migration path and to add a
test that fails against the old behavior. The `adr/1` → `adr/2` bump shipped with neither.
`docs/bootstrap.md` recorded that as owed, and a recorded debt is not a check.

## What it holds

| Path | What it is |
|---|---|
| `before.md` | one ADR at `contract_version: adr/1`, held there permanently |

There is no `after.md`. The migrated document is computed by `tests/test_migrations.py` and asserted
against `schemas/adr.v2.json`; committing the output would create a second copy of a fact the
migration already derives, and it would drift the first time the contract moved again.

## Why the input could not come from `docs/adr/`

Every ADR there was rewritten to declare `adr/2` when the contract moved. A migration exercised only
against documents that already migrated tests nothing — it would pass even if the migration returned
its input unchanged.

The id `9001` is outside the range `docs/adr/` allocates, and `scripts/validate_adrs.py` reads
`docs/adr/` only, so this file is never loaded as a decision. `tests/test_migrations.py` asserts both,
because a fixture that drifted into looking like a real ADR would be worse than no fixture.

## What it is evidence for

- **The break was real.** `schemas/adr.v2.json` rejects this document on `contract_version`, which is
  the first entry in the rule's own list: previously valid instances become invalid. Without this
  assertion, a migration test could pass over a change that was never breaking.
- **The path works.** `scripts/migrate_contracts.py` carries the document across, and the result
  validates against `adr/2` with every other field preserved.
- **The path invents nothing.** `amends` is what `adr/2` added, and it is optional. The migration does
  not supply one, because a migration that authored a field would be deciding something the original
  document never said.
- **A bump with no path is now detectable.** `scripts/check_contract_versions.py` reports two adjacent
  versions of one contract with no registered migration between them, so the debt this fixture pays
  cannot recur silently.

## What it is not evidence for

- **That `adr/1` documents still exist anywhere else.** They do not. This is a constructed input, not
  a survivor, and the migration has therefore never run against a document it did not expect.
- **That the migration handles a malformed `adr/1` document.** It refuses one declaring another
  version, and that refusal is tested; it does not repair a document that is invalid under `adr/1`
  itself, and nothing here claims it should.
- **That `schemas/adr.v1.json` is still reachable by any validator.** It is not wired into
  `make validate`. It is kept readable because this fixture references it, which is exactly the
  condition **Versioning contracts** in `.claude/rules/compatibility.md` states.
