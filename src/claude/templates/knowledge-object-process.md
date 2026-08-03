---
id: ko.process.{{context}}.{{slug}}
type: process
title: {{title}}
description: {{description}}
question: How does {{title}} proceed, and how does it end?
boundary: ko.boundary.{{context}}.{{boundary_slug}}
ddd: {{ddd}}
steps:
  - { ko: ko.definition.{{context}}.{{first_step_slug}} }
  - { ko: ko.definition.{{context}}.{{last_step_slug}} }
status: proposed
contract_version: knowledge-object/1
generated: { by: {{generated_by}}, at: {{generated_at}} }
out_of_scope:
  - {{out_of_scope}}
---

# {{title}}

## Answer

{{description}}

## Outcomes

{{title}} ends in {{outcome}}.
