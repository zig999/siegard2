---
subject: rules/lending/overdue-member-cannot-borrow
given:
  - Ana borrowed a copy of "Dom Casmurro" on day 1, so the loan is due on day 15
  - on day 15 Ana has not returned it
when:
  - on day 16 Ana tries to borrow another copy
then:
  - the borrowing is refused
involves:
  - domain/lending/member
  - domain/lending/loan
  - rules/lending/loan-due-fourteen-days-after-borrowing
---

## Description

The worked example the material gives for the overdue block.
