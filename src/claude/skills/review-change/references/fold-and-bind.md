# Fold and bind what the conformance pass read

Read at step 3b. Where the staging found no trace file, nothing here runs.

## The premise

`${CLAUDE_PLUGIN_ROOT}/schemas/reconciliation.json` is the record the fold writes: read it once,
for the `summary` and `files[].change` lines the premise owes; the fold applies the rest. Write the
premise: the one part of the reconciliation record that is the delivery's and no fold
can compose. It is a small YAML file in the workspace, carrying:

- `title`;
- `summary` — which tasks wrote these files, under which initiative, as the implementation records
  state it; never a finding of yours;
- `delivered` — this review's own name: the delivery, not a person, is what the premise rests on;
- `target`;
- one `files` entry per path of the file set, with its `change` line taken from the implementation
  records' own `files[].effect` where a record names the path, and stated as "written by the
  delivery of <task>" where none does.

## Save every return

Every conformance return is on disk by now, saved verbatim the moment its notification arrived — a
copy of the subagent's transcript and nothing else, never retyped from the notification that
relays it:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --save-return <target-source-root> <workspace> <file> <transcript>
```

`<file>` is the staged file's path as the manifest lists it, or a certification as the wave names
it, `certify__<node>`; `<transcript>` is the output file the harness names for the spawned agent.
The save prints what the wave still waits for, and whether the fold will refuse what was just
saved. A save whose receipt says so is a subagent to run again before the wave closes, never a
return repaired.

## Fold, check and bind

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --fold <target-source-root> <workspace> \
    <the premise> siegard-reconcile/<review-name>.md
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --reconciliation siegard-reconcile/<review-name>.md
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --bind-record <target-source-root> <specification-root> siegard-reconcile/<review-name>.md --workspace <workspace>
```

`--workspace` names the staging's own: the bind refuses a file or a node that moved since the
staging read it, because it stamps what the subagents read, and the workspace is where the staging
recorded what that was.

The fold writes the record mechanically from the saved returns: which answer a node folds to when
more than one subagent read it, where a finding naming a node lands, what a finding naming none
holds, which nodes are marked `collateral`. Every rule it applies lives in the fold and its tests,
not here. **Never apply those rules by hand, and never edit what the fold wrote.** A refusal naming
a subagent is a fresh subagent with the prompt fixed; a refusal about the premise is yours to fix.

The bind writes **whatever the judgment cleared, and never anything else**. A pair the judgment
refused is under no `encoded_at`, and the binding form reads only the pairs that are, so the
invocation above restamps exactly the cleared set: the delivery's own nodes at the digest their own
bind already wrote, and every other node's claim on these files at the content the delivery left.
It never passes `--replace`.

Read the bind's receipt and carry it into the report. It names the nodes it did not write and the
releases it left owed — each a file read `nowhere` beside files that still hold the node, with the
`--replace` invocation ready — which is the one place the partial shape of the act is stated at the
moment it happens. A release is the person's decision, relayed as their own and never run here.

## What this write is

This is the one place this review writes outside the delivery root: the reconciliation
record and its returns under `siegard-reconcile/`, and `siegard-trace.json`, both at the target's
git toplevel. None of it is a decision about the change: the record states what the subagents read,
the bind states what they cleared, and a finding stays a finding, routed by the person.

**Nor is it a second judgment on the delivery's own nodes made by you.** The judges are the
subagents. Where this session cannot spawn subagents and wrote any node a subagent would read, the
pass stops and reports rather than running inline.

## The findings it carries

Every finding a return carries — `contradicts`, `unstated` and `restates` alike — is a finding of
this pass, stamped `conformance` and placed in the review record under the file its subagent read,
carrying the return's `kind` as the finding's own `kind`. The fold's `unstated` list and the
review's findings are the same facts in two homes, one for the trace's reader and one for the
delivery's. The word is copied from the return, never re-judged here: it lets the record be counted
by where each repair would go without anyone re-reading the evidence.
