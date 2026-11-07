from datetime import date

from lending.fees import late_fee_cents
from lending.loans import Loan


def returned_loan(due_on, returned_on):
    return Loan("C-1", "M-1", date(2026, 1, 1), due_on, returned_on=returned_on)


def test_a_loan_returned_on_its_due_date_carries_no_fee():
    assert late_fee_cents(returned_loan(date(2026, 1, 15), date(2026, 1, 15))) == 0


def test_a_loan_returned_before_its_due_date_carries_no_fee():
    assert late_fee_cents(returned_loan(date(2026, 1, 15), date(2026, 1, 10))) == 0


def test_a_loan_returned_one_day_late_carries_one_hundred_cents():
    assert late_fee_cents(returned_loan(date(2026, 1, 15), date(2026, 1, 16))) == 100


def test_the_fee_is_one_hundred_cents_for_each_calendar_day_late():
    due_on = date(2026, 1, 25)
    cases = [
        (date(2026, 1, 28), 300),
        (date(2026, 2, 4), 1000),
        (date(2026, 3, 1), 3500),
    ]
    for returned_on, expected in cases:
        assert late_fee_cents(returned_loan(due_on, returned_on)) == expected, returned_on
