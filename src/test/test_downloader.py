import glob
import os
from datetime import datetime, timedelta

import numpy as np
import pytest
from typing import List

from src.classification.trading_classifier import TradingClassifier
from src.connection.load_stock_data import load_stock_data

from src.containers.stock_data import StockData, load_from_disk
from src.containers.time_windows import TimeWindow
from src.containers.trading_pair import TradingPair
from src.definitions import TEST_DATA_DIR, DATA_DIR
from src.helpers import is_equal
from src.test.test_compare_mock_and_backtest_runs import compare_lists
from src.type_aliases import BinanceClient, CobinhoodClient


def download_binance_data(time_window, trading_pair, sampling_period, client) -> StockData:
    return load_stock_data(time_window, trading_pair, sampling_period, client)


def download_cobinhood_data(time_window, trading_pair, sampling_period, client) -> StockData:
    return load_stock_data(time_window, trading_pair, sampling_period, client)


def compare_if_closing_prices_within_tolerance_limit(a: List, b: List) -> float:
    percentage_changes = []
    for candle_a, candle_b in zip(a, b):
        percentage_changes.append(abs(candle_a.get_close_price() - candle_b.get_close_price())
                                  / candle_b.get_close_price())
        # print(candle_b.get_close_price(), candle_a.get_close_price())
    # for percentage_change in percentage_changes:
    #     print(percentage_change)
    return float(np.median(percentage_changes))


def compare_datetimes(a: List, b: List) -> bool:
    return all([(candle_a.get_close_time_as_datetime() -
                candle_b.get_close_time_as_datetime()) < timedelta(seconds=60) for candle_a, candle_b in zip(a, b)])


def clear_downloaded_stock_data():
    files = glob.glob(os.path.join(DATA_DIR, "local_data*.dill"))
    for filename in files:
        try:
            os.remove(filename)
        except OSError:
            pass


def test_integrity_of_downloaded_stock_data():
    time_window = TimeWindow(start_time=datetime(2018, 10, 2), end_time=datetime(2018, 10, 3))
    trading_pair = TradingPair("NEO", "BTC")
    sampling_period = timedelta(minutes=1)

    clear_downloaded_stock_data()
    binance_data = download_binance_data(time_window, trading_pair, sampling_period, client=BinanceClient("", ""))
    clear_downloaded_stock_data()
    cobinhood_data = download_binance_data(time_window, trading_pair, sampling_period, client=CobinhoodClient())

    print(len(binance_data.candles))
    print(binance_data.candles[0])
    print(binance_data.candles[-1])
    print(len(cobinhood_data.candles))
    print(cobinhood_data.candles[0])
    print(cobinhood_data.candles[-1])

    assert len(binance_data.candles) == len(cobinhood_data.candles)
    assert compare_if_closing_prices_within_tolerance_limit(binance_data.candles, cobinhood_data.candles) < 0.2
    assert compare_datetimes(binance_data.candles, cobinhood_data.candles)
