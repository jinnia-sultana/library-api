"""Application errors.

Pure Python: this module must never import Flask. The domain and service
layers raise these; only app/error_handlers.py turns them into HTTP responses.
"""


class AppError(Exception):
    status = 500
    type = "/problems/internal"
    title = "Internal error"

    def __init__(self, detail=None, errors=None):
        super().__init__(detail or self.title)
        self.detail = detail or self.title
        self.errors = errors or []


class BadRequest(AppError):
    status = 400
    type = "/problems/bad-request"
    title = "Malformed request"


class NotFound(AppError):
    status = 404
    type = "/problems/not-found"
    title = "Resource not found"


class Conflict(AppError):
    status = 409
    type = "/problems/conflict"
    title = "Request conflicts with current state"


class ValidationError(AppError):
    status = 422
    type = "/problems/validation"
    title = "Validation failed"

    def __init__(self, errors):
        super().__init__("One or more fields are invalid", errors)
