from datetime import date

from lending.fees import late_fee_cents
from lending.loans import Loan


def returned_loan(due_on, returned_on):
    return Loan("C-1", "M-1", date(2026, 3, 1), due_on, returned_on)


def test_a_loan_returned_on_its_due_date_carries_no_late_fee():
    assert late_fee_cents(returned_loan(date(2026, 3, 15), date(2026, 3, 15))) == 0


def test_a_loan_returned_before_its_due_date_carries_no_late_fee():
    assert late_fee_cents(returned_loan(date(2026, 3, 15), date(2026, 3, 10))) == 0


def test_a_loan_returned_one_day_late_carries_100_cents():
    assert late_fee_cents(returned_loan(date(2026, 3, 15), date(2026, 3, 16))) == 100


def test_a_loan_returned_days_late_across_a_month_end_carries_100_cents_per_calendar_day():
    assert late_fee_cents(returned_loan(date(2026, 3, 25), date(2026, 4, 7))) == 1300
