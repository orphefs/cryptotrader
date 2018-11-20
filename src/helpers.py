# function computes SMA and EMA based on period fed to it
import hashlib
from datetime import timedelta
from typing import List, Callable

from src.containers.candle import Candle
from src.containers.time_series import TimeSeries
from src.containers.stock_data import StockData
from src.type_aliases import Hash


def simple_moving_average(SMA, EMA, p, closing_prices, closing_price_averaging_period):

    for i in range(p - 1, len(closing_prices)):
        M = 2 / (p + 1)
        SMA.append((sum(closing_prices[i - p + 1:i + 1])) / p)
        EMA.append((closing_prices[i] - (EMA[i - 1])) * M + EMA[i - 1])

    return SMA, EMA


def extract_time_series_from_stock_data(stock_data: StockData) -> TimeSeries:
    return TimeSeries(y=[candle.get_close_price() for candle in stock_data.candles],
                      x=[candle.get_close_time_as_datetime() for candle in stock_data.candles])


def convert_to_timedelta(time_val):
    num = int(time_val[:-1])
    if time_val.endswith('s'):
        return timedelta(seconds=num)
    elif time_val.endswith('m'):
        return timedelta(minutes=num)
    elif time_val.endswith('h'):
        return timedelta(hours=num)
    elif time_val.endswith('d'):
        return timedelta(days=num)


def is_equal(list_1: List, list_2: List) -> bool:
    if len(list_1) != len(list_2):
        return False
    if len(list_1) == 0 or len(list_2) == 0:
        return False
    return all([item_1 == item_2 for item_1, item_2 in zip(list_1, list_2)])


def is_time_difference_larger_than_threshold(current_candle: Candle, previous_candle: Candle, threshold: timedelta,
                                             time_getter_callback: Callable):
    return time_getter_callback(current_candle) - time_getter_callback(previous_candle) > threshold


def get_capital_from_account(capital_security: str) -> float:
    return 5.0


def generate_hash(*args) -> Hash:
    training_hash = hashlib.md5()
    for token in args:
        training_hash.update(str(token).encode("utf-8"))
    return training_hash.hexdigest()