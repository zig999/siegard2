---
entries:
- field: attributes.code
  unstated: The material says each copy is lent separately but states nothing that tells two copies of one title apart.
  decided: 'code: string, required'
  why: Copies of the same title are otherwise identical, and a loan and a reservation must name exactly one of them.
- field: relationships.reservation.cardinality
  unstated: The material speaks of 'the member who reserved' a copy and does not say whether several members may reserve one copy at once.
  decided: 0..1
  why: The material always names a single reserving member per copy and states no queue.
---
