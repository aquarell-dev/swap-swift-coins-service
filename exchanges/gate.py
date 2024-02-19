from typing import Optional, List

from ccxt.async_support import gate


class Gate(gate):
    def __init__(self):
        super().__init__({
            'apiKey': 'caf0adde67cf643ab18002a1a5d90a92',
            'secret': '2eba4e101152767fb26dac66980ade362bcbb327f4cc185ba1abbd92038c6f57',
        })

    async def fetch_deposit_withdraw_fees(self, codes: Optional[List[str]] = None, params=None):
        if params is None:
            params = {}

        fetched_networks = await super().fetch_deposit_withdraw_fees(codes, params)

        return {
            k: self._get_networks(v.get('info'))
            for k, v in fetched_networks.items()
        }

    def _get_networks(self, coin_info):
        withdraw_fix_on_chains = coin_info.get('withdraw_fix_on_chains')
        withdraw_percent_on_chains = coin_info.get('withdraw_percent_on_chains')

        if withdraw_fix_on_chains is None or withdraw_percent_on_chains is None:
            return []

        nets = withdraw_fix_on_chains.keys()

        return [
            {
                'chain': chain,
                'fee': float(withdraw_fix_on_chains.get(chain)),
                'percentage': float(withdraw_percent_on_chains.get(chain).replace('%', '')) / 100,
                'withdrawable': True,
                'depositable': True,
            } for chain in nets
        ]
