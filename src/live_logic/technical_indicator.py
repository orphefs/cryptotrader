import operator
import os
from abc import ABC, abstractmethod
from queue import Queue
from typing import Callable

import numpy as np

from src.externals.rolling_statistics.python.rolling_stats import RollingMean

from src import definitions
from src.containers.candle import Candle
from src.tools.downloader import load_from_disk


class OperatorOverloadsMixin:
    def __sub__(self, other):
        return CompoundTechnicalIndicator(self, other, operator.sub)

    def __mul__(self, other):
        return CompoundTechnicalIndicator(self, other, operator.mul)

    def __truediv__(self, other):
        return CompoundTechnicalIndicator(self, other, operator.truediv)


class TechnicalIndicator(ABC, OperatorOverloadsMixin):
    @abstractmethod
    def __init__(self, feature_getter_callback: Callable, lags: int):
        self._lags = lags
        self._candles = Queue(lags)
        self._compute_callback = Callable
        self._feature_getter_callback = feature_getter_callback
        self._result = float

    @property
    def lags(self):
        return self._lags

    @property
    def result(self):
        return self._result

    @abstractmethod
    def update(self, candle: Candle):
        raise NotImplementedError

    @abstractmethod
    def _compute(self):
        raise NotImplementedError

    def __str__(self):
        return "{}_{}_{}".format(type(self).__name__,
                                 self._feature_getter_callback.__name__,
                                 self._lags)


class CompoundTechnicalIndicator(OperatorOverloadsMixin):
    def __init__(self, technical_indicator_1,
                 technical_indicator_2,
                 operator_callback: Callable):
        self._result = float
        self._technical_indicator_1 = technical_indicator_1
        self._technical_indicator_2 = technical_indicator_2
        self._operator_callback = operator_callback
        self._lags = max([self._technical_indicator_1.lags,
                          self._technical_indicator_2.lags])

    @property
    def lags(self):
        return self._lags

    @property
    def result(self):
        return self._result

    @abstractmethod
    def update(self, candle: Candle):
        self._technical_indicator_1.update(candle)
        self._technical_indicator_2.update(candle)
        if self._technical_indicator_1.result is None or self._technical_indicator_2.result is None:
            self._result = None
        else:
            self._result = self._operator_callback(self._technical_indicator_1.result,
                                                   self._technical_indicator_2.result)


class MovingAverageTechnicalIndicator(TechnicalIndicator):
    def __init__(self, feature_getter_callback: Callable, lags: int):
        super(MovingAverageTechnicalIndicator, self).__init__(feature_getter_callback, lags)
        self._compute_callback = RollingMean(self._lags)
        self._feature_getter_callback = feature_getter_callback
        self._result = self._compute_callback.mean

    @property
    def result(self):
        return self._compute_callback.mean

    def update(self, candle: Candle):
        self._compute_callback.insert_new_sample(self._feature_getter_callback(candle))

    def _compute(self):
        raise NotImplementedError


def _normalized_autocorrelation(arr: np.ndarray) -> np.ndarray:
    autocorr = np.correlate(arr, arr, 'full')
    autocorr = autocorr / autocorr[len(arr) - 1]  # normalize by value at lag 0
    return autocorr[(len(arr) - 1):]  # return positive lags


def _area_of_normalized_autocorrelation(arr: np.ndarray) -> float:
    return np.sum(_normalized_autocorrelation(arr))


class AutoCorrelationTechnicalIndicator(TechnicalIndicator):
    def __init__(self, feature_getter_callback: Callable, lags: int):
        super(AutoCorrelationTechnicalIndicator, self).__init__(feature_getter_callback, lags)
        self._compute_callback = _area_of_normalized_autocorrelation
        self._feature_getter_callback = feature_getter_callback
        self._result = None

    @property
    def result(self):
        return self._result

    def update(self, candle: Candle):
        self._candles.put(self._feature_getter_callback(candle), block=False)
        if self._candles.full():
            self._compute()
            self._candles.get(block=False)

    def _compute(self):
        self._result = self._compute_callback(np.array(list(self._candles.queue)))


class PriceTechnicalIndicator(TechnicalIndicator):
    def __init__(self, feature_getter_callback: Callable, lags: int):
        super(PriceTechnicalIndicator, self).__init__(feature_getter_callback, lags)
        self._compute_callback = lambda x: x[lags - 1]
        self._feature_getter_callback = feature_getter_callback
        self._result = None

    @property
    def result(self):
        return self._result

    def update(self, candle: Candle):
        self._candles.put(self._feature_getter_callback(candle), block=False)
        if self._candles.full():
            self._compute()
            self._candles.get(block=False)

    def _compute(self):
        self._result = self._compute_callback(np.array(list(self._candles.queue)))


def PPOTechnicalIndicator(feature_getter_callback: Callable, slow_ma_lag: int, fast_ma_lag: int):
    return (MovingAverageTechnicalIndicator(feature_getter_callback, fast_ma_lag) -
            MovingAverageTechnicalIndicator(feature_getter_callback, slow_ma_lag)) / MovingAverageTechnicalIndicator(
        feature_getter_callback, slow_ma_lag)


# class OnBalanceVolumeTechnicalIndicator(TechnicalIndicator):
#     def __init__(self, lags: int):
#         super().__init__(lags)
#         self._compute_callback = _area_of_normalized_autocorrelation
#         self._result = None
#
#     @property
#     def result(self):
#         return self._result
#
#     def update(self, candle: Candle):
#         self._candles.put(candle.get_close_price(), block=False)
#         if self._candles.full():
#             self._compute()
#             self._candles.get(block=False)
#
#     def _compute(self):
#         self._result = self._compute_callback(np.array(list(self._candles.queue)))


if __name__ == "__main__":


    compound_maverage = (
                            MovingAverageTechnicalIndicator(Candle.get_close_price,
                                                            10) - AutoCorrelationTechnicalIndicator(
                                Candle.get_close_price, 10)) / MovingAverageTechnicalIndicator(Candle.get_close_price,
                                                                                               10)

    stock_data = load_from_disk(
        os.path.join(definitions.DATA_DIR, "local_data_15_Jan,_2018_01_Mar,_2018_XRPBTC.dill"))
    acorr = AutoCorrelationTechnicalIndicator(Candle.get_close_price, 10)
    maverage = MovingAverageTechnicalIndicator(Candle.get_close_price, 10)
    iteration = 0
    for candle in stock_data.candles:
        acorr.update(candle)
        maverage.update(candle)
        compound_maverage.update(candle)
        print("Iteration no. {}:".format(iteration))
        print(maverage.result)
        print(acorr.result)
        print(compound_maverage.result)
        iteration += 1
