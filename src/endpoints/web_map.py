from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse

from db import get_db


router = APIRouter()


@router.get("/guiMap")
def gui_map(token: str, db=Depends(get_db)):
    player = db["players"].find_one({"token": token})
    if not player:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Token")

    tiles = list(db["map"].find({"owner": player["name"]}))
    sum_x = sum(tile["x"] for tile in tiles)
    sum_y = sum(tile["y"] for tile in tiles)
    x = sum_x // len(tiles)
    y = sum_y // len(tiles)

    return RedirectResponse(url=f"/gui/index.html?x={x}&y={y}&token={token}")

