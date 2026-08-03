---
name: review-change
description: Reviews a written change from every angle that requires judgement — security patterns, rule conformance, structure, what the change exposes to its consumers, which acceptance criteria the tests prove, and why any test failed — returning the findings without a verdict. Use once a change is written, on a branch, a pull request, or a working tree. Not for planning, which is prepare-work; not for implementing or fixing, which is implement-task; and not for approving anything.
disable-model-invocation: true
argument-hint: "[file-set] [artifact-dir]"
allowed-tools: Read, Write, Grep, Glob
---

You review a written change and report what is there. One invocation, one review.

This is where the source framework's design failed hardest, and the failure is worth naming because
everything below is shaped by avoiding it. Its review agents each computed an action — block, remediate,
warn — and a verdict, and an orchestrator acted on them mechanically. The reviewer was the gate. Under
`foundation/0005` R5 a specialized agent does not choose what runs next, so none of the agents below
returns a verdict and neither does this skill. What you produce is evidence. Who decides is a person.

It is a procedure and not a sequencer: nothing records where the run stands, and a second invocation
starts over.

## Required inputs

A missing input is a stop, not a default:

1. **the file set** — every path the change created or modified, listed explicitly. Never discovered:
   a review that chose its own scope reports a different set each run, and a clean result would not say
   what it was clean over;
2. **the artifact directory**;
3. **the identifiers** for the passes you run — `ss_`, `cr_`, `as_`, `re_`, `ca_`, `td_`. You mint none.

Optionally, and each unlocking one pass: **the rule registry**, without which conformance cannot run;
**the acceptance criteria** and the test file set, without which coverage cannot; **a `test-run/1`**,
without which failures cannot be diagnosed; **a prior `code-inventory/1`**, whose predicted risks the
exposure pass then confirms or drops; **the declared architecture** and **the declared security profile**.

The `test-run/1` is produced by `bin/run_suite.py`, and **the caller runs it, not this skill**. Nothing
here executes: keeping the run outside means the evidence exists on disk before any judgement is made of
it, and the same artifact can be handed to a second reviewer who reaches a different conclusion about the
same run. Supply the artifact, or accept that the failures pass does not run.

An absent optional input never becomes a default. It removes a pass, and the summary says which pass did
not run. A review reported as clean over a pass that never ran is the failure this rule prevents.

## The passes

They are independent. Run every one whose inputs are present, in any order, or together — none reads
another's output.

| Pass | Agent | Runs when |
|---|---|---|
| security | `security-pattern-scanner` | always |
| conformance | `conformance-reviewer` | a rule registry was supplied |
| structure | `architecture-pattern-scanner` | always |
| exposure | `regression-consumer-analyst` | the change states what changed in each file |
| coverage | `acceptance-coverage-auditor` | criteria and a test file set were supplied |
| failures | `test-failure-diagnostician` | a `test-run/1` whose `outcome` is not `passed` was supplied |

Three of them divide work that one agent used to do badly, and the division is not arbitrary. Security
belongs to the scanner, structure to the structural scanner, and everything else the registry names to
the conformance reviewer — one authoritative definition per concept, so a finding has one home and two
passes never disagree about the same line.

Supply no threshold to the structure pass unless the caller gave you one. The framework ships none:
`foundation/0006` R21 admits only a threshold calibrated from executed runs, and every numeric bound the
source agent carried was uncalibrated. Where the caller supplies one, the artifact records that the value
came from the caller.

## Where the run stops

Write each artifact to the artifact directory, then summarize for the person:

- every finding, grouped by pass, with its evidence;
- **which passes did not run, and which input was missing** — this line is not optional. It is what
  separates a clean review from a narrow one;
- for the structure pass, whether any threshold was applied and where the value came from.

Then stop. Do not compute a verdict, rank the findings, decide what blocks, or open work from them. A
finding marked `contested` by the conformance reviewer stays contested: resolving it here would discard
the one signal that tells a careful finding from a confident one.

## When something fails

- an agent that stops for a missing input has named it — the pass did not run, and the summary says so;
- **`unreadable_path`** stops the pass rather than narrowing it. A scan over the readable subset would
  report clean over files nobody read;
- **`no_failure_reported`** from the diagnosis pass means the supplied run holds no failure. That is not
  an error in the run: the pass should not have been asked for, and saying so is the answer.
- a `test-run/1` whose outcome is `not_found` or `timed_out` still runs the pass. Nothing was proved
  about the code, and that is exactly what the diagnosis says — a run that could not execute is a
  finding, not an absent input.
