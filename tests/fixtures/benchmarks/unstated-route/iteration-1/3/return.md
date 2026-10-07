fact: what the repeat-request key does when a diagnose call carries no ticket reference
outcome: decided
edits:
  - path: contracts/troubleshooting/diagnose.md
    text: |
      ---
      type: api
      direction: published
      operations:
        - diagnose
      answers:
        - operation: diagnose
          refusals:
            - when: The call carries no ticket reference, so no repeat-request key can be formed for it.
              answer: A refusal reporting ticket-reference-missing
      ---

      ## Description

      The surface through which a caller asks troubleshooting to diagnose a customer problem. Each
      call names the problem; repeated calls over one problem are a concern the surface answers.
log:
  node: contracts/troubleshooting/diagnose
  field: answers
  unstated: No node states what the repeat-request key does when a diagnose call carries no ticket reference.
  decided: No key is formed and the diagnose call is refused, answering a refusal reporting ticket-reference-missing.
  why: The contract states that repeated calls over one problem are a concern the surface answers, and a call without a ticket reference cannot be recognised as a repeat; accepting it would open a duplicate case the surface promised to prevent, while refusing it keeps the stated guarantee and is recoverable by the caller resending with the reference.
noticed: No node states what diagnose answers when it accepts, nor what it answers to a repeated call that does carry a ticket reference already seen.
