---
name: plan-work
description: Turns a stated development scope plus a validated knowledge base into a development plan — an inventory, epics and tasks recorded as markdown nodes under a work root, each task bound to the base nodes that govern it — validates the plan against the base, and derives plan.json. Use when a request asks to plan, decompose, or prepare development work over a domain the base already holds. Not for analysing domain material (that is /analyse-domain), and not for writing source code or tests.
---

You turn a scope into a development plan, and you stop. One invocation, one increment: the
first fills an empty work root, and every later one evolves the plan it already holds — same
order, same discipline.

## Required inputs

A missing input is a stop, not a default:

1. **the scope** — what the human wants developed, in prose, plus any files it references.
2. **the knowledge root** — the base the plan binds to. Named by the human; inferred rather
   than named, its absence is a stop. A plan bound to a base nobody named answers a question
   nobody asked.
3. **the work root** — the directory the plan nodes are written into. Empty is the ordinary
   first run; populated, the invocation is a change to the plan it holds. Named by the human
   and absent, it is created empty; inferred rather than named, its absence is a stop.
4. **the target source root** — where the code lives or will live. An empty tree is an answer
   — a greenfield target — not a stop; but which tree it is, the human says.

## Before anything: the base

The plan is only as sound as the base it binds. Run:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/graph.py --check <knowledge-root>
```

Anything but a clean pass is a stop: report the output verbatim and go no further. A base with
problems is fixed through `/analyse-domain`; a stale `graph.json` is rederived by whoever owns
the base. Neither repair is this invocation's to make — planning never writes into the
knowledge root.

The pin every task carries is the SHA-256 of the base's `graph.json` as just checked:
`sha256:<hexdigest>`, computable as `sha256sum <knowledge-root>/graph.json`. Compute it once,
after the check passes, and stamp it on every task this invocation binds or re-binds.

## Before anything: the tree

The review is `git diff` over the work root, and a diff only says what this invocation did
when the root starts clean. Before any write, `git status --porcelain -- <work-root>` must
print nothing. Output is a stop: report what is pending and go no further — committing,
discarding, or overriding is the human's decision, never the plan's. A work root not under git
control is the same stop: without git there is no review.

## Read the contract

Read `${CLAUDE_PLUGIN_ROOT}/schemas/plan-node.json`. It is the single home of what a plan node
may and must declare — the kinds, the fields each kind requires, and one example per kind
inside that kind's branch. Do not work from memory of it, and do not restate it: what you
remember is not what the validator will apply.

`${CLAUDE_PLUGIN_ROOT}` is set where this skill runs as an installed plugin. Where it is not,
the plugin root is the directory that holds `schemas/` and `bin/` side by side — in a vendored
install, the `.claude/` directory this skill's tree sits under. Every path below resolves the
same way.

## The order

```
situate → inventory → decompose → bind → validate → report → stop
```

### 1. Situate

Two indexes, one rule: read the index, never the whole tree.

- **The base.** Read `<knowledge-root>/graph.json` — current, because the check above passed:
  identifiers, titles, summaries, each node's open gap fields, and every edge. Locate the
  nodes the scope speaks to, and close the impact set over the edges in both directions —
  what those nodes reference, and what references them. Where the scope's vocabulary does not
  surface in the index, grep the base for its terms. Read the impact-set nodes and nothing
  else: the plan binds to what governs the scope, not to everything the base holds.
- **The plan, when the work root is populated.** A stale `plan.json` is rederived by a full
  validation run before anything relies on it. Read `plan.json`, and only it: locate the
  epics and tasks the scope touches, and close the impact set over its edges — dependencies
  in both directions, and bindings that reach the base's impact set. Read those files alone.
  Outside the set, standing decisions stand: a task this change does not touch is not
  reworded, however improvable it looks.

### 2. Inventory

Before any node, persist the scope: the prose as supplied, plus any files it references, go
under `intake/` in the work root. Point every `sources` entry at a file under it. A change
persists the same way — a new file under `intake/`, never an edit to what intake already
holds.

Then survey the target source root and record the territory the plan lands in:

- the modules the change touches, leans on, or merely sits next to;
- the conventions the code already follows, each with the path it was seen at — a convention
  without evidence is an opinion, and opinions are not inventory;
- what the tasks must reuse rather than rewrite, each with where it sits;
- the risks, each with the consumers that would observe the break.

An empty target is a full answer: record the area surveyed, say the tree is empty in the
summary, and invent nothing to fill the silence.

### 3. Decompose

Epics group the work; tasks deliver it. Four tests bind every task, and a candidate failing
any of them is split or merged until it passes:

- **One objective.** A task delivers one falsifiable outcome; two outcomes are two tasks.
- **One reason to change.** A task whose parts would change for different reasons — a rule
  tightened here, a screen reworded there — is two tasks.
- **Independently demonstrable.** Its criteria can be shown met without finishing another
  task; dependencies say what must exist first, never what proves what.
- **One seam.** A task that changes an interface and its consumers in the same breath is two
  tasks joined by a dependency.

Dependencies record what a task builds on, never when it runs: any schedule satisfying the
edges is equally valid, and a cycle is a decomposition error you resolve by re-cutting — never
emit. Each epic declares the base nodes it covers — its slice of the impact set. What it
claims and this plan deliberately leaves untouched goes to `uncovered` with a why; the
validator holds everything else to the tasks. No estimates, no priorities, no order, no
status: those fields do not exist, deliberately.

### 4. Bind

Binding is per task, against the node files — never against your memory of the decomposition.
Reread each node the task cites; what governs the task is what the node says today, not what
the analysis meant when it was written.

- Cite the governing nodes by identifier in `nodes`. A task binds inside its epic's claim: a
  node the epic does not cover means `covers` grew and says so, or the task sits under the
  wrong epic — the validator refuses the third option, binding beyond the claim in silence.
- A task that binds nothing must say why in `rationale` — scaffolding is real work, but
  ungoverned work is a claim someone reviews.
- **Triage every open gap on every bound node** — the validator refuses silence. A gap that
  bears on the task is `unresolved`; one that does not is waived with a why. The why is a
  claim a reviewer can reject, so write the reason, not a formality.
- **A fact the task needs that no node holds is a question**, recorded under `unresolved`. It
  is the signal that the scope outran the base: the answer is produced through
  `/analyse-domain`, never by the plan.
- Write `objective` and `criteria` from the scope and the bound nodes, each criterion
  falsifiable on its own. Stamp the pin from the base check on `base`.

While writing, a single file can be checked on its own:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/plan.py --node <file> <work-root> <knowledge-root>
```

### 5. Validate, and derive the plan

When every node is written, run:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/plan.py <work-root> <knowledge-root>
```

This validates every plan node against the contract, runs the checks that need the whole plan
and the base — dependencies resolve without cycles, bindings resolve, every open gap on a
bound node is triaged, every covered node reaches a task or a stated why, every pin matches
the base as it stands — and derives `plan.json`. **Never write or edit `plan.json` yourself.**
Report the command's output verbatim. If it exits non-zero, the run failed — fix and rerun,
and never describe the plan as valid while it is not.

**Fixing means form, never knowledge.** A wrong shape — a malformed pin, a bad reference, a
forbidden field — is yours to correct. An untriaged gap is settled by judgment — unresolved
or waived — never by inventing the fact it names. A question is never answered by the plan. A
coverage hole is settled by a task or by `uncovered` with a why — whichever the scope actually
decided, not whichever passes.

### 6. Report, and stop

Report, in this order:

- every node written, by identifier — on a populated root, created, changed and removed
  listed apart;
- the impact set that was read — in the base and, on evolution, in the plan — so the reviewer
  can judge what the planning looked at, not only what it touched;
- every unresolved entry, by task identifier — the gaps that block and the questions that
  outran the base, the latter with the pointer back to `/analyse-domain`;
- every waiver, by task identifier — these are the claims a reviewer can reject;
- every node carrying `rationale`, by identifier;
- the validator's final output, verbatim.

Then stop. `git diff` over the work root is the review, and it belongs to a person.

## What you never do

- Write or edit `plan.json` by hand.
- Close a gap, or answer a question, with a value the base does not hold — a fact is produced
  in the base, through `/analyse-domain`, never in a task.
- Waive a gap without a why, or triage by silence.
- Record a status, an estimate, a priority or an execution order — those fields do not exist,
  and prose does not get to hold what the contract refused.
- Write source code or tests, or change the target tree — the plan is nodes, nothing else.
- Write into the knowledge root — a broken or stale base is reported with its fix, never
  repaired from here.
- Restate the contract's vocabularies from memory instead of reading the schema.
- Reopen a standing plan decision outside the impact set, or re-cut an epic as a side effect
  of a change.
- Commit, stash, or otherwise change the consumer's git state — a dirty root is reported, and
  what to do with it is the human's call.
