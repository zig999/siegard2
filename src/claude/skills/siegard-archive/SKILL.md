---
name: siegard-archive
description: Removes closed initiatives from the working tree so their history survives only in git — `bin/archive.py` decides each candidate mechanically (closed, committed, still valid as history) and removes work and delivery together and whole, touching nothing that carries understanding — the project file, the trace, the specification with its decision log, and the reconciliation records all stay. It never commits, tags or stages anything; the report hands the git commands ready, in order, and the git acts are the human's. Use when the human asks to archive closed initiatives, prune delivered history from the branch, or keep the working tree lean. Not for live initiatives, and not for deleting anything else.
disable-model-invocation: true
effort: low
---

You run one script that removes closed history from the working tree, so it survives only in git,
and you stop. One invocation, one archiving act — a working-tree change like any other skill's:
the human reviews it and the human commits it.

The framework keeps **understanding** in the specification (with the decision logs beside its
nodes), `siegard-trace.json`, `siegard-reconcile/` and the code itself, and keeps **evidence** —
plans, delivery records, proofs, captured runs, reviews — in the work and delivery roots. Evidence
may leave the tree, because git history holds it; nothing that carries understanding ever does.
The reconciliation records live beside the trace because what they justify outlives every plan
and delivery root, and archiving them would leave binds resting on judgments held nowhere.

## Required inputs

A missing input is a stop, not a default:

1. **the project root** — where `siegard.json` lives, named by the human. «Where the invocation
   names none, the project root is the git toplevel of the session's working directory, as
   `bin/project.py --here` resolves it, and only where that toplevel holds `siegard.json`»
   (SPEC-010 R6): there, `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/project.py --here`
   runs before the act, and its `project_root:` line is the root. Its refusal is a stop.
2. **the scope** — which initiatives, by slug, or the literal ask to archive everything closed.
   Never inferred: removal is the one act whose want only the human can state, which is also
   why this skill is closed to model invocation.

Optionally, **the target** — a key of `siegard.json`'s `targets`. Each delivery is checked
against the targets its own records name, so the target is asked for only where a delivery's
records name none and the project declares more than one; the script's report says so, and the
human names it for the next invocation.

`${CLAUDE_PLUGIN_ROOT}` is set where this skill runs as an installed plugin. Where it is not,
the plugin root is the directory that holds `schemas/` and `bin/` side by side.

## The act

Run, once:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/archive.py --remove <project-root> (--all | <slug>...) [--target <key>]
```

`--all` is the ask to archive everything closed; slugs are the ask to archive those. Where the
human asked only what would leave, run `--check` in place of `--remove`: it changes nothing.

The script is where the criteria live — closed, committed with nothing git ignores or does not
track inside the pair, valid as history under `bin/plan.py --check` (the closed plan held to
`${CLAUDE_PLUGIN_ROOT}/schemas/plan.json`) and `bin/deliver.py --check`, and removed as a whole
pair. Its `--help` states them; read it there, never restate it from memory. It reads every
criterion again on `--remove`, removes only the pairs that pass, and runs no git command that
writes.

A skipped initiative is not yours to repair. Where the script names what answers it — a
derivation of an index never derived, or a `--target` — hand that line on as printed; where it
says nothing here repairs it, the entry point that owns the problem does, and you name the
problem as the script printed it.

## Report, and stop

Open as «A handoff opens with what needs the person, and explains after» (SPEC-006 R1)
states; what follows is the report that opening sits above. What needs the person is the two git
acts, and any initiative skipped with the line that answers it.

Relay the script's output whole and in its order: each initiative eligible or skipped with its
criterion, the pairs removed, the git acts — the tag on the commit the removal starts from, then
the removal's own commit, pathspec-scoped to the pairs removed — the line that brings any pair
back, whether `HEAD` sits on a remote branch, and what still answers from what remains. The git
acts are the human's, ready to paste; the diff, deletions and all, is the review.

Then stop.

## What you never do

- Infer the scope, widen it, or name a slug the ask did not reach because it looked finished.
- Remove, move or edit anything yourself — the script removes, and only what passed.
- Repair what a criterion refused, or run the derivation a skipped initiative's line names.
- Commit, stage, tag, or otherwise change the consumer's git state.
