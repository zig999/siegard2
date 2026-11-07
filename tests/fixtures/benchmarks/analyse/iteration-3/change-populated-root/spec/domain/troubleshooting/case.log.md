---
entries:
- field: attributes.reopenings
  unstated: The material does not say where a case's reopenings are held or how many a case may have.
  decided: an attribute of the case holding many reopening values
  why: Nothing in the material limits a resolved case to one reopening.
- field: relationships.resolution.cardinality
  unstated: The material does not say what happens to a case's resolution when it is reopened and later resolved again.
  decided: 0..*
  why: A reopened case is resolved again, and keeping each resolution preserves the one the reopening's window counted from.
---
