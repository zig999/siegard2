# The report

Read at step 9: the report lists every item below, in this order.

Report, in this order, in the file:

- the two nodes written, by identifier, and whether this was a re-delivery;
- every path the delivery created, modified or deleted — the records' `files` and `tests`
  together, which `--unrecorded` held to the tree — this is the file set `/review-change` needs,
  and the one thing it must never discover for itself;
- every criterion recorded unmet, with what the record says about it;
- every inference recorded, and every departure — these are the decisions nobody asked for, and
  they are what a reviewer reads first;
- every node the task implements that no test demonstrates, with what the proof's `untested`
  says of it — and, where it says nothing, that the proof leaves the node open;
- everything the proof left unproven, every edge case it dismissed, and every disagreement it
  recorded;
- what the implementation deferred, and what it says must keep working;
- every node bound into the target's trace, and any binding `trace.py` refused — the trace is
  what lets a future invocation ask whether this code and the specification have since moved
  apart, and a refused binding left unreported is a delivery that looks synced when it is not;
- where the bind printed a stale-bindings receipt, the receipt verbatim, and after it one
  `/reconcile` invocation ready to paste **for the case where no `/review-change` follows this
  delivery** — the review's conformance pass judges and restamps these same bindings over the
  files it reads, so the door is taken only where that review will not run — the project root and
  the target filled in, the file set being every path the receipt names, converted to the target
  source root's own anchor (the receipt spells paths from the git toplevel, and `/reconcile` reads
  them relative to the target source root), and a slug slot left for the human to name, since
  `/reconcile` requires one and refuses a slug already taken — with the one sentence that makes
  the door real rather than decorative: it runs only after the human commits this delivery's
  pending state, because `/reconcile` refuses a named file the tree holds uncommitted. Never a
  stop, and never per file: one invocation, one file set, and taking it is the human's;
- which steps, if any, ran inline instead of in a subagent, and why;
- where this invocation stopped and hands more than one door, the door a fact on disk decides, with its criterion and both facts — «A recommendation names the
  door, the criterion, the deciding fact and the reversing fact» (SPEC-006 R2). A door whose entry point would refuse its inputs as the tree stands — a
  proof increment over a node no record under `siegard-reconcile/` carries with `remainder:
  testable`, a task `deliver.py --outstanding` does not list as deliverable — is `precondition
  unmet`, and the door left is the one recommended; a door whose work the producer's own return
  says the delivered tree already holds is `already done`. The name classifies the reason for
  the log; what the person reads is the reason in plain words, with the fact quoted and what
  would change it. A stop over a BLOCKING note, a contradiction, or a suite whose diagnosis
  two producers read apart is «the person's own decision» (SPEC-006 R3): the report says so,
  what each door assumes is true, and what would settle it, and names no door;
- the validator's final output, verbatim;
- the standard this invocation followed — where it resolved from, the invocation or the project
  file by path — by its own path and the pin taken of it, every departure
  disclosed against it by either record, and what it presupposes — that the tree holds it, or, for a
  task that produced it, that this delivery is what made it hold. Where none was named, say that
  the only project convention followed is what the inventory evidenced, which is the honestly narrow
  answer rather than a clean one — and where `--outstanding` named a standard this root's earlier
  records pin, say that too: an invocation naming none over a root that remembers one is writing
  source the review will still read against those rules. Say too every line the report prints of
  records that pin no standard, or another than the one `siegard.json` declares for their target,
  or an earlier version of it — a statement and never a stop: an invocation may name another
  registry on purpose — «A delivery record that pins no standard, or a standard other than the one
  its target declares, is reported beside the outstanding tasks and refused nowhere.» (SPEC-007 R1),
  and «a step declared after a record was written is owed by the records written after it»
  (SPEC-007 R3);
- every run this invocation captured, by path and by outcome, including the ones that failed —
  those are not noise and they are not a draft: they are the only record of what it took, and a
  report naming only the run that passed describes a delivery that went right the first time
  whether or not it did — with, for each red suite that was diagnosed, the `cause` the diagnosis
  returned — and every step of the registry that did not run, with why. Where this
  delivery built the substrate, that is most of them, and saying which rules they own is what keeps
  a substrate record from reading as a project that builds;
- every dependency this delivery installed, and that what those pulled in transitively is nobody's
  approval — the lockfile is what says what actually arrived, and it is in the diff;
- what `/review-change` still does that this invocation did not: it runs the same steps again over
  the whole change rather than one task's, and it judges — whether the tests prove the criteria,
  whether the source states only what the specification holds, whether it follows the same standard, and
  why anything failed. A green suite here is a green suite over one task, and two tasks that each
  passed alone are not a change that passes together;
- the handoff: the `/review-change` invocation ready to paste — the project root, the target and
  the initiative's slug filled in, since every root they resolve to was just validated above; the
  tasks under review being the one task this invocation delivered, by identifier; the file
  set being exactly the paths named above, because a review never discovers its own scope and
  this report is the only place that set exists; and the project's standard as it resolved,
  which is also where the review reads its commands from — a slot only where neither the
  invocation nor the project file answered it. The handoff offers the next step and
  never takes it: filling any empty slot and invoking are the human's — given per invocation, or
  given once for a whole route through the orchestrating entry point, `/deliver-scope`, whose
  own file bounds what it may fill.
