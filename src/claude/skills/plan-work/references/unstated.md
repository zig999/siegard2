# A fact the specification does not state

Read at step 4 when a binder returns a note classed `unstated`, and in a decided-fact increment.

The fact is settled before any task it touches is written, and the note never reaches a task file.

## Hold it to the cut first

Grep the specification root for the fact's terms. A fact some node outside the candidates already
states is a cut problem, not a silence: grow the epic's `covers` or move the task, and re-run step
4. What survives is a genuine silence. Deduplicate the survivors by fact — two skeletons resting on
one fact are one decision.

## Spawn one decider per fact

**The decider is spawned, never offered**: a fact a binder returns as unstated is not a question
for the person — «never left standing as a stop for a person whose only move is to trigger the
decision» (SPEC-001 R13). A node the person excluded from this scope is `uncovered` on the epic with
their why; a fact that is not excluded is decided. The disclosure is the log entry and the report,
after the write; a person who disagrees reverts the entry as an ordinary change.

Spawn one `siegard:unstated-fact-decider` subagent per fact — its judgment lives at
`${CLAUDE_PLUGIN_ROOT}/agents/unstated-fact-decider.md` — passing:

- the fact exactly as the note's `fact` carries it;
- the impact-set file paths under the specification root, plus the decision log beside each where
  one exists (`<slug>.log.md`);
- the scope's paths under `intake/`;
- the specification schema paths — one per class, the files under the plugin root's
  `schemas/spec/`, the same seven `/analyse` reads.

**Never the skeleton, never the note's own text, never a binder's reasoning**: the decider is blind
to the cut, so the specification is never bent to fit tasks already written.

## Write what comes back

Read the return from where the subagent answered — its transcript, or a return saved from it —
never from the notification that relays it.

- **`stated` or `decided`**: write the edits verbatim at the paths they name. Then append the
  returned log entry, where the return carries one — every `decided`, and a `stated` whose fact was
  read under `intake/` — through the writer, never by hand: `python3 -B
  ${CLAUDE_PLUGIN_ROOT}/bin/spec.py --decide <the return's log.node> <specification-root>`, with the
  rest of `log` as one JSON object on stdin. Its first line is what the report quotes. Once the root
  passes, run `spec.py --project`, and re-run step 4's binder for every skeleton whose candidates
  include a touched node.
- **Edits landed in a node no skeleton's candidates hold**: the fact is now stated, and the
  candidate set that lacks it is the cut — grow the epic's `covers` to that node or move the task,
  and re-run step 4.
- **`contradicted`**: the note was `blocking` wearing the wrong class. It takes the blocking
  route of `references/notes.md`, and the report says the decider refused it and why.
- **`standard`**: the fact is the stack's, and «The stack is never a node» (SPEC-003 §Rule).
  Nothing is written to the specification and the task is not stopped: the report hands the
  person the returned `rule` to add to the standard the project declares, which is theirs alone.
- **`noticed`**: a watch item for the report, never a second decision.

Every decided fact is a claim a reviewer can reject: the log entry lets them, the diff over the
specification root shows it, and the report repeats it.

## The loop is bounded

**Each fact is decided once.** A fact already settled in this invocation is never sent to a second
decider. A re-bind that returns an `unstated` note over a fact already decided here is a stop — a
disagreement a person settles — where the node the decision filled already sits inside the
candidates that returned the note; where it does not, the answer is the growth above.

A re-bind over an unchanged skeleton that returns an `unstated` note over a new fact is examined
before anything is spawned:

1. **Print the tally**: `git status --porcelain -- <specification-root>` lists exactly what this
   invocation has written to the specification. Say which re-bind of which skeleton this is.
2. **Read the fact against the criteria.** Where it rests on a condition a criterion carries, and a
   node this invocation wrote states that nothing turns on that condition, the silence is the
   skeleton's: the criterion draws a distinction the domain does not make. Reword the criterion
   without the condition and re-run step 4; spawn no decider.
3. **Otherwise decide the fact** as above, and the report carries the sequence.

Neither the count of re-binds nor the count of facts is a stop on its own: the tally shows a
skeleton being answered one cell at a time, and the rewording ends it.
