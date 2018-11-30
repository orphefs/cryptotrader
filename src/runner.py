import logging
import time
from datetime import datetime, timedelta
from typing import Union, Optional

from src.analysis_tools.run_metadata import RunMetaData
from src.backtesting_logic.logic import Hold
from src.classification.trading_classifier import TradingClassifier
from src.connection.load_stock_data import load_stock_data
from src.connection.download_live_data import download_live_data
from src.containers.candle import instantiate_1970_candle, Candle
from src.containers.portfolio import Portfolio
from src.containers.stock_data import StockData, load_from_disk
from src.containers.time_windows import TimeWindow
from src.containers.trade_helper import generate_trading_signal_from_prediction
from src.helpers import is_time_difference_larger_than_threshold, get_capital_from_account
from src.market_maker.market_maker import TestMarketMaker, MarketMaker, NoopMarketMaker
from src.live_logic.parameters import LiveParameters
from src.mixins.save_load_mixin import DillSaveLoadMixin
from src.type_aliases import Path, BinanceClient, CobinhoodClient
from src.containers.trading_pair import TradingPair


class Runner(DillSaveLoadMixin):
    def __init__(self, trading_pair: TradingPair, trade_amount: float, run_type: str,
                 mock_data_start_time: datetime,
                 mock_data_stop_time: datetime,
                 path_to_stock_data: str,
                 path_to_portfolio: Path,
                 path_to_classifier: Path,
                 client: Optional[Union[BinanceClient, CobinhoodClient]],
                 market_maker=Optional[Union[NoopMarketMaker, TestMarketMaker, MarketMaker]]):
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
        if client is None:
            self._client = BinanceClient("","") # this client does not need API key and is only used for downloading candles
        else:
            self._client = client
        self._sampling_period = timedelta(minutes=1)
        self._mock_data_start_time = mock_data_start_time
        self._mock_data_stop_time = mock_data_stop_time
        self._path_to_stock_data = path_to_stock_data
        self._path_to_portfolio = path_to_portfolio
        self._stock_data = StockData
        self._run_metadata = RunMetaData(trading_pair=self._trading_pair,
                                         trade_amount=self._trade_amount,
                                         run_type=self._run_type)
        self._parameters = LiveParameters(update_period=timedelta(hours=1),
                                          trade_amount=self._trade_amount,
                                          # sleep_time=update_interval_mappings[self._kline_interval].total_seconds(),
                                          sleep_time=2,
                                          )
        self._portfolio = Portfolio(initial_capital=get_capital_from_account(trading_pair=self._trading_pair),
                                    trade_amount=self._parameters.trade_amount)
        self._waiting_threshold = timedelta(seconds=self._sampling_period.total_seconds() - 15)

        self._classifier = TradingClassifier.load_from_disk(path_to_classifier)
        if market_maker is None:
            self._market_maker = NoopMarketMaker(self._client, self._trading_pair, self._trade_amount)
        else:
            self._market_maker = market_maker

    @property
    def portfolio(self):
        return self._portfolio

    def initialize(self):
        """Should be called by the resource manager class"""
        self._previous_candle = instantiate_1970_candle()
        self._start_time = datetime.now()
        self._run_metadata.start_time = self._start_time
        if self._run_type == "live":
            self._run_metadata.save_to_disk(self, "run_metadata.dill")

    def shutdown(self):
        """Should be called by the resource manager class"""
        self._stop_time = datetime.now()
        self._run_metadata.stop_time = self._stop_time
        self._run_metadata.stop_candle = self._current_candle
        if self._run_type == "live":
            self._run_metadata.save_to_disk(self, "run_metadata.dill")

        self.save_to_disk(self, "run.dill")
        self._portfolio.save_to_disk(self._path_to_portfolio)

    def _download_candle(self) -> Candle:
        if self._run_type == "live":
            return download_live_data(self._client, self._trading_pair, self._sampling_period, 30)
        elif self._run_type == "mock":
            return self._mock_download_candle_for_current_iteration()

    def _mock_download_stock_data_for_all_iterations(self):
        if self._mock_data_start_time and self._mock_data_stop_time:
            self._stock_data = load_stock_data(TimeWindow(start_time=self._mock_data_start_time,
                                                          end_time=self._mock_data_stop_time),
                                               self._trading_pair, self._sampling_period)
        elif self._path_to_stock_data:
            self._stock_data = load_from_disk(self._path_to_stock_data)

    def _mock_download_candle_for_current_iteration(self) -> Candle:
        if self._path_to_stock_data:
            if not self._stock_data:
                self._stock_data = load_from_disk(self._path_to_stock_data)
            return self._stock_data.candles[self._iteration_number]
        else:
            return self._stock_data.candles[self._iteration_number]

    def _is_check_condition(self):
        if self._run_type == "mock":
            return self._iteration_number < len(self._stock_data.candles)
        elif self._run_type == "live":
            return True

    def run(self):
        self._iteration_number = 0
        logging.debug("Waiting threshold between decisions is {}".format(self._waiting_threshold))
        if self._run_type == "mock":
            self._mock_download_stock_data_for_all_iterations()

        while self._is_check_condition():
            self._current_candle = self._download_candle()
            if self._iteration_number == 0:
                self._run_metadata.start_candle = self._current_candle

            logging.debug("Current candle time: {}".format(self._current_candle.get_close_time_as_datetime()))

            if is_time_difference_larger_than_threshold(self._current_candle, self._previous_candle,
                                                        self._waiting_threshold,
                                                        time_getter_callback=Candle.get_close_time_as_datetime):
                logging.info("Registering candle: {}".format(self._current_candle))
                # print(repr(self._classifier))
                self._classifier.append_new_candle(self._current_candle)
                try:
                    prediction = self._classifier.predict_one(self._current_candle)
                except ValueError:
                    prediction = None

                logging.info("Prediction is: {} on iteration {}".format(prediction, self._iteration_number))
                if prediction is not None:
                    self._current_signal = generate_trading_signal_from_prediction(prediction[0], self._current_candle)
                    # print("\n\n Prediction for signal {} \n\n".format(self._current_signal))
                    logging.debug("Prediction for signal {}".format(self._current_signal))

                    if self._current_signal.type == self._previous_signal.type:
                        logging.info("Hodling...")
                    else:
                        logging.info("Prediction for signal {}".format(self._current_signal))
                        order = self._market_maker.place_order(self._current_signal)

                        self._portfolio.update(self._current_signal)
                        self._portfolio.save_to_disk(self._path_to_portfolio)
                        self._previous_signal = self._current_signal
                self._previous_candle = self._current_candle

            if self._run_type == "live":
                logging.debug("Going to sleep for {} seconds.".format(self._parameters.sleep_time))
                time.sleep(self._parameters.sleep_time)
            self._iteration_number += 1
            logging.debug("We are on the {}th iteration".format(self._iteration_number))
