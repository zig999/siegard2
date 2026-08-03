---
name: prepare-work
description: Turns a stated scope into a reviewable plan — surveying what already exists, breaking the scope into tasks, binding each task to the specification sections its executor will need, and reporting what the specification leaves open and what infrastructure is missing. Use before any code is written, including on an existing codebase. Not for implementing a task, which is implement-task; not for reviewing a change, which is review-change; and not for deciding what to build.
disable-model-invocation: true
argument-hint: "[scope] [artifact-dir]"
allowed-tools: Read, Write, Grep, Glob
---

You turn a stated scope into a plan somebody can argue with. One invocation, one plan.

This is a procedure, not a sequencer. `foundation/0004` R2 forbids the framework shipping anything that
decides at runtime which capability runs next, records where a run stands, or resumes one. The order below
is written down, followed once, and forgotten: nothing here keeps state, and a second invocation starts
over rather than continuing. If you find yourself wanting to record progress, that is the workflow
machinery this framework removed.

Two rules govern everything below:

- **You supply no fact the specification does not state.** Where it is silent, that silence is the output —
  it travels in `unresolved` and then into a `specification-gap/1`. A plan that quietly answered an open
  question would deliver an invention to an implementer with the authority of a bound reference.
- **You stop at the plan.** The last step is a person reading it. Nothing here implements, and a plan that
  flows straight into work is a plan nobody reviewed.

## Required inputs

A missing input is a stop, not a default:

1. **the scope** — what is to be built, in the caller's words;
2. **the artifact directory** — where the artifacts below are written;
3. **the identifiers** — `ci_`, `bl_`, `eb_`, `sg_`, `ir_`, each followed by eight hex digits. You mint
   none of them: an artifact stamped from a clock could not be repeated and compared.

Optionally: **the specification set**, and **an existing backlog** where work is already recorded.

## The order, and why it cannot be rearranged

```
survey → decompose → bind → gaps + infrastructure → stop
```

1. **Survey** — delegate to `codebase-surveyor` with the scope. It returns a `code-inventory/1`: what is
   there, what conventions hold, what must not be rebuilt, what the change risks. Skip it only for a
   repository that holds nothing yet, and say so in the summary.

   The survey comes first because a decomposition written before it invents tasks for things that already
   exist. Its `must_not_duplicate` is the section that changes the backlog.

2. **Decompose** — delegate to `backlog-decomposer` with the scope and the existing backlog if any. It
   returns a `backlog/1`. Supply no granularity bound unless the caller asked for one: the framework ships
   none, and a number it invented would be a threshold nobody calibrated.

3. **Bind** — delegate to `execution-contract-binder` with the backlog, the specification set, and the
   inventory from step 1. It returns an `execution-binding/1`, one entry per task.

   Binding comes after decomposition and never with it: the same agent doing both would choose the
   references that suit the tasks it just wrote, and no one could tell a task shaped by the specification
   from a specification read to fit a task.

4. **Gaps** — collect every `unresolved` entry across the bindings. Where any exists, delegate to
   `specification-gap-reporter` with those entries as the required facts. It returns a
   `specification-gap/1`. Where the bindings resolved everything, skip it and say so.

5. **Infrastructure** — delegate to `infrastructure-dependency-analyst` with the scope. It returns an
   `infrastructure-readiness/1`. It runs against the scope rather than per task, because a dependency is
   shared and reporting it five times says nothing five times.

Steps 4 and 5 are independent of each other and may run in either order or together. Steps 1 through 3
may not be reordered.

## Where the run stops

Write each artifact to the artifact directory under its own identifier, then summarize for the person:
how many tasks, how many bound references, every gap the specification leaves, and every dependency that
is not ready. Then stop.

Do not decide whether the plan is good enough, whether the gaps are blocking, whether work may start, or
which task goes first. Order is derivable from the dependencies the backlog records — say so, and let the
reader derive it.

## When something fails

Each agent has closed failure outcomes and reports them rather than improvising. Carry the failure to the
person as it was returned:

- an agent that stops for a missing input has named what is absent — supply it and invoke again;
- a backlog that fails `backlog/1` at the boundary is not bound over. Binding a rejected backlog would
  produce references for tasks nobody accepted;
- a survey that cannot locate the area means the scope names nothing findable. That is a fact about the
  scope, and it belongs to the person rather than to a second attempt with a wider search.

Never repair an artifact that failed its contract. `foundation/0004` R12: nothing repairs it, and nothing
consumes it while the failure stands.
