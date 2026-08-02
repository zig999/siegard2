---
name: implement-task
description: Implements exactly one bound task and writes its tests — the implementation first, then the tests against the record it produced. Use once a plan has been reviewed and a task's dependencies are demonstrated. Not for planning, which is prepare-work; not for reviewing what was written, which is review-change; not for running tests; and not for taking more than one task.
disable-model-invocation: true
argument-hint: "[task-id] [artifact-dir]"
allowed-tools: Read, Write, Edit, Grep, Glob
---

You carry one bound task from plan to written code and tests. One invocation, one task.

This is the only path here that writes source, and it is deliberately narrow. It runs nothing: no build,
no test, no version control. Running is a script's work under `foundation/0004` R6, and the diagnosis of a
failed run belongs to `review-change`, which reads output this path never produced. A skill that could run
its own tests would be the only witness to whether its work passed.

It is a procedure and not a sequencer. Nothing records where the run stands, and a second invocation over
the same task starts over rather than continuing.

## Required inputs

A missing input is a stop, not a default:

1. **the task identifier**, and the `backlog/1` holding it;
2. **the `execution-binding/1`** for that task;
3. **the artifact directory**;
4. **the identifiers** — `im_` and `ta_`, each followed by eight hex digits. You mint neither.

For a task the backlog records as a defect, also **the reproduction** — how the failure is observed.
Without it the tests prove the fix rather than the defect, and the difference is invisible afterwards.

## Before anything is written

Read the binding's `unresolved` for this task. If it holds anything the task needs, **stop**. That is a
fact the specification does not settle, and implementing over it writes an invention into the codebase
where nobody will look for a decision. Report which entry stopped the run and let the person resolve it —
`prepare-work` step 4 already produced the `specification-gap/1` that examines it.

This check is the whole reason implementation is separated from planning. An implementer that discovered
the gap mid-file would be most of the way to filling it.

## The order, and why it cannot be reversed

```
implement → author tests → stop
```

1. **Implement** — delegate to `implementer` with the task, the binding, and the record identifier. It
   writes the source and returns an `implementation-record/1`: what was written, which criteria are
   satisfied, what was inferred, what it departed from, what it deferred.

2. **Author tests** — delegate to `test-author` with the task, that record, and the kind of task. It
   writes the tests and returns a `test-authoring-record/1`.

The tests come second and from a different agent on purpose. An implementation and its tests written in
one pass agree by construction, including where both are wrong. The cost is real — the test author
re-reads code someone else had in context — and it buys the only thing that makes the tests evidence: the
person who decided the behavior is not the only person who decided what proves it.

The `inferences` in the implementation record are what the test author reads most closely. Each is a
decision nobody specified, and a test over one turns a silent choice into a stated one.

## Where the run stops

Write both records to the artifact directory, then summarize: the files written, every criterion and
whether it is satisfied, every inference recorded, every divergence, and everything the test author left
untested or contested. Then stop.

Do not judge whether the work is done, whether it is correct, or whether it may be merged. Nothing here
carries a ready flag: `foundation/0005` R5 keeps a producer from running the validator over its own
output, and a skill asserting its own work is ready would reintroduce exactly that at one level up.

## When something fails

- **`unresolved_fact`** — the binding names something the specification does not settle. Nothing is
  written. This is a successful stop, not a failure of the run.
- **`unreadable_reference`** — a reference the binding names does not exist. Nothing is written; the
  binding is wrong, and improvising the reference is the failure this path exists to bound.
- **`missing_reproduction`** — a defect task arrived without its reproduction. The implementation stands;
  the tests do not, and the record says so.
- A partial implementation is never reported as complete. Where the implementer wrote files and then
  stopped, the record names what was written and the run is a failure — `foundation/0006` R18.
