from dataclasses import dataclass
from typing import List, Optional

from ccxt import Exchange

from typings.network import Network


@dataclass
class Coin:
    coin: str
    exchange: Exchange
    percentage: Optional[float] = None
    volume: Optional[float] = None
    networks: List[Network] = None
