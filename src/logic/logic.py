from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Union, Dict

import numpy as np
import pandas as pd

from containers.candle import Candle
from tools.downloader import StockData

Price = float


def rolling_mean(window_size: timedelta, time_series: TimeSeries):
    return pd.rolling_mean(time_series, window_size, min_periods=1)


def simple_moving_average(window_size: timedelta, time_series: TimeSeries) -> TimeSeries:
    window_size_int = window_size // time_series.sampling_rate
    weights = np.repeat(1.0, window_size_int) / window_size_int
    sma = np.convolve(np.array(time_series), weights, 'valid')
    return TimeSeries(x=time_series.index[window_size_int - 1:], y=sma)


def exponential_moving_average(window_size: timedelta, time_series: TimeSeries) -> TimeSeries:
    return None


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


def _generate_trading_signals_from_sma(
        original_time_series: TimeSeries,
        time_series_a: TimeSeries,
        time_series_b: TimeSeries) -> List[TradingSignal]:
    trading_signals = list(map(int, np.diff(np.where(time_series_a > time_series_b, 1.0, 0.0))))

    return [TradingSignal(trading_signals[i],
                          DataPoint(value=original_time_series[i], date_time=original_time_series.index[i]))
            for i, _ in enumerate(trading_signals)]


class BackTestingStrategy(ABC):
    @abstractmethod
    def prepare_data(self):
        pass

    @abstractmethod
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
            y=[candle.get_price().close_price for candle in self._candles])
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


class Portfolio(ABC):
    """An abstract base class representing a portfolio of
    positions (including both instruments and cash), determined
    on the basis of a set of signals provided by a Strategy."""

    @abstractmethod
    def generate_positions(self):
        """Provides the logic to determine how the portfolio
        positions are allocated on the basis of forecasting
        signals and available cash."""
        raise NotImplementedError("Should implement generate_positions()!")

    @abstractmethod
    def backtest_portfolio(self):
        """Provides the logic to generate the trading orders
        and subsequent equity curve (i.e. growth of total equity),
        as a sum of holdings and cash, and the bar-period returns
        associated with this curve based on the 'positions' DataFrame.

        Produces a portfolio object that can be examined by
        other classes/functions."""
        raise NotImplementedError("Should implement backtest_portfolio()!")


class MarketOnClosePortfolio(Portfolio):
    """Inherits Portfolio to create a system that purchases 100 units of
    a particular symbol upon a long/short signal, assuming the market
    open price of a bar.

    In addition, there are zero transaction costs and cash can be immediately
    borrowed for shorting (no margin posting or interest requirements).

    Requires:
    symbol - A stock symbol which forms the basis of the portfolio.
    bars - A DataFrame of bars for a symbol set.
    signals - A pandas DataFrame of signals (1, 0, -1) for each symbol.
    initial_capital - The amount in cash at the start of the portfolio."""

    def __init__(self, stock_data: StockData, trading_signals: List[TradingSignal],
                 initial_capital: float = 100000.0):
        self._symbol = stock_data.security
        self._candles = pd.DataFrame(data=[candle.get_price().close_price for candle in stock_data.candles],
                                     index=[candle.get_time().close_time for candle in stock_data.candles])
        self._trading_signals = pd.DataFrame(data=[signal.signal for signal in trading_signals],
                                             index=[signal.data_point.date_time for signal in trading_signals])
        self._initial_capital = initial_capital
        self._positions = self.generate_positions()
        self.backtest_portfolio()

    def generate_positions(self):
        """Creates a 'positions' DataFrame that simply longs or shorts
        100 of the particular symbol based on the forecast signals of
        {1, 0, -1} from the signals DataFrame."""
        positions = 100 * self._trading_signals.fillna(0.0)
        return positions

    def backtest_portfolio(self):
        """Constructs a portfolio from the positions DataFrame by
        assuming the ability to trade at the precise market close price
        of each bar (an unrealistic assumption?).

        Calculates the total of cash and the holdings (market price of
        each position per bar), in order to generate an equity curve
        ('total') and a set of bar-based returns ('returns').

        Returns the portfolio object to be used elsewhere."""

        # Construct the portfolio DataFrame to use the same index
        # as 'positions' and with a set of 'trading orders' in the
        # 'pos_diff' object, assuming market open prices.
        portfolio = self._positions * self._candles
        pos_diff = self._positions.diff()

        # Create the 'holdings' and 'cash' series by running through
        # the trades and adding/subtracting the relevant quantity from
        # each column
        portfolio['holdings'] = (self._positions * self._candles).sum(axis=1)
        portfolio['cash'] = self._initial_capital - (pos_diff * self._candles['Open']).sum(axis=1).cumsum()

        # Finalise the total and bar-based returns based on the 'cash'
        # and 'holdings' figures for the portfolio
        portfolio['total'] = portfolio['cash'] + portfolio['holdings']
        portfolio['returns'] = portfolio['total'].pct_change()
        return portfolio


if __name__ == '__main__':
    pass
