import os
from datetime import datetime
from typing import List, Tuple, Callable

import dill
from binance.client import Client

import definitions
from containers.candle import Candle
from containers.stock_data import StockData
from containers.time_series import TimeSeries
from containers.time_windows import TimeWindow
from type_aliases import Security


def calculate_sampling_rate_of_stock_data(stock_data: StockData) -> float:
    return TimeSeries(x=[candle.get_close_time_as_datetime() for candle in stock_data.candles],
                      y=[candle.get_close_price() for candle in stock_data.candles]).sampling_rate


def download_backtesting_data(time_window: TimeWindow, security: Security, api_interval_callback: str) -> List[Candle]:
    client = Client("", "")
    klines = client.get_historical_klines(security, api_interval_callback, time_window.start_time.as_string(),
                                          time_window.end_time.as_string())
    return Candle.from_list_of_klines(klines)


def download_live_data(client: Client, security: Security, api_interval_callback: str, lags: int) -> List[Candle]:
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

def generate_file_name(time_window: TimeWindow, security: Security) -> str:
    return ('local_data_' + time_window.start_time.as_string().replace(" ", "_") + '_' +
            time_window.end_time.as_string().replace(" ", "_") + '_' + security + ".dill").replace(" ", "_")


def download_save_load(time_window: TimeWindow, security: str):
    path_to_file = os.path.join(definitions.DATA_DIR, generate_file_name(time_window, security))
    if os.path.isfile(path_to_file):
        stock_data = load_from_disk(path_to_file)
    else:
        start = datetime.now()
        candles = download_backtesting_data(time_window, security, Client.KLINE_INTERVAL_1MINUTE)
        stop = datetime.now()
        print("Elapsed download time: {}".format(stop - start))
        for candle in candles:
            print("{}\n".format(candle))
        stock_data = StockData(candles, security)
        save_to_disk(stock_data, path_to_file)
    return stock_data


if __name__ == '__main__':
    security = "XRPBTC"
    time_window = TimeWindow(start_time=datetime(2018, 3, 2),
                             end_time=datetime(2018, 4, 10))
    download_save_load(time_window, security)