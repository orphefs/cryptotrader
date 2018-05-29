import logging
import os
import time
from datetime import timedelta, datetime
from typing import Callable

import matplotlib.pyplot as plt
from binance.client import Client

from containers.time_windows import TimeWindow
from definitions import update_interval_mappings
from mixins.save_load_mixin import SaveLoadMixin
from src import definitions
from src.backtesting_logic.logic import Hold
from src.containers.candle import Candle, instantiate_1970_candle
from src.containers.trade_helper import generate_trading_signal_from_prediction
from src.live_logic.market_maker import MarketMaker
from src.live_logic.parameters import LiveParameters
from src.live_logic.portfolio import Portfolio
from src.plotting.plot_candles import custom_plot
from src.tools.downloader import download_live_data, download_save_load
from src.tools.train_classifier import TradingClassifier

logging.basicConfig(filename=os.path.join(definitions.DATA_DIR, 'local_autotrader.log'), level=logging.INFO)
logger = logging.getLogger('cryptotrader_api')


def get_capital_from_account(capital_security: str) -> float:
    return 5.0


class LiveRunner(SaveLoadMixin):
    def __init__(self, trading_pair, trade_amount):
        self._trading_pair = trading_pair
        self._trade_amount = trade_amount
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

    def initialize(self):
        # self._classifier._maximum_lag
        self._previous_candle = instantiate_1970_candle()
        self._start_time = datetime.now()

    def shutdown(self):
        self._stop_time = datetime.now()
        self.save_to_disk("latest_run_live.dill")
        self._portfolio.save_to_disk(os.path.join(definitions.DATA_DIR, "portfolio_df.dill"))

    def download_candle(self) -> Candle:
        return download_live_data(self._client, self._trading_pair, self._kline_interval, 30)[-1]

    def mock_download_candle(self) -> Candle:
        return download_save_load(TimeWindow(start_time=datetime(2018, 5, 2), end_time=datetime(2018, 5, 3)),
                                  self._trading_pair, self._kline_interval).candles[self._iteration_number]

    def run(self):
        self._iteration_number = 1
        while True:
            self._current_candle = self.mock_download_candle()
            if is_time_difference_larger_than_threshold(self._current_candle, self._previous_candle,
                                                        self._waiting_threshold,
                                                        Candle.get_close_time_as_datetime):
                print("Registering candle: {}".format(self._current_candle))
                self._classifier.append_new_candle(self._current_candle)
                prediction = self._classifier.predict_one(self._current_candle)
                print("Prediction is: {} on iteration {}".format(prediction, self._iteration_number))
                if prediction is not None:
                    self._current_signal = generate_trading_signal_from_prediction(prediction[0], self._current_candle)
                    if self._current_signal.type == self._previous_signal.type:
                        print("Hodling...")
                    else:
                        print("Prediction for signal {}".format(self._current_signal))
                        # order = market_maker.place_order(current_signal)
                        self._portfolio.update(self._current_signal)
                        self._portfolio.save_to_disk(os.path.join(definitions.DATA_DIR, "portfolio_df.dill"))
                        self._previous_signal = self._current_signal
                self._previous_candle = self._current_candle
            time.sleep(self._parameters.sleep_time)
            self._iteration_number += 1


class live_runner:
    def __init__(self, trading_pair: str, trade_amount: float):
        self._live_runner = LiveRunner(trading_pair, trade_amount)

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


def run():
    with live_runner("XRPBTC", 100) as lr:
        lr.run()


def is_time_difference_larger_than_threshold(current_candle: Candle, previous_candle: Candle, threshold: timedelta,
                                             time_callback: Callable):
    return time_callback(current_candle) - time_callback(previous_candle) > threshold


def postprocess():
    portfolio = Portfolio.load_from_disk(os.path.join(definitions.DATA_DIR, "portfolio_df.dill"))
    portfolio.compute_performance()
    custom_plot(portfolio)
    print(portfolio._point_stats['base_index_pct_change'])
    print(portfolio._point_stats['total_pct_change'])

    plt.show()


if __name__ == '__main__':
    run()
