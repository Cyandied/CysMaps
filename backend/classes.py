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

class MapSettings:
    def __init__(self, start_pos = None, start_zoom = None, title = None, bg_color = None, exsisting_dict = None) -> None:
        self.start_pos = start_pos if exsisting_dict == None else exsisting_dict["start_pos"]
        self.start_zoom = start_zoom if exsisting_dict == None else exsisting_dict["start_zoom"]
        self.title = title if exsisting_dict == None else exsisting_dict["title"]
        self.bg_color = bg_color if exsisting_dict == None else exsisting_dict["bg_color"]

class Marker:
    def __init__(self, name:str, desc:str, icon:str,attributes:dict,pos:list[float],id = None, exsisting_marker = None) -> None:
        self.name = name if exsisting_marker == None else exsisting_marker["name"]
        self.desc = desc if exsisting_marker == None else exsisting_marker["desc"]
        self.icon = icon if exsisting_marker == None else exsisting_marker["icon"]
        self.attributes = attributes if exsisting_marker == None else exsisting_marker["attributes"]
        self.pos = pos if exsisting_marker == None else exsisting_marker["pos"]
        self.id = "cy" + str(uuid.uuid4()) if id == None else id