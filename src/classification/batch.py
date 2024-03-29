import hashlib
import os
from datetime import datetime
from typing import Set, List, Union

from src.analysis_tools.analyze_batch_run import analyze_batch_run
from src.connection.helpers import clear_downloaded_stock_data
from src.datetime_helpers import datetime_to_nth_day, nth_day_to_datetime
from src.helpers import generate_hash
from src.classification.trading_classifier import TradingClassifier
from src.classification.train_classifier import train_classifier, run_trained_classifier
from src.containers.candle import Candle
from src.containers.time_windows import TimeWindow
from src.definitions import DATA_DIR
from src.feature_extraction.technical_indicator import TechnicalIndicator, PPOTechnicalIndicator, \
    AutoCorrelationTechnicalIndicator
from src.type_aliases import Hash, Path, BinanceClient
from src.containers.trading_pair import TradingPair
import numpy as np
from random import randint
import logging

logging.basicConfig(
    filename=os.path.join(DATA_DIR, "batch_runner.log"), filemode='w',
    # stream=sys.stdout,
    level=logging.INFO,
)


def generate_sample_time_windows() -> List[TimeWindow]:
    return [
        TimeWindow(datetime(2018, 5, 5), datetime(2018, 5, 10)),
        TimeWindow(datetime(2018, 5, 11), datetime(2018, 5, 16)),
        TimeWindow(datetime(2018, 5, 17), datetime(2018, 5, 22)),
    ]


def generate_sample_time_windows_2() -> List[TimeWindow]:
    return [
        TimeWindow(datetime(2018, 5, 1), datetime(2018, 5, 2)),
        TimeWindow(datetime(2018, 5, 3), datetime(2018, 5, 5)),
        TimeWindow(datetime(2018, 5, 7), datetime(2018, 5, 11)),
        TimeWindow(datetime(2018, 5, 12), datetime(2018, 5, 17)),
        TimeWindow(datetime(2018, 5, 18), datetime(2018, 5, 25)),
        TimeWindow(datetime(2018, 5, 26), datetime(2018, 6, 4)),
        TimeWindow(datetime(2018, 6, 5), datetime(2018, 6, 15)),
        TimeWindow(datetime(2018, 6, 16), datetime(2018, 6, 28)),
    ]


def generate_time_windows(number_of_time_windows: int) -> List[TimeWindow]:
    year = 2018
    time_windows = []
    min_start_date = datetime(year, 8, 1)
    max_end_date = datetime(year, 11, 20)
    for i in range(0, number_of_time_windows):
        duration_days = randint(1, 2)
        start_day = randint(datetime_to_nth_day(min_start_date),
                            datetime_to_nth_day(max_end_date))
        end_day = start_day + duration_days
        time_windows.append(TimeWindow(
            start_time=nth_day_to_datetime(start_day, year),
            end_time=nth_day_to_datetime(end_day, year))
        )
    return time_windows


def generate_path_to_portfolio(testing_hash: str,
                               trading_pair: TradingPair,
                               trade_amount: float,
                               ) -> Path:
    m = hashlib.md5()
    m.update((str(testing_hash) + str(trading_pair) + str(trade_amount)).encode("utf-8"))
    return os.path.join(DATA_DIR, "portfolio_{}".format(m.hexdigest()))


def batch_train(training_time_windows: List[TimeWindow],
                trading_pair: TradingPair,
                client: Union[BinanceClient],
                number_of_training_runs: int,
                technical_indicators: List[TechnicalIndicator],
                ) -> Set[Hash]:
    hashes = []
    for training_time_window in training_time_windows:
        for i in range(0, number_of_training_runs):
            training_session_hash = generate_hash(training_time_window, trading_pair, i)
            path_to_classifier = os.path.join(DATA_DIR, "classifier_{}.dill".format(training_session_hash))
            train_classifier(trading_pair=trading_pair,
                             training_time_window=training_time_window,
                             technical_indicators=technical_indicators,
                             path_to_classifier=path_to_classifier,
                             client=client
                             )
            hashes.append(training_session_hash)
    return set(hashes)


def batch_test(testing_time_windows: List[TimeWindow],
               trading_pair: TradingPair,
               trade_amount: float,
               number_of_testing_runs: int,
               client: Union[BinanceClient],
               classifier: TradingClassifier) -> Set[Hash]:
    training_time_window = classifier.training_time_window
    hashes = []
    for testing_time_window in testing_time_windows:
        if not training_time_window.__is_overlap__(testing_time_window):
            for i in range(0, number_of_testing_runs):
                testing_session_hash = generate_hash(training_time_window, testing_time_window, trading_pair, i)
                path_to_portfolio = os.path.join(DATA_DIR, "portfolio_{}.dill".format(testing_session_hash))
                logging.info("Saving portfolio to {}".format(path_to_portfolio))
                run_trained_classifier(trading_pair=trading_pair,
                                       trade_amount=trade_amount,
                                       testing_data=testing_time_window,
                                       classifier=classifier,
                                       path_to_portfolio=path_to_portfolio,
                                       client=client

                                       # TODO: define saveload mixin for portfolio class
                                       )
                hashes.append(testing_session_hash)
    return set(hashes)


def run_batch():
    clear_downloaded_stock_data()
    trading_pair = TradingPair("XRP", "BTC")
    client = BinanceClient("", "")
    # client = CobinhoodClient()
    trade_amount = 50
    training_time_windows = generate_time_windows(3)
    testing_time_windows = generate_time_windows(10)
    training_hashes = batch_train(
        training_time_windows=training_time_windows,
        trading_pair=trading_pair,
        client=client,
        number_of_training_runs=2,
        technical_indicators=[
            AutoCorrelationTechnicalIndicator(Candle.get_volume, 1),
            AutoCorrelationTechnicalIndicator(Candle.get_volume, 2),
            AutoCorrelationTechnicalIndicator(Candle.get_volume, 3),
            AutoCorrelationTechnicalIndicator(Candle.get_volume, 4),
            AutoCorrelationTechnicalIndicator(Candle.get_volume, 5),
            AutoCorrelationTechnicalIndicator(Candle.get_volume, 6),
            AutoCorrelationTechnicalIndicator(Candle.get_close_price, 1),
            AutoCorrelationTechnicalIndicator(Candle.get_close_price, 2),
            AutoCorrelationTechnicalIndicator(Candle.get_close_price, 3),
            AutoCorrelationTechnicalIndicator(Candle.get_close_price, 4),
            AutoCorrelationTechnicalIndicator(Candle.get_close_price, 5),
            AutoCorrelationTechnicalIndicator(Candle.get_close_price, 6),
            AutoCorrelationTechnicalIndicator(Candle.get_close_price, 7),
            AutoCorrelationTechnicalIndicator(Candle.get_close_price, 8),
            AutoCorrelationTechnicalIndicator(Candle.get_open_price, 1),
            AutoCorrelationTechnicalIndicator(Candle.get_open_price, 2),
            AutoCorrelationTechnicalIndicator(Candle.get_open_price, 3),
            AutoCorrelationTechnicalIndicator(Candle.get_open_price, 4),
            AutoCorrelationTechnicalIndicator(Candle.get_open_price, 5),
            AutoCorrelationTechnicalIndicator(Candle.get_number_of_trades, 1),
            AutoCorrelationTechnicalIndicator(Candle.get_number_of_trades, 2),
            AutoCorrelationTechnicalIndicator(Candle.get_number_of_trades, 3),
            AutoCorrelationTechnicalIndicator(Candle.get_number_of_trades, 4),
            AutoCorrelationTechnicalIndicator(Candle.get_number_of_trades, 5),
            PPOTechnicalIndicator(Candle.get_close_price, 5, 1),
            PPOTechnicalIndicator(Candle.get_close_price, 10, 4),
            PPOTechnicalIndicator(Candle.get_close_price, 20, 1),
            PPOTechnicalIndicator(Candle.get_close_price, 30, 10),
            PPOTechnicalIndicator(Candle.get_close_price, 40, 20),
            PPOTechnicalIndicator(Candle.get_close_price, 50, 30),
            PPOTechnicalIndicator(Candle.get_close_price, 60, 40),
            PPOTechnicalIndicator(Candle.get_number_of_trades, 5, 1),
            PPOTechnicalIndicator(Candle.get_number_of_trades, 10, 2),
            PPOTechnicalIndicator(Candle.get_number_of_trades, 15, 3),
            PPOTechnicalIndicator(Candle.get_volume, 5, 1),
            PPOTechnicalIndicator(Candle.get_volume, 10, 5),
            PPOTechnicalIndicator(Candle.get_volume, 20, 10),
            PPOTechnicalIndicator(Candle.get_volume, 30, 10),
        ])
    testing_hashes = []
    for training_hash in training_hashes:
        path_to_classifier = os.path.join(DATA_DIR, "classifier_{}.dill".format(training_hash))
        print(path_to_classifier)
        classifier = TradingClassifier.load_from_disk(path_to_classifier)
        print(type(classifier))
        testing_hashes += batch_test(
            testing_time_windows=testing_time_windows,
            trading_pair=trading_pair,
            trade_amount=trade_amount,
            number_of_testing_runs=1,
            classifier=classifier,
            client=client

        )

    return training_hashes, testing_hashes


if __name__ == '__main__':
    training_hashes, testing_hashes = run_batch()
    print(training_hashes)
    print(testing_hashes)
    analyze_batch_run()
    # [print(w) for w in generate_time_windows(15)]
