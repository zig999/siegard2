fact: where a diagnose call's requester identity originates
outcome: decided
edits:
  - path: constraints/diagnose-requester-identity.md
    text: |
      ---
      statement: The requester identity of a diagnose call is read from the authenticated credential the call carries, never from a value supplied in the request itself.
      scope: troubleshooting
      ---

      ## Description

      Fixes where the diagnose surface takes the identity of whoever calls it. It does not decide
      how the credential is issued or verified, nor what the surface answers when a call carries
      none; those answers are the `answers` of contracts/troubleshooting/diagnose.
log:
  node: constraints/diagnose-requester-identity
  field: statement
  unstated: No node and no material names where a diagnose call's requester identity originates, and no constraint states it.
  decided: The requester identity of a diagnose call is read from the authenticated credential the call carries, never from a value supplied in the request itself.
  why: An identity the requester supplies as request data can name anyone, so only the credential the call is authenticated with attributes the call to its actual requester.
noticed: contracts/troubleshooting/diagnose declares no `answers`, so nothing states what diagnose answers when a call carries no authenticated credential.
