from datetime import date

from lending.fees import late_fee_cents
from lending.loans import Loan


def returned_loan(due_on, returned_on):
    return Loan("C-1", "M-1", date(2026, 1, 1), due_on, returned_on)


def test_a_loan_returned_on_its_due_date_carries_no_late_fee():
    loan = returned_loan(date(2026, 1, 15), date(2026, 1, 15))
    assert late_fee_cents(loan) == 0


def test_a_loan_returned_before_its_due_date_carries_no_late_fee():
    loan = returned_loan(date(2026, 1, 15), date(2026, 1, 10))
    assert late_fee_cents(loan) == 0


def test_a_loan_returned_one_day_after_its_due_date_carries_100_cents():
    loan = returned_loan(date(2026, 1, 15), date(2026, 1, 16))
    assert late_fee_cents(loan) == 100


def test_a_loan_returned_days_after_its_due_date_carries_100_cents_per_calendar_day():
    loan = returned_loan(date(2026, 1, 30), date(2026, 2, 4))
    assert late_fee_cents(loan) == 500
