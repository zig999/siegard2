# The generation pipeline, without a pack

A pack declaration with no producers behind it, and the four artifacts `foundation/0004` puts between a
knowledge base and a written file.

That the pack is a stub is the point. The pipeline is framework-owned and stack-independent —
`foundation/0012` R4 keeps the artifact-class schemas in the framework, and `foundation/0004` R8 closes the
class vocabulary there — so exercising it against a real pack would conflate *the pipeline works*
with *the pack works*. Nothing here produces a file.

## What it holds

| Path | What it is |
|---|---|
| `generation-run.json` | how the rest was produced: the roots, and every identifier, stated rather than minted |
| `pack-declaration.json` | four classes across both tracks, from four node types |
| `generation-scope.json` | **derived.** 14 members frozen from one root |
| `placement-decision.json` | 13 paths the pack proposed, validated and frozen |
| `generation-plan.json` | **derived.** 13 entries, all `new` on a first generation |
| `generation-manifest.json` | what a first run would transcribe, locking every path |

`tests/test_generation_pipeline.py` recomputes the scope and the plan from `generation-run.json` and
asserts they equal the committed copies. A fixture that could drift from its inputs would be a second
authority for a scope the graph already determines.

## What it is evidence for

- **The plan is derivable without a model.** Four inputs — scope, declaration, manifest, frozen
  placement — and `foundation/0004` R23 admits nothing else. A test reads the module for network and
  subprocess imports rather than taking the claim on trust.
- **Byte identity at the plan, which R29 requires separately from the output.** A test covering only
  produced source cannot distinguish a nondeterministic plan from a nondeterministic template, and
  this half is cheaper and sharper because it holds whether or not any template is correct.
- **A first generation and a regeneration are different.** Every entry is `new` against an empty
  manifest and `locked` against the committed one, with identical paths. R31 reads the path back
  rather than asking again, and a test proves a *changed* placement decision cannot override a lock —
  without which R31 would have nothing to read.
- **Scope fails closed.** An unresolvable root and an unresolvable member each raise. `foundation/0004`
  R21 forbids applying `foundation/0001` R13's fail-soft here, which is why this and the context package
  are separate artifacts (R22): their failure semantics are opposite, and one artifact serving both
  would have to pick one.
- **A node type yielding nothing is reported.** `boundary` yields no class under this declaration, and
  R11 makes silence about that read as coverage that does not exist.
- **Placement rejects rather than repairs.** A path outside the repository, a class the pack does not
  declare, a knowledge object outside the scope, two entries claiming one path, and a decision frozen
  against another scope are each rejected, and none is normalized.

## What it is not evidence for

- **No artifact was produced.** There is no template and no judged producer here, so nothing was
  written and nothing was verified by regenerate-and-diff. The manifest's content hashes are
  placeholders, and the test asserts the *paths* agree with the plan rather than that any file exists.
- **No pack was admitted.** `foundation/0012` R13 admits a pack with a fixture demonstrating it serves any
  repository on its stack. This declares four classes and ships no producer for any of them, so
  `foundation/0004` R51's one-producer-per-class rule is unexercised.
- **Placement was not judged.** The paths follow one obvious convention written into the test harness,
  standing in for what a pack's agent would decide. Which producer inside a pack proposes a path is
  the question `foundation/0004` R13 leaves open, and a stub pack cannot answer it.
