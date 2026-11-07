from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Loan:
    copy_code: str
    member_id: str
    borrowed_on: date
    due_on: date
    returned_on: date | None = None
    renewed: bool = False
