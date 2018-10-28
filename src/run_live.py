import logging
import os
import sys
import time
from datetime import timedelta, datetime
from typing import Callable

import matplotlib.pyplot as plt
from binance.client import Client

from src import definitions
from src.backtesting_logic.logic import Hold
from src.containers.candle import Candle, instantiate_1970_candle
from src.containers.stock_data import StockData
from src.containers.time_windows import TimeWindow
from src.containers.trade_helper import generate_trading_signal_from_prediction
from src.definitions import update_interval_mappings
from src.live_logic.market_maker import MarketMaker
from src.live_logic.parameters import LiveParameters
from src.live_logic.portfolio import Portfolio
from src.mixins.save_load_mixin import DillSaveLoadMixin
from src.plotting.plot_candles import custom_plot
from src.tools.downloader import download_live_data, load_stock_data
from src.tools.train_classifier import TradingClassifier, generate_predicted_portfolio

logging.basicConfig(
    # filename=os.path.join(definitions.DATA_DIR, 'local_autotrader.log'),
    level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger('cryptotrader_api')


def is_time_difference_larger_than_threshold(current_candle: Candle, previous_candle: Candle, threshold: timedelta,
                                             time_getter_callback: Callable):
    return time_getter_callback(current_candle) - time_getter_callback(previous_candle) > threshold


def postprocess():
    portfolio = Portfolio.load_from_disk(os.path.join(definitions.DATA_DIR, "portfolio_df.dill"))
    portfolio.compute_performance()
    custom_plot(portfolio)
    print(portfolio._point_stats['base_index_pct_change'])
    print(portfolio._point_stats['total_pct_change'])

    plt.show()


def get_capital_from_account(capital_security: str) -> float:
    return 5.0


class LiveRunner(DillSaveLoadMixin):
    def __init__(self, trading_pair: str, trade_amount: float, run_type: str,
                 mock_data_start_time: datetime,
                 mock_data_stop_time: datetime):
        self._trading_pair = trading_pair
        self._trade_amount = trade_amount
        self._run_type = run_type
        self._start_time = None
        self._stop_time = None
        self._current_candle = None
        self._current_prediction = None
        self._current_signal = Hold(0, None)
        self._previous_candle = None
        self._previous_prediction = None
        self._previous_signal = Hold(0, None)
        self._iteration_number = None
        self._client = Client("", "")
        self._kline_interval = Client.KLINE_INTERVAL_1MINUTE
        self._mock_data_start_time = mock_data_start_time
        self._mock_data_stop_time = mock_data_stop_time
        self._parameters = LiveParameters(
            update_period=timedelta(hours=1),
            trade_amount=100,
            # sleep_time=update_interval_mappings[self._kline_interval].total_seconds(),
            sleep_time=0.01,
        )
        self._portfolio = Portfolio(initial_capital=get_capital_from_account(capital_security=None),
                                    trade_amount=self._parameters.trade_amount)
        self._waiting_threshold = timedelta(seconds=update_interval_mappings[self._kline_interval].total_seconds() - 15)

        self._classifier = TradingClassifier.load_from_disk(os.path.join(definitions.DATA_DIR, "classifier.dill"))
        self._market_maker = MarketMaker(self._client, self._trading_pair, self._trade_amount)

    @property
    def portfolio(self):
        return self._portfolio

    def initialize(self):
        """Should be called by the resource manager class"""
        # self._classifier._maximum_lag
        self._previous_candle = instantiate_1970_candle()
        self._start_time = datetime.now()

    def shutdown(self):
        """Should be called by the resource manager class"""
        self._stop_time = datetime.now()
        self.save_to_disk("latest_run_live.dill")
        self._portfolio.save_to_disk(os.path.join(definitions.DATA_DIR, "portfolio_df.dill"))

    def _download_candle(self) -> Candle:
        if self._run_type == "live":
            return download_live_data(self._client, self._trading_pair, self._kline_interval, 30)[-1]
        elif self._run_type == "mock":
            return self._mock_download_candle_for_current_iteration()

    def _mock_download_candle_for_current_iteration(self) -> Candle:
        return load_stock_data(TimeWindow(start_time=self._mock_data_start_time, end_time=self._mock_data_stop_time),
                               self._trading_pair, self._kline_interval).candles[self._iteration_number]

    def _mock_download_stock_data_for_all_iterations(self) -> StockData:
        return load_stock_data(TimeWindow(start_time=self._mock_data_start_time, end_time=self._mock_data_stop_time),
                               self._trading_pair, self._kline_interval)

    def _is_check_condition(self):
        if self._run_type == "mock":
            return self._iteration_number < len(self._mock_download_stock_data_for_all_iterations().candles)
        elif self._run_type == "live":
            return True

    def run(self):
        self._iteration_number = 1
        logger.debug("Waiting threshold between decisions is {}".format(self._waiting_threshold))
        while self._is_check_condition():

            self._current_candle = self._download_candle()

            logger.debug("Current candle time: {}".format(self._current_candle.get_close_time_as_datetime()))

            if is_time_difference_larger_than_threshold(self._current_candle, self._previous_candle,
                                                        self._waiting_threshold,
                                                        time_getter_callback=Candle.get_close_time_as_datetime):
                logger.info("Registering candle: {}".format(self._current_candle))
                self._classifier.append_new_candle(self._current_candle)
                prediction = self._classifier.predict_one(self._current_candle)
                logger.info("Prediction is: {} on iteration {}".format(prediction, self._iteration_number))
                if prediction is not None:
                    self._current_signal = generate_trading_signal_from_prediction(prediction[0], self._current_candle)
                    if self._current_signal.type == self._previous_signal.type:
                        logger.info("Hodling...")
                    else:
                        logger.info("Prediction for signal {}".format(self._current_signal))
                        # order = market_maker.place_order(current_signal)
                        self._portfolio.update(self._current_signal)
                        self._portfolio.save_to_disk(os.path.join(definitions.DATA_DIR, "portfolio_df.dill"))
                        self._previous_signal = self._current_signal
                self._previous_candle = self._current_candle

            logger.debug("Going to sleep for {} seconds.".format(self._parameters.sleep_time))
            time.sleep(self._parameters.sleep_time)
            self._iteration_number += 1
            logger.debug("We are on the {}th iteration".format(self._iteration_number))

    def run_backtesting_batch(self):
        portfolio, _ = generate_predicted_portfolio(initial_capital=self._portfolio._initial_capital,
                                                    parameters=self._parameters,
                                                    stock_data_testing_set=self._mock_download_stock_data_for_all_iterations(),
                                                    classifier=self._classifier,
                                                    )
        pass


class live_runner:
    def __init__(self, trading_pair: str, trade_amount: float, run_type: str, mock_data_start_time: datetime,
                 mock_data_stop_time: datetime):
        self._live_runner = LiveRunner(trading_pair, trade_amount, run_type, mock_data_start_time, mock_data_stop_time)

    def __enter__(self):
        self._live_runner.initialize()
        return self._live_runner

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, traceback)
            self._live_runner.shutdown()
            return self

    @property
    def live_runner(self):
        return self._live_runner


def main():
    with live_runner("XRPBTC", 100, "mock",
                     mock_data_start_time=datetime(2018, 5, 1),
                     mock_data_stop_time=datetime(2018, 5, 2)) as lr:
        lr.run()


if __name__ == '__main__':
    main()

