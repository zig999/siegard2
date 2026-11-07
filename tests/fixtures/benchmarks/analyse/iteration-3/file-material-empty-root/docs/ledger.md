---
contract_version: siegard-ledger/1
material:
  - material.md
digests:
  material.md: "sha256:bec66729869237ae202e49b51f7c126ed8649a8fb6f4e5de2a8d69fadef13193"
entries:
  - at: material.md:3
    outside: The opening paragraph names the library's goal of controlling loans and states no fact of its own.
  - at: material.md:5
    node: rules/lending/member-holds-at-most-three-loans
  - at: material.md:6
    node: domain/lending/copy
  - at: material.md:6
    node: domain/lending/title
  - at: material.md:6
    node: domain/lending/loan
  - at: material.md:7
    node: rules/lending/loan-due-date
  - at: material.md:8
    node: rules/lending/loan-renewed-at-most-once
  - at: material.md:8
    node: rules/lending/loan-due-date
  - at: material.md:8
    node: rules/lending/renewal-refused-while-copy-reserved
  - at: material.md:9
    node: rules/lending/overdue-loan-blocks-checkout
  - at: material.md:10
    node: rules/lending/reserving-member-notified-on-return
  - at: material.md:10
    node: rules/lending/reserved-copy-held-three-days
  - at: material.md:11
    node: scenarios/lending/overdue-member-cannot-check-out
  - at: material.md:12
    outside: A button's colour and label and a list's on-screen ordering are what the interface chose, never a fact of the lending domain.
  - at: material.md:13
    node: rules/lending/overdue-fine-per-day
---
