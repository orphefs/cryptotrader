from typing import List

from containers.candle import Candle
from type_aliases import Security


class StockData(object):
    def __init__(self, candles: List[Candle], security: Security):
        self._candles = candles
        self._security = security

    @property
    def candles(self):
        return self._candles

    @property
    def security(self):
        return self._security

    def __len__(self):
        return len(self._candles)
