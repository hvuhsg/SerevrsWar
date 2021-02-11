from fastapi import FastAPI, Request, APIRouter, Depends
from fastapi.responses import RedirectResponse
from starlette.config import Config
from authlib.integrations.starlette_client import OAuth

from db import get_db

from endpoints.register import register

google_login_app = APIRouter()

config = Config(env_file="./google_login/.env")

oauth = OAuth(config)

CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email profile'
    }
)


@google_login_app.route('/login')
async def login(request: Request):
    redirect_uri = str(request.base_url) + "google_account/auth"
    return await oauth.google.authorize_redirect(request, redirect_uri)


@google_login_app.route('/auth')
async def auth(request: Request):
    db = get_db()
    token = await oauth.google.authorize_access_token(request)
    user = await oauth.google.parse_id_token(request, token)
    account = db["players"].find_one({"user.email": user["email"]})
    if not account:
        await register(user)
    if user.get("_id", None):
        user.pop("_id")
    request.session['user'] = dict(user)
    return RedirectResponse(url='/')


@google_login_app.route('/logout')
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url='/')
