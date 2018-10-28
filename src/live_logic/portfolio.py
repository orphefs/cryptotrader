import os
from collections import defaultdict
from typing import Union

import pandas as pd

from src import definitions
from src.backtesting_logic.logic import Buy, Sell, Hold
from src.containers.data_point import PricePoint
from src.mixins.save_load_mixin import DillSaveLoadMixin

percentage = float


class Portfolio(DillSaveLoadMixin):
    def __init__(self, initial_capital: float, trade_amount: int):
        self._fees = 0.001  # 0.1% on binance
        self._trade_amount = trade_amount
        self._signals = []
        self._capital = []
        self._initial_capital = initial_capital
        self._positions_df = pd.DataFrame(columns=['intended_trade_time',
                                                   'amount_traded', 'actual_price', 'intended_price'])
        self._positions = defaultdict(list)
        self._portfolio_df = pd.DataFrame(columns=['order_expenditure', 'cumulative_order_expenditure',
                                                   'remaining_capital'])
        self._point_stats = {}

    @property
    def portfolio_df(self):
        return self._portfolio_df

    @property
    def positions_df(self):
        return self._positions_df

    @property
    def signals(self):
        return self._signals

    def update(self, signal: Union[Buy, Sell, Hold]):
        self._place_order(signal, self._trade_amount, signal.price_point)
        self._signals.append(signal)

    def compute_performance(self):

        self._portfolio_df = pd.DataFrame(index=self._positions['actual_trade_time'])
        self._positions_df = pd.DataFrame(index=self._positions['actual_trade_time'])
        self._positions_df['amount_traded'] = self._positions['amount_traded']
        self._positions_df['actual_price'] = self._positions['actual_price']

        self._portfolio_df['order_expenditure'] = self._compute_order_expenditure(fees=self._fees,
                                                                positions=self._positions_df['amount_traded'],
                                                                prices=self._positions_df['actual_price'])

        self._portfolio_df['cumulative_order_expenditure'] = self._compute_cumulative_order_expenditure(
            self._portfolio_df['order_expenditure'])

        self._portfolio_df['remaining_capital'] = self._compute_remaining_capital(
            initial_capital=self._initial_capital,
            cumulative_order_expenditure=self._portfolio_df['cumulative_order_expenditure']
        )


        self._point_stats['base_index_pct_change'] = (self._positions_df['actual_price'][-1] -
                                                      self._positions_df['actual_price'][0]) / \
                                                     self._positions_df['actual_price'][0]
        self._point_stats['total_pct_change'] = (self._portfolio_df['remaining_capital'][-1] -
                                                 self._initial_capital) / self._initial_capital

    def _append_to_positions(self, trade_time, amount, price):
        self._positions['actual_trade_time'].append(trade_time)
        self._positions['amount_traded'].append(amount)
        self._positions['actual_price'].append(price)

    @staticmethod
    def _compute_remaining_capital(initial_capital: float, cumulative_order_expenditure: pd.Series) -> pd.Series:
        return initial_capital - cumulative_order_expenditure

    @staticmethod
    def _compute_order_expenditure(fees: float, positions: pd.Series,
                                    prices: pd.Series) -> pd.Series:
        return positions.multiply(prices)

    @staticmethod
    def _compute_cumulative_order_expenditure(order_expenditures: pd.Series) -> pd.Series:
        return order_expenditures.cumsum()

    def _place_order(self, signal: Union[Buy, Sell, Hold], quantity: int, price_point: PricePoint):
        if isinstance(signal, Buy):
            self._append_to_positions(signal.price_point.date_time, -quantity, price_point.value)
        if isinstance(signal, Sell):
            self._append_to_positions(signal.price_point.date_time, quantity, price_point.value)
        if isinstance(signal, Hold):
            self._append_to_positions(signal.price_point.date_time, 0.0, price_point.value)

    def convert_to_csv(self):
        self._portfolio_df.to_csv(os.path.join(definitions.DATA_DIR, "portfolio.csv"))

    def __str__(self):
        return "Trade Amount: {}, \n" \
               "Initial Capital: {}".format(self._trade_amount, self._initial_capital)
