---
id: "SPEC-007"
title: The project's standard, read back
status: proposed
contract_version: spec/1
---

# The project's standard, read back

## Scope

This specification fixes what the framework says about whether a project's own standard
(`schemas/standard.json`) reached the work it governs. It binds `bin/deliver.py` and the skills
whose reports carry its output. It does not decide what a rule requires, which rule is mandatory,
or whether a departure is acceptable: no rule carries a severity and no pass here derives a
verdict, which the standard's contract states and this specification leaves as it is.

Grounds: the delivery records of three consumer trees, read from disk on 2026-10-07 by counting
the records of `implementation/` whose front matter holds no `standard:` where the project file
declares one. The count is of records, not of runs: `ifs` held 7 of 126 without it, all written
three days after its project file declared the registry; `servicedeskn1` held 7 of 370 — none of
them refused, because the validator holds a record's citations to the registry it pins and never
holds the pin to the registry the project declares; `eternal` held 0 of 22. Whether a record
omitted it by choice or by omission is not readable from the record. In the same reading, no
framework output named a file of a reviewed set that no rule of the registry reaches.

### Decided elsewhere, deliberately not restated here

- What a rule is, and the split between a rule a reading decides and one a tool decides —
  `schemas/standard.json`.
- That a pin is a citation of what a record read and is never reverified against the registry as
  it stands — `bin/deliver.py`'s `standard_of`.
- That a review's findings are evidence and its report is not a verdict — `specs/handoff.md`
  (SPEC-006 R4).

## Definitions

- **Declared standard** — the registry `siegard.json` names for a target, or `null` where it
  declares the project follows none.
- **Pinned standard** — the registry a delivery record names in its `standard` field.
- **Reached** — a path is reached by a rule when one of the rule's scopes reaches it.

## Requirements

- **R1** — A delivery record that pins no standard, or a standard other than the one its target declares, is reported beside the outstanding tasks and refused nowhere.
- **R2** — A review reports the paths of its file set that no rule of the standard reaches, apart from the rules that do.

## Validation required before acceptance

1. Every skill whose file runs `deliver.py --outstanding` or reports a review's standard cites the
   requirement it carries.
2. A consumer tree read again after a release holds fewer records pinning no standard where one is
   declared than the 14 of 496 above; if it does not, R1 reports a thing nobody reads and is
   reversed in favor of a refusal over new records only.
