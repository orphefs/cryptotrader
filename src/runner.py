import os
import time
from datetime import datetime, timedelta
from typing import Union, Optional
import simplejson as json
import websocket

from src.analysis_tools.run_metadata import RunMetaData
from src.classification.train_classifier import train_classifier
from src.containers.order import Order
from src.containers.signal import SignalHold, SignalBuy, SignalSell
from src.classification.trading_classifier import TradingClassifier
from src.connection.load_stock_data import load_stock_data
from src.connection.download_live_data import download_live_data
from src.containers.candle import instantiate_1970_candle, Candle
from src.containers.portfolio import Portfolio
from src.containers.stock_data import StockData, load_from_disk
from src.containers.time_windows import TimeWindow
from src.containers.trade_helper import generate_trading_signal_from_prediction
from src.feature_extraction.technical_indicator import AutoCorrelationTechnicalIndicator, \
    PPOTechnicalIndicator
from src.helpers import is_time_difference_larger_than_threshold, get_capital_from_account
from src.market_maker import ExperimentalMarketMaker
from src.market_maker.market_maker import TestMarketMaker, MarketMaker, NoopMarketMaker
from src.live_logic.parameters import LiveParameters
from src.mixins.save_load_mixin import DillSaveLoadMixin
from src.type_aliases import Path, BinanceClient
from src.containers.trading_pair import TradingPair
from src.logger import logger


def _pass_signal_to_market_maker(current_signal: Union[SignalBuy, SignalSell],
                                 market_maker: Union[NoopMarketMaker, TestMarketMaker,
                                                     MarketMaker]) -> Order:
    last_filled_order = market_maker.insert_signal(current_signal)


class Runner(DillSaveLoadMixin):
    def __init__(self, trading_pair: TradingPair, trade_amount: float, run_type: str,
                 mock_data_start_time: datetime,
                 mock_data_stop_time: datetime,
                 path_to_stock_data: str,
                 path_to_portfolio: Path,
                 path_to_classifier: Path,
                 client: Optional[Union[BinanceClient]],
                 market_maker: Optional[Union[NoopMarketMaker, TestMarketMaker, MarketMaker]],
                 websocket_client: Optional[websocket.WebSocketApp]):
        self._trading_pair = trading_pair
        self._trade_amount = trade_amount
        self._run_type = run_type
        self._start_time = None
        self._stop_time = None
        self._current_candle = None
        self._current_prediction = None
        self._current_signal = SignalHold(0, None)
        self._previous_candle = None
        self._previous_prediction = None
        self._previous_signal = SignalHold(0, None)
        self._iteration_number = None
        if client is None:
            self._client = BinanceClient("",
                "")  # this client does not need API key and is only used for downloading candles
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
        # self._waiting_threshold = timedelta(seconds=4)

        if os.path.isfile(path_to_classifier):
            self._classifier = TradingClassifier.load_from_disk(path_to_classifier)
        else:
            train_classifier(trading_pair=self._trading_pair,
                client=self._client,
                training_time_window=TimeWindow(start_time=datetime.now() - timedelta(days=30),
                    end_time=datetime.now()),
                technical_indicators=[
                    AutoCorrelationTechnicalIndicator(Candle.get_close_price, 1),
                    AutoCorrelationTechnicalIndicator(Candle.get_close_price, 2),
                    AutoCorrelationTechnicalIndicator(Candle.get_close_price, 3),
                    AutoCorrelationTechnicalIndicator(Candle.get_close_price, 4),
                    PPOTechnicalIndicator(Candle.get_close_price, 5, 1),
                    PPOTechnicalIndicator(Candle.get_close_price, 10, 4),
                    PPOTechnicalIndicator(Candle.get_close_price, 20, 1),
                    PPOTechnicalIndicator(Candle.get_close_price, 30, 10),
                    PPOTechnicalIndicator(Candle.get_close_price, 40, 20),
                    PPOTechnicalIndicator(Candle.get_close_price, 50, 30),
                    PPOTechnicalIndicator(Candle.get_close_price, 60, 40),
                ],
                path_to_classifier=path_to_classifier,
            )
            pass  # TODO: train classifier on some historical data for this trading pair
        if market_maker is None:
            self._market_maker = NoopMarketMaker(self._client, self._trading_pair, self._trade_amount)
        else:
            self._market_maker = market_maker

        self._websocket_client = websocket_client

    @property
    def portfolio(self):
        return self._portfolio

    def initialize(self):
        """Should be called by the resource manager class"""
        self._previous_candle = instantiate_1970_candle()
        self._start_time = datetime.now()
        self._run_metadata.start_time = self._start_time
        if self._run_type == "live":
            self._run_metadata.save_to_disk(self._run_metadata, "run_metadata.dill")

    def shutdown(self):
        """Should be called by the resource manager class"""
        self._stop_time = datetime.now()
        self._run_metadata.stop_time = self._stop_time
        self._run_metadata.stop_candle = self._current_candle
        if self._run_type == "live":
            self._run_metadata.save_to_disk(self, "run_metadata.dill")

        # self.save_to_disk(self, "run.dill") #TODO: disabled because this tries to pickle unpicklable objects (such as websocket)
        # self._portfolio.save_to_disk(self._run_metadata._path_to_portfolio)

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
        logger.debug("Waiting threshold between decisions is {}".format(self._waiting_threshold))
        if self._run_type == "mock":
            self._mock_download_stock_data_for_all_iterations()

        while self._is_check_condition():
            try:
                self._current_candle = self._download_candle()
            except Exception as e:
                logger.debug("Error while trying to download candles: {}".format(e))
            if self._iteration_number == 0:
                self._run_metadata.start_candle = self._current_candle

            logger.debug("Current candle time: {}".format(self._current_candle.get_close_time_as_datetime()))

            if is_time_difference_larger_than_threshold(self._current_candle, self._previous_candle,
                    self._waiting_threshold,
                    time_getter_callback=Candle.get_close_time_as_datetime):
                logger.info("Registering candle: {}".format(self._current_candle))
                self._classifier.append_new_candle(self._current_candle)
                try:
                    prediction = self._classifier.predict_one(self._current_candle)
                except ValueError:
                    prediction = None

                logger.debug("Prediction is: {} on iteration {}".format(prediction, self._iteration_number))
                if prediction:
                    self._current_signal = generate_trading_signal_from_prediction(prediction[0],
                        self._current_candle)
                    self._portfolio.update(self._current_signal)
                    logger.info("Prediction for signal {}".format(self._current_signal))

                    last_filled_order = _pass_signal_to_market_maker(current_signal=self._current_signal,
                        market_maker=self._market_maker)
                    if self._websocket_client:
                        try:
                            self._websocket_client.send(json.dumps(
                                {"trading_pair": self._trading_pair.as_string_for_binance(),
                                 "signal": self._current_signal.as_dict()}))
                        except Exception as e:
                            logger.info("Websocket error: {}".format(e))

                    if last_filled_order and last_filled_order not in self._portfolio.orders:
                        self._portfolio.update(last_filled_order)
                        logger.info("Updated portfolio with new order: {}".format(last_filled_order))

                    # self._portfolio.save_to_disk(self._path_to_portfolio)
                    self._previous_signal = self._current_signal
                self._previous_candle = self._current_candle

            if self._run_type == "live":
                logger.debug("Going to sleep for {} seconds.".format(self._parameters.sleep_time))
                time.sleep(self._parameters.sleep_time)

                last_filled_order = _pass_signal_to_market_maker(current_signal=self._current_signal,
                    market_maker=self._market_maker)
                if last_filled_order and last_filled_order not in self._portfolio.orders:
                    self._portfolio.update(last_filled_order)
                    logger.info("Updated portfolio with new order: {}".format(last_filled_order))

            self._iteration_number += 1
            logger.debug("We are on the {}th iteration".format(self._iteration_number))
