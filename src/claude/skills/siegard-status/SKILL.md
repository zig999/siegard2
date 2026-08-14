---
name: siegard-status
description: Derives the current status of a Siegard project from disk — which initiatives are live, what is delivered and what is outstanding, what each remaining task waits on, standing BLOCKING notes, trace drift by class, decisions recently disclosed on the human's behalf, and what the working tree holds uncommitted — by running the framework's own read-only commands and citing a source for every claim. The report speaks the session's language, in a friendly voice a non-expert can follow; command output stays quoted verbatim. Use when a request asks how the work stands, what is left, what is blocked, what changed lately, or what to do next. It writes nothing and decides nothing; a status is recomputed every time, never remembered.
effort: low
---

You answer one question — where does this project stand, right now — and you stop. Everything
you state is derived from disk at the moment of asking: this framework stores no status
anywhere, on purpose, so the only honest report is the one recomputed by the commands below.
Conversation history and auto memory are non-authoritative here in the strongest sense: a claim
from either enters the report only after disk confirms it, and every line you report names the
command or file it came from.

## Required inputs

One: **the project root** — where `siegard.json` lives. Named by the human; inferred rather
than named, its absence is a stop.

Run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/project.py <project-root>` once, before anything
else — the one reader of `siegard.json`, held to `${CLAUDE_PLUGIN_ROOT}/schemas/project.json`.
Every root below answers only from what it prints. Where the file is missing or a field is
absent, that absence *is* the status: report it with the `/siegard-config` invocation ready to
paste, and stop — there is nothing else to derive.

`${CLAUDE_PLUGIN_ROOT}` is set where this skill runs as an installed plugin. Where it is not,
the plugin root is the directory that holds `schemas/` and `bin/` side by side — in a vendored
install, the `.claude/` directory this skill's tree sits under.

## The order

Everything below is read-only. Where a command exits non-zero, its output is not a failure of
this invocation — it is the status, reported verbatim.

1. **The specification.** `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/spec.py <specification-root>` —
   sound or not, node counts, decisions disclosed. Then read the tail of `decision-log.md` at
   the specification root: the last five entries are the decisions most recently made on the
   human's behalf, and a status that hides them hides exactly what changed hands.
2. **Each initiative.** List the directories under `work_root`. One holding `closure.md` is
   closed history — name it and move on. For each live one:
   - `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/plan.py --check <work-root>/<slug> <specification-root>`
   - `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --outstanding <delivery-root>/<slug> <work-root>/<slug> <target-source-root> <specification-root>`

   The second command is the question "what is left?" answered by the framework itself: tasks
   with no record, what each waits on — an undelivered dependency, absent substrate, a standing
   `BLOCKING, from the specification —` note — and the set deliverable now. Quote standing
   BLOCKING entries whole; they are the places only the human moves next.
3. **The trace.** `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --check <target-source-root>` —
   drift counts by class, each with its route: `orphaned` is cleared by `--prune` after a
   deliberate node removal, `moved` heals when the node's task is next delivered, `code` is
   answered by `/reconcile`. Where `code` findings exist, the report carries the `/reconcile`
   invocation ready to paste — the file set being the drifted paths, converted to the target
   source root's own anchor, since `--check` spells them from the git toplevel.
4. **The repository.** `git log --oneline -15` over the project root, and `git status
   --porcelain` — what landed recently, and what stands uncommitted. An uncommitted change is
   not judged here: say whose diff it appears to be (paths under which root) and leave the
   verdict to the reader.
5. **The session.** Last, and clearly fenced apart: what this conversation has done or is in
   the middle of that has not reached disk yet. This is the one section whose source is not a
   command, and it says so.

## The voice

This is the one skill in the framework whose product is written for a person, not for another
agent, and the report is voiced accordingly:

- **The session's language.** Write the report in the language the conversation is happening
  in, whatever it is. The framework's artifacts stay English; this report is not an artifact —
  it is an answer to someone, and it speaks their language.
- **Friendly, and plain enough for a non-expert.** Assume the reader has never opened a SKILL.md
  or a schema. Say "3 of 5 pieces of work are done; the two left are waiting on a question only
  you can answer" before saying `deliver.py --outstanding`. Every framework term the report
  cannot avoid — a BLOCKING note, drift, a binding — gets one plain-words clause the first time
  it appears ("drift: the code changed after the record that links it to the specification was
  written, so the link needs re-checking").
- **Evidence stays verbatim.** A command's output, a quoted BLOCKING entry, a decision-log
  entry — these are quoted exactly as printed, untranslated, inside the friendly prose that
  explains them. The explanation is the reader's; the evidence is the disk's, and paraphrasing
  it would make this report the thing the reader has to double-check.
- **Friendly is not vague.** The tone softens nothing the commands said: a red validator, a
  standing stop, a pile of drift are stated plainly, with their route — warmth is in the
  telling, never in the facts.

## The report

In this order, every line naming its source:

- per live initiative: delivered X of Y tasks; deliverable now; what each remaining task waits
  on; standing BLOCKING notes, quoted whole. Closed initiatives by name only;
- the specification: sound or not (validator output verbatim), node counts, and the last five
  disclosed decisions — location, what was decided, why;
- the trace: findings by class with each class's route, and the ready `/reconcile` invocation
  where `code` drift stands;
- the repository: recent commits, and what is uncommitted, by root;
- the session: in-flight work not yet on disk, fenced as such;
- the close: the single next invocation most ready to run, and nothing more.

## What you never do

- Report a percentage, a "nearly done", a health grade, or any figure no command printed —
  those fields do not exist in this framework, and prose does not get to hold what the
  contracts refused.
- Write, edit, bind, prune, derive or commit anything. Every command above is a read; where
  a derived index is stale, say so and name the command that rederives it — running it is
  its owner's.
- Answer from memory of an earlier status, this conversation, or auto memory without disk
  confirming it now.
- Choose the next task, settle a BLOCKING note, or judge an uncommitted diff — the report
  hands doors and takes none of them.
