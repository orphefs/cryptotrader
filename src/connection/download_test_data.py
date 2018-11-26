import os
from datetime import datetime

from binance.enums import KLINE_INTERVAL_1MINUTE

from src import definitions
from src.connection.download_historical_data import _download_historical_data_from_cobinhood, \
    _download_historical_data_from_binance
from src.containers.stock_data import StockData, save_to_disk
from src.containers.time_windows import TimeWindow
from src.containers.trading_pair import TradingPair


def _download_test_data_from_cobinhood():
    security = TradingPair("COB", "ETH")
    time_window = TimeWindow(start_time=datetime(2018, 5, 20, 6, 00),
                             end_time=datetime(2018, 5, 21, 8, 00))
    candles = _download_historical_data_from_cobinhood(time_window, security, "1m")
    print(candles)
    stock_data = StockData(candles, security)
    save_to_disk(stock_data, os.path.join(definitions.DATA_DIR, "sample_data.dill"))


def _download_test_data_from_binance():
    security = TradingPair("NEO", "BTC")
    time_window = TimeWindow(start_time=datetime(2018, 5, 20, 6, 00),
                             end_time=datetime(2018, 5, 21, 8, 00))
    candles = _download_historical_data_from_binance(time_window, security, KLINE_INTERVAL_1MINUTE)[0:50]
    print(candles)
    stock_data = StockData(candles, security)
    save_to_disk(stock_data, os.path.join(definitions.TEST_DATA_DIR, "test_data_long.dill"))


if __name__ == '__main__':
    _download_test_data_from_binance()
