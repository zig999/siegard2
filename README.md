# siegard-generator

This repository authors the Siegard framework under `src/claude/` and assembles it into
`dist/.claude/`, which ships as a Claude Code plugin. The repository is also the plugin's
marketplace: `.claude-plugin/marketplace.json` at this root is what a consumer adds once to
install the framework and receive its versions.

What the framework does, and how each script and skill works, is stated where it is enforced:
each script's own module docstring, printed by `--help`, and each skill's own `SKILL.md` under
`src/claude/skills/`. This page is the operational part only: how a consumer project installs
Siegard as a plugin and stays current.

## Installing Siegard in a consumer project

Run these inside a Claude Code session opened at the consumer project's root.

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

When asked for a **scope**, choose **project**. That records the marketplace and the plugin in
the consumer's `.claude/settings.json`, in this shape:

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
`hooks/hooks.json` places them into every session at start and into every agent at spawn. No
`CLAUDE.md` is copied to the project root, and a project's own `CLAUDE.md` stays its own. The
rules are short by design: they carry what binds a session when no skill is running — which
route a change takes, and what is never hand-edited or invented — and nothing a skill or a
script states in its own file. `/plugin` lists the skills; each script's `--help` states what it
does.

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

### 6. Verify

- `/plugin` → **Installed** lists `siegard` at the current version.
- `/siegard:siegard-status` runs with no `rules:` line — no copy of the rules sits at the root.
- Skills are invoked as `/siegard:<name>`; the bare form (`/analyse`, `/plan-work`, …) also works
  where no other plugin claims the name.

## Adopting an existing project

A project whose code was written before Siegard is adopted, never re-delivered. One context at a
time, after steps 1–6 above:

1. **Measure the start.** `python3 -B <plugin>/bin/trace.py --untraced <target-source-root>` lists
   every tracked file no binding names. Before an adoption every file is `unsurveyed`.
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
   be offered as certifications in the same run.
5. **Read what it hands back.** A candidate no file holds, a `contradicts` and an `unstated`
   finding all go back to `/siegard:analyse`.
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
