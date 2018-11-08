import os
from typing import List, Union

import numpy as np
import pandas as pd
import pytest

from src import definitions
from src.backtesting_logic.logic import Buy, Sell, Hold
from src.classification.classifier_helpers import replace_repeating_signals_with_holds
from src.connection.downloader import load_from_disk
from src.containers.candle import Candle
from src.containers.data_point import PricePoint, Price
from src.containers.stock_data import StockData
from src.containers.trade_helper import generate_trading_signals_from_array
from src.helpers import is_equal

predictions = [-1, -1, 1, 1, -1]
answers = [Buy,
           Hold,
           Sell,
           Hold,
           Buy]


@pytest.fixture()
def load_candle_data() -> List[Candle]:
    stock_data = load_from_disk(os.path.join(definitions.TEST_DATA_DIR, "test_data.dill"))
    return stock_data.candles


def create_mock_signals_from_candles(candles: List[Candle]) -> List[Union[Buy, Sell]]:
    return generate_trading_signals_from_array(signals=predictions,
                                               stock_data=StockData(candles=candles, security="TEST"))


def initialize_signals() -> List[Union[Buy, Sell]]:
    candles = load_candle_data()
    signals = create_mock_signals_from_candles(candles)
    return signals


def test_replace_repeating_signals_with_holds():
    signals = initialize_signals()
    cleaned_up_signals = replace_repeating_signals_with_holds(signals)
    assert is_equal(list_1=[type(signal) for signal in cleaned_up_signals],
                    list_2=answers)
