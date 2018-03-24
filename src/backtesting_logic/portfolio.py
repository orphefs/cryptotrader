from abc import ABC, abstractmethod
from typing import List

import pandas as pd

from backtesting_logic.logic import TradingSignal
from containers.stock_data import StockData


class Portfolio(ABC):
    """An abstract base class representing a portfolio of
    _positions (including both instruments and cash), determined
    on the basis of a set of signals provided by a Strategy."""

    @abstractmethod
    def generate_positions(self):
        """Provides the backtesting_logic to determine how the portfolio
        _positions are allocated on the basis of forecasting
        signals and available cash."""
        raise NotImplementedError("Should implement generate_positions()!")

    @abstractmethod
    def backtest_portfolio(self):
        """Provides the backtesting_logic to generate the trading orders
        and subsequent equity curve (i.e. growth of total equity),
        as a sum of holdings and cash, and the bar-period returns
        associated with this curve based on the '_positions' DataFrame.

        Produces a portfolio object that can be examined by
        other classes/functions."""
        raise NotImplementedError("Should implement backtest_portfolio()!")

    @property
    def portfolio(self):
        pass


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
                 initial_capital: float = 1.0):
        self._symbol = stock_data.security
        self._candles = pd.DataFrame(data={
            'Open': [candle.get_price().open_price for candle in stock_data.candles],
            'High': [candle.get_price().high_price for candle in stock_data.candles],
            'Low': [candle.get_price().low_price for candle in stock_data.candles],
            'Close': [candle.get_price().close_price for candle in stock_data.candles]},
            index=[candle.get_close_time_as_datetime() for candle in stock_data.candles])
        self._fees = 0.01  # percent
        self._trading_signals = pd.DataFrame(data=[signal.signal for signal in trading_signals],
                                             index=[signal.price_point.date_time for signal in trading_signals])
        self._initial_capital = initial_capital
        self._positions = self.generate_positions()
        self._portfolio = {}
        self.backtest_portfolio()

    def generate_positions(self):
        """Creates a '_positions' DataFrame that simply longs or shorts
        100 of the particular symbol based on the forecast signals of
        {1, 0, -1} from the signals DataFrame."""
        positions = 2000 * self._trading_signals.fillna(0.0)
        return positions

    def backtest_portfolio(self):
        """Constructs a portfolio from the _positions DataFrame by
        assuming the ability to trade at the precise market close price
        of each bar (an unrealistic assumption?).

        Calculates the total of cash and the holdings (market price of
        each position per bar), in order to generate an equity curve
        ('total') and a set of bar-based returns ('returns').

        Returns the portfolio object to be used elsewhere."""

        # Construct the portfolio DataFrame to use the same index
        # as '_positions' and with a set of 'trading orders' in the
        # 'pos_diff' object, assuming market open prices.
        pos = self._positions[0] * self._candles['Open'] * (1-self._fees)
        pos_diff = pos.diff(periods=1)
        self._portfolio = pd.DataFrame(columns=['holdings', 'cash', 'returns', 'total'])

        # Create the 'holdings' and 'cash' series by running through
        # the trades and adding/subtracting the relevant quantity from
        # each column

        self._portfolio['holdings'] = pos.cumsum(axis=0)
        self._portfolio['cash'] = self._initial_capital - (pos_diff * self._candles['Open']).cumsum(axis=0)

        # Finalise the total and bar-based returns based on the 'cash'
        # and 'holdings' figures for the portfolio
        self._portfolio['total'] = self._portfolio['cash'] + self._portfolio['holdings']
        self._portfolio['returns'] = self._portfolio['total'].pct_change()
        return self._portfolio

    @property
    def portfolio(self):
        return self._portfolio