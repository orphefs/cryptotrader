import os
from collections import defaultdict
from typing import List, Type

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

import definitions
from backtesting_logic.logic import Buy, Sell
from containers.candle import Candle
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
            training_data[type(indicator).__name__].append(indicator.result)
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


def _convert_to_pandas(predictors: defaultdict(list), labels: list = None):
    if labels is not None:
        lst = [np.nan] + [trading_signal.signal for trading_signal in labels]
    else:
        lst = [0] * len(list(predictors.values())[0])
    predictors['labels'] = lst
    df = pd.DataFrame(predictors).dropna()
    return df[[col for col in df.columns if col != 'labels']], df['labels']


class TradingClassifier:
    def __init__(self,
                 stock_data: StockData,
                 list_of_technical_indicators: List[TechnicalIndicator],
                 sklearn_classifier: Type[RandomForestClassifier],
                 training_ratio: float):
        self._stock_data = stock_data
        self._list_of_technical_indicators = list_of_technical_indicators
        self._sklearn_classifier = sklearn_classifier()
        self._training_ratio = training_ratio
        self._predictors = np.ndarray
        self._labels = np.ndarray

    def precondition(self):
        training_data = _extract_indicators_from_stock_data(self._stock_data, self._list_of_technical_indicators)
        self._predictors, self._labels = _convert_to_pandas(predictors=training_data,
                                                            labels=_get_training_labels(self._stock_data))

    def train(self):
        self._sklearn_classifier.fit(
            X=self._predictors.as_matrix(),
            y=self._labels.as_matrix())

    def predict(self, stock_data: StockData, list_of_technical_indicators: List[TechnicalIndicator]):
        testing_data = _extract_indicators_from_stock_data(stock_data, list_of_technical_indicators)
        predictors, _ = _convert_to_pandas(predictors=testing_data, labels=None)
        return self._sklearn_classifier.predict(predictors)


def main():
    stock_data_training_set = load_from_disk(
        os.path.join(definitions.DATA_DIR, "local_data_01_Oct,_2017_01_Mar,_2018_XRPBTC.dill"))
    stock_data_testing_set = load_from_disk(
        os.path.join(definitions.DATA_DIR, "local_data_02_Mar,_2018_10_Apr,_2018_XRPBTC.dill"))


    list_of_technical_indicators = [AutoCorrelationTechnicalIndicator(Candle.get_close_price, 5),
                                    MovingAverageTechnicalIndicator(Candle.get_close_price, 5)]
    sklearn_classifier = RandomForestClassifier
    training_ratio = 0.3

    my_classifier = TradingClassifier(stock_data_training_set, list_of_technical_indicators, sklearn_classifier,
                                      training_ratio)
    my_classifier.precondition()
    my_classifier.train()

    predictions = my_classifier.predict(stock_data_testing_set, list_of_technical_indicators)




if __name__ == "__main__":
    main()
