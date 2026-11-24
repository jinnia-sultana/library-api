from flask import Blueprint, jsonify, url_for

from app.routes.helpers import created, json_body, service

bp = Blueprint("loans", __name__, url_prefix="/loans")


@bp.post("")
def borrow_book():
    loan = service("loan_service").borrow_book(json_body())
    return created(loan.to_dict(), url_for("loans.get_loan", loan_id=loan.id))


@bp.get("")
def list_loans():
    return jsonify([l.to_dict() for l in service("loan_service").list_loans()])


@bp.get("/<int:loan_id>")
def get_loan(loan_id):
    return jsonify(service("loan_service").get_loan(loan_id).to_dict())


@bp.post("/<int:loan_id>/return")
def return_book(loan_id):
    return jsonify(service("loan_service").return_book(loan_id).to_dict())
