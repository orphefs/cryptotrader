import os
from typing import List

import numpy as np
import pandas as pd
import pytest
from pandas._libs.tslib import Timestamp

from src import definitions
from src.containers.order import Order
from src.containers.signal import SignalBuy
from src.containers.stock_data import load_from_disk
from src.containers.candle import Candle
from src.containers.data_point import PricePoint, Price
from src.containers.portfolio import Portfolio
from src.helpers import is_equal

positions = pd.Series([1000, 1000, 1000, 1000])
prices = pd.Series(np.array([1, 1, 1, 1]) * 1e-4)


def load_candle_data() -> List[Candle]:
    stock_data = load_from_disk(os.path.join(definitions.TEST_DATA_DIR, "test_data.dill"))
    return stock_data.candles


def create_mock_signals_from_candles(candles: List[Candle]) -> List[SignalBuy]:
    return [SignalBuy(signal=1, price_point=PricePoint(
        value=Price(candle.get_close_price()),
        date_time=candle.get_close_time_as_datetime())) for candle in candles]


def initialize_portfolio() -> Portfolio:
    candles = load_candle_data()
    portfolio = Portfolio(initial_capital=5, trade_amount=1000)
    signals = create_mock_signals_from_candles(candles)
    # print(signals)
    for signal in signals:
        portfolio.update(Order.from_signal(signal))
    portfolio.compute_performance()
    return portfolio


def test_portfolio_holdings():
    portfolio = initialize_portfolio()

    results = [
        (portfolio.portfolio_df["holdings"][0], portfolio.portfolio_df["holdings"].index[0]),
        (portfolio.portfolio_df["holdings"][4], portfolio.portfolio_df["holdings"].index[4]),
    ]
    expected_results = [
        (-0.008198793000000001, Timestamp('2018-05-21 00:56:59.999000')),
        (-0.040975983, Timestamp('2018-05-21 01:00:59.999000'))
    ]

    print("\nTest result is {}".format(results))
    print("Expected result is {}".format(expected_results))
    assert is_equal(results, expected_results)


def test__compute_holdings():
    holdings = Portfolio._compute_holdings(fees=0.1,
                                           positions=positions,
                                           prices=prices,
                                           )
    results = list(holdings)
    expected_results = [0.09000000000000001, 0.18000000000000002, 0.27, 0.36000000000000004]

    print("\nTest result is {}".format(results))
    print("Expected result is {}".format(expected_results))
    assert is_equal(results, expected_results)


def test__compute_cash():
    cash = Portfolio._compute_cash(initial_capital=5.0,
                                   positions_diff=positions.diff(),
                                   prices=prices)
    results = list(cash)
    expected_results = list(5.0 - np.ndarray([0.09000000000000001, 0.18000000000000002, 0.27, 0.36000000000000004]))

    print("\nTest result is {}".format(results))
    print("Expected result is {}".format(expected_results))
    assert is_equal(results, expected_results)


if __name__ == '__main__':
    # import subprocess
    #
    # # subprocess.call(['pytest', os.path.basename(__file__), '--collect-only'])
    # subprocess.call(['pytest', __file__])
    test_portfolio()
