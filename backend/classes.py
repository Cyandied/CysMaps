import uuid


class User:
    def __init__(
        self, name, email, role="user", games=[], id=None, packs=[], secret=False
    ) -> None:
        self.name = name
        self.email = email
        self.role = role
        self.games = games
        self.id = id or str(uuid.uuid4())
        self.secret = secret
        self.packs = packs or []

    def to_json(self):
        return {"name": self.name}

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)
