"""One end-to-end scenario: the whole thing you would click through in Postman,
run automatically, in order, with an assertion at every step."""


def test_full_library_lifecycle(client):
    # 1. create a book and a member
    book = client.post("/books", json={
        "title": "Refactoring", "author": "Martin Fowler",
        "isbn": "9780134757599", "total_copies": 1,
    }).get_json()
    member = client.post("/members", json={"name": "Carol", "email": "carol@example.com"}).get_json()

    # 2. borrow the only copy
    resp = client.post("/loans", json={"book_id": book["id"], "member_id": member["id"]})
    assert resp.status_code == 201
    loan_id = resp.get_json()["id"]
    assert client.get(f"/books/{book['id']}").get_json()["available_copies"] == 0

    # 3. a second borrow now fails with the business rule
    other = client.post("/members", json={"name": "Dan", "email": "dan@example.com"}).get_json()
    resp = client.post("/loans", json={"book_id": book["id"], "member_id": other["id"]})
    assert resp.status_code == 409

    # 4. return the book; borrowing works again
    assert client.post(f"/loans/{loan_id}/return").status_code == 200
    resp = client.post("/loans", json={"book_id": book["id"], "member_id": other["id"]})
    assert resp.status_code == 201

    # 5. history is visible
    loans = client.get("/loans").get_json()
    assert [l["active"] for l in loans] == [False, True]

    # 6. clean up: return, delete everything, confirm 404s
    client.post(f"/loans/{resp.get_json()['id']}/return")
    for path in (f"/books/{book['id']}", f"/members/{member['id']}", f"/members/{other['id']}"):
        assert client.delete(path).status_code == 204
        assert client.get(path).status_code == 404
