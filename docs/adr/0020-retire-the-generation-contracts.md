---
id: "0020"
title: Retire the generation contracts, and record the removal the code already performed
status: accepted
contract_version: adr/1
---

# Retire the generation contracts, and record the removal the code already performed

## Context

Seven contracts sit in `schemas/contract-versions.json` with no schema file left to declare them:
`artifact-class/1`, `generation-manifest/1`, `generation-plan/1`, `generation-scope/1`,
`pack-declaration/1`, `placement-decision/1`, and `change-request/1`. Two more —
`context-package/1` and `specification-delta/1` — sit the same way and are already covered by
`docs/adr/0016-remove-the-workflow-machinery.md`.

Each lost its schema when the capability that produced it was removed. The generation path went
first — the scope, the plan, the manifest, the materializer, the pack model, and the `generate`
skill — and its absence is the condition that emptied `status` of consumers, which is why the
field was removed rather than kept for a reader. `change-request/1` went with
`foundation/0001` R2, which states that a request is not a contracted artifact of this framework
and that no capability produces one.

What none of those changes did was record the *contract* retirements. `.claude/rules/compatibility.md`
makes removing a public schema breaking and requires the break to be stated in a specification or an
ADR. For `change-request/1` a specification states it. For the other six there is no record, and
`scripts/check_contract_versions.py` reports each as a lock entry whose contract vanished.

The check could not report it while it was written, because the commit that removed the last of the
generation path also deleted `src/claude/bin/cli.py`, which every validator in `make validate` imports.
For three commits the lock has been unverifiable, and four contracts changed their constraints inside
that window without a bump — recorded in the Consequences below.

## Decision

The nine contracts above are retired. A retired contract is a third state beside current and
superseded: no schema declares it, no successor replaces it, and no persisted artifact may still
carry it.

`schemas/contract-versions.json` keeps its entry, carrying `retired_by` — the specification or the
decision record that removed the capability producing it. The entry stays because deleting it would
make a contract that once existed indistinguishable from one that never did, and the lock is the only
place in this repository that could tell the difference.

`retired_by` is not `superseded_by` with a softer name. A superseded contract has a successor, and the
compatibility rule owes it a registered migration, because an artifact declaring the old version has
somewhere to go. A retired one has nowhere to go by construction, and demanding a migration for it
would demand a function with no codomain.

`scripts/check_contract_versions.py` accepts the field and verifies the reference resolves to a file
that exists — a retirement pointing at nothing is the drift this record exists to end.

## Consequences

**Nothing installed changes.** No capability read these contracts; each lost its producer before this
record was written. `make dist` output is unaffected, and no consumer carries an artifact declaring a
retired version — this repository holds no fixtures, per
`docs/adr/0019-the-repository-keeps-no-fixtures.md`, and no distribution.

**Four bumps that were owed are now paid, and they are the reason this record found them.** Restoring
the validators surfaced four schemas whose constraints moved while their version did not, all in the
commit that also broke the validators:

- `schemas/capability-declaration.json` widened `outputs` from `minItems: 1` to `0`;
- `src/claude/schemas/domain-model.json` added a required pair to `request`;
- `src/claude/schemas/validation-evidence.json` changed an identifier pattern from `^cr_` to `^rq_`;
- `src/claude/schemas/impact-analysis.json` moved to `/3` in the file without a lock entry or a
  registered hop from `/2`.

Each is breaking under `.claude/rules/compatibility.md`, and each is versioned here rather than left
as an edit in place.

**One check was wrong and is corrected.** `check_superseded` required a `superseded_by` target to be a
version some schema file declares. With one file per contract, an intermediate version in a chain —
`impact-analysis/2` between `/1` and `/3` — has no file by construction, so a two-hop chain could never
pass. The check now accepts a successor that any lock entry names.

**Release documentation is not updated, because none exists.** The obligation is unmet and recorded as
unmet, for the same reason `docs/adr/0014-a-verdict-over-an-empty-base-names-nothing.md` records one.

### What was rejected

**Deleting the entries.** Cheapest, and it discards the only record that the contract existed. The
lock's own `$comment` says an entry is kept for as long as a persisted artifact may declare it, which
reads as licence to delete once nothing does — but the entry answers a second question the comment does
not name: whether a version a reader meets in an old artifact was ever real. Version control holds the
schema text; nothing but the lock holds the fact that it shipped.

**Restoring the schemas so the entries resolve.** It would turn a green check into a lie: a contract
whose producer does not exist is not current, and shipping the file would invite the next capability to
build on it.

**Folding the four bumps into the versions this repository is about to write anyway.** Two of the four
are contracts that later work touches again. Folding would hide a change already made inside a change
not yet made, and the digest is precisely the record that distinguishes them.

### What would falsify this

A consumer holding a persisted artifact that declares one of the nine. That would mean the contract was
reachable when it was removed, the removal owed a migration, and a retirement without one was the wrong
call. Nothing in this repository can hold such an artifact today, which is why the state is admissible
at all.
