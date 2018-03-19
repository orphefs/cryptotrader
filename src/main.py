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
from tools.downloader import download_live_data, load_from_disk, serve_windowed_stock_data, \
    calculate_sampling_rate_of_stock_data
from containers.stock_data import StockData

matplotlib.use('AGG')  # generate postscript output by default
import matplotlib.pyplot as plt

from binance.client import Client

import definitions

logging.basicConfig(filename=os.path.join(definitions.DATA_DIR, '_autotrader.log'), level=logging.INFO)
enabled = True
parameters = LiveParameters(short_sma_period=timedelta(hours=3),
                            long_sma_period=timedelta(hours=8),
                            trade_amount=100,
                            sleep_time=0)


def main():
    client = Client("", "")
    strategy = SMAStrategy(parameters)
    portfolio = Portfolio(initial_capital=0.5, trade_amount=parameters.trade_amount)
    stock_data = load_from_disk(
        os.path.join(definitions.DATA_DIR, "_data_01_Oct,_2017_01_Mar,_2018_XRPBTC.dill"))
    logging.info("Sampling rate of backtesting data: {}".format(calculate_sampling_rate_of_stock_data(stock_data)))
    trading_signals = []
    window_start = 10
    iteration = 10

    while enabled:
        # stock_data = download_live_data(client, "XRPBTC")
        iteration, stock_data_window = serve_windowed_stock_data(stock_data, iteration, window_start)
        if iteration == len(stock_data)-2:
            break

        strategy.extract_time_series_from_stock_data(stock_data_window)
        strategy.compute_moving_averages()
        signal = strategy.generate_trading_signal()
        trading_signals.append(signal)
        # print(signal)
        portfolio.update(signal)

        time.sleep(parameters.sleep_time)

    fig, ax = plt.subplots(nrows=3, ncols=1, sharex=True)
    portfolio.compute_statistics()
    plot_portfolio_2(ax[1:3], portfolio._portfolio_df)
    plot_trading_signals(ax=ax[0], trading_signals=trading_signals[1:])
    plot_moving_average(ax=ax[0], time_series=rolling_mean(parameters.short_sma_period,
                                                           extract_time_series_from_stock_data(stock_data)))
    plot_moving_average(ax=ax[0], time_series=rolling_mean(parameters.long_sma_period,
                                                           extract_time_series_from_stock_data(stock_data)))

    print(portfolio._point_stats['base_index_pct_change'])
    print(portfolio._point_stats['total_pct_change'])

    plt.show()



if __name__ == "__main__":
    main()
