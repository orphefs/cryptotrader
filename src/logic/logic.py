from abc import ABC

import numpy as np
from typing import List, Union, Dict
import pandas as pd
from datetime import datetime, timedelta

from containers.candle import Candle
from tools.downloader import StockData

Price = float


class DataPoint(object):
    def __init__(self, value: Price, date_time: datetime):
        self._value = value
        self._date_time = date_time

    @property
    def value(self):
        return self._value

    @property
    def date_time(self):
        return self._date_time

    def __repr__(self):
        return "DataPoint({},{})".format(self._value, self._date_time)


class TimeSeries(pd.Series):
    def __init__(self, x: List[datetime], y: Union[List[Price], np.ndarray]):
        super().__init__(data=y, index=x)
        self._sampling_rate = np.median(np.diff(x))

    @property
    def sampling_rate(self):
        return self._sampling_rate

    @staticmethod
    def from_datapoints(data_points: List[DataPoint]):
        return TimeSeries(x=[data_point.date_time for data_point in data_points],
                          y=[data_point.value for data_point in data_points])


_signal_types = {1: "Buy",
                 -1: "Sell",
                 0: "Hold", }


class TradingSignal(object):
    def __init__(self, signal: int, data_point: DataPoint):
        self.signal = signal
        self.type = _signal_types[signal]
        self.data_point = data_point

    def __repr__(self):
        return "TradingSignal({} at {})".format(self.type, self.data_point)


class IntersectionPoint(object):
    def __init__(self, trading_signal: TradingSignal, data_point: DataPoint, intersecting_time_series: List[TimeSeries],
                 tolerance: float):
        self._trading_signal = trading_signal
        self._data_point = data_point
        self._intersecting_time_series = intersecting_time_series
        self._tolerance = tolerance

    @property
    def trading_signal(self):
        return self._trading_signal

    @property
    def data_point(self):
        return self._data_point

    @property
    def tolerance(self):
        return self._tolerance

    @property
    def intersecting_time_series(self):
        return self._intersecting_time_series

    def __repr__(self):
        return "IntersectionPoint(trading_signal={}, data_point={}, tolerance={})".format(self._trading_signal,
                                                                                          self._data_point,
                                                                                          self._tolerance)


class BackTestingStrategy(ABC):
    def generate_trading_signals(self):
        pass


class SMAStrategy(BackTestingStrategy):
    def __init__(self, stock_data: StockData):
        self._instrument = None
        self._candles = stock_data.candles
        self._security = stock_data.security
        self._data = Dict
        self._trading_signals = []

    def prepare_data(self):
        time_series = TimeSeries(
            x=[candle.get_time().close_time for candle in self._candles],
            y=[candle.get_price().close_price for candle in self._candles]
        self._data = {'time_series': time_series,
                      'sma_10': rolling_mean(window_size=timedelta(hours=10),
                                             time_series=time_series),
                      'sma_2': rolling_mean(window_size=timedelta(hours=2),
                                            time_series=time_series),
                      }

    def generate_trading_signals(self):
        self._trading_signals = _generate_trading_signals_from_sma(
            self._data['time_series'],
            self._data['sma_2'],
            self._data['sma_10'],
        )


def _generate_trading_signals_from_sma(
        original_time_series: TimeSeries,
        time_series_a: TimeSeries,
        time_series_b: TimeSeries) -> List[TradingSignal]:
    trading_signals = list(map(int, np.diff(np.where(time_series_a > time_series_b, 1.0, 0.0))))

    return [TradingSignal(trading_signals[i],
                          DataPoint(value=original_time_series[i], date_time=original_time_series.index[i]))
            for i, _ in enumerate(trading_signals)]


def rolling_mean(window_size: timedelta, time_series: TimeSeries):
    return pd.rolling_mean(time_series, window_size, min_periods=1)


def simple_moving_average(window_size: timedelta, time_series: TimeSeries) -> TimeSeries:
    window_size_int = window_size // time_series.sampling_rate
    weights = np.repeat(1.0, window_size_int) / window_size_int
    sma = np.convolve(np.array(time_series), weights, 'valid')
    return TimeSeries(x=time_series.index[window_size_int - 1:], y=sma)


def exponential_moving_average(window_size: timedelta, time_series: TimeSeries) -> TimeSeries:
    return None


if __name__ == '__main__':
    pass
