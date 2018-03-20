from typing import List

from containers.data_point import PricePoint
from containers.time_series import TimeSeries

_signal_types = {-1: "Buy",
                 1: "Sell",
                 0: "Hold", }


class TradingSignal(object):
    def __init__(self, signal: int, price_point: PricePoint):
        self.signal = signal
        self.type = _signal_types[signal]
        self.price_point = price_point

    def __repr__(self):
        return "TradingSignal({} at {})".format(self.type, self.price_point)


class Buy(TradingSignal):
    pass


class Sell(TradingSignal):
    pass


class Hold(TradingSignal):
    pass


class IntersectionPoint(object):
    def __init__(self, trading_signal: TradingSignal, price_point: PricePoint, intersecting_time_series: List[TimeSeries],
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
