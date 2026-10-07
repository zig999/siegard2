fact: whether a validation over a case reports every refusal it finds or stops at the first
outcome: decided
edits:
  - path: constraints/case-validation-reports-every-refusal.md
    text: |
      ---
      statement: A validation over a case reports every refusal it finds and never stops at the first.
      scope: troubleshooting
      ---

      ## Description

      How completely a validation over a case reports the conditions it refused. It says which
      refusals are reported, not what any of them refuses: each condition is its own rule's, such as
      rules/troubleshooting/case-transitions and rules/troubleshooting/hypothesis-requires-evidence.
      What a surface answers when it reports them is that surface's api contract's `answers`.
log:
  node: constraints/case-validation-reports-every-refusal
  field: statement
  unstated: No node and no material names a constraint on whether a validation over a case reports every refusal it finds or stops at the first.
  decided: A validation over a case reports every refusal it finds and never stops at the first.
  why: One request against a case can fail several of its rules together, such as resolving an open case whose hypothesis holds no evidence, and if validation stopped at the first refusal the caller would not see the others until a later attempt.
noticed: No node states what the diagnose operation of contracts/troubleshooting/diagnose answers when it accepts or refuses, because the api declares no `answers`.
