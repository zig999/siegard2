---
id: "0001"
title: Drive every change through knowledge objects, with determinism at the boundaries
status: accepted
contract_version: spec/1
---

# Knowledge-object-driven development

## Scope

This specification defines the workflow every [change request](../docs/concepts/change-request.md)
follows in a repository Siegard governs, from the request to acceptance. It fixes the phases and their
order, what the framework makes deterministic, what it leaves to model judgment, what context resolution
guarantees, what acceptance requires of a decision and of its evidence, and how a
[knowledge object](../docs/concepts/knowledge-object.md) gains mechanical force over an implementation.

Two things it no longer decides. How the acceptance closure is computed and what the acceptance gate
reports, and how escalation is decided, moved to
`foundation/0014-acceptance-closure-and-escalation.md` when this specification was accepted. R9 and R17
through R20 remain as forwarding entries rather than being renumbered, because renumbering would
redirect an existing citation to a different statement.


### Provenance

This specification derives from the SIGARD v0.1 draft, which it replaces as the design authority and
which carried no normative weight at any precedence level, whatever its own text said about its status.
Three defects in that draft forced the rewrite rather than an edit: a determinism claim whose decisive
steps were natural language, a knowledge-contract check with no definable mechanism, and a phase order
stated in two incompatible ways, one of which contradicted itself.

The draft is no longer in this repository. It was carried in `reference/` until that directory was
removed, and it is recoverable from git history through commit `8744312`, the last commit that contains
it. This paragraph is the anchor for the phrase "the v0.1 draft" wherever this repository still uses it.

**The workflow machinery this document's control flow rested on was removed** — a transition table, a
guard, a replay-derived state, an event contract, and the skill that drove the seven phases
(`docs/adr/0016-remove-the-workflow-machinery.md`). `foundation/0005` R23 then fixed the architecture that
replaces it: Siegard refuses rather than sequences, and order follows from what each capability declares
it requires.

Four requirements here were settled against that, under one principle: **retire what names a component
the framework no longer ships; keep what states a rule the method's actors can still honor.**

| | |
|---|---|
| **R2** | kept, and demoted from a closed control-flow vocabulary to guidance taught through a skill |
| **R5** | retired — it named an orchestrator, and there is none |
| **R7** | kept, with the absence of any enforcing mechanism stated in the requirement itself |
| **R8** | retired — it required a record nothing keeps, and resumption is given up with it |
| **R21** | unaffected, and enforced by promotion plus the scope gate rather than by an acceptance phase |

The method decision is taken here rather than in the framework family, because
`foundation/README.md` states that a framework specification does not amend the method. The architectural
decision the settlement answers to is
`docs/adr/0017-order-follows-from-declarations-not-from-a-sequencer.md`.

The one path that had a caller is now `skills/ingest-domain/`, a straight procedure with no phases and no
event log. It does not satisfy R1: an ingestion originates in received material rather than in a recorded
change request, and nothing yet records one.

### Decided elsewhere, deliberately not restated here

| Question | Authority |
|---|---|
| Which persistence model records workflow state | `foundation/0005` R14 |
| How the distribution is produced and what it excludes | `foundation/0008` R4–R6, R5a–R5c |
| Which component classes exist and what each owns | `foundation/0006` |
| When an artifact requires a versioned schema | `foundation/0005` R16a |
| Security posture, privilege, and untrusted input | `foundation/0005` R11 and R20–R22 |
| The status of a knowledge artifact, and who moves it | the governed repository's own decision |

Two copies of a rule diverge. Where this specification needs one of the above, it cites it.

## The organizing principle

> Determinism at the boundaries, judgment inside the boxes — never the reverse in control flow.

Generating content is model work and always will be. What the framework makes deterministic is what
*decides* something: transitions, validation, context assembly, acceptance. A phase may think; the
edges between phases may not.

The v0.1 draft inverted this. It required an eight-step resolution algorithm to produce identical
output for identical input while stating those steps as instructions to a reader ("identify referenced
domains", "locate root KOs"). A step that cannot be decided mechanically cannot carry a determinism
guarantee, and declaring one anyway is the defect this specification exists to correct.

## Definitions

Terms used normatively below. Each is defined once, in the concept bundle.

| Term | Concept |
|---|---|
| change request | [change-request](../docs/concepts/change-request.md) |
| impact analysis | [impact-analysis](../docs/concepts/impact-analysis.md) |
| knowledge object | [knowledge-object](../docs/concepts/knowledge-object.md) |
| knowledge graph | [knowledge-graph](../docs/concepts/knowledge-graph.md) |
| context package | [context-package](../docs/concepts/context-package.md) |
| specification delta | [specification-delta](../docs/concepts/specification-delta.md) |
| assertion | [assertion](../docs/concepts/assertion.md) |
| escalation | [escalation](../docs/concepts/escalation.md) |
| fail-soft | [fail-soft](../docs/concepts/fail-soft.md) |
| provenance | [provenance](../docs/concepts/provenance.md) |
| accepted | [accepted](../docs/concepts/accepted.md) |
| specification | [specification](../docs/concepts/specification.md) |

## The default path

```
change request → impact analysis → context resolution → specification delta
                                                              │
       acceptance ← validation ← implementation ←─────────────┘
```

Seven phases. Impact analysis is on the default path because it *is* the decision function for
escalation, and because classifying a request against the graph is cheap: it reads knowledge, it does
not author it. What scales with a request's weight is the authoring that follows a verdict other than
`none`.

Where v0.1 had four phases, one of them carried three hidden responsibilities. Naming seven is not
added ceremony; it is the same work, counted honestly.

## Escalation

Escalation inserts phases. It is decided by predicates over fields of validated artifacts, never by an
agent's judgment about how big a change feels.

| Trigger | Predicate | Inserts |
|---|---|---|
| permanent knowledge changes | `impact.verdict ∈ {update, create}` | knowledge authoring and review |
| an architectural decision is implicated | `impact.adr_ids ≠ ∅` | ADR review by a maintainer |
| regulatory change | `request.type = regulatory` | the full path, with a reinforced acceptance gate |
| more than one domain | `distinct(domain(ko) : ko ∈ impact.ko_ids) > 1` | an explicit specification delta and plan |
| large scope | `\|impact.ko_ids\| ≥ N` or affected-path count `≥ M` | detailed planning |

The predicates are stated over the fields an artifact contract defines. Where a contract does not yet
exist, the predicate names the field that contract must define.

A validation failure is absent from this table on purpose: it is a return edge of the state machine,
not a phase. Mixing the two confuses control flow with workflow composition.

## Fail-soft

Context resolution degrades rather than blocks, and acceptance is evaluated independently of what the
implementer read. The claim is calibrated, and the calibration is the point:

> Fail-soft guarantees that acceptance is evaluated **independently** of the context the implementer
> consumed. The strength of that evaluation is mechanical where the impacted knowledge object carries
> an [assertion](../docs/concepts/assertion.md), and independent review where it does not. The
> acceptance gate reports which of the two applied.

Independent review is mitigation, not a guarantee. A framework that called it one would be claiming a
property no mechanism delivers.

## The maturity ladder

Guarantees grow with a project's maturity. Without mechanics, that sentence means "we will add tests
one day", so the mechanics are stated here.

| Level | What the knowledge object is | What it binds | Cost to reach |
|---|---|---|---|
| 0 | prose, `proposed` | nothing; it enters context only | minutes |
| 1 | prose, `accepted` | enters the graph and selection; agents read it; binds **review** | an approval |
| 2 | `accepted` plus an assertion | **mechanical rejection** at validation | one test |

Level 1 is the normal and permanent state of most knowledge objects. It is not debt. What matures the
system is that promotion to level 2 is *demand-pulled*, by a recorded event:

- a validation failure traced to this knowledge object — the regression already happened, so guard it;
- a production incident attributed to the rule;
- the knowledge object is cited by a change request whose `type` is `regulatory`;
- an implementation violated it and review caught the violation — what was violated once will be again;
- a maintainer designates it critical.

Assertions accumulate over exactly the rules that are actually violated, which is where they pay for
themselves. Coverage grows without anyone running an assertion project.

**The consequence, chosen with open eyes.** If no assertion is ever demanded, this design converges to
"well-organized context plus independent review" — a genuinely useful product that addresses the
diagnosed bottleneck. But the normative inversion, code as a manifestation of knowledge, does not
happen, because nothing can reject an implementation for violating a knowledge object. The ladder makes
that outcome visible over time instead of surprising at the end.

## Requirements

### Control flow

- **R1** — Every change to a governed repository originates in a change request. No phase runs without
  one.
- **R2** — The default path is: change request, impact analysis, context resolution, specification
  delta, implementation, validation, acceptance. It is the order the work follows, and it is **guidance
  rather than a control-flow vocabulary**. What fixes an order is what each capability declares it
  requires — `foundation/0005` R10 and `foundation/0007` R24 — and this path is taught to the executor
  through a skill rather than enforced by a component the framework ships. Escalation inserts steps; it
  never removes one.

  An earlier form of this requirement said the path was *exactly* that sequence in that order, and made
  the seven names a closed vocabulary that a persisted event branched on. That vocabulary went with the
  machinery that read it, and restating the order as a closed enum would now describe a mechanism nothing
  implements. The order itself is unchanged and still worth following; what changed is what makes it
  hold.
- **R3** — Impact analysis runs for every change request, including one whose verdict turns out to be
  `none`.
- **R4** — Impact analysis produces a validated artifact carrying a verdict from the closed set
  `none | update | create`, and naming every implicated knowledge object and ADR by identifier.
- **R5** — Retired. It required an orchestrator to choose a transition by lookup on a closed field, and
  the framework ships no orchestrator: `foundation/0005` R23 states that Siegard refuses rather than
  sequences, and R3 there puts sequence with the executor. The number is retained rather than reused so
  that a citation of R5 still resolves to the statement it named. What survives of it is R6 below, which
  needs no orchestrator to bind: an artifact that fails its contract is rejected. The rule against
  deciding anything by interpreting prose survives as `foundation/0005` R6.
- **R6** — An artifact that fails its contract at the boundary is rejected, never repaired.
- **R7** — A validation failure returns the work to implementation under a stated attempt limit, and the
  knowledge object of the failed check enters the next context resolution as a mandatory root. Exhausting
  the limit is a terminal outcome that reports the failure; it is never an acceptance.

  **No mechanism enforces this.** The limit depended on a record of how many attempts had already
  happened, and the framework keeps no such record — `foundation/0005` R23. It is kept rather than retired
  because it states what the method requires of whoever does the work, and a maintainer can honor it; what
  it no longer is, is a guarantee. Where it returns as one, it returns as a refusal at a boundary and not
  as a component that counts attempts on the framework's behalf.
- **R8** — Retired. It required workflow state persisted outside the conversation and every transition
  reconstructible from persisted records alone. Both presume that the framework holds workflow state and
  chooses transitions, and `foundation/0005` R23 states that it does neither; R14 there is retired for the
  same reason. The number is retained rather than reused. What is given up with it is **resumption**: work
  interrupted halfway leaves no record of where it stopped, and nothing can reconstruct it. That is a real
  loss and it is recorded here rather than in the framework family, because whether the method needs
  resumption is a method question.

  R15 of `foundation/0005` is unaffected and still binds: a recorded decision names its inputs, its
  artifact, and its contract version, so a later reader can reproduce it without the session that made it.

### Escalation

- **R9** — Moved to `foundation/0014-acceptance-closure-and-escalation.md` R1 when this specification was
  accepted, because no escalation predicate existed to satisfy the condition that covered it. The number is
  retained rather than reused so that a citation of R9 still resolves to the statement it named.
- **R10** — A numeric threshold in an escalation predicate is calibrated from executed workflows and
  recorded together with the evidence that calibrated it. A threshold asserted without that evidence is
  not a valid escalation predicate.

### Context resolution

- **R11** — Context resolution produces a context package that is a manifest of identifiers and content
  hashes, not copies of the artifacts it names.
- **R12** — Root selection is model judgment, and each selected root is recorded with the claim that
  justifies it. Expansion is deterministic: the same roots, the same graph, and the same budget produce
  a byte-identical manifest.
- **R13** — Context resolution never blocks the workflow. Where it cannot satisfy a selection rule —
  a root it cannot locate, a cycle it cannot resolve, contradictory knowledge, an exhausted budget — it
  records the degradation in the context package and continues.
- **R14** — A recorded degradation is an input to acceptance, and the acceptance gate names it.
- **R15** — Resolution never invents a knowledge object to fill a gap. A concept the graph does not
  hold is reported as a gap in permanent knowledge.
### Specification delta

- **R16** — A specification delta describes only the requested change, and references knowledge objects
  and ADRs by identifier rather than restating their content.

### Acceptance

- **R17** — Moved to `foundation/0014-acceptance-closure-and-escalation.md` R2. The number is retained rather
  than reused so that a citation of R17 still resolves to the statement it named.
- **R18** — Moved to `foundation/0014-acceptance-closure-and-escalation.md` R3, with R17 above: the two are one
  closure and neither is testable without the other.
- **R19** — Moved to `foundation/0014-acceptance-closure-and-escalation.md` R4, because no acceptance gate exists
  to report a mode.
- **R20** — Moved to `foundation/0014-acceptance-closure-and-escalation.md` R5, with R19 above: what the gate may
  not present as a guarantee is meaningless where no gate reports anything.
- **R21** — Acceptance requires a maintainer's decision, or a deterministic approval mechanism the
  governed repository defines. No workflow accepts its own output.

  **This holds, and it is enforced.** It was counted among the guarantees the removal gave up, and that
  was wrong: it is a refusal rather than a sequence, and the framework still performs it. A knowledge
  object derived from existing material is born `proposed` under R26 and only a maintainer promotes it,
  and `foundation/0004` R54 makes a generation scope compile accepted knowledge only — so nothing the
  framework runs can accept its own output and then build on it. What is gone is the *acceptance phase*
  that recorded the decision, not the requirement that a decision be someone's.
- **R22** — Validation produces evidence that records what ran, its result, and the inputs needed to
  reproduce it. An acceptance with no evidence is a defect, not a fast path.

### Knowledge maturity

- **R23** — A knowledge object at level 0 binds nothing; at level 1 it enters the graph and selection
  and binds review; at level 2 it binds mechanical rejection at validation. The level is derived from
  the artifact — its status and whether an assertion references it — never declared separately.
- **R24** — An assertion is never required to author or to accept a knowledge object. Promotion to
  level 2 is demand-pulled by a recorded trigger.
- **R25** — Assertion coverage is observability. No gate, threshold, or acceptance criterion is
  expressed as a coverage figure.
- **R26** — A knowledge object derived from existing code is born `proposed`, records provenance naming
  the source it was read from, and requires a maintainer to promote. Deriving knowledge from code
  cannot canonize a defect as a rule.

## What this specification does not decide

Deferred deliberately, because a contract written ahead of the code that needs it is a guess that reads
like a requirement:

- the schema of any individual artifact — impact analysis, context package, specification delta,
  evidence, event — each arrives with the phase that produces it;
- the knowledge object frontmatter contract, including how an assertion references its knowledge
  object;
- the expansion algorithm's depth and budget parameters, and the selection instrumentation that shows
  whether resolution outperforms sending the whole bundle;
- the values of `N` and `M` in R10, which R10 forbids inventing here;
- the layout a governed repository uses for these artifacts, and how the distribution installs it;
- knowledge derived from code as a capability: R26 constrains it, and nothing here requires it to exist.

