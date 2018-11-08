import os
from typing import List, Union

import numpy as np
import pandas as pd
import pytest

from src import definitions
from src.backtesting_logic.logic import Buy, Sell, Hold
from src.classification.classifier_helpers import replace_repeating_signals_with_holds
from src.classification.trading_classifier import TradingClassifier
from src.connection.downloader import load_from_disk
from src.containers.candle import Candle
from src.containers.data_point import PricePoint, Price
from src.containers.stock_data import StockData
from src.containers.trade_helper import generate_trading_signals_from_array
from src.definitions import TEST_DATA_DIR
from src.helpers import is_equal


@pytest.fixture()
def load_classifier() -> TradingClassifier:
    classifier = TradingClassifier.load_from_disk(os.path.join(TEST_DATA_DIR, "test_classifier.dill"))
    return classifier


@pytest.fixture()
def load_stock_data() -> StockData:
    stock_data = load_from_disk(os.path.join(TEST_DATA_DIR, "test_data.dill"))
    return stock_data


def test_repeatability_of_classifier_predictions():
    classifier = load_classifier()
    stock_data = load_stock_data()

    predicted_values = []
    for i in range(10):
        result = classifier.predict(stock_data)
        print(result)
        predicted_values.append(result)

    assert 9 == sum([is_equal(previous_answer, next_answer) for previous_answer, next_answer in
     zip(predicted_values[0:], predicted_values[1:])])
