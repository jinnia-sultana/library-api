from dataclasses import asdict, dataclass

from app.errors import Conflict


@dataclass
class Book:
    title: str
    author: str
    isbn: str
    total_copies: int
    available_copies: int = None
    id: int = None

    def __post_init__(self):
        if self.available_copies is None:
            self.available_copies = self.total_copies

    # --- business rules (no Flask, no storage) ---
    def borrow(self):
        if self.available_copies == 0:
            raise Conflict("No copies of this book are available")
        self.available_copies -= 1

    def give_back(self):
        if self.available_copies >= self.total_copies:
            raise Conflict("All copies of this book are already in the library")
        self.available_copies += 1

    def set_total_copies(self, new_total):
        on_loan = self.total_copies - self.available_copies
        if new_total < on_loan:
            raise Conflict(f"Cannot set total_copies to {new_total}: {on_loan} copies are on loan")
        self.total_copies = new_total
        self.available_copies = new_total - on_loan

    def to_dict(self):
        return asdict(self)
