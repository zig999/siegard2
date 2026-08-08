# Sample standards — not distributed

**Nothing in this directory ships.** It sits under `src/standards/`, outside `src/claude/`, and the
assembly copies only `src/claude/` into `dist/.claude/`. Compare the two trees and this directory is
absent from the second, by construction rather than by omission.

It holds **examples** of the artifact a project authors for itself: a registry of rules about how its
own source is arranged. Nothing here governs anything. Nothing here is read at runtime by a skill, a
validator or an agent.

## Why the framework ships no rule

A standard says how a project's source is arranged. That is neither a domain fact nor this
framework's to state: a stack's conventions are not a domain's, and a framework shipping them would
prescribe one language to a project written in another.

So Siegard ships the **slot** and the **enforcement**, never the content:

| what ships | where |
|---|---|
| the contract a registry answers to | `src/claude/schemas/standard.json` |
| the validator that holds a registry to it | `bin/deliver.py --standard <file>` |
| the review pass that reports departures | `/review-change`, the standard pass |
| the split between what a reading decides and what a tool decides | `decided_by` on every rule |
| **any rule** | nowhere — it is the project's |

These files are not this repository's standard either. This repository is Python, JSON, YAML and
markdown; a TypeScript registry could not govern it. They are transcriptions of real registries,
kept as worked examples of the contract.

## A project may hold several

The contract says so on the field that names one:

> *"This standard's name, as the review that read it records it. **One project may hold several** — a
> backend's rules are not a frontend's — and each is named where it is used."*

So several registries is the intended shape, not a workaround. The constraint sits one level down:
**one registry per invocation**, because the field carrying it on a delivery node is a single
reference and the copy under `standards/` is one file per name. A project holds as many as its
concerns need; each invocation names the one that governs the work in hand.

## The three samples

Two of them are the split. The third is what merging them costs.

- **`backend-node-stack.yaml`** — *what the service is built on*, and what is not introduced beside
  it. Twelve rules: the runtime, the HTTP framework, the driver, the JWT library, the logger, the
  test runner, the one datastore.
- **`backend-typescript.yaml`** — *how the source is laid out*. Forty-seven rules across
  arrangement, DTOs, API shape, errors, edge cases, security, types, naming, maintenance and tests.
- **`backend-node-service.yaml`** — the two above, merged into one registry. Fifty-nine rules, and a
  header saying what the merge gave up.

The first two separate by **concern**, not by path, and this is worth stating because it is the
mistake that is easy to make: 11 of the stack registry's 12 rules and 15 of the arrangement
registry's 47 target the same `src/**.ts`. `applies_to` narrows a rule to a part of the tree; it
cannot express "this rule is about the stack and that one is about the layering". Nothing in the
contract carries that distinction — only the separate files do.

### What the merge taught

The rules concatenate cleanly: 12 plus 47, ids never colliding, and the merged file's counts are the
sum of its parts. What does not survive is prose. Two `elsewhere` entries of the stack registry each
described a boundary that merging erases — one pointing the reader at the arrangement standard for
layering, which is now in the same file, and one declaring that no linter is configured, which 23
tool-decided rules beside it contradict. Copied along with the rules, they would have stated two
falsehoods about their own document.

**Nothing in the contract would have caught either.** The validator holds ids, scopes, the
reading/tool split and the duplicate-id refusal; it does not read prose for whether a boundary still
stands. That is the cost of merging two registries, and `backend-node-service.yaml` states it in its
own header rather than leaving a reader to find it.

## Using one

The registry belongs in the project's own tree, never here and never inside a delivery root as its
origin. Copy a sample across, rewrite it for the project, and then:

```
python3 src/claude/bin/deliver.py --standard <the-project>/standard.yaml
```

Real output over the samples:

```
standard checked: src/standards/backend-node-stack.yaml declares 12 rule(s) — 11 decided by reading, 1 by a tool
  pin sha256:37d23cae…431880e4
  the rules a tool decides run as step(s) typecheck (1 rule(s)); a review reads only the 11 decided by reading
  what a step exits 0 over is the command exiting 0. […]

standard checked: src/standards/backend-typescript.yaml declares 47 rule(s) — 24 decided by reading, 23 by a tool
  pin sha256:f27431c6…c1ae8e26
  the rules a tool decides run as step(s) lint (20 rule(s)), secret-scan (2 rule(s)), typecheck (1 rule(s)); a review reads only the 24 decided by reading
  what a step exits 0 over is the command exiting 0. […]

standard checked: src/standards/backend-node-service.yaml declares 59 rule(s) — 35 decided by reading, 24 by a tool
  pin sha256:cf31b196…7c179f83
  the rules a tool decides run as step(s) lint (20 rule(s)), secret-scan (2 rule(s)), typecheck (2 rule(s)); a review reads only the 35 decided by reading
  what a step exits 0 over is the command exiting 0. […]
```

That fourth line follows every registry declaring a rule a tool decides, and it is cut here at the
`[…]` rather than repeated whole three times. In full it reads: *whether it is configured to decide
the rule(s) resting on it is this registry's to know: nothing here reads a stack, and a step
deciding nothing passes exactly like one deciding all of them.*

The third line of counts is the merge checked by arithmetic: 11 + 24 readings and 1 + 23 tools, with
nothing gained and nothing lost.

Read the counts beside each step, because they are what the framework can say and the most it can.
It cannot tell a step that decided every rule resting on it from one that decided none — both exit
0, and telling them apart means reading a stack this repository ships no knowledge of. Twenty rules
resting on one step is a number worth an author's look, and looking is what produced the
`eslint.config.js` presupposition both TypeScript registries now carry: a `lint` script in the
manifest is a step that runs, and the configuration is what makes it a step that decides.

Read the last line of each. A rule marked `decided_by: tool` is **not** a review's to read: it runs
as a step of the project's own suite through `bin/run.py`, and what it finds arrives through the
failures pass with the tool's own message as evidence. A model applying a rule the compiler owns has
strictly worse recall than the compiler and costs more.

Then name the path at invocation. `/implement-task` takes it so the source is written to follow it,
copies it into the delivery root's `standards/` and pins that copy; `/review-change` takes it so the
same source is held to the same rules. **One registry per invocation** — the field carrying it is a
single reference, and the copy under `standards/` is one file per name.

A project that has authored no standard gets an honestly narrow review: the pass records that it did
not run, and what was absent. Never a clean one.

## Two lines that bound what a rule may say

Both are in `schemas/standard.json`, and both are the whole of its scope.

**No rule states what the system answers or who may see what** — a status, an error code, a refusal,
an authorization outcome. Those are what the business decided, they live in the specification as
nodes, and a rule stating one would put two review passes in contradiction over the same line: one
requiring in code exactly what the other reports as a fact the specification does not hold. What a
rule may state is *where the mapping lives*.

**No rule carries a severity, and nothing derives a verdict.** A finding states what it costs; a
person decides what that means.

## What the suite reads

`tests/test_standard.py` holds **every** registry in this directory to the contract, parametrized
over the glob, so a sample that stopped holding fails the suite rather than teaching the wrong shape
to whoever copies it. Until the third sample was added, only `backend-typescript.yaml` was read at
all, and the other went unchecked whenever the contract moved.

Two guards are worth knowing about because they exist for failure modes that pass in silence:

- The glob is asserted non-empty. A parametrized test over a glob that matches nothing reports
  success, so if these files ever move, one test says so instead of the whole set quietly passing.
- `backend-node-service.yaml` is held to being exactly the concatenation of the two it was built
  from. A rule edited in one place and not the other would leave the merged sample teaching
  something neither source says. Only the rules are held: its `elsewhere` deliberately drops the two
  entries that stop being true once the boundary they describe is internal.

`backend-typescript.yaml` additionally carries the scope-matcher tests, which are the ones worth
running hardest — neither `PurePath.match` nor `fnmatch` gives what a reader expects, and either
would decide whether a finding is refused.
