fact: whether citations are by name or by identifier
outcome: stated
found: "domain/troubleshooting/evidence.md, ## Description: \"Where a piece of evidence cites a source, citations are by name and never by identifier.\""
edits:
  - path: rules/troubleshooting/evidence-cites-by-name.md
    text: |
      ---
      type: invariant
      statement: A piece of evidence that cites a source MUST cite it by name and never by identifier.
      constrains:
        - domain/troubleshooting/evidence
      ---

      ## Description

      How a piece of evidence refers to the source it cites. What kinds of evidence exist is
      domain/troubleshooting/evidence-type's; whether a hypothesis holds enough evidence is
      rules/troubleshooting/hypothesis-requires-evidence's.
  - path: domain/troubleshooting/evidence.md
    text: |
      ---
      type: value-object
      attributes:
        - name: kind
          type: evidence-type
          required: true
        - name: value
          type: string
          required: true
        - name: collected_at
          type: datetime
          required: true
      ---

      ## Description

      One collected fact supporting or refuting a hypothesis.

      ## Responsibility

      None.
