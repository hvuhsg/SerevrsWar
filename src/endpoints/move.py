from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status

from utils import random_tile, updated_tile_power
from config import NEW_POWER_RATE, START_MOVE_TIME, TIME_PER_MOVE
from db import get_db
from websocket_manager import get_manager


router = APIRouter()


players_that_play_this_turn = set()
turn = 0


@router.post("/move")
async def move(
        token: str,
        src_x: int,
        src_y: int,
        dst_x: int,
        dst_y: int,
        power: int = None,
        db=Depends(get_db),
        ws_manager=Depends(get_manager),
        played_players=Depends(lambda: players_that_play_this_turn)
):
    player = db["players"].find_one({"token": token})
    if not player:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Token")

    # TURN RELATED VALIDATION STUFF
    turn_validations(token, played_players)
    # TURN RELATED VALIDATION STUFF

    # TILES VALIDATION STUFF
    src = db["map"].find_one({"x": src_x, "y": src_y})
    dst = db["map"].find_one({"x": dst_x, "y": dst_y})

    src["power"] = updated_tile_power(src, NEW_POWER_RATE)
    if not power:
        power = src["power"]

    tiles_related_validation(power, src, dst, src_x, src_y, dst_x, dst_y, player)
    # TILES VALIDATION STUFF

    src, dst = update_tiles(src, dst, dst_x, dst_y, power, player, db)
    played_players.add(token)

    src.pop("_id", None)
    dst.pop("_id", None)
    src.pop("updated_at", None)
    dst.pop("updated_at", None)

    await ws_manager.push_update(src_x, src_y, src)
    await ws_manager.push_update(dst_x, dst_y, dst)

    return {"src": src, "dst": dst}


def turn_validations(token, played_players):
    global turn
    game_started = datetime.now() < START_MOVE_TIME
    time_until_game_starting = (START_MOVE_TIME - datetime.now()).total_seconds()
    current_turn = (datetime.now() - START_MOVE_TIME).total_seconds() // TIME_PER_MOVE.total_seconds()
    time_until_next_turn = TIME_PER_MOVE.total_seconds() \
                           - (datetime.now() - START_MOVE_TIME).total_seconds() \
                           % TIME_PER_MOVE.total_seconds()
    time_until_playable_turn = time_until_next_turn + TIME_PER_MOVE.total_seconds()

    if game_started:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Game have not started yet, will start in {time_until_game_starting} seconds",
            headers={"X-TIME": str(time_until_game_starting)}
        )

    if current_turn % 2 != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You can't make move now please wait {time_until_next_turn} seconds",
            headers={"X-TIME": str(time_until_next_turn)},
        )
    elif current_turn != turn:
        played_players.clear()
        turn = current_turn

    if token in played_players:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You already play this turn, wait {time_until_playable_turn} seconds until next turn",
            headers={"X-TIME": str(time_until_playable_turn)}
        )
    return turn


def tiles_related_validation(power, src, dst, src_x, src_y, dst_x, dst_y, player):
    if power is not None and power < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Power mast be grater then zero")

    if ((src_x - dst_x) ** 2 + (src_y - dst_y) ** 2) ** 0.5 != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The src tile and the dst tile are not neighbors"
        )

    if not src or src["owner"] != player["name"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The source tile is not your's")

    if power > src["power"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The source tile has not enough power")

    if src["power"] == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The source tile has no power")


def update_tiles(src, dst, dst_x, dst_y, power, player, db):
    game_tile = False  # The tile has owner
    if dst and dst["owner"] != player["name"]:
        dst["power"] = dst["power"] - power
    elif dst and dst["owner"] == player["name"]:
        dst["power"] = dst["power"] + power
    else:
        game_tile = True  # It is no one tile (not registered in the db)
        dst = {"x": dst_x, "y": dst_y, "power": random_tile(dst_x, dst_y) - power, "owner": None}

    dst["power"] = updated_tile_power(dst, NEW_POWER_RATE)

    if dst["power"] < 0:
        dst["power"] *= -1
        dst["owner"] = player["name"]

    src["power"] = src["power"] - power

    db["map"].update_one({"_id": src["_id"]}, {"$set": {"power": src["power"], "updated_at": datetime.now()}})
    if not game_tile:
        db["map"].update_one(
            {"_id": dst["_id"]},
            {"$set": {"power": dst["power"], "owner": dst["owner"], "updated_at": datetime.now()}}
        )
    else:
        db["map"].insert_one(
            {
                "x": dst_x,
                "y": dst_y,
                "power": dst["power"],
                "owner": dst.get("owner", None),
                "updated_at": datetime.now()
            }
        )

    return src, dst