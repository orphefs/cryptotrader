from typing import List
import pandas as pd
import matplotlib.dates as mdate
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.axis import Axis
from matplotlib.dates import DateFormatter, WeekdayLocator, \
    DayLocator, MONDAY
from externals.mpl_finance.mpl_finance import candlestick_ohlc

from backtesting_logic.logic import IntersectionPoint, TradingSignal
from containers.time_series import TimeSeries
from backtesting_logic.portfolio import Portfolio
from helpers import extract_time_series_from_stock_data
from tools.downloader import load_from_disk
from containers.stock_data import StockData
from backtesting_logic.signal_processing import rolling_mean


def plot_close_price(ax: Axis, data: StockData):
    ax.scatter(
        y=[candle.get_close_price() for candle in data.candles],
        x=[candle.get_close_time_as_datetime() for candle in data.candles],
        c='r', alpha=0.3
    )


def plot_portfolio(ax: List[Axis], portfolio: Portfolio):
    if 'holdings' in portfolio.portfolio:
        portfolio.portfolio['holdings'].plot(ax=ax[0], alpha=0.7)
    if 'cash' in portfolio.portfolio:
        portfolio.portfolio['cash'].plot(ax=ax[1], alpha=0.7)
    if 'total' in portfolio.portfolio:
        portfolio.portfolio['total'].plot(ax=ax[1], alpha=0.7)
    if 'returns' in portfolio.portfolio:
        portfolio.portfolio['returns'].plot(ax=ax[0], alpha=0.7)
    ax[0].legend()
    ax[1].legend()


def plot_portfolio_2(ax: List[Axis], portfolio_df: pd.DataFrame):
    if 'holdings' in portfolio_df:
        portfolio_df['holdings'].plot(ax=ax[0], alpha=0.7)
    if 'cash' in portfolio_df:
        portfolio_df['cash'].plot(ax=ax[2], alpha=0.7)
    if 'total' in portfolio_df:
        portfolio_df['total'].plot(ax=ax[2], alpha=0.7)
    if 'returns' in portfolio_df:
        portfolio_df['returns'].plot(ax=ax[1], alpha=0.7)
    ax[0].legend()
    ax[1].legend()


def plot_returns(ax: Axes, stock_data: StockData, returns: List[float]):
    ax.scatter(x=[mdate.date2num(candle.get_close_time_as_datetime())
                  for candle in stock_data.candles][0:-1],
               y=returns)


def plot_moving_average(ax: Axes, time_series: TimeSeries):
    time_series.plot(kind='line', marker='', ax=ax)
    ax.set_ylim(time_series.min(), time_series.max())


def plot_intersection_point(ax: Axes, intersection_point: IntersectionPoint):
    ax.scatter(y=intersection_point.data_point.value, x=intersection_point.data_point.date_time)


def plot_trading_signals(ax: Axes, trading_signals: List[TradingSignal]):
    marker_map = {
        "Buy": '^',
        "Sell": 'v',
        "Hold": "",
    }
    markers = [marker_map[trading_signal.type] for trading_signal in trading_signals]

    for marker, trading_signal in zip(markers, trading_signals):
        if marker != "":
            ax.scatter(
                x=trading_signal.price_point.date_time,
                y=trading_signal.price_point.value,
                marker=marker,
                color='k',
                s=40
            )


def plot_candlesticks(ax: Axes, data: StockData):
    lines, patches = candlestick_ohlc(ax=ax,
                                      quotes=[
                                          (mdate.date2num(candle.get_close_time_as_datetime()),
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


def custom_plot(portfolio, strategy, parameters, stock_data):
    fig, ax = plt.subplots(nrows=4, ncols=1, sharex=True)
    plot_portfolio_2(ax[1:4], portfolio._portfolio_df)
    plot_trading_signals(ax=ax[0], trading_signals=portfolio._signals[1:])
    plot_moving_average(ax=ax[0], time_series=strategy._short_sma)

    plot_moving_average(ax=ax[0], time_series=strategy._long_sma)

    # plot_close_price(ax=ax[0], data=stock_data)

    for x in ax:
        x.grid()
