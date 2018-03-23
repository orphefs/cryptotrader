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
    plot_candlesticks, plot_moving_average, custom_plot
from tools.downloader import download_live_data, load_from_disk, serve_windowed_stock_data, \
    calculate_sampling_rate_of_stock_data
from containers.stock_data import StockData

matplotlib.use('AGG')  # generate postscript output by default
import matplotlib.pyplot as plt
from binance.client import Client
import definitions

logging.basicConfig(filename=os.path.join(definitions.DATA_DIR, 'local_autotrader.log'), level=logging.INFO)
enabled = True
parameters = LiveParameters(short_sma_period=timedelta(hours=2),
                            long_sma_period=timedelta(hours=20),
                            trade_amount=100,
                            sleep_time=0)


def main():
    client = Client("", "")
    strategy = SMAStrategy(parameters)
    portfolio = Portfolio(initial_capital=0.5, trade_amount=parameters.trade_amount)
    stock_data = load_from_disk(
        os.path.join(definitions.DATA_DIR, "local_data_15_Jan,_2018_01_Mar,_2018_XRPBTC.dill"))
    logging.info("Sampling rate of backtesting data: {}".format(calculate_sampling_rate_of_stock_data(stock_data)))
    trading_signals = []
    window_start = 10
    iteration = 10

    short_smas = []
    long_smas = []

    while enabled:
        # stock_data = download_live_data(client, "XRPBTC")
        iteration, stock_data_window = serve_windowed_stock_data(stock_data, iteration, window_start)
        if iteration == len(stock_data) - 2:
            break

        strategy.extract_time_series_from_stock_data(stock_data_window)
        strategy.compute_moving_averages()

        # TODO: Compute custom rolling average
        short_smas.append(strategy._short_sma)
        long_smas.append(strategy._long_sma)

        signal = strategy.generate_trading_signal()
        trading_signals.append(signal)
        # print(signal)
        portfolio.update(signal)
        time.sleep(parameters.sleep_time)

    portfolio.compute_performance()
    # custom_plot(portfolio, trading_signals, parameters, stock_data)
    print(portfolio._point_stats['base_index_pct_change'])
    print(portfolio._point_stats['total_pct_change'])

    plt.figure()
    plt.plot(long_smas)

    plt.show()


if __name__ == "__main__":
    main()
