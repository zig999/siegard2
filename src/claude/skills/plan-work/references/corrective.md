# The corrective increment

Read when the person names one wrong behavior, observed in code already delivered.

The behavior answers to no criterion any task holds: the task that wrote the file was delivered and
reviewed before anybody saw it. **The person names this in the invocation; it is never inferred
from the tree.** The invocation names two things, both the person's: the wrong behavior, and the
file it lives in.

The correction comes through the plan rather than by hand because by hand one context writes the
fix and its test, which then agree by construction, and nothing binds, so `siegard-trace.json`
keeps a digest that is no longer there. The route is the ordinary one, at the size of the work:

```
situate → intake → the task, written here → implement-against → validate → report → stop
```

## What does not run

**The survey and the decomposition do not run.** `intake` is step 2's first paragraph alone. The
person is holding the file, and the increment is one task; where it is genuinely more than one, it
is a scope, and the ordinary route is what it gets.

**The scope under `intake/` is the person's and nothing else**: the behavior as they described it,
the reproduction, and the file by path. Where a goal's findings policy named the finding in advance,
the intake holds three things from the review's record: the node the finding names, as what the
code must do; the file; and the record, by path — never the finding's account of what the code
does. Nothing you read in the source goes there: the decider reads `intake/` as the one place a fact
may already be stated, and a description of the code there would make what the code does a stated
fact.

**The binder runs, per task, as it always does.** It decides which nodes the correction answers to,
and returns a classified note where the fix contradicts the specification or meets a silence — the
common shape here, since a behavior nobody specified is how the bug survived review. The
decided-fact route of `references/unstated.md` settles that silence the same way.

## The task you write

You write the task yourself, held to every test a decomposer's task is held to:

- **criteria falsifiable, one condition each**, written from the observed behavior and the node
  that governs it — never "the bug is fixed", which no test can fail;
- `rationale` where it implements nothing, and `sources` pointing at the scope under `intake/`;
- **no `produces`**: a correction to delivered source is not an artifact the standard presupposes.

**A criterion's one condition is the observed behavior, in the domain's terms.** How a target keeps
an answer between surfaces — a client's cache, a marker it compares against, whether the data
arrived before a surface was mounted — is how the target implements the domain, never a fact the
domain states. A criterion conditioned on it rests on a fact no node can state: the binder returns
the silence, and every act the criteria name under that condition becomes a silence of its own. The
reproduction is the test's setup, not the criterion's condition. Where a decided node says nothing
turns on such a condition, the criterion that carries it was the silence, and the criterion is what
changes: you rewrite the skeleton, and it runs through the binder again before it touches disk.

## The epic

**The correction gets its own epic, never an existing one.** Growing a delivered epic's `covers`
re-opens every task it holds. The file seeds what the binder reads:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --encodes <target-source-root> <file> [<file> ...]
```

- **A file the trace does not know is a stop**, named in the report: a correction to code no task
  ever bound has no claim to correct against.
- **Close what came back as step 1 closes any impact set.** That closed set is the binder's
  candidate set, handed as the pack `spec.py --pack` prints over it, in place of an epic's
  `covers`, since the epic is not written yet.
- **Write the epic after the binder returns.** Its `covers` is the `implements` the binder returned
  plus any node the person named for this correction, and nothing else. `uncovered` holds only a
  node the epic claims that the person excluded, with the person's own why.

A live work root takes the task as any increment does. A work root holding `closure.md` takes
nothing: the correction names a new slug.

The task goes to `/implement-task` like every other task. Say in the report that this was a
corrective increment and which steps did not run, and carry the `--encodes` output the binder's
candidates were seeded from, verbatim.
