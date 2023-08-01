import uuid


class User:
    def __init__(
        self, name, email, role="user", games=[], id=None, packs=[], secret=False, allowed_maps=False, nr_maps=0, max_maps=0
    ) -> None:
        self.name = name
        self.email = email
        self.role = role
        self.games = games
        self.id = id or str(uuid.uuid4())
        self.secret = secret
        self.packs = packs or []
        self.allowed_maps = allowed_maps
        self.nr_maps = nr_maps
        self.max_maps = max_maps

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
