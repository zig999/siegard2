---
entries:
- field: attributes.name
  unstated: The material names members (Ana) but states no attribute a member carries.
  decided: 'name: string, required'
  why: The material identifies its one member by name, so a member without a name could not be told apart in the domain's own terms.
- field: relationships.loan.type
  unstated: The material does not say where the consistency boundary of a loan lies.
  decided: 'composition: a member''s loans live inside the member aggregate'
  why: The three-loan limit and the overdue block both decide a borrowing from the member's other loans at the moment of borrowing, which only one aggregate can hold immediately.
---
