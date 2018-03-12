from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Dict, Callable
import pandas as pd

from containers.time_series import TimeSeries
from backtesting_logic.signal_processing import rolling_mean, _generate_trading_signals_from_sma
from tools.downloader import StockData


class LiveStrategy(ABC):
    @abstractmethod
    def prepare_data(self):
        pass

    @abstractmethod
    def generate_trading_signals(self):
        pass


class Parameters:
    pass


class LiveParameters(Parameters):
    def __init__(self, short_sma_period: timedelta,
                 long_sma_period: timedelta,
                 trade_amount: int,
                 sleep_time: timedelta):
        self.short_sma_period = short_sma_period
        self.long_sma_period = long_sma_period
        self.trade_amount = trade_amount
        self.sleep_time = sleep_time


class SMAStrategy(LiveStrategy):
    def __init__(self, stock_data: StockData, parameters: LiveParameters):
        self._candles = stock_data.candles
        self._security = stock_data.security
        self._data = Dict
        self._trading_signals = []
        self._parameters = parameters
        self._time_series = TimeSeries
        self._short_sma = pd.Series
        self._long_sma = pd.Series
        self._bought = False

    def is_sma_crossing_up(self):
        return (self._short_sma[-2] < self._long_sma[-2]) and (self._short_sma[-1] > self._long_sma[-1])

    def is_sma_crossing_down(self):
        return (self._short_sma[-2] > self._long_sma[-2]) and (self._short_sma[-1] < self._long_sma[-1])

    def extract_time_series_from_stock_data(self):
        self._time_series = TimeSeries(
            x=[candle.get_time().close_time for candle in self._candles],
            y=[candle.get_price().close_price for candle in self._candles])

    def compute_moving_averages(self):
        self._short_sma = rolling_mean(self._parameters.short_sma_period, self._time_series)
        self._long_sma = rolling_mean(self._parameters.long_sma_period, self._time_series)

    def generate_trading_signal(self, order_fcn: Callable):
        if self.is_sma_crossing_up():
            if self._bought:
                pass
            elif not self._bought:
                place_order(order_fcn, symbol=self._security, side=Client.SIDE_BUY,
                            type=Client.ORDER_TYPE_MARKET, quantity=self._parameters.trade_amount)
        elif self.is_sma_crossing_down():
            if self._bought:
                place_order(order_fcn, symbol=self._security, side=Client.SIDE_SELL,
                            type=Client.ORDER_TYPE_MARKET, quantity=self._parameters.trade_amount)
            elif not self._bought:
                pass
