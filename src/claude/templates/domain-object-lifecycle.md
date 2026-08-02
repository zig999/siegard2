---
id: dm.lifecycle.{{context}}.{{slug}}
type: lifecycle
title: {{title}}
boundary: dm.context.{{context}}
subject: dm.definition.{{context}}.{{slug}}
states:
  - {{initial_state}}
  - {{next_state}}
initial: {{initial_state}}
transitions:
  - { from: {{initial_state}}, trigger: {{trigger}}, to: {{next_state}} }
rejections:
  - { from: {{next_state}}, trigger: {{trigger}}, error: dm.definition.{{context}}.{{error_slug}} }
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

## State semantics

A {{title}} in {{initial_state}} {{state_meaning}}.
