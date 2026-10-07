fact: whether a role, not a person, may be a recipient
outcome: stated
found: "intake/scope.md — \"The recipient publishes as an operational role — the on-call support role of the customer — and never as a named person: the role is what the customer keeps current, and a person moves on.\""
edits:
  - path: domain/troubleshooting/case.md
    text: |
      ---
      type: aggregate-root
      attributes:
        - name: id
          type: case-id
          required: true
        - name: status
          type: case-status
          required: true
        - name: opened_at
          type: datetime
          required: true
        - name: resolved_at
          type: datetime
        - name: recipient_role
          type: string
      relationships:
        - target: investigation
          type: composition
          cardinality: "1"
        - target: resolution
          type: composition
          cardinality: "0..1"
      operations:
        - open
        - start-investigation
        - resolve
        - cancel
      ---

      ## Description

      A customer problem submitted to the troubleshooting process. The recipient recorded on a case
      is an operational role of the customer, never a named person.

      ## Responsibility

      Control the investigation from opening to resolution or cancellation.
log:
  node: domain/troubleshooting/case
  field: attributes.recipient_role
  unstated: No node states that a case records a recipient, nor that the recipient is an operational role rather than a named person.
  found: "intake/scope.md — \"The recipient publishes as an operational role — the on-call support role of the customer — and never as a named person: the role is what the customer keeps current, and a person moves on.\""
noticed: The material does not state the shape of the role's value (carried here as string), nor whether a case must always record a recipient role.
