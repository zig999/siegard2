---
entries:
- field: type
  unstated: The material names a reopening but not which construct records it.
  decided: value-object
  why: Two reopenings carrying the same reason and instant are interchangeable records inside their case.
- field: attributes.reopened_at
  unstated: The material does not say that a reopening records when it happened.
  decided: A required datetime reopened_at.
  why: The 7-day window can only be checked against the instant the reopening was made.
- field: attributes.reason.type
  unstated: The material says the customer's reason is recorded but not what shape it takes.
  decided: string
  why: The reason is what the customer said, which the material gives no closed set of values for.
---
