---
id: dm.process.{{context}}.{{slug}}
type: process
title: {{title}}
boundary: dm.context.{{context}}
ddd: {{ddd}}
steps:
  - { node: dm.definition.{{context}}.{{first_step_slug}} }
description: {{description}}
question: {{question}}
contract_version: domain-object/2
generated: { by: {{generated_by}}, at: "{{generated_at}}" }
origin: {{origin}}
out_of_scope:
  - {{out_of_scope}}
---

# {{title}}

## Answer

{{description}}

## Outcomes

{{title}} ends in {{outcome}}.
