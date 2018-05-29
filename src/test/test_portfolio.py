import os
from typing import List

import pytest

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


def test_portfolio():
    candles = load_candle_data()
    portfolio = Portfolio(initial_capital=5, trade_amount=100)
    signals = create_mock_signals_from_candles(candles)
    print(signals)
    for signal in signals:
        portfolio.update(signal)
    portfolio.compute_performance()

    expected_results = portfolio.portfolio_df["holdings"]
    results = [1]

    print("\nTest result is {}".format(results))
    print("Expected result is {}".format(expected_results))
    assert is_equal(results, expected_results)


if __name__ == '__main__':
    # import subprocess
    #
    # # subprocess.call(['pytest', os.path.basename(__file__), '--collect-only'])
    # subprocess.call(['pytest', __file__])
    test_portfolio()
