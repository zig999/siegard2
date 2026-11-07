# The project's standard

Read with the inputs, and again at step 1 when the registry check runs.

## What it is for here

**The project's standard** is the path to the registry of rules the project set for itself. It
plays one part in planning and no other: a registry states the artifacts its rules presuppose — a
manifest, a compiler configuration — and where the target tree does not hold one, building it is
work this plan holds or nothing does. The specification has no node for a manifest and should not,
and `/implement-task` refuses to write source while the absence stands. The rules themselves are
not a plan's business: a plan writes no source.

## Resolving it

It resolves in this order, from the same `project.py` run the inputs name, and the report says
which step answered:

1. **A naming in the invocation wins**, unlike the roots.
2. Otherwise the file's `standard` answers **for the target**. `project.py` prints one `standard:`
   line for a one-target project, or one `standard <target>:` line per target the file declares one
   for; the line for this invocation's target is the answer, never another target's. `null` there
   declares that the target has none: take the narrow path without asking again.
3. Where neither answers — no naming, no file, no field, or no entry for this target — the standard
   joins the single stop of absent inputs, and the report carries the `/siegard-config` invocation
   that declares it for this target, ready to paste.

A file that does not hold together is a stop reported verbatim. A naming that overrode a differing
file is reported with both. Below, a standard "named" means resolved by either step.

## At step 1

`deliver.py --standard <the registry> --against <target-source-root> --specification
<specification-root>`:

- **A registry that does not hold together is a stop**, reported verbatim: fixing it is its
  owner's. So is a step deciding a constraint the specification does not hold.
- **An artifact it presupposes and the tree does not hold is not a stop** — it is what this check
  is for. Keep, for each: the path, what the registry says it provides, and the rules it named as
  unanswerable while it is absent. That set goes to step 3, where it may add one task the scope
  never asked for.
- **Keep what it printed against the specification**: which constraints a step decides, and which
  none does. The second are held by reading alone, and the report names them beside the tasks that
  implement them.
