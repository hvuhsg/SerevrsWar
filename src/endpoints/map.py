from fastapi import APIRouter, Depends, HTTPException, status

from db import get_db
from websocket_manager import get_manager
from config import MAX_CHUNK_SIZE
from objects.tile import Tile
from objects.player import Player
from utils import coordinates_to_chunk

router = APIRouter()


@router.get("/map")
async def get_map(
        token: str,
        client_id: str,
        x: int = 0,
        y: int = 0,
        chunk_size: int = MAX_CHUNK_SIZE,
        db=Depends(get_db),
        ws_manager=Depends(get_manager)
):
    player = Player.get(token)
    if not player:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Token")
    device_id = token + client_id
    range_view = min(MAX_CHUNK_SIZE, chunk_size)

    x, y = coordinates_to_chunk(x, y, chunk_size)

    max_x = int(x + range_view//2)
    min_x = int(x - range_view//2)
    max_y = int(y + range_view//2)
    min_y = int(y - range_view//2)

    results = db["map"].find(
        {
            "$and": [
                {"x": {"$lte": max_x}},
                {"x": {"$gte": min_x}},
                {"y": {"$lte": max_y}},
                {"y": {"$gte": min_y}},
            ]
        }
    )
    dict_results = {}
    for tile_dict in results:
        tile = Tile.from_dict(tile_dict)
        dict_results[f"{tile.x},{tile.y}"] = tile.to_json_dict()

    for xc in range(min_x, max_x+1):
        for yc in range(min_y, max_y+1):
            if not dict_results.get(f"{xc},{yc}", None):
                dict_results[f"{xc},{yc}"] = Tile.generate_tile(xc, yc).to_json_dict()

    ws_manager.add_load_range(device_id, {"x": x, "y": y, "chunk_size": chunk_size})

    return dict_results
