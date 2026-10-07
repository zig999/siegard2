---
type: aggregate-root
attributes:
  - name: name
    type: string
    required: true
  - name: output_names
    type: string
    many: true
    required: true
---

## Description

A diagnostic the system can run over a case, declaring by name each output it produces.

## Responsibility

Own the names of the outputs a diagnostic produces.
