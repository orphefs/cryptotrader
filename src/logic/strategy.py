from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Dict

from containers.time_series import TimeSeries
from logic.signal_processing import rolling_mean, _generate_trading_signals_from_sma
from tools.downloader import StockData


class BackTestingStrategy(ABC):
    @abstractmethod
    def prepare_data(self):
        pass

    @abstractmethod
    def generate_trading_signals(self):
        pass


class SMAStrategy(BackTestingStrategy):
    def __init__(self, stock_data: StockData):
        self._instrument = None
        self._candles = stock_data.candles
        self._security = stock_data.security
        self._data = Dict
        self._trading_signals = []

    def prepare_data(self):
        time_series = TimeSeries(
            x=[candle.get_time().close_time for candle in self._candles],
            y=[candle.get_price().close_price for candle in self._candles])
        self._data = {'time_series': time_series,
                      'sma_10': rolling_mean(window_size=timedelta(hours=10),
                                             time_series=time_series),
                      'sma_2': rolling_mean(window_size=timedelta(hours=2),
                                            time_series=time_series),
                      }

    def generate_trading_signals(self):
        self._trading_signals = _generate_trading_signals_from_sma(
            self._data['time_series'],
            self._data['sma_2'],
            self._data['sma_10'],
        )