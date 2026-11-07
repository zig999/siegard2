from datetime import date

from lending.loans import Loan


def test_a_loan_keeps_the_dates_it_was_made_with():
    loan = Loan("C-1", "M-1", date(2026, 1, 1), date(2026, 1, 15))
    assert (loan.borrowed_on, loan.due_on, loan.returned_on) == (date(2026, 1, 1), date(2026, 1, 15), None)
