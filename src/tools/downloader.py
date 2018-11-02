import copy
import os
from datetime import datetime, timedelta
from typing import List, Tuple

import dill
from binance.client import Client

from src import definitions
from src.containers.candle import Candle
from src.containers.stock_data import StockData
from src.containers.time_series import TimeSeries
from src.containers.time_windows import TimeWindow, Date
from src.tools.connection_handling import retry_on_network_error
from src.type_aliases import Security


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


def download_backtesting_data(time_window: TimeWindow, security: Security, api_interval_callback: str) -> List[Candle]:
    client = Client("", "")
    klines = client.get_historical_klines(security, api_interval_callback,
                                          Date(time_window.start_datetime).as_string(),
                                          Date(time_window.end_datetime).as_string())

    return Candle.from_list_of_klines(klines)


# TODO: handle case of missing data due to broken connection

@retry_on_network_error
def download_live_data(client: Client, security: Security, api_interval_callback: str, lags: int) -> List[Candle]:
    klines = client.get_historical_klines(security, api_interval_callback, "{} minutes ago GMT".format(lags))
    return Candle.from_list_of_klines(klines)


def mock_download_live_data(client: Client, security: Security, api_interval_callback: str, lags: int) -> List[Candle]:
    klines = client.get_historical_klines(security, api_interval_callback, "{} minutes ago GMT".format(lags))
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

def generate_file_name(time_window: TimeWindow, security: Security, api_interval_callback: str) -> str:
    return ('local_data_' + Date(time_window.start_datetime).as_string().replace(" ", "_") + '_' +
            Date(time_window.end_datetime).as_string().replace(" ",
                                                               "_") + '_' + security + '_' + api_interval_callback + ".dill").replace(
        " ", "_")


def load_stock_data(time_window: TimeWindow, security: str, api_interval_callback: str):
    path_to_file = os.path.join(definitions.DATA_DIR, generate_file_name(time_window, security, api_interval_callback))
    if os.path.isfile(path_to_file):
        stock_data = load_from_disk(path_to_file)
    else:
        start = datetime.now()
        extended_time_window = copy.deepcopy(
            time_window).increment_end_time_by_one_day().decrement_start_time_by_one_day()
        candles = download_backtesting_data(extended_time_window, security, api_interval_callback)
        candles = finetune_time_window(candles, time_window)
        stop = datetime.now()
        print("Elapsed download time: {}".format(stop - start))
        for candle in candles:
            print("{}\n".format(candle))
        stock_data = StockData(candles, security)
        save_to_disk(stock_data, path_to_file)
    return stock_data


def download_test_data():
    security = "XRPBTC"
    time_window = TimeWindow(start_time=datetime(2018, 5, 20, 6, 00),
                             end_time=datetime(2018, 5, 21, 8, 00))
    candles = download_backtesting_data(time_window, security, Client.KLINE_INTERVAL_1MINUTE)[-5:]
    print(candles)
    stock_data = StockData(candles, security)
    save_to_disk(stock_data, os.path.join(definitions.DATA_DIR, "test_data.dill"))


if __name__ == '__main__':
    download_test_data()
