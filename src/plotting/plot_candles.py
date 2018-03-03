import matplotlib.dates as mdate
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.axis import Axis
from matplotlib.dates import DateFormatter, WeekdayLocator, \
    DayLocator, MONDAY
from matplotlib.finance import candlestick_ohlc
from typing import List, Optional

from tools.downloader import load_from_disk, StockData


def plot_close_price(ax: Axis, data: StockData):
    ax.scatter(
        y=[candle.get_price().close_price for candle in data.candles],
        x=[candle.get_time().close_time.as_datetime() for candle in data.candles],
    )


def plot_returns(ax: Axes, stock_data: StockData, returns: List[float]):
    ax.scatter(x=[mdate.date2num(candle.get_time().close_time.as_datetime())
               for candle in stock_data.candles][0:-1],
            y=returns)


def plot_candlesticks(ax: Axes, data: StockData):
    lines, patches = candlestick_ohlc(ax=ax,
                                      quotes=[
                                          (mdate.date2num(candle.get_time().close_time.as_datetime()),
                                           candle.get_price().open_price,
                                           candle.get_price().high_price,
                                           candle.get_price().low_price,
                                           candle.get_price().close_price)
                                          for candle in data.candles],
                                      width=0.01)
    for p in patches:
        ax.add_patch(p)
    for l in lines:
        ax.add_line(l)

    mondays = WeekdayLocator(MONDAY)  # major ticks on the mondays
    alldays = DayLocator()  # minor ticks on the days
    weekFormatter = DateFormatter('%b %d')  # e.g., Jan 12
    dayFormatter = DateFormatter('%d')  # e.g., 12
    ax.xaxis.set_major_locator(mondays)
    ax.xaxis.set_minor_locator(alldays)
    ax.xaxis.set_major_formatter(weekFormatter)
    ax.xaxis_date()
    ax.autoscale_view()
    plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
    ax.set_title(data.security)


if __name__ == '__main__':
    stock_data = load_from_disk(
        '/home/orphefs/Documents/Code/autotrader/autotrader/data/_data_01_Oct,_2017_10_Oct,_2017_LTCBTC.dill')
    fig, ax = plt.subplots()

    plot_candlesticks(ax, stock_data)
    plt.show()
