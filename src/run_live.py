import logging
import os
import time
from datetime import timedelta
from typing import Callable

import matplotlib.pyplot as plt
from binance.client import Client

import definitions
from backtesting_logic.logic import Hold
from containers.candle import Candle
from containers.trade_helper import generate_trading_signal_from_prediction
from live_logic.market_maker import MarketMaker
from live_logic.parameters import LiveParameters
from live_logic.portfolio import Portfolio
from plotting.plot_candles import custom_plot
from tools.downloader import download_live_data
from tools.train_classifier import TradingClassifier

logging.basicConfig(filename=os.path.join(definitions.DATA_DIR, 'local_autotrader.log'), level=logging.INFO)
logger = logging.getLogger('cryptotrader_api')


def get_capital_from_account(capital_security: str) -> float:
    return 5.0


def run(trade_amount: float, capital_security: str, trading_pair: str):
    client = Client("SlVs0AIAk6BsU1l4L4xbABxS40fCzxChxDFutURg4",
                    "ryGbS7EIdoF0n1xvoE71Pa8dl7ePO93rcApUaJkmP")
    parameters = LiveParameters(
        update_period=timedelta(hours=1),
        trade_amount=100,
        sleep_time=1
    )
    portfolio = Portfolio(initial_capital=get_capital_from_account(capital_security=None),
                          trade_amount=parameters.trade_amount)

    threshold = timedelta(seconds=45)

    classifier = TradingClassifier.load_from_disk(os.path.join(definitions.DATA_DIR, "classifier.dill"))
    market_maker = MarketMaker(client, trading_pair, trade_amount)
    logger.info("Initialized portfolio: {}".format(portfolio))

    candles = download_live_data(client, trading_pair, Client.KLINE_INTERVAL_1MINUTE, 30)
    for candle in candles:
        classifier.append_new_candle(candle)
    previous_candle = candles[-1]
    previous_signal = Hold(0,None)

    while True:
        # print("Loop iterating...")
        current_candle = download_live_data(client, trading_pair, Client.KLINE_INTERVAL_1MINUTE, 30)[-1]
        if is_time_difference_larger_than_threshold(current_candle, previous_candle, threshold,
                                                    Candle.get_close_time_as_datetime):
            # logger.info("Registering candle: {}".format(current_candle))
            classifier.append_new_candle(current_candle)
            prediction = classifier.predict_one(current_candle)
            if prediction is not None:
                current_signal = generate_trading_signal_from_prediction(prediction[0], current_candle)
                if current_signal.type == previous_signal.type:
                    logger.info("Hodling...")
                    pass  # HODL
                else:
                    logger.info("Prediction for signal {}".format(current_signal))
                    order = market_maker.place_order(current_signal)
                    portfolio.update(current_signal)
                    portfolio.save_to_disk(os.path.join(definitions.DATA_DIR, "portfolio.dill"))
                    previous_signal = current_signal
            previous_candle = current_candle
        time.sleep(parameters.sleep_time)


def is_time_difference_larger_than_threshold(current_candle: Candle, previous_candle: Candle, threshold: timedelta,
                                             time_callback: Callable):
    return time_callback(current_candle) - time_callback(previous_candle) > threshold


def postprocess():
    portfolio = Portfolio.load_from_disk(os.path.join(definitions.DATA_DIR, "portfolio.dill"))
    portfolio.compute_performance()
    custom_plot(portfolio)
    print(portfolio._point_stats['base_index_pct_change'])
    print(portfolio._point_stats['total_pct_change'])

    plt.show()


if __name__ == '__main__':
    run(trade_amount=1000, capital_security="BTC", trading_pair="XRPBTC")
