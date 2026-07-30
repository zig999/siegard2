---
defaults:
  timezone: America/Sao_Paulo
  currency: BRL
  identity_strategy: surrogate
limits:
  body_lines: 24
---

# System defaults

The three defaults every attribute inherits, declared once as R26 requires.

An override is a fact about the attribute that carries it.
A repetition is noise, and spec 0002 R2 removes noise.

`limits.body_lines` is the ceiling R48 requires a validator to enforce.
The value lives here rather than in the validator because
`.claude/rules/distribution.md` rejects a hidden default, and a ceiling supplied by
whatever reads the knowledge base is exactly that.

Spec 0003 defers this file's schema beyond the three defaults, so `limits` is an
extension this fixture exercises rather than a form the specification fixed.
