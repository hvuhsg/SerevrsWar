from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from db import setup_db, shutdown_db, get_db

from endpoints import map
from endpoints import move
from endpoints import me
from endpoints import websocket
from endpoints import web_map
from provider.main import provider_login_app


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key="SJDI(ERGSDcC52")

app.include_router(map.router)
app.include_router(move.router)
app.include_router(me.router)
app.include_router(websocket.router)
app.include_router(web_map.router)
app.include_router(provider_login_app, prefix="/provider")

app.mount("/gui", StaticFiles(directory="www"), name="gui")
app.mount("/register_site", StaticFiles(directory="register_www"), name="register_www")
templates = Jinja2Templates(directory="register_www")


@app.get("/")
def main_registration_page(request: Request):
    db = get_db()
    user = request.session.get("user", None)
    token = None
    connected = False
    if user and user.get("email", None):
        connected = True
        token = db["players"].find_one({"user.email": user["email"]}, {"token": 1})["token"]
    return templates.TemplateResponse("index.html", {"request": request, "connected": connected, "token": token})


@app.on_event("startup")
def startup():
    setup_db()


@app.on_event("shutdown")
def shutdown():
    shutdown_db()
