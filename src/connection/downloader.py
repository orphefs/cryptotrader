import logging
import os
from datetime import datetime, timedelta
from typing import List, Tuple

import dill
from binance import client
from binance.enums import KLINE_INTERVAL_1MINUTE
from cobinhood_api import Cobinhood

dill.dill._reverse_typemap['ClassType'] = type

from binance.client import Client

from src import definitions
from src.containers.candle import Candle
from src.containers.stock_data import StockData
from src.containers.time_series import TimeSeries
from src.containers.time_windows import TimeWindow, Date
from src.connection.connection_handling import retry_on_network_error
from src.type_aliases import Exchange
from src.containers.trading_pair import TradingPair


def calculate_sampling_rate_of_stock_data(stock_data: StockData) -> float:
    return TimeSeries(x=[candle.get_close_time_as_datetime() for candle in stock_data.candles],
                      y=[candle.get_close_price() for candle in stock_data.candles]).sampling_rate


def finetune_time_window(candles: List[Candle], time_window: TimeWindow):
    new_candles = [candle for candle in
                   candles if
                   time_window.start_datetime - timedelta(minutes=1)
                   <= candle.get_close_time_as_datetime() <
                   time_window.end_datetime + timedelta(minutes=1)]
    return new_candles


def download_backtesting_data_from_binance(time_window: TimeWindow, security: TradingPair, api_interval_callback: str) -> \
        List[Candle]:
    client = Client("", "")
    klines = client.get_historical_klines(str(security), api_interval_callback,
                                          Date(time_window.start_datetime).as_string(),
                                          Date(time_window.end_datetime).as_string())

    return Candle.from_list_of_klines(klines, Exchange.BINANCE)


class DownloadingError(RuntimeError):
    pass


def download_backtesting_data_from_cobinhood(time_window: TimeWindow, security: TradingPair, api_interval_callback: str) -> \
        List[Candle]:
    client = Cobinhood()
    klines = client.chart.get_candles(trading_pair_id=security,
                                      start_time=round(time_window.start_datetime.timestamp() * 1000),
                                      end_time=round(time_window.end_datetime.timestamp() * 1000),
                                      timeframe=api_interval_callback,
                                      )
    if "error" in klines:
        raise DownloadingError("{}".format(klines["error"]["error_code"]))
    else:
        pass

    return Candle.from_list_of_klines(klines["result"]["candles"], Exchange.COBINHOOD)


# TODO: handle case of missing data due to broken connection

@retry_on_network_error
def download_live_data(client: Client, security: TradingPair, api_interval_callback: str, lags: int) -> List[Candle]:
    klines = client.get_historical_klines(str(security), api_interval_callback, "{} minutes ago GMT".format(lags))
    return Candle.from_list_of_klines(klines, source=Exchange.BINANCE)


def mock_download_live_data(client: Client, security: TradingPair, api_interval_callback: str, lags: int) -> List[Candle]:
    klines = client.get_historical_klines(str(security), api_interval_callback, "{} minutes ago GMT".format(lags))
    return Candle.from_list_of_klines(klines)


def serve_windowed_stock_data(data: StockData, iteration: int, window_start: int) -> Tuple[int, StockData]:
    iteration += 1
    return iteration, StockData(data.candles[iteration - window_start:iteration], data.security)


def save_to_disk(data: StockData, path_to_file: str):
    with open(path_to_file, 'wb') as outfile:
        dill.dump(data, outfile)


def load_from_disk(path_to_file: str) -> StockData:
    with open(path_to_file, 'rb') as outfile:
        data = dill.load(outfile)
    return data


# def replace_spaces_with_underscores(s: str) -> str:

def generate_file_name(time_window: TimeWindow, security: TradingPair, api_interval_callback: str) -> str:
    return ('local_data_' + Date(time_window.start_datetime).as_string().replace(" ", "_") + '_' +
            Date(time_window.end_datetime).as_string().replace(" ",
                                                               "_") + '_' + str(
                security) + '_' + api_interval_callback + ".dill").replace(
        " ", "_")


def load_stock_data(time_window: TimeWindow, security: TradingPair, api_interval_callback: str) -> StockData:
    path_to_file = os.path.join(definitions.DATA_DIR, generate_file_name(time_window, security, api_interval_callback))
    if os.path.isfile(path_to_file):
        stock_data = load_from_disk(path_to_file)
    else:
        logging.info("Downloading stock data for {} from {} to {}".format(security, time_window.start_datetime,
                                                                          time_window.end_datetime))
        start = datetime.now()
        # extended_time_window = copy.deepcopy(
        #     time_window).increment_end_time_by_one_day().decrement_start_time_by_one_day()
        candles = download_backtesting_data_from_binance(time_window, security, api_interval_callback)
        # candles = finetune_time_window(candles, time_window)
        stop = datetime.now()
        logging.info("Elapsed download time: {}".format(stop - start))
        # for candle in candles:
        #     print("{}\n".format(candle))
        stock_data = StockData(candles, security)
        save_to_disk(stock_data, path_to_file)
    return stock_data


def download_test_data_from_cobinhood():
    security = TradingPair("COB", "ETH")
    time_window = TimeWindow(start_time=datetime(2018, 5, 20, 6, 00),
                             end_time=datetime(2018, 5, 21, 8, 00))
    candles = download_backtesting_data_from_cobinhood(time_window, security, "1m")
    print(candles)
    stock_data = StockData(candles, security)
    save_to_disk(stock_data, os.path.join(definitions.DATA_DIR, "sample_data.dill"))


def download_test_data_from_binance():
    security = TradingPair("NEO", "BTC")
    time_window = TimeWindow(start_time=datetime(2018, 5, 20, 6, 00),
                             end_time=datetime(2018, 5, 21, 8, 00))
    candles = download_backtesting_data_from_binance(time_window, security, KLINE_INTERVAL_1MINUTE)[0:50]
    print(candles)
    stock_data = StockData(candles, security)
    save_to_disk(stock_data, os.path.join(definitions.TEST_DATA_DIR, "test_data_long.dill"))


if __name__ == '__main__':
    download_test_data_from_binance()
