import logging
import os
import time
from datetime import timedelta

# matplotlib.use('AGG')  # generate postscript output by default
import matplotlib.pyplot as plt

import definitions
from live_logic.strategy import SMAStrategy
from live_logic.parameters import LiveParameters
from live_logic.portfolio import Portfolio
from plotting.plot_candles import custom_plot
from tools.downloader import load_from_disk, calculate_sampling_rate_of_stock_data

logging.basicConfig(filename=os.path.join(definitions.DATA_DIR, 'local_autotrader.log'), level=logging.INFO)
enabled = True
parameters = LiveParameters(
    short_sma_period=timedelta(hours=2),
    long_sma_period=timedelta(hours=20),
    update_period=timedelta(hours=1),
    trade_amount=1000,
    sleep_time=0
)


def main():
    strategy = SMAStrategy(parameters)
    portfolio = Portfolio(initial_capital=0.5,
                          trade_amount=parameters.trade_amount)
    stock_data = load_from_disk(
        os.path.join(definitions.DATA_DIR, "local_data_01_Oct,_2017_01_Mar,_2018_XRPBTC.dill"))
    # logging.info("Sampling rate of backtesting data: {}".format(calculate_sampling_rate_of_stock_data(stock_data)))

    i = 0

    while enabled:
        candle = stock_data.candles[i]
        if i == len(stock_data.candles) - 1:
            break

        strategy.insert_new_data(candle)

        if i > 1:
            signal = strategy.generate_trading_signal()
            # TODO: add market maker
            # order = classifier.update(signal)

            portfolio.update(signal)
        time.sleep(parameters.sleep_time)
        i += 1

    portfolio.compute_performance()
    custom_plot(portfolio, strategy, parameters, stock_data)
    print(portfolio._point_stats['base_index_pct_change'])
    print(portfolio._point_stats['total_pct_change'])

    plt.show()


if __name__ == "__main__":
    main()
