from lending.loans import Loan

FEE_CENTS_PER_OVERDUE_DAY = 100


def late_fee_cents(loan: Loan) -> int:
    # A loan returned after its due date pays 100 cents for each overdue day.
    overdue_days = (loan.returned_on - loan.due_on).days
    if overdue_days <= 0:
        return 0
    return overdue_days * FEE_CENTS_PER_OVERDUE_DAY
