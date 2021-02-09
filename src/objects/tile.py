from typing import Union
from datetime import datetime, timezone

from fastapi.encoders import jsonable_encoder
from perlin_noise import PerlinNoise

from config import PERLIN_NOISE_OCTAVES, RANDOMIZE_SEED, NEW_POWER_RATE
from db import get_db
from utils import time_now

noise = PerlinNoise(octaves=PERLIN_NOISE_OCTAVES, seed=RANDOMIZE_SEED)


class Tile:
    def __init__(
            self,
            x: int,
            y: int,
            power: int,
            owner: Union[str, None] = None,
            updated_at: Union[datetime, None] = None,
            _id=None
    ):
        if updated_at:
            updated_at = updated_at.replace(tzinfo=timezone.utc)
        self.x = x
        self.y = y
        self._power = power
        self.owner = owner
        self.updated_at = updated_at

    @property
    def power(self):
        power_per_time = 0
        if self.owner:
            now = time_now()
            power_per_time = (now - self.updated_at) // NEW_POWER_RATE
            power_per_time = min(0, power_per_time)  # Redundant (But just in case)
        return self._power + power_per_time

    def save(self):
        # TODO: save the _id for performers search
        db = get_db()
        return db["map"].insert_one(self.to_dict())

    def update(self):
        db = get_db()
        tile_dict = self.to_dict()
        tile_dict.pop("x")
        tile_dict.pop("y")
        return db["map"].update_one(
            {"x": self.x, "y": self.y},
            {"$set": tile_dict}
        )

    def to_json_dict(self):
        """
        Json compilable dict
        """
        tile_dict = self.to_dict()
        if tile_dict.get("updated_at", None):
            tile_dict["updated_at"] = tile_dict["updated_at"].isoformat()
        return jsonable_encoder(tile_dict)

    def to_dict(self):
        return {"x": self.x, "y": self.y, "power": self._power, "owner": self.owner, "updated_at": self.updated_at}

    def distance(self, other_tile):
        return ((self.x - other_tile.x)**2 + (self.y - other_tile.y)**2)**0.5

    def transfer_power(self, other_tile, power):
        self._power -= power
        other_tile._power += power
        self.update()
        other_tile.update()

    def attack(self, other_tile, power):
        other_tile_in_db = Tile.get(other_tile.x, other_tile.y) is not None

        #  Update power
        self._power -= power
        other_tile._power = power - other_tile.power

        if other_tile.power <= 0:  # If you lose
            other_tile._power = other_tile.power * -1
        else:  # If you won
            other_tile.owner = self.owner
            other_tile.updated_at = time_now()
        self.update()
        if other_tile_in_db:
            other_tile.update()
        else:
            other_tile.save()

    @classmethod
    def from_dict(cls, tile_dict):
        return cls(**tile_dict)

    @classmethod
    def get(cls, x, y):
        db = get_db()
        tile_dict = db["map"].find_one({"x": x, "y": y})
        if tile_dict is None:
            return
        return cls.from_dict(tile_dict)

    @classmethod
    def generate_tile(cls, x, y):
        tile_dict = {"x": x, "y": y, "power": Tile.generate_tile_power(x, y)}
        return cls.from_dict(tile_dict)

    @staticmethod
    def has_owner(x, y):
        db = get_db()
        tile_dict = db["map"].find_one({"x": x, "y": y})
        return tile_dict is not None

    @staticmethod
    def generate_tile_power(x, y):
        distance_from_center = (x ** 2 + y ** 2) ** 0.5
        return abs(round(noise([x / 1000, y / 1000]) * 50 + distance_from_center // 10))
