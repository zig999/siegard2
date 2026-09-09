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

### 4. Place the rules file at the project root

The plugin carries the session rules every Siegard skill assumes, at `consumer/CLAUDE.md` inside
the plugin — and nothing loads a `CLAUDE.md` from inside a plugin. It has to sit at the consumer
project's root as `CLAUDE.md`. This is the one step a plugin update cannot do for you, because the
file may carry rules the project added of its own.

Run any Siegard skill, for example:

```
/siegard:siegard-status
```

The first thing every skill runs is `project.py`, and where the root `CLAUDE.md` is absent it
prints one `rules:` line with the exact `cp` command, pointing at the plugin's own copy. Paste
and run it. To find the copy by hand instead:

```bash
find ~/.claude/plugins -path '*siegard*/consumer/CLAUDE.md'
```

### 5. Declare the project

```
/siegard:siegard-config
```

writes `siegard.json` — the specification root, targets, work and delivery roots, and the
standard each target follows. Commit `CLAUDE.md`, `siegard.json` and `.claude/settings.json`:
those three make the install reproducible for everyone on the project.

### 6. Verify

- `/plugin` → **Installed** lists `siegard` at the current version.
- `/siegard:siegard-status` runs with no `rules:` line — the rules and the skills are from one
  release.
- Skills are invoked as `/siegard:<name>`; the bare form (`/analyse`, `/plan-work`, …) also works
  where no other plugin claims the name.

## When an update arrives

After `/reload-plugins`, the skills are the new version and the root `CLAUDE.md` is still the
old one. The first skill you run reports it — a `rules:` line naming the version the file
carries, the version the framework is, and where the current copy sits. Replace the Siegard
portion of the file, keeping anything the project added. A project whose rules match its
framework hears nothing.

## For maintainers: what publishes a version

The consumer's update check compares the version in the installed plugin's manifest against the
one on this repository's default branch. A release is therefore: bump the version in
`src/claude/.claude-plugin/plugin.json`, `dist/.claude/.claude-plugin/plugin.json` and the
marker line of `src/consumer/CLAUDE.md` (the suite refuses a mismatch among the three), assemble
`dist/`, run `python3 -m pytest`, and land it on `main`. No bump, no update.

A major is a version whose contract a persisted record no longer satisfies, and it ships with the
rewrite a consumer runs once, under `tools/` — outside `src/claude/`, so no assembly distributes it.
The consumer's sequence is fixed: update the plugin, run the migration from this repository against
the project root, run `deliver.py --check` over every delivery root and `plan.py --check` over every
plan, and land the rewrite as one commit. Between the update and the migration every root reads as
broken, so the two happen in one sitting. 4.0.0 is `tools/migrate_delivery_targets.py`: every
delivery record gains `target`, the key of `siegard.json`'s `targets` its paths are anchored at.
