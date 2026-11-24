"""Application factory. All wiring happens here, in one place."""
from flask import Flask, jsonify

from app.config import Config
from app.error_handlers import register_error_handlers
from app.logging_setup import configure_logging
from app.middleware import register_middleware
from app.repositories.book_repository import BookRepository
from app.repositories.loan_repository import LoanRepository
from app.repositories.member_repository import MemberRepository
from app.routes import books, loans, members, ui
from app.services.book_service import BookService
from app.services.loan_service import LoanService
from app.services.member_service import MemberService


def create_app(overrides=None):
    config = Config(overrides)
    configure_logging(config.LOG_LEVEL)

    app = Flask(__name__)
    app.extensions["config"] = config

    # Dependencies are created here and passed in (constructor injection).
    book_repo, member_repo, loan_repo = BookRepository(), MemberRepository(), LoanRepository()
    app.extensions["book_service"] = BookService(book_repo, loan_repo, config.MAX_COPIES)
    app.extensions["member_service"] = MemberService(member_repo, loan_repo)
    app.extensions["loan_service"] = LoanService(
        book_repo, member_repo, loan_repo, config.MAX_ACTIVE_LOANS
    )

    register_middleware(app)
    register_error_handlers(app)
    app.register_blueprint(books.bp)
    app.register_blueprint(members.bp)
    app.register_blueprint(loans.bp)
    app.register_blueprint(ui.bp)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    return app
