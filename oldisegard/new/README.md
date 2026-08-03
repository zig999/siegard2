# oldisegard/new — the extracted components, in Siegard form

Seventeen components — thirteen specialized agents, three skills, and one script — carrying the knowledge
of the backend dev-phase components in `oldisegard/`, rebuilt against this framework's rules. Staging
only: nothing here is under `src/claude/`, so nothing is installed, nothing is generated into `dist/`, and
no validator in `make check` looks at it.

## The one script

`bin/run_suite.py` runs the caller's build and test commands, captures what each printed, and records the
outcome as a `test-run/1`. It is the only component here that executes anything, and it holds no
knowledge of any technology: the commands are the caller's, it composes none of them and infers none from
the repository. Three properties are worth naming because each was a choice:

- **no shell** — every command is split with `shlex` and executed directly, so `&&`, `|`, `>` and `$VAR`
  reach the command as arguments rather than being acted on;
- **no default timeout** — `foundation/0006` R21 admits only a calibrated threshold and none exists, so
  the timeout is a required input rather than a shipped constant, and there is still no unbounded run;
- **no parsing of results** — how many tests passed is not recorded. A reporter's format is stack-specific,
  and a runner that parsed it would be a target pack wearing a framework's clothes. The count is read from
  the output by whoever reads it.

`test-failure-diagnostician` consumes the `test-run/1` and executes nothing, which is what keeps a run
reproducible independently of the judgement about it.

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

- `bin/run_suite.py` was executed against a passing run, a failing step, a timeout, a command that does
  not exist, and seven refused inputs; its output validates against `test-run/1` in every case. One
  defect was found and fixed this way: a refused step created the run directory before refusing, which
  left an empty directory behind and burned the identifier for any later run.

What is **not** verified: the sixteen components other than the runner have not been exercised by a test,
an eval, or a run in a consuming repository, so under `foundation/0005` R11 they are candidates with
contracts rather than capabilities. The runner has been exercised and is the only one of the seventeen
that has.

## Open question

Should `review-change` run the suite itself? Today it does not: the caller runs `bin/run_suite.py` and
supplies the artifact, which keeps every pass in that skill read-only and puts the evidence on disk
before any judgement is made of it. The alternative — the skill running it — would be more convenient and
would re-couple running to judging one level above the agent, which is where the source framework's
review agent went wrong. Recorded rather than decided.

## What stands between this and shipping

1. **A target pack.** `security-pattern-scanner`, `architecture-pattern-scanner`, `conformance-reviewer`,
   `codebase-surveyor`, `implementer` and `test-author` read or write source in one technology's idiom.
   `docs/concepts/target-pack.md` is where stack-specific agents live, and no pack exists.
2. **The six scripts still missing.** The runner is written; these are not, and the agents point at them
   by name: a boundary validator over the fourteen contracts, the semantic checks no JSON Schema can
   express (a dependency cycle in `backlog/1`, `failures_reported` against the diagnosis count, one
   binding per task, one coverage entry per criterion supplied), an import-graph checker for the cycle,
   cross-layer and responsibility-boundary patterns, a shared-state detector, an undeclared-debt check
   against `implementation-record/1`, and a lint pass for naming, placement, type escapes and the
   prohibition list. The lint pass may not include hardcoded credentials or unparameterized SQL: the
   security taxonomy owns those as `hardcoded_secret` and `injection`, and two passes reporting one line
   would disagree about it. Until the boundary validator exists, **no artifact here is validated before
   it is consumed**, and the guarantee every agent says it does not self-report is reported by nobody.
3. **Evidence.** `foundation/0005` R11 wants a test, an eval, or a run in a consuming repository.
4. **A decision about scope.** These belong to an implementation phase this framework does not have. The
   product today goes from a request to knowledge objects and stops; `CLAUDE.md` **Scope** forbids
   introducing an abstraction before a current requirement needs it.
