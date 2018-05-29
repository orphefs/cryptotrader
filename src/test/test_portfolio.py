import os
from typing import List

import pandas as pd
import pytest
from pandas._libs.tslib import Timestamp

from src import definitions
from src.backtesting_logic.logic import Buy
from src.containers.candle import Candle
from src.containers.data_point import PricePoint, Price
from src.helpers import is_equal
from src.live_logic.portfolio import Portfolio
from src.tools.downloader import load_from_disk


@pytest.fixture()
def load_candle_data() -> List[Candle]:
    stock_data = load_from_disk(os.path.join(definitions.TEST_DATA_DIR, "test_data.dill"))
    return stock_data.candles


def create_mock_signals_from_candles(candles: List[Candle]) -> List[Buy]:
    return [Buy(signal=1, price_point=PricePoint(value=Price(candle.get_close_price()),
                                                 date_time=candle.get_close_time_as_datetime())) for candle in candles]


def initialize_portfolio() -> Portfolio:
    candles = load_candle_data()
    portfolio = Portfolio(initial_capital=5, trade_amount=100)
    signals = create_mock_signals_from_candles(candles)
    # print(signals)
    for signal in signals:
        portfolio.update(signal)
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
                                           positions=pd.Series([1, -1, 1, 1]),
                                           prices=pd.Series([1, 1, 1, 1]))
    results = list(holdings)
    expected_results = [0.9, 0.0, 0.9, 1.8]

    print("\nTest result is {}".format(results))
    print("Expected result is {}".format(expected_results))
    assert is_equal(results, expected_results)


if __name__ == '__main__':
    # import subprocess
    #
    # # subprocess.call(['pytest', os.path.basename(__file__), '--collect-only'])
    # subprocess.call(['pytest', __file__])
    test_portfolio()
