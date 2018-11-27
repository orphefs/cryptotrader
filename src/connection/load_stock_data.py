import logging
import os
from datetime import timedelta, datetime
from typing import Optional, Union


from src import definitions
from src.connection.download_historical_data import _download_historical_data_from_exchange
from src.connection.helpers import _generate_file_name
from src.containers.stock_data import StockData, save_to_disk, load_from_disk
from src.containers.time_windows import TimeWindow
from src.containers.trading_pair import TradingPair
from src.type_aliases import BinanceClient, CobinhoodClient


def load_stock_data(time_window: TimeWindow, trading_pair: TradingPair,
                    sampling_period: timedelta,
                    client: Optional[Union[BinanceClient, CobinhoodClient]]) -> StockData:
    path_to_file = os.path.join(definitions.DATA_DIR,
                                _generate_file_name(time_window, trading_pair, str(sampling_period)))
    if client is None:
        client = BinanceClient("", "")
    if os.path.isfile(path_to_file):
        stock_data = load_from_disk(path_to_file)
    else:
        logging.info("Downloading stock data for {} from {} to {}".format(trading_pair, time_window.start_datetime,
                                                                          time_window.end_datetime))
        start = datetime.now()
        # extended_time_window = copy.deepcopy(
        #     time_window).increment_end_time_by_one_day().decrement_start_time_by_one_day()
        candles = _download_historical_data_from_exchange(time_window, trading_pair, sampling_period, client)
        # candles = finetune_time_window(candles, time_window)
        stop = datetime.now()
        logging.info("Elapsed download time: {}".format(stop - start))
        # for candle in candles:
        #     print("{}\n".format(candle))
        stock_data = StockData(candles, trading_pair)
        save_to_disk(stock_data, path_to_file)
    return stock_data


