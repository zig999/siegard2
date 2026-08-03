---
id: concept.transition-guard
type: term
title: transition guard
description: The condition that must hold for a workflow to move between states.
status: accepted
contract_version: concept/1
tags: [determinism, workflow]
generated: { by: claude-opus-5, at: 2026-07-29T16:33:28Z }
---

# transition guard

The condition that must hold for a workflow to move between states.

A guard must be deterministic and testable — decidable by a script or hook rather than by model
judgment. A guard that requires interpreting prose is not a guard; it is a suggestion, and two runs
will disagree.

Guards read [workflow state](workflow-state.md), not conversation history.
