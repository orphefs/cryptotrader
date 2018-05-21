# function computes SMA and EMA based on period fed to it
from datetime import timedelta

from src.containers.time_series import TimeSeries
from src.containers.stock_data import StockData


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
