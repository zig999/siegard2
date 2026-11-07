---
entries:
- field: aggregate
  unstated: The material does not say which aggregate owns a reservation.
  decided: copy
  why: A reservation blocks a renewal and is triggered by a return of one copy, whatever member holds it.
- field: attributes.pickup_deadline
  unstated: The material gives the reserving member three days to pick the copy up but names no field for that limit.
  decided: 'pickup_deadline: date, optional, set when the copy is returned'
  why: The three days start only at the return, so the deadline does not exist while the copy is still lent.
- field: attributes.reserved_on
  unstated: The material does not say when a reservation was made or whether that is recorded.
  decided: 'reserved_on: date, required'
  why: Whether a reservation exists at the time of a renewal is what the renewal rule reads, and a dated reservation answers it.
---
