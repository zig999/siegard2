# Framework vocabulary

This file is the authority for terms used normatively in `CLAUDE.md`, specifications, schemas, and
rules. Add a term here before using it in a rule. A term used normatively but absent from this file is
an interpretation waiting to drift.

## accepted

The status of a specification or ADR whose decision binds. Mechanically: `status: accepted` in the
artifact's frontmatter. An artifact with `status: proposed` records a decision under consideration and
binds nothing — it carries no normative weight in the precedence order. See `docs/adr/README.md`.

## capability

A reusable framework behavior with a testable contract, installed into a target repository through the
distribution. A capability requires at least one fixture that exercises it; a behavior with no fixture
is not yet a capability.

## contract version

An explicit identifier that a consumer reads to decide whether it can process an artifact, carried in
the artifact itself (for example `"contract_version": "review-verdict/1"`). A consumer selects
behavior on this value and must never infer version from an artifact's shape.

## distribution

The assembled release artifact under `dist/.claude/`, produced from framework source by a generator
and copied into target repositories. Generated output, never a source tree.

## event log

The append-only record of workflow facts, persisted outside the conversation. Each entry states
something that happened, not the state that resulted. It is the sole durable source for workflow
history; conversation history and auto memory are not.

## fixture

A case in `fixtures/` shaped like a real downstream application need, used to exercise a framework
capability. Fixtures are how downstream reality enters this repository without downstream features
entering it — see the scope fence in `CLAUDE.md`.

## projection

Current workflow state derived by reading the event log, not stored independently of it. A projection
is reproducible: replaying the same events must yield the same state. If state can drift from the
events that produced it, it is not a projection.

## provenance

The recorded origin of a material decision: which inputs, evidence, agent, and contract version
produced it. Enough to reproduce the decision without asking the agent that made it.

## specialized agent

An agent with one declared role and the minimum tools that role requires. Used for context separation,
tool restriction, or work that genuinely requires model judgment.

## transition guard

The condition that must hold for a workflow to move between states. A guard must be deterministic and
testable — decidable by a script or hook rather than by model judgment.
