from random import randint

from fastapi import status, HTTPException

from config import SPAWN_RANGE, INITIAL_POWER
from db import get_db
from websocket_manager import get_manager
from utils import time_now
from objects.tile import Tile
from objects.player import Player


# Internal endpoint
async def register(user: dict):
    print(user)
    db = get_db()
    ws_manager = get_manager()
    name = user["name"].split(" ")[0]

    spawn_range = SPAWN_RANGE  # By value
    if Player.name_exist(name):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Name already exist")
    token = Player.generate_token()

    while True:
        x, y = randint(-spawn_range, spawn_range), randint(-spawn_range, spawn_range)
        spawn_range += 2
        tile = Tile.get(x, y)  # db["map"].find_one({"x": x, "y": y})
        if not tile:
            results = db["map"].find({
                "$and": [
                    {"x": {"$lte": x + 1}},
                    {"x": {"$gte": x - 1}},
                    {"y": {"$lte": y + 1}},
                    {"y": {"$gte": y - 1}},
                ]
            })
            if list(results):
                continue
            break
    tile = Tile(x=x, y=y, power=INITIAL_POWER, owner=name, updated_at=time_now())
    tile.save()  # == db["map"].insert_one(tile)

    player = Player(name=name, token=token, spawn_point={"x": x, "y": y}, user=user)
    player.save()

    await ws_manager.push_update(x, y, tile.to_json_dict())

    return player.to_dict()
