import logging
import os
from datetime import timedelta, datetime
from typing import List

import matplotlib.pyplot as plt
import numpy as np
from binance.client import Client
from sklearn.ensemble import RandomForestClassifier

from src import definitions
from src.backtesting_logic.logic import _TradingSignal
from src.classification.classifier_helpers import compute_confusion_matrix, \
    generate_reference_portfolio, generate_all_signals_at_once
from src.classification.trading_classifier import TradingClassifier
from src.connection.downloader import load_stock_data, load_from_disk
from src.containers.candle import Candle
from src.containers.portfolio import Portfolio
from src.containers.stock_data import StockData
from src.containers.time_windows import TimeWindow
from src.definitions import DATA_DIR
from src.feature_extraction.technical_indicator import AutoCorrelationTechnicalIndicator, \
    PPOTechnicalIndicator
from src.live_logic.parameters import LiveParameters
from src.plotting.plot_candles import custom_plot
from src.type_aliases import Path


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


def main():
    trading_pair = "NEOBTC"

    training_time_window = TimeWindow(
        start_time=datetime(2018, 9, 24),
        end_time=datetime(2018, 9, 25)
    )

    stock_data_training_set = load_stock_data(training_time_window, trading_pair, Client.KLINE_INTERVAL_1MINUTE)
    testing_time_window = TimeWindow(start_time=datetime(2018, 10, 1), end_time=datetime(2018, 10, 2))

    stock_data_testing_set = load_stock_data(testing_time_window, trading_pair, Client.KLINE_INTERVAL_1MINUTE)

    list_of_technical_indicators = [
        # AutoCorrelationTechnicalIndicator(Candle.get_volume, 4),
        AutoCorrelationTechnicalIndicator(Candle.get_close_price, 1),
        AutoCorrelationTechnicalIndicator(Candle.get_close_price, 2),
        PPOTechnicalIndicator(Candle.get_close_price, 5, 1),
        PPOTechnicalIndicator(Candle.get_close_price, 10, 4),
        PPOTechnicalIndicator(Candle.get_close_price, 20, 1),
        PPOTechnicalIndicator(Candle.get_close_price, 30, 10),
        PPOTechnicalIndicator(Candle.get_number_of_trades, 5, 1),
        PPOTechnicalIndicator(Candle.get_number_of_trades, 10, 2),
        PPOTechnicalIndicator(Candle.get_number_of_trades, 15, 3),
        # PPOTechnicalIndicator(Candle.get_number_of_trades, 20, 1) / PPOTechnicalIndicator(Candle.get_volume, 20, 5),
        PPOTechnicalIndicator(Candle.get_volume, 5, 1),
    ]
    sklearn_classifier = RandomForestClassifier(n_estimators=1000, criterion="entropy", class_weight="balanced")
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

    predicted_portfolio.save_to_disk(os.path.join(DATA_DIR, "portfolio_backtest_df.dill"))

    custom_plot(portfolio=predicted_portfolio, strategy=None, title='Prediction portfolio_df')
    custom_plot(portfolio=reference_portfolio, strategy=None, title='Reference portfolio_df')
    print(my_classifier.sklearn_classifier.feature_importances_)
    conf_matrix = compute_confusion_matrix(reference_signals, predicted_signals)
    accuracy = np.sum(np.diag(conf_matrix)) / np.sum(conf_matrix)
    print(conf_matrix)
    print(accuracy)
    plt.show()


def run_trained_classifier(trading_pair: str, trade_amount: float, path_to_stock_data: Path,
                           path_to_portfolio: Path):

    stock_data_testing_set = load_from_disk(path_to_stock_data)

    parameters = LiveParameters(
        update_period=timedelta(minutes=1),
        trade_amount=trade_amount,
        sleep_time=0
    )
    my_classifier = TradingClassifier.load_from_disk(os.path.join(definitions.DATA_DIR, "classifier.dill"))

    initial_capital = 5
    reference_portfolio, reference_signals = generate_reference_portfolio(
        initial_capital, parameters, stock_data_testing_set)
    predicted_portfolio, predicted_signals = generate_predicted_portfolio(
        initial_capital, parameters, stock_data_testing_set, my_classifier)
    predicted_portfolio.save_to_disk(path_to_portfolio)

    if 0:
        plot_portfolios(
            my_classifier,
            predicted_portfolio,
            reference_portfolio,
            reference_signals,
            predicted_signals)


def plot_portfolios(my_classifier: TradingClassifier,
                    predicted_portfolio: Portfolio, reference_portfolio: Portfolio,
                    reference_signals: List[_TradingSignal],
                    predicted_signals: List[_TradingSignal]):
    custom_plot(portfolio=predicted_portfolio, strategy=None, title='Prediction portfolio_df')
    custom_plot(portfolio=reference_portfolio, strategy=None, title='Reference portfolio_df')
    print(my_classifier.sklearn_classifier.feature_importances_)
    conf_matrix = compute_confusion_matrix(reference_signals, predicted_signals)
    accuracy = np.sum(np.diag(conf_matrix)) / np.sum(conf_matrix)
    print(conf_matrix)
    print(accuracy)
    plt.show()


if __name__ == "__main__":
    logging.basicConfig(
        filename=os.path.join(definitions.DATA_DIR, 'local_autotrader_training_run.log'), filemode='w',
        # stream=sys.stdout,
        level=logging.DEBUG,
    )
    logger = logging.getLogger('cryptotrader_api')

    main()
    # run_trained_classifier()
