---
id: concept.fixture
type: term
title: fixture
description: A case in fixtures/ shaped like a real downstream need, used to exercise a capability.
status: accepted
contract_version: concept/1
tags: [scope, evidence, testing]
generated: { by: claude-opus-5, at: 2026-07-29T16:33:28Z }
---

# fixture

A case in `fixtures/` shaped like a real downstream application need, used to exercise a framework
[capability](capability.md).

Fixtures are how downstream reality enters this repository without downstream features entering it.
The scope fence in `CLAUDE.md` excludes business application work; the fixture is the one channel it
leaves open, and it is the only feedback loop that tells the framework which abstractions are real.
