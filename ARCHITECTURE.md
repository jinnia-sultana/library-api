# Architecture note

Request flow: **route -> service -> repository**, with the **domain** holding the business rules.
Each layer only calls the one below it.

| Layer | Files | Responsibility | Must not |
|---|---|---|---|
| Routes (handlers) | `app/routes/*.py` | Parse JSON, call one service method, choose the status code and `Location` header | contain SQL, storage or business rules |
| Services (use cases) | `app/services/*.py` | Orchestrate a use case: look things up, check cross-entity rules (member loan limit, duplicate ISBN), call the domain, save, log | import Flask or know about HTTP |
| Repositories (storage) | `app/repositories/*.py` | Store and find entities (in-memory dicts) | contain business rules |
| Domain | `app/domain/*.py` | Entities and rules: `Book.borrow()` ("no copies left"), `Loan.mark_returned()`, input validation | import Flask or touch storage |
| Errors | `app/errors.py` | `NotFound`, `Conflict`, `ValidationError`, `BadRequest` (pure Python) | import Flask |
| HTTP error mapping | `app/error_handlers.py` | The one place errors become RFC 9457 `application/problem+json` | |
| Middleware | `app/middleware.py`, `app/logging_setup.py` | Request ID, request log, request id in every log line | |
| Wiring | `app/__init__.py` (`create_app`) | Create repositories, inject them into services, register routes/middleware/errors | |
| Settings | `app/config.py`, `.env.example` | Read settings from the environment | |

## Business rules (all return 409)
- Borrow a book with no copies left
- Member already has the maximum number of active loans (`MAX_ACTIVE_LOANS`)
- Member already has this book on loan
- Return a loan that was already returned
- Delete a book or member that has active loans
- Reduce a book's `total_copies` below the number currently on loan
- Duplicate ISBN or email

## Status codes
201 + `Location` on create, 200 on read/update/return, 204 on delete, 400 malformed JSON,
404 unknown resource or route, 405 wrong method, 409 business rule failed,
422 invalid fields (with per-field messages), 500 unexpected error (generic message to the client, full traceback in the log).

## Changing storage
Only the files in `app/repositories/` need to change (for example, write SQLite versions
with the same method names) plus the three lines in `create_app` that construct them.
