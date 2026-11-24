from dataclasses import asdict, dataclass


@dataclass
class Member:
    name: str
    email: str
    id: int = None

    def to_dict(self):
        return asdict(self)
