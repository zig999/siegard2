from lending.loans import Loan

LATE_FEE_CENTS_PER_DAY = 100


def late_fee_cents(loan: Loan) -> int:
    overdue_days = (loan.returned_on - loan.due_on).days
    return max(overdue_days, 0) * LATE_FEE_CENTS_PER_DAY
