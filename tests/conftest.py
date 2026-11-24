import pytest

from app import create_app


@pytest.fixture
def app():
    # Fresh app (and fresh in-memory storage) for every test.
    return create_app({"MAX_COPIES": 5, "MAX_ACTIVE_LOANS": 2, "LOG_LEVEL": "WARNING"})


@pytest.fixture
def client(app):
    return app.test_client()


# ---- helpers: these replace clicking through Postman ----
_isbn_counter = {"n": 0}


def make_book(client, **overrides):
    _isbn_counter["n"] += 1
    payload = {
        "title": "Clean Architecture",
        "author": "Robert C. Martin",
        "isbn": f"978013449416{_isbn_counter['n'] % 10}",
        "total_copies": 2,
    }
    payload.update(overrides)
    resp = client.post("/books", json=payload)
    assert resp.status_code == 201, resp.get_json()
    return resp.get_json()


def make_member(client, **overrides):
    payload = {"name": "Alice", "email": f"alice{_isbn_counter['n']}@example.com"}
    _isbn_counter["n"] += 1
    payload.update(overrides)
    resp = client.post("/members", json=payload)
    assert resp.status_code == 201, resp.get_json()
    return resp.get_json()


def borrow(client, book_id, member_id):
    return client.post("/loans", json={"book_id": book_id, "member_id": member_id})
