from typing import List, Union, Tuple
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix

from src.containers.signal import SignalBuy, SignalSell, SignalHold
from src.classification.helpers import get_training_labels
from src.classification.trading_classifier import TradingClassifier
from src.containers.portfolio import Portfolio
from src.containers.stock_data import StockData, load_from_disk
from src.containers.trade_helper import generate_trading_signal_from_prediction, generate_trading_signals_from_array
from src.type_aliases import Path


def convert_signals_to_pandas(signals: List[Union[SignalBuy, SignalSell, SignalHold]]) -> pd.DataFrame:
    return pd.DataFrame([{'Action': s.type.__name__, 'Timestamp': s.price_point.date_time} for s in signals])


def compute_confusion_matrix(training_signals: List[Union[SignalBuy, SignalSell, SignalHold]],
                             predicted_signals: List[Union[SignalBuy, SignalSell, SignalHold]]) -> np.ndarray:
    # TODO: Figure out why the two dfs are not merged properly
    # The wrong merging results in a wrong confusion matrix
    training_df = convert_signals_to_pandas(training_signals)
    predicted_df = convert_signals_to_pandas(predicted_signals)
    df = pd.merge_asof(training_df, predicted_df, on='Timestamp')
    clean_df = df.dropna()
    return confusion_matrix(y_true=clean_df.Action_x.as_matrix(), y_pred=clean_df.Action_y.as_matrix())


def generate_reference_portfolio(initial_capital, parameters, stock_data_testing_set):
    reference_portfolio = Portfolio(initial_capital=initial_capital,
                                    trade_amount=parameters.trade_amount)
    training_signals = get_training_labels(stock_data_testing_set)
    for signal in training_signals:
        reference_portfolio.update(signal)
    reference_portfolio.compute_performance()
    return reference_portfolio, training_signals


def generate_signals_iteratively(stock_data: Union[Path, StockData], classifier: Union[Path, TradingClassifier]):
    if isinstance(classifier, Path):
        classifier = TradingClassifier.load_from_disk(classifier)
    if isinstance(stock_data, Path):
        stock_data = load_from_disk(stock_data)
    predicted_signals = []
    for candle in stock_data.candles:
        prediction = classifier.predict_one(candle)
        if prediction is not None:
            predicted_signals.append(generate_trading_signal_from_prediction(prediction[0], candle))
    return predicted_signals


def generate_signals_from_classifier(stock_data: Union[Path, StockData],
                                     classifier: Union[Path, TradingClassifier]) -> List[Union[SignalBuy, SignalSell]]:
    if isinstance(classifier, Path):
        classifier = TradingClassifier.load_from_disk(classifier)
    if isinstance(stock_data, Path):
        stock_data = load_from_disk(stock_data)
    predictions = classifier.predict(stock_data)
    predicted_signals = generate_trading_signals_from_array(predictions[:], stock_data)
    return predicted_signals


def replace_repeating_signals_with_holds(signals: List[Union[SignalBuy, SignalSell]]) -> List[Union[SignalBuy, SignalSell, SignalHold]]:
    cleaned_up_signals = []
    previous_signal = None
    for signal in signals:
        if isinstance(signal, type(previous_signal)):
            hold_signal = SignalHold(0, signal.price_point)
            cleaned_up_signals.append(hold_signal)
        else:
            cleaned_up_signals.append(signal)
        previous_signal = signal
    return cleaned_up_signals


def generate_all_signals_at_once(stock_data_testing_set, classifier, predicted_portfolio) -> Tuple[
    TradingClassifier, Portfolio, List[Union[SignalBuy, SignalSell, SignalHold]]]:
    predictions = classifier.predict(stock_data_testing_set)
    signals = generate_trading_signals_from_array(predictions[:], stock_data_testing_set)
    cleaned_up_signals = replace_repeating_signals_with_holds(signals[:])
    for signal in cleaned_up_signals:
        predicted_portfolio.update(signal)
    return classifier, predicted_portfolio, cleaned_up_signals
