---
entries:
- field: type
  unstated: The material names the copy but not which construct it is.
  decided: aggregate-root
  why: The domain cares which copy is lent and reserved, and loans and reservations point at it by identity.
- field: attributes.inventory_number
  unstated: The material names no attribute that tells copies of one title apart.
  decided: inventory_number, string, required
  why: Copies of one title are otherwise indistinguishable, and each is lent separately.
---
