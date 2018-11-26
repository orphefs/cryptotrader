from datetime import timedelta
from typing import Tuple, List

from src.containers.candle import Candle
from src.containers.stock_data import StockData
from src.containers.time_series import TimeSeries
from src.containers.time_windows import TimeWindow, Date
from src.containers.trading_pair import TradingPair


class DownloadingError(RuntimeError):
    pass


def _generate_file_name(time_window: TimeWindow, security: TradingPair, api_interval_callback: str) -> str:
    return ('local_data_' + Date(time_window.start_datetime).as_string().replace(" ", "_") + '_' +
            Date(time_window.end_datetime).as_string().replace(" ",
                                                               "_") + '_' + str(
                security) + '_' + api_interval_callback + ".dill").replace(
        " ", "_")


def _serve_windowed_stock_data(data: StockData, iteration: int, window_start: int) -> Tuple[int, StockData]:
    iteration += 1
    return iteration, StockData(data.candles[iteration - window_start:iteration], data.security)


def _calculate_sampling_rate_of_stock_data(stock_data: StockData) -> float:
    return TimeSeries(x=[candle.get_close_time_as_datetime() for candle in stock_data.candles],
                      y=[candle.get_close_price() for candle in stock_data.candles]).sampling_rate


def _finetune_time_window(candles: List[Candle], time_window: TimeWindow):
    new_candles = [candle for candle in
                   candles if
                   time_window.start_datetime - timedelta(minutes=1)
                   <= candle.get_close_time_as_datetime() <
                   time_window.end_datetime + timedelta(minutes=1)]
    return new_candles