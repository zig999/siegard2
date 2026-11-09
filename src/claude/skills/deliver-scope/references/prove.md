# Close what the review left testable

Read at step 5, where the review refused a certification with `remainder: testable`.

A certification the review refused over a node one of this run's own tasks implements, with
`remainder: testable`, is the handoff that review's report names: the proof-only re-delivery of
`/implement-task` over that task, handed the node, the assertion and the proof file, all read from
the review's record. Taking it is inside the ask: «A finite test is preferred to a reading, and to a
registry step's decision, wherever one exists» (SPEC-004 R10).

1. Fill those slots from the record, one re-delivery per task, and commit each as
   `deliver-scope <slug>: prove <task>`, one after the other: each is its own `/implement-task`
   invocation, run to its end and committed before the next begins — never test-authors spawned side
   by side over one tree, and never one suite run standing for several tasks.
2. A suite is one run over the whole tree, so a red re-delivery beside green ones holds them all,
   and the clean-tree stop each invocation opens with keeps them apart. A re-delivery that stops red
   leaves its files for the person, every one already committed stands, and those not yet begun are
   relayed as not reached.
3. Then invoke `/review-change` once more over exactly those tasks, named by step 4's rule; it
   commits itself.

This step runs once per run: a certification refused again is relayed with its new remainder, and a
third attempt is the person's decision about cost. A remainder over a node no task of this run
implements is not this run's; the report hands it on as `trace.py --owed` does.
