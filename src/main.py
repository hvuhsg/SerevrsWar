from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db import setup_db, shutdown_db

from endpoints import map
from endpoints import move
from endpoints import register
from endpoints import me
from endpoints import websocket


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(map.router)
app.include_router(move.router)
app.include_router(register.router)
app.include_router(me.router)
app.include_router(websocket.router)


@app.on_event("startup")
def startup():
    setup_db()


@app.on_event("shutdown")
def shutdown():
    shutdown_db()
