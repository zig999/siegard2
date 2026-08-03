---
id: concept.contract-version
type: term
title: contract version
description: The identifier a consumer reads to decide whether it can process an artifact.
status: accepted
contract_version: concept/1
tags: [contracts, compatibility]
generated: { by: claude-opus-5, at: 2026-07-29T16:33:28Z }
sources:
  - resource: .claude/rules/contracts.md
    title: Inter-agent artifact contracts
---

# contract version

An explicit identifier that a consumer reads to decide whether it can process an artifact, carried in
the artifact itself — for example `"contract_version": "review-verdict/1"`.

A consumer selects behavior on this value and must never infer version from an artifact's shape.
Inferring version from shape is how a compatible-looking change becomes a silent break.
