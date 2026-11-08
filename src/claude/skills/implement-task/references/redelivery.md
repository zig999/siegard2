# Re-delivery, the proof-only re-delivery, and `stands`

Read at step 1, before anything is written, when a record already sits at the path this task
computes to, when the person names a proof-only re-delivery, or when the task carries `stands`.

## A record already at the path

**A record already at the path this task computes to makes this a re-delivery**, not a stop, and
the report says so. Run names are deterministic per task and `bin/run.py` refuses one that already
exists, so name each run with the next free `-N` suffix the delivery root's `run/` does not yet
hold, read with `ls <delivery-root>/run` — exactly as a retry within one invocation does. Never
improvise a name past the refusal or retype a phase from prose to avoid it.

Both records are rewritten whole, never amended: the proof's pin on the implementation refuses the
pair if one is rewritten and the other left. `git diff` over the two is the delivery's history.

## The implementation stands, and only the proof moves

One narrower re-delivery exists, and only the person names it — stated in the invocation, never
inferred from the tree: **the implementation stands, and only the proof must answer a tree that
moved.** Two cases call for it:

- **A sibling task's delivery falsified an assertion** that claimed more than this task's criteria
  establish — totality over ground the two tasks share. The proof's `## Notes` names the task
  whose delivery falsified it.
- **An auditor refused a certification and named what would close it.** A reconciliation or a
  review judged a node this task encodes as decided by reading, with `remainder: testable` and the
  assertion in `remainder_why`, and `trace.py --owed` lists it. The invocation states the node's
  identity, the assertion verbatim and the proof file(s) the record named; they reach the
  test-author as the `remainder` line of step 5's block, and the new test names the node under
  `demonstrates`. The proof's `## Notes` names the record that left the remainder. Whether a
  remainder is worth a test is the person's to weigh, not this mode's.

Steps 3 and 4 do not run: the implementation record is not touched. A fresh test-author rewrites
the proof whole against the tree as it stands, the suite runs and is captured as ever, and the
proof is written through `--write-proof --replace` with every `--note` line given again. The
writer restamps the proof's pin, which stays valid because the implementation record did not move.

Before anything is written, run over the target:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --check --all <target-source-root>
```

`--all` is needed here alone: it includes a freely edited target's findings, which an ordinary
check holds back. Then read the findings that name a node the task implements, on a file its
implementation record names or on the node alone:

- **Any such finding is a stop**: a binding out of date is what makes "the implementation stands"
  false. Where a later task's own delivery over that file moved it, the test is that delivery's to
  rewrite, under the second `test` exit of `references/red-suite.md`; anywhere else, the answer is
  a full re-delivery.
- **A finding that names any other node on those files is not this task's.** The delivery proceeds,
  and the proof's `## Notes` names each such node and file, one `--note` line apiece — «A binding of
  another node to one of those files does not close it: the review that follows reads that binding,
  as it does for a task carrying `stands` (R26).» (SPEC-004 R25).

## A task carrying `stands`

**A task carrying `stands` is delivered the same way from its first delivery, because its plan
says so.** `/plan-work` writes `stands` only over files the trace binds, together, to every node
the task implements. The implementation stands at those files, and this delivery writes no source.

Before anything is written, `trace.py --encodes <target-source-root> <each file>` must still list
each node the task implements for some file and some such node for each file, and the same
`trace.py --check --all` is read for the findings that name a node the task implements, on one of
those files or on the node alone:

- **Any such finding means the task is not delivered** — «a file changed since the binding was
  written, or a node whose text moved since the file was read against it makes the implementation
  not stand» (SPEC-004 R26). The door is `/reconcile` over the files those findings name,
  handed with those files.
- **A finding that names any other node on those files is not this task's.** The delivery proceeds,
  and the implementation record's `## Notes` names each such node and file, one `--note` line
  apiece — «A binding of a node the task does not implement to one of those files is never that
  refusal: the review that follows reads each `stands` file against every node the trace binds to
  it.» (SPEC-004 R26).

`--write-implementation` holds the same reading over the trace and refuses the record where a
binding of the task's own nodes is out of date, or a node or a file is bound to none of the other.

Step 3 does not run. Step 4 does, over the tree as it stands, and the record points at that build
run. No producer is spawned for the record: you compose the mapping yourself, as plain YAML in a
file, from the plan and from the record the task's `sources` name — never from a reading of the
source — and write it through `--write-implementation --from-text <that file>`. The mapping holds:

- `stands` exactly as the task lists it, and `files` empty;
- one `criteria` entry per criterion, `met: true`, its `how` saying the implementation stands at
  those files and the proof decides it;
- one `nodes` entry per node the task implements, its `how` quoting where the fact is held as the
  named record's reading states it, and never `encoded_at` — this delivery binds nothing, and step
  8 prints that and moves on.

The test-author receives each criterion's assertion as its `remainder` line and the task's `stands`
as the files under test. The proof names the node under `demonstrates`, and the review that reads
it, with the `stands` files in its file set, certifies it.
