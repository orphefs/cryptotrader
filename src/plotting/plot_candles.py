from typing import List, Union

import matplotlib.dates as mdate
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.axis import Axis
from matplotlib.dates import DateFormatter, WeekdayLocator, \
    DayLocator, MONDAY

from src.containers.intersection_point import IntersectionPoint
from src.containers.signal import SignalBuy, SignalSell, SignalHold
from src.containers.portfolio import Portfolio
from src.containers.candle import Candle
from src.containers.stock_data import StockData
from src.containers.time_series import TimeSeries
from src.externals.mpl_finance.mpl_finance import candlestick_ohlc


def plot_close_price(ax: Axes, candles: List[Candle], color: str = None):
    if color is None:
        color = 'k'
    ax.scatter(
        y=[candle.get_close_price() for candle in candles],
        x=[candle.get_close_time_as_datetime() for candle in candles],
        c=color, alpha=0.3
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
    if 'order_expenditure' in portfolio_df:
        portfolio_df['order_expenditure'].plot(ax=ax[0], alpha=0.7)
    if 'cumulative_order_expenditure' in portfolio_df:
        portfolio_df['cumulative_order_expenditure'].plot(ax=ax[1], alpha=0.7)
    if 'remaining_capital' in portfolio_df:
        portfolio_df['remaining_capital'].plot(ax=ax[2], alpha=0.7)
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


def plot_trading_signals(ax: Axes, trading_signals: List[Union[SignalBuy, SignalSell, SignalHold]], color: str = None, **kwargs):
    if color is None:
        color = 'k'

    marker_map = {
        "Buy": '^',
        "Sell": 'v',
        "Hold": "",
    }
    markers = [marker_map[trading_signal.type.__name__] for trading_signal in trading_signals]

    prices = []
    for marker, trading_signal in zip(markers, trading_signals):
        if marker != "":
            prices.append(trading_signal.price_point.value)
            ax.scatter(
                trading_signal.price_point.date_time,
                trading_signal.price_point.value,
                40,
                color,
                marker,
                kwargs
            )
    ax.set_ylim(min(prices), max(prices))


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
    ax.set_title(data.trading_pair)


def custom_plot(portfolio, strategy, title=None):
    fig, ax = plt.subplots(nrows=4, ncols=1, sharex=True)
    ax[0].set_title(title)
    plot_portfolio_2(ax[1:4], portfolio.portfolio_df)
    plot_trading_signals(ax=ax[0], trading_signals=portfolio.signals[1:])
    if strategy is not None:
        plot_moving_average(ax=ax[0], time_series=strategy._short_sma)
        plot_moving_average(ax=ax[0], time_series=strategy._long_sma)
        # plot_candlesticks(ax=ax, data=stock_data)
        # plot_close_price(ax=ax[0], data=stock_data)
        #
        # for x in ax:
        #     x.grid()
