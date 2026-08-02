---
id: concept.analysis-seal
type: term
title: analysis seal
description: What the analysis wrote, recorded per object by something other than the producer, so a later pass can be held to the fields it owns.
status: accepted
contract_version: concept/1
tags: [knowledge, determinism, provenance]
generated: { by: claude-opus-5, at: 2026-08-02T11:45:00Z }
sources:
  - resource: foundation/0004-runtime-architecture.md
    title: Run the framework as capabilities a harness invokes, with determinism at the boundaries
  - resource: docs/adr/0025-one-vocabulary-written-once-where-it-is-read.md
    title: Let the analysis write the knowledge, and stop converting one vocabulary into another
---

# analysis seal

A record of what an analysis wrote, taken per object immediately after it wrote it: a digest of every
field on the analysis's side of the ownership line, the gaps only the domain can close, and the body
headings.

It exists because the pass that comes next may touch four fields and a body and nothing else, and no
tool grant can say that. A grant names tools, not files, and certainly not keys within a file — so the
restriction is prose until something compares the object against what it looked like before.

## Why a record and not a re-derivation

While a deterministic script wrote the objects, "before" was a function: the same inputs yielded the
same bytes, so what had been written was recoverable at any time and nothing had to be kept. That stops
holding the moment the writing is judgment. Two analyses of one request agree in meaning and not in
bytes, and a re-derivation would report every such difference as a later pass overstepping.

A seal also has no input beyond the tree it seals, which a re-derivation did: reproducing an expansion
meant reproducing everything it read, including the [knowledge base](knowledge-base.md), so a change
there between two runs surfaced as a difference nobody had made.

## Who may write one

Not the pass it constrains. A seal the analysis wrote about itself would be a producer reporting its
own compliance, and `foundation/0004` puts validation at the boundary that consumes an artifact rather
than inside the one that produces it. Writing and checking are separate commands for the same reason: a
check able to refresh the baseline it compares against would report success on the change it exists to
catch.

## What it is not

Not a version, and not a copy of the object. It records enough to say **which field moved** and nothing
to reconstruct what the field held — a whole-file digest would answer that something changed while
leaving a reader to find what, and naming the field is what makes a report actionable.
