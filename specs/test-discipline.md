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
mechanically. It also decides where a proof is cut (R18–R21, R23), when an implementation that stands still stands (R26), who answers a red build or a
red suite (R24, R25), and what a review answers for (R22).

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

- **R14** — Coverage is stated per obligation, never as a figure: the state of each criterion a
  review answers for, and of each node fact a certification reads, is named, and no percentage,
  line or branch measure stands in for it. An `UNDERDETERMINED` note is owed evidence by the test
  author and holds no coverage state of its own.
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

- **R18** — A task writes source, or its implementation already stands. A task planned to write no source carries `stands`, and before the task is written the trace binds each node the task implements to a file it names, and each file it names to a node the task implements. A task whose delivery finds its implementation already standing carries `stands` in its implementation record instead, held to the same bindings before the record is written (R20). A fact the plan's own deliveries will write into source is proven by the task that writes it, as that task's criterion, never by a task of its own.
- **R19** — A node whose fact already stands in source the trace does not bind to it gets no proof task. The plan reports the reconciliation that would bind it, over the files that hold it, and the proof waits for that binding.

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

- **R20** — A delivery whose implementer finds every criterion of the task already met by source the tree holds writes no source: its implementation record carries `stands` over the files that hold the fact, and its proof follows as for any task. Where the trace does not hold the bindings R26 reads between those files and the task's nodes, the record writer refuses the record and names the reconciliation that would write them — an adoption over those files whose candidates are the task's nodes bound to none of them, or an ordinary one where every node is bound and a binding moved — and that reconciliation is the delivery's one door: an orchestrating run takes it, once per task, and delivers the task again. A node the adoption leaves bound to none of the files is a stop, and the person's: the implementer and the reconciliation's judges read the same files two ways.

  Grounds: on 2026-10-30, reading every `orchestration.md` under the delivery roots of the sales consumers
  for a line naming a task whose implementer found the criteria met and wrote no file, 20 tasks in 5
  plans of two consumers stopped with `files` empty and no `stands` (13 of them in one plan); the estimator is that
  line match, so a stop logged in other words is not counted. The record writer refuses such a
  return, and nothing stated what the delivery then hands: each orchestration chose its own door,
  withdrawing the task from the plan in some and planning it again with `stands` in others.

  Grounds for the record carrying `stands` and the reconciliation being an adoption, read on
  2026-11-09 from the orchestration logs and transcripts of five sales consumers between
  2026-11-07 and 2026-11-09 (Siegard 5.47.1 to 5.79.1): about ten tasks in four plans stopped on
  this requirement's earlier form, which wrote no record and handed the person the plan over the
  slug carrying `stands`, or the reconciliation. Every one was taken by the person after the stop,
  and none reached a record without a loss: one delivery added a field to the logger's redaction
  list so the writer would admit a record (productorder `762ba5d`), one plan withdrew its last task
  (configurator `1dab02b`), and one run deleted six records and the review naming them (partymgmt
  `968d87c`). Where the trace bound a node to none of the files, the reconciliation handed was an
  ordinary one, which judges a file against the nodes the trace already binds to it: in partymgmt
  it read the two unbound nodes as candidates only and bound neither, so that door could not have
  closed. An adoption reads every candidate it is handed on every file and binds each where the
  judgment holds its fact (SPEC-005 R3, R4).

- **R21** — A re-delivery of a task whose own earlier implementation record names every file that holds the fact writes no `stands`: the record is written again over those files, answering the task as it stands. A re-delivery names a file the tree did not change only where the record it replaces named it. A re-delivery that writes no source and finds the fact held in a file the earlier record does not name is R20's: its record replaces the earlier one carrying `stands`.

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

### Who answers a red build

- **R24** — A build red whose fix lies only in files the project declares as its tests is answered by the delivery's test author, before the implementation record is written: the implementer writes no test, and the record cites the build that passed once the test author answered. A test the proof of another task names is answered here only where this delivery's files include one that task's implementation record names; otherwise the red is a stop.

  Grounds: the build runs every step of the registry but the suite, the record is written only
  over a build that passed, and the test author was handed that record — so a red only a test
  could answer had no producer. On 2026-10-31, reading the build runs under the delivery roots
  of the consumer trees on one workstation (each `-build` run's `run.json` and the log of its
  failed step, for a test named missing or failing to compile), 68 were red and 2 were that red.
  One consumer's layout check requires a contract test for every routes file; its first task
  writing one stopped at the build as `outside-task`, handing `/plan-work`, which no re-plan
  answers, since every task writing a routes file meets the same build. Another consumer's
  typecheck reached an earlier task's test whose call the delivery's source legitimately
  changed; the session handed the test author a red build and no record, outside any stated
  route. A red worded otherwise in its log is not counted.

- **R25** — A suite red on a test the proof of an earlier task names is answered by this delivery only where its files include one that task's implementation record names: the test author rewrites the test whole and it joins this delivery's proof. Otherwise the test is not edited here: the answer is a proof-only re-delivery of the owning task, which only a person names, which rewrites the proof and never the implementation record, and which runs only while every binding of a node that task implements to a file its implementation record names is current. A binding of another node to one of those files does not close it: the review that follows reads that binding, as it does for a task carrying `stands` (R26).

  Grounds: stated in `/implement-task` since the proof-only re-delivery shipped (9a2a3df) and in
  no specification until the audit of 2026-11-01 found the route with no requirement to hold it;
  it is the suite-time counterpart of R24's second sentence, and no measurement reopens it.

  The last sentence read any drift on the owning task's files as closing the route, whichever
  node it named, until R26 decided the same question for `stands`. On 2026-11-04, reading the
  trace at the commits of the two orchestration logs that recorded the route closed by drift (a
  file digest or a node digest out of date against each binding), the route was closed over four
  tasks: three had a binding of their own nodes out of date on a named file, and one —
  carrying a testable remainder — only other nodes' bindings, so the same question gets the
  same answer on both routes.

- **R26** — A task carrying `stands`, in its plan or in its implementation record, is delivered only while the trace holds the bindings R18 requires and every binding of a node the task implements to a file `stands` names is current: a node the task implements bound to no `stands` file, a `stands` file bound to no node the task implements, a file changed since the binding was written, or a node whose text moved since the file was read against it makes the implementation not stand, and the record writer refuses the record. A node the task implements and a `stands` file the trace does not bind to each other are never that refusal while the node is bound to another `stands` file and the file to another node the task implements: the files hold the implementation together, and no file need hold all of it. A binding of a node the task does not implement to one of those files is never that refusal: the review that follows reads each `stands` file against every node the trace binds to it.

  Grounds: `/implement-task` held every `stands` file to `trace.py --check --all` and read any
  finding on it as "stands" false, whichever node the finding named — a reading inherited from
  the proof-only re-delivery, whose files are the task's own (R25), and decided nowhere for
  `stands`. On 2026-11-04, reading the trace at the commit that wrote each `stands` in the four
  consumer trees that carry one (sha256 of each named file at that commit against each binding's
  digest; file digests only, so a moved node is not counted), 23 tasks carried `stands` since R18
  shipped: none had a binding of its own nodes out of date, and 8 had another node's binding to
  a `stands` file out of date. Of those, one plan stopped — and resumed only after the person had
  the file released from three other nodes' bindings, dropping 11 more drifted files from them —
  and four deliveries proceeded, one disclosing it in its notes. Since 3.37.0 the review's
  conformance pass reads every file it reviews against every node the trace binds to it and
  restamps what that judgment clears, and a review of a `stands` task lists the `stands` files.

  The bindings R18 requires were read two ways until 2026-11-08: R20's door, `/plan-work`'s
  `--encodes` check and validation item 13 asked that every node be bound to some `stands` file,
  while R18 and the record writer asked that every file be bound to every node. One consumer
  plan's last task, its seven nodes held across four files that bound one to three of them each,
  was handed the plan's door, given `stands`, refused by the writer, reverted and withdrawn from
  the plan. Reading every task carrying `stands` in the four consumer trees that carry one
  against today's trace, 57 tasks: 38 bind every file to every node, 12 bind every node and every
  file to some node of the task, 2 name a file bound to no node of the task, 2 cover neither way
  and 3 name files the tree no longer holds. The 12 and the 2 were all written before the writer
  held the bindings (5.53.0), so the writer's form never refused a `stands` the other form admits
  but the one above; their reviews were not read for this measurement. The two forms that name a file bound to no node the task implements were so at the
  commit that wrote each record, and are refused by this requirement: such a file is not where
  the implementation stands.

- **R27** — A record writer reads the producer's return as one YAML mapping. Where it does not parse, each line whose key the record's contract types as a string, and whose single-line value does not stand alone as a string, has that value quoted whole, and the return is read again; the writer names each line it quoted and repairs nothing else. A return that still does not parse, that opens with a code fence, or that carries text before or after its mapping is refused, and the producer answers again.

  Grounds: on 2026-11-09, every mapping reply of `task-implementer` and `test-author` in the five
  `sales*` consumers' subagent transcripts (2026-10-10..11-09), read by the writer's own loader:
  of first replies, 6.1% did not parse in October (127 of 2,069) and 6.5% in November (48 of
  734), with the agents' instruction to quote such a value in place since 3.48.2. The failing line
  was a text field holding `: ` — `how` 73 times, `proves` 30, `effect` 21 — mostly code quoted in
  a sentence. Quoting those values whole read 151 of the 198 failing replies and changed none of
  the 3,180 that parse; where the producer answered again, its next reply was identical to the
  quoted one in 21 of 71 and at least 95% the same text in 41 more. Each answer again cost the
  subagent a median of $0.07 and 43 seconds (90th percentile 522 s), and opens a branch where one
  consumer committed a delivery with the previous proof. The 47 left are text before or after
  the mapping, a fence, or list items — two answers or prose, which no reading decides.

### What a review answers for

- **R22** — A review answers for its tasks as they stood when it was written. A task is reviewed as it stands where a review naming it lists every file the task's records name that its target source root holds and, where its coverage pass ran, answers every criterion the task states; a task some review names and none answers as it stands is owed a review, and a review written before the task or its records changed is never refused for it. A delivered task no review names is reported as never reviewed beside the outstanding tasks, and refused nowhere. The review being written is held to its tasks as they stand, and refused where it falls short. A path the records name that the target source root no longer holds — a file the delivery deleted — or that lies outside that root has no bytes a review reads: no review is held to list it, and the review's report names it as not read.

  Grounds: a review carries no pin, and every review was held, for as long as its plan was live,
  to the records and criteria of today. On 2026-10-29 one consumer's proof-only re-delivery wrote a
  helper after the first review of its task; the second review listed it, and the first was
  refused from then on — `deliver.py --check` failed, `/review-change` refuses to run over a
  delivery that fails it, and `--outstanding` refused to derive. On 2026-10-20 another consumer's
  re-plan reworded the criteria of reviewed tasks; its one review drew 17 refusals no later
  review could clear, and the person closed the plan to carry the work into a new initiative.
  Across seven consumers on 2026-10-30, these were the only two plans whose reviews drew either
  refusal.
  On 2026-11-02 a third consumer's goal ended in state B on the review alone: one task deleted
  seven files, as R16 requires its record to name, and another changed the repository's own
  `CLAUDE.md`, outside the target; `--stage` reads neither, `/review-change` handed 113 of the 121
  paths, and `--review` refused the record for the 8 it could not read. A deleted path holds
  nothing a judge opens and a path outside the target answers to no standard of it, so the
  review is held to what the root holds and says what it did not read.

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
   before it writes it — every node the task implements listed for some file, and every file
   listing some node the task implements — and states both requirements in the words above; the backlog decomposer
   states R18's last sentence; `tests/test_spec_citations.py` proves each quote is a substring of
   the requirement it names.
7. For R20: the task implementer returns that case as a mapping carrying `stands`;
   `bin/deliver.py --check` admits an implementation record carrying `stands` over a task that
   carries none, and still refuses one whose task carries other files;
   `--write-implementation` refuses such a record where a node is bound to none of its files and
   prints the adoption that would bind it, its candidates those nodes, or the ordinary
   reconciliation where only a binding moved; `/implement-task` hands that line as its one door,
   and `/deliver-scope` takes it once per task — `tests/test_deliver.py`,
   `tests/test_skill_contract.py` and `tests/test_deliver_scope.py` prove each.
8. For R21: `bin/deliver.py --unrecorded` refuses a re-delivered implementation naming a file the
   tree did not change that the record it replaces did not name, and admits one the record it
   replaces named; `--write-implementation --replace` writes a re-delivered record carrying
   `stands` over files the earlier record did not name; `/implement-task` hands the implementer the
   record a re-delivery replaces — `tests/test_unrecorded.py`, `tests/test_deliver.py` and
   `tests/test_skill_contract.py` prove each.
9. For R22: `bin/deliver.py --check` admits a review that lists fewer files than its tasks'
   records now name, or answers criteria its tasks no longer state, and refuses it under `--review`
   naming it; `--outstanding` names a task some review names and none answers as it stands, and
   no task one review answers; and neither holds a review to list a path the records name that
   the target source root no longer holds or that lies outside it — `tests/test_deliver.py`
   proves each.
10. For R23: `bin/deliver.py --outstanding` names a task delivered as the substrate alone apart
    from a task implemented and unproven, and counts it delivered; `/implement-task` writes no
    proof only for a task that report names so — `tests/test_deliver.py` and
    `tests/test_skill_contract.py` prove each.
11. For R24: `bin/project.py --declared-tests` says which paths a red's fix names are tests the
    target declares; `/implement-task` hands the red to the test author only where every path is
    one, with the implementer's return in the record's place, and the test author takes that
    return; a declared test another task's proof names is answered only where this delivery's
    files include one that task's record names, and is otherwise the stop —
    `tests/test_project.py` and `tests/test_skill_contract.py` prove each.
12. For R25: `/implement-task`'s suite step reads which shape a red on an earlier task's test
    took from the two implementation records, rewrites the test where a file is shared, and
    otherwise hands the proof-only re-delivery, which only a person names and which runs
    `trace.py --check --all` before anything is written and reads the findings naming a node the
    owning task implements — `tests/test_skill_contract.py` proves
    each.
13. For R26: `bin/deliver.py --write-implementation` refuses a record carrying `stands` where a
    node the task implements has no binding to a `stands` file, where a `stands` file has no
    binding to a node the task implements, or where a binding between them has a file changed or
    a node moved since it was written; it writes the record where the files hold the nodes between
    them and no file binds every node, and where only a node the task does not implement has a
    binding out of date on one; `/implement-task` states the requirement in the words above
    — `tests/test_deliver.py` and `tests/test_spec_citations.py` prove each.
14. Over the next consumer deliveries the measurement in the scope above is repeated: tests per
    criterion, covered share per review, and the count of nodes decided by a test. A covered share
    that falls below the two-tests-per-criterion figure recorded there is what reopens R5 to R8.

## Readings

- 2026-10-07 — not yet read: the measurement has no measurer in the distribution — the grounding
  figures were produced by throwaway scripts outside this repository — so it waits on a telemetry
  section over proof and review records (tests per criterion as a histogram, coverage states per
  review, bindings decided by a test) and on consumer deliveries made after it ships. Verdict
  pending.
- 2026-11-01 — the measurer ships: telemetry's `proofs` (`siegard-telemetry/19`) counts, over the
  reviews whose last commit falls in its window, the criteria by state and by how many tests each
  names, names the review naming the most, and counts the bindings a test decides. The reading
  above now waits only on consumer deliveries made after it ships.
- 2026-10-31 — the delegation returns of a delivery and of its plan, read for characters no
  consumer reads, by the method SPEC-005 R12 was cut by; nothing was cut. Returns: the last
  assistant text of every subagent transcript under the five `sales*` consumers' Claude Code
  project directories (2026-10-10..31): `execution-contract-binder` 3,193 runs, 16.3M characters;
  `test-author` 1,072 runs, 13.1M; `task-implementer` 1,050 runs, 11.6M. Shares are of each
  parsed return's top-level fields, each serialized alone by one `yaml.safe_dump`, summed.
  Binder: `notes` 93.8% (`note` 66.6%, `passes` 14.5%, `belongs` 6.0%, `fact` 2.5%), `implements`
  6.2%; by class, underdetermined 39.3%, remainder 21.1%, advisory 20.8%, unstated 7.9%,
  blocking 2.8%, compound 0.9%. Test author: `tests` 56.6% (`proves` 21.0%, `fails_when` 15.5%,
  `name` 11.6%), `untested` 24.6%, `not_applicable` 10.8%. Implementer: `criteria` 32.5% (`how`
  18.5%), `nodes` 21.6% (`how` 13.8%), `inferences` 15.9%, `files` 14.6% (`effect` 12.0%),
  `deferred` 7.0%, `preserved` 4.8%. Readers, from code: `deliver.py --write-implementation` and
  `--write-proof` write the return whole as the record's frontmatter (`front.update(returned)`),
  dropping only empty lists — so the records under four consumers' delivery roots (725
  implementation records, 7.65M characters; 719 proofs, 8.57M) carry the same shares to within a
  point; `plan-work` transcribes `implements` into the task and every note but `compound` into its
  `## Notes` under its class's opening, with `passes` and `belongs` beside it (772 task files hold
  3.15M characters of notes: UNDERDETERMINED 44.0%, ADVISORY 22.1%, REMAINDER 20.4%), hands
  `compound`'s `criterion` and `conditions` to the decomposer and `unstated`'s `fact` to the
  decider. Scripts read, of the records: `criteria[].criterion` and `met`, `nodes[].node` and
  `encoded_at`, `files[].path`, `tests[].file` and `demonstrates`, `divergences`' `cites`,
  `file` and `from`, `installed`, `stands`, `title`, `summary`; of the task notes, the BLOCKING and
  UNDERDETERMINED openings. What no script reads — the `how`s, `effect`s, `inferences`,
  `deferred`, `preserved`, `proves`, `fails_when`, `not_applicable`, `untested`, `contested`, the
  REMAINDER and ADVISORY notes — sits in a persisted record a later step is handed whole: the test
  author reads the implementation record (R4 names its inferences), the task implementer and
  test author read the task file's `## Notes`, `/review-change` situates on the records'
  inferences, departures, `untested` and `contested`, `/implement-task`'s report lists each, and
  `git diff` over every one is the person's review. R12's cut was of entries quoted into no
  record; by that criterion the share here is 0%, and a cut would be a cut from the records. What
  reopens this: a field a record carries that no step is handed and no person reads in a review.
  The measured lever is elsewhere: over the four consumers whose work roots were read, the binder
  ran 1,856 times for 772 task files on disk, a ratio this reading did not break down by cause.
