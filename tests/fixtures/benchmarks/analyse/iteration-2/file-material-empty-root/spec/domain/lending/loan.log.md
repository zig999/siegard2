---
entries:
- field: aggregate
  unstated: The material does not say whether a loan stands alone or belongs to the member who took it.
  decided: member
  why: The three-loan limit and the overdue block are conditions over all of one member's loans, which hold immediately only if those loans change inside the member's aggregate.
- field: attributes.renewed
  unstated: The material says a loan renews once but not how a loan records that it was renewed.
  decided: 'renewed: boolean, required'
  why: A single renewal allowed means the only fact to keep is whether it has happened.
- field: attributes.returned_on
  unstated: The material speaks of returning a copy but not of what a loan records about the return.
  decided: 'returned_on: date, absent until the copy is returned'
  why: Overdue is judged by day, so the day of return is the fact that ends a loan's exposure to the overdue block.
---
