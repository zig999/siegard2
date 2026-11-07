from datetime import date

from lending.fees import late_fee_cents
from lending.loans import Loan

DUE_ON = date(2026, 3, 16)


def returned_loan(returned_on: date) -> Loan:
    return Loan("C-1", "M-1", date(2026, 3, 2), DUE_ON, returned_on)


def test_a_loan_returned_on_its_due_date_carries_no_late_fee():
    assert late_fee_cents(returned_loan(date(2026, 3, 16))) == 0


def test_a_loan_returned_before_its_due_date_carries_no_late_fee():
    assert late_fee_cents(returned_loan(date(2026, 3, 10))) == 0


def test_a_loan_returned_one_day_after_its_due_date_carries_100_cents():
    assert late_fee_cents(returned_loan(date(2026, 3, 17))) == 100


def test_a_loan_returned_ten_days_after_its_due_date_carries_100_cents_per_day():
    assert late_fee_cents(returned_loan(date(2026, 3, 26))) == 1000
