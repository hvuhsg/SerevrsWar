from fastapi import APIRouter, WebSocket, Depends, HTTPException, status, WebSocketDisconnect

from db import get_db
from websocket_manager import get_manager

router = APIRouter()


@router.websocket("/ws")
async def connection(token: str, client_id: str, ws: WebSocket, db=Depends(get_db), ws_manager=Depends(get_manager)):
    player = db["players"].find_one({"token": token})
    device_id = token + client_id
    if not player:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Token")
    await ws.accept()
    ws_manager.new(device_id, ws)
    while True:
        try:
            await ws.receive_text()
        except WebSocketDisconnect:
            print("remove", ws)
            ws_manager.remove(device_id)
            break
        except RuntimeError:
            ws_manager.remove(device_id)
            break
