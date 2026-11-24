"""Input validation. Collects field-level messages and raises ValidationError (422)."""
import re

from app.errors import ValidationError

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_ISBN = re.compile(r"^(\d{9}[\dXx]|\d{13})$")


def _text(data, field, errors, max_len):
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        errors.append({"field": field, "message": f"{field} is required"})
        return None
    value = value.strip()
    if len(value) > max_len:
        errors.append({"field": field, "message": f"{field} must be at most {max_len} characters"})
        return None
    return value


def _positive_int(data, field, errors):
    value = data.get(field)
    # bool is a subclass of int in Python, so exclude it explicitly.
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        errors.append({"field": field, "message": f"{field} must be a positive integer"})
        return None
    return value


def validate_book(data, max_copies):
    errors = []
    title = _text(data, "title", errors, 200)
    author = _text(data, "author", errors, 100)

    isbn = data.get("isbn")
    clean_isbn = None
    if not isinstance(isbn, str) or not _ISBN.match(isbn.replace("-", "").replace(" ", "")):
        errors.append({"field": "isbn", "message": "isbn must be a valid ISBN-10 or ISBN-13"})
    else:
        clean_isbn = isbn.replace("-", "").replace(" ", "").upper()

    total = _positive_int(data, "total_copies", errors)
    if total is not None and total > max_copies:
        errors.append({"field": "total_copies", "message": f"total_copies must be at most {max_copies}"})

    if errors:
        raise ValidationError(errors)
    return {"title": title, "author": author, "isbn": clean_isbn, "total_copies": total}


def validate_member(data):
    errors = []
    name = _text(data, "name", errors, 100)
    email = data.get("email")
    if not isinstance(email, str) or not _EMAIL.match(email.strip()):
        errors.append({"field": "email", "message": "email must be a valid email address"})
        email = None
    else:
        email = email.strip().lower()
    if errors:
        raise ValidationError(errors)
    return {"name": name, "email": email}


def validate_loan_request(data):
    errors = []
    book_id = _positive_int(data, "book_id", errors)
    member_id = _positive_int(data, "member_id", errors)
    if errors:
        raise ValidationError(errors)
    return {"book_id": book_id, "member_id": member_id}
