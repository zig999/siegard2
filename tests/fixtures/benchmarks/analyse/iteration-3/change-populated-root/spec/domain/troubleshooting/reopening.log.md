---
entries:
- field: type
  unstated: The material names a reopening and says each one records the customer's reason, but not whether the domain tells two reopenings apart by identity.
  decided: value-object
  why: A reopening is never changed after it is recorded, so two with equal reason and time are interchangeable.
- field: attributes.reason.type
  unstated: The material says the reason is the one the customer reports, not what shape it takes.
  decided: string
  why: The reason is the customer's own account, which no closed set of values could hold.
- field: attributes.reopened_at
  unstated: The material does not say that a reopening records when it happened.
  decided: a required datetime reopened_at
  why: The 7-day window can only be checked against the moment the reopening was made.
---
