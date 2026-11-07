# The report

Read at step 6, after `handoff.py --prepare` has printed its skeleton.

Write it through `handoff.py --save-report` and hand the person what `handoff.py --render`
prints, as step 6 states.

## Contents

- What the report says, in order
- Collateral
- A whole reconciliation, and a partial one
- The next file set
- The doors for a node the judgment did not clear

## What the report says, in order

Say, in this order and in prose, in the file:

1. The file set as given.
2. What the staging held for each file, by state — judged, nothing left to judge, unbound — and how
   many pairs it omitted as current and unowed.
3. The shape the judgment ran in: how many subagents, one per file, and whether the pass ran
   inline.
4. What the judgment answered per node, with its evidence.
5. Which pairs a run answered instead of a judge, with the step and the run's own outcome per step.
6. Which pairs the declared rewrite carried, how many over how many files, with the transcription
   verbatim beside the person's own words for it, and which drifted pairs it did not carry, with
   the reason the staging gave for each. A carried pair was read by no judge, and the report says
   so plainly.
7. Where the record, the returns and the run were written.
8. What was bound and what was not, from the bind's receipt.
9. Which nodes are decided by a test from here, and which certifications did not hold, in the
   auditor's own words. For each of those, whether the remainder is testable, with the assertion
   the auditor named beside it and the file's own count of bindings a reading decides: a node a
   test closes frees a judge only once every binding on its file is decided by a step or a test.
10. The route that closes the testable remainders, as one invocation: a proof increment,
    `/deliver-scope` with an ask naming the proof increment and, per testable remainder, the node,
    the assertion verbatim, this record's path and the files the node is bound to, all read from
    the record you just folded, under a new slug. `/plan-work` plans one task per fact,
    `/implement-task` writes the proof alone, and the review that reads it certifies the node.
    «A finite test is preferred to a reading, and to a registry step's decision, wherever one
    exists» (SPEC-004 R10), so every testable remainder is handed on, never only the ones that
    look cheap. Which to take is the person's: they paste the invocation whole, or trimmed to the
    facts they want.
11. The next invocation, where there is one.

## Collateral

Where a node the judgment did not clear carries `collateral`, say so apart from the contested
ones. Nothing was found against that node's own substance: it shares a file with a finding that
named no node, and the conservative default holds every node of that file. Its route rides the
finding's own: route the finding, and the re-invocation that follows re-judges the file and
re-clears the node with it. A reader who cannot tell collateral from contested reads four open
questions where there is one.

## A whole reconciliation, and a partial one

Where the judgment cleared everything, there is no next invocation. The trace now describes the
tree as it stands, and `trace.py --check` over the target is what a reader confirms that with.

Where it cleared part of the set, say both halves and keep them apart: the nodes now bound, and the
nodes still owed exactly as the bind's receipt names them. Naming only the first leaves a reader
believing a partial reconciliation was a whole one.

- `trace.py --check` over the target reports the drift that remains: two findings where the report
  opened with forty is progress, not a clean tree.
- `trace.py --owed` over the same target reports what this judgment found and no bind could close,
  the half `--check` cannot see: a node bound to no file here has no digest to drift, so its
  finding lives in the record alone.

## The next file set

**Then say what the next invocation's file set is, and make it the remainder**: the files whose
nodes are still owed, never the whole set again. The cleared nodes are bound and their files
committed, so re-judging them pays one subagent per file for text that did not move.

Two things go in with the remainder, both read from `--check` rather than from your memory of this
run:

- any file the run about to follow leaves reporting `moved`, because an `/analyse` that shifts a
  node re-opens every file bound to it, including one that cleared here;
- any file whose nodes the remainder shares: the binding form refuses a record that names a file
  and answers for only some of the nodes bound to it.

Name them; the file set is still the person's to state. A bound file `--check` reports as no longer
existing goes in no file set — there is nothing to read — and `trace.py --release
<target-source-root> <path>` is what answers it; the report names that invocation beside the
remainder.

## The doors for a node the judgment did not clear

Where the judgment did not clear a node, there are two readings, and **settling them is the
person's own decision.** The source may be right and the specification behind it, or the node may
be right and the source wrong; a reviewer that settles it is a decision wearing a finding's
clothes. Hand both, and say which finding each one answers, what each door assumes is true, and
what would settle it: two readings of one piece of evidence are «the person's own decision»
(SPEC-006 R3).

The first, where the fact the source now states belongs in the specification — the `/analyse`
invocation ready to paste, naming the material (the finding's evidence, the file it was read in,
and the nodes located above) and the project root. After it runs, this skill is invoked again over
the remainder under a new slug: the node has moved, the judgment reads it as it now stands, and the
bind stamps both sides.

The second, where the node is right and the behavior is not — the `/plan-work` invocation ready to
paste for a corrective increment, in the form `/plan-work`'s `argument-hint` states, naming the
scope (the one wrong behavior, as the finding states it), the project root, the target, and the
initiative's slug. That route ends in a delivery, which binds on its own and leaves this
reconciliation with nothing to do.

The third, where the node and the behavior agree and what the finding names is the file's own
prose — a comment breaking the consumer rules' comment rule.

- Neither door above fits it: there is no fact to decide into the specification and no behavior
  to correct, and routing it through either prices a line of prose like a defect.
- The consumer rules' comment route is the answer: the person removes the prose, never refreshes
  it, and this skill invoked again over that file under a new slug re-judges and rebinds.
- The prose removed is every comment the file carries, directives the toolchain reads excepted,
  never only the ones cited: a judge names what it read, not every comment, so a file stripped of
  the cited ones hands the next judge the rest.
- Hand that invocation ready to paste, and say which findings it answers.
- Over these findings the comment route is recommended, naming the door, the criterion, the
  deciding fact and the reversing fact: «A recommendation names the door, the criterion, the
  deciding fact and the reversing fact» (SPEC-006 R2). The criterion is `rule violated`, since
  either door above would route prose as a fact or a behavior; the deciding fact is the judge's
  return naming prose and no contradicted node, quoted; the reversing fact is a return naming a
  fact or a behavior, which puts the finding back between the two readings above. The person
  reads the reason in plain words; the criterion's name is for the orchestration log.

The fourth, where the fold placed a finding in the record's `notes` because it names a node no
file of this set is bound to — the note ends "owed a route of its own".

- It blocked nothing here, and `trace.py --owed` reads a record's nodes and its `unstated`, never
  its notes, so this report is the one place the finding is handed on.
- Name it apart, with the node, the file and the evidence, and hand it the same two doors as a
  finding on a node: `/analyse` where the fact belongs in the specification, `/plan-work` where the
  node is right and the behavior is not.
- Or, where the finding says the file holds the node's fact and nothing binds it, this skill
  invoked again over that file under a new slug, which hands a judge that node's text. Where the
  note says so, that door is recommended as R2 states: the criterion is `already done`, since the
  fact is already in the file and only the binding is owed; the deciding fact is the note, quoted;
  the reversing fact is a note saying the file contradicts the node, which leaves the two readings
  as the person's own decision. Said in plain words, as above.

A finding left in the notes and not in the report is a finding nobody will act on.
