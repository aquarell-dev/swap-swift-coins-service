from typing import Optional, List

from ccxt.async_support import kucoin


class Kucoin(kucoin):
    async def fetch_deposit_withdraw_fees(self, codes: Optional[List[str]] = None, params=None):
        if params is None:
            params = {}

        fetched_networks = await super().fetch_deposit_withdraw_fees(codes, params)

        return {
            k: [
                {
                    'chain': chain['chainName'],
                    'fee': float(chain['withdrawalMinFee']),
                    'percentage': 0,
                    'withdrawable': bool(chain['isWithdrawEnabled']),
                    'depositable': bool(chain['isDepositEnabled']),
                } for chain in v['info']['chains']
            ]
            for k, v in fetched_networks.items()
        }
