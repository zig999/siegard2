from lending.loans import Loan

LATE_FEE_CENTS_PER_OVERDUE_DAY = 100


def late_fee_cents(loan: Loan) -> int:
    if loan.returned_on is None:
        raise ValueError("a late fee is answered for a returned loan only")
    overdue_days = (loan.returned_on - loan.due_on).days
    return max(overdue_days, 0) * LATE_FEE_CENTS_PER_OVERDUE_DAY
