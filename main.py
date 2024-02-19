import asyncio

from fastapi import FastAPI

from events import startup
from exchanges import exchanges
from services import CoinsService
from settings import get_config

config = get_config()

app = FastAPI(
    title=config.APP_NAME,
    version=config.API_VERSION,
    root_path=config.API_PREFIX
)

service = CoinsService(*exchanges)


@app.on_event("startup")
async def on_startup():
    asyncio.create_task(startup(service))


@app.get('/coins', tags=['coins'])
async def get_coins():
    if service.get_loading():
        return {"status": "loading", "data": {}}

    return {"status": "loaded", "data": service.get_coins()}
