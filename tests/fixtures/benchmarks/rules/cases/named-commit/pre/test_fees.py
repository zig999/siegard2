from datetime import date, timedelta

from lending.fees import late_fee_cents
from lending.loans import Loan

DUE_ON = date(2026, 1, 20)


def returned_loan(returned_on: date) -> Loan:
    return Loan("C-1", "M-1", date(2026, 1, 6), DUE_ON, returned_on=returned_on)


def test_a_loan_returned_on_its_due_date_carries_no_late_fee():
    assert late_fee_cents(returned_loan(DUE_ON)) == 0


def test_a_loan_returned_before_its_due_date_carries_no_late_fee():
    assert late_fee_cents(returned_loan(DUE_ON - timedelta(days=5))) == 0


def test_each_further_calendar_day_after_the_due_date_adds_100_cents():
    previous = late_fee_cents(returned_loan(DUE_ON + timedelta(days=1)))
    for days_late in range(2, 41):
        fee = late_fee_cents(returned_loan(DUE_ON + timedelta(days=days_late)))
        assert fee - previous == 100, days_late
        assert (days_late - 1) * 100 <= fee <= days_late * 100, days_late
        previous = fee
