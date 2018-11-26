from typing import List

import dill

from src.containers.candle import Candle
from src.containers.trading_pair import TradingPair


class StockData(object):
    def __init__(self, candles: List[Candle], trading_pair: TradingPair):
        self._candles = candles
        self._trading_pair = trading_pair

    @property
    def candles(self):
        return self._candles

    def append_new_candle(self, candle: Candle):
        self._candles.append(candle)

    @property
    def trading_pair(self):
        return self._trading_pair

    def __len__(self):
        return len(self._candles)


def save_to_disk(data: StockData, path_to_file: str):
    with open(path_to_file, 'wb') as outfile:
        dill.dump(data, outfile)


def load_from_disk(path_to_file: str) -> StockData:
    with open(path_to_file, 'rb') as outfile:
        data = dill.load(outfile)
    return data