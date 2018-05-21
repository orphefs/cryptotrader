from typing import List

from src.containers.data_point import PricePoint
from src.containers.time_series import TimeSeries


class _TradingSignal(object):
    def __init__(self, signal: int, price_point: PricePoint):
        self.signal = signal
        self.type = _signal_types[signal]
        self.price_point = price_point

    def __repr__(self):

        return type(self).__name__ + "({} at {})".format(self.signal, self.price_point)

    @staticmethod
    def from_signal_integer(signal_integer: int, price_point: PricePoint):
        cls = _signal_types[signal_integer]
        return cls(signal_integer, price_point)


class Buy(_TradingSignal):
    pass


class Sell(_TradingSignal):
    pass


class Hold(_TradingSignal):
    pass


_signal_types = {-1: Buy,
                 1: Sell,
                 0: Hold, }


class IntersectionPoint(object):
    def __init__(self, trading_signal: _TradingSignal, price_point: PricePoint,
                 intersecting_time_series: List[TimeSeries],
                 tolerance: float):
        self._trading_signal = trading_signal
        self._data_point = price_point
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
        return "IntersectionPoint(trading_signal={}, price_point={}, tolerance={})".format(self._trading_signal,
                                                                                           self._data_point,
                                                                                           self._tolerance)


if __name__ == '__main__':
    pass
