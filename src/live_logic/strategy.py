from abc import ABC, abstractmethod
from datetime import timedelta, datetime
from typing import Dict, Callable, Union
import pandas as pd

from backtesting_logic.logic import TradingSignal
from containers.candle import Candle
from containers.time_series import TimeSeries
from backtesting_logic.signal_processing import rolling_mean, _generate_trading_signals_from_sma
from tools.downloader import StockData


class Signal:
    def __init__(self, date_time: datetime, candle: Candle):
        self._date_time = date_time
        self._candle = candle

    @property
    def date_time(self):
        return self._date_time

    @property
    def candle(self):
        return self._candle


class Buy(Signal):
    pass


class Sell(Signal):
    pass


class Hold(Signal):
    pass


class LiveStrategy:
    pass


class Parameters:
    pass


class LiveParameters(Parameters):
    def __init__(self, short_sma_period: timedelta,
                 long_sma_period: timedelta,
                 trade_amount: int,
                 sleep_time: int):
        self.short_sma_period = short_sma_period
        self.long_sma_period = long_sma_period
        self.trade_amount = trade_amount
        self.sleep_time = sleep_time


class Portfolio:
    def __init__(self, initial_capital: float, trade_amount: int):
        self._fees = 0.01  # percent
        self._trade_amount = trade_amount
        self._capital = []
        self._initial_capital = initial_capital
        self.portfolio = {}
        self.portfolio['holdings'] = [(None, 0.0)]
        self._portfolio_df = pd.DataFrame(columns=['holdings', 'cash', 'returns', 'total'])

    def _append_to_holdings(self, trade_time, amount):
        cumulative_amount = self.portfolio['holdings'][0][1] + amount
        self.portfolio['holdings'].append((trade_time, cumulative_amount))

    def convert_to_pandas(self):
        self._portfolio_df = pd.DataFrame(index=[holding[0] for holding in self.portfolio['holdings']])
        self._portfolio_df['holdings'] = [holding[1] for holding in self.portfolio['holdings']]


    def _compute_cash(self):
        pass

    def _compute_total(self):
        pass

    def _compute_returns(self):
        pass

    def _place_order(self, signal: Union[Buy, Sell, Hold], quantity: int):
        if isinstance(signal, Buy):
            self._append_to_holdings(signal.date_time, quantity)
        if isinstance(signal, Sell):
            self._append_to_holdings(signal.date_time, -quantity)

    def update(self, signal: Union[Buy, Sell, Hold]):
        self._place_order(signal, self._trade_amount)


class SMAStrategy(LiveStrategy):
    def __init__(self, parameters: LiveParameters):
        self._data = Dict
        self._stock_data = StockData
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

    def extract_time_series_from_stock_data(self, stock_data: StockData):
        self._stock_data = stock_data
        self._time_series = TimeSeries(
            x=[candle.get_time().close_time.as_datetime() for candle in stock_data.candles],
            y=[candle.get_price().close_price for candle in stock_data.candles])

    def compute_moving_averages(self):
        self._short_sma = rolling_mean(self._parameters.short_sma_period, self._time_series)
        self._long_sma = rolling_mean(self._parameters.long_sma_period, self._time_series)

    def generate_trading_signal(self) -> Union[Buy, Sell, Hold]:
        if self.is_sma_crossing_up():
            if self._bought:
                pass
            elif not self._bought:

                self._bought = True
                return Buy(date_time=self._stock_data.candles[-1].get_time().close_time.as_datetime(),
                           candle=self._stock_data.candles[-1])

        elif self.is_sma_crossing_down():
            if self._bought:

                self._bought = False
                return Sell(date_time=self._stock_data.candles[-1].get_time().close_time.as_datetime(),
                            candle=self._stock_data.candles[-1])

            elif not self._bought:
                pass
        else:
            return Hold(date_time=self._stock_data.candles[-1].get_time().close_time.as_datetime(),
                        candle=self._stock_data.candles[-1])

# def sell():
#     self._portfolio.place_order(symbol=self._security, side='sell',
#                                 type='market', quantity=self._parameters.trade_amount)
#
#
# def buy():
#     self._portfolio.place_order(symbol=self._security, side='buy',
#                                 type='market', quantity=self._parameters.trade_amount)
