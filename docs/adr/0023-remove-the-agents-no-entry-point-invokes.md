---
id: "0023"
title: Remove the agents no entry point invokes, and close the path that wrote into the base unreviewed
status: accepted
contract_version: adr/1
---

# Remove the agents no entry point invokes, and close the path that wrote into the base unreviewed

## Context

Two agents ship that nothing runs. `domain-analyst` classified a domain model into the ontology, and
`knowledge-author` wrote one object from an entry that classification named. The change recorded in
`docs/adr/0022-close-the-loop-the-pipeline-left-open.md` replaced the first with `bin/expand_model.py` —
the mapping is a closed table and the identifiers are arithmetic — and split the second into an
expansion that writes the design and a `knowledge-enricher` that writes the four fields only judgment
supplies. Neither replacement removed what it replaced.

What is left is not dormant. A skill is a door the user opens: both carry
`disable-model-invocation: true`, so nothing selects one on the model's own initiative. An agent is the
opposite, and `scripts/check_component_prose.py` says so in the rule it enforces — agents are the only
layer a model selects, and it routes on the description. Both descriptions read as current work.
`domain-analyst` offers to classify a model, and `knowledge-author` offers to author an object.

The second is the one that matters. Its tool grant is `Read, Grep, Glob, Write, Edit`, and its worked
example writes `knowledge/rule/sales/cancelled-order-not-billable.md` — a path under the knowledge root,
not under staging. `src/claude/CLAUDE.md` binds every session in an installation with the opposite rule:
do not author a knowledge object outside `/ingest-domain`, because an object written outside it skips
the validation that makes the base trustworthy. The distribution therefore ships a rule and a capability
that contradicts it, and the capability is the one a model can reach without a person asking for it. It
writes past the staging tree a reviewer reads, past `check_enrichment.py`, and past
`promote_staged.py` — which is every boundary the two-pass design has.

`knowledge-intake-plan.json` already recorded the intended end state: its `producer` enum carries
`expand-model` and `domain-analyst` with the note that the agent's entry goes when it is retired.

## Decision

Both agents are removed, with the contract only one of them produced.

- `src/claude/agents/domain-analyst.md` and `src/claude/agents/knowledge-author.md` are deleted, and
  their declarations leave `src/claude/capabilities.declaration.json`.
- `knowledge-authoring-result` is **retired**, in the third state
  `docs/adr/0020-retire-the-generation-contracts.md` defines: no schema declares it, no successor
  replaces it, and its lock entry stays carrying `retired_by` naming this record. Nothing else ever
  produced it, and no capability read one.
- `knowledge-intake-plan` moves from `/6` to `/7`, closing `producer` to `expand-model` alone. A plan is
  now produced by a script, and one claiming an agent that does not exist is not an instance of the
  contract.

The registered hop from `/6` to `/7` **refuses** a plan whose producer is `domain-analyst` rather than
relabelling it. Rewriting the field would assert that a script produced a document an agent produced,
and `producer` exists precisely so a consumer need not infer that from shape. A plan already naming
`expand-model` crosses by stamping the version, which is what every such plan carries.

Neither agent is replaced by a note telling a reader where the work went. The skills state the order in
full, and a file whose only content is its own absence is a file to keep in step.

## Consequences

**No consumer path changes.** `/model-domain` and `/ingest-domain` name every capability they delegate
to, and neither named either agent. The distribution loses three files and two capability declarations;
the remaining ten are what the two entry points actually run.

**One contradiction the distribution shipped is gone.** There is no longer an installed capability that
writes a knowledge object into the base outside `/ingest-domain`, so the rule in `src/claude/CLAUDE.md`
is now a rule about the only path that exists rather than about one of two.

**Three prose references had to be rewritten, and each was a dangling pointer waiting.**
`domain-modeler` and `impact-analyst` both told a reader that classification is `domain-analyst`'s
work. In an installation that sentence named a file that will not be there. Both now name
`bin/expand_model.py`, which is where the work went and which does ship.

**Four tests keyed on the deleted files were repointed rather than deleted.** They assert properties of
the validators and the generator — a filename that must equal its `name`, a duplicate agent name, a
schema violation, a source whose removal must empty the output — and none of those properties is about
the agent it happened to use as its subject. Two tests that asserted the prose of the deleted agents are
gone, because what they asserted no longer exists.

**Release documentation is not updated, because none exists.** The obligation under
`.claude/rules/compatibility.md` is unmet and recorded as unmet, as
`docs/adr/0020-retire-the-generation-contracts.md` records the same gap.

### What was rejected

**Leaving them installed and marked deprecated.** This is the state that produced the defect. A
deprecation marker is prose in a file a model reads for its description, and the description is what
routing uses; nothing in the harness excludes a component because a comment elsewhere calls it
superseded. The `knowledge-intake-plan` schema had already written the marker down, and the agent went
on shipping for two more changes.

**Keeping `domain-analyst` in the producer enum so old plans stay valid.** No such plan exists to keep
valid — this repository holds no fixtures, per
`docs/adr/0019-the-repository-keeps-no-fixtures.md`, and a consumer that ran the retired path holds a
staging tree rather than a stored plan. Keeping the value would leave the contract admitting a producer
the distribution cannot contain, which is the drift the closed enum exists to prevent.

**Keeping `knowledge-author` as the manual-correction path.** It is the one argument for keeping it: an
object already in the base sometimes needs an edit, and no capability offers one. But it never was that
path — it authored from a classification entry, not from a correction — and a capability retained for a
use it does not implement is how the next reader concludes the use is supported. The gap is real and
stays open, named here rather than papered over by a component that would not close it.

### What would falsify this

A consumer invoking either agent by name and depending on its result. That would mean the capability was
reachable in practice, the removal owed a migration for the artifact it produced, and a retirement
without one was the wrong call. Nothing in the two entry points can reach either, which is why the
removal is admissible at all.
