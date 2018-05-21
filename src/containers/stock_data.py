from typing import List

from src.containers.candle import Candle
from src.type_aliases import Security


class StockData(object):
    def __init__(self, candles: List[Candle], security: Security):
        self._candles = candles
        self._security = security

    @property
    def candles(self):
        return self._candles

    def append_new_candle(self, candle: Candle):
        self._candles.append(candle)

    @property
    def security(self):
        return self._security

    def __len__(self):
        return len(self._candles)
