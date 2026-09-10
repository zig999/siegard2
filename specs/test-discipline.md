---
id: "SPEC-004"
title: Test discipline
status: proposed
contract_version: spec/1
---

# Test discipline

## Scope

This specification fixes how the framework derives, sizes and certifies the automated tests that
prove a delivered task: what a test is owed to, when one is written, when writing stops, and when
a test rather than a reading decides that a specification node's fact still holds. It binds the
agent that writes a proof, the agent that audits coverage, and the entry points that hand them
their inputs.

It decides the obligation set, the necessity and stopping rules, the partition of inputs, the
preference for a test over a reading wherever a finite test decides a fact, and which halves the
validator enforces mechanically.

Grounds: measured over 483 proof records and 95 reviews of two consumer projects in September
2026, the share of criteria a coverage audit found covered rose from 60% at one test per
criterion to 83% at two, and stayed between 78% and 82% at three or more. The proofs averaged
2.5 tests per criterion, the test code ran to 3.6 times the source it proved, and no specification
node of either project was decided by a test.

### Decided elsewhere, deliberately not restated here

- The shape of a proof record, a coverage entry and a certification return —
  `delivery-node.json` and `certification-return.json`.
- How a certified test becomes a binding's decider, and what a drift on the test does —
  `trace.json` and `bin/trace.py`.
- How a project arranges its tests — file placement, naming, stand-ins, levels, table-driven
  cases — the project's own standard under `standard.json`, never this framework.
- What a task's criteria are and how a plan writes them — the plan-work skill and its decomposer.

## Definitions

- **Obligation** — one condition a proof owes evidence to: a criterion of the task as the task
  states it; the fact of a specification node the task implements; an `UNDERDETERMINED` entry of
  the task's notes.
- **Evidence** — a test that fails when the obligation it protects is violated.
- **Finite test** — a test that decides a fact whole: one input against one expected result, or
  every pairing of a declared finite set.
- **Equivalence class** — inputs an obligation treats alike. A **boundary** is the input at which
  the obligation changes what it requires.
- **Redundant test** — a test whose removal leaves every obligation with evidence and every
  boundary protected.

## Requirements

### Derivation

- **R1** — Every test is derived from an obligation, never from the structure of the source: a
  class, a method, a branch or an internal call is not a reason for a test to exist.
- **R2** — Every test states what would have to break for it to fail. A test that cannot fail, or
  that asserts a literal or a value it computed itself, is not evidence and is not written.
- **R3** — A test asserts observable behavior — what is returned, answered, refused or recorded —
  and never which internal call happened; two implementations that both satisfy the obligation
  both pass it.
- **R4** — A behavior no obligation states is not tested. An inference the implementation recorded
  is not an obligation: an inference about arrangement gets no test, and an inference about
  behavior is a fact the specification does not hold, recorded as unproven and never pinned by a
  test.

### Size

- **R5** — A test is written only where it protects an obligation, or a stated part of one, that
  no other test protects. A test whose removal would leave every obligation protected is
  redundant and is not written.
- **R6** — Inputs are partitioned into equivalence classes; one representative per class is
  tested, and each boundary at which the obligation changes behavior is tested. A dimension of
  input that does not alter what the obligation requires never multiplies the set.
- **R7** — At most one test per valid behavior that is semantically distinct; a second example of
  the same valid behavior is redundant.
- **R8** — Writing stops when every obligation has evidence and no test is redundant. A test
  beyond that point names the distinct boundary it protects, or it is not written.
- **R9** — A test fails for one reason. Obligations share a test only where a failure still names
  which obligation was violated.

### What a test decides

- **R10** — Where a node the task implements states a fact a finite test decides, the proof
  carries a test that fails if that fact stops holding, whole, and names the node on that test.
  A finite test is preferred to a reading wherever one exists: a reading is the fallback for a
  fact no finite test decides, never the default for one a test could.
- **R11** — A declared transition set is finite: a node stating every pairing of a state and a
  trigger as a transition or a rejection is decided by a test over every pairing.
- **R12** — A fact no finite test decides — an identity spanning files, a totality over a set
  nothing enumerates — is recorded as unproven with why, and is never approximated by a test
  that asserts part of it as the whole.
- **R13** — Every claim that a test demonstrates a node is carried to certification by the review
  that reads the proof, and a node the task implements that no test claims is named in that
  review's report with the reason the proof gives; a claim certified is what makes the binding
  one a test decides.

### Coverage

- **R14** — Coverage is stated per obligation, never as a figure: the state of each obligation is
  named, and no percentage, line or branch measure stands in for it.

## Validation required before acceptance

1. The test author's judgment states R1 to R12 and cites each in the words above; the coverage
   auditor's judgment states R14 and the finite-test rule of R11; `tests/test_spec_citations.py`
   proves each quote is a substring of the requirement it names.
2. The delivery-node contract requires of every test what R2 requires, and refuses a proof naming
   a node the task does not implement — `tests/test_deliver.py` proves each.
3. The certification contract admits a remainder a test can close and one no test can, and names
   as examples of the second only facts R12 names; `tests/test_reconcile.py` proves the contract
   demonstrates every outcome.
4. Over the next consumer deliveries the measurement in the scope above is repeated: tests per
   criterion, covered share per review, and the count of nodes decided by a test. A covered share
   that falls below the two-tests-per-criterion figure recorded there is what reopens R5 to R8.
