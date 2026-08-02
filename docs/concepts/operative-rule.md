---
id: concept.operative-rule
type: term
title: operative rule
description: The imperative form of a rule, held by exactly one artifact and separate from the record of why it was decided.
status: accepted
contract_version: concept/1
tags: [governance, normative-source]
generated: { by: claude-opus-5, at: 2026-07-30T11:18:24Z }
sources:
  - resource: CLAUDE.md
    title: Siegard Code repository instructions
---

# operative rule

The imperative form of a rule: the statement an agent follows while working, phrased so it can be
conformed to or violated. An operative rule is held by exactly one artifact — `CLAUDE.md`, a
[specification](specification.md), a file under `.claude/rules/`, or a schema.

An operative rule is not the reasoning that produced it. The reasoning — the alternative rejected, the
cost accepted, what would falsify the decision — belongs to the decision record, and only there. The two
never restate each other: the ADR cites the operative rule, and the operative rule cites the ADR for its
reasoning.

The separation exists because the two artifacts are read at different moments. The operative rule loads
while someone authors; the decision record is opened when someone asks why. A rule copied into both
diverges silently, and the copy that decays is the one nobody consults while working.

Where a rule is stated is not the same question as whether it is enforced. `CLAUDE.md` and
`.claude/rules/` are context, not configuration, so an operative rule stated there holds by cooperation;
one enforced by a hook, a script, or a schema holds regardless of model judgment. Stating a rule and
guaranteeing it are separate acts, and a rule that must hold needs both.
