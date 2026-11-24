from flask import Blueprint, jsonify, url_for

from app.routes.helpers import created, json_body, service

bp = Blueprint("members", __name__, url_prefix="/members")


@bp.post("")
def create_member():
    member = service("member_service").create_member(json_body())
    return created(member.to_dict(), url_for("members.get_member", member_id=member.id))


@bp.get("")
def list_members():
    return jsonify([m.to_dict() for m in service("member_service").list_members()])


@bp.get("/<int:member_id>")
def get_member(member_id):
    return jsonify(service("member_service").get_member(member_id).to_dict())


@bp.put("/<int:member_id>")
def update_member(member_id):
    member = service("member_service").update_member(member_id, json_body())
    return jsonify(member.to_dict())


@bp.delete("/<int:member_id>")
def delete_member(member_id):
    service("member_service").delete_member(member_id)
    return "", 204
