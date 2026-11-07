# Re-delivery, the proof-only re-delivery, and `stands`

Read at step 1, before anything is written, when a record already sits at the path this task
computes to, when the person names a proof-only re-delivery, or when the task carries `stands`.

## A record already at the path

A third fact the report does not carry, because you can see it directly: **a record already at the
path this task computes to.** That is a re-delivery, not a stop, and the report says so. Every run name the steps give is deterministic per task, and `bin/run.py` refuses a name that already exists — so a
re-delivery names each of its runs with the next free `-N` suffix the delivery root's `run/`
directory does not yet hold, exactly as a retry within one invocation does. `ls <delivery-root>/run`
is how that is read; a name is never improvised past the refusal, and a phase is never retyped from
prose to avoid it. Both records are rewritten whole rather than amended — a record amended across two acts of writing
describes neither, and the proof's pin on the implementation refuses the pair if you rewrite one
and leave the other. `git diff` over the two is then the history of the delivery.

## The implementation stands, and only the proof moves

One narrower re-delivery exists, and only the human names it — stated in the invocation, never
inferred from the tree: **the implementation stands, and only the proof must answer a tree that
moved.** Two plain cases. A sibling task's legitimate delivery falsifying an assertion that
claimed more than this task's criteria establish — totality over ground the two tasks share. And
a certification an auditor refused while naming what would close it: a reconciliation or a
review judged a node this task encodes as decided by reading, with `remainder: testable` and the
assertion in `remainder_why`, and `trace.py --owed` lists it as the work a test closes. For that
case the invocation states three things the record holds — the node's identity, the assertion
verbatim, and the proof file(s) the record named — and they reach the test author as its
`remainder` line of step 5's block: the assertion is the obligation the new test fails for, and the test
names the node under `demonstrates`, so the next review's staging carries the claim to
certification without anyone composing it. The proof's `## Notes` names the record that left the
remainder. Nothing here decides that a remainder is worth a test — `--owed` prints the count of
bindings a reading still decides on the file, and whether closing this one frees a judge is what
a person weighs.
Steps 3 and 4 do not run: the implementation record is not touched, and the proof is rewritten
whole — never amended — by a fresh test author reading the tree as it stands now, with the suite
running and captured as ever, and written through `--write-proof --replace` as step 6 states,
every `--note` line it carries given again. The pin the writer restamps is valid precisely
because the implementation record did not move; what the validator refuses is the opposite
direction, an implementation rewritten under a proof left behind. Two things hold the mode
honest. Before anything is written, run

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --check --all <target-source-root>
```

over the target, and read the findings that name a node the task implements — on a file its
implementation record names, or the node alone: the implementation's files are bound with
digests, and one of those bindings out of date is exactly what makes "the implementation stands"
false — that drift is a stop. Where what moved it is a later task's own delivery over
that file, the answer is not this task's at all: the test is that delivery's to rewrite, under
step 6's second `test` exit; anywhere else, the answer is a full re-delivery. A finding that names any other node on those files is not this task's, so the delivery proceeds
and the proof's `## Notes` names each such node and file, one `--note` line apiece — «A binding of
another node to one of those files does not close it: the review that follows reads that binding,
as it does for a task carrying `stands` (R26).» (SPEC-004 R25). **`--all` is what
makes this mode's premise checkable at all**, and it is the one place in this framework that
needs it: a project may declare a target freely edited, and an ordinary check then holds that
class back as noise a reader cannot act on — but here it is the whole question, so this call asks
for the findings rather than the report. And the reason the proof had to move goes in the record's
`## Notes`, naming the task whose delivery falsified it, so the diff carries what only the
conversation would otherwise hold.

## A task carrying `stands`

**A task carrying `stands` is delivered the same way from its first delivery, because its plan
says so** — the one case where the narrower route is read from the task rather than from the
invocation: `/plan-work` writes `stands` only over files the trace already binds to every node
the task implements, in the proof increment the human names or in an ordinary decomposition
alike. The implementation stands at the files `stands` lists,
and nothing in this delivery writes source. Before anything is written, `trace.py --encodes
<target-source-root> <each file>` must still list every node the task implements for them, and
the same `trace.py --check --all` is read for the findings that name a node the task implements —
on one of those files, or the node alone: «a binding the trace does not hold, a file changed
since the binding was written, or a node whose text moved since the file was read against it
makes the implementation not stand» (SPEC-004 R26). Any one of them and the task is not
delivered: the door is `/reconcile` over the files those findings name, which the person asks
for, and the report hands it with those files named. A finding that names any other node on those files is not this task's, so the delivery proceeds
and the record's `## Notes` names each such node and file, one `--note` line apiece — «A binding
of a node the task does not implement to one of those files is never that refusal: the review that
follows reads each `stands` file against every node the trace binds to it.» (SPEC-004 R26). `--write-implementation`
holds the same reading over the trace and refuses the record where a binding of the task's own
nodes is out of date or absent. Step 3 does not run. Step
4 does, over the tree as it stands: the build is what shows the standing implementation still
builds, and the record points at that run as any implementation record does. No producer is
spawned for the record: you compose the return yourself, from the plan and from the record the
task's `sources` name, never from a reading of the source — the same mapping the
`task-implementer` would return, as plain YAML in a file — and write the record through
`--write-implementation --from-text <that file>`, stamps and all, exactly as step 4 states.
What the mapping holds: `stands` exactly as the task lists it, `files` empty, one
criteria entry per criterion — `met: true`, its `how` saying that the implementation stands at
those files and the proof below decides it — and one node answer per node the task implements,
`how` quoting where the fact is held as the named record's reading states it, never
`encoded_at`: this delivery binds nothing, and step 8 prints that and moves on. The test author
receives each criterion's assertion as its `remainder` line and the task's `stands` as the files
under test; the proof names the node under `demonstrates`, and the review that reads it — with
the `stands` files in its file set, which the validator holds — certifies it.
