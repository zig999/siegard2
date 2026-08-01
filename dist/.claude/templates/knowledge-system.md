---
defaults:
  timezone: {{timezone}}
  currency: {{currency}}
  identity_strategy: {{identity_strategy}}
limits:
  body_lines: {{body_lines}}
---

# System defaults

The three defaults every attribute inherits, declared once.

An override is a fact about the attribute that carries it.
A repetition is noise, and noise is what declaring them once removes.

`limits.body_lines` is the ceiling the body-length check enforces.
It lives here rather than in the validator because a ceiling supplied by whatever reads the
knowledge base is a hidden default, and a hidden default is rejected.
Where this file does not declare it, the check reports itself unenforceable rather than assuming a
value.

This file is authored and is not a knowledge object.
It carries no `id`, no `type`, and no body sections, and the validator treats it as reserved.
