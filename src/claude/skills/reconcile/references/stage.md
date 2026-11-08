# The staging

Read at step 2, before acting on the receipt `trace.py --stage` prints.

`--check` is the reverse lookup for what drifted: the trace is keyed by node, and a file is
findable in its output only because the file changed. The staging is the locate step, run by the
one reader that cannot miss a binding. A node missed in a hand reading is a judge handed an
incomplete node set, and the record that comes back reads exactly like a complete one.

## Contents

- Two anchors
- What is judged, and the one subtraction
- An audit
- The four states
- The mechanical tier
- A rewrite
- A carry
- Nodes written since the bind

## Two anchors

**Two anchors meet here, and only one of them belongs in what anyone writes.**

- The git toplevel anchors what `trace.py` *prints* — a `--check` finding, an entry of the trace
  file — and nothing else.
- Everything written — the file set the person gave you, every path in the premise, and the `file`
  every finding names — is spelled from the target source root, the anchor every other record in
  this framework uses. The pack header hands the judge that spelling verbatim, and the judge
  copies it.

`--stage` takes the person's own spelling and refuses the other one, naming the correction. Never
convert the person's paths to match the drift report you just read.

## What is judged, and the one subtraction

What is judged is every node the trace binds to the set, never a chosen subset: reconciling a file
against the part of the specification that agrees with it is the failure this route exists to
prevent.

The one subtraction is `--stage`'s own, mechanical, and rechecked at bind time: a pair whose
binding computes at the file's content as it stands, with no open finding against it in the
corpus, was judged over these exact bytes already. Re-judging it buys a second reading of text
that did not move.

## An audit

**Where the person's ask is an audit, pass `--audit` and omit nothing.** An audit is this same
invocation over a set whose bindings did not drift: a binding over-broad from the day it was
written never drifts, so the person's ask is the one trigger there is.

- The staging hands every pair to a judge, and stages no candidate tier (`references/judge.md`
  says why).
- The premise's `summary` says the source did not change and the claims are what is being re-read.
- Everything downstream runs unmodified. A claim confirmed is restamped with the record justifying
  it; a fact held nowhere blocks its node, and the report hands the `--release ... --node` release
  ready to paste; a finding nobody acts on stays in the corpus, where `--owed` repeats it.
- `trace.py --encodes --rank <target-source-root>` is where an audit's candidate set comes from —
  the two accretion counts, as facts. The file set is still the person's to name.

An audit is never chosen by this skill. Without the word, a reconciliation omits what the guard
allows: re-judging unchanged pairs is bought deliberately or not at all.

## The four states

The staging separates four states, and they do not all continue:

| State | What follows |
|---|---|
| A file with nodes in the manifest | The subject. Its judge is spawned at step 3. |
| A file the trace binds nothing to | Reported, never guessed: the manifest holds it under `unbound`, the fold carries it into the record, and it goes no further — except on an adoption, where the analysis's candidates are what its judge reads it against. |
| A file whose every pair the staging omitted | Nothing left to judge. It stays in the file set and in the premise, and the record accounts for it under `pairs_omitted`. |
| A node reported under the orphaned class | Stop for that node and say so plainly: the specification no longer holds it, and the route is `trace.py --prune` followed by whatever put the fact somewhere else. `--stage` hands no judge such a node and names each one. Do not bind around it, and do not prune it from here. |

Deciding which node an untraced file answers to is a delivery's judgment or an analysis's;
inventing one here would write this framework's most durable claim out of its thinnest evidence.

## The mechanical tier

**A pair a run decides is handed no judge, and the staging separates it under `mechanical`.** Two
kinds land there, answered the same way: a constraint some step of the project's registry
`decides`, and a node a certified test decides. A reading of either would re-decide, at a model's
recall, what a run settles exactly.

Two guards send such a pair back to a judge, and neither is yours to override:

- a certification whose test's text moved is no longer live;
- a node whose own text moved was decided by a step or a test never asked about the sentence that
  replaced it.

A pair that is current and owes nothing is omitted before either tier reaches it.

## A rewrite

**Where the person stated a rewrite, write it into a small YAML file in the workspace and pass it
as `--rewrite`** — `pattern` and `replacement` as Python's `re.sub` reads them, and `steps`, the
registry steps the person named. You transcribe the rewrite they state into the `pattern` and the
`replacement`, and the report shows that transcription beside what it carried. A rewrite read off
a diff and proposed by you is a claim the person never made: the reproduction proves a text is the
old text rewritten, never that the rewrite changes no behavior.

«A pair whose file changed by a rewrite the reconciliation declares is carried to the file as it
stands without a judgment, where the declared rewrite applied to the text the binding pinned
reproduces the current text exactly and every step the declaration names passed over that tree»
(SPEC-005 R11).

- The staging recovers each pinned text from git and hands no judge a pair the rewrite reproduces.
- Every other drifted pair is judged as without it, and the receipt names each with the reason:
  the node moved, an open finding stands against the pair, git holds no pinned text, or the
  rewrite does not reproduce it.
- A rewrite never rides an audit, a review or an adoption, and the staging refuses a step the
  registry does not declare.
- **Where the receipt says the rewrite reproduces nothing, stop and show the person the
  transcription before any judge runs.** Either it says something other than what they stated, or
  the change was not that rewrite alone, and only they can say which.

## A carry

«A carried pair is no reading: it clears no finding and closes none» (SPEC-005 R13). A pair
`--carry` left names why — no stamped text in git, a changed reading, an open finding, a live
plan's pin — and stays `moved`, judged as before.

## Nodes written since the bind

**A node written since the bind is in none of that.** A node no delivery ever encoded has no entry
in the trace — the ordinary state of every node `/analyse` wrote after the source it governs.
Such a node cannot be cleared or bound here: binding it is a delivery's act. What it can be is a
**candidate**.

- Where the person names nodes written since this source was last bound — `/analyse` ends by
  listing exactly those identities — name each to the staging with `--node <node>`.
- It lands in the candidate index beside the bound nodes, the manifest records it with its digest,
  and the record's notes name it, so what the judges were offered is on disk.
- A fact one of them now holds is then attributed to it instead of reported as held by nothing.
- Named, never discovered, and by the same person who named the file set: a reconciliation that
  went looking for its own candidates chose part of its own scope.

Where a node also drifted on the specification side, the judgment reads it as it now stands, and
the record says so in `notes`. Both sides having moved is two facts, and the bind restamps both.
