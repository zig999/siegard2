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

A capability does not require a [fixture](fixture.md). A fixture is the recommended evidence where the
behavior's failure mode is not evident from its contract, and one is created only with maintainer
authorization.
