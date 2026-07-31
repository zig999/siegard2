---
id: "0013"
title: Version the framework so a break is always announced, and a migration is always executable
status: accepted
contract_version: spec/1
---

# The framework lifecycle

## Scope

This specification fixes how the framework changes over time from a consumer's point of view. It decides
five things:

1. what a framework version covers, and how it relates to the finer-grained
   [contract versions](../docs/concepts/contract-version.md) it ships;
2. what a release records, so that a consumer can tell what changed without reading the diff;
3. deprecation — the window a consumer is owed before something stops working;
4. migration — who writes it, what makes it acceptable, and when it runs;
5. the framework's relationship to the harness it targets, including when an externally sourced constraint
   is re-verified.

It does not define what makes a change breaking, or what a breaking change requires. That is
`.claude/rules/compatibility.md`, which is the single authority and is cited rather than repeated. This
document decides the *release mechanics* around that rule.

It governs the framework Siegard ships. It does not govern this repository's own development process, which
`CLAUDE.md` defines.

### Provenance

This document is the family's last and its subject is the least exercised: the framework has never released,
never deprecated anything, and never migrated a consumer.

It is nevertheless the document with the most evidence behind a single requirement. R13 and R14 below exist
because two gaps were recorded rather than theorized. ADR-0009 states plainly that its contracts encode a
snapshot of external documentation, that the retrieval date is recorded so staleness is checkable, and that
"nothing yet forces re-verification". `specs/0010` then added a second retrieval date — for a different set
of pages on an overlapping *subject*, which is not the same thing and is worth saying precisely: no page in
the framework is cited at two dates. R13 closes the gap ADR-0009 named. R14 closes the one the second date
makes visible without yet committing, which is that nothing would notice if the same page were cited twice
at different dates.

R11 has similar grounding of the negative kind: `docs/bootstrap.md` records that the `adr/1` to `adr/2`
contract bump happened *without* a migration test, and lists that debt as owed. ADR-0011 records the same
exposure for `workflow-event/1`. The framework has therefore already twice done the thing R11 forbids, which
is the strongest available argument for stating it.

### Decided elsewhere, deliberately not restated here

- what makes a change breaking, what a breaking change requires, how a contract is versioned, and when
  compatibility should *not* be preserved — `.claude/rules/compatibility.md`, the authority for all four;
- the status vocabulary of a specification or an ADR, who may change a status, and how an
  [amendment](../docs/concepts/amendment.md) differs from a supersession — `docs/adr/README.md`;
- the lifecycle of one [capability](../docs/concepts/capability.md) — `specs/0006` R14 through R17;
- what an installation and an upgrade do, and the distribution manifest that records them — `specs/0008`;
- how a [target pack](../docs/concepts/target-pack.md)'s version relates to the framework's — `specs/0012`
  R8 through R10.

## Definitions

This specification uses these terms as the concept bundle defines them:
[contract version](../docs/concepts/contract-version.md),
[distribution](../docs/concepts/distribution.md),
[capability](../docs/concepts/capability.md),
[target pack](../docs/concepts/target-pack.md),
[amendment](../docs/concepts/amendment.md),
[accepted](../docs/concepts/accepted.md),
[specification](../docs/concepts/specification.md),
[provenance](../docs/concepts/provenance.md),
[fixture](../docs/concepts/fixture.md),
[event log](../docs/concepts/event-log.md).

## Requirements

### What a version covers

- **R1** — The framework carries one version, declared in its plugin manifest, covering everything the
  framework distribution ships. It is what a consumer states when reporting a problem and what an upgrade
  moves between. A [target pack](../docs/concepts/target-pack.md) is outside it: a pack is its own plugin
  with its own version, per `specs/0008` R23 and `specs/0012` R8, so framework and pack compose as a matrix
  rather than as one number.
- **R2** — A contract version is independent of the framework version and finer-grained. A consumer selects
  behavior on the contract version of the artifact in front of it, never on the framework version, because
  one release may ship several contracts at different versions.
- **R3** — A framework version is never reused, and a released version is never rewritten. A defect in a
  release is corrected by a further release.

### What a release records

- **R4** — A release carries a [release record](../docs/concepts/release-record.md) naming every contract
  version it ships, every contract version it dropped, and every capability whose status changed. A consumer
  reads that record rather than diffing two distributions.
- **R5** — A release that breaks compatibility says so in the release record, names what breaks, and points
  to the migration. An undocumented break is a defect; this requirement is what makes the documented one
  legible without reading the specifications.
- **R6** — A release records the harness versions it was verified against. A framework that does not say
  what it was tested with leaves the consumer to discover incompatibility at run time.

### Deprecation

- **R7** — Something removed is deprecated first, in at least one release where it still works while marked
  deprecated. A deprecation announced in the same release that removes it gives the consumer no window and is
  a removal wearing a softer name.
- **R8** — A deprecation names the replacement, or states plainly that none exists. "Deprecated" without
  either is an instruction to stop with no direction to go.
- **R9** — Deprecation is readable from an installation, not only from a release record. The
  [distribution manifest](../docs/concepts/distribution-manifest.md) carries each capability's lifecycle
  status under `specs/0008` R12, so a consumer inspecting what is installed can tell that a capability is
  going away.

### Migration

- **R10** — A migration ships in the release that requires it, not afterwards. A release that breaks
  something and promises a migration later has moved its own debt onto its consumers.
- **R11** — A migration is executable and is tested against the old behavior: the test fails before the
  migration and passes after. A migration that has only been described has not been shown to work.
- **R12** — A migration does not run implicitly during an upgrade. It is invoked deliberately, reports what
  it changed, and is idempotent, so that running it twice is safe and running it once is a decision the
  consumer made.

### The harness

- **R13** — Every constraint the framework derives from external documentation records the page and the date
  it was retrieved, and is re-verified at the next version bump of the contract that carries it. A recorded
  date makes staleness checkable; re-verification at the bump is what keeps it from accumulating.
- **R14** — Where two parts of the framework rely on the same external documentation, they are re-verified
  together and record the same retrieval date. Two dates for one source is a contradiction waiting to be
  discovered by a consumer rather than by the framework.
- **R15** — A behavior the documentation does not specify is not the basis of a guarantee. Where the
  framework depends on one anyway, it says so in the component that depends on it, and the dependency is
  recorded as a risk rather than as a feature.

### What is not promised

- **R16** — The framework promises that identical inputs to an identical framework version produce identical
  control flow, validation outcomes, and recorded state. It promises nothing about the text a model produces.
- **R17** — The framework promises no compatibility for anything it did not ship as a contract. A consumer
  depending on an implementation detail, an internal path, or an artifact's incidental shape is depending on
  something no version protects.

## What satisfied acceptance

Accepted on 2026-07-31 by maintainer decision, which `CLAUDE.md` **Normative sources** makes sufficient on
its own. The conditions this document had set were **not** met. They are kept below rather than deleted,
because they are the evidence this document still owes and removing them on acceptance would turn an open
debt into a silent one.

What that costs is stated rather than glossed. From here `.claude/rules/compatibility.md` governs this
document, so a change to a requirement is a breaking change owing a migration path and a migration test
rather than a revision — and the first component built against it is the thing most likely to demand
exactly such a change. `specs/0001-knowledge-object-driven-development.md` was accepted the other way, on
evidence, with the requirements its three unmet conditions covered moved out to
`specs/0014-acceptance-closure-and-escalation.md` rather than accepted unexercised. That route was
available and was not taken here.

### Conditions recorded before acceptance, still outstanding

1. One release exists, with the record R4 requires. Nothing here is exercised: the framework has never
   released.
2. One migration is written, tested per R11 in both directions, and run against a fixture that was installed
   under the previous version. R11 is the requirement the framework has already violated twice, so satisfying
   it once is the minimum evidence that the mechanism exists.
3. The two debts named in **Provenance** are settled or explicitly written off: the missing `adr/1` to
   `adr/2` migration test recorded in `docs/bootstrap.md`, and the `workflow-event/1` exposure recorded in
   ADR-0011.
4. A deterministic check in `scripts/` reports any documentation page cited at two different retrieval
   dates, which is R14 made mechanical rather than read. The two dates in the framework today are not that
   case, and the distinction is worth recording because an earlier draft of this condition treated them as
   one: ADR-0009 cites the skills, sub-agents, and best-practices pages at 2026-07-29, while ADR-0012,
   `specs/0008`, and `specs/0010` cite the plugins and hooks pages at 2026-07-31. Two dates over two
   disjoint page sets is what R13 produces by design; two dates over *one* page is the contradiction R14
   forbids, and nothing checks for it yet.
5. The [release record](../docs/concepts/release-record.md) of R4 has a versioned schema in `schemas/`. A
   consumer parses it to decide whether to upgrade, which `.claude/rules/contracts.md` places in the row
   requiring one. It arrives with the first release that produces one, on the same rule `specs/0008`
   condition 7 applies to the distribution manifest.
6. R6 has a mechanism. The framework has never been tested against a pinned harness version and nothing
   pins one, so until a fixture runs against a recorded version and the release reads that record, R6
   states a practice rather than requiring one.
7. One capability completes deprecation and removal under R7 through R9, with the deprecation readable from
   an installation rather than only from a release note.
8. A consumer upgrade is performed across a breaking change, end to end, in a fixture: install the old
   version, generate, upgrade, migrate, and regenerate. Until that exists, this document describes a
   lifecycle no artifact has lived through.
