# The passes

Read at step 3, before spawning any subagent. Four passes, independent, in any order or together,
plus the certification a staged proof claim owes. None reads another's output, and none decides
what runs next.

## Contents

- Coverage
- Conformance
- Standard
- Certification
- Failures
- How the passes divide

## Coverage

Spawn a `siegard:coverage-auditor` subagent, its judgment at
`${CLAUDE_PLUGIN_ROOT}/agents/coverage-auditor.md`. Pass:

- the criteria, as the task files state them;
- the test file set, out of the proof records;
- the target source root;
- the `coverageEntry` and `unpairedTest` slices printed at the contract step, each pasted whole.

It returns one entry per criterion, and `unpaired`: every test in the set that bears on no
criterion any task under this review states, each with what it asserts. That list is the coverage
reading answered in the other direction — a criterion with no test is a fact unproven, and a test
with no criterion is a proof of something no task stated. It is never a verdict on the test, since
a test may prove a sibling task's criterion, and never a recommendation to remove one.

## Conformance

One `siegard:specification-conformance-reviewer` subagent **per file the staging manifest holds**,
dispatched **by the waves the staging receipt lists**, each judging at
`${CLAUDE_PLUGIN_ROOT}/agents/specification-conformance-reviewer.md`.

- Spawn one wave whole, in one message, then save every return of that wave before the next wave
  is spawned. A wave ends when `--save-return` reports `0 pending` for it, read from the returns
  on disk, never a count of notifications you keep, because notifications arrive several in
  one turn, and some inside the turn that spawns the wave.
- The wave is the harness's ceiling on subagents running at once, cut by `--stage` into a list
  rather than estimated here. A launch the harness refuses is a wave cut too wide, reported with
  `--stage --concurrency <fewer>` ready to run again, and never a subagent dispatched a second time
  on its own.

Each subagent is passed, every path absolute and already resolved:

1. a file set of exactly its one file — the resolved path its pack header names, the spelling a
   finding echoes being the header's own;
2. as the node set, its node pack's path from the manifest — the pack is the set, whole, the
   trace's nodes and the plan's alike, each node's text with its source named;
3. as candidates, the path to the workspace's candidate index, which it may consult where its file
   states a fact its own nodes do not settle;
4. the specification root;
5. the path to `${CLAUDE_PLUGIN_ROOT}/schemas/conformance-return.json`, both where a finding's own
   shape lives and the contract the whole return is held to. One contract, handed once: this
   pass's findings reach a delivery node's `findings` only once you have stamped the pass onto
   each of them;
6. the form of the reply, in the agent's own words: the reply begins with the first key the shape
   lists that the answer carries, and ends with the mapping's last line; no ``` line anywhere.

The pack and the index go as paths, never as their text: one index serves the batch, and a prompt
carrying it inline pays for it once per file. It returns where the source states a domain fact the
specification does not hold, contradicts one it does, or became a second home for one — and, per
node, where the node's fact is held in that file, which is what a cleared binding's `how` is
written from.

One subagent per file rather than one over the set, because a judgment over the set saturates: a
single context holding every node and every file answers hundreds of node-file pairs in one reading
and claims clean over pairs it never weighed. No subagent reads another's return, and the pass is
the union of what they return.

- **Save each return verbatim the moment it arrives**, at
  `siegard-reconcile/<review-name>.returns/<the file's path with every '/' as '__'>.yaml` — a copy
  and nothing else, never reshaped, trimmed or repaired: the returns are the evidence the record is folded from, and they
  outlive this session.
- The fold admits the five keys `conformance-return.json` names and refuses a sixth; what a
  subagent says outside them belongs in your report, never in the file the fold reads.
- A subagent answers once. Where a return is unusable, the correction is a fresh subagent with the
  prompt fixed, never a follow-up to the one that already answered.

Where the staging found no trace file, this pass is instead one subagent over the whole file set
with the plan's node identities as its set, and nothing of step 3b runs.

## Standard

Where a standard is named, run:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --standard <the standard's path> --reading \
    --for <every path of the file set, one --for each>
```

Keep its output: the rules a tool decides are never this pass's to read, and neither is a rule
scoped away from every file under review. Spawn a `siegard:standard-conformance-reviewer`
subagent, its judgment at `${CLAUDE_PLUGIN_ROOT}/agents/standard-conformance-reviewer.md`, passing:

- that output, in place of the standard's path;
- the file set;
- the target source root;
- the `finding` slice printed at the contract step, pasted whole.

It returns the rules that were in scope and, for each departure, a finding citing exactly one of
them. Where no standard is named, the pass does not run, and the record says the project has
authored none.

## Certification

Where the staging holds entries under `certify`, one `siegard:coverage-auditor` subagent per node,
its judgment at `${CLAUDE_PLUGIN_ROOT}/agents/coverage-auditor.md`. Hand it the certification
pack's path from the manifest and the target source root, and nothing else: the pack names the
node, the proof and the contract its return is held to. Save each return verbatim at
`siegard-reconcile/<review-name>.returns/certify__<node with every '/' as '__'>.yaml`.

- Its rule is the whole test of a test: the named tests would fail if the node's fact stopped
  holding. It is the same rule the coverage pass applies to a criterion.
- Only its `covered` makes the binding one a test decides, and only where the conformance pass
  cleared the node as well. The fold writes both halves, and says in the record's notes why any
  certification did not land.
- Where the auditor answered short of `covered`, the fold carries onto the node's entry whether
  the remainder is one a test could assert, so that `trace.py --owed` lists it as the work a test
  closes. That work's route is the proof-only re-delivery of `/implement-task` over the task whose
  implementation record lists the file, handed the node, the assertion and the proof file. The
  report names that route and fills nothing in: which remainders are worth a test is not this
  pass's to decide.

This pass does not replace the coverage pass: coverage asks whether the tests prove the task's
criteria, certification whether one test proves one node's fact, and a criterion and a node are
two things.

## Failures

Spawn a `siegard:failure-diagnostician` subagent, its judgment at
`${CLAUDE_PLUGIN_ROOT}/agents/failure-diagnostician.md`, passing:

- the run's directory;
- the target source root;
- the specification nodes, with the specification root;
- the file set;
- the `finding` slice printed at the contract step, pasted whole.

It returns how many failures it counted, and one finding for each.

## How the passes divide

Whether the tests prove the criteria has one home, whether the source answers to the specification
has another, whether it follows the rules the project set for itself has a third, and why a run
failed has a fourth. One judgment per pass keeps two passes from disagreeing about one line, and
makes a clean result from any one of them mean something specific.

**The two conformance passes divide by authority.** The specification holds what the business
decided — what the system answers, which refusal, which code, who may see what — and a fact of
that kind written in source and in no node is the specification pass's finding. A standard holds
how the project is arranged — its layers, its wiring, its naming — and a rule of that kind is the
standard pass's. A standard rule stating what the system answers would put the two in
contradiction over one line, so the standard's contract excludes it, and a rule you find doing it
is a defect in the standard rather than a finding to record.

**The line all four passes stop at is not a subject line.** It is the line between a rule whose
application is a reading and a rule a tool decides. A model hunting an interpolated query competes
with a scanner built for it and loses; hunting a forbidden construct, it competes with the
compiler and loses. So this framework runs the consumer's own tools: a standard marks those rules
as a tool's, they become steps of the captured run, and what they print reaches the failures pass
carrying the tool's own message as its evidence. What is left — a responsibility spanning two
layers, an interface a caller cannot satisfy, a fact the specification does not hold — is what a
reading is for.

This framework never supplies the content of any of it: no rule, no threshold, no security
profile. A project that has authored neither a standard nor its tools gets an honestly narrow
review rather than a clean one. Say as much in the report, so a reader never mistakes four passes
for every pass.
