# Security

## What the plugin runs

Siegard executes. Knowing what it runs and where its limits sit is the first part of judging it.

- **Hooks.** The plugin's `hooks/hooks.json` runs two scripts, `hooks/rules.py` and
  `hooks/drift.py`, at session start, and `hooks/rules.py` again when an agent is spawned. They place
  context only in a project that declares `siegard.json` at its git toplevel and print nothing
  elsewhere, even where the plugin is enabled for every project you open; `drift.py` reads the
  project's trace with `trace.py --check` and never fails a session.
- **Skills run commands the project's own registry declares.** A skill installs what a project's
  standard authorizes and runs the steps it declares, so a delivery hands over a project that
  installs and builds. This repository composes no command and authorizes no package: every
  command, bound and package name is the consumer registry's. Approving a package is that
  registry gaining an entry, written by a person in their own file.
- **Every execution goes through `bin/run.py`,** which captures it and refuses a run under a name
  that already exists. A run that was not captured did not happen.
- **No agent holds a shell.** The shipped agents run without `Bash`, and
  `tests/test_agent_contract.py` enforces it. Only `task-implementer` and `test-author` can write
  files; every other agent returns content and the calling skill writes it.
- **Commits are bounded.** Only `/deliver-scope` and `/adopt-scope` commit, pathspec-scoped, one
  per step, never a branch, a push or a rewrite, and only under an ask the person's own words
  state end to end.
- **Network.** No script under `bin/` or `hooks/` imports a networking module. The commands a
  project's registry declares may use the network; that is the registry's.

A project that runs the plugin trusts its own `standard` registry and the skills' instructions to
the model. Read the registry before enabling a project.

## Reporting a vulnerability

Report privately; do not open a public issue for a vulnerability.

- Use GitHub's private vulnerability reporting on this repository (the Security tab, then
  *Report a vulnerability*), or
- write to <zig999@gmail.com>.

Include the version (`.claude-plugin/plugin.json`), what you did and what happened. Reports are
answered on a best-effort basis; there is no fixed response time.

In scope: a way for the plugin to run a command no registry declared, an agent gaining a shell or a
write it was not granted, a commit outside the bounds above, a hook placing context outside a project
that declares `siegard.json`, and a path where untrusted material in a project reaches execution without
passing `bin/run.py`. A vulnerability in Claude Code itself belongs to Anthropic.

## Supported versions

The latest release on `main`. A fix ships as a new version; an earlier one is not patched.
