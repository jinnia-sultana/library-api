from app.repositories.base import InMemoryRepository


class MemberRepository(InMemoryRepository):
    def find_by_email(self, email):
        return next((m for m in self._rows.values() if m.email == email), None)
