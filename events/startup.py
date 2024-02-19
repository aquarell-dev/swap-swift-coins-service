import asyncio

from services import CoinsService
from settings import get_config

config = get_config()


async def startup(coins_service: CoinsService):
    while True:
        await coins_service.update_coins()
        await asyncio.sleep(int(config.INTERVAL_MINUTES) * 60)
