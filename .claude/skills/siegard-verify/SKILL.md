---
name: siegard-verify
description: Verify a Siegard framework change before reporting it complete. Use when finishing work on this repository, before claiming a change is done, or when asked to check, validate, or verify framework changes, schemas, or the generated distribution.
---

# Verify a Siegard change

Run this before reporting any framework change complete. Every step either produces a result or
produces a named gap — it never produces a silent pass.

## 1. Run the validation for the affected area

| Area touched | Command |
|---|---|
| `schemas/`, `specs/` | `make validate` |
| any framework source | `make test` |
| distribution inputs (`.claude/`, `templates/`, `scripts/`) | `make dist` then `make validate` |
| broad or uncertain scope | `make check` |

**If the command does not exist**, stop treating this as a passing step. Record it verbatim as:

> `make validate` — not run: no target exists in this repository.

The prohibition itself lives in `CLAUDE.md` under **Commands**; this step only says how to record the
gap.

## 2. Check the normative chain

The change is complete only when these agree. Name any that do not:

- the governing specification or ADR states the intended behavior;
- the schema or contract encodes it;
- the implementation satisfies the contract;
- a test covers the contract, the transition, and the failure outcome;
- the generated distribution reflects the source;
- the documentation describes the current behavior, not the previous one.

## 3. Check authority placement

- Does any rule introduced by this change now exist in two places? Remove the duplicate; keep the
  higher-level source.
- Did a prompt become the only place a rule lives, where a schema or validator could hold it? Move it.

## 4. Inspect the diff

- unrelated changes: revert them into their own change;
- source-only paths (`specs/`, `tests/`, `fixtures/`, `docs/`) appearing under `dist/`: fix the
  generator;
- secrets, credentials, or environment-specific values anywhere in the distribution: remove them.

## 5. Report

State plainly:

- the commands run and their actual results;
- every check that did not run, and why;
- what remains open.

A report that omits a skipped check is a false report. If step 1 produced nothing runnable, say that
the change is unverified and explain what would verify it.
