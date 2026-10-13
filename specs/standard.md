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

Grounds for R3: one consumer tree, `newcatalog`, read on 2026-10-13. Its registry declared no
command while 200 records were delivered; declaring `install`, `typecheck`, `build` and `test`
on 2026-10-11 (commit `126edc6`) made `deliver.py --outstanding` refuse every one of the 200 as
having captured no run, and the commands were withdrawn five minutes later (`dfc74a6`, "until
the project builds and passes its suite"). The same cycle ran again on 2026-10-13 over 40
records (`08461c1`, `abe60f5`, `a1e0626`), and was closed by four baseline runs of ~10 minutes
each and 162 proof records and 15 reviews rewritten to point at a run the delivery never saw.
The validator held each record to the registry as it stood at the reading, while
`standard_of` stated that the pin is a citation of what the record read and that a project
evolving its registry cannot retroactively invalidate what was written against an earlier one.

### Decided elsewhere, deliberately not restated here

- What a rule is, and the split between a rule a reading decides and one a tool decides —
  `schemas/standard.json`.
- That a pin is a citation of what a record read and is never reverified to refuse the record —
  `bin/deliver.py`'s `standard_of`. The one thing comparing it to the file as it stands decides
  is R3 here.
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
- **R3** — A record owes a run of the steps the registry it pins declared, and nothing of a registry that moved since: a step declared after a record was written is owed by the records written after it, and a record pinning an earlier version of the registry its target declares is reported beside the outstanding tasks.

## Validation required before acceptance

1. Every skill whose file runs `deliver.py --outstanding` or reports a review's standard cites the
   requirement it carries.
2. A consumer tree read again after a release holds fewer records pinning no standard where one is
   declared than the 14 of 496 above; if it does not, R1 reports a thing nobody reads and is
   reversed in favor of a refusal over new records only.
3. A consumer tree whose registry gains a step after records exist shows `deliver.py
   --outstanding` deriving its report over those records and naming them as pinning an earlier
   version, and the records written after the step point at a run of it. The criterion that
   reverses R3: a record written while its registry declared a step, pointing at no run, read
   again after an edit to that registry and no longer reported — the figure is the count of such
   records in a tree, and above zero the pin is replaced by the owed steps' names stamped on the
   record at writing.

## Readings

- 2026-10-07 — not yet read: no consumer tree has been re-read under 5.12.0 or later, the
  release that ships R1. The figure is the standard lines `deliver.py --outstanding` prints per
  target, counted over `implementation/` records written after that release. Verdict pending.
- 2026-10-13 — `newcatalog`, under 5.19.0: R3 was not yet in force, and the grounds above are
  its reading — 200 records refused on 2026-10-11 and 40 on 2026-10-13, each time by a step
  declared after they were written. Validation 3 is read at the next consumer window under the
  release that ships R3.
