# Full text

Derived by spec.py from the specification files; never edited. Grep here to locate;
open the node file a match names before claiming anything about it.

=== domain/lending/_context
---
strategic: core
---

## Description

Lending covers how the neighbourhood community library lends copies of its books to its members (the material's "empréstimos" to "sócios").
It holds members, the copies they check out, the loans that record each checkout, and the reservations members place on copies.

## Responsibility

Lending decides who may check out, renew and return a copy, and when.

=== domain/lending/_context.log
---
entries:
- field: strategic
  unstated: The material does not say whether lending is where the library differs, is merely specific, or is already solved.
  decided: core
  why: Lending to members is the whole of what the material asks the library to control, so it is the problem this system exists for.
---

=== domain/lending/copy
---
type: aggregate-root
attributes:
  - name: inventory_number
    type: string
    required: true
relationships:
  - target: title
    type: reference
    cardinality: "1"
---

## Description

A copy is one physical exemplar of a title, lent on its own (the material's "exemplar").

## Responsibility

A copy is the unit a loan and a reservation are placed on.

=== domain/lending/copy.log
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

=== domain/lending/loan
---
type: entity
aggregate: member
attributes:
  - name: checked_out_on
    type: date
    required: true
  - name: due_on
    type: date
    required: true
  - name: renewed
    type: boolean
    required: true
  - name: returned_on
    type: date
relationships:
  - target: copy
    type: reference
    cardinality: "1"
---

## Description

A loan records one copy checked out by one member, from its checkout until its return (the material's "empréstimo").
A loan whose due date has passed while it is unreturned is overdue.

## Responsibility

A loan carries the dates that decide when its copy is due back and whether it may still be renewed.

=== domain/lending/loan.log
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

=== domain/lending/member
---
type: aggregate-root
attributes:
  - name: name
    type: string
    required: true
relationships:
  - target: loan
    type: composition
    cardinality: 0..*
operations:
  - check-out
  - renew-loan
  - return-copy
---

## Description

A member is a person registered with the library who may borrow its copies (the material's "sócio").

## Responsibility

A member holds the loans whose limits decide whether it may check out another copy.

=== domain/lending/member.log
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

=== domain/lending/reservation
---
type: aggregate-root
attributes:
  - name: notified_on
    type: date
relationships:
  - target: member
    type: reference
    cardinality: "1"
  - target: copy
    type: reference
    cardinality: "1"
---

## Description

A reservation is a member's claim on a copy that is currently lent to someone else (the material's "reserva").

## Responsibility

A reservation decides who is told when the copy comes back and who may pick it up first.

=== domain/lending/reservation.log
---
entries:
- field: type
  unstated: The material names a reservation on a copy but not which construct it is.
  decided: aggregate-root
  why: A reservation is placed, notified and picked up independently of the loan on the same copy.
---

=== domain/lending/title
---
type: aggregate-root
attributes:
  - name: name
    type: string
    required: true
---

## Description

A title is a book as a work, such as "Dom Casmurro", which the library may hold in several copies (the material's "título").

## Responsibility

A title groups the copies that are the same book.

=== domain/lending/title.log
---
entries:
- field: type
  unstated: The material names the title but not which construct it is.
  decided: aggregate-root
  why: Several copies point at one title, which must exist by identity apart from any copy.
---

=== rules/lending/loan-due-date
---
type: invariant
statement: A loan's due date MUST be fourteen calendar days after its checkout date, plus fourteen more calendar days once it is renewed.
constrains:
  - domain/lending/loan
---

## Description

This rule fixes when a loan's copy is due back.
It does not decide how many times a loan may be renewed.

=== rules/lending/loan-due-date.log
---
entries:
- field: statement
  unstated: The material says a renewal adds 14 days but not whether they count from the due date or from the day of renewal.
  decided: fourteen calendar days added to the due date
  why: The material says the loan is renewed for 14 more days, which reads as extending the period rather than restarting it.
---

=== rules/lending/loan-renewed-at-most-once
---
type: invariant
statement: A loan MUST be renewed at most once.
constrains:
  - domain/lending/loan
---

## Description

This rule limits renewal to a single extension of the loan.

=== rules/lending/member-holds-at-most-three-loans
---
type: invariant
statement: A member MUST hold at most three unreturned loans at the same time.
constrains:
  - domain/lending/member
  - domain/lending/loan
---

## Description

This rule limits how many copies one member may have out at once.
It does not decide whether an overdue loan blocks a checkout; rules/lending/overdue-loan-blocks-checkout does.

=== rules/lending/overdue-fine-per-day
---
type: invariant
statement: An overdue loan MUST accrue a fine of 1.00 BRL for each calendar day past its due date until it is returned.
constrains:
  - domain/lending/loan
---

## Description

This rule fixes what a member owes for returning a copy late.
It does not decide how or when the fine is paid.

=== rules/lending/overdue-fine-per-day.log
---
entries:
- field: statement
  unstated: The material asks whether the late fine is charged per day of delay or as a fixed amount, and the board suggests R$ 1.00 per day.
  decided: 1.00 BRL per calendar day past the due date, following the board recommendation
  why: The board is the only party in the material that answered the question, and per-day matches the calendar-day counting of the loan period.
---

=== rules/lending/overdue-loan-blocks-checkout
---
type: invariant
statement: A member holding an unreturned loan whose due date has passed MUST NOT check out another copy until that loan is returned.
constrains:
  - domain/lending/member
  - domain/lending/loan
---

## Description

This rule stops a member with an overdue loan from borrowing more.

=== rules/lending/renewal-refused-while-copy-reserved
---
type: policy
statement: A loan MUST NOT be renewed while a reservation is held on its copy.
constrains:
  - domain/lending/loan
  - domain/lending/reservation
consistency: eventual
---

## Description

This rule gives a member waiting on a copy precedence over the member who holds it.

=== rules/lending/renewal-refused-while-copy-reserved.log
---
entries:
- field: consistency
  unstated: The material does not say how promptly a reservation must be seen by a renewal.
  decided: eventual
  why: The rule crosses the member aggregate and the reservation aggregate, where an immediate demand is refused.
---

=== rules/lending/reserved-copy-held-three-days
---
type: invariant
statement: A returned copy under a reservation MUST stay available to the reserving member for three calendar days after that member is notified.
constrains:
  - domain/lending/reservation
---

## Description

This rule bounds how long a returned copy waits for the member who reserved it.
It does not decide what happens to the reservation once the three days pass.

=== rules/lending/reserved-copy-held-three-days.log
---
entries:
- field: statement
  unstated: The material says the reserving member has 3 days to pick the copy up but not whether these are calendar or business days.
  decided: three calendar days after notification
  why: The material counts the loan period in calendar days, and nothing in it distinguishes this period.
---

=== rules/lending/reserving-member-notified-on-return
---
type: policy
statement: When a copy under a reservation is returned, the member holding that reservation MUST be notified.
constrains:
  - domain/lending/loan
  - domain/lending/reservation
consistency: eventual
---

## Description

This rule tells the reserving member that the copy is back.

=== rules/lending/reserving-member-notified-on-return.log
---
entries:
- field: consistency
  unstated: The material does not say how soon after the return the notification must happen.
  decided: eventual
  why: The notification follows a return in another aggregate and the material sets no deadline for it.
---

=== scenarios/lending/overdue-member-cannot-check-out
---
subject: rules/lending/overdue-loan-blocks-checkout
given:
  - member Ana checked out a copy of "Dom Casmurro" on day 1
  - Ana has not returned that copy by the end of day 15
when:
  - Ana tries to check out another copy on day 16
then:
  - the checkout is refused
involves:
  - domain/lending/member
  - domain/lending/loan
---

## Description

This is the material's worked example of an overdue loan blocking a new checkout.
