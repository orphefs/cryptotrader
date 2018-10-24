from typing import List

from src.backtesting_logic.logic import _TradingSignal
from src.containers.candle import Candle
from src.containers.data_point import PricePoint
from src.containers.stock_data import StockData


def generate_trading_signals_from_array(signals: List[int], stock_data: StockData):
    return [generate_trading_signal_from_prediction(signal, candle)
            for signal, candle in zip(signals, stock_data.candles)]


def generate_trading_signal_from_prediction(prediction: int, candle: Candle):
    return _TradingSignal.from_integer_value(integer_value=prediction,
                                             price_point=PricePoint(value=candle.get_close_price(),
                                                                    date_time=candle.get_close_time_as_datetime()))
