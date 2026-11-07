# Validating and binding

Read at step 7 before the first validation, and at step 8 when the bind prints anything.

## Naming every changed path

«Every path a delivery created, modified or deleted under its target source root is named by one
of the delivery's records» (SPEC-004 R16). The tree started clean under your pathspec, so what git
shows changed under the target is what this delivery did, and the records' paths are the file set
the report hands `/review-change`.

Name each path `--unrecorded` prints where it belongs, with the effect the producer that changed it
states — re-entered to state it where its return did not:

- a source path in the implementation's `files`;
- a test file in the proof's `tests`, or in the proof's `files` where the path holds no test the
  proof's `tests` names.

A path neither producer claims is reported as such and never reverted: what to do with a change
nobody explains is the person's.

On a re-delivery `--unrecorded` also prints `uncarried:` beside an unchanged path the
implementation names that the record it replaces did not — «A re-delivery names a file the tree did
not change only where the record it replaces named it» (SPEC-004 R21). That path is source the task
never wrote: the return goes back to the implementer, and where the fact holds only there, the stop
`references/implementer-returns.md` states is the answer.

Rerun until it exits 0. A record rewritten here goes through its writer again under `--replace`,
from the producer's revised return. Rewriting the implementation changes the pin the proof carries,
and the writer prints a receipt saying so: rewrite the proof whole through `--write-proof
--replace`, with the same `--note` lines, so its `implementation` is stamped again.

## What the validator holds, and what fixing means

`deliver.py` validates every delivery node against the contract and derives `delivery.json`. It
also checks, against the plan:

- the task exists, and a proof sits beside its implementation;
- every criterion of the task is answered exactly once, and nothing else is;
- every specification node the task implements is accounted for;
- no task is delivered before what it builds on;
- every record's pin matches its own task as it stands, and each proof's pin matches the
  implementation beside it;
- every departure disclosed against a standard rule cites one that standard declares and sits in a
  file the record says it wrote.

**Never write or edit `delivery.json` yourself.** Report the output verbatim. A non-zero exit means
the run failed: fix and rerun, and never describe the delivery as sound while it is not.

**Fixing means form, never knowledge.** A malformed pin, a criterion paraphrased instead of quoted,
a missing entry for a node the task implements — these are yours to correct. A criterion the source
does not satisfy is recorded as unmet, never talked into met. A fact the specification does not
hold is never supplied to make a check pass: it is a stop.

## What the bind does, refuses and prints

The trace outlives the delivery's records: it is what lets a later `/plan-work` or `/analyse` ask
whether this code and the specification it followed have since moved apart.

- **It binds what the record already says.** `--bind-record` reads the record's `nodes` and binds
  every entry carrying `encoded_at`, at exactly the paths it lists. A node answered only by `how`
  is not bound, and a record with no such entry binds nothing — neither is a failure. The trace
  binds what the source encodes; the proof's criteria stay with the records.
- **It binds the whole record or nothing.** A node or file that does not resolve refuses all of it.
- **It is the one write outside your three roots** — `siegard-trace.json`, beside `siegard.json`
  at the target's git toplevel. What it refuses — a node the specification no longer holds, a trace
  bound to a different specification root — is reported plainly, never worked around. A refusal
  does not unwrite the delivery: the validated records stand, and the files are just not yet linked.
- **It may print a stale-bindings receipt**, never a refusal: another node's binding over a file
  this delivery rewrote, or a file this task's nodes carried from an earlier bind that has since
  changed. Keep the receipt whole for the report. The `/review-change` that follows reads every
  file of the change against every node bound to it and restamps what cleared; where no review
  follows, the report's `/reconcile` door is what answers it.
