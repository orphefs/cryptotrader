import hashlib
import logging
import os
import random
from datetime import timedelta, datetime
from typing import List, Union

import matplotlib.pyplot as plt
import numpy as np
from binance.client import Client
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

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
from src.definitions import DATA_DIR, TEST_DATA_DIR
from src.feature_extraction.technical_indicator import AutoCorrelationTechnicalIndicator, \
    PPOTechnicalIndicator, TechnicalIndicator
from src.live_logic.parameters import LiveParameters
from src.plotting.plot_candles import custom_plot
from src.type_aliases import Path, Hash


def generate_predicted_portfolio(initial_capital: int, parameters: LiveParameters,
                                 stock_data_testing_set: StockData, classifier: TradingClassifier):
    predicted_portfolio = Portfolio(initial_capital=initial_capital,
                                    trade_amount=parameters.trade_amount,
                                    classifier=classifier)

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


def train_classifier(trading_pair: str,
                     training_time_window: TimeWindow,
                     technical_indicators: List[TechnicalIndicator],
                     path_to_classifier: Path,
                     ) -> Hash:
    stock_data_training_set = load_stock_data(training_time_window, trading_pair, Client.KLINE_INTERVAL_1MINUTE)

    sklearn_classifier = RandomForestClassifier(max_depth=5,
                                                n_estimators=10,
                                                # criterion="gini",
                                                class_weight="balanced",
                                                random_state=random.seed(1234))

    # sklearn_classifier = SVC(gamma="auto")
    training_ratio = 0.5  # this is not enabled
    my_classifier = TradingClassifier(trading_pair, technical_indicators,
                                      sklearn_classifier, training_time_window, training_ratio)
    my_classifier.train(stock_data_training_set)
    # my_classifier.save_to_disk(os.path.join(definitions.TEST_DATA_DIR, "classifier.dill"))
    my_classifier.save_to_disk(path_to_classifier)


def run_trained_classifier(trading_pair: str,
                           trade_amount: float,
                           testing_data: Union[TimeWindow, StockData, Path],
                           classifier: Union[Path, TradingClassifier],
                           path_to_portfolio: Path, ):
    stock_data_testing_set = None
    if isinstance(testing_data, TimeWindow):
        stock_data_testing_set = load_stock_data(testing_data, trading_pair, Client.KLINE_INTERVAL_1MINUTE)
    elif isinstance(testing_data, Path):
        stock_data_testing_set = load_from_disk(testing_data)
    elif isinstance(testing_data, StockData):
        stock_data_testing_set = testing_data
    assert isinstance(stock_data_testing_set, StockData)

    parameters = LiveParameters(
        update_period=timedelta(minutes=1),
        trade_amount=trade_amount,
        sleep_time=0
    )
    my_classifier = None
    if isinstance(classifier, Path):
        my_classifier = TradingClassifier.load_from_disk(classifier)
    elif isinstance(classifier, TradingClassifier):
        my_classifier = classifier

    initial_capital = 5

    predicted_portfolio, predicted_signals = generate_predicted_portfolio(
        initial_capital, parameters, stock_data_testing_set, my_classifier)
    predicted_portfolio.save_to_disk(path_to_portfolio)

    # if 0:
    #     plot_portfolios(
    #         my_classifier,
    #         predicted_portfolio,
    #         reference_portfolio,
    #         reference_signals,
    #         predicted_signals)


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

    train_classifier(trading_pair="NEOBTC",
                     training_time_window=TimeWindow(
                         start_time=datetime(2018, 9, 1),
                         end_time=datetime(2018, 9, 2)
                     ),
                     technical_indicators=[
                         AutoCorrelationTechnicalIndicator(Candle.get_volume, 4),
                         AutoCorrelationTechnicalIndicator(Candle.get_close_price, 1),
                         AutoCorrelationTechnicalIndicator(Candle.get_close_price, 2),
                         PPOTechnicalIndicator(Candle.get_close_price, 5, 1),
                         PPOTechnicalIndicator(Candle.get_close_price, 10, 4),
                         PPOTechnicalIndicator(Candle.get_close_price, 20, 1),
                         # PPOTechnicalIndicator(Candle.get_close_price, 20, 5),
                         # PPOTechnicalIndicator(Candle.get_close_price, 20, 10),
                         PPOTechnicalIndicator(Candle.get_close_price, 30, 10),
                         PPOTechnicalIndicator(Candle.get_number_of_trades, 5, 1),
                         PPOTechnicalIndicator(Candle.get_number_of_trades, 10, 2),
                         PPOTechnicalIndicator(Candle.get_number_of_trades, 15, 3),
                         # PPOTechnicalIndicator(Candle.get_number_of_trades, 20, 1) / PPOTechnicalIndicator(Candle.get_volume, 20, 5),
                         PPOTechnicalIndicator(Candle.get_volume, 5, 1),
                     ],
                     path_to_classifier=os.path.join(DATA_DIR, "classifier.dill"))
    if 0:
        run_trained_classifier(trading_pair="NEOBTC",
                               trade_amount=100,
                               path_to_stock_data="/home/orphefs/Documents/Code/autotrader/autotrader/data/local_data_01_Oct,_2018_02_Oct,_2018_NEOBTC_1m.dill",
                               path_to_portfolio="/home/orphefs/Documents/Code/autotrader/autotrader/data/offline_portfolio.dill")
