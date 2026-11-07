# Validating and binding

Read at step 7 before the first validation, and at step 8 when the bind prints anything.

## Why the trace is bound

The delivery's own records are disposable — the plan and the delivery root exist to get this code
written, and nothing requires either to survive the code landing. What has to survive is the link
between the specification and the files that now encode it, so a later `/plan-work` or `/analyse`
invocation can ask, without either root, whether this code and the specification it followed have
since moved apart.

## Naming every changed path

«Every path a delivery created, modified or deleted under its target source root is named by one
of the delivery's records» (SPEC-004 R16). The tree started clean under this invocation's
pathspec, so what git shows changed under the target is what this delivery did, and the file set
the report hands `/review-change` is the records' — a path they leave out is one no review reads.
Each path it prints is named where it belongs: a source path in the implementation's `files`, a
test file in the proof's `tests`, or in its `files` where the path holds no test `tests` names —
with the effect the producer that changed it states, that delegation re-entered to say it where
its return did not. A path neither producer claims is reported as such and never reverted: what
to do with a change nobody explains is a person's. On a re-delivery it prints `uncarried:`
beside an unchanged path the implementation names that the record it replaces did not — «A
re-delivery names a file the tree did not change only where the record it replaces named it»
(SPEC-004 R21) — and that path is source the task never wrote: the return goes back to the
implementer, and where the fact holds only there, the stop `references/implementer-returns.md` states is the answer. Rerun until it
exits 0. A record rewritten
here goes through its writer again under `--replace`, from the producer's revised return. An
implementation rewritten changes the pin the proof carries, and the writer prints a receipt
saying so: the proof is then rewritten whole through `--write-proof --replace`, with the same
`--note` lines, so its `implementation` is stamped again from the record as it now stands.

## What the validator holds, and what fixing means

This validates every delivery node against the contract, runs the checks that need the plan — the
task exists, a proof sits beside an implementation, every criterion of the task is answered
exactly once and nothing else is, every specification node the task implements is accounted for,
no task is delivered before what it builds on, every record's
pin matches its own task as it stands, each proof's pin matches the implementation beside it, and
every departure disclosed against a standard rule cites one that standard declares and sits in a
file this record says it wrote — and derives `delivery.json`. **Never write or edit
`delivery.json` yourself.** Report the command's output verbatim. If it exits non-zero, the run
failed — fix and rerun, and never describe the delivery as sound while it is not.

**Fixing means form, never knowledge.** A wrong shape — a malformed pin, a criterion paraphrased
instead of quoted, a missing entry for a node the task implements — is yours to correct. A criterion the source
does not satisfy is recorded as unmet, not talked into met. A fact the specification does not hold is not
supplied to make a check pass: it is a stop, and it was one before the source was written.

## What the bind does, refuses and prints

It reads that record's `nodes` and binds every entry carrying `encoded_at`, at exactly the paths
that entry lists — so nothing here is retyped, and the rule that the trace states what the record
already says rather than a second judgment about it is held by the reading rather than by you. A
node the record answers only by `how` — constrained but encoded nowhere — is not bound: there is no
file to name, and a bind with none is refused; a record naming no such node binds nothing and that
is not a failure. Where a proof exists, its criteria stay with the implementation record; the trace
binds what the source encodes, not what the tests prove.

The whole record is one act: a node or a file it names that does not resolve refuses all of it and
writes nothing, because a trace holding half a delivery's bindings reads exactly like one holding
all of them.

This is the one place in the whole invocation that touches a file outside the delivery root, the
work root and the target source root — `siegard-trace.json`, beside `siegard.json` at the
target's git toplevel — and it is not this skill's to design around: `trace.py` is the one writer,
and what it refuses (a node the specification no longer holds, a trace already bound to a
different specification root) is reported here, plainly, rather than worked around. A refusal at
this step does not unwrite the delivery: the records already validated stand on their own, and
what is missing is exactly the fact that this delivery's files and the specification it followed
are not yet linked for anyone who looks later.

One more thing the bind may print, and it is a receipt, never a refusal: **the bindings this act
left stale** — another node's binding over a file this delivery rewrote (a bind restamps only this
task's own nodes), or a file this task's nodes carried forward from an earlier bind that has since
changed. Keep the receipt whole for the report. The `/review-change` that follows this delivery is
what answers it: its conformance pass reads every file of the change against every node the trace
binds to it and restamps what cleared. Where no review will follow, the receipt is the one moment
those bindings are in the hands of whoever changed the files, and dropped here it survives only as
a `--check` finding nobody was going to run.
