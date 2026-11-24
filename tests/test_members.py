from tests.conftest import make_member


def test_member_full_lifecycle(client):
    # create
    resp = client.post("/members", json={"name": "Bob", "email": "Bob@Example.com"})
    assert resp.status_code == 201
    member = resp.get_json()
    assert resp.headers["Location"] == f"/members/{member['id']}"
    assert member["email"] == "bob@example.com"  # normalised to lowercase
    # read + list
    assert client.get(f"/members/{member['id']}").get_json() == member
    assert len(client.get("/members").get_json()) == 1
    # update
    resp = client.put(f"/members/{member['id']}", json={"name": "Robert", "email": "bob@example.com"})
    assert resp.status_code == 200 and resp.get_json()["name"] == "Robert"
    # delete
    assert client.delete(f"/members/{member['id']}").status_code == 204
    assert client.get(f"/members/{member['id']}").status_code == 404


def test_invalid_email_is_422_with_field_message(client):
    resp = client.post("/members", json={"name": "Bob", "email": "not-an-email"})
    assert resp.status_code == 422
    assert resp.get_json()["errors"] == [
        {"field": "email", "message": "email must be a valid email address"}
    ]


def test_duplicate_email_is_409(client):
    make_member(client, email="same@example.com")
    resp = client.post("/members", json={"name": "Other", "email": "same@example.com"})
    assert resp.status_code == 409


def test_updating_to_another_members_email_is_409(client):
    make_member(client, email="a@example.com")
    b = make_member(client, email="b@example.com")
    resp = client.put(f"/members/{b['id']}", json={"name": "B", "email": "a@example.com"})
    assert resp.status_code == 409


def test_unknown_member_is_404(client):
    assert client.get("/members/42").status_code == 404
