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
  never ships; see `docs/adr/0006-separate-development-environment-from-framework-source.md`.
- Never place secrets, credentials, tokens, or environment-specific values in the distribution.
- Reject hidden defaults: if an installed component behaves differently when a setting is absent,
  state that default in the component itself, not only in the generator.

## Before the generator exists

No generator exists yet. Until one does, `dist/` is not authoritative and must not be treated as
release output. Do not create `dist/` by copying files by hand to make a rule appear satisfied —
build the generator, or record in `docs/bootstrap.md` that this step is still open.
