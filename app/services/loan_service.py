import logging

from app.domain.loan import Loan
from app.domain.validation import validate_loan_request
from app.errors import Conflict, NotFound

log = logging.getLogger("library.services.loan")


class LoanService:
    """Borrow / return use cases. Holds the cross-entity business rules."""

    def __init__(self, book_repo, member_repo, loan_repo, max_active_loans):
        self.books = book_repo
        self.members = member_repo
        self.loans = loan_repo
        self.max_active_loans = max_active_loans

    def borrow_book(self, data):
        clean = validate_loan_request(data)
        book = self.books.get(clean["book_id"])
        if book is None:
            raise NotFound(f"Book {clean['book_id']} not found")
        member = self.members.get(clean["member_id"])
        if member is None:
            raise NotFound(f"Member {clean['member_id']} not found")

        active = self.loans.active_for_member(member.id)
        if len(active) >= self.max_active_loans:
            raise Conflict(f"Member already has {self.max_active_loans} active loans")
        if any(l.book_id == book.id for l in active):
            raise Conflict("Member already has this book on loan")

        book.borrow()  # raises Conflict("No copies ...") when none are left
        self.books.save(book)
        loan = self.loans.add(Loan(book_id=book.id, member_id=member.id))
        log.info("book borrowed loan=%s book=%s member=%s", loan.id, book.id, member.id)
        return loan

    def return_book(self, loan_id):
        loan = self.get_loan(loan_id)
        loan.mark_returned()  # raises Conflict if already returned
        book = self.books.get(loan.book_id)
        book.give_back()
        self.loans.save(loan)
        self.books.save(book)
        log.info("book returned loan=%s", loan_id)
        return loan

    def get_loan(self, loan_id):
        loan = self.loans.get(loan_id)
        if loan is None:
            raise NotFound(f"Loan {loan_id} not found")
        return loan

    def list_loans(self):
        return self.loans.list()
