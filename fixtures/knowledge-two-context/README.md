# Fixture: a two-context knowledge bundle

What this fixture is for, what it covers, and what it found. It exists to discharge
validation items 2 through 6 of `foundation/0003-knowledge-ontology-and-notation.md`, which that
specification requires before a maintainer may accept it.

It is a downstream-shaped case, per `CLAUDE.md` **Scope**: a Sales context that prices and
issues proposals, and a Billing context that charges for the ones Sales records as accepted.
No business rule from any real repository enters here — the domain is invented to exercise
the ontology, and nothing else reads it.

## Layout

| Path | Authored or derived |
|---|---|
| `knowledge/system.md` | authored — the three system defaults, plus `limits.body_lines` |
| `knowledge/boundary/`, `definition/`, `rule/`, `lifecycle/`, `interface/`, `process/` | authored |
| `knowledge/decision/0001-proposal-validity-window.md` | authored — an ADR node, never a knowledge object |
| `knowledge/graph.json` | **derived** — the materialized graph, contract `knowledge-graph/1` |
| `knowledge/index.md`, `glossary.md`, `context-map.md` | **derived** — the three projections R50 permits |
| `ontology-utilization.md` | **derived** — the R52 measurement |

Regenerate every derived file with `make knowledge`. `make validate` verifies them with
`--check` and mutates nothing.

Every knowledge object carries `status: proposed`. `docs/adr/README.md` restricts a status
change to a maintainer and covers every artifact class carrying `status`, so an agent
authoring this fixture may not write `accepted`. Nothing in the ontology branches on status,
so coverage is unaffected.

## What it covers

| Requirement of foundation/0003 | Where the evidence is |
|---|---|
| Item 2 — eleven rejections the contract must make | `tests/test_knowledge_rejections.py` |
| Item 3 — R15, R11 with both shorthands, R18, both outcomes each | `tests/test_knowledge_checks.py` |
| Item 4 — two contexts, six node types, every traversed edge | `tests/test_knowledge_fixture.py` |
| Item 5 — projections generated, regeneration byte-identical | `tests/test_projections.py` |
| Item 6 — the R52 measurement recorded | `ontology-utilization.md` |

Counts, as measured: 27 knowledge objects and one ADR across two bounded contexts and three
aggregates, 61 edges, one `superseded_by` reference, every declared edge kind instantiated, and
12 of the closed `ddd` vocabulary's values exercised. Every check in
`scripts/validate_knowledge.py` was confirmed to have at least one covering test by disabling
each check in turn and observing the suite fail.

Item 1 is not discharged here and cannot be: it requires a maintainer to accept the
specification.

## What building it found, and what was repaired

Eleven findings. Each is a statement about `foundation/0003`, not about this fixture. Six were
contradictions or gaps and have been repaired in the specification itself; one was a placement
decision a maintainer has since settled; four remain open. None of the four is a contradiction —
three are limits of what a mechanism can decide, and one is a redundant check kept deliberately.

### Repaired in foundation/0003

Findings 1 through 6. Each repair carries tests for both outcomes, and each was mutation-checked
by reverting the repair and observing the suite fail.

1. **The closed edge vocabulary of R17 omitted two references that must resolve.** A `list`
   attribute's `of` and a rejection's `error` both name knowledge-object ids, and R29 and the
   totality check of R11 require both to resolve — which nothing does without an edge. Both are
   now rows in the table, structural and traversed at depth 1, alongside the `ref` target and
   the transition guard they are indistinguishable from. R17 now also states the closure
   positively: every field that names a node and must resolve is an edge, except `superseded_by`.
   `tests/test_edge_table_agreement.py` reads the specification's own table and fails if the
   module drifts from it again.

2. **R9 forced a false statement for two `ddd` values.** It required `identity` of every
   `definition`, including `ddd: value-object` — which is *defined* by holding no identity — and
   `ddd: domain-error`. R9 now requires `identity` of an entity, aggregate root, or read model
   and forbids it of the other two, expressed as a conditional in the schema.

3. **R10's "system boundary" had no representable form.** A `quality-attribute` rule had to
   declare "the one boundary that is not a bounded context", while `boundary.ddd` was closed to
   `bounded-context | aggregate` — so that one `ddd` value of `rule` was unusable. Such a rule now
   declares the bounded context it constrains, like every other rule, and a quality attribute
   spanning contexts is recorded once per context or is stack knowledge. Admitting a third
   boundary kind was rejected for the reason the DDD mapping table already gives for not
   modelling the domain as a node: it would hold one instance.
   `rule/sales/proposal-response-time.md` exercises the fifth `ddd` value the fixture previously
   could not.

4. **R52's three removal candidates were acted on.** `references`, `supersedes`, and
   `superseded_by` were read by no resolution. `references` was removed outright: authored,
   traversed by nothing, required by no other statement. `supersedes` was removed as the
   symmetric inverse R52 names explicitly. `superseded_by` could **not** be removed — R40
   requires it — so it moved out of the edge table into a resolvable reference: the target must
   resolve under R22, and expansion must never follow it. `Graph.supersessions` holds those
   outside `Graph.edges`, so no traversal can reach one by accident rather than by every
   consumer remembering to filter. Every edge that remains is traversed and instantiated.

5. **A cross-aggregate `list` could not declare its binding.** R28 required `binding:
   by-identity` of a `ref` leaving an aggregate, and `list` had no `binding` parameter — so the
   identical crossing was rejected as a `ref` and accepted as a `list`, leaving R28 claiming a
   mechanical check it delivered for half the cases. The asymmetry was demonstrated before it
   was repaired: pointing `proposal.items` at a definition in another aggregate produced no
   binding complaint, while the same target as a `ref` was named and rejected. `list` now
   carries `binding` with the same enum and the same rule, and `check_aggregate_binding` reads
   one table of referencing primitives instead of branching on `ref`.

   Deriving `binding` from the two boundaries instead of declaring it was considered and
   rejected. It is derivable, so it buys nothing for generation — but spec 0002 R2 admits an
   element that increases the capability to *verify* automatically, and the declaration is
   exactly that: it catches an author who believes two definitions share an aggregate when they
   do not. That is why `ref` required it, and why `list` requires it rather than both becoming
   derived. `definition/sales/customer-proposals.md` exercises the accepted shape, and
   `tests/test_knowledge_repairs.py` compares the two verdicts rather than asserting each alone.

6. **The cardinality column was transcribed but unchecked.** Edge names and traversal flags were
   compared against the specification mechanically; cardinality was not. The column mixed
   "0..n", "exactly 1", "≤ 2", and "1 per relationship", so no parser could read it — and the
   numbers a validator enforces were the one part of the table nothing verified.

   The cause was not the notation but the column: it answered three questions at once — edges
   out of a node, edges into a node, and targets named by one attribute. It is now two columns,
   **Out** and **In**, both in `<min>..<max>` with `n` for unbounded, and the third question
   moved to prose where it belongs: how many targets one `ref` or one transition names is a
   frontmatter fact the schema already enforces, not a graph bound. A definition holding three
   `ref` attributes declares three `attributes[].target` edges, which is why every such row is
   `0..n` out — the old cell said "1 per `ref` attribute" and meant something else entirely.

   `tests/test_edge_table_agreement.py` now parses and compares every column: names, Out, In,
   traversal, and depth. Mutation-checked on both sides — loosening the inverse bound on
   `lifecycle.subject` or changing a depth fails, in the specification or in the module, and
   reverting the column to prose fails all nine assertions rather than passing vacuously.

### Settled by a maintainer

7. **R48's ceiling had no home.** The specification required a validator to enforce a body length
   ceiling and deferred both the value and the schema of the file that might hold it. A number
   invented in the validator would be the hidden default `.claude/rules/distribution.md` rejects,
   so this fixture declared it as `limits.body_lines` in `knowledge/system.md` — a placement an
   agent chose inside a space the specification had left open, which is why it was raised rather
   than left to look like a decision.

   A maintainer settled it on 2026-07-30, and R48 now names the home: the ceiling MUST be declared
   there, a validator MUST NOT supply a default, and an absent field MUST be reported as R48 being
   unenforceable rather than assumed. The *value* remains deferred to R52's measurement; its home
   no longer is.

### Still open

8. **R18's forward cardinality is unreachable through valid input.** Every forward bound is
   `0..n`, or `1..1` over a scalar frontmatter field, so `schemas/knowledge-object.json`
   rejects a violation before a graph exists. Only the inverse bound on `lifecycle.subject`
   needs the graph. The forward mechanism is proven against a hand-built graph in
   `tests/test_knowledge_rejections.py`, and that test says so. Kept rather than deleted: it
   costs nothing and it is the check that fires first if a scalar field ever becomes a list.

9. **Two residuals of the edge-table comparison.** The **In** column's minimum is not modelled —
   nothing requires a node to be referenced, and whether an unreferenced one is a defect is the
   orphan rule of R22 rather than a cardinality bound. And the zero-`boundary` exception for a
   bounded-context boundary cannot live in a table cell, so it is prose beside the table and one
   named function in the validator: the comparison checks the rule, not its exception.

10. **Two clauses of R46 are not mechanically enforceable**: that a body carries no rationale,
   history, alternatives, or motivating narrative, and that a body is not the only place a
   machine-read fact appears. Both are judgments about meaning.
   `scripts/validate_knowledge.py` names them as unenforced rather than leaving a reader to
   assume coverage.

11. **R45's pronoun check is bounded, not closed.** It rejects personal and possessive
   pronouns in a normative statement. Demonstratives are excluded deliberately: in "this
   system MUST", `this` is a determiner, and rejecting it would reject conforming text. A
   paraphrase that avoids the listed words passes.
