---
entries:
- field: type
  unstated: The material names the loan but not which construct it is.
  decided: entity inside the member aggregate
  why: Each loan is tracked individually through renewal and return, and its limits are decided against its member.
- field: attributes.renewed
  unstated: The material says a loan may be renewed once but not how that is recorded.
  decided: renewed, boolean, required
  why: A single permitted renewal needs only whether it has happened.
---
