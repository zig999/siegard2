# The report

Read at step 9: the report holds every item below, in this order.

- the two records written, by identifier, and whether this was a re-delivery;
- every path the delivery created, modified or deleted — the records' `files` and `tests`
  together, which `--unrecorded` held to the tree. This is the file set `/review-change` needs and
  must never discover for itself;
- every criterion recorded unmet, with what the record says about it;
- every inference and every departure recorded — the decisions nobody asked for, which a reviewer
  reads first;
- every node the task implements that no test demonstrates, with what the proof's `untested` says
  of it — or, where it says nothing, that the proof leaves the node open;
- everything the proof left unproven, every edge case it dismissed, and every disagreement it
  recorded;
- what the implementation deferred, and what it says must keep working;
- every node bound into the target's trace, and any binding `trace.py` refused — a refused binding
  left unreported makes the delivery look linked when it is not;
- where the bind printed a stale-bindings receipt: the receipt verbatim, then one `/reconcile`
  invocation ready to paste **for the case where no `/review-change` follows this delivery**,
  since the review's conformance pass restamps the same bindings. Fill the project root and the
  target; the file set is every path the receipt names, converted from the git toplevel the
  receipt spells to the target source root `/reconcile` reads; leave the slug as a slot for the
  person to name, since `/reconcile` requires one and refuses one already taken. Say that it runs
  only after the person commits this delivery, because `/reconcile` refuses a named file the tree
  holds uncommitted. One invocation over one file set, never one per file and never a stop; taking
  it is the person's;
- which steps, if any, ran inline instead of in a subagent, and why;
- where you stopped and hand more than one door, the recommended one with its criterion and both
  facts — «A recommendation names the door, the criterion, the deciding fact and the reversing
  fact» (SPEC-006 R2). A door whose entry point would refuse its inputs as the tree stands — a
  proof increment over a node no record under `siegard-reconcile/` carries with `remainder:
  testable`, a task `deliver.py --outstanding` does not list as deliverable — is `precondition
  unmet`, and the door left is the one recommended. A door whose work the producer's own return
  says the tree already holds is `already done`. Those names classify the reason for the log; the
  person reads the reason in plain words, with the fact quoted and what would change it. A stop
  over a BLOCKING note, a contradiction, or a suite red the two producers read apart is «the
  person's own decision» (SPEC-006 R3): the report says so, says what each door assumes is true
  and what would settle it, and names no door;
- the validator's final output, verbatim;
- the standard you followed: where it resolved from — the invocation, or the project file by path
  — its path and pin, every departure either record disclosed against it, and what it
  presupposes: that the tree holds it or, for a task that produced it, that this delivery made it
  hold. Where none was named, say that the only convention followed is what the inventory
  evidenced — a narrow answer, not a clean one — and, where `--outstanding` names a standard this
  root's earlier records pin, say that the review will still read this source against those
  rules. Also state, never as a stop, every line `--outstanding` prints of records that pin no
  standard, another than the one `siegard.json` declares for their target, or an earlier version
  of it — «A delivery record that pins no standard, or a standard other than the one its target
  declares, is reported beside the outstanding tasks and refused nowhere.» (SPEC-007 R1), and «a
  step declared after a record was written is owed by the records written after it» (SPEC-007 R3);
- every run you captured, by path and outcome, including the ones that failed — they are the only
  record of what it took — with, for each diagnosed red suite, the `cause` the diagnosis returned;
  and every step of the registry that did not run, with why. Where this delivery built the
  substrate, that is most of them;
- every dependency this delivery installed, and that what those pulled in transitively is nobody's
  approval: the lockfile, in the diff, says what arrived;
- what `/review-change` still does that you did not: it runs the same steps over the whole change
  rather than one task, and it judges whether the tests prove the criteria, whether the source
  states only what the specification holds, whether it follows the standard, and why anything
  failed. A green suite here covers one task;
- the handoff: the `/review-change` invocation ready to paste, with the project root, the target and
  the initiative's slug filled in; the tasks under review being the one task you delivered, by
  identifier; the file set being exactly the paths named above, since this report is the only
  place that set exists; and the project's standard as it resolved, where the review also reads
  its commands — a slot only where neither the invocation nor the project file answered it. The
  handoff offers the next step and never takes it: filling a slot and invoking are the person's,
  per invocation or once for a whole route through `/deliver-scope`, whose own file bounds what it
  may fill.
