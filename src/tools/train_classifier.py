import os
from datetime import timedelta, datetime
from typing import List, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from binance.client import Client
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix

from src import definitions
from src.backtesting_logic.logic import Buy, Sell, Hold
from src.containers.candle import Candle
from src.containers.stock_data import StockData
from src.containers.time_windows import TimeWindow
from src.containers.trade_helper import generate_trading_signal_from_prediction, generate_trading_signals_from_array
from src.live_logic.parameters import LiveParameters
from src.live_logic.portfolio import Portfolio
from src.live_logic.technical_indicator import TechnicalIndicator, AutoCorrelationTechnicalIndicator
from src.mixins.save_load_mixin import DillSaveLoadMixin
from src.plotting.plot_candles import custom_plot
from src.tools.classifier_helpers import extract_indicators_from_stock_data, \
    get_training_labels, convert_to_pandas, extract_indicator_from_candle
from src.tools.downloader import load_stock_data


class TradingClassifier(DillSaveLoadMixin):
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

    @property
    def sklearn_classifier(self):
        return self._sklearn_classifier

    def _precondition(self, stock_data_training: StockData):
        training_data = extract_indicators_from_stock_data(stock_data_training,
                                                           self._list_of_technical_indicators)
        self._predictors, self._labels = convert_to_pandas(predictors=training_data,
                                                           labels=get_training_labels(stock_data_training))

    def train(self, stock_data_training: StockData):
        self._precondition(stock_data_training)
        self._sklearn_classifier.fit(
            X=self._predictors.as_matrix(),
            y=self._labels.as_matrix())

    def predict(self, stock_data: StockData):
        '''Return Buy/Sell/Hold prediction for a stock dataset.
        stock_data.candles must be of length at least self._maximum_lag'''
        testing_data = extract_indicators_from_stock_data(stock_data, self._list_of_technical_indicators)
        predictors, _ = convert_to_pandas(predictors=testing_data, labels=None)
        # TODO: Implement trading based on probabilities
        predicted_values = self._sklearn_classifier.predict(predictors)
        return predicted_values

    def predict_one(self, candle: Candle):
        if self._is_candles_requirement_satisfied:
            print("Checkpoint........")
            testing_data = extract_indicator_from_candle(candle, self._list_of_technical_indicators)
            predictors, _ = convert_to_pandas(predictors=testing_data, labels=None)
            predicted_values = self._sklearn_classifier.predict(predictors)
            return predicted_values

    def append_new_candle(self, candle: Candle):
        self._stock_data_live.append_new_candle(candle)
        if len(self._stock_data_live.candles) >= self._maximum_lag:
            self._is_candles_requirement_satisfied = True

    def __str__(self):
        return "Trading Pair: {}, Technical Indicators: {}".format(self._stock_data_live.security,
                                                                   self._list_of_technical_indicators)

        # def save_to_disk(self, path_to_file: str):
        #     with open(os.path.join(definitions.DATA_DIR, path_to_file), 'wb') as outfile:
        #         json.dump(self, outfile)
        #
        # @staticmethod
        # def load_from_disk(path_to_file: str):
        #     with open(os.path.join(definitions.DATA_DIR, path_to_file), 'rb') as outfile:
        #         obj = json.load(outfile)
        #     return obj


def generate_reference_portfolio(initial_capital, parameters, stock_data_testing_set):
    reference_portfolio = Portfolio(initial_capital=initial_capital,
                                    trade_amount=parameters.trade_amount)
    training_signals = get_training_labels(stock_data_testing_set)
    for signal in training_signals:
        reference_portfolio.update(signal)
    reference_portfolio.compute_performance()
    return reference_portfolio, training_signals


def generate_predicted_portfolio(initial_capital: int, parameters: LiveParameters,
                                 stock_data_testing_set: StockData, classifier: TradingClassifier):
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
    trading_pair = "NEOBTC"

    training_time_window = TimeWindow(
        start_time=datetime(2018, 5, 1),
        end_time=datetime(2018, 5, 13)
    )

    stock_data_training_set = load_stock_data(training_time_window, trading_pair, Client.KLINE_INTERVAL_1MINUTE)
    testing_time_window = TimeWindow(start_time=datetime(2018, 9, 2), end_time=datetime(2018, 9, 3))

    stock_data_testing_set = load_stock_data(testing_time_window, trading_pair, Client.KLINE_INTERVAL_1MINUTE)

    list_of_technical_indicators = [
        # AutoCorrelationTechnicalIndicator(Candle.get_volume, 24),
        # AutoCorrelationTechnicalIndicator(Candle.get_close_price, 4),
        AutoCorrelationTechnicalIndicator(Candle.get_close_price, 2),
        # PPOTechnicalIndicator(Candle.get_close_price, 5, 1),
        # PPOTechnicalIndicator(Candle.get_close_price, 10, 4),
        # PPOTechnicalIndicator(Candle.get_close_price, 20, 1),
        # PPOTechnicalIndicator(Candle.get_close_price, 30, 10),
        # PPOTechnicalIndicator(Candle.get_number_of_trades, 5, 1),
        # PPOTechnicalIndicator(Candle.get_number_of_trades, 10, 2),
        # PPOTechnicalIndicator(Candle.get_number_of_trades, 15, 3),
        # PPOTechnicalIndicator(Candle.get_number_of_trades, 20, 1) / PPOTechnicalIndicator(Candle.get_volume, 20, 5),
        # PPOTechnicalIndicator(Candle.get_volume, 5, 1),
    ]
    sklearn_classifier = RandomForestClassifier(n_estimators=100, criterion="entropy", class_weight="balanced")
    training_ratio = 0.5  # this is not enabled
    my_classifier = TradingClassifier(trading_pair, list_of_technical_indicators,
                                      sklearn_classifier, training_ratio)
    my_classifier.train(stock_data_training_set)
    my_classifier.save_to_disk(os.path.join(definitions.DATA_DIR, "classifier.dill"))

    # predictions = my_classifier.predict(stock_data_testing_set, list_of_technical_indicators)
    parameters = LiveParameters(
        update_period=timedelta(minutes=1),
        trade_amount=100,
        sleep_time=0
    )
    # stock_data_testing_set = stock_data_training_set

    initial_capital = 5
    reference_portfolio, reference_signals = generate_reference_portfolio(
        initial_capital, parameters, stock_data_testing_set)
    predicted_portfolio, predicted_signals = generate_predicted_portfolio(
        initial_capital, parameters, stock_data_testing_set, my_classifier)

    custom_plot(portfolio=predicted_portfolio, strategy=None, title='Prediction portfolio_df')
    custom_plot(portfolio=reference_portfolio, strategy=None, title='Reference portfolio_df')
    print(my_classifier.sklearn_classifier.feature_importances_)
    conf_matrix = compute_confusion_matrix(reference_signals, predicted_signals)
    accuracy = np.sum(np.diag(conf_matrix)) / np.sum(conf_matrix)
    print(conf_matrix)
    print(accuracy)
    plt.show()


def run_trained_classifier():
    testing_time_window = TimeWindow(start_time=datetime(2018, 5, 2), end_time=datetime(2018, 5, 5))

    trading_pair = "XRPBTC"
    stock_data_testing_set = load_stock_data(testing_time_window, trading_pair, Client.KLINE_INTERVAL_1MINUTE)

    parameters = LiveParameters(
        update_period=timedelta(minutes=1),
        trade_amount=100,
        sleep_time=0
    )
    my_classifier = TradingClassifier.load_from_disk(os.path.join(definitions.DATA_DIR, "classifier.dill"))

    initial_capital = 5
    reference_portfolio, reference_signals = generate_reference_portfolio(
        initial_capital, parameters, stock_data_testing_set)
    predicted_portfolio, predicted_signals = generate_predicted_portfolio(
        initial_capital, parameters, stock_data_testing_set, my_classifier)

    custom_plot(portfolio=predicted_portfolio, strategy=None, title='Prediction portfolio_df')
    custom_plot(portfolio=reference_portfolio, strategy=None, title='Reference portfolio_df')
    print(my_classifier.sklearn_classifier.feature_importances_)
    conf_matrix = compute_confusion_matrix(reference_signals, predicted_signals)
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
    # run_trained_classifier()
