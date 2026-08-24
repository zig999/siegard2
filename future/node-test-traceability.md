# Node → test traceability, and the drift budget

Status: roadmap, non-normative. A specification states what the framework must do; this file
only records what was decided about a direction, what already shipped of it, and the gates the
remaining steps wait behind. When a step here is taken, the specification and the schemas are
what gain the statement — this file never substitutes for either.

Written 2026-08-21, out of the evaluation of the maintainer's change request "Rastreabilidade
orientada por Assertions" (assertion-driven traceability). The CR's diagnosis was right and its
remedy was rejected: the node→file binding stays — `/review-change` and `/reconcile` depend on
the diff→node direction, and the CR's own validation-closure section (§18) requires it — but
the link it found missing is real, and this is the plan that closes it in the framework's own
terms.

## The finding that grounds all of this

Two facts, both verified against this tree:

1. **The node→test link dies with the plan.** A delivery holds it transiently — the
   implementation record's `nodes[]`, the proof's `tests[]`, pinned to each other by sha256 —
   and `/siegard-archive` removes the pair. The trace keeps node→source and lets node→test die,
   although both were in hand at the same instant, at implement-task's step 8. After the
   archive, "which tests prove this rule holds today?" has no answer.

2. **Scenario fails its own admission test.** `specs/metamodel.md` admits a normative class
   only if it has its own verification mode, and Scenario's stated mode is "executable as an
   acceptance test" — yet nothing downstream of `/analyse` consumes a Scenario. The class
   exists under a promise of a verification mode the framework does not honor. This, not the
   CR's metadata economics, is the decisive argument.

## Done

### P3 (reduced) — the `code` drift class listed per file — SHIPPED 2026-08-21

The measured harm (a live consumer tree at 74→76→79 findings, 16 of them collateral from one
shared service file; `bin/trace.py`'s own docstring predicted the collapse) was readability,
not the traceability model. So the fix was presentation, not semantics:

- `src/claude/bin/trace.py` — `drift_of()` still computes one fact per (node, file); `prune`,
  the `edits_freely` suppression and every receipt untouched; counts stay comparable across
  runs. A `code` finding's message now carries the reason alone (node and path already ride
  the tuple), and `code_report()` groups the listing by file: one line naming the file, the
  reason, and every binding the change staled — the shape `/reconcile` is invoked in. The
  class tally gains `over N file(s)`.
- `tests/test_trace.py` — canary `test_check_lists_the_code_class_per_file_not_per_binding`
  (two nodes, one file, one line, the phrase once); one tally assertion updated to the new
  deliberate shape. 710 passed.
- `src/claude/skills/reconcile/SKILL.md` (Locate step), `docs/how-siegard-works.md` (captured
  example), `dist/.claude/` in step.

Deliberately not changed: finding semantics, exit codes, receipts, any schema — no contract
bump.

### Decided against, with reasons — so nobody re-litigates them from scratch

- **The CR's core (drop node→file, replace with KO→assertion→observed source):** refused.
  Removing node→file loses the diff→node direction that validation closure, `/review-change`
  and `/reconcile` stand on; "no assertion failed" over a deliberately non-exhaustive test set
  is absence of evidence read as evidence; coverage observation is strictly weaker information
  than an author's reviewed `encoded_at`. Four of its rules (no percentage gate, no artificial
  assertion, specification authority, validation independence) were already doctrine here.
- **A new "Assertion" class in the metamodel:** refused — it fails the class admission test;
  Scenario already occupies that verification mode. What is missing is an edge, not a class.
- **P0 as an artifact (a token-cost ledger):** refused — no mechanical token source exists, so
  a ledger would be self-report, the vacuous-measurement class this repository has already
  caught twice. Careful per-round manual measurement remains the instrument.
- **Hunk-vs-region drift classification:** refused — bindings pin files, not regions; nothing
  records which lines a node claims, so the intersection is not computable from what the trace
  holds. Reopen only if a bind ever gains region data, which nothing currently asks for.

## Next steps, in order

### Step 1 — the trace persists the proof's test files (recommended now)

At `--bind-record` time, the delivery's transient node→test join is in hand; persist it: the
proof record's test files enter the traced node's entry, pinned by digest like every traced
file. One writer (`trace.py`), no new consumer authoring, no annotation syntax, no extractor.

Honesty constraint that shapes the field: the join is **task-granular** — a proof proves
criteria, and criteria do not map to individual nodes — so the field claims exactly that
("these tests were written by the delivery that encoded this node"), never "this test proves
this node". Name it accordingly (`proof_files`, not `proven_by`).

Touches: `schemas/trace.json` (contract bump — `siegard-plan/2` set the migration pattern:
textual, non-distributed script), `bin/trace.py`, implement-task step 8, tests, dist. Size:
comparable to P3 plus the contract bump.

### Step 2 — P1: the derived edge index (`spec.py --graph` / `--impact`), amended

The sixth projection, and the one whose consumer is an agent. `spec.py` already resolves every
reference on every validation and throws the graph away; emit it: nodes (identity, class,
subtype, context, digest) and edges (`from`, `to`, `kind`, `at`). Carries **no sentences** —
no title, no summary — so it is structurally incapable of becoming a second authority.

Amendments over the first proposal, all binding:

- **Emitted on demand, never committed** — no staleness surface.
- **Closure as receipt, not refusal**: `plan.py` reports "covers reaches N unclaimed nodes";
  promotion to a refusal only after measuring closure-size distribution on a real consumer
  specification (if the transitive closure is typically the whole spec, the check is either
  vacuous or oppressive, and the receipt is all it should ever be).
- **The index augments, never replaces, the vocabulary grep** in plan-work's situate step:
  prose-stated coupling is not an edge (a rule's statement naming a concept outside any
  reference field), and the grep is what catches it. The SKILL keeps the grep mandatory.

### Step 3 — Stage 2 of the node→test link: declared Scenario→test binding

The CR's genuine contribution, held behind two gates, both measurable:

1. **A live use Step 1 cannot answer** — one consumer round where the task-granular answer was
   insufficient and somebody had to open the tests by hand. Until that happens, this is
   contract paid for a question nobody asked.
2. **Step 2 exists** — a Scenario→test binding with no index to query it is metadata nobody
   reads, which is the disease the CR came to cure.

Bounds that survive into the design, whenever it happens:

- The concrete annotation syntax and the extractor live in the consumer's registry
  (`commands`) — this repository composes no command and knows no stack. Where no extractor
  exists, the binding does not exist: the honest narrow result.
- Pinned by digest, so a Scenario rename surfaces as drift, never as silent breakage in test
  files no framework tool reaches.
- **Declaration is never verification.** A binding says a test claims a Scenario; whether the
  test would fail is the coverage-auditor's judgment, unchanged.
- **State, never a gate.** A rule without a Scenario is reported, never "owed" — the maturity
  ladder was refused and stays refused.

## What "done" looks like

The enterprise question — *what executable evidence shows this rule is implemented, today,
long after the plan that wrote it is archived?* — answered by a query: node → trace →
proof files (Step 1 precision), or node → scenario → declared test (Step 3 precision), with
the drift report readable at the size real consumers reach (P3, shipped). The specification
remains the one normative source; tests remain evidence; the code remains free to move
structurally while the trace says who must re-judge what.
