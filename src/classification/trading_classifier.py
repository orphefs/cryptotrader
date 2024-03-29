from typing import List

import numpy as np
from sklearn.ensemble import RandomForestClassifier

from src.classification.helpers import extract_indicators_from_stock_data, convert_to_pandas, \
    get_training_labels, \
    extract_indicator_from_candle, timeshift_predictions
from src.containers.candle import Candle
from src.containers.stock_data import StockData
from src.containers.time_windows import TimeWindow
from src.feature_extraction.technical_indicator import TechnicalIndicator
from src.mixins.save_load_mixin import DillSaveLoadMixin, JsonSaveMixin
from src.type_aliases import Path
from src.containers.trading_pair import TradingPair

fudge_factor = 1000  # scaling factor to avoid inputting really tiny values to the classifier (may cause instabilities)


class TradingClassifier:
    def __init__(self, trading_pair: TradingPair,
                 list_of_technical_indicators: List[TechnicalIndicator],
                 sklearn_classifier: RandomForestClassifier,
                 training_time_window: TimeWindow,
                 training_ratio: float):
        self._stock_data_live = StockData(candles=[], trading_pair=trading_pair)
        self._list_of_technical_indicators = list_of_technical_indicators
        self._maximum_lag = max([ti.lags for ti in list_of_technical_indicators])
        self._is_candles_requirement_satisfied = False
        self._sklearn_classifier = sklearn_classifier
        self._training_ratio = training_ratio
        self._training_time_window = training_time_window
        self._predictors = np.ndarray
        self._labels = np.ndarray
        self._dill_save_load = DillSaveLoadMixin()
        self._json_save = JsonSaveMixin()

    @property
    def sklearn_classifier(self):
        return self._sklearn_classifier

    def erase_classifier_from_memory(self):
        delattr(self, "_sklearn_classifier")

    @property
    def training_time_window(self):
        return self._training_time_window

    def _precondition(self, stock_data_training: StockData):
        training_data = extract_indicators_from_stock_data(stock_data_training,
            self._list_of_technical_indicators)
        self._predictors, self._labels = convert_to_pandas(predictors=training_data,
            labels=get_training_labels(stock_data_training))

        self._labels = timeshift_predictions(self._labels)

    def train(self, stock_data_training: StockData):
        self._precondition(stock_data_training)
        self._sklearn_classifier.fit(
            X=self._predictors.values * fudge_factor,
            y=self._labels.values)

    def predict(self, stock_data: StockData):
        '''Return Buy/Sell/Hold prediction for a stock dataset.
        stock_data.candles must be of length at least self._maximum_lag'''
        testing_data = extract_indicators_from_stock_data(stock_data,
            self._list_of_technical_indicators)
        predictors, _ = convert_to_pandas(predictors=testing_data, labels=None)
        predictors *= fudge_factor
        # TODO: Implement trading based on probabilities
        predicted_values = self.sklearn_classifier.predict(predictors)
        return predicted_values

    def predict_one(self, candle: Candle):
        # if self._is_candles_requirement_satisfied:
        testing_data = extract_indicator_from_candle(candle, self._list_of_technical_indicators)
        predictors, _ = convert_to_pandas(predictors=testing_data, labels=None)
        predictors *= fudge_factor
        predicted_values = self._sklearn_classifier.predict(predictors)
        return predicted_values

    def append_new_candle(self, candle: Candle):
        self._stock_data_live.append_new_candle(candle)
        if len(self._stock_data_live.candles) >= self._maximum_lag:
            self._is_candles_requirement_satisfied = True

    def save_to_disk(self, path_to_file: Path):
        self._dill_save_load.save_to_disk(self, path_to_file)
        # self._json_save.save_to_disk(self, path_to_file) # TODO: saving a classifier to JSON does not make sense. Rethink this.

    @staticmethod
    def load_from_disk(path_to_file: Path):
        obj = DillSaveLoadMixin.load_from_disk(path_to_file)
        return obj

    def __str__(self):
        return "Trading Pair: {}, Technical Indicators: {}".format(self._stock_data_live.trading_pair,
            self._list_of_technical_indicators)
