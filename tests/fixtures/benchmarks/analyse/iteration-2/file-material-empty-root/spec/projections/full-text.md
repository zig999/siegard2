# Full text

Derived by spec.py from the specification files; never edited. Grep here to locate;
open the node file a match names before claiming anything about it.

=== contracts/lending/reserved-copy-returned
---
type: domain-event
direction: published
payload: domain/lending/reservation
---

## Description

This event tells the member who reserved a copy that it has been returned and is being held for collection.

=== contracts/lending/reserved-copy-returned.log
---
entries:
- field: type
  unstated: The material says the reserving member is notified ("é avisado") but names no such event or message.
  decided: domain-event, published, payload domain/lending/reservation
  why: The notice reports something that already happened to a reservation and crosses to the member outside the system.
---

=== domain/lending/_context
---
strategic: core
---

## Description

Lending is the community library's lending of book copies to its members ("empréstimos aos sócios").
It covers borrowing, renewing and returning a copy, and the reservations that hold a returned copy for the member who reserved it.

## Responsibility

It decides whether a member may take a copy home and for how long.

=== domain/lending/_context.log
---
entries:
- field: strategic
  unstated: The material does not say whether lending is the library's core, supporting or generic concern.
  decided: core
  why: Controlling loans to members is the whole of what the material asks the system to do.
---

=== domain/lending/copy
---
type: aggregate-root
attributes:
  - name: code
    type: string
    required: true
relationships:
  - target: title
    type: reference
    cardinality: "1"
---

## Description

A copy ("exemplar") is one physical item of a title, and it is the unit that is lent.

## Responsibility

It is what a loan and a reservation point at, so two copies of one title are lent and reserved separately.

=== domain/lending/copy.log
---
entries:
- field: attributes.code
  unstated: The material says a title has several copies lent separately but names nothing that tells one copy from another.
  decided: 'code: string, required'
  why: Copies of one title are lent separately, so each needs its own identifying code.
---

=== domain/lending/loan
---
type: entity
aggregate: member
attributes:
  - name: borrowed_on
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

A loan ("empréstimo") is one copy in a member's hands, from the day it is borrowed until the day it is returned.
A loan whose due date has passed and that has not been returned is overdue.

## Responsibility

It records when a copy left, when it is due back, and whether it has been renewed.

=== domain/lending/loan.log
---
entries:
- field: aggregate
  unstated: The material does not say whether a loan stands alone or belongs to the member who took it.
  decided: member
  why: The three-loan limit and the overdue block are conditions over all of one member's loans, which hold immediately only if those loans change inside the member's aggregate.
- field: attributes.renewed
  unstated: The material says a loan renews once but not how a loan records that it was renewed.
  decided: 'renewed: boolean, required'
  why: A single renewal allowed means the only fact to keep is whether it has happened.
- field: attributes.returned_on
  unstated: The material speaks of returning a copy but not of what a loan records about the return.
  decided: 'returned_on: date, absent until the copy is returned'
  why: Overdue is judged by day, so the day of return is the fact that ends a loan's exposure to the overdue block.
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
  - borrow
  - renew
  - return
---

## Description

A member ("sócio") is a person registered with the library who may borrow its copies.

## Responsibility

It holds every loan the member has taken, so the limits on what one member may hold are checked in one place.

=== domain/lending/member.log
---
entries:
- field: attributes.name
  unstated: The material names a member only through the example "Ana" and states no attribute of a member.
  decided: 'name: string, required'
  why: The material's one example identifies a member by name, and no other member fact is stated.
---

=== domain/lending/reservation
---
type: aggregate-root
attributes:
  - name: reserved_on
    type: date
    required: true
  - name: collect_by
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

A reservation ("reserva") is a member's claim on a copy that is currently lent to someone else.
Its collection deadline is set when the copy is returned.

## Responsibility

It holds a returned copy for the member who reserved it.

=== domain/lending/reservation.log
---
entries:
- field: attributes.reserved_on
  unstated: The material mentions reserving a copy but states nothing a reservation records besides the member and the copy.
  decided: 'reserved_on: date, required'
  why: A reservation is a dated claim, and its date is the minimum fact distinguishing two reservations of one copy.
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

A title ("título") is a book as a work, such as "Dom Casmurro", which the library may hold in several copies.

## Responsibility

It groups the copies that are the same book.

=== rules/lending/loan-falls-due-fourteen-days-after-borrowing
---
type: invariant
statement: A loan that has not been renewed MUST fall due fourteen calendar days after the day its copy was borrowed.
constrains:
  - domain/lending/loan
---

## Description

This rule sets a loan's first due date; a renewal moves it.

=== rules/lending/loan-renews-at-most-once
---
type: invariant
statement: A loan MUST NOT be renewed more than once.
constrains:
  - domain/lending/loan
---

## Description

This rule refuses a second renewal of the same loan.

=== rules/lending/member-holds-at-most-three-loans
---
type: invariant
statement: A member MUST NOT hold more than three unreturned loans at the same time.
constrains:
  - domain/lending/member
  - domain/lending/loan
---

## Description

This rule refuses the borrowing that would give a member a fourth copy at once.

=== rules/lending/overdue-loan-accrues-daily-fine
---
type: invariant
statement: An unreturned loan whose due date has passed MUST accrue a fine of BRL 1.00 for each calendar day past its due date.
constrains:
  - domain/lending/loan
---

## Description

This rule fixes the late fine ("multa por atraso") a loan owes.

=== rules/lending/overdue-loan-accrues-daily-fine.log
---
entries:
- field: statement
  unstated: The material asks, as an open question, whether the late fine is charged per day of delay or as a fixed amount, and the board recommends BRL 1.00 per day.
  decided: BRL 1.00 per calendar day past the due date, following the board's recommendation
  why: The board's recommendation is the only value the material offers and nothing in it argues for a fixed amount.
---

=== rules/lending/overdue-loan-blocks-borrowing
---
type: invariant
statement: A member holding an unreturned loan whose due date has passed MUST NOT borrow another copy until that loan is returned.
constrains:
  - domain/lending/member
  - domain/lending/loan
---

## Description

This rule refuses borrowing to a member with an overdue loan, and lifts once every overdue loan is returned.

=== rules/lending/renewal-extends-due-date-by-fourteen-days
---
type: invariant
statement: Renewing a loan MUST move its due date fourteen calendar days later.
constrains:
  - domain/lending/loan
---

## Description

This rule sets the due date a renewal produces.

=== rules/lending/reserved-copy-blocks-renewal
---
type: policy
statement: A loan MUST NOT be renewed while a reservation is held on its copy.
constrains:
  - domain/lending/loan
  - domain/lending/reservation
consistency: eventual
---

## Description

This rule refuses a renewal of a loan whose copy someone has reserved.

=== rules/lending/reserved-copy-blocks-renewal.log
---
entries:
- field: consistency
  unstated: The material does not say how promptly a new reservation must stop a renewal of the loan holding that copy.
  decided: eventual
  why: The loan lives in the member's aggregate and the reservation in its own, so a reservation recorded at the same moment as a renewal may not refuse it.
---

=== rules/lending/returned-reserved-copy-held-for-collection
---
type: policy
statement: When a reserved copy is returned, the member who reserved it MUST be notified and the copy MUST be held for that member for three calendar days.
constrains:
  - domain/lending/loan
  - domain/lending/reservation
consistency: eventual
---

## Description

This rule sets the reservation's collection deadline and notifies the reserving member when the copy comes back.

=== rules/lending/returned-reserved-copy-held-for-collection.log
---
entries:
- field: statement
  unstated: The material says the reserving member has 3 days to collect the copy without saying whether those are calendar or working days.
  decided: three calendar days
  why: The material counts the loan term in calendar days ("dias corridos") and gives no other day-count for the library.
- field: consistency
  unstated: The material does not say how promptly the reserving member is notified after the return.
  decided: eventual
  why: The return changes the member's aggregate and the hold changes the reservation's, and a notice does not need to land in the same transaction as the return.
---

=== scenarios/lending/overdue-member-cannot-borrow
---
subject: rules/lending/overdue-loan-blocks-borrowing
given:
  - Ana borrowed a copy of "Dom Casmurro" on day 1
  - the loan fell due on day 15
  - Ana had not returned it by the end of day 15
when:
  - Ana tries to borrow another copy on day 16
then:
  - the borrowing is refused
involves:
  - domain/lending/member
  - domain/lending/loan
  - rules/lending/loan-falls-due-fourteen-days-after-borrowing
---

## Description

Ana's late return of "Dom Casmurro" is the material's own example of an overdue loan blocking a new borrowing.
