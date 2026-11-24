class InMemoryRepository:
    """Dict-backed storage. Swap the repositories to change the storage."""

    def __init__(self):
        self._rows = {}
        self._next_id = 1

    def add(self, entity):
        entity.id = self._next_id
        self._next_id += 1
        self._rows[entity.id] = entity
        return entity

    def get(self, entity_id):
        return self._rows.get(entity_id)

    def list(self):
        return list(self._rows.values())

    def save(self, entity):
        self._rows[entity.id] = entity
        return entity

    def delete(self, entity_id):
        self._rows.pop(entity_id, None)
