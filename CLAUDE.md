# Siegard Generator

This repository is `siegard-generator`. It authors the framework's source under `src/claude/`;
`dist/.claude/` is assembled from it and kept in step with it. It is not the framework: the
framework is what an assembly of `src/claude/` produces. This repository does not build a business
application.

## Golden rule: this file

**`CLAUDE.md` is the maintainer's file. Only the maintainer changes it.**

An agent proposes; it never applies. Write the exact text, say where it goes and what it displaces, and
stop there. Authorization is per change and stated in the session: it covers the edit that was
described, never a standing license, and approval of one edit does not carry to the next.

Proposals are wanted, not merely tolerated. A rule this file should carry and does not is a gap worth
naming — as a proposal.

This binds this file only. Everything else — schemas, templates, and code — is ordinary work that an
agent creates and changes without asking. **No artifact needs approval to take effect. It takes
effect because it exists.** An artifact that is wrong is corrected by the next change, not held
behind a gate.

## Language

Write every artifact in this repository in English (en-US): source, generated distribution, specs,
schemas, tests, fixtures, docs, and commit messages. Conversation with a maintainer may use any
language; committed content may not.

## Decision order

Two tiers. A valid option must preserve, in order:

1. correctness and safety;
2. explicit, testable contracts and stated compatibility guarantees;
3. deterministic control flow, validation, and state;
4. traceability and reproducibility.

Among options that satisfy all four, prefer, in order: the smallest sufficient design; lower runtime and
context cost; easier testing, recovery, and maintenance.

A later criterion never overrides an earlier one, and no tier-two criterion settles a question tier one
has already settled. Recoverability and diagnosability are criterion 1. Human convenience sits outside
both tiers: these artifacts are consumed by agents, and a form that reads pleasantly to a person while
leaving a contract implicit is the worse form.

## Where authority lives

A specification states what the framework must do. Where nothing states it, the specification is what
gains the statement — there is no second authority to decide it elsewhere. A schema encodes the
structure a contract requires and fixes what a term means. Code and tests implement them, and
documentation explains them. When two disagree, the earlier one in that list wins, and the change that
resolves it updates both — never one alone.

Keep one authoritative definition per concept, in one place. A prompt may say how to apply a rule; it
must not be the sole home of one a specification, a schema, or a validator could hold.

Use one name for a concept across specs, schemas, code, and tests.

A distributed artifact that cites a specification requirement carries, in `«…»` beside the
citation, a sentence of that requirement verbatim. The pointer is this repository's — the consumer
never receives `specs/` — and the sentence is the consumer's: it reads the rule in the words it was
decided in. `tests/test_spec_citations.py` keeps the two from drifting; a spec that changes its
words leaves the test red until what cites it follows.

When two sources genuinely conflict and neither wins, say so in the change: name the files and the
incompatible statements, then proceed under the reading that constrains more. Silently merging them, or
picking one without saying so, is the failure to avoid.

## What ships is timeless

Everything under `src/` states what the framework is — never what it was, what it replaced, or
what incident produced it. No shipped artifact — a rule, a skill, an agent, a script's docstring,
a schema's description — carries a measurement from a named consumer, an observed anecdote, an
"until this existed", or the form a rule superseded. The reason a rule holds is stated as a
standing fact where it calibrates the agent executing it; the evidence that produced the rule
lives in this repository's commits, session records and proposals, which the distribution does
not carry.

Justification has one placement per artifact class. `src/consumer/CLAUDE.md` states rules
directively — the prohibition and the operative instruction, no why. Skills, agents, scripts and
schemas may carry the timeless why, never the history. A change grounded in a measurement cites
it in the commit message.

Operational time is not history. A consumer project's own lifecycle — an earlier bind, a node the
specification no longer holds, a plan evolving toward closure — is what these artifacts exist to
describe, and stays. And this boundary binds `src/` alone: this file, `specs/`, the repository's
own schemas and its tests are the maintainer's memory, and may say what happened. What a
specification says about what happened is not quotable: the `«…»` a distributed artifact carries
beside a citation is the requirement's statement, and it crosses into `src/` as shipped text — a
history sentence is a substring the test accepts and a history the distribution then carries.

## Change size

A change is **minor** when it alters no specification, no schema, no contract version, and no generated
output — a typo, a comment, a clarification that narrows nothing, a test for behavior already specified.
It runs the validation for the area it touches and stops there.

When unclear, treat the change as ordinary and say so.

## Determinism and state

- Treat conversation history and auto memory as non-authoritative. Verify any claim they make against
  persisted state or source before acting on it.
- Decide mechanically decidable checks in hooks or scripts. Use agents for work that genuinely requires
  model judgment.
- What no mechanism decides is not left unmeasured: a script reports it, names the far end of the
  distribution so a reader can open it, and refuses nothing on a threshold this repository invented.
  A limit stated nowhere is a limit nobody can dispute, and a report that always finds something is
  a floor, not a finding.
- Record the inputs, outputs, evidence, and contract version needed to reproduce a decision.
- A proposal declined is recorded with its reason and the criterion that would reverse it; a
  decline nobody can reopen is a decision nobody can reproduce.
- A change justified by cost cites the measurement and the estimator that produced it. A figure
  read from a record is not a figure read from what ran, and the two disagree; where a later
  measurement supersedes an earlier one, the change corrects it where it was recorded rather than
  leaving two numbers for the next reader to choose between.
- A proposal to add a field, a check, a channel or an agent first names what already exists for the
  need and shows why it does not suffice — read from that thing's record, never from its
  description. A mechanism's prompt or docstring is what it says it does; its returns, its outputs
  and its history are what it did, and the two disagree often enough that a proposal grounded in
  the first alone is a proposal to build a second copy of the second.
- A red suite stops the change until it is green on the change's own terms. A test anchored on
  words the change rewrote is re-anchored on the new words and never loosened to pass; a test
  asserting that something is absent is re-read whenever the words it looks for change, because
  "not found" is true of a fragment that no longer exists and proves nothing about what replaced it.

## Execution authority

The framework executes. A skill installs what a consumer's own registry authorizes and runs the
steps it declares, so a delivery hands over a project that installs and builds rather than source
alone. It was granted deliberately; widening or withdrawing it is the maintainer's.

Five bounds hold it, and giving up any of them is a proposal, never a change:

- **No agent holds a shell.** The skills run; the shipped agents do not, and
  `tests/test_agent_contract.py` is what enforces it. An agent that gained one would run outside
  the capture, where what it saw exists only in a context nobody else can open.
- **Every execution goes through `bin/run.py`,** which refuses a run under a name that already
  exists. That refusal is what replaced the older rule that a producer must not witness its own
  work: iterating is permitted because every attempt stays readable. A run narrated instead of
  captured did not happen.
- **This repository composes no command and authorizes no package.** Every command, bound and
  package name is the consumer registry's; a default shipped from here would be a stack this
  framework says it does not know. Approval of a package is that registry gaining an entry — a
  human editing their own file — never an answer given in a session, which the next invocation
  does not have.
- **Only the orchestrating entry point commits, and only under bounds.** `/deliver-scope` is the
  one component granted a git commit: pathspec-scoped, one per step, under a message naming the
  run — never a sweep, a branch, a push or a rewrite — and only under an ask the human's own
  words state end to end. Every other skill's refusal to commit stands; a second committer, or a
  commit outside these bounds, is a proposal, never a change.
- **Only what a delivery is made of holds a write.** `task-implementer` and `test-author` grant
  `Write` and `Edit`; every other agent returns content and the caller writes it, and
  `tests/test_agent_contract.py` is what enforces it. The grant cannot be scoped to a path —
  `schemas/agent.json` admits tool names and nothing narrower — so a reviewer that gained one
  could edit what it flagged, and a finding nobody can disagree with is a decision wearing a
  finding's clothes. Widening it is a proposal, never a change.

## Decision authority

The framework decides. Where planning finds a fact no specification node states, the
specification gains the statement with a decided value rather than stopping for a person
whose only move is to trigger the decision — SPEC-001 R13 is the rule, and it was granted
deliberately, after measurement showed the stop guarded a species that never occurred.

Three bounds hold it, and giving up any of them is a proposal, never a change:

- **The decision is made blind.** The context that decides never sees the task cut that
  surfaced the fact — a decision made where the cut is visible is the specification bent
  to fit it.
- **Every decision is disclosed, and disclosure is never a gate.** The decided value lands
  in the specification and its entry in the decision log; a human reviews after the fact,
  and disagreement is an ordinary change. A decided fact with no log entry is invention.
- **A contradiction is never decided.** A node stating the opposite turns the route back
  into the standing stop — the scope and the specification disagreeing is the one thing
  only a person settles, and the only thing left that stops a task.