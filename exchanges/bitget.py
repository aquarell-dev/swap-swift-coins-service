from ccxt.async_support import bitget
from ccxt.base.types import Strings


class Bitget(bitget):
    async def fetch_deposit_withdraw_fees(self, codes: Strings = None, params=None):
        if params is None:
            params = {}

        fetched_networks = await super().fetch_deposit_withdraw_fees(codes, params)

        return {
            k: [
                {
                    'chain': chain.get('chain', None),
                    'fee': float(chain.get('withdrawFee', None)),
                    'percentage': float(chain.get('extraWithdrawFee', None)),
                    'withdrawable': True if chain.get('withdrawable', '') == 'true' else False,
                    'depositable': True if chain.get('rechargeable', '') == 'true' else False,
                } for chain in v.get('info', {}).get('chains', [])
            ]
            for k, v in fetched_networks.items()
        }
