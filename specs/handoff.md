---
id: "SPEC-006"
title: The handoff
status: proposed
contract_version: spec/1
---

# The handoff

## Scope

This specification fixes the form of the last message a skill's invocation leaves to a person —
its report, or the stop that ends it early — and when that message names one door over the
others. It binds every skill that reports, and the two orchestrating entry points that relay
another skill's report.

It decides what the message opens with, what it may recommend and on what grounds, what it never
recommends, and where a recommendation is recorded so that it can be counted.

Grounds: one consumer session on 2026-10-05 and 2026-10-06, Siegard 5.2.0, read from its
transcript. Its 26 long final messages ran from 1,950 to 24,343 characters, and in 24 of them the
last decision word sat past 78% of the text. The person asked 7 questions right after a report —
the status, what had to be done, the recommendation, whether anything blocked, whether the
initiative was over, what an enumerated "8 deliveries" were, and the detail of a risk handed as
an observation. Of the 10 skill reports that handed doors, 6 handed doors only the person could
choose — the ask, a review of a decided diff — 2 handed doors a fact on disk decided, 2 handed one
door such a fact excluded, and 1 handed two readings of the same evidence. The agent recommended
on 4 doors when asked: the 3 a fact decided held; the 1 over two readings was wrong, and a binder
refused the corrective increment it led to. One `/plan-work` invocation ran only to stop at a
precondition the report before it already held.

### Decided elsewhere, deliberately not restated here

- What each skill reports and in which order — that skill's own file.
- What stops a skill — that skill's own file; a contradiction between scope and specification
  is a stop only a person settles — `specs/minimal-documentation.md` (SPEC-001 R13).
- What a reviewer returns: evidence, never a verdict, a severity or a ranking — the reviewing
  agents' own files.

## Definitions

- **Handoff** — the last message of a skill's invocation, where control returns to a person: its
  report, or a stop that ends the run early. A spawned agent's return is never a handoff.
- **Door** — an act the handoff hands the person, an invocation ready to paste among them.
- **Owed act** — a door without which a named step refuses to run; the handoff names that step.
- **Offered act** — any other door.
- **Criterion** — the closed reason a recommendation is made on, one of `precondition unmet`,
  `rule violated`, `already done`, `reading paid twice`.

## Requirements

### What the handoff opens with

- **R1** — A handoff opens with what needs the person, and explains after. The opening holds, in this order, omitting a part that is empty: the state in one line; what this report withdraws from what the same invocation said earlier; each pending decision with its doors, what each door does, and what stays as it is if none is taken; each owed act with its invocation and the step it unblocks, kept apart from every offered one; neither list is ranked, and an order no command printed is a preference. Each item of the opening says what it is for the person, in the session's own plain words — what must be done before a named step runs, what may be done and nothing waits on, what only the person decides, what is suggested and why — and never in a word of this framework's: a reader who has never opened a skill's file reads the opening whole. Where the report recommends a door, the opening says so and why, before any explanation. The report then follows the order the skill's own file states, in the session's language, each framework term explained once where it first appears, and every command output, note and log entry quoted verbatim and untranslated.

### What a handoff recommends

- **R2** — A recommendation names the door, the criterion, the deciding fact and the reversing fact; without all four, none is named. The criterion is one of four and no other: `precondition unmet`, the door's own entry point refuses its inputs as the tree stands; `rule violated`, the door breaks a rule this framework states; `already done`, the door's work is already in the tree; `reading paid twice`, the same file read by two judgments, where of two readings over the same files the one owed once is named over the one paid twice — two invocations over different files are each paid once, and their order is a decision about cost. In the handoff the four are carried as sentences in the session's plain words — the door, why it, what on disk says so, what would change it — and the criterion's name is written as it reads here only in the log line R5 states; a label, a field name or the criterion's English name in the prose is the record showing through. The deciding fact and the reversing fact are each a fact on disk, named by path or quoted.
- **R3** — No recommendation is made over the ask or its scope, over a scope and a specification that contradict, over two readings of one piece of evidence, over whether a finding matters or what route it deserves, or over a decision about cost. Each is the person's, and a handoff hands its doors and names none.

### What stops

- **R4** — A finding stops nothing. A handoff names a stop only where the skill's own file names one, and names it as a stop. Where a handoff says a step may proceed, it lists the checks it ran and their output verbatim.

### Where a recommendation is recorded

- **R5** — An orchestrating entry point that relays a report carrying a recommendation writes it to the run's orchestration log as one line, `recommended: <door> — <criterion> — <deciding fact>`. A recommendation made where no orchestration log exists is in the report alone, and nothing counts it.

## Validation required before acceptance

1. Every skill whose file states a report cites R1 beside it.
2. Telemetry counts the `recommended:` lines of every orchestration log under the delivery root,
   by criterion, and names each line that does not parse; it computes nothing about which door
   was taken.
3. A consumer initiative run under this specification is read for the lines it recorded: fewer
   than two per ten handoffs that hand doors reverses R2, leaving R1, R3 and R4.

## Readings

- 2026-10-07 — not yet read: no initiative has run end to end through `/deliver-scope` or
  `/adopt-scope` under 5.5.0 or later, so no orchestration log holds a `recommended:` line. The
  numerator is `telemetry.py`'s `recommendations` count by criterion; the denominator — handoffs
  that hand doors — is read from the transcript until telemetry counts it. Verdict pending.
