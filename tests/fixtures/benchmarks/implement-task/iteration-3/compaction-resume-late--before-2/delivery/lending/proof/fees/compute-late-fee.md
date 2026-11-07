---
target: app
implementation: sha256:afe5f2ecd47aacdf5c59681d80b7b7d3390bfd4f8ff7ba641369b4a66a1ab23b
standard:
  at: standard.yaml
  pin: sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6
run: run/fees-compute-late-fee-suite
title: Proof of the late fee of a returned loan
summary: Three tests holding late_fee_cents to the task's two criteria, over returns
  on, before and after the due date.
tests:
- file: tests/test_fees.py
  name: test_a_loan_returned_on_its_due_date_carries_no_late_fee
  proves: A loan returned on or before its due date carries a late fee of 0 cents.
  fails_when: a loan returned on its due date is answered any fee other than 0 cents
- file: tests/test_fees.py
  name: test_a_loan_returned_before_its_due_date_carries_no_late_fee
  proves: A loan returned on or before its due date carries a late fee of 0 cents.
  fails_when: a loan returned before its due date is answered any fee other than 0
    cents
- file: tests/test_fees.py
  name: test_each_further_calendar_day_after_the_due_date_adds_100_cents
  proves: A loan returned after its due date carries 100 cents for each calendar day
    between its due date and its return.
  fails_when: a further calendar day of lateness adds anything but 100 cents
  demonstrates: rules/lending/late-fee-per-overdue-day
---
## What it is
Three tests holding late_fee_cents to the task's two criteria, over returns on, before and after the due date.

## Notes
None.
