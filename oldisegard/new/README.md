# oldisegard/new — the extracted components, in Siegard form

Sixteen components — thirteen specialized agents and three skills — carrying the knowledge of the backend
dev-phase components in `oldisegard/`, rebuilt against this framework's rules. Staging only: nothing here
is under `src/claude/`, so nothing is installed, nothing is generated into `dist/`, and no validator in
`make check` looks at it.

Each agent ships with the contract for the artifact it produces, because `foundation/0005` R5 gives a
specialized agent exactly one artifact class and an agent with no contract for its output has none.

## The three skills — the way in

An agent is delegated to; under `foundation/0005` R4 a skill is the only class a user invokes directly.
Without these, thirteen agents are thirteen pieces with no board.

| Skill | Ends at | Delegates to |
|---|---|---|
| `prepare-work` | a plan a person reads | `codebase-surveyor`, `backlog-decomposer`, `execution-contract-binder`, `specification-gap-reporter`, `infrastructure-dependency-analyst` |
| `implement-task` | one task written, with its tests | `implementer`, `test-author` |
| `review-change` | findings a person reads | `security-pattern-scanner`, `conformance-reviewer`, `architecture-pattern-scanner`, `regression-consumer-analyst`, `acceptance-coverage-auditor`, `test-failure-diagnostician` |

Three rather than one, because each ends where a person has to decide something: a plan before work
starts, a change before it is reviewed, findings before anything is merged. Merging two of them would have
a skill run past a human gate.

**A procedure is not a sequencer.** `foundation/0004` R2 forbids shipping anything that decides at runtime
which capability runs next, records where a run stands, or resumes one — which is precisely what the
orchestrators in `oldisegard/` did, with a claim, an event log, and a phase state machine. A skill holding
a written order is a different thing: it is followed once and forgotten, nothing records progress, and a
second invocation starts over. `/ingest-domain` in this repository is the precedent.

All three declare `disable-model-invocation: true`. Each writes artifacts, and R4 requires a skill whose
effects reach outside the session to say a description match may not trigger it.

## Tier 1 — the five that survive contact with this repository unchanged

| Agent | Artifact | Comes from |
|---|---|---|
| `security-pattern-scanner` | `security-scan/1` | `u-security-reviewer` |
| `test-failure-diagnostician` | `test-failure-diagnosis/1` | `u-be-qa`, Phase 1 Step 3 |
| `acceptance-coverage-auditor` | `coverage-audit/1` | `u-be-qa` Phase 2 Step 2, `u-be-standards` |
| `codebase-surveyor` | `code-inventory/1` | `u-be-planner` Step 0 |
| `specification-gap-reporter` | `specification-gap/1` | `u-be-developer`, spec-compliance rules |

## Tier 2 — the eight that needed splitting or adaptation first

| Agent | Artifact | Comes from | What it took |
|---|---|---|---|
| `backlog-decomposer` | `backlog/1` | `u-be-planner` Steps 1–3 | order, estimate and priority removed; numeric bounds became caller-supplied |
| `execution-contract-binder` | `execution-binding/1` | `u-be-planner` Step 3B | split out, so what an executor reads is chosen before it runs |
| `infrastructure-dependency-analyst` | `infrastructure-readiness/1` | `u-be-developer` Step 1B | criticality removed; no shell, so readiness is read rather than probed |
| `regression-consumer-analyst` | `regression-exposure/1` | `u-be-qa` Step 3B | narrowed to a realized change, against `codebase-surveyor`'s planned one |
| `architecture-pattern-scanner` | `architecture-scan/1` | `u-architecture-reviewer` | five of eight patterns handed to a script; every threshold un-shipped |
| `conformance-reviewer` | `conformance-review/1` | `u-be-review` skill | eleven axes reduced to the five that require reading |
| `implementer` | `implementation-record/1` | `u-be-developer` | gate, branch, run and CR removed; inferences made a required field |
| `test-author` | `test-authoring-record/1` | `u-be-qa` + `u-be-standards` | separated from the implementer; nothing is executed |

Neither `implementer` nor `conformance-reviewer` carries `backend` in its name. The stack is the target
pack's, not the agent's: a pack carries one technology and namespaces what it holds.

## What was dropped, and under which rule

- **Orchestration.** `ORCH_TASK_ID`, `SESSION_DIR`, attempt counters, idempotency renames, branch and
  commit mechanics, the return envelope, round escalation, and every "notify the Orchestrator-Dev".
  `foundation/0004` R2: the framework does not sequence, and ships nothing that records where a run
  stands. `backlog/1` carries dependencies and no order, per R3.
- **Choosing what runs next.** `block_tc` and the remediation actions; the approve/reject verdict; the
  bug severities feeding an approval gate; the `suggested_tc_objective` an orchestrator turned into a
  task verbatim. `foundation/0005` R5.
- **Self-validation.** The developer's pre-delivery checklist over its own output, and the QA gate fields
  written for the gate that judged them. Same R5, which is why `implementation-record/1` has no
  readiness flag.
- **Write and Bash grants.** Eleven of thirteen are `Read, Grep, Glob`. The two that write —
  `implementer` and `test-author` — hold `Read, Write, Edit, Grep, Glob` and no shell: they build
  nothing, run nothing, and touch no version control. `foundation/0005` R6.
- **Running anything.** `u-be-qa` ran the build and the suite and then judged the result. Running is a
  script's under `foundation/0004` R6; `test-failure-diagnostician` reads output it did not produce.
- **Coverage as a number.** `docs/concepts/assertion.md` forbids expressing a gate or threshold as a
  coverage figure, so `coverage-audit/1` carries no percentage, ratio, or score.
- **Uncalibrated thresholds.** `u-architecture-reviewer` shipped ">15 public methods", "≥3 domain areas",
  "≥8 lines", "≥80% similarity", "depth ≤5"; `u-planning` shipped "2 to 6 tasks per epic", "estimate L
  prohibited", "backlog > 15". `foundation/0006` R21 admits only a threshold calibrated from executed
  runs and recorded with its evidence. None was, so none ships: a caller supplies one per run, and R22
  makes the artifact say the value came from the caller.
- **The change request.** `change-request/1` is retired here, so the reporter produces a
  `specification-gap` — an observation about a document — and what to do about it stays a later decision.
- **Mechanically decidable patterns.** Import cycles, layer violations, hidden shared state, undeclared
  debt, naming, folder placement, type escapes, and the prohibition list all left the agents.
  `foundation/0004` R6 puts them in a script, and an agent reporting both kinds would make the script's
  findings look like opinions.
- **Embedded skill copies.** `u-be-developer` and `u-be-qa` each pasted ~400 lines of `u-be-development`
  and `u-be-standards` into the prompt under a "Last synced" date. One authoritative definition per
  concept; that content is stack knowledge and belongs to a pack.

## How the sixteen fit together

Order is derivable rather than asserted, per `foundation/0004` R3: `codebase-surveyor` and
`backlog-decomposer` need nothing; `execution-contract-binder` needs a `backlog/1`; `implementer` needs a
`backlog/1` and an `execution-binding/1`; `test-author` needs an `implementation-record/1`;
`regression-consumer-analyst` optionally reads a `code-inventory/1`. The rest take only a file set and an
identifier.

Every agent is named by exactly one skill, so the thirteen are reachable and none is reachable two ways.
That is checked rather than asserted — see below.

## What is verified

Run from the repository root, against this repository's real contracts:

- the declaration set validates against `schemas/capability-declaration.json` (`capability-declaration/3`),
  with sixteen declarations for sixteen components and one each;
- all thirteen agent frontmatters validate against `schemas/agent.json`, each `name` equal to its filename
  stem;
- all three skill frontmatters validate against `schemas/skill.json`, each `name` equal to its directory
  name;
- all thirteen artifact schemas are valid JSON Schema Draft 2020-12;
- the worked example in each agent body validates against the contract that agent cites;
- every agent declares exactly one artifact class, and every declared contract version equals the `const`
  in its schema file;
- every agent is named by exactly one skill — none unreachable, none reachable two ways.

What is **not** verified: nothing here has been exercised by a test, an eval, or a run in a consuming
repository, so under `foundation/0005` R11 none of these is a capability yet — they are sixteen
candidates with contracts.

## What stands between this and shipping

1. **A target pack.** `security-pattern-scanner`, `architecture-pattern-scanner`, `conformance-reviewer`,
   `codebase-surveyor`, `implementer` and `test-author` read or write source in one technology's idiom.
   `docs/concepts/target-pack.md` is where stack-specific agents live, and no pack exists.
2. **The scripts the components shed.** This is now the largest gap, and the agents themselves point at
   it ten times: "a script's work", "a linter's", "the boundary validator". What is missing is an
   import-graph checker, a lint pass, a dependency-cycle check over `backlog/1`, the runner whose output
   the diagnostician reads, and a boundary validator for each of the thirteen contracts. Every one was
   removed from an agent for the right reason under `foundation/0004` R6 and placed nowhere. Until they
   exist, the coverage is smaller than sixteen components suggest, and no artifact here is validated
   before it is consumed.
3. **Evidence.** `foundation/0005` R11 wants a test, an eval, or a run in a consuming repository.
4. **A decision about scope.** These belong to an implementation phase this framework does not have. The
   product today goes from a request to knowledge objects and stops; `CLAUDE.md` **Scope** forbids
   introducing an abstraction before a current requirement needs it.
