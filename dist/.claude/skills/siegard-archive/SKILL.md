---
name: siegard-archive
description: Removes closed initiatives from the working tree so their history survives only in git — verifies each candidate mechanically (the human's closure marker present, the pair's tree clean and committed, the closed plan and its delivery still validating) and removes work and delivery together and whole, touching nothing that carries understanding — the project file, the trace, the specification with its decision log, and the reconciliation records all stay. It never commits, tags or stages anything; the report hands the git commands ready, in order, and the git acts are the human's. Use when the human asks to archive closed initiatives, prune delivered history from the branch, or keep the working tree lean. Not for live initiatives, and not for deleting anything else.
disable-model-invocation: true
effort: low
---

You remove closed history from the working tree, so it survives only in git, and you stop. One
invocation, one archiving act — and the act is a working-tree change like any other skill's:
the human reviews it and the human commits it.

The boundary this skill exists to hold: the framework keeps **understanding** in the
specification (with its decision log), `siegard-trace.json`, `siegard-reconcile/` and the code
itself, and keeps **evidence** — plans, delivery records, proofs, captured runs, reviews — in
the work and delivery roots. Evidence may leave the tree, because git history holds it; nothing
that carries understanding ever does. The reconciliation records in particular live beside the
trace *because* what they justify outlives every plan and delivery root — a bind resting on a
judgment held nowhere is exactly what they exist to prevent, and archiving them would create
it.

## Required inputs

A missing input is a stop, not a default:

1. **the project root** — where `siegard.json` lives. Named by the human; inferred rather than
   named, its absence is a stop.
2. **the scope** — which initiatives, by slug, or the literal ask to archive everything closed.
   Never inferred: removal is the one act whose want only the human can state, which is also
   why this skill is closed to model invocation.
3. **the target** — which of the project's target source roots the initiatives delivered into,
   by the key `siegard.json`'s `targets` names it. Where `targets` declares exactly one key and
   the invocation names none, that key is the target: decided and disclosed, never asked.

Run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/project.py <project-root>` once, before anything
else. `work_root`, `delivery_root`, `targets` and `specification_root` answer only from here,
and where the file does not declare one, that is a stop — the report carries the
`/siegard-config` invocation ready to paste.

`${CLAUDE_PLUGIN_ROOT}` is set where this skill runs as an installed plugin. Where it is not,
the plugin root is the directory that holds `schemas/` and `bin/` side by side — in a vendored
install, the `.claude/` directory this skill's tree sits under.

## The criteria

Per initiative, in order; the first that fails skips that initiative — reported with the
criterion that failed, repaired by nothing here — and the rest still proceed:

1. **Closed.** `closure.md` present at `work_root/<slug>`. A live initiative is never eligible,
   whatever the ask says: closing is its own act, through `/plan-work`, and archiving is not a
   way to end work.
2. **Committed.** `git status --porcelain -- <work-root>/<slug> <delivery-root>/<slug>` prints
   nothing. A clean pair is what makes "removed" mean "recoverable": the history about to leave
   the tree is already in a commit. A pair not under git control fails here for the same
   reason — without git there is no archive, only deletion.
3. **Valid history.** `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/plan.py --check <work-root>/<slug>`
   — a closed plan validates without the specification, and its index, held to
   `${CLAUDE_PLUGIN_ROOT}/schemas/plan.json`, still matches the files — and
   `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --check <delivery-root>/<slug>
   <work-root>/<slug> <target-source-root>` over the pair. Corrupted history is not archived:
   it is reported, whole, while it is still in front of somebody.
4. **The pair, whole.** `work_root/<slug>` and `delivery_root/<slug>` leave together and
   entire, never one without the other and never partially — the runs inside a delivery are
   required fields of its records, so a delivery stripped of them is records that no longer
   validate, and a delivery removed under a kept live plan is a plan whose every task reads as
   undelivered again. Where one side does not exist on disk, say so and archive what does.

## The act

Remove the eligible directories from the working tree. Nothing else: no commit, no tag, no
staging, no touch on `siegard.json`, `siegard-trace.json`, the specification root, its
decision log, or `siegard-reconcile/` — and nothing outside the named pairs, however
archivable it looks.

## Report, and stop

- per initiative archived: the two directories removed, with file counts;
- per initiative skipped: which criterion failed, verbatim where a command said it;
- the git acts, ready to paste and in this order — both the human's, never this skill's:
  1. `git tag -a archive/<date> -m "last tree holding: <slugs>"` — the tree was clean, so
     HEAD is the pre-removal state, and the tag is what makes recovery one command;
  2. `git add -A && git commit` — the removal itself, reviewed as a diff like any other;
- the recovery line: `git checkout archive/<date> -- <delivery-root>/<slug>` brings any of it
  back;
- one honesty line: a clean tree proves the history is committed, not that it is pushed — in a
  repository with no remote, git is the only copy;
- what still answers from what remains: run
  `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/spec.py <specification-root>` and
  `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --check <target-source-root>` and report both
  verbatim — the understanding stayed, and these two are the proof.

Then stop. The diff — deletions and all — is the review, and it belongs to a person.

## What you never do

- Archive a live initiative, or one whose pair the tree holds uncommitted changes for.
- Remove, trim or touch `siegard-trace.json`, `siegard.json`, the specification root, the
  decision log, or `siegard-reconcile/` — the understanding set is not evidence, and no ask
  makes it eligible.
- Split a pair: a work root without its delivery, a delivery without its plan, a delivery
  without its runs.
- Commit, tag, stage, push, or otherwise change the consumer's git state — the report hands
  the commands, and running them is the human's.
- Infer the scope, widen it, or archive anything the ask did not reach because it looked
  finished.
- Repair what a criterion refused — a stale index, a broken record, a dirty tree are reported,
  and fixing them belongs to the entry points that own them.
