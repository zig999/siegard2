---
id: dm.process.{{context}}.{{slug}}
type: process
title: {{title}}
boundary: dm.context.{{context}}
ddd: {{ddd}}
steps:
  - { ko: dm.definition.{{context}}.{{first_step_slug}} }
description: {{description}}
question: {{question}}
contract_version: domain-object/1
generated: { by: {{generated_by}}, at: {{generated_at}} }
origin: {{origin}}
out_of_scope:
  - {{out_of_scope}}
---

# {{title}}

## Answer

{{description}}

## Outcomes

{{title}} ends in {{outcome}}.
