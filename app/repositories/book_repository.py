from app.repositories.base import InMemoryRepository


class BookRepository(InMemoryRepository):
    def find_by_isbn(self, isbn):
        return next((b for b in self._rows.values() if b.isbn == isbn), None)
