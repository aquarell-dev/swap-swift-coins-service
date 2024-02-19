from ccxt.async_support import mexc
from ccxt.base.types import Strings


class Mexc(mexc):
    def __init__(self):
        super().__init__({
            'apiKey': 'mx0vglhfoE7NCLDfpd',
            'secret': 'fad624c14e8645a6b1310feb70c58cee',
        })

    async def fetch_deposit_withdraw_fees(self, codes: Strings = None, params=None):
        if params is None:
            params = {}

        fetched_networks = await super().fetch_deposit_withdraw_fees(codes, params)

        return {
            k: [
                {
                    'chain': chain['network'],
                    'fee': float(chain['withdrawFee']),
                    'percentage': 0,
                    'withdrawable': bool(chain['withdrawEnable']),
                    'depositable': bool(chain['depositEnable']),
                } for chain in v['info']['networkList']
            ]
            for k, v in fetched_networks.items()
        }
