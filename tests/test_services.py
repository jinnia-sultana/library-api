"""Use cases run directly, with no Flask app and no HTTP server."""
import pytest

from app.domain.book import Book
from app.errors import Conflict, NotFound, ValidationError
from app.repositories.book_repository import BookRepository
from app.repositories.loan_repository import LoanRepository
from app.repositories.member_repository import MemberRepository
from app.services.book_service import BookService
from app.services.loan_service import LoanService
from app.services.member_service import MemberService


@pytest.fixture
def services():
    books, members, loans = BookRepository(), MemberRepository(), LoanRepository()
    return (
        BookService(books, loans, max_copies=5),
        MemberService(members, loans),
        LoanService(books, members, loans, max_active_loans=2),
    )


def test_borrow_last_copy_then_conflict(services):
    book_svc, member_svc, loan_svc = services
    book = book_svc.create_book(
        {"title": "T", "author": "A", "isbn": "9780441172719", "total_copies": 1}
    )
    m1 = member_svc.create_member({"name": "A", "email": "a@x.com"})
    m2 = member_svc.create_member({"name": "B", "email": "b@x.com"})
    loan_svc.borrow_book({"book_id": book.id, "member_id": m1.id})
    with pytest.raises(Conflict, match="No copies"):
        loan_svc.borrow_book({"book_id": book.id, "member_id": m2.id})


def test_service_raises_validation_error_with_fields(services):
    book_svc, _, _ = services
    with pytest.raises(ValidationError) as exc:
        book_svc.create_book({})
    assert {e["field"] for e in exc.value.errors} == {"title", "author", "isbn", "total_copies"}


def test_service_raises_not_found(services):
    _, _, loan_svc = services
    with pytest.raises(NotFound):
        loan_svc.return_book(123)


def test_domain_rule_has_no_framework_or_storage():
    book = Book(title="T", author="A", isbn="9780441172719", total_copies=1)
    book.borrow()
    with pytest.raises(Conflict):
        book.borrow()
    book.give_back()
    assert book.available_copies == 1
