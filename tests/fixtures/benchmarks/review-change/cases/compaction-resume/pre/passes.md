coverage (inline):
coverage:
  - criterion: >-
      A loan returned on or before its due date carries a late fee of 0 cents.
    state: covered
    tests:
      - {file: tests/test_fees.py, name: test_a_loan_returned_on_its_due_date_carries_no_late_fee}
      - {file: tests/test_fees.py, name: test_a_loan_returned_before_its_due_date_carries_no_late_fee}
  - criterion: >-
      A loan returned after its due date carries 100 cents for each calendar day between its due date and its return.
    state: partial
    tests:
      - {file: tests/test_fees.py, name: test_each_further_calendar_day_after_the_due_date_adds_100_cents}
    why: >-
      The fee of a loan returned exactly one calendar day after its due date is held to a range of 0 to 100 cents, not to 100 cents, so the first day of lateness is unexercised.
unpaired: []

standard (inline, over `deliver.py --standard app/standard.yaml --reading --for lending/fees.py --for tests/test_fees.py`):
in_scope:
  - PY-01
looked_past: >-
  The tests' date arithmetic, which no rule in scope names.
