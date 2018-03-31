import os
from collections import defaultdict
from typing import List

import numpy as np
from sklearn.ensemble import RandomForestClassifier

import definitions
from backtesting_logic.logic import Buy, Sell
from containers.data_point import PricePoint
from containers.stock_data import StockData
from live_logic.technical_indicator import AutoCorrelationTechnicalIndicator, MovingAverageTechnicalIndicator, \
    TechnicalIndicator
from tools.downloader import load_from_disk


def _extract_indicators_from_stock_data(stock_data, list_of_technical_indicators):
    training_data = defaultdict(list)
    for candle in stock_data.candles:
        for indicator in list_of_technical_indicators:
            indicator.update(candle)
            training_data[indicator.__name__].append(indicator.result)
    return training_data


def _get_training_labels(stock_data: StockData):
    training_labels = []
    for current_candle, next_candle in list(zip(stock_data.candles[0:], stock_data.candles[1:])):

        if next_candle.get_close_price() > current_candle.get_close_price():
            training_labels.append(Buy(-1, PricePoint(value=current_candle.get_close_price(),
                                                      date_time=current_candle.get_close_time_as_datetime())))
        else:
            training_labels.append(Sell(1, PricePoint(value=current_candle.get_close_price(),
                                                      date_time=current_candle.get_close_time_as_datetime())))
    return training_labels


def _convert_to_numpy_array(training_data: defaultdict(list)):
    my_list = []
    for key, item in training_data.items():
        my_list.append(item)

    array = np.array(my_list)
    return array


class TradingClassifier:
    def __init__(self,
                 stock_data: StockData,
                 list_of_technical_indicators: List[TechnicalIndicator],
                 sklearn_classifier: RandomForestClassifier,
                 training_ratio: float):
        self._stock_data = stock_data
        self._list_of_technical_indicators = list_of_technical_indicators
        self._sklearn_classifier = sklearn_classifier
        self._training_ratio = training_ratio
        self._predictors = np.ndarray
        self._labels = np.ndarray

    def precondition(self):
        training_data = _extract_indicators_from_stock_data(self._stock_data, self._list_of_technical_indicators)
        self._predictors = _convert_to_numpy_array(training_data)
        self._labels = _get_training_labels(self._stock_data)

    def train(self):
        self._sklearn_classifier.fit(X=self._predictors, y=self._labels)

    def predict(self):
        pass


def main():
    stock_data = load_from_disk(
        os.path.join(definitions.DATA_DIR, "local_data_15_Jan,_2018_01_Mar,_2018_XRPBTC.dill"))

    list_of_technical_indicators = [AutoCorrelationTechnicalIndicator('close_price', 5),
                                    MovingAverageTechnicalIndicator('close_price', 5)]

    my_classifier = TradingClassifier(stock_data, list_of_technical_indicators, sklearn_classifier,
                                      training_ratio)

    pass


if __name__ == "__main__":
    main()
