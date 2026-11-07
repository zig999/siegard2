from lending.loans import Loan

LATE_FEE_CENTS_PER_OVERDUE_DAY = 100


def late_fee_cents(loan: Loan) -> int:
    overdue_days = (loan.returned_on - loan.due_on).days
    if overdue_days <= 0:
        return 0
    return overdue_days * LATE_FEE_CENTS_PER_OVERDUE_DAY
