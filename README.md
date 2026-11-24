# Library API

A small REST backend for a library: **books**, **members** and **loans** (borrow / return).
Built for CSE 3102L (Topic 04 lab task).

## Why Flask
Small and readable, so every line can be explained. It does not force a structure on you,
so the layers (routes, services, repositories, domain) are visible as plain folders.
I am also learning Python, and Flask lets me practise it directly.

## Run it (from a fresh clone)
```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # Windows: copy .env.example .env
python run.py                      # http://127.0.0.1:5000
```

## Test it
```bash
pytest
```
The tests call the real endpoints through Flask's test client and use fresh in-memory
storage per test, so no server and no Postman are needed. `tests/test_lifecycle.py` is the
automatic version of a full Postman walkthrough.

## Endpoints
| Method | Path | Success | Notes |
|---|---|---|---|
| POST | `/books` | 201 + `Location` | body: `title`, `author`, `isbn`, `total_copies` |
| GET | `/books`, `/books/<id>` | 200 | |
| PUT | `/books/<id>` | 200 | full replace |
| DELETE | `/books/<id>` | 204 | 409 if it has active loans |
| POST | `/members` | 201 + `Location` | body: `name`, `email` |
| GET | `/members`, `/members/<id>` | 200 | |
| PUT | `/members/<id>` | 200 | |
| DELETE | `/members/<id>` | 204 | 409 if it has active loans |
| POST | `/loans` | 201 + `Location` | body: `book_id`, `member_id`; **409 if no copies left** |
| GET | `/loans`, `/loans/<id>` | 200 | |
| POST | `/loans/<id>/return` | 200 | 409 if already returned |
| GET | `/health` | 200 | |

Every error uses one format (RFC 9457 `application/problem+json`):
```json
{"type": "/problems/conflict", "title": "Request conflicts with current state",
 "status": 409, "detail": "No copies of this book are available", "requestId": "c631fdb3d304"}
```
Validation errors (422) add `"errors": [{"field": "...", "message": "..."}]`.

## Configuration
Settings are read from environment variables (see `.env.example`). `.env` is git-ignored.
`MAX_COPIES` limits copies per book; `MAX_ACTIVE_LOANS` limits loans per member.

## Structure
See [ARCHITECTURE.md](ARCHITECTURE.md) for which files belong to which layer.

## Limitations
Storage is in-memory, so data is lost when the server stops. There is no authentication.

## AI use disclosure
- **What helped:** Claude (Anthropic) generated the first version of this project and its tests
  from the lab brief, following the layered structure in the course slides.

