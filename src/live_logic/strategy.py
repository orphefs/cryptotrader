from abc import ABC, abstractmethod
from datetime import timedelta, datetime
from typing import Dict, Callable, Union
import pandas as pd

from backtesting_logic.logic import TradingSignal, Buy, Hold, Sell
from containers.candle import Candle
from containers.data_point import DataPoint
from containers.time_series import TimeSeries
from backtesting_logic.signal_processing import rolling_mean, _generate_trading_signals_from_sma
from containers.stock_data import StockData


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
        self._fees = 0.001  # 0.1% on binance
        self._trade_amount = trade_amount
        self._capital = []
        self._initial_capital = initial_capital
        self.portfolio = {}
        self.portfolio['positions'] = [(None, 0.0, None)]
        self._portfolio_df = pd.DataFrame(columns=['holdings', 'cash', 'returns', 'total'])
        self._point_stats = {}

    def _append_to_positions(self, trade_time, amount, candle):
        cumulative_amount = self.portfolio['positions'][0][1] + amount
        self.portfolio['positions'].append((trade_time, cumulative_amount, candle))

    def compute_statistics(self):
        self._portfolio_df = pd.DataFrame(index=[holding[0] for holding in self.portfolio['positions']])
        self._portfolio_df['positions'] = [holding[1] for holding in self.portfolio['positions']]
        data_points = [item[2] for item in self.portfolio['positions']][1:]
        data_points_df = pd.DataFrame(data=[data_point.value for data_point in data_points],
                                      index=[data_point.date_time for data_point in data_points])

        pos = self._portfolio_df['positions'][1:][0] * data_points_df[:][0] * (1 - self._fees)
        pos_diff = pos.diff(periods=1)

        # Create the 'holdings' and 'cash' series by running through
        # the trades and adding/subtracting the relevant quantity from
        # each column

        self._portfolio_df['holdings'] = pos.cumsum(axis=0)
        self._portfolio_df['cash'] = self._initial_capital - (pos_diff * data_points_df[:][0]).cumsum(axis=0)

        # Finalise the total and bar-based returns based on the 'cash'
        # and 'holdings' figures for the portfolio
        self._portfolio_df['total'] = self._portfolio_df['cash'] + self._portfolio_df['holdings']
        self._portfolio_df['returns'] = self._portfolio_df['total'].pct_change()

        self._point_stats['base_index_pct_change'] = (data_points_df[0][-1] - data_points_df[0][0])/data_points_df[0][0]
        self._point_stats['total_pct_change'] = (self._portfolio_df['total'][-1] -
                                                 self._initial_capital)/self._initial_capital

    def _compute_cash(self):
        pass

    def _compute_total(self):
        pass

    def _compute_returns(self):
        pass

    def _place_order(self, signal: Union[Buy, Sell, Hold], quantity: int, data_point: DataPoint):
        if isinstance(signal, Buy):
            self._append_to_positions(signal.data_point.date_time, quantity, data_point)
        if isinstance(signal, Sell):
            self._append_to_positions(signal.data_point.date_time, -quantity, data_point)

    def update(self, signal: Union[Buy, Sell, Hold]):
        if signal is None:
            self._place_order(None, self._trade_amount, None)
        else:
            self._place_order(signal, self._trade_amount, signal.data_point)


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
        self._last_buy_price = 0.0

    def is_sma_crossing_from_below(self):
        return (self._short_sma[-2] < self._long_sma[-2]) and (self._short_sma[-1] > self._long_sma[-1])

    def is_sma_crossing_from_above(self):
        return (self._short_sma[-2] > self._long_sma[-2]) and (self._short_sma[-1] < self._long_sma[-1])

    def is_current_price_higher_than_last_buy(self, current_price: float):
        return current_price > self._last_buy_price

    def extract_time_series_from_stock_data(self, stock_data: StockData):
        self._stock_data = stock_data
        self._time_series = TimeSeries(
            x=[candle.get_time().close_time.as_datetime() for candle in stock_data.candles],
            y=[candle.get_price().close_price for candle in stock_data.candles])

    def compute_moving_averages(self):
        self._short_sma = rolling_mean(self._parameters.short_sma_period, self._time_series)
        self._long_sma = rolling_mean(self._parameters.long_sma_period, self._time_series)

    def generate_trading_signal(self) -> Union[Buy, Sell, Hold]:
        current_price = self._stock_data.candles[-1].get_price().close_price
        current_time = self._stock_data.candles[-1].get_time().close_time.as_datetime()

        if self.is_sma_crossing_from_below():
            if self._bought:
                return Hold(signal=0, data_point=DataPoint(value=current_price, date_time=current_time))

            elif not self._bought:
                self._bought = True
                self._last_buy_price = current_price
                return Buy(signal=-1, data_point=DataPoint(value=current_price, date_time=current_time))

        elif self.is_sma_crossing_from_above():
            if self._bought:
                self._bought = False
                return Sell(signal=1, data_point=DataPoint(value=current_price, date_time=current_time))

            elif not self._bought:
                return Hold(signal=0, data_point=DataPoint(value=current_price, date_time=current_time))
        else:
            return Hold(signal=0, data_point=DataPoint(value=current_price, date_time=current_time))
