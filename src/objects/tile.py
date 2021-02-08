from typing import Union
from datetime import datetime

from perlin_noise import PerlinNoise

from config import PERLIN_NOISE_OCTAVES, RANDOMIZE_SEED
from db import get_db

noise = PerlinNoise(octaves=PERLIN_NOISE_OCTAVES, seed=RANDOMIZE_SEED)


class Tile:
    def __init__(self, x: int, y: int, power: int, updated_at: Union[datetime, None] = None):
        self.x = x
        self.y = y
        self.power = power
        self.updated_at = updated_at

    @classmethod
    def from_dict(cls, tile_dict):
        return cls(**tile_dict)

    @classmethod
    def get(cls, x, y):
        db = get_db()
        tile_dict = db["map"].find_one({"x": x, "y": y})
        if not tile_dict:
            tile_dict = {"x": x, "y": y, "power": Tile.generate_tile_power(x, y)}
        return Tile.from_dict(tile_dict)

    @staticmethod
    def generate_tile_power(x, y):
        distance_from_center = (x ** 2 + y ** 2) ** 0.5
        return abs(round(noise([x / 1000, y / 1000]) * 50 + distance_from_center // 10))
