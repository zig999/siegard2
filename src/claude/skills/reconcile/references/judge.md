# The judgment

Read at step 3, before spawning any subagent. Its judgment lives at
`${CLAUDE_PLUGIN_ROOT}/agents/specification-conformance-reviewer.md`.

## Contents

- Saving each return
- What each subagent is handed
- Two rules about the paths in a prompt
- On an audit, no candidate tier
- The three kinds a finding answers
- Verbatim is literal
- One judge per file, answering once
- One agent for both routes
- The form of the reply

## Saving each return

**Save each return verbatim the moment it arrives**, at
`siegard-reconcile/<slug>.returns/<the file's path with every '/' as '__'>.yaml` — a copy and
nothing else. Never reshape one, never trim one, never repair one: the returns are the evidence
the record is folded from, they outlive this session, and a return adjusted by the hand that saved
it carries a judgment the subagent never made. The copy is the script's, from the subagent's
transcript — the output file the harness names for the spawned agent:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --save-return <target-root> <workspace> <file> <transcript>
```

- `<file>` is the staged file's path as the manifest lists it, or a certification by its node
  identity or as the wave names it, `certify__<node>`.
- The save prints what the wave still waits for, and whether the fold will refuse what was just
  saved. A save whose receipt says so is the subagent to run again before the wave closes, never a
  return repaired.
- Never retype a return from the notification that relays it: that text is re-rendered for
  display, and an escaped character it carries parses as part of a scalar.
- A refusal says why. A subagent answers either by its final reply or by a hand-back the harness
  confirmed delivered, whose `message` is then the return; one whose transcript ends in any other
  tool call has not answered yet. Only one whose transcript cannot be read is saved by hand, under
  the same discipline.

## What each subagent is handed

- **A file set of exactly its one file** — the resolved path its pack header names; a finding
  echoes the header's own spelling.
- **As the node set, its node pack's path from the manifest** — the pack is the set, whole, each
  node's text with its source named.
- **As candidates, the path to the workspace's candidate index**, which holds any node the person
  named as written since the bind. The subagent may consult it where its file states a fact its own
  nodes do not settle: a fact one file states can be governed by a node another file carries, and
  a judge who cannot open that node reports an absence where the true finding is a
  misattribution.
- **The specification root.**
- **The path to `${CLAUDE_PLUGIN_ROOT}/schemas/conformance-return.json`** — where a finding's shape
  lives, and the contract the whole return is held to by the fold. One contract, handed once: a
  second one pasted beside it would be a shape the fold never applies.
- **The form of the reply**, in the agent's own words, as the last section here gives it.

## Two rules about the paths in a prompt

Both are about what a prompt costs.

- **The candidate index goes as its path and never as its contents.** One index serves the whole
  batch, and a judge opens it on demand, in its own context. Written into each prompt, the same
  text is paid N times in your context, where nothing reuses it. The same holds for the node pack:
  its path, never its text.
- **Every path a subagent receives is absolute and already resolved.** Never a path relative to a
  root the subagent is told to prepend, and never a root plus an instruction to compose the rest:
  a nested `src/`, a monorepo alias or a generated directory turns that composition into a guess,
  and a guess that misses returns a refusal that costs the whole subagent.

## On an audit, no candidate tier

**On an audit, no candidate tier is passed, and the staging writes none.** The manifest carries an
empty `candidates` and the workspace holds no index, so there is nothing to hand over.

- A candidate exists to let a judge say that a fact its own nodes do not hold is held by a node
  another file carries. An audit asks a narrower question: does this file still carry this node's
  fact, so that this claim stands?
- Both answers a candidate separates end at the same act on that pair: the claim is not carried,
  and the release is what the report hands over. Binding the node that does hold the fact is a
  delivery's act.
- The ordinary route keeps the tier: there a misattribution reported as a gap is a false finding,
  a false finding blocks its node, and undoing one costs a fresh subagent over the whole file.

## The three kinds a finding answers

**A judgment answers two questions, and `kind` is which one a finding answers.** One boolean per
node would land the second question on whichever node shared the file with it.

| `kind` | Means | What follows |
|---|---|---|
| `contradicts` | A node governs the fact, and the source disagrees with it or became a second home for it. | The pair's: the node does not bind, and a rebind is what closes it. |
| `unstated` | No node holds the fact at all. | The specification's: the route is `/analyse`, **no rebind can ever close it**, and it blocks no binding a node's own reading cleared. The fold lands it under the record's `unstated`, keyed by file. |
| `restates` | A comment or a docstring says a node's fact while code holds it too, in that file or another — never text the running system emits, such as a tool description or an error message, which is behavior. | The pair conforms and binds where the code is. The fold lands it under the record's `restates`; what it owes is the text's removal, then this route over the file. |

`trace.py --owed` reports all three apart from what a bind is owed, and the report hands each its
route.

## Verbatim is literal

**The fold enforces it against five keys.** `conformance-return.json` admits `findings`, `read`,
`nowhere`, `looked_past` and `candidates_opened`, and nothing else at any depth.

- A sixth key — a `notes` holding a subagent's closing paragraph, a summary line written for a
  person — refuses that return at `--fold`, and the fold refuses whole: every saved return is
  re-read before it runs at all.
- What a subagent says outside those keys belongs in your report to the person, never in the file
  the fold reads.
- Where a return arrives shaped for a reader rather than for the contract, the fix is still a
  copy: save what came back, and say the rest in the report.

## One judge per file, answering once

One judge per file rather than one over the set: a single context holding every node and every
file answers hundreds of pairs in one reading and claims clean over pairs it never weighed.

- No subagent reads another's return, and the pass is the union of what they return: a finding
  keeps the file its judge read, and a node is cleared exactly where no subagent that read one of
  its files found against it.
- **A subagent answers once.** Where a return is unusable — a field missing, a node it never
  accounted for — the prompt was wrong, and the correction is a fresh subagent with the prompt
  fixed, never a follow-up question: a resumed judge holds its first reading and the new question
  at once.
- Two divergent answers from one subagent are not a union to fold. They void each other, the file
  is judged again from a clean context, and `notes` says that happened.

## One agent for both routes

One agent serves this route and the review's. What belongs in the file set and the node set is the
invocation's rule and never the agent's own: in a review that rule is the change, with the trace's
nodes and the plan's read together over each file it wrote; here it is the trace alone, one file at
a time. Duplicating the judgment into a second agent is how two passes end up disagreeing about
what conformance means.

Two things this route needs are in the agent's own contract: the candidate tier it may open to
attribute a fact, and the per-node `read` it returns — `held_at` and its quoted evidence — from
which a cleared node's `how` is written. **Never write a `how` from your own reading of the file**;
that is the judgment this step delegated.

## The form of the reply

Handed to every subagent, in the agent's own words: the reply begins with the first key the shape
lists that the answer carries, and ends with the mapping's last line; no ``` line anywhere.
