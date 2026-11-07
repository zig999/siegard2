# What a binder's notes do

Read at step 4 when a binder returns any note not classed `unstated`, and before writing a task
that carries `stands`.

## Where the notes land

A binder's notes are appended to the task body's `## Notes`, one sentence per line, and the report
repeats them by task: the diff is the review, and a divergence only the conversation holds is one
the reviewer never sees. What each class means is the binder's file; what it does here is this:

| class | the note opens | what it does to the task | what travels with it |
|---|---|---|---|
| `compound` | never written to a task | sends the skeleton back to the decomposer to be re-cut, once | the criterion and the conditions the binder named |
| `blocking` | `BLOCKING, from the specification —` | stops it being written until settled | the note, where the scope is what it blocks |
| `underdetermined` | `UNDERDETERMINED, from the specification —` | nothing; it re-cuts nothing | the note, and the implementation named in `passes` |
| `remainder` | `REMAINDER, from the specification —` | nothing; it re-cuts nothing | the note, and the destination named in `belongs` |
| `advisory` | `ADVISORY, from the specification —` | nothing | the note |

**Every opening is exact text, never a style.** `bin/plan.py` holds the blocking and
underdetermined openings as constants and refuses a task persisting an `UNSTATED` one;
`/implement-task` collects underdetermined entries by their opening for the test-author; and
`/siegard-telemetry` counts both.

## `compound`

A `compound` note is never persisted: it is answered before the task exists as a file. The skeleton
goes back to the decomposer with the criterion verbatim and the conditions the binder read in it,
to be re-cut into criteria of one condition each, or into two skeletons where the conditions are two
outcomes. Then it runs through step 4 again, and the notes returned on the re-cut criteria are the
ones that land.

**Once.** A `compound` note over a skeleton this invocation already re-cut is written into the
report with both readings, and the skeleton proceeds as the decomposer last left it. You rewrite no
criterion yourself: the decomposer is the author of criteria.

## `blocking`

Settling a blocking note takes one of two routes, and the skeleton's `rationale` says which:

- **The blocked statement was the decomposer's decision** — the skeleton carries `rationale` over
  that cut: the skeleton goes back to the decomposer with the note, is re-cut, and runs through step
  4 again.
- **It came from the scope**: the task is written with the note, and the report names it as a
  conflict only the person settles — through the scope, or through `/analyse` extending the
  specification.

The class is never yours to overrule: a blocking note you disagree with is still settled as
blocking, and the disagreement goes in the report.

## `remainder` and a binder that found nothing

A remainder's clause is answered where it belongs — another task's reference, the epic's
`uncovered`, or scope this plan does not yet hold. No validator walks clauses, so the report is
where a reviewer checks that something answers it.

Where the binder found nothing to implement against, the task carries `rationale` saying why:
ungoverned work is a claim someone reviews.

## A note that names a node outside the epic's covers

Where a note says the task needs what the candidates do not hold, the cut is wrong. Decide one of
three, never widening the reference by hand:

1. **Grow the epic's `covers`** and re-run step 4.
2. **Move the task** to the epic that covers it and re-run step 4.
3. **Let it stand**, recorded on its own line immediately after the note in `## Notes`:
   `Decision, beyond the covers — stand: <why>`. The validator refuses a task whose `## Notes`
   names a node outside its epic's covers with no such line naming that node.

## A skeleton carrying `stands`

Once the binder has returned its `implements`, a skeleton carrying `stands` is held to the trace
before it is written — «every file it names is bound in the trace, before the task is written, to
every node the task implements» (SPEC-004 R18):

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --encodes <target-source-root> <each file stands names>
```

A file the command cannot read — a path spelled from the repository rather than from the target
source root among them — or a node the task implements that the output does not list for those
files sends the skeleton back to the decomposer once, with the output verbatim:

- **Where a task of this plan writes the source that holds the fact**, the proof becomes a criterion
  of that task, and the skeleton goes.
- **Where the source already holds it and the trace does not bind it**, no task is cut — «The plan
  reports the reconciliation that would bind it, over the files that hold it, and the proof waits
  for that binding.» (SPEC-004 R19) — and the report hands `/reconcile` over those files as the
  person's door.

A skeleton that comes back carrying the same unconfirmed `stands` is not written; the report names
it with the output.
