---
subject: rules/lending/overdue-loan-blocks-borrowing
given:
  - Ana borrowed a copy of "Dom Casmurro" on day 1
  - the loan fell due on day 15
  - Ana had not returned it by the end of day 15
when:
  - Ana tries to borrow another copy on day 16
then:
  - the borrowing is refused
involves:
  - domain/lending/member
  - domain/lending/loan
  - rules/lending/loan-falls-due-fourteen-days-after-borrowing
---

## Description

Ana's late return of "Dom Casmurro" is the material's own example of an overdue loan blocking a new borrowing.
