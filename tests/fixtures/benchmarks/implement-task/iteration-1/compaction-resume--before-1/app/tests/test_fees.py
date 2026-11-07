from datetime import date

from lending.fees import late_fee_cents
from lending.loans import Loan

DUE_ON = date(2026, 1, 15)


def returned_on(day):
    return Loan("C-1", "M-1", date(2026, 1, 1), DUE_ON, returned_on=day)


def test_a_loan_returned_before_its_due_date_carries_no_late_fee():
    assert late_fee_cents(returned_on(date(2026, 1, 10))) == 0


def test_a_loan_returned_on_its_due_date_carries_no_late_fee():
    assert late_fee_cents(returned_on(DUE_ON)) == 0


def test_a_loan_returned_one_day_after_its_due_date_carries_100_cents():
    assert late_fee_cents(returned_on(date(2026, 1, 16))) == 100


def test_a_loan_returned_several_days_after_its_due_date_carries_100_cents_per_day():
    assert late_fee_cents(returned_on(date(2026, 1, 22))) == 700
