import glob
import os
from datetime import timedelta
from typing import Tuple, List

from src.containers.candle import Candle
from src.containers.stock_data import StockData
from src.containers.time_series import TimeSeries
from src.containers.time_windows import TimeWindow, Date
from src.containers.trading_pair import TradingPair
from src.definitions import DATA_DIR


class DownloadingError(RuntimeError):
    pass


def _generate_file_name(time_window: TimeWindow, trading_pair: TradingPair, sampling_period: str, client_name: str) -> str:
    return ('local_data_' + Date(time_window.start_datetime).as_string().replace(" ", "_") + '_' +
            Date(time_window.end_datetime).as_string().replace(" ",
                                                               "_") + '_' + str(
                trading_pair) + '_' + sampling_period + "_" + client_name + ".dill").replace(
        " ", "_")


def _serve_windowed_stock_data(data: StockData, iteration: int, window_start: int) -> Tuple[int, StockData]:
    iteration += 1
    return iteration, StockData(data.candles[iteration - window_start:iteration], data.trading_pair)


def _calculate_sampling_rate_of_stock_data(stock_data: StockData) -> float:
    return TimeSeries(x=[candle.get_close_time_as_datetime() for candle in stock_data.candles],
                      y=[candle.get_close_price() for candle in stock_data.candles]).sampling_rate


def finetune_time_window(candles: List[Candle], time_window: TimeWindow):
    new_candles = [candle for candle in
                   candles if
                   time_window.start_datetime
                   <= candle.get_close_time_as_datetime() <
                   time_window.end_datetime ]
    return new_candles


def clear_downloaded_stock_data():
    files = glob.glob(os.path.join(DATA_DIR, "local_data*.dill"))
    for filename in files:
        try:
            os.remove(filename)
        except OSError:
            pass