---
entries:
- field: type
  unstated: The material names the member but not which construct it is.
  decided: aggregate-root
  why: The three-loan limit and the overdue block are decided per member, so the member is the boundary those loans must change within.
- field: attributes.name
  unstated: The material states no attribute of a member; its example only calls one Ana.
  decided: name, string, required
  why: The example identifies a member by name, and a root needs at least one attribute to hold.
- field: relationships.loan
  unstated: The material does not say whether a loan is held inside the member or apart from it.
  decided: composition, 0..*
  why: Both the three-loan limit and the overdue block count a member's loans together, so they must change in one transaction with the member.
---
