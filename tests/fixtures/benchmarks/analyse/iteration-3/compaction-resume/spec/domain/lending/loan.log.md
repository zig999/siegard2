---
entries:
- field: aggregate
  unstated: The material does not say which aggregate owns a loan.
  decided: member
  why: Both limits on borrowing are counted over one member's loans.
- field: attributes.renewed
  unstated: The material says a loan may be renewed once but not how a loan records that it was.
  decided: 'renewed: boolean, required'
  why: With at most one renewal allowed, whether it happened is the only fact the limit reads.
- field: attributes.returned_on
  unstated: The material speaks of returning a copy but names no return date.
  decided: 'returned_on: date, optional'
  why: The overdue block, the late fee and the reservation's three days are all counted from the day the copy came back.
- field: attributes.late_fee
  unstated: The material asks whether the late fee is charged per day or as a fixed amount and does not say where the fee is recorded.
  decided: 'late_fee: decimal, optional, an amount in BRL'
  why: The fee is owed for one overdue loan, so the loan is what carries it.
---
