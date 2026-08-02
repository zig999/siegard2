---
id: concept.artifact-class
type: term
title: artifact class
description: The kind of artifact a capability produces, identified by the contract its instances satisfy.
status: accepted
contract_version: concept/1
tags: [capability, contracts]
generated: { by: claude-opus-5, at: 2026-07-30T15:26:04Z }
verified:
  - by: claude-opus-5
    at: 2026-08-01T18:20:00Z
sources:
  - resource: foundation/0005-capability-model.md
    title: Close the set of capability classes, and give each one thing it owns
  - resource: foundation/0006-capability-contracts.md
    title: Make a capability describe itself well enough to be chosen without being read
---

# artifact class

The kind of artifact a capability produces, identified by the contract its instances satisfy.
`domain-model`, `knowledge-object`, `impact-analysis`, and `knowledge-intake-plan` are four; the version
a producer stamps — `domain-model/2` — names the class and the revision of its contract together.

It is what `foundation/0005` R5 counts when it gives a specialized agent exactly one, and what R9 counts
when it gives a template exactly one. Counting is the whole use: an agent producing two classes has two
roles and cannot be delegated to for one of them, and a template producing two is two templates.

The class is not the file. One class may be written to many files — a knowledge base is one class in
hundreds of instances — and the count that matters is of classes, never of outputs.

## It is not a component class

`foundation/0005` R1 keeps the two apart, and says so in one line: *"An artifact is not a component and
needs no class."* A component executes or is delegated to, and the closed set of what may execute is
skill, specialized agent, hook, script, template, and target pack. An artifact is produced, and what
closes its set is the contract set rather than that table.

Confusing the two puts an artifact in front of the admission rule that governs components, which asks
what runs it — a question an artifact has no answer to.

## The earlier meaning, and why it is gone

This concept previously named the vocabulary of things *generation* produced from a knowledge object — a
type, a persistence schema, a migration, a validator, a conformance test — with the mapping from node
type to class owned by a [target pack](target-pack.md). That vocabulary lived in a specification the
repository removed with the generation path, and no capability reads it now.

The term survived in `foundation/0005` with the meaning above, which is the one a reader of the current
specification set needs. Recording the displacement rather than deleting the file is deliberate: the two
meanings are close enough that a reader meeting the old one in an ADR would otherwise think the current
requirements say something they do not.
