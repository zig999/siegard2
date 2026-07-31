---
name: siegard-change
description: Procedure for changing a Siegard framework artifact — specs, schemas, commands, agents, skills, hooks, templates, or scripts. Use when adding or modifying framework capabilities, or when a change touches derived or generated artifacts.
---

# Change a Siegard artifact

`CLAUDE.md` **Where authority lives**, **Scope**, and **Change size** hold the rules this procedure
applies. It adds only the order of operations and the derived artifacts that are easy to miss.

## 1. Change the source, not the symptom

Find where the concept is defined — `specs/`, then `docs/adr/`, then `schemas/`, then implementation —
and change the highest-level source that owns it, then update what derives from it. Editing an
implementation to work around a specification is a defect, not a change.

## 2. Name it once

One name for the concept across specs, schemas, code, tests, and docs. A term used normatively needs a
file in `docs/concepts/` and a row in `docs/concepts/index.md`; the contract is `schemas/concept.json`.

## 3. Update everything derived, in the same change

- regenerate what a generator owns rather than editing its output;
- update every dependent contract, template, and test;
- add or update tests for the contract, the transition, the validation, and the packaging;
- a fixture is optional. Where one would catch something the tests cannot, propose it and name what it
  would catch — creating it needs maintainer authorization.

## 4. Classify compatibility

Check the change against the breaking-change test in `.claude/rules/compatibility.md`. If it matches,
follow the requirements there before continuing.

## 5. Verify

Run `/siegard-verify`. This skill describes what to do; it is not evidence that it worked.
