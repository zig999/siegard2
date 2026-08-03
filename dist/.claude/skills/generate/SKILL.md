---
name: generate
description: Produces source from the knowledge base through the active target pack, deriving and validating a plan before writing anything. Use when a knowledge change has been accepted and the code it implies must be produced or regenerated. Not for authoring knowledge, and not for deciding what the change should say.
disable-model-invocation: true
---

You run generation. `specs/0004` R18 makes this the entry point, and everything it drives is
mechanical except one step.

Two rules govern everything below, and neither is yours to relax:

- **You write nothing before the plan validates.** The plan is producible and inspectable without
  touching a file, which is what makes validating it first possible. A plan that fails validation is
  rejected, never repaired.
- **You supply no domain fact.** If the knowledge base does not hold something a template needs, that
  is a generative gap and it blocks the scope. Inventing it would author a domain fact in the
  framework, which is what generative completeness exists to prevent.

## Required inputs

Collect these before running anything. A missing input is a stop, not a default:

1. **the framework script root** — the directory holding `generation_lib.py` and its siblings.
   Installation decides this path; a component that guessed it would fail silently in a repository
   laid out differently.
2. **the knowledge root**, and the contract governing it.
3. **the active pack** and its declaration. `specs/0004` R17: the framework ships no default pack, and
   a missing or ambiguous one blocks generation with a report naming what is missing. A pack inferred
   at run time is a hidden default and is rejected.
4. **the roots** the scope expands from, and the change request they answer.
5. **the generation manifest**, if the repository has one. Its absence means a first generation; do
   not create one to make the run look ordinary.
6. **an id for the scope, the placement decision, and the plan** — `gs_`, `pd_`, and `gp_` followed by
   eight hex digits. You own the clock and the identifiers; the framework refuses to invent either.

## The order, and why it cannot be rearranged

```
scope  →  demand  →  placement  →  freeze  →  plan  →  validate  →  write  →  manifest
```

1. **Resolve the scope.** It fails closed: a member that cannot be resolved blocks the run. This is
   the opposite of context resolution, which degrades and continues — the two are separate artifacts
   because their failure semantics are opposite.
2. **Derive the demand** from the scope and the pack's declaration. A node type that yields no class
   under the active pack is **reported**, not skipped in silence.
3. **Delegate placement** for every artifact the manifest does not already lock. This is the one
   judged step, and the pack owns it.
4. **Validate and freeze the placement decision** before deriving anything. A path outside the
   repository, a class the pack does not declare, or two entries claiming one path each reject the
   whole decision.
5. **Derive the plan.** Four inputs, no model. A locked entry takes its path from the manifest; a new
   one from the frozen decision.
6. **Validate the plan.** Every reference resolves, every class is declared, no two entries claim one
   path, and every locked path still exists. A target-path collision is a defect to report — there is
   no policy that resolves one, because two objects competing for one path is a modelling error or an
   agent error and a silent winner hides both.
7. **Write**, then **record the manifest** in the same run. A run that ends without producing an
   artifact locks no path for it.

## What you never do

- Decide a path yourself. Placement is the pack's, and on a later run it is the manifest's.
- Re-decide a locked path. Moving a produced file is an explicit recorded unlock; a silent relocation
  appears in a diff as a deletion and an addition, indistinguishable from a change in knowledge.
- Edit a produced file. Extension happens through an extension point the plan declares, in a separate
  hand-authored file.
- Report a passing conformance suite as byte identity, or a first generation as a regeneration. They
  are different claims and stating one for the other is a false report.

## Result

Report the scope size, the node types that yielded nothing, the plan entry count split by locked and
new, and the manifest path. Where the run blocked, name the condition and the artifact it blocked on —
a blocked generation that reports only failure leaves the caller re-running it to find out why.
