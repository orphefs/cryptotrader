from typing import List, Union

import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix

from src.backtesting_logic.logic import Buy, Sell, Hold
from src.classification.helpers import get_training_labels
from src.classification.trading_classifier import TradingClassifier
from src.containers.portfolio import Portfolio
from src.containers.stock_data import StockData
from src.containers.trade_helper import generate_trading_signal_from_prediction, generate_trading_signals_from_array


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


def timeshift_predictions(labels: pd.Series) -> pd.Series:
    # Shift label by 1 minute to associate previous prediction with next price move - Experimental
    ser = pd.Series(np.roll(labels, -1))
    ser.index += 1
    return ser


def generate_reference_portfolio(initial_capital, parameters, stock_data_testing_set):
    reference_portfolio = Portfolio(initial_capital=initial_capital,
                                    trade_amount=parameters.trade_amount)
    training_signals = get_training_labels(stock_data_testing_set)
    for signal in training_signals:
        reference_portfolio.update(signal)
    reference_portfolio.compute_performance()
    return reference_portfolio, training_signals


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
    predictions = np.roll(np.sign(np.diff(predictions)), 1)
    # predictions = np.roll(predictions, 7)
    predictions[0] = - predictions[0]

    signals = generate_trading_signals_from_array(predictions, stock_data_testing_set)
    # signals = filter_signals
    for signal in signals:
        if signal is not None:
            predicted_portfolio.update(signal)
            predicted_signals.append(signal)
    return classifier, predicted_portfolio, predicted_signals