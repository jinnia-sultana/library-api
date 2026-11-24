import logging
import re
import uuid

from flask import g, request

log = logging.getLogger("library.request")

# Only trust a client-supplied id if it is short and harmless (no log injection).
_SAFE_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def register_middleware(app):
    @app.before_request
    def assign_request_id():
        incoming = request.headers.get("X-Request-ID", "")
        g.request_id = incoming if _SAFE_ID.match(incoming) else uuid.uuid4().hex[:12]

    @app.after_request
    def log_request(resp):
        resp.headers["X-Request-ID"] = g.get("request_id", "-")
        log.info("%s %s -> %s", request.method, request.path, resp.status_code)
        return resp
