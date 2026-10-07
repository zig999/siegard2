---
# `status` is one of:
#   proposed  — written, and its "Validation required before acceptance" list is not yet
#               satisfied in full. The specification still binds: it is the authority for what
#               it states, and `proposed` says the evidence it asked for is incomplete.
#   accepted  — every item of that list is satisfied and something in the repository proves each,
#               by name. Flipping this is the maintainer's, because it is a statement about their
#               ratification and not about the artifact.
#   retired   — superseded. It names what replaced it and is kept so a reference to it resolves.
id: "{{id}}"
title: {{title}}
status: {{proposed | accepted | retired}}
contract_version: spec/1
---

# {{short_title}}

## Scope

This specification fixes {{scope}}.

It decides {{decides}}.

### Decided elsewhere, deliberately not restated here

{{decided_elsewhere}}

## Definitions

- **{{term}}** — {{definition}}.

## Requirements

### {{requirement_group}}

- **R1** — {{requirement}}

## Validation required before acceptance

1. {{acceptance_condition}}

## Readings

<!-- Present wherever the list above names a fact that reverses or reopens a requirement. One line
     per reading, dated: the consumer and framework version read, the figure, what it was read
     from (a command, a file), and the verdict — `stands`, `reversed`, or `not yet read` with what
     must happen first. A criterion nobody records a reading for is a reversal nobody can trigger. -->

- {{date}} — {{verdict}}: {{figure, where it was read from, consumer and version}}.
