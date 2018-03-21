from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import timedelta, datetime
from typing import Dict, Callable, Union
import pandas as pd

from backtesting_logic.logic import TradingSignal, Buy, Hold, Sell
from containers.candle import Candle
from containers.data_point import PricePoint
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
        self._positions_df = pd.DataFrame(columns=['intended_trade_time',
                                                   'amount_traded', 'actual_price', 'intended_price'])
        self._positions = defaultdict(list)
        self._portfolio_df = pd.DataFrame(columns=['holdings', 'cash', 'returns', 'total'])
        self._point_stats = {}

    def _append_to_positions(self, trade_time, amount, price):
        self._positions['actual_trade_time'].append(trade_time)
        self._positions['amount_traded'].append(amount)
        self._positions['actual_price'].append(price)

    def compute_performance(self):

        self._portfolio_df = pd.DataFrame(index=self._positions['actual_trade_time'])
        self._positions_df = pd.DataFrame(index=self._positions['actual_trade_time'])
        self._positions_df['amount_traded'] = self._positions['amount_traded']
        self._positions_df['actual_price'] = self._positions['actual_price']

        pos = self._compute_positions(fees=self._fees,
                                      positions=self._positions_df['amount_traded'],
                                      prices=self._positions_df['actual_price'])

        self._portfolio_df['holdings'] = self._compute_holdings(positions=pos)
        self._portfolio_df['cash'] = self._compute_cash(initial_capital=self._initial_capital,
                                                        positions=pos,
                                                        prices=self._positions_df['actual_price'])

        self._portfolio_df['total'] = self._compute_total(
            cash=self._portfolio_df['cash'],
            holdings=self._portfolio_df['holdings'])

        self._portfolio_df['returns'] = self._compute_returns(total_earnings=self._portfolio_df['total'])

        self._point_stats['base_index_pct_change'] = (self._positions_df['actual_price'][-1] -
                                                      self._positions_df['actual_price'][0]) / \
                                                     self._positions_df['actual_price'][0]
        self._point_stats['total_pct_change'] = (self._portfolio_df['total'][-1] -
                                                 self._initial_capital) / self._initial_capital

    @staticmethod
    def _compute_holdings(positions: pd.Series) -> pd.Series:
        return positions.cumsum(axis=0)

    @staticmethod
    def _differentiate_positions(positions: pd.Series) -> pd.Series:
        return positions.diff()

    @staticmethod
    def _compute_positions(fees: float, positions: pd.Series, prices: pd.Series) -> pd.Series:
        return positions * prices * (1 - fees)

    @staticmethod
    def _compute_cash(initial_capital: float, positions: pd.Series, prices: pd.Series):
        return initial_capital - (positions * prices).cumsum(axis=0)

    @staticmethod
    def _compute_total(cash: pd.Series, holdings: pd.Series) -> pd.Series:
        return cash + holdings

    @staticmethod
    def _compute_returns(total_earnings: pd.Series) -> pd.Series:
        returns = total_earnings.pct_change()
        return returns

    def update(self, signal: Union[Buy, Sell, Hold]):
        self._place_order(signal, self._trade_amount, signal.price_point)

    def _place_order(self, signal: Union[Buy, Sell, Hold], quantity: int, price_point: PricePoint):
        if isinstance(signal, Buy):
            self._append_to_positions(signal.price_point.date_time, quantity, price_point.value)
        if isinstance(signal, Sell):
            self._append_to_positions(signal.price_point.date_time, -quantity, price_point.value)
        if isinstance(signal, Hold):
            self._append_to_positions(signal.price_point.date_time, 0.0, price_point.value)


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
                return Hold(signal=0, price_point=PricePoint(value=current_price, date_time=current_time))

            elif not self._bought:
                self._bought = True
                self._last_buy_price = current_price
                return Buy(signal=-1, price_point=PricePoint(value=current_price, date_time=current_time))

        elif self.is_sma_crossing_from_above():
            if self._bought:
                self._bought = False
                return Sell(signal=1, price_point=PricePoint(value=current_price, date_time=current_time))

            elif not self._bought:
                return Hold(signal=0, price_point=PricePoint(value=current_price, date_time=current_time))
        else:
            return Hold(signal=0, price_point=PricePoint(value=current_price, date_time=current_time))
