---
id: concept.capability
type: term
title: capability
description: A reusable framework behavior with a testable contract, installed through the distribution.
status: accepted
contract_version: concept/1
tags: [framework, scope]
generated: { by: claude-opus-5, at: 2026-07-29T16:33:28Z }
---

# capability

A reusable framework behavior with a testable contract, installed into a target repository through the
[distribution](distribution.md).

A capability requires at least one [fixture](fixture.md) that exercises it. A behavior with no fixture
is not yet a capability — it is an intention.
