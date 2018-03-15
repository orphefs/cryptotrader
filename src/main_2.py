import logging
import os
import time
from typing import List

import matplotlib
from datetime import timedelta

from live_logic.strategy import SMAStrategy, Parameters, LiveParameters, Portfolio, Buy, Hold
from plotting.plot_candles import plot_portfolio, plot_portfolio_2, plot_close_price
from tools.downloader import download_live_data, load_from_disk, simulate_live_data, StockData, \
    calculate_sampling_rate_of_stock_data

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
    data = load_from_disk(
        "/home/orphefs/Documents/Code/autotrader/autotrader/data/_data_01_Jan,_2017_10_Oct,_2017_LTCBTC.dill")
    logging.info("Sampling rate of backtesting data: {}".format(calculate_sampling_rate_of_stock_data(data)))


    i = 10
    while enabled:
        try:
            # stock_data = download_live_data(client, "XRPBTC")
            stock_data = simulate_live_data(data, i)
            print(i)
            i += 1
            if i == 2106:
                break

        except Exception:
            break

        strategy.extract_time_series_from_stock_data(stock_data)
        strategy.compute_moving_averages()
        signal = strategy.generate_trading_signal()
        print(signal)
        portfolio.update(signal)

        time.sleep(parameters.sleep_time)

    fig, ax = plt.subplots(nrows=3, ncols=1)
    portfolio.compute_statistics()
    plot_portfolio_2(ax[1:3], portfolio._portfolio_df)
    plot_close_price(ax=ax[0], data=data)
    plt.show()
    plot_close_price()


if __name__ == "__main__":
    main()
