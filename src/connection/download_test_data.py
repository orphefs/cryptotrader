import os
from datetime import datetime, timedelta

from binance.enums import KLINE_INTERVAL_1MINUTE

from src import definitions
from src.connection.download_historical_data import _download_historical_data_from_binance
from src.containers.stock_data import StockData, save_to_disk
from src.containers.time_windows import TimeWindow
from src.containers.trading_pair import TradingPair
from src.type_aliases import BinanceClient


def _download_test_data_from_cobinhood():
    trading_pair = TradingPair("ETH", "BTC")
    sampling_period = timedelta(minutes=1)
    client = CobinhoodClient()
    time_window = TimeWindow(start_time=datetime(2018, 10, 20, 6, 00),
        end_time=datetime(2018, 10, 22, 8, 00))
    candles = _download_historical_data_from_cobinhood(time_window, trading_pair, sampling_period, client)[
              0:2000]
    print(candles)
    stock_data = StockData(candles, trading_pair)
    save_to_disk(stock_data, os.path.join(definitions.TEST_DATA_DIR, "test_data_3.dill"))


def _download_test_data_from_binance():
    trading_pair = TradingPair("XRP", "BTC")
    sampling_period = timedelta(minutes=1)
    client = BinanceClient("", "")
    time_window = TimeWindow(start_time=datetime(2021, 5, 20, 6, 00),
        end_time=datetime(2021, 5, 21, 8, 00))
    candles = _download_historical_data_from_binance(time_window=time_window, trading_pair=trading_pair,
        sampling_period=sampling_period, client=client)
    print(candles)
    stock_data = StockData(candles, trading_pair)
    save_to_disk(stock_data, os.path.join(definitions.TEST_DATA_DIR, "test_data_long.dill"))


if __name__ == '__main__':
    _download_test_data_from_binance()
