# Siegard Generator

This repository is `siegard-generator`. It authors the Siegard framework's source under `src/claude/`
and generates the distribution consumers install, at `dist/.claude/`. It is not the framework: the
framework is what `make dist` produces. This repository does not build a business application.

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
gains the statement — there is no second authority to decide it elsewhere. A concept fixes what a term
means. A schema encodes the structure a contract requires. Code and tests implement them, and
documentation explains them. When two disagree, the earlier one in that list wins, and the change that
resolves it updates both — never one alone.

Keep one authoritative definition per concept, in one place. A prompt may say how to apply a rule; it
must not be the sole home of one a specification, a schema, or a validator could hold.

Use one name for a concept across specs, schemas, code, and tests. Add a file to `docs/concepts/` before
using a term normatively; where a concept names a specification in its `sources`, that specification
outranks the concept — correct the concept, never the reverse.

When two sources genuinely conflict and neither wins, say so in the change: name the files and the
incompatible statements, then proceed under the reading that constrains more. Silently merging them, or
picking one without saying so, is the failure to avoid.

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
- Record the inputs, outputs, evidence, and contract version needed to reproduce a decision.