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
reference, by the registry's own path. A project holds as many as its concerns need; each
invocation names the one that governs the work in hand.

## The two samples

Each is one project, one stack, one registry answering for all of it — proof the same contract
holds two different stacks without a line of schema changing between them.

- **`backend-node-service.yaml`** — a Node/TypeScript service. Fifty-nine rules across what it is
  built on (the runtime, the HTTP framework, the driver, the JWT library, the logger, the test
  runner, the datastore) and how its source is arranged: DTOs, API shape, errors, edge cases,
  security, types, naming, maintenance and tests.
- **`frontend-typescript.yaml`** — a React + TypeScript frontend, not a service. Fifty-one rules
  across component composition, state management, consuming a backend's contract, asynchronous and
  failure edge cases, accessibility, security, types, naming, maintenance, prohibitions, performance
  and tests. Its `elsewhere` draws the same line the backend registry draws for a transport status:
  what a screen tells the user is the specification's, how the screen is wired to say it is this
  file's. Its one presupposition without a backend counterpart is a design-token file — because
  unlike `package.json` or `tsconfig.json`, nothing about its shape is already universally known, so
  a worked example, `frontend-design-tokens.example.css`, sits beside it rather than leaving
  `presupposes` to name a shape nobody had shown.

Nothing requires one registry per project. The contract's own `standard` field says a project may
hold several — a backend's rules are not a frontend's, and where a project's own stack and its own
arrangement change at genuinely different rates, splitting them into separate files by *concern*,
not by path, is the shape to reach for instead. Each sample here answers for one project's whole
stack in a single file because, in each, that split was not worth the second file: what a service
runs on and how its source is arranged change together often enough that a second file would only
be a second place to look. Splitting is a choice a project makes about its own registry, not a
shape this directory has to teach by holding both at once.

## Using one

The registry belongs in the project's own tree, never here and never inside a delivery root as its
origin. Copy a sample across, rewrite it for the project, and then:

```
python3 src/claude/bin/deliver.py --standard <the-project>/standard.yaml
```

Real output over the samples:

```
standard checked: src/standards/backend-node-service.yaml declares 59 rule(s) — 35 decided by reading, 24 by a tool
  pin sha256:cf31b196…7c179f83
  the rules a tool decides run as step(s) lint (20 rule(s)), secret-scan (2 rule(s)), typecheck (2 rule(s)); a review reads only the 35 decided by reading
  what a step exits 0 over is the command exiting 0. […]

standard checked: src/standards/frontend-typescript.yaml declares 51 rule(s) — 33 decided by reading, 18 by a tool
  pin sha256:0b9631b2…5e445c71
  the rules a tool decides run as step(s) lint (15 rule(s)), secret-scan (1 rule(s)), style (1 rule(s)), typecheck (1 rule(s)); a review reads only the 33 decided by reading
  what a step exits 0 over is the command exiting 0. […]
```

Read the split in the second against the first: thirty-three of fifty-one rules are `reading` in the
frontend registry, against thirty-five of fifty-nine — roughly the same proportion, slightly higher
here. Not a stricter registry — a stack where more of what matters (a state placed in the wrong
layer, a screen's accessibility, a token used correctly) is a judgment no configured tool actually
renders a verdict on, and two rules say so in their own text rather than claim a tool decides what
nothing here runs (`ACC-09`'s contrast ratio and `ACC-10`'s touch-target size both depend on a
computed, rendered value `applies_to` cannot presuppose).

That fourth line follows every registry declaring a rule a tool decides, and it is cut here at the
`[…]` rather than repeated whole twice. In full it reads: *whether it is configured to decide
the rule(s) resting on it is this registry's to know: nothing here reads a stack, and a step
deciding nothing passes exactly like one deciding all of them.*

Read the counts beside each step, because they are what the framework can say and the most it can.
It cannot tell a step that decided every rule resting on it from one that decided none — both exit
0, and telling them apart means reading a stack this repository ships no knowledge of. Twenty rules
resting on one step is a number worth an author's look, and looking is what produced the
`eslint.config.js` presupposition every TypeScript registry here now carries: a `lint` script in the
manifest is a step that runs, and the configuration is what makes it a step that decides.

Read the last line of each. A rule marked `decided_by: tool` is **not** a review's to read: it runs
as a step of the project's own suite through `bin/run.py`, and what it finds arrives through the
failures pass with the tool's own message as evidence. A model applying a rule the compiler owns has
strictly worse recall than the compiler and costs more.

Then name the path at invocation. `/implement-task` takes it so the source is written to follow
it, reads it fresh, and pins the SHA-256 of what it read; `/review-change` takes it so the same
source is held to the same rules. Nothing is copied: a record points at the registry's own path,
relative to the target source root, the same way it already points at code. **One registry per
invocation** — the field carrying it is a single reference.

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

## If the project declares a target freely edited

`siegard.json`'s `edits_freely` says a person changes that target's source without a task. What it
costs is not a mystery, and this is the place to plan around it rather than to discover it: an edit
made that way is read by **only** the rules a tool decides — through the project's own suite, over
its whole tree, on every commit — plus whatever `/check-source` is later invoked over, and whatever
a future review happens to reach when a task finally touches those files. Nothing schedules a
reading on its own.

So on such a target, `decided_by` stops being a note about who is better at deciding a rule and
becomes a note about **whether a rule is applied at all** between one task and the next. That makes
one question worth asking of every rule an ordinary surface edit could break: is it really a
reading, or is it a reading because nobody wired the tool?

`frontend-typescript.yaml` is the worked example of the problem. Its most exposed rules are exactly
the ones a cosmetic change reaches, and every one of them is `reading`:

| rule | broken by | decidable by |
|---|---|---|
| ACC-09, text contrast | changing a colour | axe-core, pa11y, a Playwright step |
| ACC-10, touch target size | changing spacing | the same, against a rendered page |
| ACC-05, visible focus indicator | a CSS tidy-up | the same |
| ACC-08, state not conveyed by colour alone | a palette swap | partly the same, partly a reading |

The sample leaves them as readings and says why in its own header comment — it presumes no rendering
step, and a rule claiming a tool decides it when nothing runs is worse than one that admits a reader
must. That reasoning is right for a sample and wrong for a project that declared the target freely
edited: there, the same rules are the ones going unread most often, and the project has a strong
reason to adopt the browser step the sample would not presume. Declare it in `commands`, name it as
the rule's `tool`, and the rule moves from a reading nobody schedules to a step every commit runs.

What does not move is the rest: whether a component composes a catalogued primitive, whether a page
holds business logic, whether a prop is adapted at the boundary. Those are judgment, they stay
`reading`, and `/check-source` is what reaches them.

## What the suite reads

`tests/test_standard.py` holds **every** registry in this directory to the contract, parametrized
over the glob, so a sample that stopped holding fails the suite rather than teaching the wrong shape
to whoever copies it. Before that parametrization existed, only one sample was read at all, and the
rest went unchecked whenever the contract moved.

One guard is worth knowing about because it exists for a failure mode that passes in silence: the
glob is asserted non-empty. A parametrized test over a glob that matches nothing reports success, so
if these files ever move, one test says so instead of the whole set quietly passing.

`backend-node-service.yaml` additionally carries the scope-matcher tests, which are the ones worth
running hardest — neither `PurePath.match` nor `fnmatch` gives what a reader expects, and either
would decide whether a finding is refused.
