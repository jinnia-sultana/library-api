import logging

from app.domain.book import Book
from app.domain.validation import validate_book
from app.errors import Conflict, NotFound

log = logging.getLogger("library.services.book")


class BookService:
    """Use cases for books. Knows nothing about HTTP."""

    def __init__(self, book_repo, loan_repo, max_copies):
        self.books = book_repo
        self.loans = loan_repo
        self.max_copies = max_copies

    def create_book(self, data):
        clean = validate_book(data, self.max_copies)
        if self.books.find_by_isbn(clean["isbn"]):
            raise Conflict(f"A book with ISBN {clean['isbn']} already exists")
        book = self.books.add(Book(**clean))
        log.info("book created id=%s", book.id)
        return book

    def get_book(self, book_id):
        book = self.books.get(book_id)
        if book is None:
            raise NotFound(f"Book {book_id} not found")
        return book

    def list_books(self):
        return self.books.list()

    def update_book(self, book_id, data):
        clean = validate_book(data, self.max_copies)
        book = self.get_book(book_id)
        other = self.books.find_by_isbn(clean["isbn"])
        if other is not None and other.id != book_id:
            raise Conflict(f"A book with ISBN {clean['isbn']} already exists")
        book.set_total_copies(clean["total_copies"])  # may raise Conflict
        book.title, book.author, book.isbn = clean["title"], clean["author"], clean["isbn"]
        self.books.save(book)
        log.info("book updated id=%s", book_id)
        return book

    def delete_book(self, book_id):
        self.get_book(book_id)
        if self.loans.active_for_book(book_id):
            raise Conflict("Cannot delete a book that has active loans")
        self.books.delete(book_id)
        log.info("book deleted id=%s", book_id)
