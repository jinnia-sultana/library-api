from tests.conftest import make_book

VALID = {"title": "Dune", "author": "Frank Herbert", "isbn": "9780441172719", "total_copies": 3}


def test_create_book_returns_201_with_location(client):
    resp = client.post("/books", json=VALID)
    body = resp.get_json()
    assert resp.status_code == 201
    assert resp.headers["Location"] == f"/books/{body['id']}"
    assert body["available_copies"] == 3


def test_get_book_returns_what_was_created(client):
    created = make_book(client)
    resp = client.get(f"/books/{created['id']}")
    assert resp.status_code == 200
    assert resp.get_json() == created


def test_list_books_returns_all(client):
    make_book(client)
    make_book(client)
    resp = client.get("/books")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 2


def test_update_book_replaces_fields(client):
    book = make_book(client)
    resp = client.put(f"/books/{book['id']}", json={**VALID, "title": "Dune Messiah"})
    assert resp.status_code == 200
    assert resp.get_json()["title"] == "Dune Messiah"
    assert client.get(f"/books/{book['id']}").get_json()["title"] == "Dune Messiah"


def test_delete_book_then_get_is_404(client):
    book = make_book(client)
    assert client.delete(f"/books/{book['id']}").status_code == 204
    assert client.get(f"/books/{book['id']}").status_code == 404


def test_create_book_with_bad_fields_gives_422_with_field_messages(client):
    resp = client.post("/books", json={"title": "", "isbn": "abc", "total_copies": 0})
    body = resp.get_json()
    assert resp.status_code == 422
    assert resp.mimetype == "application/problem+json"
    fields = {e["field"] for e in body["errors"]}
    assert fields == {"title", "author", "isbn", "total_copies"}


def test_total_copies_above_configured_maximum_is_422(client):
    resp = client.post("/books", json={**VALID, "total_copies": 6})  # MAX_COPIES=5 in tests
    assert resp.status_code == 422
    assert resp.get_json()["errors"][0]["field"] == "total_copies"


def test_duplicate_isbn_is_409(client):
    client.post("/books", json=VALID)
    resp = client.post("/books", json=VALID)
    assert resp.status_code == 409
    assert resp.get_json()["type"] == "/problems/conflict"


def test_unknown_book_is_404_problem(client):
    resp = client.get("/books/999")
    body = resp.get_json()
    assert resp.status_code == 404
    assert body["type"] == "/problems/not-found"
    assert "999" in body["detail"]


def test_update_unknown_book_is_404(client):
    assert client.put("/books/999", json=VALID).status_code == 404
