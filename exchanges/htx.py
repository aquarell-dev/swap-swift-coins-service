from typing import Optional, List

from ccxt.async_support import huobi


class HTX(huobi):
    def __init__(self):
        super().__init__()

    async def fetch_deposit_withdraw_fees(self, codes: Optional[List[str]] = None, params=None):
        if params is None:
            params = {}

        fetched_networks = await super().fetch_deposit_withdraw_fees(codes, params)

        return {
            k: [
                {
                    'chain': chain['displayName'],
                    'withdrawable': chain['withdrawStatus'] == 'allowed',
                    'depositable': chain['depositStatus'] == 'allowed',
                    'fee': float(
                        chain.get('transactFeeWithdraw') or 0
                        if chain['withdrawFeeType'] == 'fixed'
                        else chain.get('minTransactFeeWithdraw') or 0
                    ),
                    'percentage': float(
                        chain.get('transactFeeRateWithdraw') or 0
                        if chain['withdrawFeeType'] == 'ratio'
                        else 0
                    )
                } for chain in v['info']['chains']
            ]
            for k, v in fetched_networks.items()
        }
