---
id: "0001"
title: Drive every change through knowledge objects, with determinism at the boundaries
status: proposed
contract_version: spec/1
---

# Knowledge-object-driven development

## Scope

This specification defines the workflow every [change request](../docs/concepts/change-request.md)
follows in a repository Siegard governs, from the request to acceptance. It fixes what the framework
makes deterministic, what it leaves to model judgment, how a workflow escalates, how acceptance is
evaluated, and how a [knowledge object](../docs/concepts/knowledge-object.md) gains mechanical force
over an implementation.

It governs the framework Siegard ships. It does not govern this repository's own development process,
which `CLAUDE.md` defines.

### Provenance

This specification derives from the SIGARD v0.1 draft in `reference/`, which it replaces as the design
authority and which carries no normative weight at any precedence level, whatever its own text says
about its status. Three defects in that draft forced the rewrite rather than an edit: a determinism
claim whose decisive steps were natural language, a knowledge-contract check with no definable
mechanism, and a phase order stated in two incompatible ways, one of which contradicted itself.

### Decided elsewhere, deliberately not restated here

| Question | Authority |
|---|---|
| Which persistence model records workflow state | undecided; `CLAUDE.md` **Determinism and state** bounds it |
| How the distribution is produced and what it excludes | `.claude/rules/distribution.md`, `CLAUDE.md` **Repository layout** |
| Which component classes exist and what each owns | ADR-0009 for the contracts; the taxonomy is undecided |
| When an artifact requires a versioned schema | `.claude/rules/contracts.md` |
| Security posture, privilege, and untrusted input | `CLAUDE.md` **Security** |
| The status vocabulary and who may change a status | `docs/adr/README.md` |

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
| transition guard | [transition-guard](../docs/concepts/transition-guard.md) |
| projection | [projection](../docs/concepts/projection.md) |
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
- **R2** — The default path is exactly: change request, impact analysis, context resolution,
  specification delta, implementation, validation, acceptance, in that order. Escalation inserts
  phases; it never removes one.
- **R3** — Impact analysis runs for every change request, including one whose verdict turns out to be
  `none`.
- **R4** — Impact analysis produces a validated artifact carrying a verdict from the closed set
  `none | update | create`, and naming every implicated knowledge object and ADR by identifier.
- **R5** — An orchestrator chooses a transition by lookup on a closed field of an artifact that passed
  its contract at the boundary. It never chooses a transition by interpreting prose.
- **R6** — An artifact that fails its contract at the boundary is rejected, never repaired.
- **R7** — A validation failure returns the workflow to implementation under a stated attempt limit,
  and the knowledge object of the failed check enters the next context resolution as a mandatory root.
  Exhausting the limit is a terminal outcome that reports the failure; it is never an acceptance.
- **R8** — Workflow state is persisted outside the conversation, and every transition is
  reconstructible from persisted records alone. Conversation history and auto memory are not records.
  Which persistence model satisfies this is not decided by this specification.

### Escalation

- **R9** — Escalation is decided by predicates over fields of validated artifacts. No predicate reads
  prose, and no agent decides whether to escalate.
- **R10** — A numeric threshold in an escalation predicate is calibrated from executed workflows and
  recorded together with the evidence that calibrated it. A threshold asserted without that evidence is
  not a valid instantiation of R9.

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

- **R17** — The set of checks that decides acceptance is computed from the impact artifact, the
  knowledge graph, and the actual diff. It is never computed from the context package the implementer
  consumed.
- **R18** — The validation closure covers every knowledge object the diff touches, whether or not the
  impact artifact named it. Declared impact and observed diff are unioned, so independence does not
  leak when an implementation touches a path outside its plan.
- **R19** — The acceptance gate reports, for each impacted knowledge object, the mode that decided it:
  `mechanical` where an assertion exists, `review` where none does. Every gap is named.
- **R20** — Fail-soft guarantees independence of evaluation, not correctness of implementation. Where no
  assertion covers an impacted knowledge object, acceptance rests on independent review. A report that
  presents review as a guarantee is a false report.
- **R21** — Acceptance requires a maintainer's decision, or a deterministic approval mechanism the
  governed repository defines. No workflow accepts its own output.
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

## Validation required before acceptance

This specification presupposes components that do not exist. It binds nothing until:

1. a maintainer accepts it;
2. the knowledge-only path — change request, impact analysis, knowledge authoring, validation,
   acceptance — runs end to end in a fixture under `fixtures/`, with each transition chosen by lookup
   on a validated artifact (R5);
3. one escalation predicate is decided by a script or hook against a validated artifact, with a test
   covering both outcomes (R9);
4. a test shows the validation closure exceeding the context closure for a change where the two differ,
   which is what makes R17 and R18 falsifiable rather than aspirational;
5. the acceptance gate reports the mode of each impacted knowledge object, and a test asserts that a
   knowledge object with no assertion is reported as `review` rather than as passing (R19, R20).

If building the knowledge-only path shows that a phase in R2 is ceremony for the workflows the
framework actually runs, narrow the path before accepting this specification.
