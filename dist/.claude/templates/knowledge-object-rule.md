---
id: ko.rule.{{context}}.{{slug}}
type: rule
title: {{title}}
description: {{description}}
question: {{question}}
boundary: ko.boundary.{{context}}.{{boundary_slug}}
ddd: domain-rule
expression: "{{expression}}"
examples:
  - given: { {{given_field}}: "{{allowed_value}}" }
    when: { trigger: {{trigger}} }
    then: { outcome: allowed }
  - given: { {{given_field}}: "{{rejected_value}}" }
    when: { trigger: {{trigger}} }
    then: { outcome: rejected }
contract_version: knowledge-object/4
generated: { by: {{generated_by}}, at: {{generated_at}} }
origin: {{origin}}
out_of_scope:
  - {{out_of_scope}}
---

# {{title}}

## Answer

{{description}}

## Conditions

The rule holds when {{condition}}.
