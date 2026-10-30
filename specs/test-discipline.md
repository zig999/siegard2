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
preference for a test over a reading wherever a finite test decides a fact, that no test a
delivery changes goes unnamed by its records, and which halves the validator enforces
mechanically.

Grounds: measured over 483 proof records and 95 reviews of two consumer projects in September
2026, the share of criteria a coverage audit found covered rose from 60% at one test per
criterion to 83% at two, and stayed between 78% and 82% at three or more. The proofs averaged
2.5 tests per criterion, the test code ran to 3.6 times the source it proved, and no specification
node of either project was decided by a test. Over the same period, 13 of 97 delivery commits of
one of the two projects changed a file under the target that no record of the delivery named —
every one of them a test file or a test's helper, an existing test adjusted as often as a new one
left out — so the file set the review that followed was handed never held them.

### Decided elsewhere, deliberately not restated here

- The shape of a proof record, a coverage entry and a certification return —
  `delivery-node.json` and `certification-return.json`.
- How a certified test becomes a binding's decider, and what a drift on the test does —
  `trace.json` and `bin/trace.py`.
- How a project arranges its tests — file placement, naming, stand-ins, levels, table-driven
  cases — the project's own standard under `standard.json`, never this framework.
- What a task's criteria are and how a plan words them — the plan-work skill and its decomposer;
  which task a proof belongs to is R18 and R19.

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
  A finite test is preferred to a reading, and to a registry step's decision, wherever one exists:
  a reading or a step is the fallback for a fact no finite test decides, never the default for one
  a test could.
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
- **R15** — The coverage audit names every test in the set that no criterion it was handed
  derives, with what the test asserts. It is R1 and R4 read from the evidence side: a test with no
  obligation is a proof of something nobody stated. It is a reading and never a verdict — a test
  proving a node's fact under R10 stands there until the certification R13 carries claims it, and
  which of the two a test is, and what follows, is a person's.

### What a delivery names

- **R16** — Every path a delivery created, modified or deleted under its target source root is
  named by one of the delivery's records: the implementation's `files`, or the proof's `tests` or
  `files`. The file set a review is handed is the one the records name, so a path none names is a
  change no review reads, and a test changed there is changed where nobody would see it. A
  delivery whose tree holds such a path is refused before it is validated, and the refusal names
  the path.
- **R17** — A proof's `tests` name files its target source root holds while its plan is live. A
  test that moved or went is proved again, by the proof written anew; over a closed plan the
  record stands as written, and a test the tree no longer holds is reported, never refused.

  Grounds: on 2026-10-19 one consumer's proofs named 381 test paths its tree no longer held, a
  test directory having moved by hand, and `deliver.py --check` passed every delivery root that
  held them; all 381 sat in closed plans. A second consumer held none.

### Where a proof is cut

- **R18** — A task writes source, or its implementation already stands. A task that writes no source carries `stands`, and every file it names is bound in the trace, before the task is written, to every node the task implements. A fact the plan's own deliveries will write into source is proven by the task that writes it, as that task's criterion, never by a task of its own.
- **R19** — A node whose fact already stands in source the trace does not bind to it gets no proof task. The plan reports the reconciliation that would bind it, over the files that hold it, and the proof waits for that binding.
- **R20** — A delivery whose implementer finds every criterion of the task already met by source the tree holds writes no record and stops, naming the files that hold the fact. Where the trace binds every node the task implements to those files, the door is the plan over this slug carrying `stands` over them; where it does not, the door is the reconciliation over them, and the plan waits for that binding.

  Grounds: on 2026-10-30, reading every `orchestration.md` under the delivery roots of the sales consumers
  for a line naming a task whose implementer found the criteria met and wrote no file, 20 tasks in 5
  plans of two consumers stopped with `files` empty and no `stands` (13 of them in one plan); the estimator is that
  line match, so a stop logged in other words is not counted. The record writer refuses such a
  return, and nothing stated what the delivery then hands: each orchestration chose its own door,
  withdrawing the task from the plan in some and planning it again with `stands` in others.

  Grounds: on 2026-10-26 three successive plans of one consumer cut proof-only tasks in the
  ordinary decomposition, and none could be delivered — the record writer accepts a task that
  writes no source only with `stands`, and `stands` confirms only bindings the trace already
  holds. Two plans named files whose bindings did not cover the task's nodes, one of them a node
  the same run had just created (7 of 7 tasks, then 1 of 1); the third cut a proof of a
  constraint sibling tasks of the same plan implemented, and carried no `stands` at all. Each was
  refused at delivery, after the plan was committed; a goal over the third ended there. A
  plan-shape rule for the third form — a task whose nodes its dependencies all implement — fires
  on 96 tasks across five consumers, 94 of which wrote source, so R18's second sentence is held by
  the decomposer's judgment and not by a validator.

- **R21** — A re-delivery of a task whose own earlier implementation record names every file that holds the fact is not the stop R20 states: the record is written again over those files, answering the task as it stands. A re-delivery names a file the tree did not change only where the record it replaces named it.

  Grounds: on 2026-10-30 one consumer re-bound eight delivered tasks whose implemented nodes had
  moved; the re-bind widened what each task implements and changed no criterion, so `deliver.py
  --check` refused all eight records (50 problems) for answering nodes they never read. The
  implementer of each re-delivery finds every criterion met by the files its own first delivery
  wrote, and R20 then stopped it; over three of the eight, `trace.py --encodes` bound 5, 5 and 10
  of the task's nodes to nothing, so the door R20 hands was `/reconcile`, then the plan carrying
  `stands`, then the delivery again — for a task whose files were already its own.

- **R23** — A task delivered as the substrate alone — it declares `produces`, and nothing it wrote is a file a rule of its standard reaches — owes no proof. Every other task owes one, a task that built the substrate and also wrote a file a rule reaches included.

  Grounds: `/implement-task` wrote no proof for any task that produced the substrate, while the
  validator exempted only the substrate alone from the proof a dependent needs. On 2026-10-30,
  across seven consumers, four substrate tasks held an implementation record and no proof; two
  of them had written test files the standard's rules reach and implemented 3 and 5
  specification nodes. No route returns to a delivered task, so neither proof was ever written:
  one plan was closed over it, and a goal over the other ended in state B with every other task
  of its scope delivered — while the full suite of its last review ran that task's 9 test files
  green.

### What a review answers for

- **R22** — A review answers for its tasks as they stood when it was written. A task is reviewed as it stands where a review naming it lists every file the task's records name and, where its coverage pass ran, answers every criterion the task states; a task some review names and none answers as it stands is owed a review, and a review written before the task or its records changed is never refused for it. The review being written is held to its tasks as they stand, and refused where it falls short.

  Grounds: a review carries no pin, and every review was held, for as long as its plan was live,
  to the records and criteria of today. On 2026-10-29 one consumer's proof-only re-delivery wrote a
  helper after the first review of its task; the second review listed it, and the first was
  refused from then on — `deliver.py --check` failed, `/review-change` refuses to run over a
  delivery that fails it, and `--outstanding` refused to derive. On 2026-10-20 another consumer's
  re-plan reworded the criteria of reviewed tasks; its one review drew 17 refusals no later
  review could clear, and the person closed the plan to carry the work into a new initiative.
  Across seven consumers on 2026-10-30, these were the only two plans whose reviews drew either
  refusal.

## Validation required before acceptance

1. The test author's judgment states R1 to R12 and cites each in the words above; the coverage
   auditor's judgment states R14 and R15 and the finite-test rule of R11; `tests/test_spec_citations.py`
   proves each quote is a substring of the requirement it names.
2. The delivery-node contract requires of every test what R2 requires, refuses a proof naming a
   node the task does not implement, refuses an unpaired list under a coverage pass that did not
   run, and admits a review written before the list existed — reporting it as one whose tests
   were never read for what no criterion derives, never refusing the delivery root that holds it
   — `tests/test_deliver.py` proves each.
3. The certification contract admits a remainder a test can close and one no test can, and names
   as examples of the second only facts R12 names; `tests/test_reconcile.py` proves the contract
   demonstrates every outcome.
4. `bin/deliver.py --unrecorded` refuses a tree holding a path under the target that no named
   record names, admits a helper the proof's `files` names and a deleted path a record names, and
   never counts the framework's own roots as the delivery's change; `tests/test_unrecorded.py`
   proves each.
5. For R17: `bin/deliver.py --check` refuses a live plan's proof naming a test its target does
   not hold, names the path, and hands the proof's rewrite; over a closed plan it prints the same
   finding as a receipt and exits as it would without it; a proof whose tests the target holds
   draws neither — `tests/test_deliver.py` proves each
   (`test_a_live_proof_naming_a_test_the_target_does_not_hold_is_refused`,
   `test_a_closed_proof_naming_a_test_the_target_does_not_hold_is_a_receipt`).
6. For R18 and R19: `/plan-work` holds every task carrying `stands` to `trace.py --encodes`
   before it writes it, and states both requirements in the words above; the backlog decomposer
   states R18's last sentence; `tests/test_spec_citations.py` proves each quote is a substring of
   the requirement it names.
   For R20: `/implement-task` runs `trace.py --encodes` over the files a no-write return names
   and hands the door that output decides, and the task implementer returns that case without a
   record — `tests/test_skill_contract.py` proves both.
   For R21: `bin/deliver.py --unrecorded` refuses a re-delivered implementation naming a file the
   tree did not change that the record it replaces did not name, and admits one the record it
   replaces named; `/implement-task` hands the implementer the record a re-delivery replaces —
   `tests/test_unrecorded.py` and `tests/test_skill_contract.py` prove each.
   For R22: `bin/deliver.py --check` admits a review that lists fewer files than its tasks'
   records now name, or answers criteria its tasks no longer state, and refuses it under `--review`
   naming it; `--outstanding` names a task some review names and none answers as it stands, and
   no task one review answers — `tests/test_deliver.py` proves each.
   For R23: `bin/deliver.py --outstanding` names a task delivered as the substrate alone apart
   from a task implemented and unproven, and counts it delivered; `/implement-task` writes no proof
   only for a task that report names so — `tests/test_deliver.py` and `tests/test_skill_contract.py`
   prove each.
7. Over the next consumer deliveries the measurement in the scope above is repeated: tests per
   criterion, covered share per review, and the count of nodes decided by a test. A covered share
   that falls below the two-tests-per-criterion figure recorded there is what reopens R5 to R8.

## Readings

- 2026-10-07 — not yet read: the measurement has no measurer in the distribution — the grounding
  figures were produced by throwaway scripts outside this repository — so it waits on a telemetry
  section over proof and review records (tests per criterion as a histogram, coverage states per
  review, bindings decided by a test) and on consumer deliveries made after it ships. Verdict
  pending.
