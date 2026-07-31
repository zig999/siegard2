---
paths:
  - "src/claude/**"
  - "dist/**"
  - "scripts/**"
---

# Generated distribution

`dist/.claude/` is a release artifact assembled from the framework source in `src/claude/`. It is not
a source tree.

## Rules

- Do not hand-edit a file under `dist/` when a generator owns it. Change the source or the generator,
  then regenerate.
- Keep the output reproducible: the same committed source must produce the same distribution.
- Exclude source-only paths from the output — `specs/`, `tests/`, `fixtures/`, `docs/`, `.claude/`, and
  any other development-only configuration. `.claude/` is this repository's development environment and
  never ships. `CLAUDE.md` under **Repository layout** holds the path table; **The two trees** in
  `.claude/rules/claude-code-authoring.md` is the authority for the boundary itself.
- Never place secrets, credentials, tokens, or environment-specific values in the distribution.
- Reject hidden defaults: if an installed component behaves differently when a setting is absent,
  state that default in the component itself, not only in the generator.

## The generator

`scripts/generate_dist.py` produces `dist/.claude/`, `make dist` runs it, and `make dist-check` verifies
the committed tree against a fresh run. `dist/` is therefore authoritative and is release output. Change
the source or the generator and regenerate; a file placed there by hand is drift `verify_dist.py` reports.
