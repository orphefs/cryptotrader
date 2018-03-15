from datetime import timedelta
from typing import List

import pandas as pd
import numpy as np

from backtesting_logic.logic import TradingSignal
from containers.time_series import TimeSeries
from containers.data_point import DataPoint


def rolling_mean(window_size: timedelta, time_series: TimeSeries):
    return pd.rolling_mean(time_series, window_size, min_periods=1)


def simple_moving_average(window_size: timedelta, time_series: TimeSeries) -> TimeSeries:
    window_size_int = window_size // time_series.sampling_rate
    weights = np.repeat(1.0, window_size_int) / window_size_int
    sma = np.convolve(np.array(time_series), weights, 'valid')
    return TimeSeries(x=time_series.index[window_size_int - 1:], y=sma)


def exponential_moving_average(window_size: timedelta, time_series: TimeSeries) -> TimeSeries:
    return None


def _generate_trading_signals_from_sma(
        original_time_series: TimeSeries,
        time_series_a: TimeSeries,
        time_series_b: TimeSeries) -> List[TradingSignal]:
    trading_signals = list(map(int, np.diff(np.where(time_series_a > time_series_b, 0.0, 1.0))))

    return [TradingSignal(trading_signals[i],
                          DataPoint(value=original_time_series[i], date_time=original_time_series.index[i]))
            for i, _ in enumerate(trading_signals)]