import os
from abc import ABC, abstractmethod
from queue import Queue
from typing import Callable

import numpy as np

import definitions
from containers.candle import Candle
from externals.rolling_statistics.python.rolling_stats import RollingMean
from tools.downloader import load_from_disk


class TechnicalIndicator(ABC):
    @abstractmethod
    def __init__(self, lags: int):
        self._lags = lags
        self._candles = Queue(lags)
        self._compute_callback = Callable
        self._result = float

    @property
    def result(self):
        return self._result

    @abstractmethod
    def update(self, candle: Candle):
        raise NotImplementedError

    @abstractmethod
    def _compute(self):
        raise NotImplementedError


class MovingAverageTechnicalIndicator(TechnicalIndicator):
    def __init__(self, lags: int):
        super().__init__(lags)
        self._compute_callback = RollingMean(self._lags)
        self._result = self._compute_callback.mean

    @property
    def result(self):
        return self._compute_callback.mean

    def update(self, candle: Candle):
        self._compute_callback.insert_new_sample(candle.get_close_price())

    def _compute(self):
        raise NotImplementedError


def _normalized_autocorrelation(arr: np.ndarray) -> np.ndarray:
    autocorr = np.correlate(arr, arr, 'full')
    autocorr = autocorr / autocorr[len(arr) - 1]  # normalize by value at lag 0
    return autocorr[(len(arr) - 1):]  # return positive lags


def _area_of_normalized_autocorrelation(arr: np.ndarray) -> float:
    return np.sum(_normalized_autocorrelation(arr))


class AutoCorrelationTechnicalIndicator(TechnicalIndicator):
    def __init__(self, lags: int):
        super().__init__(lags)
        self._compute_callback = _area_of_normalized_autocorrelation
        self._result = None

    @property
    def result(self):
        return self._result

    def update(self, candle: Candle):
        self._candles.put(candle.get_close_price(), block=False)
        if self._candles.full():
            self._compute()
            self._candles.get(block=False)

    def _compute(self):
        self._result = self._compute_callback(np.array(list(self._candles.queue)))


if __name__ == "__main__":
    stock_data = load_from_disk(
        os.path.join(definitions.DATA_DIR, "local_data_15_Jan,_2018_01_Mar,_2018_XRPBTC.dill"))
    acorr = AutoCorrelationTechnicalIndicator(10)
    maverage = MovingAverageTechnicalIndicator(10)
    for candle in stock_data.candles:
        acorr.update(candle)
        maverage.update(candle)
        print(maverage.result)
        print(acorr.result)
