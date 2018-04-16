from collections import defaultdict
from typing import Union

import pandas as pd

from backtesting_logic.logic import Buy, Sell, Hold
from containers.data_point import PricePoint


class Portfolio:

    def __init__(self, initial_capital: float, trade_amount: int):
        self._fees = 0.001  # 0.1% on binance
        self._trade_amount = trade_amount
        self._signals = []
        self._capital = []
        self._initial_capital = initial_capital
        self._positions_df = pd.DataFrame(columns=['intended_trade_time',
                                                   'amount_traded', 'actual_price', 'intended_price'])
        self._positions = defaultdict(list)
        self._portfolio_df = pd.DataFrame(columns=['holdings', 'cash', 'returns', 'total'])
        self._point_stats = {}

    def update(self, signal: Union[Buy, Sell, Hold]):
        self._place_order(signal, self._trade_amount, signal.price_point)
        self._signals.append(signal)

    def compute_performance(self):

        self._portfolio_df = pd.DataFrame(index=self._positions['actual_trade_time'])
        self._positions_df = pd.DataFrame(index=self._positions['actual_trade_time'])
        self._positions_df['amount_traded'] = self._positions['amount_traded']
        self._positions_df['actual_price'] = self._positions['actual_price']

        self._portfolio_df['holdings'] = self._compute_holdings(fees=self._fees,
                                                                positions=self._positions_df['amount_traded'],
                                                                prices=self._positions_df['actual_price'])

        self._portfolio_df['cash'] = self._compute_cash(initial_capital=self._initial_capital,
                                                        positions_diff=self._positions_df['amount_traded'].diff(),
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

    def _append_to_positions(self, trade_time, amount, price):
        self._positions['actual_trade_time'].append(trade_time)
        self._positions['amount_traded'].append(amount)
        self._positions['actual_price'].append(price)

    @staticmethod
    def _differentiate_positions(positions: pd.Series) -> pd.Series:
        return positions.diff()

    @staticmethod
    def _compute_holdings(fees: float, positions: pd.Series, prices: pd.Series) -> pd.Series:
        return (positions * prices * (1 - fees)).cumsum(axis=0)

    @staticmethod
    def _compute_cash(initial_capital: float, positions_diff: pd.Series, prices):
        return initial_capital - (positions_diff * prices).cumsum()

    @staticmethod
    def _compute_total(cash: pd.Series, holdings: pd.Series) -> pd.Series:
        return cash + holdings

    @staticmethod
    def _compute_returns(total_earnings: pd.Series) -> pd.Series:
        returns = total_earnings.pct_change()
        return returns

    def _place_order(self, signal: Union[Buy, Sell, Hold], quantity: int, price_point: PricePoint):
        if isinstance(signal, Buy):
            self._append_to_positions(signal.price_point.date_time, -quantity, price_point.value)
        if isinstance(signal, Sell):
            self._append_to_positions(signal.price_point.date_time, quantity, price_point.value)
        if isinstance(signal, Hold):
            self._append_to_positions(signal.price_point.date_time, 0.0, price_point.value)