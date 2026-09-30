---
id: "SPEC-005"
title: Adoption of existing source
status: proposed
contract_version: spec/1
---

# Adoption of existing source

## Scope

This specification fixes how source no delivery wrote enters a Siegard project: how its facts
reach the specification, how its files reach the trace, and how a project reads how much of its
tree has been adopted. It binds the reconciliation route's adoption staging, the fold that writes
its record, and the report that counts a target's files.

It decides where an adopted system's first specification comes from, what a binding of adopted
source rests on, which files an adopted node is bound to, the states a tracked file is in, and
when an adoption is complete.

Grounds: a pilot over one context of a consumer backend in September 2026 — 15 source files, 69
nodes written from a survey of the source alone — found every node held by at least one file and
none held by no file; 35 findings, 18 of them facts the survey had left out or misread; and a
documentation increment that followed corrected 4 nodes, one of them a behavior the source
exhibits and the documentation forbids.

### Decided elsewhere, deliberately not restated here

- What a specification holds, how material becomes nodes, and what is decided and disclosed —
  `specs/minimal-documentation.md` (SPEC-001) and the analyse skill.
- What an upstream system imposes that a consumed contract may name —
  `specs/metamodel.md` (SPEC-003 §Contract).
- How a test becomes a binding's decider — `specs/test-discipline.md` (SPEC-004).
- The shape of a reconciliation record — `reconciliation.json`; of survey material —
  `survey.json`; of the ledger — `ledger.json`.

## Definitions

- **Adopted source** — source under a target that no delivery wrote and the trace binds nothing
  to.
- **Candidate** — a node an analysis wrote from material read from adopted source, named to the
  staging that judges that source — by the ledger, per file the material read it at, or by the
  invocation.
- **Ledger** — the record beside survey material saying, per fact line, the node that holds the
  fact or why none does.
- **Adoption** — a reconciliation whose record carries `adopted`: every candidate read on every
  file of its set.

## Requirements

### Where the facts come from

- **R1** — Source no delivery wrote is adopted, never re-delivered: its facts reach the
  specification as material, and its files reach the trace through a judgment recorded per node.
- **R2** — The first material of an adopted system is read from its source alone, stating
  observable behavior, each fact beside the path it was read at. Documentation is material for
  the increment that follows, never merged into the first: the first specification is one every
  node of which the source holds, and what the documentation corrects arrives as an ordinary
  change to it.

### What a binding rests on

- **R3** — A binding of adopted source rests on a reconciliation record whose judgment cleared
  the pair. The candidates are named in the invocation, never discovered; a raw bind the caller
  states is not an adoption.
- **R4** — An adopted node binds the files whose judgment holds its fact and no others. A
  candidate no file of the set holds is reported and bound to nothing; a file the trace already
  binds it to must still hold it.

### What the tree holds

- **R5** — Every tracked file under a target is in exactly one state: bound — a binding names it;
  holds-nothing — an adoption judged it and bound none of its candidates to it; outside — an
  adoption kept it out of the judgment; unsurveyed — none of these. The states are computed from
  the trace and the reconciliation corpus, and the report refuses nothing.
- **R6** — Adoption changes no source. Tests already in the tree are certified where the human
  offers them, and prose in source is answered by the routes that already answer it.
- **R7** — Adoption is complete when no file is unsurveyed and no node is unreached. Completion is
  computed, never recorded, and it is no gate: work may begin before it, at the cost the unbound
  files carry into the first review that reaches them.

### What the material owes

- **R8** — Every fact line of the material lands in a node or is left out with a stated reason,
  recorded per line in a ledger beside the material and outside the specification root. A line
  with neither is a fact the analysis dropped, and the ledger is refused. The ledger discloses
  where each fact went; it holds no fact, and no node carries it.
