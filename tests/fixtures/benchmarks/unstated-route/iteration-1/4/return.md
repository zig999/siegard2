fact: what a published case's content hash is computed over
outcome: decided
edits:
  - path: rules/troubleshooting/published-case-hash-covers-payload.md
    text: |
      ---
      type: invariant
      statement: A published case's content hash MUST be computed over the whole published payload, the case's attributes together with its composed investigation, hypotheses, evidence and resolution.
      constrains:
        - domain/troubleshooting/case
      ---

      ## Description

      What a published case's content hash covers. Which contract publishes the case is
      contracts/troubleshooting/case-resolved's; the hash algorithm and how a consumer uses the
      hash are not decided here.
log:
  node: rules/troubleshooting/published-case-hash-covers-payload
  field: type
  unstated: No node and no material names a rule fixing what a published case's content hash is computed over.
  decided: invariant
  why: The hash identifies the content a consumer receives, and contracts/troubleshooting/case-resolved publishes the case aggregate as its payload, so the hash covers exactly that payload and nothing narrower.
noticed: No node states that a published case carries a content hash at all, nor which hash algorithm computes it.
