---
id: "0001"
title: Start every change from a recorded request, and say what it touches before touching it
status: accepted
contract_version: spec/1
---

# The method

## Scope

What a repository governed by Siegard does when it changes: what a change starts from, what must be
established about existing knowledge before anything is altered, and what an authored knowledge object
records about the material it came from.

Not here: how a request is analysed into a domain model (`foundation/0002`), or how the analysis is
stored (`foundation/0003`).

## Requirements

### The request

- **R1** — Every change to a governed repository originates in a recorded request. The request states
  what is wanted and names the material it was read from, so that a later reader can check an analysis
  against the ask.
- **R2** — A request is not itself a contracted artifact of this framework. No capability produces one,
  and a capability that consumes one takes its statement and its referenced material as inputs.

### Impact

- **R3** — Impact analysis runs for every request, including one whose verdict is `none` and one made
  where nothing exists yet.
- **R4** — Impact analysis produces a validated artifact carrying a verdict from the closed set
  `none | update | create`, and naming every implicated element by its identifier.
- **R5** — Impact analysis records whether anything existed to implicate. A request made where nothing
  exists yields `create` against an empty state, which is a different outcome from `none` and MUST NOT be
  reported as one.
- **R6** — Impact analysis decides what a change touches and nothing else. It does not author, does not
  alter what it analysed, and does not decide whether the change should happen.

### Classification

- **R7** — Every construct MUST be classified before any knowledge object is authored. Classification
  produces a validated artifact naming, per construct, the node type it becomes, the identifier it will
  take, and every fact the analysis does not supply.
- **R8** — Classification decides node type and identity. It does not decide what the domain is, and it
  MUST NOT re-open a decision the analysis recorded.
- **R9** — A fact the analysis does not supply is reported as a gap on the construct it belongs to, with
  what would fill it. Nothing fills a gap on the domain's behalf.
- **R10** — A construct the ontology has no home for is recorded as unmapped rather than forced into the
  nearest node type.

### Authoring

- **R11** — A knowledge object authored from analysed material records provenance naming the material it
  was read from. The knowledge base holds one statement of each fact, and that statement is current: no
  maturity level, approval state, or retired revision is recorded on a knowledge object.
- **R12** — No capability validates or approves its own output. A check a producer runs over what it
  produced establishes nothing, and validation happens at the boundary that consumes the artifact.

### Boundaries

- **R13** — An artifact that fails its contract at a boundary is rejected, never repaired, and nothing
  consumes it while the failure stands.
- **R14** — A capability MUST NOT report success on work it did not complete. Where it completed part, it
  reports the failure and what was produced.
