---
id: concept.least-privilege
type: term
title: least privilege
description: The rule that a component receives only the tools and permissions its contract names.
status: accepted
contract_version: concept/1
tags: [security, contract]
generated: { by: claude-opus-5, at: 2026-07-29T19:49:09Z }
sources:
  - resource: docs/adr/0007-least-privilege-and-untrusted-input.md
    title: Treat every input as untrusted and grant least privilege by default
---

# least privilege

The rule that an agent, skill, hook, or script receives only the tools and permissions its contract
names. The contract states the grant; the absence of a statement is not a grant, and a component with no
stated grant is incomplete rather than permissive.

The term entered this bundle to settle existing drift: the same rule appeared in four artifacts under
three phrasings — "minimum tools and permissions", "the minimum tools that role requires", and "minimum
tools". A [specialized agent](specialized-agent.md) is where it binds most visibly, but it governs every
component the [distribution](distribution.md) installs.
