---
contract_version: siegard-ledger/1
material:
  - material.md
digests:
  material.md: sha256:bec66729869237ae202e49b51f7c126ed8649a8fb6f4e5de2a8d69fadef13193
entries:
  - at: material.md:3
    outside: A context paragraph stating the purpose of the material, controlling loans to members, and no fact a node's field holds.
  - at: material.md:5
    node: rules/lending/member-holds-at-most-three-loans
  - at: material.md:6
    node: domain/lending/copy
  - at: material.md:6
    node: domain/lending/book
  - at: material.md:7
    node: rules/lending/loan-due-fourteen-days-after-borrowing
  - at: material.md:8
    node: rules/lending/loan-renewed-at-most-once
  - at: material.md:8
    node: rules/lending/renewal-extends-due-date-fourteen-days
  - at: material.md:8
    node: rules/lending/reserved-copy-blocks-renewal
  - at: material.md:9
    node: rules/lending/overdue-member-cannot-borrow
  - at: material.md:10
    node: rules/lending/returned-reserved-copy-notifies-reserver
  - at: material.md:10
    node: rules/lending/reserved-copy-held-three-days
  - at: material.md:10
    node: rules/lending/reserved-copy-lent-only-to-reserver
  - at: material.md:11
    node: scenarios/lending/overdue-member-refused-new-loan
  - at: material.md:12
    outside: A screen's button colour, label and list ordering are presentation, and state no fact of the lending domain.
  - at: material.md:13
    node: rules/lending/late-fee-per-overdue-day
  - at: material.md:13
    node: domain/lending/loan
---
