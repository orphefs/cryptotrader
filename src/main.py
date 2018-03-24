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

# matplotlib.use('AGG')  # generate postscript output by default
import matplotlib.pyplot as plt
from binance.client import Client
import definitions

logging.basicConfig(filename=os.path.join(definitions.DATA_DIR, 'local_autotrader.log'), level=logging.INFO)
enabled = True
parameters = LiveParameters(
    short_sma_period=timedelta(hours=2),
    long_sma_period=timedelta(hours=20),
    update_period=timedelta(hours=1),
    trade_amount=100,
    sleep_time=0
)


def main():
    client = Client("", "")
    strategy = SMAStrategy(parameters)
    portfolio = Portfolio(initial_capital=0.5,
                          trade_amount=parameters.trade_amount)
    stock_data = load_from_disk(
        os.path.join(definitions.DATA_DIR, "local_data_15_Jul,_2017_01_Mar,_2018_XRPBTC.dill"))
    logging.info("Sampling rate of backtesting data: {}".format(calculate_sampling_rate_of_stock_data(stock_data)))
    trading_signals = []

    i = 0

    while enabled:
        candle = stock_data.candles[i]
        if i == len(stock_data.candles) - 1:
            break

        strategy.update_moving_averages(candle)

        if i > 1:
            signal = strategy.generate_trading_signal()

            trading_signals.append(signal)
            portfolio.update(signal)
        time.sleep(parameters.sleep_time)
        i += 1

    portfolio.compute_performance()
    custom_plot(portfolio, strategy, trading_signals, parameters, stock_data)
    print(portfolio._point_stats['base_index_pct_change'])
    print(portfolio._point_stats['total_pct_change'])

    plt.show()


if __name__ == "__main__":
    main()
