---
contract_version: siegard-ledger/1
material:
  - material.md
digests:
  material.md: sha256:bec66729869237ae202e49b51f7c126ed8649a8fb6f4e5de2a8d69fadef13193
entries:
  - at: material.md:3
    outside: States the purpose of the system as a whole, which the lending context exists to serve, and no fact of its own.
  - at: material.md:5
    node: rules/lending/member-holds-at-most-three-loans
  - at: material.md:6
    node: domain/lending/copy
  - at: material.md:6
    node: domain/lending/loan
  - at: material.md:7
    node: rules/lending/loan-falls-due-fourteen-days-after-borrowing
  - at: material.md:8
    node: rules/lending/loan-renews-at-most-once
  - at: material.md:8
    node: rules/lending/renewal-extends-due-date-by-fourteen-days
  - at: material.md:8
    node: rules/lending/reserved-copy-blocks-renewal
  - at: material.md:9
    node: rules/lending/overdue-loan-blocks-borrowing
  - at: material.md:10
    node: rules/lending/returned-reserved-copy-held-for-collection
  - at: material.md:10
    node: contracts/lending/reserved-copy-returned
  - at: material.md:10
    node: domain/lending/reservation
  - at: material.md:11
    node: scenarios/lending/overdue-member-cannot-borrow
  - at: material.md:12
    outside: A button's color and label and a list's sort order are interface choices the implementation makes, never a fact of the domain (SPEC-005 R2).
  - at: material.md:13
    node: rules/lending/overdue-loan-accrues-daily-fine
---
