import logging

from app.domain.member import Member
from app.domain.validation import validate_member
from app.errors import Conflict, NotFound

log = logging.getLogger("library.services.member")


class MemberService:
    def __init__(self, member_repo, loan_repo):
        self.members = member_repo
        self.loans = loan_repo

    def create_member(self, data):
        clean = validate_member(data)
        if self.members.find_by_email(clean["email"]):
            raise Conflict(f"A member with email {clean['email']} already exists")
        member = self.members.add(Member(**clean))
        log.info("member created id=%s", member.id)
        return member

    def get_member(self, member_id):
        member = self.members.get(member_id)
        if member is None:
            raise NotFound(f"Member {member_id} not found")
        return member

    def list_members(self):
        return self.members.list()

    def update_member(self, member_id, data):
        clean = validate_member(data)
        member = self.get_member(member_id)
        other = self.members.find_by_email(clean["email"])
        if other is not None and other.id != member_id:
            raise Conflict(f"A member with email {clean['email']} already exists")
        member.name, member.email = clean["name"], clean["email"]
        self.members.save(member)
        log.info("member updated id=%s", member_id)
        return member

    def delete_member(self, member_id):
        self.get_member(member_id)
        if self.loans.active_for_member(member_id):
            raise Conflict("Cannot delete a member who has active loans")
        self.members.delete(member_id)
        log.info("member deleted id=%s", member_id)
