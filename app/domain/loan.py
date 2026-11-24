from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.errors import Conflict


def _now():
    return datetime.now(timezone.utc)


@dataclass
class Loan:
    book_id: int
    member_id: int
    borrowed_at: datetime = field(default_factory=_now)
    returned_at: datetime = None
    id: int = None

    @property
    def is_active(self):
        return self.returned_at is None

    def mark_returned(self):
        if not self.is_active:
            raise Conflict("This loan has already been returned")
        self.returned_at = _now()

    def to_dict(self):
        return {
            "id": self.id,
            "book_id": self.book_id,
            "member_id": self.member_id,
            "borrowed_at": self.borrowed_at.isoformat(),
            "returned_at": self.returned_at.isoformat() if self.returned_at else None,
            "active": self.is_active,
        }
