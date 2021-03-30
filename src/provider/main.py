from fastapi import Request, APIRouter, Depends
from fastapi.responses import RedirectResponse
from starlette.config import Config
from authlib.integrations.starlette_client import OAuth

from db import get_db

from endpoints.register import register

provider_login_app = APIRouter()

config = Config(env_file="./provider/.env")

oauth = OAuth(config)

oauth.register(
    name='provider',
    api_base_url='https://auth.qwhale.ml/',
    access_token_url='https://auth.qwhale.ml/token',
    authorize_url='https://auth.qwhale.ml/login',
    access_token_params={
        "client_id": config.get("PROVIDER_CLIENT_ID"),
        "client_secret": config.get("PROVIDER_CLIENT_SECRET")
    }
)


@provider_login_app.get('/login')
async def login(request: Request):
    redirect_uri = request.url_for("auth").replace("http://", "https://")
    return await oauth.provider.authorize_redirect(request, redirect_uri)


@provider_login_app.get('/auth')
async def auth(request: Request):
    db = get_db()
    token = await oauth.provider.authorize_access_token(request)
    user = await oauth.provider.get(url="/me", token=token)
    user = user.json()

    account = db["players"].find_one({"user.identity_id": user["identity_id"]})
    if not account:
        await register(user)
    if user.get("_id", None):
        user.pop("_id")

    session_data = {"identity_id": user["identity_id"]}

    request.session["user"] = session_data
    return RedirectResponse(url="/")


@provider_login_app.get('/logout')
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url='/')
