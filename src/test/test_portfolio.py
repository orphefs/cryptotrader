import os
from typing import List, Union

import numpy as np
import pandas as pd
import pytest
from pandas._libs.tslib import Timestamp

from src import definitions
from src.analysis_tools.generate_run_statistics import cleanup_signals
from src.backtesting_logic.logic import Buy, Sell, Hold
from src.connection.downloader import load_from_disk
from src.containers.candle import Candle
from src.containers.data_point import PricePoint, Price
from src.containers.portfolio import Portfolio
from src.helpers import is_equal
from src.test.test_compare_mock_and_backtest_runs import compare_lists

positions = pd.Series([1000, 1000, 1000, 1000])
prices = pd.Series(np.array([1, 1, 1, 1]) * 1e-4)


@pytest.fixture()
def load_candle_data() -> List[Candle]:
    stock_data = load_from_disk(os.path.join(definitions.TEST_DATA_DIR, "test_data_2.dill"))
    return stock_data.candles


def create_mock_signals_from_candles(candles: List[Candle]) -> List[Union[Buy, Sell, Hold]]:
    print("length of cnadles:{}".format(len(candles)))
    signals = []
    current_signal = None
    last_signal = None
    for previous_candle, next_candle in zip(candles[0:], candles[1:]):

        if next_candle.get_close_price() > previous_candle.get_close_price():
            if isinstance(last_signal, Sell) or isinstance(last_signal, Hold) or last_signal is None:
                current_signal = Buy(signal=-1,
                                  price_point=PricePoint(
                                      value=Price(previous_candle.get_close_price()),
                                      date_time=previous_candle.get_close_time_as_datetime()))
                last_signal = current_signal
            else:
                current_signal = Hold(signal=0,
                                   price_point=PricePoint(
                                       value=Price(previous_candle.get_close_price()),
                                       date_time=previous_candle.get_close_time_as_datetime()))
            signals.append(current_signal)
        else:
            if isinstance(last_signal, Buy) or isinstance(last_signal, Hold) or last_signal is None:
                current_signal = Sell(signal=1,
                                     price_point=PricePoint(
                                         value=Price(previous_candle.get_close_price()),
                                         date_time=previous_candle.get_close_time_as_datetime()))
                last_signal = current_signal
            else:
                current_signal = Hold(signal=0,
                                      price_point=PricePoint(
                                          value=Price(previous_candle.get_close_price()),
                                          date_time=previous_candle.get_close_time_as_datetime()))

            signals.append(current_signal)

    for signal in signals:
        print(signal)
    return signals


def initialize_portfolio() -> Portfolio:
    candles = load_candle_data()
    portfolio = Portfolio(initial_capital=5, trade_amount=1000)
    signals = create_mock_signals_from_candles(candles)
    # print(signals)
    for signal in signals:
        portfolio.update(signal)
    portfolio.compute_performance()
    return portfolio


def test_cleanup_signals():
    candles = load_candle_data()
    signals = create_mock_signals_from_candles(candles)
    cleaned_up_signals = cleanup_signals(signals)
    expected_signal_types = [Buy,
                             Sell,
                             Buy,
                             Sell,
                             Buy]
    assert compare_lists(expected_signal_types, [signal.type for signal in cleaned_up_signals])
