---
name: siegard-change
description: Procedure for changing a Siegard framework artifact — specs, schemas, commands, agents, skills, hooks, templates, or scripts. Use when adding or modifying framework capabilities, or when a change touches derived or generated artifacts.
---

# Change a Siegard artifact

## 1. Locate the authority before editing

Find where the concept is currently defined, in precedence order: `specs/`, then `docs/adr/`, then
`schemas/`, then implementation. Change the highest-level source that owns the concept, then update
what derives from it.

Editing an implementation to work around a specification is a defect, not a change.

If sources disagree, stop and follow the conflict protocol in `CLAUDE.md`: name the conflicting files
and the incompatible statements, resolve the highest-level source first, and do not merge or pick
between contradictory rules on your own.

## 2. Reuse before adding

Answer these against the **Scope** section of `CLAUDE.md`, which is the authority for all three:

- Does an existing concept already cover this, with its semantics still valid? Reuse it.
- Is this a new abstraction, and does a current requirement need it with a testable contract?
- Is this framework work at all, or a downstream application need in disguise?

## 3. Name it once

Use one name for the concept across specs, schemas, code, tests, and docs. Add a concept file to
`docs/concepts/` before using a term normatively, then run `make validate`. A term used in a rule but
absent from the bundle is an interpretation waiting to drift.

The frontmatter contract is `schemas/concept.v1.json`; `docs/concepts/index.md` lists the bundle and
must gain a row for the new concept.

## 4. Update everything derived

In the same change:

- regenerate artifacts a generator owns rather than editing the output;
- update every dependent contract, template, and test;
- add or update tests for the contract, the transition, the validation, and the packaging;
- add or update the fixture in `fixtures/` that exercises the capability as a downstream-shaped case.

## 5. Classify compatibility

Check the change against the breaking-change test in `.claude/rules/compatibility.md`. If it matches,
follow the breaking-change requirements there before continuing.

## 6. Verify

Run `/siegard-verify`. Do not report the change complete on the strength of this procedure alone —
this skill describes what to do, not evidence that it worked.
