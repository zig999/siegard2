---
target: app
implementation: sha256:cac0acdf04f50692664067da5ac6dc89900891c67159c0e55889943816e3cb81
standard:
  at: standard.yaml
  pin: sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6
run: run/fees-compute-late-fee-suite
title: Proof of the late fee of a returned loan
summary: Four tests holding late_fee_cents to the task's two criteria and the per-day
  late-fee rule.
tests:
- file: tests/test_fees.py
  name: test_a_loan_returned_on_its_due_date_carries_no_fee
  proves: A loan returned on or before its due date carries a late fee of 0 cents.
  fails_when: A loan returned on the very day it is due is charged anything but 0
    cents, the boundary where the fee starts.
- file: tests/test_fees.py
  name: test_a_loan_returned_before_its_due_date_carries_no_fee
  proves: A loan returned on or before its due date carries a late fee of 0 cents.
  fails_when: A loan returned days ahead of its due date answers a non-zero fee, a
    negative credit included.
- file: tests/test_fees.py
  name: test_a_loan_returned_one_day_late_carries_one_hundred_cents
  proves: A loan returned after its due date carries 100 cents for each calendar day
    between its due date and its return.
  fails_when: The first day after the due date is not charged exactly 100 cents, an
    off-by-one in the day count included.
- file: tests/test_fees.py
  name: test_the_fee_is_one_hundred_cents_for_each_calendar_day_late
  proves: The rule's BRL 1.00 for each calendar day between the due date and the return,
    over spans within a month, across a month end and across February.
  fails_when: The fee stops scaling at 100 cents per calendar day, or counts days
    other than calendar days between the due date and the return.
  demonstrates: rules/lending/late-fee-per-overdue-day
not_applicable:
- edge_case: Two fee computations over one loan at once
  why: The function is pure over a frozen record, and no obligation states concurrent
    behavior.
- edge_case: A dependency that fails or answers slowly
  why: The computation reads no dependency.
- edge_case: An empty collection or a duplicate
  why: The function takes one loan, and no obligation reaches a collection.
untested:
- The implementation's inference that a loan with no return date raises ValueError
  is a behavior no node decides, recorded as unproven and not pinned by a test.
---
## What it is
Four tests holding late_fee_cents to the task's two criteria and the per-day late-fee rule.

## Notes
None.
