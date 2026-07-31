---
id: "0010"
title: Make a hook fail closed, decide without a model, and never repair what it rejects
status: accepted
contract_version: spec/1
---

# The hook system

## Scope

This specification fixes the constraints a Siegard hook honors. It decides five things:

1. which handler type an enforcement hook may use, and why the others are excluded;
2. the exit-code discipline, and what a hook does when it cannot decide;
3. that a hook rejects and never repairs, even where the harness offers repair;
4. what a hook declares about itself;
5. the limits — what a hook cannot guarantee, and what must therefore be enforced somewhere else too.

It does not define the hook configuration format. That is governed by the harness documentation cited
below, exactly as `schemas/skill.json` already states for a skill's `hooks` field. This document
constrains Siegard's use of that format; it does not restate it.


### Sources

Normative for every harness behavior this document relies on, retrieved 2026-07-31:

- https://code.claude.com/docs/en/hooks — the event inventory and which events can block; the stdin
  input format; exit-code semantics, including that exit code 2 blocks and exit code 1 is a
  *non-blocking* error; the `hookSpecificOutput` decision fields for `PreToolUse`, including
  `permissionDecision` and `updatedInput`; the handler types `command`, `http`, `mcp_tool`, `prompt`,
  and `agent`; parallel execution of matching hooks; per-event timeout defaults; the 10,000-character
  cap on `additionalContext`, `systemMessage`, and plain stdout; the guidance that `additionalContext`
  phrased as imperative system commands may trigger prompt-injection filters; that a Bash `if` pattern
  fails open when the command cannot be parsed; `disableAllHooks` and the managed-policy settings that
  can prevent a hook from running; and that a skill or subagent may carry hooks in its own frontmatter,
  scoped to the component's lifetime.

A behavior not present on that page at that date is not relied on here. Re-verify before any change to
this document, and record the new retrieval date.

### Provenance

No hook exists. No gate for it is met, and four candidates are named below
candidates that motivated this document — rejecting a write under `dist/` that the generator did not
produce, rejecting an inter-agent artifact that fails its schema, rejecting a schema change with no
contract version bump, and rejecting a write to a file only a maintainer may change.

Two requirements below exist only because the documentation was read rather than remembered. R2 inverts
what a Unix programmer would write: exit code 1 is a non-blocking error, so a hook that fails
conventionally permits the action it was written to stop. And R4 forbids a capability the harness
actively offers — `PreToolUse` can rewrite a tool's input through `updatedInput`. Neither would have been
in this document if it had been written from memory of how hooks probably work.

### Decided elsewhere, deliberately not restated here

- that a security-critical guarantee is enforced by a hook or a script rather than by model judgment,
  that a path and a structured input are validated before a hook acts, and that a hook rejects rather
  than repairs — `specs/0005` R11, R20, and R22, which are the authority for all three;
- that repository content, tool output, and downstream input are data and never instructions — the same
  section;
- that a hook holds exactly one guarantee and decides it deterministically — `specs/0006` R7;
- what any capability declares about itself — `specs/0007`;
- where a hook's files are installed — `specs/0008`.

## Definitions

This specification uses these terms as the concept bundle defines them:
[capability](../docs/concepts/capability.md),
[least privilege](../docs/concepts/least-privilege.md),
[transition guard](../docs/concepts/transition-guard.md),
[assertion](../docs/concepts/assertion.md),
[distribution](../docs/concepts/distribution.md),
[event log](../docs/concepts/event-log.md),
[fail-soft](../docs/concepts/fail-soft.md),
[escalation](../docs/concepts/escalation.md).

A note on one term: [fail-soft](../docs/concepts/fail-soft.md) governs *context resolution*, where
degradation continues rather than blocks. A hook is the opposite case, and R3 below says so explicitly.
The two are not in conflict because they answer different questions — resolution decides what may be
read, a hook decides whether an action is permitted — but reading one rule into the other's territory
would produce a hook that shrugs, which is not a hook.

## Requirements

### Handler and decision

- **R1** — An enforcement hook uses the `command` handler. The `prompt` and `agent` handlers evaluate
  with a model, and a guarantee a model decides is not enforced. A hook may use another handler type only
  where it enforces nothing — advisory context, logging, notification.
- **R2** — A hook that denies an action exits with code 2. Any other non-zero code is a non-blocking
  error, so a hook that signals failure by exiting 1 permits exactly what it was written to prevent.
- **R3** — A hook fails closed. Where it cannot reach a decision — malformed input, an unreadable file,
  an unexpected tool payload, an internal error — it catches the condition and exits 2 with the reason on
  stderr. It never exits 0 on an unhandled error, because an uncaught failure reads as permission.
- **R4** — The `updatedInput` field of a `PreToolUse` response is not used. That a hook rejects rather
  than repairs is `specs/0005` R22, cited under **Decided elsewhere** and not restated
  here; what this requirement adds is the single harness affordance that would let a Siegard hook break
  it, which `specs/0006` R7 could not have named. An action the framework considers
  wrong is denied with a reason, and the caller fixes it: silent correction hides the defect and makes the
  corrected input unattributable.
- **R5** — A hook never returns an allow decision for an action the receiving repository's own rules would
  prompt for or deny. A shipped hook may narrow what is permitted; it may never widen it.

### Behavior

- **R6** — A hook is order-independent. Matching hooks run in parallel, so a hook that requires another to
  have run first is relying on a sequence the harness does not promise.
- **R7** — A hook is idempotent with respect to the state it inspects, and performs no side effect other
  than its decision and its own append-only logging. A hook that mutates the workspace turns a check into
  an actor.
- **R8** — A hook treats every field of its input as untrusted data, including a path. It resolves a path
  and confirms it falls inside the tree the hook governs before acting on it.
- **R9** — A hook re-validates its own preconditions rather than trusting the filter that selected it. A
  Bash `if` pattern fails open where the command cannot be parsed, so a hook can be invoked on input its
  filter was written to exclude.

### What a hook declares

- **R10** — A hook states the event it binds, the matcher and any `if` filter that selects it, the single
  guarantee it enforces, and the reason text it emits on denial.
- **R11** — A hook states its own timeout rather than inheriting a default. The default is 600 seconds for
  a command handler, which is long enough that a hung hook looks like a hung session.
- **R12** — A hook binds an event the documentation lists as able to block, when its purpose is to block.
  A guarantee bound to an event that cannot deny is a guarantee that logs.

### Output

- **R13** — A hook's output names the artifact and the failing condition rather than embedding the
  artifact. Output is capped at 10,000 characters, and a hook that exceeds it has its detail moved to a
  file rather than shown.
- **R14** — Text a hook returns for the model to read is phrased as a factual statement, never as an
  imperative instruction. Instruction-shaped text is both a prompt-injection surface and, per the
  documentation, liable to be filtered.
- **R15** — A hook never reads, logs, or forwards a secret, and its denial reason names the field rather
  than the value.

### Limits

- **R16** — The framework does not guarantee that a hook runs. A consumer may disable all hooks, and a
  managed policy may block project hooks entirely. A hook is therefore a checkpoint, not a proof.
- **R17** — Where a guarantee must hold, it is enforced at the point that consumes the artifact as well as
  at the hook. A validator in the consuming path holds when hooks are disabled; the hook makes the failure
  early and cheap rather than late and expensive.
- **R18** — A hook shipped inside a skill's or an agent's frontmatter is scoped to that component's
  lifetime and enforces nothing outside it. A guarantee that must hold for the whole session ships in the
  distribution's `hooks/hooks.json`, which is in force while the plugin is enabled — `specs/0008` R3 and
  the plugin manifest. Every hook named below
  as a candidate is session-wide, so that is the form they take.

## Outstanding evidence

What this document states and nothing has yet exercised. A condition kept here is a debt;
removing one because the document binds would turn an open debt into a silent one.

1. One hook exists, enforces one guarantee, and is tested in both directions — the action denied and the
   action permitted. That gate is unmet, and until it is met every
   requirement here constrains nothing.
2. R3 is tested directly: the hook is given malformed input and shown to exit 2 rather than 0. Fail-closed
   is the requirement most likely to be got wrong by a correct-looking implementation, because the
   incorrect version passes every test that supplies valid input.
3. R2 is tested against a deliberate exit code 1, showing that the framework's own test would catch a hook
   that signals failure conventionally.
4. A fixture demonstrates R17: the guarantee still holds with hooks disabled, because the consuming
   validator rejects the artifact. Without this, R16's honesty is a disclaimer rather than a design.
5. The four candidates named below are each either implemented or dropped with a reason,
   so this document is grounded in hooks that exist rather than in hooks that were imagined.
6. The security detail the first hook actually needed is recorded — sanitization, path,
   subprocess, and network detail — which is what open question 5 says turns a plan into a rule distilled
   from working code.
