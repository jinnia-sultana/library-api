from tests.conftest import borrow, make_book, make_member


def test_borrow_creates_loan_and_reduces_available_copies(client):
    book, member = make_book(client, total_copies=2), make_member(client)
    resp = borrow(client, book["id"], member["id"])
    loan = resp.get_json()
    assert resp.status_code == 201
    assert resp.headers["Location"] == f"/loans/{loan['id']}"
    assert loan["active"] is True
    assert client.get(f"/books/{book['id']}").get_json()["available_copies"] == 1


def test_borrow_with_no_copies_left_is_409(client):
    book = make_book(client, total_copies=1)
    first, second = make_member(client), make_member(client)
    assert borrow(client, book["id"], first["id"]).status_code == 201
    resp = borrow(client, book["id"], second["id"])
    body = resp.get_json()
    assert resp.status_code == 409
    assert body["type"] == "/problems/conflict"
    assert body["detail"] == "No copies of this book are available"
    assert "requestId" in body


def test_failed_borrow_does_not_change_state(client):
    book = make_book(client, total_copies=1)
    first, second = make_member(client), make_member(client)
    borrow(client, book["id"], first["id"])
    borrow(client, book["id"], second["id"])  # fails
    assert client.get(f"/books/{book['id']}").get_json()["available_copies"] == 0
    assert len(client.get("/loans").get_json()) == 1


def test_member_cannot_exceed_max_active_loans(client):
    member = make_member(client)  # MAX_ACTIVE_LOANS=2 in tests
    books = [make_book(client) for _ in range(3)]
    assert borrow(client, books[0]["id"], member["id"]).status_code == 201
    assert borrow(client, books[1]["id"], member["id"]).status_code == 201
    assert borrow(client, books[2]["id"], member["id"]).status_code == 409


def test_member_cannot_borrow_same_book_twice(client):
    book, member = make_book(client, total_copies=3), make_member(client)
    borrow(client, book["id"], member["id"])
    assert borrow(client, book["id"], member["id"]).status_code == 409


def test_return_restores_copy_and_marks_loan_inactive(client):
    book, member = make_book(client, total_copies=1), make_member(client)
    loan = borrow(client, book["id"], member["id"]).get_json()
    resp = client.post(f"/loans/{loan['id']}/return")
    assert resp.status_code == 200
    assert resp.get_json()["active"] is False
    assert client.get(f"/books/{book['id']}").get_json()["available_copies"] == 1


def test_returning_twice_is_409(client):
    book, member = make_book(client), make_member(client)
    loan = borrow(client, book["id"], member["id"]).get_json()
    client.post(f"/loans/{loan['id']}/return")
    assert client.post(f"/loans/{loan['id']}/return").status_code == 409


def test_return_unknown_loan_is_404(client):
    assert client.post("/loans/99/return").status_code == 404


def test_borrow_unknown_book_or_member_is_404(client):
    book, member = make_book(client), make_member(client)
    assert borrow(client, 999, member["id"]).status_code == 404
    assert borrow(client, book["id"], 999).status_code == 404


def test_borrow_with_missing_or_bad_fields_is_422(client):
    resp = client.post("/loans", json={"book_id": "one"})
    assert resp.status_code == 422
    assert {e["field"] for e in resp.get_json()["errors"]} == {"book_id", "member_id"}


def test_cannot_delete_book_or_member_with_active_loan(client):
    book, member = make_book(client), make_member(client)
    loan = borrow(client, book["id"], member["id"]).get_json()
    assert client.delete(f"/books/{book['id']}").status_code == 409
    assert client.delete(f"/members/{member['id']}").status_code == 409
    # after returning, deletion is allowed
    client.post(f"/loans/{loan['id']}/return")
    assert client.delete(f"/books/{book['id']}").status_code == 204
    assert client.delete(f"/members/{member['id']}").status_code == 204


def test_cannot_reduce_total_copies_below_copies_on_loan(client):
    book = make_book(client, total_copies=3)
    for _ in range(2):
        borrow(client, book["id"], make_member(client)["id"])
    payload = {k: book[k] for k in ("title", "author", "isbn")}
    resp = client.put(f"/books/{book['id']}", json={**payload, "total_copies": 1})
    assert resp.status_code == 409
    resp = client.put(f"/books/{book['id']}", json={**payload, "total_copies": 4})
    assert resp.status_code == 200
    assert resp.get_json()["available_copies"] == 2
