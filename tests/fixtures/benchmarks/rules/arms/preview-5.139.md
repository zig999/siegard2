<persisted-output>
Output too large (13.3KB). Full output saved to: /tmp/an8/persisted/hook-SessionStart-additionalContext.txt

Preview (first 2KB):
# Siegard

These rules ship with Siegard 5.139.0. The plugin's hooks place them in every session and every
agent of a project that declares `siegard.json`; nothing is copied to the project root for them.

**The specification is the authority.** It is recorded as markdown nodes under one specification
root; source, tests and documentation derive from it. Where code and a node disagree, the node is
what the business decided.

What the framework does is stated where it runs, and nowhere else: each skill in its own file,
each script in the docstring `--help` prints, each contract in its schema under `schemas/`. Read
the one that applies; never restate it from memory.

## Which route a change takes

Six routes; which one a change takes is stated by a person and never inferred. **Invoke the
entry point by name rather than doing its work ad hoc**: the entry point is the route, and the
fifth names none.

| what changed | route |
|---|---|
| a fact of the business — a status, a refusal, what the system tells someone, who may see what | `/analyse` → `/plan-work` → `/implement-task` → `/review-change` |
| a capability's surface — a screen, a state, an interaction the specification already holds | `/plan-work` → `/implement-task` → `/review-change` |
| one wrong behavior in code already delivered | `/plan-work`'s corrective increment → `/implement-task` — never a fix typed straight into the file |
| **the comment alone** — prose in source that breaks the comment rule below, with the behavior correct and the fact already held | the source, changed directly (removal, never refresh), then `/reconcile` over that file |
| **the surface alone** — a control's label, a colour, spacing, a column's order, an icon | the source, changed directly, on a target `siegard.json` declares `edits_freely` |
| **source no delivery wrote** — a project adopting Siegard | `/survey` → `/analyse` → `/reconcile` as an adoption, one context at a time, or `/adopt-scope` carrying the three under one ask; the
...
</persisted-output>
