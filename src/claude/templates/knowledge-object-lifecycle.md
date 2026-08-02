---
id: ko.lifecycle.{{context}}.{{slug}}
type: lifecycle
title: {{title}}
description: {{description}}
question: Which states may a {{subject_title}} hold, and how does it move between them?
boundary: ko.boundary.{{context}}.{{boundary_slug}}
subject: ko.definition.{{context}}.{{subject_slug}}
states: [{{initial_state}}, {{terminal_state}}]
initial: {{initial_state}}
terminal: [{{terminal_state}}]
transitions:
  - { from: {{initial_state}}, trigger: {{trigger}}, to: {{terminal_state}} }
rejections:
  - { from: {{terminal_state}}, trigger: {{trigger}}, error: ko.definition.{{context}}.{{error_slug}} }
contract_version: knowledge-object/5
generated: { by: {{generated_by}}, at: {{generated_at}} }
origin: {{origin}}
out_of_scope:
  - {{out_of_scope}}
---

# {{title}}

## Answer

{{description}}

## State semantics

A {{subject_title}} in `{{initial_state}}` {{initial_meaning}}.
A {{subject_title}} in `{{terminal_state}}` {{terminal_meaning}}.
