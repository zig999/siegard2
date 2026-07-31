---
name: upgrade
description: Moves an installed Siegard distribution to a newer version, detecting any file the repository changed and stopping rather than overwriting it. Use when a new framework version is available, or to check whether an installation has diverged. Not for the first installation, and not for changing what the framework ships.
disable-model-invocation: true
---

You move an installation forward, or you stop and say why.

One rule governs everything below: **a local change is the repository's to keep or to discard, never
the framework's to erase without saying so.** `it, and it is the reason this
is a skill rather than a copy.

## Required inputs

1. **the framework script root** — the directory holding `install_dist.py`. Installation decides
   this path; a component that guessed it would fail silently in a repository laid out differently.
2. **the installed plugin root**, and **the distribution to move to**.
3. **the repository root**, if you are to report shadowing.

A missing input is a stop, not a default.

## Procedure

1. **Check first.** `install_dist.py status --target <plugin> --project <repo>` reports every file
   that changed since installation, and every project agent that shadows a shipped one. Read it
   before doing anything.
2. **Where nothing diverged**, upgrade. The comparison is against the *installed* manifest, never
   against the incoming files: a file differing from the new distribution might simply be old, and
   only a file differing from what was recorded was changed by someone.
3. **Where something diverged, stop.** Report each file and what changed. The repository decides
   whether to keep the change or discard it; you do not decide for it, and you do not merge.
4. **Report shadowing either way.** `a project agent overrides a same-named plugin
   agent, and the precedence resolves in the repository's favour, which is correct. What is not
   correct is the capability being lost silently.
5. **Confirm the version moved.** A consumer reads the installed version from `plugin.json` and
   everything else from the distribution manifest.

## What you never do

- Overwrite a diverged file, or merge one.
- Upgrade part of the way. A partial upgrade leaves an installation matching no manifest at all,
  which is worse than the state it started in.
- Install where nothing is installed. That is a first installation and it is a different operation.
- Add a permission or disable a check in the receiving repository. `an installation
  may narrow what is permitted and never widen it.

## Result

Report the version moved from and to, the count of files replaced, and every divergence and shadow
by name. Where you stopped, the report is the whole product: a refusal that does not say which file
leaves the caller re-running it to find out.
