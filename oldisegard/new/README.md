# oldisegard/new — the Tier 1 agents, in Siegard form

Five specialized agents carrying the knowledge of the backend dev-phase components in `oldisegard/`,
rebuilt against this framework's rules. Staging only: nothing here is under `src/claude/`, so nothing is
installed, nothing is generated into `dist/`, and no validator in `make check` looks at it.

Each agent ships with the contract for the artifact it produces, because `foundation/0005` R5 gives a
specialized agent exactly one artifact class and an agent with no contract for its output has none.

| Agent | Artifact | Comes from |
|---|---|---|
| `security-pattern-scanner` | `security-scan/1` | `agents/dev/u-security-reviewer.md` |
| `test-failure-diagnostician` | `test-failure-diagnosis/1` | `agents/dev/u-be-qa.md`, Phase 1 Step 3 |
| `acceptance-coverage-auditor` | `coverage-audit/1` | `agents/dev/u-be-qa.md` Phase 2 Step 2, `skills/u-be-standards` |
| `codebase-surveyor` | `code-inventory/1` | `agents/dev/u-be-planner.md` Step 0 |
| `specification-gap-reporter` | `specification-gap/1` | `agents/dev/u-be-developer.md`, spec-compliance rules |

## What was carried across

The substance: the twelve-pattern security taxonomy with its severity criteria and the
evidence-must-be-quoted rule; the four-way failure classification with the examples that tell the causes
apart; the test-quality criteria that decide whether a test proves a criterion; the four sections of the
existing-system inventory; and the four conditions under which an implementation must stop rather than
invent what a specification failed to state.

## What was dropped, and under which rule

- **Orchestration.** `ORCH_TASK_ID`, `SESSION_DIR`, attempt counters, idempotency renames, branch and
  commit mechanics, the return envelope, and every "notify the Orchestrator-Dev". `foundation/0004` R2:
  the framework does not sequence, and ships nothing that records where a run stands.
- **Choosing what runs next.** `u-security-reviewer` assigned each finding `block_tc`,
  `create_remediation_tc`, or `log_warning`; `u-be-qa` computed an approve/reject verdict and a round
  escalation. `foundation/0005` R5: a specialized agent does not choose what runs next. The findings stay;
  what to do about them is the caller's.
- **Self-validation.** The pre-delivery checklist the developer ran on its own output, and the QA gate
  fields the QA agent wrote for the gate that judged it. Same R5: an agent does not run the validator that
  checks its own output.
- **Write and Bash grants.** All five are `Read, Grep, Glob`. `foundation/0005` R6, and in each agent the
  reason the read-only grant is load-bearing rather than incidental.
- **Running the suite.** `u-be-qa` ran the build and the tests and then judged the result.
  `test-failure-diagnostician` reads a captured output instead: `foundation/0004` R6 puts the mechanical
  part in a script, and it keeps the run reproducible independently of the judgment about it.
- **Coverage as a number.** `u-be-qa` graded gaps by severity into an approval gate.
  `docs/concepts/assertion.md` forbids expressing a gate or threshold as a coverage figure, so
  `coverage-audit/1` carries no percentage, ratio, or score.
- **The change request.** `u-be-developer` opened one on a spec gap. `change-request/1` is retired here —
  `schemas/contract-versions.json` records it, retired by `foundation/0001` — so the reporter produces a
  `specification-gap`, an observation about a document, and leaves what to do about it to a later decision.
- **Embedded skill copies.** `u-be-developer` and `u-be-qa` each carried ~400 lines of
  `u-be-development` and `u-be-standards` pasted into the prompt under a "Last synced" date. One
  authoritative definition per concept: what those skills hold is stack knowledge and belongs to a target
  pack, not to a copy inside two agents.

## What is verified

Run from the repository root, against this repository's real contracts:

- the declaration set validates against `schemas/capability-declaration.json` (`capability-declaration/3`);
- all five agent frontmatters validate against `schemas/agent.json`, with each `name` equal to its
  filename stem;
- all five artifact schemas are valid JSON Schema Draft 2020-12;
- the worked example in each agent body validates against the contract that agent cites.

What is **not** verified: nothing here is exercised by a test, an eval, or a run in a consuming
repository, so under `foundation/0005` R11 none of these is a capability yet — they are five candidates
with contracts.

## What stands between this and shipping

1. **A target pack.** `security-pattern-scanner`, `test-failure-diagnostician` and
   `codebase-surveyor` read source in one technology's idiom. `docs/concepts/target-pack.md` is where
   stack-specific agents live, and no pack exists. Moving them to `src/claude/agents/` would put a
   stack inside the framework distribution.
2. **Evidence.** R11 wants a test, an eval, or a run in a consuming repository behind each.
3. **A decision about scope.** These belong to an implementation phase this framework does not have. The
   product today goes from a request to knowledge objects and stops; `CLAUDE.md` **Scope** forbids
   introducing an abstraction before a current requirement needs it.
