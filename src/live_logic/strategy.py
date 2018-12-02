from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Dict, Union

from dill import dill

from src.externals.rolling_statistics.python.rolling_stats import RollingMean
from src.containers.signal import SignalBuy, SignalSell, SignalHold
from src.containers.candle import Candle
from src.containers.data_point import PricePoint
from src.containers.stock_data import StockData
from src.containers.time_series import TimeSeries
from src.live_logic.parameters import LiveParameters, ClassifierParameters


def _convert_sma_period_to_no_of_samples(sma_period: timedelta, update_period: timedelta) -> int:
    return int(sma_period / update_period)


def load_from_file(path_to_file: str) -> ClassifierParameters:
    with open(path_to_file, 'rb') as infile:
        parameters = dill.load(infile)
    return parameters


class LiveStrategy(ABC):
    @abstractmethod
    def insert_new_data(self, candle: Candle):
        raise NotImplementedError

    @abstractmethod
    def generate_trading_signal(self) -> Union[SignalBuy, SignalSell, SignalHold]:
        raise NotImplementedError


class SMAStrategy(LiveStrategy):
    def __init__(self, parameters: LiveParameters):
        self._data = Dict
        self._stock_data = StockData
        self._trading_signals = []
        self._parameters = parameters
        self._time_series = TimeSeries
        self._current_candle = Candle
        self._short_sma_computer = RollingMean(
            _convert_sma_period_to_no_of_samples(parameters.short_sma_period, parameters.update_period))
        self._short_sma = TimeSeries()
        self._long_sma_computer = RollingMean(
            _convert_sma_period_to_no_of_samples(parameters.long_sma_period, parameters.update_period))
        self._long_sma = TimeSeries()
        self._bought = False
        self._last_buy_price = 0.0

    def insert_new_data(self, candle):
        self._current_candle = candle
        self._update_moving_averages()

    def generate_trading_signal(self) -> Union[SignalBuy, SignalSell, SignalHold]:

        current_price = self._current_candle.get_close_price()
        current_time = self._current_candle.get_close_time_as_datetime()

        if self._is_sma_crossing_from_below():
            if self._bought:
                return SignalHold(signal=0, price_point=PricePoint(value=current_price, date_time=current_time))

            elif not self._bought:
                self._bought = True
                self._last_buy_price = current_price
                return SignalBuy(signal=-1, price_point=PricePoint(value=current_price, date_time=current_time))

            else:
                return SignalHold(signal=0, price_point=PricePoint(value=current_price, date_time=current_time))

        elif self._is_sma_crossing_from_above():
            if self._bought:  # and current_price > self._last_buy_price:
                self._bought = False
                return SignalSell(signal=1, price_point=PricePoint(value=current_price, date_time=current_time))

            elif not self._bought:
                return SignalHold(signal=0, price_point=PricePoint(value=current_price, date_time=current_time))

            else:
                return SignalHold(signal=0, price_point=PricePoint(value=current_price, date_time=current_time))

        else:
            return SignalHold(signal=0, price_point=PricePoint(value=current_price, date_time=current_time))

    def _is_sma_crossing_from_below(self):
        return (self._short_sma[-2] < self._long_sma[-2]) and (self._short_sma[-1] > self._long_sma[-1])

    def _is_sma_crossing_from_above(self):
        return (self._short_sma[-2] > self._long_sma[-2]) and (self._short_sma[-1] < self._long_sma[-1])

    def _is_current_price_higher_than_last_buy(self, current_price: float):
        return current_price > self._last_buy_price

    def _extract_time_series_from_stock_data(self, stock_data: StockData):
        self._stock_data = stock_data
        self._time_series = TimeSeries(
            x=[candle.get_close_time_as_datetime() for candle in stock_data.candles],
            y=[candle.get_close_price() for candle in stock_data.candles])

    def _update_moving_averages(self):
        self._short_sma_computer.insert_new_sample(self._current_candle.get_close_price())
        self._long_sma_computer.insert_new_sample(self._current_candle.get_close_price())
        s1 = TimeSeries(y=[self._short_sma_computer.mean],
                        x=[self._current_candle.get_close_time_as_datetime()])
        s2 = TimeSeries(y=[self._long_sma_computer.mean],
                        x=[self._current_candle.get_close_time_as_datetime()])
        self._short_sma = self._short_sma.append(s1)
        self._long_sma = self._long_sma.append(s2)


class ClassifierStrategy(LiveStrategy):
    def __init__(self, parameters: ClassifierParameters):
        self._parameters = parameters
        self._candles = []

    def insert_new_data(self, candle):
        self._current_candle = candle
        self._update_classifier()

    def generate_trading_signal(self) -> Union[SignalBuy, SignalSell, SignalHold]:
        # classifier predict and output Signal
        pass

    def set_mode(self, mode: str):
        self._mode = mode

    @staticmethod
    def from_trained_classifier(path_to_config: str):
        parameters = load_from_file(path_to_config)
        cs = ClassifierStrategy(parameters)
        cs.set_mode('predict')
        return cs
