from typing import Type, List

from ccxt.async_support import Exchange

from .htx import HTX
from .gate import Gate
from .mexc import Mexc
from .kucoin import Kucoin
from .bitget import Bitget

exchanges: List[Type[Exchange]] = [HTX, Gate, Kucoin, Bitget, Mexc]
