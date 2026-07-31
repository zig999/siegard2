---
id: "0004"
title: Produce the system from knowledge, and lock what reproduces it
status: accepted
contract_version: spec/1
---

# Generation and reproducibility

## Scope

This specification fixes how software is produced from the knowledge a repository Siegard governs holds, and
what "the same knowledge produces the same system" guarantees. It decides six things:

1. the calibrated promise — which artifacts carry byte identity, which carry behavioural conformance, and
   what a reproducibility claim must name;
2. the closed vocabulary of [artifact classes](../docs/concepts/artifact-class.md), and how a
   [target pack](../docs/concepts/target-pack.md) declares which classes it produces on which
   [track](../docs/concepts/generation-track.md);
3. the three derived artifacts between knowledge and source — the
   [scope](../docs/concepts/generation-scope.md), the [plan](../docs/concepts/generation-plan.md), and the
   [manifest](../docs/concepts/generation-manifest.md) — why none of them is an authored rule language, and
   the one judged input they need: the [placement decision](../docs/concepts/placement-decision.md) that
   supplies a target path the manifest does not yet hold;
4. [generative completeness](../docs/concepts/generative-completeness.md) as a blocking validation;
5. how produced and hand-authored source bind back to the knowledge that justifies them;
6. the [persistence](../docs/concepts/artifact-persistence.md) of every artifact it names — which are
   committed, which are recomputed, and what a claim must record for the ones that are not kept.

It **derives from `specs/0002-knowledge-economy-principles.md`**, which decides what knowledge is worth
holding, and from **`specs/0003-knowledge-ontology-and-notation.md`**, which decides how it is represented.
Both are cited here rather than repeated.

It does not restate spec 0001's workflow. Where this specification's validations run inside that workflow,
it names the requirement of 0001 that governs.

It governs the framework Siegard ships. It does not govern this repository's own development process, which
`CLAUDE.md` defines.

### The premise this specification rests on, now settled

Whether a target pack is framework work at all rested on `CLAUDE.md` **Scope**, which excludes "architecture
chosen for one downstream system" and did not say whether a technology pack is that. A maintainer settled it
on 2026-07-30: a target pack is not that architecture, and `specs/0005` R4
**Target packs** holds the distinction and the fixture gate that keeps it honest.

R12 through R18 therefore rest on an accepted rule rather than on a presumption. What remains open is not the
premise but the evidence: no pack exists, so nothing has exercised any of them.

### Decided elsewhere, deliberately not restated here

| Question | Authority |
|---|---|
| What knowledge is worth holding, and the domain/stack boundary | spec 0002 |
| The representation ratio, and why it is not a gate | spec 0002 R7–R8 |
| The ontology, the notation, the type system, and the knowledge layout | spec 0003 |
| The workflow every change request follows | spec 0001 |
| That context resolution degrades rather than blocks | spec 0001 R13–R15, [fail-soft](../docs/concepts/fail-soft.md) |
| The maturity ladder, and what an assertion binds | spec 0001 R23–R26 |
| Which component classes exist; that there is no command class | `specs/0006` |
| The frontmatter contract of a distributable agent or skill | `schemas/agent.v1.json`, `schemas/skill.v1.json` |
| That a generated tree is never hand-edited, and that hidden defaults are rejected | R7 below; `specs/0005` R16b |
| What makes a change breaking | `specs/0013` R3a |

Two copies of a rule diverge. Where this specification needs one of the above, it cites it.

## The calibrated promise

"The same knowledge produces the same system" is achievable in a calibrated form. Stating it without the
calibration would repeat the defect spec 0001 exists to correct: a determinism guarantee resting on steps no
mechanism decides.

Reproducibility comes from **locking**, not from authoring. The pack decides where a produced artifact goes,
because placement is stack knowledge that spec 0002 R4 keeps out of the knowledge base — and where a model
makes that decision it cannot be relied on to decide identically twice. The manifest records the decision
once, and every later run obeys the record. The pattern is a dependency lockfile's.

| | first generation of an artifact | regeneration under lock |
|---|---|---|
| Target path | the placement decision of R52 supplies it; the manifest records it | read from the manifest; not decided again |
| Content, `deterministic` class | template expansion over structured knowledge | **byte-identical** |
| Content, `judged` class | the class's agent authors it | verified against the generated conformance suite |
| What a diff means | a new entry is expected to vary | any variation in a locked entry is a finding |

Three consequences are stated rather than left implicit.

**A reproducibility claim names four pinned identities**: the knowledge base version, the generation scope,
the target pack version, and the manifest. A claim omitting any of the four is not a reproducibility claim,
because each of the four changes the output.

**The judged track guarantees conformance, not identity.** Two runs may produce different source that passes
the same generated suite. That is the same software at the level of observable behaviour and false at the
level of text.

**The trade is explicit.** An earlier design derived placement from an authored ruleset and could claim byte
identity from the first run. This one claims it from the second. What the concession bought is the removal of
a rule language: a rule language for placement is paid on every change, and a lock is paid once.

## Artifact classes and what a pack declares

Which node type produces which kind of source is stack knowledge, and the specialized agent holds it. Two
things are nevertheless declared, because verification depends on them and an agent's knowledge is not
observable.

**The class vocabulary is closed and belongs to this specification.** It names what a produced artifact *is*,
never how a technology expresses it:

| Artifact class | What it is |
|---|---|
| `type` | the in-language representation of a definition |
| `dto` | a transfer representation crossing a boundary |
| `persistence-schema` | tables, columns, constraints, indexes |
| `migration` | the ordered change from the previous persistence schema |
| `enum` | a closed value set |
| `state-machine` | states, transition dispatch, illegal-transition rejection |
| `validator` | executable enforcement of a rule |
| `conformance-test` | a test derived from examples or from lifecycle totality |
| `event-schema` | the payload contract of an interface |
| `api-description` | the machine-readable description of an exposed interface |
| `orchestration` | the coordination skeleton of a process |
| `documentation` | a human-readable projection of knowledge |

**A pack declares its capability, and nothing more.** This is the whole of it:

```yaml
pack: kotlin-spring
version: 1.4.0
produces:
  - { class: type,               track: deterministic, from: [definition] }
  - { class: persistence-schema, track: deterministic, from: [definition] }
  - { class: migration,          track: deterministic, from: [definition] }
  - { class: enum,               track: deterministic, from: [definition] }
  - { class: state-machine,      track: deterministic, from: [lifecycle] }
  - { class: conformance-test,   track: deterministic, from: [rule, lifecycle] }
  - { class: validator,          track: judged,        from: [rule] }
  - { class: orchestration,      track: judged,        from: [process] }
```

Eight lines of declaration in place of an authored ruleset. What the declaration buys, and what could not be
read off an agent's prompt: a class outside the vocabulary is rejected, the track of every class is known
before anything runs, and a node type yielding nothing under the active pack is **reported** rather than
silently uncovered.

**`from` is the third column, and an earlier draft omitted it.** That draft declared only the class and the
track, and R14 said the declaration holds nothing else, while `specs/0012` R6 assigned the node-type-to-class
mapping to the pack and `specs/0012` R7 left it in the agent's own competence. R23 then derived the plan from
the scope, this declaration, and the manifest, with no model in the loop — so nothing in the plan's declared
inputs could answer *which artifacts a knowledge object demands*. The plan was model-free and incomplete at
the same time. R11 was already unsatisfiable for the same reason: a node type yielding no class cannot be
reported by anything that cannot enumerate what each type yields.

`from` is the smallest input that closes it. It is not what R14's exclusion protects — a mapping from a node
type to an artifact class names no directory, no filename, and no storage representation, and `specs/0012`
R6 already put it in the pack rather than in the framework. R10 still holds unchanged: *this specification*
fixes no mapping, because the mapping presumes a technology and the pack is where a technology may be
presumed.

What remains deliberately absent: naming conventions, directory layout, path derivation, expansion order, and
the mapping from a reference to a storage representation. Each is stack knowledge, each already lives in the
agent, and each would be maintenance cost with no differentiating content — the economy spec 0002 protects.

Two classes were considered and cut. `module-layout` is precisely the stack knowledge spec 0002 R4 excludes,
and `client-stub` added nothing `api-description` does not already carry.

## The target pack

A target pack is the specialized agents and templates that produce the classes it declares, distributed
together under `src/claude/`. Each agent conforms to `schemas/agent.v1.json` and enumerates its tool grant,
per ADR-0009 and [least privilege](../docs/concepts/least-privilege.md). The entry point that runs
generation is a [skill](../docs/concepts/skill.md), because ADR-0009 records that there is no command class.

**Composition follows the declaration, and an earlier draft of this section did not.** It said a pack is
*one* specialized agent and the templates it expands, which cannot be reconciled with `specs/0006` R5 — a
specialized agent produces exactly one artifact class — for any pack declaring two judged classes. The
example declaration below declares two, `validator` and `orchestration`, so the contradiction was not
hypothetical: this document's own example could not be built by a conforming pack. The composition rule is
therefore derived from the declaration rather than fixed at one agent, and R51 makes the correspondence
exact.

The alternative repair was to keep one agent and forbid a pack from declaring more than one judged class.
It is recorded here as considered and rejected: it forces one stack to be served by several packs, which
R12's single active pack then makes unreachable, and it buys nothing the producer-cardinality check does
not already give.

Exactly one pack is active in a governed repository. One pack is what lets a template assume its technology
instead of abstracting over it, which is where the deterministic track gets its width, and it is consistent
with `specs/0005` R4 forbidding a vendor-neutral abstraction absent an accepted
requirement.

The framework ships no default pack. A missing or ambiguous pack blocks generation and is reported, because
`specs/0005` R16b rejects a hidden default and a pack inferred at run time is the largest
hidden default available.

## The generation model

Three derived artifacts. None is authored, and none is a rule language.

```text
knowledge graph ─┐
                 ├──→ generation scope ─┐
roots ───────────┘   (closed, frozen)   │
                                        ├──→ generation plan ──→ execution ──→ source
target pack declaration ────────────────┤   (derived, validated)              + manifest
manifest (the lock) ────────────────────┤
placement decision ─────────────────────┘
(judged, validated, frozen —
 new target paths only)
```

### The scope — derived, frozen, fail-closed

Nobody generates everything. A project generates a bounded context, an aggregate, a feature, or a change, so
a reproducibility claim over the knowledge base is ambiguous until the compiled subset is named.

A scope is a closed set of knowledge-object ids with content hashes, derived by expansion from declared roots
over the edges spec 0003 marks as traversed, then frozen. After freezing, a change to any member invalidates
the scope rather than quietly altering what is compiled.

A scope resembles a [context package](../docs/concepts/context-package.md) and differs on the axis that
matters most:

| | context package | generation scope |
|---|---|---|
| Purpose | what an implementer may read | what is compiled |
| Unresolvable member | a recorded degradation; resolution continues | **blocks**; nothing is generated |
| Failure semantics | fail-soft, per spec 0001 R13 | fail-closed |
| Identity | advisory manifest | part of the reproducibility identity |

Conflating the two would carry fail-soft into generation, and a generation that degrades quietly produces
less software than was asked for with no signal.

### The placement decision — where judgment becomes a lock

Placement is stack knowledge and an agent decides it, which is the concession **The calibrated promise**
already records. What that section left implicit is *when* the decision enters, and the omission made the
plan impossible to derive for a first generation. The plan must know a new entry's target path — R25
detects collisions before any write, and a collision between two new entries is the case worth catching —
while R23 admits no model into the derivation. A path the manifest does not yet hold has only one source,
and that source is a model.

The [placement decision](../docs/concepts/placement-decision.md) is that source, made explicit and made an
input. For the entries the manifest does not lock, the pack proposes a target path per entry; the proposal
is validated against the pack's declaration, the closed class vocabulary, path safety, and the repository
boundary; and the validated result is **frozen** before the plan is derived. From there the derivation is
the model-free function R23 describes, over four inputs rather than three.

*Which* producer inside the pack proposes a path is left open, and the reason is worth being explicit
about. A judged class has an agent that can decide one. A deterministic class has a template, and a
template cannot judge — but `specs/0011` R12 already puts naming and layout inside the template, so a pack
may well derive a deterministic class's path rather than propose it, which would give that class byte
identity from the first run instead of the second. Both designs satisfy every requirement here, they differ
in what the first run promises, and choosing between them without a pack to try them on is the guess this
specification's **What this specification does not decide** exists to refuse.

The gain is that the one judged step in an otherwise deterministic pipeline is a named, validated,
inspectable artifact instead of an unstated assumption. What it does not buy is byte identity for a first
run: two first generations over the same knowledge may place the same artifact differently, and that is the
same trade the calibrated promise already made. Identity begins at the second run, where R31 reads the path
back rather than asking again.

An authored placement ruleset shipped by the pack was considered and rejected. It would produce byte
identity from the first run, and it is precisely the rule language **The calibrated promise** removed: a
placement grammar is paid on every change to the stack, a lock is paid once, and R14 excludes path
derivation from the declaration for that reason.

### The plan — derived, inspectable before any write

The plan is a consequence, not a design. It is derived from the scope, the pack's declaration, the manifest,
and the frozen placement decision, and it exists for four reasons: audit, validation before execution,
incremental execution, and reproducibility.

Each entry names the knowledge object, the artifact class, the track, the target path, and whether the entry
is **locked** — a path already in the manifest — or **new**, in which case the path came from the frozen
placement decision. That flag is what lets a diff distinguish expected variation from a finding.

The plan is validated **before any file is written**: every reference resolves, every class is in the
vocabulary and in the pack's declaration, no two entries claim one target path, and every locked path still
exists. A plan that fails validation is rejected, never repaired, and a plan may be produced and inspected
without writing anything.

A target-path collision is a **defect to report**, not a conflict to resolve by policy. Two objects competing
for one path is a modelling error or an agent error, and a policy that silently picked a winner would hide
both.

Because no model participates in the derivation itself, plan determinism is testable on its own — cheaper
and sharper than diffing produced source, and independent of whether any template is correct. The judgment
the placement decision carries is upstream of the derivation and frozen before it runs, so it is one of the
four inputs held fixed by the test rather than a source of variation inside it.

### The manifest — the lock

The manifest records, for each produced artifact, the knowledge object, the artifact class, the target path, a
content hash, and the pack version that produced it. It locks placement and records execution, and it decides
nothing.

Moving a produced file is an explicit recorded unlock, never a consequence of an agent choosing differently on
a later run. Without that rule a relocation appears in a diff as a deletion and an addition, indistinguishable
from a change in knowledge.

## Artifact persistence

Which of the three derived artifacts is kept was left open by an earlier draft of this specification, and
leaving it open makes two conforming implementations disagree about whether a manifest survives a run. R31
requires the manifest to be read on every later run, which implies persistence without stating it, and nothing
was said about the scope or the plan at all.

Persistence, normativity, and derivation are three axes, not one. This section fixes the first. The second is
already fixed where it needs to be — R33 states that the manifest decides nothing, and
`specs/0003-knowledge-ontology-and-notation.md` R51 states that a projection is never normative. The third is
fixed per artifact by R23 and R30.

A two-value split into permanent knowledge and disposable execution output was considered and rejected. It
collapses the three axes, and produced source — every artifact class this specification names — has no slot in
it. This repository already holds artifacts that are derived and committed at once: `dist/.claude/` is
assembled from `src/claude/` and compared against the committed tree by `make dist-check`, and
`knowledge/index.md` and `knowledge/graph.json` are generated. Derived has never implied disposable.

**The rule that assigns the value**, rather than a table asserting one per artifact:

> An artifact's persistence follows from whether its body is recomputable from committed inputs with no model
> involved, and from whether anything outside the run pins its identity.

| Value | Recomputable from committed inputs, without a model | Identity pinned outside the run | What it means |
|---|---|---|---|
| `run-scoped` | yes | no | exists for the duration of one run; never committed |
| `claim-recorded` | yes | yes | not committed; the claim records its declared inputs and the content hash of its frozen body, and the body recomputes |
| `committed` | no | yes | records a decision no committed input determines; kept in version control |

The rule is what makes the assignment derivable instead of asserted, and it is why the manifest and the plan
land on opposite sides despite both being derived.

| Artifact | Persistence | Why the rule yields this |
|---|---|---|
| generation scope | `claim-recorded` | Expansion is deterministic under R19, so the members recompute from the declared roots and the knowledge base version, both of which R4 already pins. Recording the frozen content hash makes R20's invalidation mechanically checkable rather than only stated. |
| generation plan | `run-scoped` | R23 derives it, R28 makes it byte-identical for identical inputs, and R26 makes it producible without writing a file. No model participates, and nothing outside the run reads it. |
| generation manifest | `committed` | It records placement, which `specs/0002-knowledge-economy-principles.md` R4 excludes from the knowledge base and which a specialized agent decides. No committed input determines it. R4 names it as a pinned identity, R31 reads it on every later run, R32 requires a recorded unlock to move a file, R35 needs a locked entry to attribute a difference, and R42 and R44 answer reverse impact from it. |
| produced source | `committed` | Verification compares against the committed tree, and judged-track content is model-authored, so it is not recomputable byte-for-byte. |
| target pack declaration | `committed` | Authored, versioned, and distributed under `src/claude/` per R13. |
| placement decision | `run-scoped` | The one entry the rule does not yield on its own — see below. A model produces it, so the rule reads `committed`; the manifest is what actually keeps the decision, and committing both would create the second authority for placement that R50 exists to prevent. |

**The placement decision is the rule's one refinement, and it is narrow on purpose.** Its body is
model-produced, so the rule as stated lands it on `committed`. Committing it would put the same fact in two
places: R30 already requires the manifest to record the target path of every produced artifact, and R31
makes the manifest the thing every later run reads. Two records of one decision drift, and the drift would
be between a lock and a proposal — the worst pair to have disagree.

What licenses the exception is that the run *transcribes* the decision into a committed artifact before it
ends. R53 states the conditions, and they are the ones that make the transcription trustworthy rather than
convenient: the committed artifact is named, the transcription happens in the same run, and a run that fails
before writing locks nothing. Without the last condition the manifest could hold a path for a file that was
never produced, which R25's "every locked path still exists" would then reject on the next run.

Discarding the manifest was the one reclassification this section exists to refuse. Placement has exactly
three possible sources: the knowledge base, which `specs/0002` R4 forbids; a persisted manifest; or the agent,
on every run, which cannot be relied on to decide identically twice. Closing the first two leaves only the
third, and byte identity is then unobtainable.

The persistence of the artifacts `specs/0001-knowledge-object-driven-development.md` names — change request,
impact analysis, context package, specification delta, validation evidence — is not decided here. That
specification defers their contracts, and deciding the persistence of evidence before the evidence contract
exists is the guess that reads like a requirement both specifications warn against. The deferral ends per
artifact, as each contract arrives: `specs/0009-context-assembly.md` R13 assigns the context package
`claim-recorded` by applying the rule above, now that R1 there fixes the package's contract. The rule is
this section's; the assignment is that document's.

## Verification

A produced file is never hand-edited, for the reason R7 gives about a generated
tree. Where produced code must be extended, the plan declares an extension point and the extension is a
separate hand-authored file the produced code calls. Mixed files defeat regenerate-and-diff, which is the only
mechanism that makes the promise checkable.

Verification regenerates into a temporary tree from the four pinned identities, compares against the committed
tree, and mutates nothing. A difference in a locked entry is exactly one of three things — a change in
knowledge, a template or agent regression, or a hand edit of a produced file — and all three are findings.

The share of source produced on the deterministic track is measured and reported. It is the only evidence that
the generative premise holds: where the share covers little of the structural code, the knowledge base is
scaffolding the system rather than producing it, and the promise is reduced to what the mechanism delivers
rather than restated. Its companion on the knowledge side is the representation ratio of spec 0002 R7.

## Generative completeness

A gap is tolerable where knowledge is documentation and fatal where knowledge produces software, because
whatever reads the gap must either stop or invent. Completeness is a validation of its own, evaluated over a
scope, so one context compiles while another is still incomplete.

A scope is generatively complete when every `definition` in it has full types and a declared identity, every
stateful `definition` has exactly one `lifecycle` whose transition table is total, every `rule` carries an
`expression` or `examples`, every `interface` carries a version and a schema, and every `ref`, `enum`,
`guard`, and `step` resolves inside the scope or through an `interface`.

Completeness covers domain facts only. A missing naming convention is not an incompleteness, because spec 0002
R4 never admitted it.

This does not conflict with fail-soft: resolution reports a gap and continues under spec 0001 R13 and R15, and
validation rejects under spec 0001 R6. Nor is completeness the maturity ladder, which measures binding force
rather than sufficiency. Two axes, deliberately orthogonal.

## Binding implementation to knowledge

There is no software graph. A graph over source elements costs three to four orders of magnitude more nodes
than the knowledge it indexes, requires maintenance on every commit, and decays without a signal.

Binding comes from two derived indexes: the manifest for produced source, and a coverage index for
hand-authored source, derived from declarations the files carry at file or module granularity. Neither is
authored.

A test that asserts a `rule` declares that rule's id, and that declaration is the assertion linkage: a
knowledge object never declares its own assertion, so the maturity level of spec 0001 R23 stays derived from
evidence rather than claimed. A generated conformance test carries the same declaration, emitted by execution.

Reverse impact is a query over the two indexes plus version-control history. What this gives up, stated
rather than glossed: function-level traceability for hand-authored code. Produced source has it through the
manifest.

## Deliberately not specified

Declared absence, not oversight. A request to record one of these is a request to change this list:

| Not specified | Why |
|---|---|
| Naming conventions, directory layout, project structure | Stack knowledge, excluded by spec 0002 R4 |
| Idiomatic decisions of a language or framework | Stack knowledge |
| How a reference becomes a column or a foreign key | Stack knowledge; the domain fact is `binding`, per spec 0003 |
| Where produced source lives in the tree | The pack decides once, through the placement decision of R52; the manifest locks it |
| Which producer inside a pack proposes a new path, and whether a deterministic class derives its own | Both designs satisfy R52; they differ in what a first run promises, and no pack exists to choose on |
| Deployment topology, infrastructure | ADR for the decision, the pack for what is produced |

## Definitions

Terms used normatively below.

| Term | Concept |
|---|---|
| artifact class | [artifact-class](../docs/concepts/artifact-class.md) |
| artifact persistence | [artifact-persistence](../docs/concepts/artifact-persistence.md) |
| target pack | [target-pack](../docs/concepts/target-pack.md) |
| generation track | [generation-track](../docs/concepts/generation-track.md) |
| generation scope | [generation-scope](../docs/concepts/generation-scope.md) |
| generation plan | [generation-plan](../docs/concepts/generation-plan.md) |
| generation manifest | [generation-manifest](../docs/concepts/generation-manifest.md) |
| placement decision | [placement-decision](../docs/concepts/placement-decision.md) |
| generative completeness | [generative-completeness](../docs/concepts/generative-completeness.md) |
| knowledge base | [knowledge-base](../docs/concepts/knowledge-base.md) |
| knowledge graph | [knowledge-graph](../docs/concepts/knowledge-graph.md) |
| knowledge object | [knowledge-object](../docs/concepts/knowledge-object.md) |
| domain knowledge | [domain-knowledge](../docs/concepts/domain-knowledge.md) |
| stack knowledge | [stack-knowledge](../docs/concepts/stack-knowledge.md) |
| definition | [definition](../docs/concepts/definition.md) |
| rule | [rule](../docs/concepts/rule.md) |
| lifecycle | [lifecycle](../docs/concepts/lifecycle.md) |
| interface | [interface](../docs/concepts/interface.md) |
| specialized agent | [specialized-agent](../docs/concepts/specialized-agent.md) |
| skill | [skill](../docs/concepts/skill.md) |
| least privilege | [least-privilege](../docs/concepts/least-privilege.md) |
| context package | [context-package](../docs/concepts/context-package.md) |
| fail-soft | [fail-soft](../docs/concepts/fail-soft.md) |
| assertion | [assertion](../docs/concepts/assertion.md) |
| distribution | [distribution](../docs/concepts/distribution.md) |
| accepted | [accepted](../docs/concepts/accepted.md) |
| fixture | [fixture](../docs/concepts/fixture.md) |

## Requirements

### The calibrated promise

- **R1** — Every artifact class MUST declare its track: `deterministic` or `judged`.
- **R2** — The deterministic track MUST produce byte-identical output for identical input and MUST NOT invoke
  a model.
- **R3** — The judged track MUST be verified against a conformance suite generated from the knowledge base. A
  judged artifact with no covering suite is not accepted output.
- **R4** — A reproducibility claim MUST name four pinned identities: the knowledge base version, the
  generation scope, the target pack version, and the manifest. A claim omitting any of the four is not a
  reproducibility claim.
- **R5** — A report MUST distinguish byte identity from behavioural conformance, and MUST distinguish a first
  generation from a regeneration under lock. Presenting a passing conformance suite as byte identity is a
  false report.
- **R6** — The share of source produced on the deterministic track MUST be measured and reported. Where the
  share does not cover the structural code, the promise MUST be reduced to what the mechanism delivers rather
  than restated.
- **R7** — A produced file MUST NOT be hand-edited. Extension happens through an extension point the plan
  declares, in a separate hand-authored file.

### Artifact classes

- **R8** — The artifact class vocabulary is closed, per the table under **Artifact classes and what a pack
  declares**. A class outside it MUST be rejected.
- **R9** — A new artifact class is admitted when a target pack needs it, recorded with the case that
  demanded it. A fixture exercising the class is recommended evidence, not a condition of admission.
- **R10** — Each target pack MUST declare which classes it produces and the track of each. This specification
  fixes no mapping from node type to class, because such a mapping presumes a technology.
- **R11** — A node type yielding no class under the active pack MUST be reported. Silence about a type that
  produces nothing reads as coverage that does not exist.

### The target pack

- **R12** — Exactly one target pack is active in a governed repository.
- **R13** — A target pack comprises the specialized agents and templates that produce the classes it
  declares, distributed together under `src/claude/`. Every agent MUST conform to `schemas/agent.v1.json`
  and MUST enumerate its tool grant. R51 fixes the correspondence between the declaration and the producers,
  and a pack MUST NOT carry a producer for a class it does not declare. Whether a pack additionally carries
  an agent that only decides placement is not fixed here — see **Deliberately not specified**.
- **R14** — A pack MUST declare only its identity, its version, and the classes it produces with the track of
  each and the node types each is yielded by. It MUST NOT declare a naming convention, a directory layout,
  path derivation, expansion order, or the mapping from a reference to a storage representation.
- **R15** — A stack fact a template expands MUST live in the pack, and MUST NOT be required of the knowledge
  base, per spec 0002 R4.
- **R16** — A component other than a target pack MUST NOT depend on a specific pack.
- **R17** — The framework ships no default pack. A missing or ambiguous pack MUST block generation with a
  report naming what is missing, and a pack inferred at run time MUST be rejected as a hidden default.
- **R18** — The entry point that runs generation is a [skill](../docs/concepts/skill.md). `specs/0006`
  fixes the capability classes and holds that there is no command class;
  `docs/adr/0009-component-contracts-from-anthropic-documentation.md` records why.

### The generation scope

- **R19** — A generation scope MUST be a closed set of knowledge-object ids with content hashes, derived by
  expansion from declared roots over the edges spec 0003 marks as traversed, and frozen.
- **R20** — After a scope is frozen, a change to any member MUST invalidate the scope rather than alter it.
- **R21** — Scope resolution MUST fail closed. A member that cannot be resolved blocks generation, and the
  fail-soft behaviour of spec 0001 R13 MUST NOT be applied to a generation scope.
- **R22** — A generation scope and a context package MUST remain separate artifacts, because their failure
  semantics are opposite.

### The generation plan

- **R23** — The plan MUST be derived from the scope, the pack's declaration, the manifest, and the frozen
  placement decision of R52. It MUST NOT be authored, it MUST NOT hold a rule, and no model MUST participate
  in the derivation itself.
- **R24** — Each plan entry MUST name the knowledge object, the artifact class, the track, the target path,
  and whether the entry is locked or new. A locked entry takes its path from the manifest and a new entry
  takes it from the frozen placement decision; a plan entry with no target path cannot be validated under
  R25.
- **R25** — The plan MUST be validated before any file is written: every reference resolves, every class is in
  the vocabulary and in the pack's declaration, no two entries claim one target path, and every locked path
  still exists. A plan that fails validation is rejected, never repaired.
- **R26** — A plan MUST be producible and inspectable without writing any file.
- **R27** — A target-path collision MUST be reported as a defect. A policy that resolves a collision silently
  MUST NOT exist.
- **R28** — An identical scope, pack declaration, manifest, and frozen placement decision MUST yield a
  byte-identical plan. Holding the placement decision fixed is what makes this testable for a first
  generation; it is not a claim that two first generations choose the same paths, which R52 denies.
- **R29** — Determinism MUST be tested at the plan as well as at the output. A test covering only produced
  source cannot distinguish a nondeterministic plan from a nondeterministic template.

### The generation manifest

- **R30** — The manifest MUST record, for each produced artifact, the knowledge object, the artifact class,
  the target path, a content hash, and the pack version that produced it.
- **R31** — A target path recorded in the manifest MUST be read on every later run and MUST NOT be decided
  again.
- **R32** — Moving a produced file MUST be an explicit recorded unlock. A silent relocation appears in a diff
  as a deletion and an addition, indistinguishable from a change in knowledge.
- **R33** — The manifest records execution and MUST NOT decide anything.

### Verification

- **R34** — Verification is regenerate-and-diff into a temporary tree and MUST NOT mutate the repository. A
  check that repairs what it detects reports success on a defect.
- **R35** — A difference in a locked entry MUST be reported as a finding, and the report MUST name which of
  the three causes it is: a change in knowledge, a template or agent regression, or a hand edit of a produced
  file.
- **R36** — A conformance test MUST be generated from `rule.examples` and from `lifecycle` totality, and MUST
  declare the id of the knowledge object it covers.

### Generative completeness

- **R37** — Generative completeness is a validation, evaluated over a generation scope, and covers domain
  facts only. A missing stack fact is not an incompleteness.
- **R38** — A generative gap MUST block generation for its scope. Resolution reports a gap and continues under
  spec 0001 R13 and R15; validation rejects under spec 0001 R6.
- **R39** — The generation path MUST NOT supply a domain fact the knowledge base does not hold, and MUST NOT
  ask a model to supply one.
- **R40** — Generative completeness MUST NOT be reported as a level of the maturity ladder of spec 0001 R23.

### Binding implementation to knowledge

- **R41** — A software element MUST NOT be a node of the knowledge graph.
- **R42** — Produced source binds to knowledge through the manifest; hand-authored source binds through a
  declaration it carries at file or module granularity. Both indexes MUST be derived, never authored.
- **R43** — A knowledge object MUST NOT declare its own assertion.
- **R44** — Reverse impact MUST be answered from the derived indexes and version-control history. A
  hand-maintained mapping from knowledge to code MUST NOT exist.

### Artifact persistence

- **R45** — Every artifact this specification names MUST declare exactly one persistence value from the closed
  set `committed | claim-recorded | run-scoped`.
- **R46** — A persistence value MUST follow from the rule under **Artifact persistence**: an artifact whose
  body is not recomputable from committed inputs without a model MUST be `committed`, unless R53's
  transcription conditions hold for it. A declaration that contradicts the rule, and does not meet those
  conditions, MUST be rejected rather than repaired.
- **R47** — The assignment under **Artifact persistence** is normative for the artifacts it names.
- **R48** — For a `claim-recorded` artifact, the reproducibility claim of R4 MUST record the artifact's
  declared inputs and the content hash of its frozen body, and the body MUST be recomputable from committed
  inputs with no model involved.
- **R49** — A `run-scoped` artifact MUST NOT be committed, and its absence MUST NOT be reported as a finding
  by the verification of R34 and R35.
- **R50** — The generation manifest MUST be `committed`. A design in which placement is decided on any run
  after the first MUST be rejected: `specs/0002-knowledge-economy-principles.md` R4 excludes placement from
  the knowledge base, and R31 has nothing to read without a committed manifest.

### Producer cardinality, and the first placement

These three arrived after R1 through R50, and they are numbered here rather than inserted beside the
requirements they qualify, so that an existing citation still resolves to the statement it named.

- **R51** — Every artifact class a pack declares MUST have exactly one producer within that pack: a template
  for a class on the `deterministic` track, a specialized agent for a class on the `judged` track. A
  declared class with no producer MUST be rejected, and two producers for one class MUST be rejected. This
  is `specs/0006` R5 made checkable at the pack rather than restated: an agent produces exactly one artifact
  class, so a pack declaring two judged classes carries two agents.
- **R52** — For each plan entry the manifest does not lock, the target path MUST come from a placement
  decision that the pack produced, that was validated before use, and that was frozen before plan
  derivation began. Validation MUST reject a path outside the governed repository, a path that is not a
  legal path for the repository, an entry naming a class the pack does not declare, and two entries naming
  one path. A placement decision that fails validation MUST be rejected, never repaired, and no plan MUST be
  derived from it. This specification claims no byte identity for a placement decision: a model produces it,
  and R5's distinction between a first generation and a regeneration under lock is what a report carries
  instead.
- **R53** — A placement decision is `run-scoped`. It is the one artifact this specification exempts from
  R46's rule that a model-produced body is `committed`, and the exemption holds only while all four
  conditions hold: the run transcribes the decision into the manifest under R30; the manifest is named as
  the committed authority for the same fact; the transcription happens in the run that produced the
  decision; and a run that ends without producing an artifact locks no path for it. A design meeting fewer
  than all four MUST NOT claim this exemption.

## What this specification does not decide

Deferred, because a contract written ahead of the code that needs it is a guess that reads like a
requirement:

- the schemas of the scope, the plan, the manifest, the pack declaration, and the placement decision, each
  arriving with the first pack that produces one. R52 fixes what the placement decision is for and what its
  validation must reject; the contract it is validated against is deferred here for the reason this list
  gives, and `specs/0005` R16a already decides that it needs a versioned schema when it arrives,
  because it is an artifact a later derivation consumes;
- the declaration syntax hand-authored source uses in R42, and its language coverage;
- how a `rule.expression` is evaluated. Spec 0003 defers the grammar; this specification defers the evaluator
  and requires only that a rule without an expression carry `examples`;
- the unit of the deterministic share in R6, and any value that would count as sufficient: the number needs
  one generated system before it means anything, and inventing a threshold now would produce the
  target-chasing spec 0002 R8 forbids;
- how a governed repository installs the generation artifacts, and how the distribution carries the pack;
- which pack the framework ships first, and whether it ships any — each is demand-pulled by a fixture.

## What satisfied acceptance

Accepted on 2026-07-31 by maintainer decision, which `CLAUDE.md` **Normative sources** makes sufficient on
its own. The conditions this document had set were **not** met. They are kept below rather than deleted,
because they are the evidence this document still owes and removing them on acceptance would turn an open
debt into a silent one.

What that costs is stated rather than glossed. From here `.claude/rules/compatibility.md` governs this
document, so a change to a requirement is a breaking change owing a migration path and a migration test
rather than a revision — and the first component built against it is the thing most likely to demand
exactly such a change. `specs/0001-knowledge-object-driven-development.md` was accepted the other way, on
evidence, with the requirements its three unmet conditions covered moved out to
`specs/0014-acceptance-closure-and-escalation.md` rather than accepted unexercised. That route was
available and was not taken here.

### Conditions recorded before acceptance, still outstanding

This specification presupposes components that do not exist. Condition 1 is met; the rest are not, and
each remains the evidence this document owes:

1. ~~a maintainer accepts this specification.~~ **Met** on 2026-07-31. Both specifications it derives from
   were already accepted — spec 0002, and spec 0003 on 2026-07-30 — and the `CLAUDE.md` **Scope** question
   R12 through R18 rested on was settled;
2. one target pack exists under `src/claude/` with a declaration conforming to a schema, and a test proves
   rejection of a declaration naming a class outside the vocabulary (R8) and of a declaration carrying a
   naming convention (R14);
3. one generation scope is produced, frozen, and shown to invalidate when a member changes (R20), and a test
   proves scope resolution fails closed rather than degrading (R21);
4. a plan is produced from that scope and validated without writing a file (R25, R26); a test asserts the plan
   is byte-identical across two runs (R28); and a test asserts a target-path collision is reported rather than
   resolved (R27);
5. one artifact class is executed on the deterministic track, and a test asserts that a second run reuses the
   locked path rather than deciding one (R31) — the requirement that carries this specification's
   reproducibility claim;
6. regenerate-and-diff is proven to detect each of the three causes in a locked entry, and to name which
   (R35);
7. a conformance suite is generated from one rule's `examples` and one lifecycle's totality, and a test
   asserts a judged artifact with no covering suite is rejected (R3);
8. a fixture under `fixtures/` holds a two-context bundle with a scope that deliberately excludes one context,
   because a scope including everything never tests scoping;
9. the deterministic share of R6 is measured on that fixture and recorded, because the number is the evidence
   for the premise and an unmeasured premise is an assumption;
10. a test freezes a generation scope, discards the artifact, recomputes it from the recorded roots and the
    knowledge base version, and asserts the content hash matches the recorded one (R48). This is what makes
    `claim-recorded` a mechanism rather than a label, and it is what turns R20 into a check;
11. a test asserts that no plan file survives a generation run, and that verification does not report its
    absence as a finding (R49);
12. a test asserts that a persistence declaration contradicting the rule of R46 is rejected rather than
    repaired;
13. the fixture of condition 8 carries all three persistence values, so the assignment of R47 is exercised
    rather than asserted;
14. the pack of condition 2 declares two judged classes, and a test proves a pack carrying one agent for
    both is rejected (R51), together with a declaration naming a class no producer covers. One judged class
    never tests the cardinality rule, which is the defect that survived this document's first draft;
15. the pack's declaration is shown to answer R11: a node type in the scope that the declaration's `from`
    entries do not cover is reported rather than passing silently;
16. a first generation produces a placement decision that is validated, frozen, and shown to be the only
    judged input to the plan (R52), and a test proves a placement decision naming a path outside the
    governed repository is rejected rather than repaired. A second test asserts that a run failing before
    execution locks no path, which is R53's fourth condition and the one that keeps R25's "every locked path
    still exists" satisfiable.

Condition 5 already carries R50: a second run that reuses the locked path is the same evidence that the
manifest survived the first. Nothing further is asked of it here.

If the fixture shows that an artifact class no pack produces survives in R8, or that the deterministic share
is small enough to make the generative claim scaffolding, reduce the vocabulary or the claim before accepting
this specification rather than after. The same applies to the persistence vocabulary: if no artifact needs
`claim-recorded` — if the scope turns out to be either committed outright or purely run-scoped — reduce R45 to
two values before accepting rather than after.
