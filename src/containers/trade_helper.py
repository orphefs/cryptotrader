from typing import List

from backtesting_logic.logic import _TradingSignal
from containers.candle import Candle
from containers.data_point import PricePoint
from containers.stock_data import StockData


def generate_trading_signals_from_array(signals: List[int], stock_data: StockData):

    return [_TradingSignal.from_signal_integer(signal_integer=signal, price_point=PricePoint(value=candle.get_close_price(),
                                                                      date_time=candle.get_close_time_as_datetime()))
            for signal, candle in zip(signals, stock_data.candles)]


def generate_trading_signal_from_prediction(prediction: int, candle: Candle):

    return _TradingSignal.from_signal_integer(signal_integer=prediction, price_point=PricePoint(value=candle.get_close_price(),
                                                                      date_time=candle.get_close_time_as_datetime()))
