from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime

from db import get_db
from config import TIME_PER_MOVE, START_MOVE_TIME

router = APIRouter()


@router.get("/me")
def me(token: str, db=Depends(get_db)):
    player = db["players"].find_one({"token": token}, {"token": 0})
    if not player:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Token")

    tiles = list(db["map"].find({"owner": player["name"]}, {"_id": 0, "updated_at": 0}))

    player.pop("_id")
    game_started = datetime.now() > START_MOVE_TIME
    return {
        "tiles": tiles,
        "player": player,
        "game": {
            "started": game_started,
            "time_per_move": TIME_PER_MOVE.total_seconds()
        }
    }
