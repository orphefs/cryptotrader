import os

import numpy as np
import pytest

from src.classification.trading_classifier import TradingClassifier
from src.containers.stock_data import StockData, load_from_disk
from src.definitions import TEST_DATA_DIR
from src.helpers import is_equal


def load_classifier() -> TradingClassifier:
    classifier = TradingClassifier.load_from_disk(os.path.join(TEST_DATA_DIR, "classifier.dill"))
    return classifier


def load_stock_data() -> StockData:
    stock_data = load_from_disk(os.path.join(TEST_DATA_DIR, "test_data.dill"))
    return stock_data


def test_repeatability_of_classifier_predictions():

    stock_data = load_stock_data()

    predicted_values = []
    for i in range(10):
        classifier = []
        classifier = load_classifier()
        result = classifier.predict(stock_data)
        print(result)
        predicted_values.append(result)

    assert 9 == sum([is_equal(previous_answer, next_answer) for previous_answer, next_answer in
                         zip(predicted_values[0:], predicted_values[1:])])
