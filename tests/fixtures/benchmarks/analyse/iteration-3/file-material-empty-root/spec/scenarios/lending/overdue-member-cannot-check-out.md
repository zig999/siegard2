---
subject: rules/lending/overdue-loan-blocks-checkout
given:
  - member Ana checked out a copy of "Dom Casmurro" on day 1
  - Ana has not returned that copy by the end of day 15
when:
  - Ana tries to check out another copy on day 16
then:
  - the checkout is refused
involves:
  - domain/lending/member
  - domain/lending/loan
---

## Description

This is the material's worked example of an overdue loan blocking a new checkout.
