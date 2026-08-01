---
id: "0017"
title: Let order follow from what a capability declares, and let Siegard refuse rather than sequence
status: accepted
contract_version: adr/1
---

# Let order follow from what a capability declares, and let Siegard refuse rather than sequence

## Context

A maintainer put the position plainly: phases are an idea of how Claude should create artifacts, taught
through skills. Siegard should be agents, skills, and templates, each specialist agent responsible for one
artifact, each artifact declaring its inputs and its output — and *that* is what guarantees the right
sequence. Siegard should not control the sequence of execution.

**`foundation/0005` already said this.** R1 makes Claude Code the executor and ships no scheduler. R2:
"The framework never owns the workflow. No component it ships decides which capability runs next, in what
order, or at what depth." R3 puts selection with the model. R10: "Two capabilities that must run in a fixed
order state that dependency in their declarations." Its Provenance even rejects the v0.1 architecture for
the same reason the maintainer gave — it duplicates scheduling the harness already performs.

So the position was not a proposal. It was the accepted architecture, and what needed deciding was why the
repository did not behave as though it were. Three findings answered that.

**`foundation/0005` contradicted itself, by one fine line.** R3 carved out a component that chooses a
*transition* rather than *work*. R5 put control flow in the class of things only a script may decide, R6
required a transition chosen by lookup, R14 required workflow state derived from a durable record, and the
division-of-responsibility table put "decides transitions by lookup in a script" in Siegard's column. The
document held the architecture and its opposite, separated by a distinction between *work* and *transition*
carrying more weight than it could bear.

**Nothing made a declaration sufficient to sequence.** R10 permitted order-from-declaration and neither
required nor checked it. Measured over the framework's own declarations, 3 of 13 orderings were derivable.
The clearest case: `knowledge-author` declared no artifact input at all while receiving the node type and
the subject as bare values another capability had decided. R10 was satisfied by declaring no order rather
than by declaring the true one.

**Phases were control flow, not pedagogy.** `foundation/0001` R2 said the default path was *exactly* seven
named steps in that order, and the phase names were a closed vocabulary a persisted event branched on.
Nothing in the specifications said phases were something Claude is taught.

## Decision

Order follows from what each capability declares it requires, and from nothing else. Siegard refuses at a
boundary; it does not sequence. Five documents changed, and each change is stated where the requirement is
read rather than only here.

| Document | Change |
|---|---|
| `foundation/0005` | R23 added: Siegard refuses, it does not sequence. R3 loses the carve-out; R5 narrowed to a validation verdict and a boundary rejection; R6 and R14 retired with their numbers kept; R10 made the sole thing that fixes an order; the responsibility table moved sequencing to Claude Code |
| `foundation/0007` | R24 added: every artifact that must exist before a capability runs is a declared input with its contract version, so the order is derivable without executing anything. R25 added: alternatives are declared as alternatives, and the choice among them is the executor's |
| `foundation/0001` | R2 demoted from a closed control-flow vocabulary to guidance taught through a skill; R5 and R8 retired; R7 kept with the absence of a mechanism stated in the requirement; R21 found unaffected |
| `foundation/0014` | R1 rewritten; R2 through R4 kept with their absent mechanism named; R5 confirmed as binding |
| `foundation/0006` | R8 corrected — it had assigned durable control flow to a script and named an orchestrator as where that logic lives |

One principle settled `foundation/0001` and `foundation/0014`: **retire what names a component the
framework no longer ships; keep what states a rule the method's actors can still honor.** It is why R5 and
R8 are retired while R7 and R2 through R4 of `foundation/0014` are kept as debts.

## Consequences

**Three guarantees are given up, and naming them is the point.** A guarantee lost silently is worse than
one withdrawn.

| Given up | Why a declared dependency cannot hold it |
|---|---|
| A bounded number of attempts, whose exhaustion is terminal and is never an acceptance | depends on how many attempts already happened |
| Agreement between an outcome and the evidence that outcome carries | not an ordering; a refusal of a false report |
| Resumption after an interruption | requires a record of where work stopped |

Each depends on what has already happened rather than on a prerequisite. Where one is needed again it
returns as a refusal at a boundary, never as a component that sequences work.

**A fourth was counted and was wrong.** The rule that no workflow accepts its own output survives, and it
is enforced: a knowledge object derived from existing material is born `proposed` and only a maintainer
promotes it, and a generation scope compiles accepted knowledge only. Nothing the framework runs can accept
its own output and then build on it. What was lost is the acceptance *phase* that recorded the decision, not
the requirement that a decision be someone's.

**The framework family briefly amended the method.** The first form of `foundation/0005` R23 declared two of
`foundation/0001`'s requirements given up. `foundation/README.md` states that a framework specification does
not amend the method, so that was `foundation/0005` deciding what was not its to decide. It now states the
framework's architecture and leaves the method to settle its own.

**`foundation/0014` R1 is itself only half implemented, and that is not hidden.** It keeps escalation's
condition checkable and requires that an inserted step which is itself a guarantee be verified at a
boundary. No such boundary check exists. The requirement is honest about what it asks and nothing reports it
as satisfied.

**Three concepts left the bundle** — `orchestrator`, `transition-guard`, `workflow-state` — because no
requirement names them and a bundle keeping a dead term to satisfy a historical note inverts which serves
which. `event-log` was rewritten rather than removed: a governed repository may keep one, and the rule that
no secret enters a record reaches it.

**A validator gap surfaced while doing this.** Three concepts kept linking to two that had been removed, and
`make validate` passed on all three: the specification validator had always checked links into the bundle,
and the bundle's own cross-references were checked by nothing. One of the three dangling links was written
during this change. The check now exists, with both directions covered.

**No shipped code changed.** The implementation already behaved this way after the machinery was removed —
`docs/adr/0016-remove-the-workflow-machinery.md` — so this was the cheapest moment available to align the
specifications, and what it removed was a standing disagreement between what they required and what existed.

### What was rejected

**Deriving the order mechanically and shipping the derivation.** It is the strongest form and it costs a
third computed artifact in the distribution, which would falsify the sentence in `CLAUDE.md` naming two —
an edit only a maintainer makes. Checking a derivation against the declarations was the cheaper form and was
not built either: the audit showed too little was derivable for a check to be worth its weight before the
declarations are complete. R24 is what makes them complete; the check is available afterwards and is not
owed.

**Deleting `foundation/0001`'s workflow requirements.** It would assert that the method changed, which
nobody argued. What changed is what makes the method hold.

**Retiring `foundation/0014` outright.** Its R5 — that a report must not present independent review as a
guarantee — survives untouched, binds now, and is what makes it safe to record three unimplemented
requirements without misrepresenting them.

**Keeping the carve-out.** This was the status quo, and it left a document readable as forbidding and
permitting the same thing depending on which requirement was cited.

### What would falsify this

An escalation the executor skips with nothing catching it. `foundation/0014` R1 leans on a boundary check
that does not exist, so today the condition is checkable and the honoring is not. If a required review is
missed in practice, the repair is that boundary check — not a component that decides what runs.

The three abandoned guarantees biting in that order of likelihood: resumption first, because an ingestion
over real material is long enough to be interrupted.
