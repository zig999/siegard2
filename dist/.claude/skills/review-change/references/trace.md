# The trace check

Read at step 1, when `trace.py --check <target-source-root>` has printed.

**This is neither a stop nor a finding.** Drift is not a rule of the standard and not a statement
about whether the change conforms to anything: a file edited since its bind may be perfectly right.
It is one fact no pass here produces — whether the link this framework keeps after a plan is
deleted still describes the code as it stands. Report the counts by class, and the route each class
takes:

| Class | What it is | Route |
|---|---|---|
| `orphaned` | a binding to a specification node that no longer exists; no rebind repairs it, because a bind refuses a node the specification does not hold | `trace.py --prune` |
| `moved` | a binding to a node whose text moved since the bind, or a file of it last read against an earlier text | `/reconcile` over the bound files re-reads them against the node as it stands; a delivery of a task implementing the node restamps only the files its record names, and the node's other files stay `moved` until a reading reaches them |
| `proof` | a binding a certified test decides whose test's text changed since | a reconciliation that certifies the test as it now stands; the node is decided by reading until then |
| `code` | a file changed without a rebind, whatever wrote it | over this review's files, the conformance pass; over files outside it, `/reconcile`, never a deletion |
| `code`, file gone | a bound file the tree no longer holds | `trace.py --release` |

Over the files of this review, the conformance pass answers `code`: the delivery's bind restamped
only its own task's nodes, and every other node bound to a file it rewrote still asserts the digest
that was there before. That is why the pass reads the trace's node set and not the plan's alone.

The trace is read here because this is the last place a delivered tree is read whole with a report
attached; a review silent about drift lets a tree accumulate a trace nobody can trust while every
command still exits 0.

## The suppression receipt

**Where the output carries a suppression receipt, one line of the report is owed to it, and it is
not a finding either.** A project may declare a target whose source a person changes without a
task; the `code` class is then counted rather than listed, because on such a target it names every
label and every colour anybody moved. Two things follow, and both go in the report rather than in
your hands:

1. Those files were changed by nobody this framework can name, so **the rules that a reading
   decides went unread over them** — nothing here scheduled that reading, and the project's own
   suite only ever answered the rules a tool decides.
2. The file set of this review is the person's to widen. Where the receipt's count is worth acting
   on, `trace.py --check --all` lists the paths, and **offer them**: as paths the person may add to
   the file set of this review, so the standard pass reaches them, or as the argument for a
   `/check-source` invocation over the same list.

Offer, never widen: a review that pulled files in on its own would be choosing its own scope.
