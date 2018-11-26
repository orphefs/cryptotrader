import os

import numpy as np
import pytest

from src.classification.trading_classifier import TradingClassifier
from src.containers.stock_data import StockData, load_from_disk
from src.definitions import TEST_DATA_DIR
from src.helpers import is_equal


@pytest.fixture()
def load_classifier() -> TradingClassifier:
    classifier = TradingClassifier.load_from_disk(os.path.join(TEST_DATA_DIR, "classifier.dill"))
    return classifier


@pytest.fixture()
def load_stock_data() -> StockData:
    stock_data = load_from_disk(os.path.join(TEST_DATA_DIR, "test_data.dill"))
    return stock_data



def test_convert_to_pandas():
    pass
