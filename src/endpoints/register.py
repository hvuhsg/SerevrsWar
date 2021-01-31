from datetime import datetime
from random import randint
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status

import config
from db import get_db
from websocket_manager import get_manager


router = APIRouter()


@router.post("/register")
async def register(name: str, db=Depends(get_db), ws_manager=Depends(get_manager)):
    spawn_range = config.SPAWN_RANGE
    if db["players"].find_one({"name": name}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Name already exist")
    token = str(uuid4())

    while True:
        x, y = randint(-spawn_range, spawn_range), randint(-spawn_range, spawn_range)
        spawn_range += 2
        tile = db["map"].find_one({"x": x, "y": y})
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
    tile = {"x": x, "y": y, "power": 50, "owner": name, "updated_at": datetime.now()}
    db["map"].insert_one(tile)
    player = {"name": name, "token": token, "spawn_point": {"x": x, "y": y}}
    db["players"].insert_one(player)
    player.pop("_id")

    tile.pop("_id", None)
    tile.pop("updated_at", None)
    await ws_manager.push_update(x, y, tile)

    return player
