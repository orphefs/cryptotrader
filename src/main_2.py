import logging
import os
import time
from typing import List

import matplotlib
from datetime import timedelta

from live_logic.strategy import SMAStrategy, Parameters, LiveParameters, Portfolio
from tools.downloader import download_live_data

matplotlib.use('AGG')  # generate postscript output by default
import matplotlib.pyplot as plt

from binance.client import Client

import definitions
from containers.candle import Candle
from containers.trade import Trade
from helpers import simple_moving_average
from trading_logic import get_heading, get_trend

logging.basicConfig(filename=os.path.join(definitions.DATA_DIR, '_autotrader.log'), level=logging.INFO)
is_enabled = True
parameters = LiveParameters(short_sma_period=timedelta(minutes=1),
                            long_sma_period=timedelta(minutes=15),
                            trade_amount=100,
                            sleep_time=0)


def main():
    client = Client()

    portfolio = Portfolio(initial_capital=1.0)

    while is_enabled:
        stock_data = download_live_data(client, "XRPBTC")
        strategy = SMAStrategy(stock_data, parameters, portfolio)
        strategy.extract_time_series_from_stock_data()
        strategy.compute_moving_averages()
        signal = strategy.generate_trading_signal()
        portfolio.update(signal)

        time.sleep(parameters.sleep_time)


if __name__ == "__main__":
    main()
