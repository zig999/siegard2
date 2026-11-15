from lending.loans import Loan

CENTS_PER_OVERDUE_DAY = 100


def late_fee_cents(loan: Loan) -> int:
    if loan.returned_on is None:
        raise ValueError("a loan that was not returned carries no late fee yet")
    overdue_days = (loan.returned_on - loan.due_on).days
    return max(overdue_days, 0) * CENTS_PER_OVERDUE_DAY
