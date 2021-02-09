from fastapi import APIRouter, Depends, HTTPException, status
from collections import defaultdict

from config import GAME_START_TIME, TIME_PER_MOVE, MOVES_PER_TURN
from db import get_db
from objects.tile import Tile
from objects.player import Player
from websocket_manager import get_manager
from utils import time_now

router = APIRouter()

players_that_play_this_turn = defaultdict(lambda: {"moves": MOVES_PER_TURN}.copy())
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
    player = Player.get(token)
    if not player:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Token")

    # TURN VALIDATION
    turn_validations(token, played_players)

    # TILES VALIDATION
    src = Tile.get(src_x, src_y)  # get the tile from the db
    dst = Tile.get(dst_x, dst_y)
    if dst is None:
        dst = Tile.generate_tile(dst_x, dst_y)

    if power is None:
        power = src.power
    tiles_related_validation(power, src, dst, player)

    move_the_power(src, dst, power)
    played_players[token]["moves"] -= 1

    await ws_manager.push_update(src_x, src_y, src.to_json_dict())
    await ws_manager.push_update(dst_x, dst_y, dst.to_json_dict())

    return {"src": src.to_json_dict(), "dst": dst.to_json_dict()}


def turn_validations(token, played_players):
    global turn
    now = time_now()
    game_started = now < GAME_START_TIME
    time_until_game_starting = (GAME_START_TIME - now).total_seconds()
    current_turn = (now - GAME_START_TIME).total_seconds() // TIME_PER_MOVE.total_seconds()
    time_until_next_turn = TIME_PER_MOVE.total_seconds() \
                           - (now - GAME_START_TIME).total_seconds() \
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

    if played_players[token]["moves"] <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You already play this turn, wait {time_until_playable_turn} seconds until next turn",
            headers={"X-TIME": str(time_until_playable_turn)}
        )
    return turn


def tiles_related_validation(power, src, dst, player):
    if src is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Source tile is not your's")

    if power <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Power mast be grater then zero")

    if src.distance(dst) != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The src tile and the dst tile are not neighbors"
        )

    if src.owner != player.name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The source tile is not your's")

    if power > src.power:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The source tile has not enough power")

    if src.power == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The source tile has no power")


def move_the_power(src, dst, power):
    if src.owner == dst.owner:
        src.transfer_power(dst, power)
    else:
        src.attack(dst, power)
