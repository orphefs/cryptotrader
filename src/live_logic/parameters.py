from datetime import timedelta
from typing import List

from live_logic.technical_indicator import TechnicalIndicator


class Parameters:
    pass


class LiveParameters(Parameters):
    def __init__(self, short_sma_period: timedelta,
                 long_sma_period: timedelta, update_period: timedelta,
                 trade_amount: int,
                 sleep_time: int):
        self.short_sma_period = short_sma_period
        self.long_sma_period = long_sma_period
        self.update_period = update_period
        self.trade_amount = trade_amount
        self.sleep_time = sleep_time


class ClassifierParameters(Parameters):
    def __init__(self, list_of_technical_indicators: List[TechnicalIndicator]):
        self._list_of_technical_indicators = list_of_technical_indicators
