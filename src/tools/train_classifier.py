import os
from collections import defaultdict
from datetime import timedelta, datetime
from typing import List, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix

import definitions
from backtesting_logic.logic import Buy, Sell, Hold
from containers.candle import Candle
from containers.data_point import PricePoint
from containers.stock_data import StockData
from containers.time_windows import TimeWindow
from containers.trade_helper import generate_trading_signal_from_prediction, generate_trading_signals_from_array
from live_logic.parameters import LiveParameters
from live_logic.portfolio import Portfolio
from live_logic.technical_indicator import TechnicalIndicator, AutoCorrelationTechnicalIndicator, PPOTechnicalIndicator
from mixins.save_load_mixin import SaveLoadMixin
from plotting.plot_candles import custom_plot
from tools.downloader import download_save_load


def _extract_indicators_from_stock_data(stock_data, list_of_technical_indicators):
    training_data = defaultdict(list)
    for candle in stock_data.candles:
        for indicator in list_of_technical_indicators:
            indicator.update(candle)
            indicator_key = str(indicator)
            training_data[indicator_key].append(indicator.result)
    return training_data


def _extract_indicator_from_candle(candle, list_of_technical_indicators):
    training_data = defaultdict(list)
    for indicator in list_of_technical_indicators:
        indicator.update(candle)
        indicator_key = str(indicator)
        training_data[indicator_key].append(indicator.result)
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


class TradingClassifier(SaveLoadMixin):
    def __init__(self, trading_pair: str,
                 list_of_technical_indicators: List[TechnicalIndicator],
                 sklearn_classifier: RandomForestClassifier,
                 training_ratio: float):
        self._stock_data_live = StockData(candles=[], security=trading_pair)
        self._list_of_technical_indicators = list_of_technical_indicators
        self._maximum_lag = max([ti.lags for ti in list_of_technical_indicators])
        self._is_candles_requirement_satisfied = False
        self._sklearn_classifier = sklearn_classifier
        self._training_ratio = training_ratio
        self._predictors = np.ndarray
        self._labels = np.ndarray

    def _precondition(self, stock_data_training: StockData):
        training_data = _extract_indicators_from_stock_data(stock_data_training,
                                                            self._list_of_technical_indicators)
        self._predictors, self._labels = _convert_to_pandas(predictors=training_data,
                                                            labels=_get_training_labels(stock_data_training))

    def train(self, stock_data_training: StockData):
        self._precondition(stock_data_training)
        self._sklearn_classifier.fit(
            X=self._predictors.as_matrix(),
            y=self._labels.as_matrix())

    def predict(self, stock_data: StockData):
        '''Return Buy/Sell/Hold prediction for a stock dataset.
        stock_data.candles must be of length at least self._maximum_lag'''
        testing_data = _extract_indicators_from_stock_data(stock_data, self._list_of_technical_indicators)
        predictors, _ = _convert_to_pandas(predictors=testing_data, labels=None)
        # TODO: Implement trading based on probabilities
        return self._sklearn_classifier.predict(predictors)

    def predict_one(self, candle: Candle):
        if self._is_candles_requirement_satisfied:
            testing_data = _extract_indicator_from_candle(candle,
                                                          self._list_of_technical_indicators)
            predictors, _ = _convert_to_pandas(predictors=testing_data, labels=None)
            return self._sklearn_classifier.predict(predictors)

    @property
    def sklearn_classifier(self):
        return self._sklearn_classifier

    def append_new_candle(self, candle: Candle):
        self._stock_data_live.append_new_candle(candle)
        if len(self._stock_data_live.candles) >= self._maximum_lag:
            self._is_candles_requirement_satisfied = True

    def __str__(self):
        return "Trading Pair: {}, Technical Indicators: {}".format(self._stock_data_live.security,
                                                                   self._list_of_technical_indicators)


def generate_reference_portfolio(initial_capital, parameters, stock_data_testing_set):
    reference_portfolio = Portfolio(initial_capital=initial_capital,
                                    trade_amount=parameters.trade_amount)
    training_signals = _get_training_labels(stock_data_testing_set)
    for signal in training_signals:
        reference_portfolio.update(signal)
    reference_portfolio.compute_performance()
    return reference_portfolio, training_signals


def generate_predicted_portfolio(initial_capital, parameters, stock_data_testing_set, classifier):
    predicted_portfolio = Portfolio(initial_capital=initial_capital,
                                    trade_amount=parameters.trade_amount)

    classifier, predicted_portfolio, predicted_signals = generate_all_signals_at_once(stock_data_testing_set,
                                                                                      classifier,
                                                                                      predicted_portfolio)
    predicted_portfolio.compute_performance()

    return predicted_portfolio, predicted_signals


def generate_reference_to_prediction_portfolio(initial_capital, parameters, stock_data_testing_set, classifier):
    reference_portfolio, training_signals = generate_reference_portfolio(
        initial_capital, parameters, stock_data_testing_set)
    predicted_portfolio, predicted_signals = generate_predicted_portfolio(
        initial_capital, parameters, stock_data_testing_set, classifier)
    return predicted_portfolio, predicted_signals, reference_portfolio, training_signals


def generate_signals_iteratively(stock_data: StockData, classifier: TradingClassifier, predicted_portfolio: Portfolio):
    predicted_signals = []
    for candle in stock_data.candles:
        classifier.append_new_candle(candle)
        prediction = classifier.predict_one(candle)
        if prediction is not None:
            signal = generate_trading_signal_from_prediction(prediction[0], candle)
            predicted_portfolio.update(signal)
            predicted_signals.append(signal)
    return classifier, predicted_portfolio, predicted_signals


def generate_all_signals_at_once(stock_data_testing_set, classifier, predicted_portfolio):
    predicted_signals = []
    predictions = classifier.predict(stock_data_testing_set)
    predictions = np.roll(predictions, -1)  # attach current prediction to the next candle by circular shift
    # do not repeat signal in a row
    predictions = np.sign(np.diff(predictions))  # TODO: rewrite this

    signals = generate_trading_signals_from_array(predictions, stock_data_testing_set)
    # signals = filter_signals
    for signal in signals:
        if signal is not None:
            predicted_portfolio.update(signal)
            predicted_signals.append(signal)
    return classifier, predicted_portfolio, predicted_signals


def main():
    trading_pair = "XRPBTC"

    training_time_window = TimeWindow(
        start_time=datetime(2018, 5, 10),
        end_time=datetime(2018, 5, 11)
    )

    stock_data_training_set = download_save_load(training_time_window, trading_pair)
    testing_time_window = TimeWindow(
        start_time=datetime(2018, 5, 12),
        end_time=datetime(2018, 5, 17)
    )

    stock_data_testing_set = download_save_load(testing_time_window, trading_pair)

    list_of_technical_indicators = [
        AutoCorrelationTechnicalIndicator(Candle.get_volume, 24),
        AutoCorrelationTechnicalIndicator(Candle.get_close_price, 4),
        AutoCorrelationTechnicalIndicator(Candle.get_close_price, 2),
        PPOTechnicalIndicator(Candle.get_close_price, 5, 1),
        PPOTechnicalIndicator(Candle.get_close_price, 10, 4),
        PPOTechnicalIndicator(Candle.get_close_price, 20, 1),
        PPOTechnicalIndicator(Candle.get_close_price, 30, 10),
        PPOTechnicalIndicator(Candle.get_number_of_trades, 5, 1),
        PPOTechnicalIndicator(Candle.get_number_of_trades, 10, 2),
        PPOTechnicalIndicator(Candle.get_number_of_trades, 15, 3),
        PPOTechnicalIndicator(Candle.get_number_of_trades, 20, 1) / PPOTechnicalIndicator(Candle.get_volume, 20, 5),
        PPOTechnicalIndicator(Candle.get_volume, 5, 1),
    ]
    sklearn_classifier = RandomForestClassifier(n_estimators=100, criterion="entropy", class_weight="balanced")

    training_ratio = 0.5  # this is not enabled
    # TODO: rename variable "security" to "trading pair"
    my_classifier = TradingClassifier(trading_pair, list_of_technical_indicators,
                                      sklearn_classifier, training_ratio)
    my_classifier.train(stock_data_training_set)
    my_classifier.save_to_disk(os.path.join(definitions.DATA_DIR, "classifier.dill"))

    # predictions = my_classifier.predict(stock_data_testing_set, list_of_technical_indicators)

    parameters = LiveParameters(
        update_period=timedelta(hours=1),
        trade_amount=1000,
        sleep_time=0
    )

    # stock_data_testing_set = stock_data_training_set

    initial_capital = 5
    reference_portfolio, training_signals = generate_reference_portfolio(
        initial_capital, parameters, stock_data_testing_set)
    predicted_portfolio, predicted_signals = generate_predicted_portfolio(
        initial_capital, parameters, stock_data_testing_set, my_classifier)

    custom_plot(portfolio=predicted_portfolio, strategy=None, title='Prediction portfolio')
    custom_plot(portfolio=reference_portfolio, strategy=None, title='Reference portfolio')
    print(my_classifier.sklearn_classifier.feature_importances_)
    conf_matrix = compute_confusion_matrix(training_signals, predicted_signals)
    accuracy = np.sum(np.diag(conf_matrix)) / np.sum(conf_matrix)
    print(conf_matrix)
    print(accuracy)
    plt.show()


def convert_signals_to_pandas(signals: List[Union[Buy, Sell, Hold]]) -> pd.DataFrame:
    return pd.DataFrame([{'Action': s.type.__name__, 'Timestamp': s.price_point.date_time} for s in signals])


def compute_confusion_matrix(training_signals: List[Union[Buy, Sell, Hold]],
                             predicted_signals: List[Union[Buy, Sell, Hold]]) -> np.ndarray:
    # TODO: Figure out why the two dfs are not merged properly
    # The wrong merging results in a wrong confusion matrix
    training_df = convert_signals_to_pandas(training_signals)
    predicted_df = convert_signals_to_pandas(predicted_signals)
    df = pd.merge_asof(training_df, predicted_df, on='Timestamp')
    clean_df = df.dropna()
    return confusion_matrix(y_true=clean_df.Action_x.as_matrix(), y_pred=clean_df.Action_y.as_matrix())


if __name__ == "__main__":
    main()
