from fastapi import APIRouter, Depends, HTTPException, status

from db import get_db
from config import TIME_PER_MOVE, GAME_START_TIME, MOVES_PER_TURN, NEW_POWER_RATE
from utils import time_now
from objects.player import Player

router = APIRouter()


@router.get("/me")
def me(token: str, db=Depends(get_db)):
    player = Player.get(token)
    if not player:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Token")

    tiles = list(db["map"].find({"owner": player.name}, {"_id": 0, "updated_at": 0}))

    player_dict = player.to_dict()
    player_dict.pop("token", None)

    game_started = time_now() > GAME_START_TIME
    return {
        "tiles": tiles,
        "player": player_dict,
        "game": {
            "started": game_started,
            "time_per_move": TIME_PER_MOVE.total_seconds(),
            "moves_per_turn": MOVES_PER_TURN,
            "power_growth_rate": NEW_POWER_RATE.total_seconds(),
        }
    }
