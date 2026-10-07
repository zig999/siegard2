# Full text

Derived by spec.py from the specification files; never edited. Grep here to locate;
open the node file a match names before claiming anything about it.

=== contracts/system/customer-registration
---
type: capability
---

## Description

The system lets its users register a customer.

=== domain/customer-management/_context
---
strategic: supporting
---

## Description

The people and organisations the business serves, each held once as a customer.
The material's word for a customer is cliente.

## Responsibility

Hold the record of every customer the business registers.

=== domain/customer-management/_context.log
---
entries:
- field: strategic
  unstated: The material does not say whether registering customers is where this business differs, merely specific to it, or already solved.
  decided: supporting
  why: Registering a customer is a record the business needs in its own terms and not where it competes.
---

=== domain/customer-management/customer
---
type: aggregate-root
attributes:
  - name: name
    type: string
    required: true
operations:
  - register
---

## Description

A person or organisation the business serves, told apart from every other by its own identity.
How a customer is captured or shown is not a fact of this node.

## Responsibility

Hold what the business records about one customer from its registration on.

=== domain/customer-management/customer.log
---
entries:
- field: attributes
  unstated: The material does not say what a customer record holds.
  decided: one attribute, name, a required string
  why: A registration that records nothing about the customer registers nothing, and a name is the least by which a person refers to one.
---
