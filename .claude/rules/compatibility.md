---
paths:
  - "foundation/**"
  - "schemas/**"
  - "src/claude/**"
  - "dist/**"
---

# Compatibility and migration

## A change is breaking when it

- removes or renames a public artifact (skill, agent, hook, schema, template);
- alters a schema so that previously valid instances become invalid, or previously invalid instances
  become valid;
- changes workflow semantics, including transition guards and terminal states;
- invalidates persisted events or the workflow state derived from them;
- changes the observable contract of an installed user-invocable skill.

This list is the test. If a change matches any entry, it is breaking regardless of how small the
diff looks.

## Required for a breaking change

- state the break explicitly in the governing specification or ADR;
- define the supported migration path;
- version the affected contracts rather than mutating them in place;
- add a compatibility or migration test that fails against the old behavior;
- update release documentation.

## Versioning contracts

Increment the version in the contract's own identifier and filename (`review-verdict.json` →
`review-verdict.json`) and keep the prior version readable for as long as persisted artifacts
reference it. A consumer selects behavior on `contract_version`; it must not infer version from
shape.

## When not to preserve compatibility

Do not preserve compatibility that would retain incorrect or unsafe behavior. Break it, and record
the exception and its migration in the governing specification or ADR. An undocumented break is a
defect; a documented one is a decision.
