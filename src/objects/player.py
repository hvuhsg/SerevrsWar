from uuid import uuid4

from config import TOKEN_GENERATION_RETRY
from db import get_db


class Player:
    def __init__(self, name, token, spawn_point, user=None):
        self.token = token
        self.name = name
        self.spawn_point = spawn_point
        self.user = user

    def save(self):
        db = get_db()
        db["players"].insert_one(self.to_dict())

    def to_dict(self):
        return {"name": self.name, "token": self.token, "spawn_point": self.spawn_point, "user": self.user}

    @staticmethod
    def name_exist(name):
        db = get_db()
        return db["players"].find_one({"name": name}) is not None

    @staticmethod
    def generate_token():
        db = get_db()
        for try_ in range(TOKEN_GENERATION_RETRY):
            token = str(uuid4())
            if not db["players"].find_one({"token": token}):
                return token
        raise ValueError(f"The token was already exist {TOKEN_GENERATION_RETRY} times (Check for errors)")

    @classmethod
    def from_dict(cls, player_dict):
        player_dict.pop("_id", None)
        return cls(**player_dict)

    @classmethod
    def get(cls, token):
        db = get_db()
        player_dict = db["players"].find_one({"token": token})
        if not player_dict:
            return
        return cls.from_dict(player_dict)
