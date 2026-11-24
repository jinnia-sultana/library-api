from flask import Blueprint, jsonify, url_for

from app.routes.helpers import created, json_body, service

bp = Blueprint("books", __name__, url_prefix="/books")


@bp.post("")
def create_book():
    book = service("book_service").create_book(json_body())
    return created(book.to_dict(), url_for("books.get_book", book_id=book.id))


@bp.get("")
def list_books():
    return jsonify([b.to_dict() for b in service("book_service").list_books()])


@bp.get("/<int:book_id>")
def get_book(book_id):
    return jsonify(service("book_service").get_book(book_id).to_dict())


@bp.put("/<int:book_id>")
def update_book(book_id):
    book = service("book_service").update_book(book_id, json_body())
    return jsonify(book.to_dict())


@bp.delete("/<int:book_id>")
def delete_book(book_id):
    service("book_service").delete_book(book_id)
    return "", 204
