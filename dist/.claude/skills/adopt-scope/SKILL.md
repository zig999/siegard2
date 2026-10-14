---
name: adopt-scope
description: Carries one context of source no delivery wrote end to end through the adoption route — /survey over the areas the ask names, /analyse over the material it wrote, /reconcile as an adoption over the ledger — committing between steps with a pathspec, recording each step in an orchestration log, and stopping at everything only a human settles. Use only where the human's own message states that the whole route is wanted for that context — an end-to-end ask quoted verbatim, or a standing automation whose condition names this skill. An intent inferred from anything less is a stop. Not for a single phase (invoke that entry point directly), never for code a delivery wrote, and never for planning or delivering work — the adoption changes no source.
effort: medium
---

You carry one context of adopted source through the route — survey, analysis, adoption —
committing between steps, and you stop. One invocation, one context adopted. This skill owns no
judgment of its own: every judgment belongs to the entry point that holds it, invoked whole, and
every routing decision is a script's answer. What this skill adds is only the taking of the
handoffs the reports already carry, and the commits between them — the two acts that were the
human's, delegated once, in the ask.

## Required inputs

A missing input is a stop, not a default:

1. **the ask** — the human's own words stating that this context is to be adopted end to end,
   quoted verbatim. The authorization is the statement itself, and it is never inferred: a
   request that names one phase gets that entry point, not this one, and an intent read into a
   message that does not state it is a stop. A standing automation the human armed — a goal
   condition naming this skill — is such a statement; this skill deciding on its own that a
   session "meant" the whole route is not.
2. **the project root** — where `siegard.json` lives. Named by the human; inferred rather than
   named, its absence is a stop.
3. **the target** — by the key `siegard.json`'s `targets` names it. Where `targets` declares
   exactly one key and the ask names none, that key is the target: decided and disclosed, never
   asked.
4. **the slug** — the context's name under `siegard-survey/` and `siegard-reconcile/`, named in
   the ask or derived from the context's name and disclosed. A slug whose reconciliation record
   already exists is a resume: this skill continues from the step whose commit the log below
   does not hold, and the report says so.
5. **the areas** — each a short name and the files it holds, in the ask's own words, spelled
   from the target source root as paths or directories. They are `/survey`'s own input, handed
   through unchanged; this skill never widens, narrows or cuts an area. What leaves an area is
   the project's declared tests, which `/survey` reads through `trace.py --area`: the
   declaration narrows it, never this skill.
6. **outside** — optional: the tracked files the ask keeps out of the judgment. Absent, none. A
   declared test is never one of them: it is uncertified until a certification names it.
7. **certifications** — optional: the tests the ask offers as proof of named nodes, in the shape
   `/reconcile` takes. Absent, none; this skill proposes no certification of its own.

Run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/project.py <project-root>` once, before anything else.
Every root answers only from there, exactly as it does for every entry point this skill invokes;
a field the file does not declare is a stop, and the report carries the `/siegard-config`
invocation ready to paste — that skill is closed to model invocation, so the paste is the human's.

Absent inputs stop once, together, so the human answers once — never a question at a time.

## Before anything: the specification, and the tree

Run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/spec.py <specification-root>`, and hold the
specification root to `git status --porcelain`: anything but a clean pass over a committed root
is a stop. An empty root is the ordinary first adoption; a root with pending changes is
somebody's work in progress, and the analysis below would commit it under this run's name.

Before any step, `git status --porcelain -- <specification-root> <target-source-root>
siegard-trace.json siegard-reconcile siegard-survey/<slug>` must print nothing. Output is a stop.

This skill commits where `HEAD` already points and never creates a branch, never pushes, never
stashes: starting the run on a branch cut for it is the human's act, offered in the report's
opening line, which names where `HEAD` stood when the run began.

## This skill invokes `/analyse`, and only inside the ask

Writing the specification from adopted source is this route — «Source no delivery wrote is
adopted, never re-delivered: its facts reach the specification as material» (SPEC-005 R1) — so
this skill invokes `/analyse` where `/deliver-scope` never does. What stands in for the review a
person would give the diff before it is committed is disclosure, mechanical and complete: every
fact line of the material lands in a node or is left out with a reason the ledger records,
«Every fact line of the material lands in a node or is left out with a stated reason» (SPEC-005 R8),
every decided value is an entry of the decision log beside its node, the validator holds the root together, and
the report below lists all of it. A person reviews the commit range afterwards, and
disagreeing with a node is an ordinary `/analyse` change.

What this skill never invokes is `/plan-work`, `/implement-task`, `/review-change` or
`/deliver-scope`: «Adoption changes no source» (SPEC-005 R6). A behavior the adoption finds
wrong is a `contradicts` in the record, relayed whole; the corrective increment is a new ask.

## Read the contract

Read `${CLAUDE_PLUGIN_ROOT}/schemas/ledger.json` — the contract of the file this skill's second
commit adds and its third step reads — and take every remaining answer from
`${CLAUDE_PLUGIN_ROOT}/bin/trace.py`, whose
`--survey`, `--ledger` and `--untraced` runs are the only readings this skill makes of its own
route. Do not re-derive either from memory.

`${CLAUDE_PLUGIN_ROOT}` is set where this skill runs as an installed plugin. Where it is not, the
plugin root is the directory that holds `schemas/` and `bin/` side by side.

## The order

```
gate → survey → commit → analyse → commit → adopt → commit → measure → commit → report → stop
```

Two rules bind every step, and they are what this skill is:

- **Paste, never compose.** Each entry point's report ends with the next invocation ready to
  paste; this skill takes that handoff verbatim and fills only the slots its authorization
  covers — the areas, the outside set and the certifications with the ask's own words, the slug
  with the ask's. It never composes an invocation a report did not hand over, and it never edits
  one beyond its slots. The handoff lives in conversation, and conversation is not state — what
  makes the paste safe is the receiving skill, which rereads every root from disk and stops on
  anything the handoff got wrong; this skill relies on those stops rather than on its own memory
  of what a report said.
- **Every routing decision is a script's answer.** Whether the material holds together, whether
  every fact landed, whether the specification is sound, what the adoption bound and what it
  left: `trace.py --survey`, `trace.py --ledger`, `spec.py`, the fold, `--reconciliation`,
  `--untraced`. A stop a script reports is this skill's stop.

The steps:

1. **Survey.** Invoke `/survey` with the project root, the target, the slug and the areas as the
   ask states them. Its report carries `--survey`'s counts and the `/analyse` handoff.
2. **Commit the material**: `siegard-survey/<slug>` alone, under the message
   `adopt-scope <slug>: survey`. Every commit this skill makes names its paths; none sweeps the
   tree.
3. **Analyse.** Take the `/analyse` invocation from the survey's handoff and invoke it. That
   skill writes the nodes, the decision logs beside them and the ledger, and holds all three
   together; its stop is this skill's stop.
4. **Commit the increment**: the specification root and `siegard-survey/<slug>` — the nodes,
   their logs and the ledger are one increment — under `adopt-scope <slug>: analyse`.
5. **Adopt.** Take the `/reconcile` invocation from the analysis's handoff, fill the outside set
   and the certifications from the ask where it names them, and invoke it. The judges, the fold,
   the record and the bind are that skill's; a return it re-delegates once and refuses again is
   its stop and this skill's.
6. **Commit the adoption**: `siegard-trace.json`, `siegard-reconcile` and
   `siegard-survey/<slug>`, under `adopt-scope <slug>: adopt`.
7. **Measure.** Run `telemetry.py --probe --since <the instant step 1 began>` over the project
   root; announce the read as that script requires; run it. Commit `siegard-telemetry` under
   `adopt-scope <slug>: measure`. A probe that cannot read is a line in the report, never a stop.

**The orchestration log.** After each step, append one line to `orchestration.md` at
`siegard-survey/<slug>/` — what was invoked, the commit that followed by its hash, and the
outcome, one sentence per line. It is a marker, never a node, exactly as `closure.md` is: no
contract holds it, and nothing reads that directory but the files named to `trace.py --survey`
and `--ledger`, so it is committed with the step it records and read by a person. It is the one
place the run's own decisions — the slug derived, the target decided, the step resumed from, the
stop that ended it — survive the conversation that made them.

## What ends the run

Every stop below ends the run with the doors the stopping report already carried, relayed
verbatim, and with the log's last line naming it — and, where that report recommended a door, one
line after it and on a line of its own, «`recommended: <door> — <criterion> — <deciding fact>`»
(SPEC-006 R5): its door and deciding fact copied from the report, and its criterion the name the
handoff's specification gives the ground the report stated in plain words — never a
recommendation the report did not make.
None is worked around, and none is retried:

- a material file `--survey` refuses after the one re-delegation `/survey` makes;
- a specification that does not hold together, or a ledger `--ledger` still refuses after the
  analysis answered every fact line it could;
- a judge's return the fold refuses after the one re-delegation `/reconcile` makes, a record
  `--reconciliation` refuses, or a bind refused;
- a field `siegard.json` does not declare;
- a pending change this skill did not make, anywhere the pathspec above reaches.

What does not end the run, and is relayed whole instead: every `unheld` candidate, every
`contradicts`, `unstated` and `restates` finding, every fact the ledger left out with a reason,
every decision the log gained, and a certification the auditor refused. Each is disclosure, and
the report is where a person reads it.

## Report, and stop

Open as «A handoff opens with what needs the person, and explains after» (SPEC-006 R1)
states; what follows is the report that opening sits above.

Report, in this order: where `HEAD` stood when the run began; every commit this run made, by hash
and message, and the `git log` range that holds them, because the range is the review and it
belongs to a person; every input this skill decided rather than was told — the slug derived, the
target decided, the step resumed from — each disclosed; `--survey`'s counts per area and
`--ledger`'s output verbatim, with every reason a fact was left out, grouped; every decision the
analysis logged, by node and field; the adoption's counts as its report gave them — bound,
`unheld`, `contradicts`, `unstated`, `restates`, certified — and `trace.py --untraced` over the
target after the bind, every state it prints, the uncertified tests among them; the telemetry's receipt; what ended the run, where it ended early, with the
stopping report's doors verbatim and its recommendation where it made one; and what this skill never did — no `/plan-work`, no
`/implement-task`, no repair of any finding, no certification it proposed, no step beyond the
route.

Then stop. The commit range is the review, and it belongs to a person.

## What you never do

- Invoke `/plan-work`, `/implement-task`, `/review-change` or `/deliver-scope` — the adoption
  changes no source, and a wrong behavior it finds is a new ask.
- Invoke `/analyse` over anything but the material this run's survey wrote — the documentation is
  the increment after the adoption, and a person hands it to `/analyse` on its own.
- Widen, narrow or cut an area, name a certification, or decide what is outside — those are the
  ask's words or they are absent.
- Commit without a pathspec, sweep the tree, create a branch, push, stash, or rewrite history.
- Override, soften or skip any stop an entry point raised — its rules bind its invocation whole,
  and this skill's only grant over a stop is to relay it.
