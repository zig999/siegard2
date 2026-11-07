# Full text

Derived by spec.py from the specification files; never edited. Grep here to locate;
open the node file a match names before claiming anything about it.

=== domain/lending/_context
---
strategic: core
---

## Description

Lending is the community library's lending of book copies to its members ("empréstimos" in the material).
It covers members, books, copies, loans, renewals, overdue loans, reservations and late fees.

## Responsibility

Keep track of which member holds which copy, until when, and on what terms a copy may be borrowed, renewed or picked up.

=== domain/lending/_context.log
---
entries:
- field: strategic
  unstated: The material does not say whether lending is where the library differs or a solved problem.
  decided: core
  why: Controlling loans to members is the whole of what the material asks the system to do.
---

=== domain/lending/book
---
type: aggregate-root
attributes:
  - name: title
    type: string
    required: true
---

## Description

A book ("livro", "título") is a title the library holds, such as "Dom Casmurro".
One book may have several copies.

## Responsibility

Name the work its copies are copies of.

=== domain/lending/copy
---
type: aggregate-root
attributes:
  - name: code
    type: string
    required: true
relationships:
  - target: book
    type: reference
    cardinality: "1"
  - target: reservation
    type: composition
    cardinality: 0..1
operations:
  - reserve
---

## Description

A copy ("exemplar") is one physical item of a book, lent on its own.

## Responsibility

Be the thing a loan lends and a reservation reserves.

=== domain/lending/copy.log
---
entries:
- field: attributes.code
  unstated: The material says each copy is lent separately but states nothing that tells two copies of one title apart.
  decided: 'code: string, required'
  why: Copies of the same title are otherwise identical, and a loan and a reservation must name exactly one of them.
- field: relationships.reservation.cardinality
  unstated: The material speaks of 'the member who reserved' a copy and does not say whether several members may reserve one copy at once.
  decided: 0..1
  why: The material always names a single reserving member per copy and states no queue.
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
  - name: late_fee
    type: decimal
relationships:
  - target: copy
    type: reference
    cardinality: "1"
---

## Description

A loan ("empréstimo") is one copy lent to one member, from the day it is borrowed until the day it is returned.
A loan is overdue while it is unreturned after its due date.

## Responsibility

Record when a copy was borrowed, when it is due, whether it was renewed and when it came back.

=== domain/lending/loan.log
---
entries:
- field: aggregate
  unstated: The material does not say which aggregate owns a loan.
  decided: member
  why: Both limits on borrowing are counted over one member's loans.
- field: attributes.renewed
  unstated: The material says a loan may be renewed once but not how a loan records that it was.
  decided: 'renewed: boolean, required'
  why: With at most one renewal allowed, whether it happened is the only fact the limit reads.
- field: attributes.returned_on
  unstated: The material speaks of returning a copy but names no return date.
  decided: 'returned_on: date, optional'
  why: The overdue block, the late fee and the reservation's three days are all counted from the day the copy came back.
- field: attributes.late_fee
  unstated: The material asks whether the late fee is charged per day or as a fixed amount and does not say where the fee is recorded.
  decided: 'late_fee: decimal, optional, an amount in BRL'
  why: The fee is owed for one overdue loan, so the loan is what carries it.
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

A member ("sócio") is a person registered with the community library who may borrow its copies.
A member holds the loans currently and previously made to them.

## Responsibility

Decide whether a member may borrow or renew, against the loans the member already holds.

=== domain/lending/member.log
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

=== domain/lending/reservation
---
type: entity
aggregate: copy
attributes:
  - name: reserved_on
    type: date
    required: true
  - name: pickup_deadline
    type: date
relationships:
  - target: member
    type: reference
    cardinality: "1"
---

## Description

A reservation ("reserva") is a member's claim on a copy, to borrow it once it is returned.

## Responsibility

Hold a copy for the member who reserved it.

=== domain/lending/reservation.log
---
entries:
- field: aggregate
  unstated: The material does not say which aggregate owns a reservation.
  decided: copy
  why: A reservation blocks a renewal and is triggered by a return of one copy, whatever member holds it.
- field: attributes.pickup_deadline
  unstated: The material gives the reserving member three days to pick the copy up but names no field for that limit.
  decided: 'pickup_deadline: date, optional, set when the copy is returned'
  why: The three days start only at the return, so the deadline does not exist while the copy is still lent.
- field: attributes.reserved_on
  unstated: The material does not say when a reservation was made or whether that is recorded.
  decided: 'reserved_on: date, required'
  why: Whether a reservation exists at the time of a renewal is what the renewal rule reads, and a dated reservation answers it.
---

=== rules/lending/late-fee-per-overdue-day
---
type: invariant
statement: A loan returned after its due date MUST carry a late fee of BRL 1.00 for each calendar day between its due date and its return.
constrains:
  - domain/lending/loan
---

## Description

None.

=== rules/lending/late-fee-per-overdue-day.log
---
entries:
- field: statement
  unstated: The material asks whether the late fee is charged per day of delay or as a fixed amount, and the board recommends BRL 1.00 per day.
  decided: BRL 1.00 per calendar day between the due date and the return, following the board's recommendation
  why: The board is the body the material names as recommending, and nothing in the material argues for a fixed amount.
---

=== rules/lending/loan-due-fourteen-days-after-borrowing
---
type: invariant
statement: A loan's due date MUST be fourteen calendar days after the day its copy was borrowed, until the loan is renewed.
constrains:
  - domain/lending/loan
---

## Description

Calendar days count every day, weekends and holidays included ("dias corridos" in the material).

=== rules/lending/loan-renewed-at-most-once
---
type: invariant
statement: A loan MUST NOT be renewed more than once.
constrains:
  - domain/lending/loan
---

## Description

None.

=== rules/lending/member-holds-at-most-three-loans
---
type: invariant
statement: A member MUST NOT hold more than three unreturned loans at the same time.
constrains:
  - domain/lending/member
  - domain/lending/loan
---

## Description

A borrowing that would give the member a fourth unreturned loan is refused.

=== rules/lending/overdue-member-cannot-borrow
---
type: invariant
statement: A member holding an unreturned loan past its due date MUST NOT borrow another copy until that loan is returned.
constrains:
  - domain/lending/member
  - domain/lending/loan
---

## Description

None.

=== rules/lending/renewal-extends-due-date-fourteen-days
---
type: invariant
statement: Renewing a loan MUST move its due date fourteen calendar days later.
constrains:
  - domain/lending/loan
---

## Description

None.

=== rules/lending/renewal-extends-due-date-fourteen-days.log
---
entries:
- field: statement
  unstated: The material says a renewal lasts 'mais 14 dias' and does not say whether they count from the current due date or from the day of renewal, nor in which kind of day.
  decided: the due date moves fourteen calendar days later than it stood
  why: '''Mais 14 dias'' adds to the loan''s term, and the material counts that term in calendar days.'
---

=== rules/lending/reserved-copy-blocks-renewal
---
type: policy
statement: A loan MUST NOT be renewed while its copy holds a reservation.
constrains:
  - domain/lending/loan
  - domain/lending/reservation
consistency: eventual
---

## Description

The reservation is read as the copy last recorded it.

=== rules/lending/reserved-copy-blocks-renewal.log
---
entries:
- field: consistency
  unstated: The material does not say how promptly a new reservation must stop a renewal.
  decided: eventual
  why: The loan sits in the member's aggregate and the reservation in the copy's, so the renewal reads the reservation as last recorded.
---

=== rules/lending/reserved-copy-held-three-days
---
type: invariant
statement: A reservation's pickup deadline MUST be three calendar days after the day its copy was returned.
constrains:
  - domain/lending/reservation
---

## Description

Until the pickup deadline the copy is held for the member who reserved it.

=== rules/lending/reserved-copy-held-three-days.log
---
entries:
- field: statement
  unstated: The material gives the reserving member 3 days to pick the copy up and does not say whether they are calendar or business days.
  decided: three calendar days after the day the copy was returned
  why: The material counts its only other period in calendar days ('dias corridos') and names no other way of counting.
---

=== rules/lending/returned-reserved-copy-notifies-reserver
---
type: policy
statement: When a reserved copy is returned, the member who reserved it MUST be notified that the copy is ready to be picked up.
constrains:
  - domain/lending/loan
  - domain/lending/reservation
consistency: eventual
---

## Description

None.

=== rules/lending/returned-reserved-copy-notifies-reserver.log
---
entries:
- field: consistency
  unstated: The material does not say how promptly the reserving member is notified after the return.
  decided: eventual
  why: The return is recorded in the borrower's aggregate and the reservation in the copy's, and a notice delivered shortly after the return meets what the material asks.
---

=== scenarios/lending/overdue-member-refused-new-loan
---
subject: rules/lending/overdue-member-cannot-borrow
given:
  - Ana borrowed a copy of "Dom Casmurro" on day 1, so the loan is due on day 15
  - on day 15 Ana has not returned it
when:
  - on day 16 Ana tries to borrow another copy
then:
  - the borrowing is refused
involves:
  - domain/lending/member
  - domain/lending/loan
  - rules/lending/loan-due-fourteen-days-after-borrowing
---

## Description

The worked example the material gives for the overdue block.
