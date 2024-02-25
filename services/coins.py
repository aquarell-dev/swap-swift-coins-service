import asyncio
import re
from collections import Counter
from dataclasses import asdict
from typing import Awaitable, Callable, Dict, List, Optional, Type

import ccxt
from ccxt.async_support import Exchange

from logger import logger
from typings import Coin, Network


class CoinsService:
    def __init__(self, *exchanges: Type[Exchange]) -> None:
        self._exchanges = [exchange() for exchange in exchanges]
        self._exchange_mapping = {exchange.name: exchange for exchange in self._exchanges}
        self._coin_mapping: dict[str, dict[str, Coin]] = {}
        self._loading = False

    def get_loading(self) -> bool:
        return self._loading

    def get_coins(self) -> dict[str, dict[str, dict]]:
        self._coin_mapping
        return {
            exchange_name: {
                coin_name: {
                    'coin': coin_name,
                    'percentage': coin.percentage,
                    'volume': coin.volume,
                    'exchange': exchange_name,
                    'networks': [asdict(network) for network in (coin.networks or [])]
                } for coin_name, coin in coins.items()
            }
            for exchange_name, coins in self._coin_mapping.items()
        }

    async def update_coins(self) -> None:
        self._loading = True

        tasks = [self._get_spot_coins(exchange) for exchange in self._exchanges]

        spot_coins = await asyncio.gather(*tasks)
        extended_coins = [coin for coins in spot_coins for coin in coins]

        sorted_coins = sorted(extended_coins, key=lambda a: a.coin)

        common_coins = self._filter_elements(sorted_coins)

        coin_mapping: Dict[str, Dict[str, Coin]] = {}

        for coin in common_coins:
            if coin.exchange.name not in coin_mapping:
                coin_mapping[coin.exchange.name] = {}
            coin_mapping[coin.exchange.name][coin.coin] = coin

        tasks = [
            self._fetch_networks(exchange_name, coins)
            for exchange_name, coins in coin_mapping.items()
        ]
        await asyncio.gather(*tasks)

        await asyncio.gather(*[exchange.close() for exchange in self._exchanges])

        self._coin_mapping = coin_mapping
        self._loading = False

    async def _fetch_networks(self, exchange_name: str, coins: Dict[str, Coin]):
        exchange = self._exchange_mapping[exchange_name]
        networks = await _async_retry(
            lambda: exchange.fetch_deposit_withdraw_fees(list(coins.keys()))
        )

        for coin, networks in networks.items():
            try:
                coins.get(coin).networks = [
                    Network(**network) for network in networks
                    if network.get('percentage') == 0
                ]
            except (ValueError, KeyError, AttributeError):
                continue

        logger.info(f"Fetched networks for {exchange_name}")

    def _filter_elements(self, input_list):
        """
        Essentially just returns those elements that are presented at least 2 times in a given list

        :param input_list:
        :return: a new list
        """
        coin_counts = Counter(coin.coin for coin in input_list)

        filtered_coins = [coin for coin in input_list if coin_counts[coin.coin] >= 2]

        return filtered_coins

    def _check_coin_name(self, coin_name):
        """
        Returns True if the given coin base contains symbols such as 3l, 3s,
        so basically any combination of numbers and letters.
        Returns False otherwise.
        Used to filter services.

        :param coin_name:
        :return: true or false
        """
        pattern = re.compile(r'\d+[ls]', re.IGNORECASE)
        return not bool(pattern.search(coin_name))

    async def _get_spot_coins(self, exchange: Exchange) -> List[Coin]:
        """
        Returns a list of all spot services for a given exchange

        :param exchange:
        :return: List of all spot services
        """
        tickers = await _async_retry(lambda: exchange.fetch_tickers())

        coins = [self._get_coin_from_ticker(ticker, ticker_data, exchange) for ticker, ticker_data
                 in tickers.items()]

        logger.info(f"Fetched {len(coins)} coins for {exchange.name}")

        return [coin for coin in coins if coin is not None]

    def _get_coin_from_ticker(self, ticker: str, ticker_data: dict, exchange: Exchange) -> Optional[
        Coin]:
        if '/' not in ticker:
            return

        coin, base = ticker.split('/')

        if base != 'USDT' or not self._check_coin_name(coin):
            return

        percentage = ticker_data.get('percentage', None)
        volume = ticker_data.get('quoteVolume', None)

        return Coin(coin=coin, exchange=exchange, percentage=percentage, volume=volume)


async def _async_retry(
    func: Callable[..., Awaitable],
    retries: int = 7,
    delay: float = 3.0,
    backoff: float = 4.0,
):
    for attempt in range(retries + 1):
        try:
            return await func()
        except ccxt.BaseError as e:
            if attempt < retries:
                await asyncio.sleep(delay * (backoff ** attempt))
            else:
                raise e
