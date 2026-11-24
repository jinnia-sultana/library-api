"""One error format for every failure: RFC 9457 problem details."""
import logging

from flask import g, jsonify
from werkzeug.exceptions import HTTPException

from app.errors import AppError

log = logging.getLogger("library.errors")


def _problem(status, type_, title, detail, errors=None):
    body = {
        "type": type_,
        "title": title,
        "status": status,
        "detail": detail,
        "requestId": g.get("request_id"),
    }
    if errors:
        body["errors"] = errors
    resp = jsonify(body)
    resp.status_code = status
    resp.mimetype = "application/problem+json"
    return resp


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(err):
        log.warning("%s: %s", err.__class__.__name__, err.detail)
        return _problem(err.status, err.type, err.title, err.detail, err.errors)

    @app.errorhandler(HTTPException)
    def handle_http_error(err):
        # Unknown URL (404), wrong method (405), etc. raised by the framework.
        slug = err.name.lower().replace(" ", "-")
        return _problem(err.code, f"/problems/{slug}", err.name, err.description)

    @app.errorhandler(Exception)
    def handle_unexpected(err):
        # Full details (with traceback) go to the log only; the client gets
        # a generic message plus the request id to quote when reporting it.
        log.exception("Unhandled error")
        return _problem(
            500,
            "/problems/internal",
            "Internal server error",
            "An unexpected error occurred. Quote the requestId when reporting it.",
        )
