import os

from binance.client import Client
from datetime import datetime

from typing import List, Any
import dill

import definitions
from containers.candle import Candle
from containers.time_windows import TimeWindow
from type_aliases import Security


def download_backtesting_data(time_window: TimeWindow, security: Security):
    client = Client("", "")
    klines = client.get_historical_klines(security, Client.KLINE_INTERVAL_1HOUR, time_window.start_time.as_string(),
                                          time_window.end_time.as_string())
    return Candle.from_list_of_klines(klines)


def save_to_disk(data: Any, path_to_file: str):
    with open(path_to_file, 'wb') as outfile:
        dill.dump(data, outfile)


def load_from_disk(path_to_file: str) -> Any:
    with open(path_to_file, 'rb') as outfile:
        data = dill.load(outfile)
    return data


# def replace_spaces_with_underscores(s: str) -> str:

def generate_file_name(time_window: TimeWindow, security: Security) -> str:
    return ('_data_' + time_window.start_time.as_string().replace(" ", "_") + '_' +
            time_window.end_time.as_string().replace(" ", "_") + '_' + security + ".dill").replace(" ", "_")


class StockData(object):
    def __init__(self, candles: List[Candle], security: Security):
        self._candles = candles
        self._security = security

    @property
    def candles(self):
        return self._candles

    @property
    def security(self):
        return self._security


if __name__ == '__main__':
    security = "LTCBTC"
    time_window = TimeWindow(start_time=datetime(2017, 10, 1),
                             end_time=datetime(2017, 10, 10))
    candles = download_backtesting_data(time_window, security)
    stock_data = StockData(candles, security)
    save_to_disk(stock_data, os.path.join(definitions.DATA_DIR, generate_file_name(time_window, security)))
