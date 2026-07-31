# The first target pack

`typescript-node`, declaring all twelve artifact classes of the closed vocabulary: ten on the
deterministic track with a template each, two on the judged track with an agent each.

## Where it lives, and why not `src/claude/`

`foundation/0012` **Outstanding evidence** item 5 records an unresolved conflict between `foundation/0004` R13, which puts a
pack's agents and templates under `src/claude/`, and `foundation/0008` R23, which keeps every pack out of
the framework distribution. Both are accepted at equal precedence with no supersession, so the conflict rule
of `CLAUDE.md` **Where authority lives** applies and a maintainer decides.

A *fixture* pack does not turn on that decision, because it is not distributed at all. This is one,
and the framework generator does not ship it — a test in `tests/test_generator.py` asserts no
`packs/` reaches the distribution, and this tree is under `fixtures/` where nothing collects it.

## What it holds

| Path | What it is |
|---|---|
| `pack-declaration.json` | identity, version, and twelve classes with their track and node types |
| `templates/expand.py` | the ten deterministic producers |
| `agents/validator-producer.md` | the judged producer for `validator` |
| `agents/orchestration-producer.md` | the judged producer for `orchestration` |

## What it is evidence for

- **One producer per declared class** (`foundation/0004` R51, `foundation/0006` R5). Ten templates and two
  agents, asserted against the declaration rather than counted by hand.
- **Byte identity on the deterministic track** (`foundation/0004` R2). Every template is run twice over
  the same knowledge object and compared. That is what backs the track assignment: `foundation/0011` R2
  says a template that cannot hold byte identity is not a weaker template — its class moves to the
  judged track.
- **A template reads only its inputs** (`foundation/0011` R4), read off the module by AST rather than
  asserted in prose: no clock, no environment, no randomness, no network, no file, no `open`.
- **Nothing is minted** (R5). The pack version is an argument, and a test proves two versions
  produce different output — so it is genuinely an input rather than a constant with a parameter
  wrapped around it.
- **No default is substituted for a domain fact** (R10, `foundation/0004` R39). A definition with no
  attributes, a lifecycle with no transitions, and an interface with no version each fail naming the
  field. A test walks the AST for any two-argument `.get()`, which is what a silent default looks
  like.
- **The attribute vocabulary is total.** Every type `schemas/knowledge-object.json` admits has a
  mapping, asserted against the schema. A type the base can hold and the pack cannot express would
  otherwise fail at expansion, which is the worst place to find a gap in coverage.
- **No domain knowledge, and no downstream-specific value** (R13, R14). A test extracts the strings
  the module *evaluates* — excluding docstrings, where a rationale legitimately lives — and asserts
  none names an object in the fixture base or a term from its domain.
- **A generative gap is named rather than filled.** `ko.rule.sales.proposal-validity` carries no
  `examples`, so no conformance test can be generated from it, and the template says so.
  `foundation/0004` R38 blocks the scope; it does not invent an example.

## What it is not evidence for

- **Nothing was written.** The templates return strings; no generation run has executed them through
  a plan, and no `regenerate-and-diff` has compared produced source against a committed tree. That is
  the phase after this one.
- **The judged track is unexercised.** Both agents are authored and neither has run, so `foundation/0004`
  R3 — a judged artifact verified against a generated conformance suite — is stated and untested. The
  suite exists; the thing it would check does not.
- **`foundation/0012` R13's admission is not met.** A pack is admitted with a fixture demonstrating it
  serves *any* repository on its stack, and this runs against one knowledge base. Running against a
  second is what would distinguish a pack from an extraction of one repository's conventions.
- **Placement is not decided here.** Which producer inside a pack proposes a path is what
  `foundation/0004` R13 leaves open, and this pack proposes none — `fixtures/pack-minimal/` supplies paths
  from a test harness instead.
