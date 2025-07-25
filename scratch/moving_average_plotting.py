import os
from datetime import timedelta

import definitions
import matplotlib.pyplot as plt
import numpy as np
from src.backtesting_logic.portfolio import MarketOnClosePortfolio
from tools.downloader import load_from_disk

from src.containers.time_series import TimeSeries
from src.feature_extraction.signal_processing import rolling_mean, _generate_trading_signals_from_sma
from src.plotting.plot_candles import plot_moving_average, plot_trading_signals, plot_close_price, plot_portfolio


def main():
    # time_series_a = TimeSeries(x=[datetime(2017, 1, d) for d in range(1, 30)], y=np.random.normal(5, 1, 29))
    # time_series_b = TimeSeries(x=[datetime(2017, 1, d) for d in range(1, 30)], y=np.random.normal(6, 3, 29))
    stock_data = load_from_disk(os.path.join(definitions.DATA_DIR,'_data_01_Feb,_2018_01_Mar,_2018_XRPBTC.dill'))
    fig, ax = plt.subplots(nrows=3,ncols=1, sharex=True)
    time_series_orig = TimeSeries(y=np.array([candle.get_close_price() for candle in stock_data.candles]),
                                  x=[candle.get_close_time_as_datetime() for candle in stock_data.candles])
    time_series_sma10 = rolling_mean(timedelta(hours=20), time_series_orig)
    time_series_sma2 = rolling_mean(timedelta(hours=2), time_series_orig)
    trading_signals = _generate_trading_signals_from_sma(time_series_orig, time_series_sma2, time_series_sma10)
    plot_close_price(ax[0], stock_data.candles)
    plot_moving_average(ax[0], time_series_sma10)
    plot_moving_average(ax[0], time_series_sma2)
    plot_trading_signals(ax[0], trading_signals)

    portfolio = MarketOnClosePortfolio(stock_data=stock_data, trading_signals=trading_signals)
    plot_portfolio(ax[1:3], portfolio)

    # for intersection_point in intersection_points:
    #     print(intersection_point)
    plt.show()

if __name__=="__main__":
    main()