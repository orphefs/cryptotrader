import logging
import os
from datetime import timedelta, datetime
from typing import Optional, Union

from binance.client import Client as BinanceClient
from cobinhood_api import Cobinhood as CobinhoodClient

from src import definitions
from src.connection.download_historical_data import _download_historical_data_from_exchange
from src.connection.helpers import _generate_file_name
from src.containers.stock_data import StockData, save_to_disk, load_from_disk
from src.containers.time_windows import TimeWindow
from src.containers.trading_pair import TradingPair


def load_stock_data(time_window: TimeWindow, security: TradingPair,
                    api_interval_callback: timedelta,
                    client: Optional[Union[BinanceClient, CobinhoodClient]]) -> StockData:
    path_to_file = os.path.join(definitions.DATA_DIR,
                                _generate_file_name(time_window, security, str(api_interval_callback)))
    if client is None:
        client = BinanceClient("", "")
    if os.path.isfile(path_to_file):
        stock_data = load_from_disk(path_to_file)
    else:
        logging.info("Downloading stock data for {} from {} to {}".format(security, time_window.start_datetime,
                                                                          time_window.end_datetime))
        start = datetime.now()
        # extended_time_window = copy.deepcopy(
        #     time_window).increment_end_time_by_one_day().decrement_start_time_by_one_day()
        candles = _download_historical_data_from_exchange(time_window, security, api_interval_callback, client)
        # candles = _finetune_time_window(candles, time_window)
        stop = datetime.now()
        logging.info("Elapsed download time: {}".format(stop - start))
        # for candle in candles:
        #     print("{}\n".format(candle))
        stock_data = StockData(candles, security)
        save_to_disk(stock_data, path_to_file)
    return stock_data


