import logging
import os
import time
from typing import List

import matplotlib
from datetime import timedelta

from backtesting_logic.signal_processing import rolling_mean
from containers.time_series import TimeSeries
from helpers import extract_time_series_from_stock_data
from live_logic.strategy import SMAStrategy, Parameters, LiveParameters, Portfolio, Buy, Hold
from plotting.plot_candles import plot_portfolio, plot_portfolio_2, plot_close_price, plot_trading_signals, \
    plot_candlesticks, plot_moving_average
from tools.downloader import download_live_data, load_from_disk, simulate_live_data, \
    calculate_sampling_rate_of_stock_data
from containers.stock_data import StockData

matplotlib.use('AGG')  # generate postscript output by default
import matplotlib.pyplot as plt

from binance.client import Client

import definitions

logging.basicConfig(filename=os.path.join(definitions.DATA_DIR, '_autotrader.log'), level=logging.INFO)
enabled = True
parameters = LiveParameters(short_sma_period=timedelta(hours=2),
                            long_sma_period=timedelta(hours=10),
                            trade_amount=100,
                            sleep_time=0)


def main():
    client = Client("", "")
    strategy = SMAStrategy(parameters)
    portfolio = Portfolio(initial_capital=1000.0, trade_amount=parameters.trade_amount)
    stock_data = load_from_disk(
        "/home/orphefs/Documents/Code/autotrader/autotrader/data/_data_01_Jan,_2017_10_Oct,_2017_LTCBTC.dill")
    logging.info("Sampling rate of backtesting data: {}".format(calculate_sampling_rate_of_stock_data(stock_data)))
    trading_signals = []

    i = 10
    while enabled:
        try:
            # stock_data = download_live_data(client, "XRPBTC")
            stock_data_partial = simulate_live_data(stock_data, i)
            print(i)
            i += 1
            if i == 2106:
                break

        except Exception:
            break

        strategy.extract_time_series_from_stock_data(stock_data_partial)
        strategy.compute_moving_averages()
        signal = strategy.generate_trading_signal()
        trading_signals.append(signal)
        print(signal)
        portfolio.update(signal)

        time.sleep(parameters.sleep_time)

    fig, ax = plt.subplots(nrows=3, ncols=1, sharex=True)
    portfolio.compute_statistics()
    plot_portfolio_2(ax[1:3], portfolio._portfolio_df)
    # plot_close_price(ax=ax[0], data=stock_data)
    plot_trading_signals(ax=ax[0], trading_signals=trading_signals[1:])
    plot_moving_average(ax=ax[0], time_series=rolling_mean(parameters.short_sma_period,
                                                           extract_time_series_from_stock_data(stock_data)))
    plot_moving_average(ax=ax[0], time_series=rolling_mean(parameters.long_sma_period,
                                                           extract_time_series_from_stock_data(stock_data)))

    # plot_candlesticks(ax[0], stock_data)
    plt.show()
    plot_close_price()


if __name__ == "__main__":
    main()
