from app.repositories.base import InMemoryRepository


class LoanRepository(InMemoryRepository):
    def active_for_member(self, member_id):
        return [l for l in self._rows.values() if l.member_id == member_id and l.is_active]

    def active_for_book(self, book_id):
        return [l for l in self._rows.values() if l.book_id == book_id and l.is_active]
