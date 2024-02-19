from dataclasses import dataclass


@dataclass
class Network:
    chain: str
    fee: float
    percentage: float
    withdrawable: bool
    depositable: bool

    @property
    def caption(self):
        return f'{self.chain}({self.fee} + {self.percentage * 100}%)'
