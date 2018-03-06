from datetime import timedelta
import os
import matplotlib.pyplot as plt
import numpy as np

from logic.logic import TimeSeries, _generate_trading_signals_from_sma, rolling_mean, MarketOnClosePortfolio
from src.plotting.plot_candles import plot_moving_average, plot_trading_signals, plot_close_price, plot_portfolio
from tools.downloader import load_from_disk
import definitions


def main():
    # time_series_a = TimeSeries(x=[datetime(2017, 1, d) for d in range(1, 30)], y=np.random.normal(5, 1, 29))
    # time_series_b = TimeSeries(x=[datetime(2017, 1, d) for d in range(1, 30)], y=np.random.normal(6, 3, 29))
    stock_data = load_from_disk(os.path.join(definitions.DATA_DIR,'_data_01_Jan,_2017_10_Oct,_2017_LTCBTC.dill'))
    fig, ax = plt.subplots(nrows=3,ncols=1, sharex=True)
    time_series_orig = TimeSeries(y=np.array([candle.get_price().close_price for candle in stock_data.candles]),
                                  x=[candle.get_time().close_time.as_datetime() for candle in stock_data.candles])
    time_series_sma10 = rolling_mean(timedelta(hours=3), time_series_orig)
    time_series_sma2 = rolling_mean(timedelta(hours=7), time_series_orig)
    trading_signals = _generate_trading_signals_from_sma(time_series_orig, time_series_sma2, time_series_sma10)
    plot_close_price(ax[0], stock_data)
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