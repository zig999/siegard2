---
id: concept.fixture
type: term
title: fixture
description: A case in fixtures/ shaped like a real downstream need, used to exercise a capability.
status: accepted
contract_version: concept/1
tags: [scope, evidence, testing]
generated: { by: claude-opus-5, at: 2026-07-29T19:49:09Z }
---

# fixture

A case in `fixtures/` shaped like a real downstream application need, used to exercise a framework
[capability](capability.md).

Fixtures are how downstream reality enters this repository without downstream features entering it. The
scope fence in `CLAUDE.md` excludes business application work; the fixture is the one channel through
which such work enters, as evidence rather than as a feature.

A fixture is optional and no capability is blocked for want of one. It earns its cost where a failure
mode is not evident from the contract: a multi-step flow, a generator whose output has to be read, a case
that already broke once. An agent proposes a fixture and names what it would catch; only a maintainer
authorizes creating one.

A fixture is not the only evidence that an abstraction is real. An installation or upgrade incident, an
incompatibility with a supported Claude Code version, an eval result, a controlled dogfooding run, and a
failure observed in a consuming repository are all legitimate, and none of them passes through a
fixture. What no channel admits is a consuming repository's business rules.
