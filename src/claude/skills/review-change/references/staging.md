# Staging the conformance pass

Read at step 1, after the trace check. Stage into a fresh workspace directory nothing commits
(`mktemp -d` is the ordinary choice): the workspace is a reading copy, and a committed copy of node
text would be a second home for it.

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --stage <target-source-root> <specification-root> \
    <review-name> <workspace> <each path of the file set> --review --node <each node the tasks implement> \
    --demonstrated <each proof record of the tasks under review> [--certify <certifications file>]
```

Run it; never infer any of it, and never reconstruct a node set by reading `siegard-trace.json`
yourself.

## The certification a proof claims

**Where a proof under review offers a test as the proof of a specification node, the staging
carries the claim to the judgment that settles it.**

- Pass every proof record of the tasks under review under `--demonstrated`, one path each.
  `--stage --review` reads their `tests[]`; an entry with `demonstrates` says this test would fail
  if that node's fact stopped holding.
- The staging composes one certification per node from those entries and nothing else: its
  `proof` is the file(s) of every test demonstrating it, and its `step` is the registry's command
  whose `role` is `suite`, the step that proves the work. It refuses the composition where the
  registry declares no such step.
- Compose nothing yourself: never from your own reading of a test, never from a node's kind, and
  never from a proof you did not pass. `deliver.py` already refused a `demonstrates` naming a node
  the task does not implement; what this step adds is whether the test makes good on the claim.
- `--certify` may still ride beside it, for a claim no proof carries and a person states. A node
  under both is refused.
- Where no proof carries a claim, the staging stages no certification, and the report says so.

Either way the report lists every node the tasks implement that no test demonstrates, with what
the proof's `untested` says of each: «a node the task implements that no test claims is named in
that review's report with the reason the proof gives» (SPEC-004 R13). A node with no claim and no
reason is a proof short of what it owes, said as that and never as a finding: this pass judges no
test.

## What the staging computes

This is the locate step of the conformance pass, run by the one reader that cannot miss a binding.
For every file of the set it computes every node the trace binds to it, and it writes:

- one **node pack** per file — the full text of every node that file's subagent reads, each entry
  naming its source path and digest;
- the **candidate index** for the whole batch;
- `siegard-reconcile/<review-name>.returns/`, empty, beside the record's own reserved path.

`--review` makes this a review's staging and not a reconciliation's, in two ways the manifest
records:

1. **Only what a judgment already read is omitted.** A pair is left out when a reconciliation's
   judgment cleared it at the very bytes on disk — its file entry in the trace carries `judged` —
   the node's text is unchanged since, and no finding stands against it in the corpus. Every pair
   a delivery or a hand stamped goes to a subagent, since that bind recorded what was written and
   nobody has read it against the node, and so does every pair of the delivery's own nodes named
   under `--node`, whatever the trace says of them. `--bind-record` rechecks each omission when it
   binds, and refuses the record where the pair has lost `judged` since the staging.
2. **The plan's nodes ride along on every file.** Each `--node` is the identity of a node the
   tasks under review implement, exactly as `plan.json` names it. Every subagent reads them and
   answers for them in its return, so a fact the delivery wrote against a node its record never
   bound is still read against that node. They are never bound from here: a binding this review
   wrote would be a claim no implementation record made.

A file the trace binds nothing to — a test, a file the records did not name under `encoded_at` —
is still handed a subagent, over the plan's nodes alone, and still staged under `unbound`: being
read and being claimed by a binding are two facts, and the record owes both.

## Two states that continue differently

- **A node under the orphaned class** is a stop for that node alone, said plainly: the
  specification no longer holds it, no bind repairs the entry, `--prune` is its route, and no
  subagent is handed it.
- **No trace file at all** is not a stop: nothing has been bound in this target, so there is no
  collateral to judge. The conformance pass runs over the file set with the plan's node identities
  as its whole node set, in one subagent, writes no record and binds nothing, and the report says
  so.
