---
paths:
  - "foundation/**"
  - "schemas/**"
  - "src/claude/**"
  - "dist/**"
---

# Compatibility and migration

## A change is breaking when it

- removes or renames a public artifact (skill, agent, hook, schema, template);
- alters a schema so that previously valid instances become invalid, or previously invalid instances
  become valid;
- changes workflow semantics, including transition guards and terminal states;
- invalidates persisted events or the workflow state derived from them;
- changes the observable contract of an installed user-invocable skill.

This list is the test. If a change matches any entry, it is breaking regardless of how small the
diff looks.

## Required for a breaking change

- state the break explicitly in the governing specification or ADR;
- define the supported migration path;
- version the affected contracts rather than mutating them in place;
- add a compatibility or migration test that fails against the old behavior;
- update release documentation.

## Versioning contracts

Increment the version in the contract's own identifier — `review-verdict/1` → `review-verdict/2` — and
keep the file name unchanged. One contract has one file in `schemas/`, holding the current version only.
A consumer selects behavior on `contract_version`; it must not infer version from shape.

The prior version stays recoverable from three places, and a bump is not complete until all three hold:

- `schemas/contract-versions.json` keeps the superseded entry, with its constraint digest and the version
  that replaced it. That record is what makes the bump visible without a diff, and removing it is how a
  superseded contract becomes indistinguishable from a deleted one;
- `scripts/migrate_contracts.py` registers an executable migration for the hop. A path that is only
  described has not been shown to work;
- version control holds the superseded schema text.

A second version file was the earlier convention and is not used. It put the version in the file name,
which `scripts/check_contract_versions.py` cannot represent — it matches a contract file as `<name>.json`
and requires the declared version to name that file — so the two records of one version disagreed by
construction. What that convention bought was a check keyed on two files sitting side by side; the lock
entry above buys the same check keyed on a record instead, and the check fires on a missing migration
rather than on a missing file.

## When not to preserve compatibility

Do not preserve compatibility that would retain incorrect or unsafe behavior. Break it, and record
the exception and its migration in the governing specification or ADR. An undocumented break is a
defect; a documented one is a decision.
