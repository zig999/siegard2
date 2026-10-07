fact: how a case declares the resolution taken when no hypothesis is confirmed, given two distinct non-conclusion outcomes exist
outcome: decided
edits:
  - path: domain/troubleshooting/resolution-outcome.md
    text: |
      ---
      type: enumeration
      values:
        - confirmed
        - no-fault-found
        - inconclusive
      ---

      ## Description

      How a resolution closes a case. `confirmed` closes it on a hypothesis the evidence
      confirms. The two non-conclusion outcomes are `no-fault-found`, which closes it once the
      evidence refutes every hypothesis raised, and `inconclusive`, which closes it while the
      evidence neither confirms nor refutes any of them. Whether a case may close without
      resolving at all is case-transitions' (`cancel`), not this enumeration's.

      ## Responsibility

      None.
  - path: domain/troubleshooting/resolution.md
    text: |
      ---
      type: entity
      aggregate: case
      attributes:
        - name: summary
          type: string
          required: true
        - name: outcome
          type: resolution-outcome
          required: true
        - name: resolved_at
          type: datetime
          required: true
      ---

      ## Description

      The outcome that closes a case.

      ## Responsibility

      Record how the case closed: what solved the problem, or which non-conclusion outcome it closed on.
log:
  node: domain/troubleshooting/resolution-outcome
  field: type
  unstated: No node and no material names how a resolution declares the outcome it closes a case on when no hypothesis is confirmed.
  decided: enumeration
  why: A case that resolves with no confirmed hypothesis must declare which of two distinct non-conclusion outcomes it closed on, so the resolution carries a required outcome drawn from a closed set, confirmed, no-fault-found (every hypothesis refuted) or inconclusive (none confirmed or refuted).
noticed: No node states whether a resolution whose outcome is confirmed must name the hypothesis it confirmed.
