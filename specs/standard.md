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
verdict, which the standard's contract states and this specification leaves as it is. It also
fixes which side of a delivery's proof a rule's step decides it on.

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

Grounds for R4: the registries of the consumer trees on one workstation, read on 2026-10-31,
held 25 rules decided by a step other than the suite whose scope reaches the tests their project
declares — 12 in one registry, 13 in another. 24 of them constrain how a test is written and
hold over a tree that holds none. One requires a test to exist — a contract test for every routes
file — and the build, which runs before the proof is written, could never pass for a task that
wrote a routes file. The schema already said a rule is a condition over a file that exists and
never a requirement that one does; nothing said which step such a rule may name.

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
- **R4** — A rule decided by a step other than the one whose role is `suite` holds over a tree that holds no test of the task being delivered; a rule that requires a test file to exist names the `suite` step.

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
4. `bin/deliver.py --standard <file> --against <target>` names the rules a step other than the
   suite decides whose scope reaches the tests the target declares, and refuses none of them:
   whether a rule requires a test to exist or constrains a test that exists is a reading, and a
   scope cannot say which — 1 of the 25 above was the first — so the report states R4 beside the
   names and the registry's author reads them. `tests/test_deliver.py` proves the report and that
   it refuses nothing. The criterion that reverses the report into a refusal: a mechanical
   discriminator between the two kinds that agrees with a reading on every rule of the
   registries above.

## Readings

- 2026-10-07 — not yet read: no consumer tree has been re-read under 5.12.0 or later, the
  release that ships R1. The figure is the standard lines `deliver.py --outstanding` prints per
  target, counted over `implementation/` records written after that release. Verdict pending.
- 2026-10-13 — `newcatalog`, under 5.19.0: R3 was not yet in force, and the grounds above are
  its reading — 200 records refused on 2026-10-11 and 40 on 2026-10-13, each time by a step
  declared after they were written. Validation 3 is read at the next consumer window under the
  release that ships R3.
