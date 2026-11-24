import logging


def test_health(client):
    assert client.get("/health").get_json() == {"status": "ok"}


def test_home_page_serves_the_demo_ui(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.mimetype == "text/html"
    assert b"<title>Library</title>" in resp.data


def test_request_id_is_generated_when_missing(client):
    resp = client.get("/health")
    assert len(resp.headers["X-Request-ID"]) == 12


def test_request_id_is_echoed_when_safe(client):
    resp = client.get("/health", headers={"X-Request-ID": "abc-123"})
    assert resp.headers["X-Request-ID"] == "abc-123"


def test_unsafe_request_id_is_replaced(client):
    unsafe = "bad id;<script>" + "x" * 100  # wrong characters and too long
    resp = client.get("/health", headers={"X-Request-ID": unsafe})
    assert resp.headers["X-Request-ID"] != unsafe
    assert len(resp.headers["X-Request-ID"]) == 12


def test_error_body_contains_same_request_id_as_header(client):
    resp = client.get("/books/999", headers={"X-Request-ID": "trace-1"})
    assert resp.get_json()["requestId"] == "trace-1"


def test_unknown_route_uses_problem_format(client):
    resp = client.get("/nope")
    assert resp.status_code == 404
    assert resp.mimetype == "application/problem+json"
    assert resp.get_json()["type"] == "/problems/not-found"


def test_wrong_method_is_405_problem(client):
    resp = client.patch("/books")
    assert resp.status_code == 405
    assert resp.mimetype == "application/problem+json"


def test_malformed_json_is_400(client):
    resp = client.post("/books", data="{not json", content_type="application/json")
    assert resp.status_code == 400
    assert resp.get_json()["type"] == "/problems/bad-request"


def test_json_array_instead_of_object_is_400(client):
    assert client.post("/books", json=[1, 2, 3]).status_code == 400


def test_unexpected_error_is_hidden_from_client_but_logged_in_full(app, client, caplog):
    def boom():
        raise RuntimeError("db password=hunter2")

    app.extensions["book_service"].list_books = boom
    with caplog.at_level(logging.ERROR, logger="library"):
        resp = client.get("/books")

    body = resp.get_data(as_text=True)
    assert resp.status_code == 500
    assert resp.get_json()["type"] == "/problems/internal"
    assert "hunter2" not in body and "RuntimeError" not in body  # client sees nothing internal
    assert "hunter2" in caplog.text and "Traceback" in caplog.text  # log has everything
