from datetime import timedelta

from logic.logic import TimeSeries, simple_moving_average
from plotting.plot_candles import plot_candlesticks, plot_moving_average
from tools.downloader import load_from_disk
import matplotlib.pyplot as plt
import numpy as np

def main():
    # time_series_a = TimeSeries(x=[datetime(2017, 1, d) for d in range(1, 30)], y=np.random.normal(5, 1, 29))
    # time_series_b = TimeSeries(x=[datetime(2017, 1, d) for d in range(1, 30)], y=np.random.normal(6, 3, 29))
    stock_data = load_from_disk(
        '/home/orphefs/Documents/Code/autotrader/autotrader/data/_data_01_Jan,_2017_10_Oct,_2017_LTCBTC.dill')
    fig, ax = plt.subplots()
    time_series_orig = TimeSeries(y=np.array([candle.get_price().close_price for candle in stock_data.candles]),
                                  x=[candle.get_time().close_time.as_datetime() for candle in stock_data.candles])
    time_series_sma10 = simple_moving_average(timedelta(hours=10), time_series_orig)
    time_series_sma2 = simple_moving_average(timedelta(hours=2), time_series_orig)
    plot_candlesticks(ax, stock_data)
    plot_moving_average(ax, time_series_sma10)
    plot_moving_average(ax, time_series_sma2)
    plt.show()

    # intersection_points = get_intersection_points(avg_time_series_a, avg_time_series_b, 1)
    # for intersection_point in intersection_points:
    #     print(intersection_point)

if __name__=="__main__":
    main()