# Siegard

Siegard is a framework for [Claude Code](https://claude.com/claude-code), shipped as a plugin. It
keeps **one written specification of what a project decided** and makes the code answer to it:
the specification is markdown a script validates, the work is planned and delivered against it,
and a trace records which file holds which decision, so a change made outside the route is found
and not trusted.

```
/analyse ──► SPECIFICATION (markdown nodes) ──► /plan-work ──► /implement-task ──► SOURCE + TESTS
                       ▲                                                                │
                       └──────────────── /review-change · /reconcile ◄─── trace ◄───────┘
```

## What it gives a project

- **A specification that refuses what does not hold together.** Five classes of node — Domain
  Model, Rule, Scenario, Contract, Architecture Constraint — recorded as markdown and checked by
  `spec.py`. A node carries no status.
- **A plan whose every task names the nodes it implements.** `/siegard:plan-work` cuts a stated
  scope into tasks, and the plan is validated against the specification before any code is written.
- **Delivery that proves itself.** `/siegard:implement-task` writes the source and the tests that
  prove it, and runs the steps your own registry declares until the project builds and its suite
  passes. Every execution is captured through `bin/run.py`; no agent holds a shell.
- **Judgments made by a context that did not write the thing.** `/siegard:review-change` and
  `/siegard:reconcile` delegate to separate agents and save what they return verbatim.
- **A trace.** `siegard-trace.json` binds each node to the files that hold its fact, pinned with
  SHA-256 digests. `trace.py --check` reports a file that changed without a rebind, and
  `/siegard:reconcile` re-reads it.
- **A way in for code that already exists.** `/siegard:survey`, `/siegard:analyse` and
  `/siegard:reconcile` adopt source no delivery wrote, one context at a time.

It is meant for Claude Code projects that want delivered code to stay traceable to a decision.
It needs Claude Code and `python3` with PyYAML and jsonschema; it builds no application of its own.

## An example: a hand fix

During an incident someone added a guard to `src/billing/raise.ts` so an order cannot get two
invoices, and committed it. The behavior is correct, and no specification node says it. CI runs
the trace:

```
$ trace.py --check backend
backend/src/billing/raise.ts: the file changed without a rebind — 1 binding(s): rules/sales/invoice-immutable
```

You hand the file to the reconcile route:

```
/siegard:reconcile  file set: src/billing/raise.ts   project root: .   slug: hand-fix-invoicing
```

A judge that did not write the change reads the file against `rules/sales/invoice-immutable` and
returns a finding — `contradicts`: the guard states a cap no node holds. The skill records it and
hands back two doors without choosing: the code is right and the specification is behind
(`/siegard:analyse` with the finding as material, so a node gains "an order carries at most one
invoice"), or the specification is right and the code is wrong (a corrective increment of
`/siegard:plan-work`). Until a record clears the pair, `trace.py --owed backend` keeps listing it.
The glossary walks the same case step by step in
[One complete example: a hand fix](glossary/siegard-glossary/12-one-complete-example-a-hand-fix.md).

## Where things are stated

What each script and skill does is stated where it is enforced: a script's module docstring,
printed by `--help`, and a skill's own `SKILL.md` under `src/claude/skills/`. The requirements
the framework must meet are in `specs/`, the structure they require is in `schemas/`, and the
[glossary](glossary/siegard-glossary.md) explains the vocabulary in plain words; where the
glossary and a specification, a schema or code disagree, those win.

- [`CHANGELOG.md`](CHANGELOG.md) — what each version changed.
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — how to change this repository.
- [`SECURITY.md`](SECURITY.md) — what the plugin runs, and how to report a vulnerability.
- [`LICENSE`](LICENSE) — MIT.

## About this repository

This repository authors the framework under `src/claude/` and assembles it into
`dist/.claude/`, which ships as a Claude Code plugin. The repository is also the plugin's
marketplace: `.claude-plugin/marketplace.json` at this root is what a consumer adds once to
install the framework and receive its versions. The rest of this page is the operational part:
how a consumer project installs Siegard as a plugin and stays current.

## Installing Siegard in a consumer project

Run these inside a Claude Code session opened at the consumer project's root.

### 0. Python on the machine

The skills run the plugin's scripts with `python3`. Every script states its own dependencies in
its `--help`; across them that is PyYAML and jsonschema, and `run.py` needs nothing beyond the
standard library. Where PyYAML was built with libyaml the scripts read YAML through it, and
otherwise through PyYAML's own scanner: the output is the same, the speed is not. Over a project
whose `siegard-reconcile/` holds megabytes of records, `trace.py --owed` and `--convergence` — and
so `/siegard:siegard-status` — answer in a second or two with libyaml and wait tens of seconds
without it. This prints whether the interpreter has it:

```sh
python3 -c "import yaml; print(yaml.__with_libyaml__)"
```

### 1. Add the marketplace (once per machine)

```
/plugin marketplace add zig999/siegard2
```

That clones over HTTPS. If the repository is private and your access is by SSH key, add it by
its git URL instead:

```
/plugin marketplace add git@github.com:zig999/siegard2.git
```

Claude Code clones with your own git credentials; whatever lets you `git clone` this repository
lets you add it as a marketplace.

### 2. Install the plugin

```
/plugin install siegard@siegard-generator
```

When asked for a **scope**, choose **project**. That records the plugin in the consumer's
`.claude/settings.json` under `enabledPlugins`. For anyone who opens the repository afterwards
to be offered the same install, that file also needs the marketplace: where the install did not
write `extraKnownMarketplaces`, add it by hand, so the file reads in this shape:

```json
{
  "extraKnownMarketplaces": {
    "siegard-generator": { "source": { "source": "github", "repo": "zig999/siegard2" } }
  },
  "enabledPlugins": { "siegard@siegard-generator": true }
}
```

Anyone who opens the repository afterwards is offered the same install. Choosing **user** scope
installs it for you alone and writes nothing into the project.

### 3. Turn on auto-update

Auto-update is per marketplace and off by default for a marketplace that is not Anthropic's own.
Turn it on once:

`/plugin` → **Marketplaces** tab → `siegard-generator` → **Enable auto-update**.

With it on, Claude Code checks for a newer version in the background shortly after a session
starts and says when one is ready. Nothing installs silently, and a running session keeps the
version it started with: the check finds, you apply with `/reload-plugins` (or a new session).
Without it, `/plugin marketplace update siegard-generator` followed by `/plugin update` asks the
same question on demand.

### 4. Nothing to place: the rules arrive by hook

The plugin carries the session rules every Siegard skill assumes at `hooks/rules.md`, and its
`hooks/hooks.json` places them into every session at start and into every agent at spawn — in a
project that declares `siegard.json` at its git toplevel, and nowhere else. A repository that
never adopted Siegard receives nothing, even where the plugin is installed for every project you
open, so until step 5 writes `siegard.json` a session runs without the rules. No
`CLAUDE.md` is copied to the project root, and a project's own `CLAUDE.md` stays its own. The
rules are short by design: they carry what binds a session when no skill is running — which
route a change takes, and what is never hand-edited or invented — and nothing a skill or a
script states in its own file. `/plugin` lists the skills; each script's `--help` states what it
does.

Three of those rules shape how you work with a session, so expect them:

- **A session commits only what your own words in that session authorized, and only what the
  skill it invoked wrote.** Say "commit", or state the whole route end to end in your ask. A
  summary of an earlier context is not an authorization: after a compaction, a resumed route asks
  again before its next commit. Each commit is pathspec-scoped, one per invocation — never a
  branch, a push, a stash or a rewrite.
- **A question about where the project stands is answered from disk.** Ask it, and the session
  runs `/siegard:siegard-status` (the whole project) or `/siegard:siegard-progress` (one
  initiative) rather than recalling the conversation; the framework's version is `project.py`'s
  answer.
- **A report opens with what needs you, and a finding stops nothing.** Its first lines are what
  must be done before a named step runs, what you alone decide, and what it suggests and why — in
  plain words. A review's findings are evidence for you to route; only a stop the skill's own file
  names ends a run.

A project that placed an earlier release's rules at its root as `CLAUDE.md` hears about it: the
first thing every skill runs is `project.py`, and where the root file carries a Siegard marker
line it prints one `rules:` line asking for the Siegard portion to be removed, keeping anything
the project added. Hooks are what carry the rules, so a session with hooks disabled runs the
skills without them.

One file does ship for the project root, and a person copies it: `siegard-clean-zone-identifiers.sh`,
a command no skill invokes. It removes every `<name>:Zone.Identifier` file from the root down —
what Windows leaves under WSL when material is copied in — printing each removal; `--dry-run`
prints without removing.

### 5. Declare the project

```
/siegard:siegard-config
```

writes `siegard.json` — the specification root, targets, work and delivery roots, and the
standard each target follows. Commit `siegard.json` and `.claude/settings.json`: those two
make the install reproducible for everyone on the project.

What else the file declares, and what each declaration changes, is `schemas/project.json`'s to
say; three of its fields are worth deciding before any work starts:

- **`standard`, one registry per target.** `/siegard:siegard-standard` writes a target's registry
  from the project's own configuration; a project with more than one target declares `standard`
  keyed by target. This repository's `src/standards/` holds worked registries that do not ship —
  read them in a clone, as with `tools/` below. Every delivery record pins the registry it was
  delivered under, and `deliver.py --outstanding` — so `/siegard:siegard-status`,
  `/siegard:siegard-progress` and `/siegard:deliver-scope` — lists every record pinning none, or
  another than the one `siegard.json` declares for its target. Declared late, a registry leaves
  every record delivered before it on that list for good: a fact, never a refusal.
- **`tests`, per target.** Declare which files are a target's tests before the first survey:
  a declared test is never read as source, and `--untraced` counts it `uncertified` until a
  certification names it.
- **`edits_freely`**, for a target whose bytes change without a task — what it holds back from
  `trace.py --check`, and what answers it instead (`/siegard:check-source`), is in the schema.

### 6. Verify

- `/plugin` → **Installed** lists `siegard` at the current version.
- `/siegard:siegard-status` runs with no `rules:` line — no copy of the rules sits at the root.
- Skills are invoked as `/siegard:<name>`; the bare form (`/analyse`, `/plan-work`, …) also works
  where no other plugin claims the name.
- Four skills are closed to the model and run only when you type them: `siegard-config`,
  `siegard-standard`, `siegard-archive` and `clarify-request`. A skill that needs one of them
  hands you the invocation ready to paste.

`/siegard:clarify-request <your request>` is the one entry point that executes nothing. Given a
request in your own words, it reads the project to settle what "this" or "the standard" points
at, asks you only the decisions that are yours — at most twice — and hands back one instruction
held to `schemas/clarified-request.json`: a mode (`ANALYZE`, `PLAN`, `OPERATE`, `IMPLEMENT`,
`IMPLEMENT_AND_VALIDATE`), the task, and every reading it took without asking listed under
`ASSUMPTIONS`. You then send that instruction, or say what to change. It does not rewrite a
request that is already a skill invocation.

## Adopting an existing project

A project whose code was written before Siegard is adopted, never re-delivered. One context at a
time, after steps 1–6 above:

1. **Measure the start, and sort the tree.** `python3 -B <plugin>/bin/trace.py --untraced
   <target-source-root>` lists every tracked file no binding names. Before an adoption every
   file is `unsurveyed`, except the declared tests, which are `uncertified`. Decide each one's
   place before the first survey: a context's source, or outside — configuration, wiring, a
   submodule — named with the adoption of the context it borders.
2. **`/siegard:survey`** over the context's source, cut into areas you name. One surveyor per
   area reads the code — never its documentation or comments — and returns material: every
   observable behavior, every refusal with its answer, the closed vocabularies, what upstream
   imposes, each fact beside the path it was read at. The material lands under
   `siegard-survey/<slug>/`, held to `schemas/survey.json`.
3. **`/siegard:analyse`** over that material. Beside the nodes it writes a ledger saying where
   every fact line went — a node, or a stated reason none holds it — and `trace.py --ledger`
   refuses a ledger short one fact. Its report hands the adoption invocation ready to fill.
4. **`/siegard:reconcile` as an adoption** over the ledger, with the files to keep out of the
   judgment (configuration, wiring) named as outside. Each file's judge reads the candidates that
   file's own facts reached; each cleared node is bound to the files that hold its fact; the
   first adoption writes `siegard-trace.json`. Tests you know assert a node's own condition may
   be offered as certifications in the same run. The judges run in waves of at most twenty, the
   harness's ceiling on agents running at once, and a wave ends when `trace.py --save-return`
   prints `0 pending` for it. A launch the harness refuses anyway is a wave cut too wide: the
   report hands `trace.py --stage … --concurrency <fewer>` ready to run again.
5. **Read what it hands back.** A candidate no file holds, a `contradicts` and an `unstated`
   finding all go back to `/siegard:analyse`. A `restates` finding is a comment saying a node's
   fact: remove every comment the file carries, not only the one cited, and reconcile the file
   again.
6. **Then the documentation**, as an ordinary `/siegard:analyse` increment over the adopted
   specification. What it corrects surfaces as drift, and a behavior the business wants changed is
   a corrective increment of `/siegard:plan-work`.
7. **And the tests, where the target declares them.** `/siegard:survey` in its tests form reads
   the declared tests instead of the source and writes intent material, held to
   `schemas/intent.json`: what the source should do, each fact beside the test it was read at and
   the source file it governs. `/siegard:analyse` writes its ledger as in step 3, and the adoption
   over that ledger judges each governed file against the nodes its own facts reached — never
   every candidate on every file, and never the tests themselves.

Steps 2–4 run as one under `/siegard:adopt-scope`, given an ask in your own words naming the
context, its areas and what stays outside: it invokes the three, commits after each with a
pathspec, and reports every decision, finding and count for you to review afterwards. A standing
`/goal` whose condition names it and reads mechanically — `trace.py --untraced <target>` printing
`0 unsurveyed` — carries every context in turn.

The adoption is complete when `--untraced` shows no `unsurveyed` file and `--convergence` no
`unreached` node; `/siegard:siegard-status` prints both. Nothing waits for it: new work may start
before, and the first review that reaches an unsurveyed file pays for it.

## When an update arrives

After `/reload-plugins`, the skills, the rules and the hooks are the new version together: the
rules travel inside the plugin, and the next session or agent start places the current ones.
Nothing at the project root needs to change.

A record already on disk is read as the contract it names. A reconciliation record keeps its
`siegard-reconcile/<n>` and a telemetry report its `siegard-telemetry/<n>`; neither is rewritten
to the newer shape, and a field a newer version adds is absent from an older record, which is not
a count of zero. Where a newer version counts a figure differently, its schema says which earlier
figures it is not comparable to: under `siegard-telemetry/12` a repeated agent is the same prompt
handed to the same agent type, and an `/11` report's repeats — the same description — are not
that count. A report run from inside a linked git worktree counts that worktree's sessions alone
and names it under `harness.worktree`.

### Across a major

A major changes something a consumer's own files hold, and says so in its version: the files a
consumer already has stop satisfying the contract, and the plugin refuses them rather than
reading them differently. The rewrite that brings them across is a tool in this repository's
`tools/`, which the plugin does not carry — clone this repository and run it from there, once
per project, over the project's own files.

**5.0.0 — one decision log beside each node.** Before 5.0.0 a specification held a single
`decision-log.md` at its root, each entry naming the file it filled under `location`. From 5.0.0
the log is `<slug>.log.md` beside the node it discloses, an entry names only its `field`, an
entry is written by `spec.py --decide` and never by hand, and the derived
`projections/decisions-by-node.md` no longer exists. A project still holding the root log has it
reported as a file that computes to no identity, which is the sign the rewrite has not run.

To migrate a project:

1. Update the plugin to 5.0.2 or later, so `spec.py` is the version that reads the new logs.
2. Commit or stash what the working tree holds. The rewrite touches only the specification
   root; a commit of that path keeps the rest of the tree out of it.
3. Preview it, then run it, from a clone of this repository:

   ```sh
   python3 tools/migrate_decision_log.py --dry-run <project>/<specification-root>
   python3 tools/migrate_decision_log.py <project>/<specification-root>
   ```

   It reads every YAML block of the root log, not only the first, groups the entries by
   `location`, writes one log per node, refuses unless the entries written equal the entries
   read, removes the root log and the projection, and runs `spec.py` over the root.
4. If it refuses an entry as not YAML, it names the lines: usually a colon inside an unquoted
   scalar. Quote the value, or turn it into a `|-` block with the text unchanged, and rerun.
   Nothing is written until every entry parses.
5. If `spec.py` then reports a log beside no node, a node left the specification without its
   decisions being retired; append the retirement with `spec.py --decide <identity> <root>` —
   a decision about where the fact went is the project's, and the tool makes none.
6. Run `spec.py --project <specification-root>` and commit the specification root in one commit.

A telemetry report written before 5.0.0 is the count it was and is read as such; the first
report written after it is `siegard-telemetry/8`, and its decision figures are not comparable
to a `/7` report's over the same window.

## For maintainers: what publishes a version

The consumer's update check compares the version in the installed plugin's manifest against the
one on this repository's default branch. A release is therefore: bump the version in
`src/claude/.claude-plugin/plugin.json`, `dist/.claude/.claude-plugin/plugin.json` and the
marker line of `src/claude/hooks/rules.md` (the suite refuses a mismatch among the three), assemble
`dist/`, run `python3 -m pytest`, and land it on `main`. No bump, no update.

Assembling `dist/` is two copies, and the suite refuses a release missing either:
`src/claude/` to `dist/.claude/` (a byte-for-byte copy, `__pycache__` left out), and what
`src/consumer/` authors for the consumer's root to `dist/`, beside the plugin.

```sh
rsync -a --delete --exclude '__pycache__' src/claude/ dist/.claude/
cp src/consumer/* dist/
```

A major is a version whose contract a persisted record no longer satisfies, and it ships with the
rewrite a consumer runs once, under `tools/` — outside `src/claude/`, so no assembly distributes it.
The consumer's sequence is fixed: update the plugin, run the migration from this repository against
the project root, run `deliver.py --check` over every delivery root and `plan.py --check` over every
plan, and land the rewrite as one commit. Between the update and the migration every root reads as
broken, so the two happen in one sitting. 4.0.0 is `tools/migrate_delivery_targets.py`: every
delivery record gains `target`, the key of `siegard.json`'s `targets` its paths are anchored at.
