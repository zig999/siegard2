---
target: app
implementation: sha256:d640cac5ee9d1163a64b3341a63980d8b1b104d75b00d22cb8bc081732d836da
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
  fails_when: a loan returned on its due date, the boundary where the criterion changes
    behavior, is answered any fee other than 0 cents
- file: tests/test_fees.py
  name: test_a_loan_returned_before_its_due_date_carries_no_late_fee
  proves: A loan returned on or before its due date carries a late fee of 0 cents.
  fails_when: a loan returned before its due date is answered any fee other than 0
    cents, as an implementation counting the absolute distance between the dates would
- file: tests/test_fees.py
  name: test_each_further_calendar_day_after_the_due_date_adds_100_cents
  proves: A loan returned after its due date carries 100 cents for each calendar day
    between its due date and its return.
  fails_when: a further calendar day of lateness, from the second to the fortieth
    day after the due date and across a month boundary, adds anything but 100 cents,
    or the fee for a return n days late lies outside (n-1)*100 to n*100 cents, as
    a flat fee, another daily rate or a count anchored on any date but the due date
    would
not_applicable:
- edge_case: a loan with no return date
  why: the task and the rule state the fee of a returned loan only, and the implementation
    record defers the unreturned loan as outside the function's domain
- edge_case: a renewed loan
  why: renewal moves the due date and nothing else; the rule reads only the due date
    and the return, so renewal is a dimension that does not alter what the obligation
    requires
- edge_case: two computations over one loan at once
  why: the computation reads a frozen record and writes nothing, and no node states
    concurrent behavior
untested:
- 'The fee of a loan returned exactly one calendar day after its due date: the implementation
  inferred that the days between the due date and the return are their difference,
  so one day late is 100 cents, and no node decides whether the return day or the
  due date counts; the inference is recorded as unproven and no test pins it.'
- 'rules/lending/late-fee-per-overdue-day as a whole: the rule''s per-day rate is
  held by test_each_further_calendar_day_after_the_due_date_adds_100_cents, but the
  count of calendar days "between its due date and its return" is not stated by the
  node (whether an end day counts), so no finite test decides the fact whole without
  pinning the implementation''s inference.'
---
## What it is
Three tests holding late_fee_cents to the task's two criteria, over returns on, before and after the due date.

## Notes
None.
