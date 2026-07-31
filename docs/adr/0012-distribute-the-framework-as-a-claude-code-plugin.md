---
id: "0012"
title: Distribute the framework as a Claude Code plugin, and let the harness namespace it
status: accepted
contract_version: adr/1
---

# Distribute the framework as a Claude Code plugin

## Context

`specs/0008-distribution-layout.md` described the distribution as a tree copied into a consuming
repository's `.claude/`, with a reserved name prefix on every component to avoid collisions. Two reviews
found that design failing on its own terms:

- **It could not install its own enforcement.** Every hook named as a candidate —
  rejecting a write under `dist/`, rejecting an artifact that fails its schema, rejecting a schema change
  with no contract bump, rejecting a write to `CLAUDE.md` — is a session-wide guarantee. `specs/0010` R18
  scopes a hook declared in component frontmatter to that component's lifetime, and `specs/0008` R16
  forbids the framework rewriting a `settings.json` it does not own. So installing Siegard could not
  install the hooks that make Siegard's guarantees hold.
- **`scripts/` was an invented directory.** The harness has no documented convention for a script
  directory under `.claude/`, and the specification said so only by omission.

The prefix requirement had a documented basis — ADR-0009 records that two agents with the same name load
by filesystem read order with no documented precedence — but it invalidated both components that already
exist, and a rename reaches 17 files for `concept-author` and 14 for `knowledge-change`, including a
`const` in `schemas/concept-authoring-result.json`.

Research against the plugin documentation settled all of it, and settled it differently from the
assumption the specification was built on.

## Decision

The framework is distributed as a Claude Code plugin. `specs/0008-distribution-layout.md` carries the
resulting layout and rules; this record carries why, and the sourcing that decided it.

Four consequences of the plugin form replace things `specs/0008` had invented:

- **`hooks/hooks.json` at the plugin root** carries hooks in the same format as a settings file's `hooks`
  object, and they take effect while the plugin is enabled. Enabling the plugin installs the enforcement,
  with no file of the consumer's rewritten.
- **`bin/` at the plugin root** puts executables on the Bash tool's `PATH` while the plugin is enabled.
  Siegard's deterministic logic has a documented home instead of an invented one.
- **The plugin's `name` is the skill namespace.** A skill is invoked as `/<plugin>:<skill>`, and the
  documentation states plugin skills are always namespaced to prevent conflicts between plugins. A
  reserved prefix on a skill name is therefore redundant, and worse than redundant: it would render as
  `/siegard:siegard-knowledge-change`.
- **`version` in `.claude-plugin/plugin.json`** is the framework version, and a consumer receives an
  update only when it is bumped.

Agents are a different case and the difference is decided here rather than assumed. The documentation
states that project and user `.claude/agents/` definitions **override** same-named plugin agents. That is
a documented precedence, unlike the read-order behavior ADR-0009 recorded for the non-plugin case, and it
resolves in the consumer's favour — which is correct, and which means the framework's exposure is a
capability silently shadowed rather than a load order nobody can predict. Siegard therefore **detects and
reports shadowing rather than trying to prevent it by naming**: a name chosen to be unlikely is a
convention hoped to work, and a check is a check. No component is renamed.

A target pack is its own plugin, versioned independently. `specs/0004` R17 already states the framework
ships no default pack, so a `packs/` directory inside the framework distribution would be a directory the
framework's own rules guarantee is always empty.

### Sources

Normative for every harness behavior above, retrieved 2026-07-31:

- https://code.claude.com/docs/en/plugins — the plugin root layout and the recognized directories
  (`skills/`, `agents/`, `hooks/`, `bin/`, `monitors/`, `.mcp.json`, `.lsp.json`, `settings.json`); that
  only `plugin.json` belongs inside `.claude-plugin/`; that the manifest `name` is the skill namespace and
  plugin skills are always namespaced; that `version` gates updates and a missing `version` falls back to
  the git commit SHA; that project and user `.claude/agents/` definitions override same-named plugin
  agents, while a plugin skill and a same-named standalone skill both remain available; that
  `hooks/hooks.json` uses the settings `hooks` format; that plugin `settings.json` supports only the
  `agent` and `subagentStatusLine` keys; distribution by marketplace, `--plugin-dir`, and `--plugin-url`;
  and `claude plugin validate`.
- https://code.claude.com/docs/en/hooks — `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}` as path
  placeholders exported to a hook's environment.

A behavior not present on those pages at that date is not relied on. `specs/0013` R13 and R14 govern
re-verification. The two retrieval dates now in the framework — ADR-0009 at 2026-07-29 and these at
2026-07-31 — cover disjoint page sets: ADR-0009 cites skills, sub-agents, and best practices, and nothing
above re-cites any of them. R14 is therefore satisfied rather than breached, since no page is cited at two
dates, and what remains open is R13's obligation to re-verify each page at the next version bump of the
contract carrying it.

## Consequences

- `specs/0008` is rewritten around the plugin root rather than a `.claude/` overlay. The directories it
  invented (`scripts/`) or misplaced (`packs/`) are corrected, and the reserved-prefix requirement becomes
  a shadowing check.
- `concept-author` and `knowledge-change` keep their names. The rename that two reviews called cheap-now
  and expensive-later turns out to be unnecessary, which is worth stating plainly: the evidence removed
  the work rather than confirming it.
- `plugin.json` and Siegard's own manifest are two records, not one. The plugin manifest carries identity
  and version because the harness reads it; Siegard's manifest carries source revision, generator version,
  installed paths, shipped contract versions, capability lifecycle status, and declared overrides, because
  nothing else does.
- **`CLAUDE.md` names `dist/.claude/` as the assembled distribution.** A plugin root is any directory
  holding `.claude-plugin/plugin.json`, so `dist/.claude/` can remain that path and become a plugin root.
  It is a confusing name for one, and a clearer path is a `CLAUDE.md` change that only the maintainer
  makes — proposed, not applied.
- Siegard's own resources — schemas, templates, rules — sit in plugin-root directories the harness does not
  recognize and does not read. They are Siegard's to resolve through `${CLAUDE_PLUGIN_ROOT}`, and nothing
  about them depends on harness support.
- A plugin cannot ship arbitrary default settings: only `agent` and `subagentStatusLine` are supported. Any
  behavior Siegard wanted to establish through settings must be carried by a component or by a hook.
- The framework gains an external check it did not have: `claude plugin validate`. It is not a substitute
  for `make validate`, and it tests loadability rather than conformance to Siegard's contracts.

## Outstanding evidence

What this document states and nothing has yet exercised. A condition kept here is a debt;
removing one because the document binds would turn an open debt into a silent one.

1. A generator produces a plugin directory, `claude plugin validate` passes on it, and `--plugin-dir`
   loads it in a fixture. This is ADR-0009 condition 2 and the build plan open question 2, and it is
   what turns every claim above from documentation into behavior.
2. One hook ships in `hooks/hooks.json`, is shown to fire in the loaded fixture, and is shown to deny in
   both directions. Until then the central argument for this decision — that the plugin form installs
   enforcement — is documented rather than demonstrated.
3. The shadowing check exists: a test installs the plugin into a repository holding an agent of the same
   name and asserts the framework reports the shadowing rather than silently losing the capability.
4. One script ships in `bin/` and is invoked by a hook through `${CLAUDE_PLUGIN_ROOT}`, showing the script
   home is real.
5. A target pack ships as a second plugin and is shown to install and version independently of the
   framework.
