from argparse import ArgumentParser
from typing import List, Union

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes

from src.containers.signal import SignalBuy, SignalSell, SignalHold
from src.containers.candle import Candle, Price
from src.containers.portfolio import Portfolio
from src.containers.time import Time, MilliSeconds
from src.plotting.plot_candles import plot_trading_signals, plot_close_price
from src.analysis_tools.generate_run_statistics import compute_all_statistics
from src.analysis_tools.run_metadata import FullPaths


def convert_signals_to_backtest_candles(signals: List[Union[SignalBuy, SignalSell, SignalHold]]) -> List[Candle]:
    return [Candle(price=Price(
        open_price=None,
        high_price=None,
        low_price=None,
        close_price=signal.price_point.value),
        volume=None,
        time=Time(open_time=None, close_time=MilliSeconds(
            signal.price_point.date_time.timestamp()))) for signal in signals]


def display_statistics(title: str, axis: Axes, path_to_live_portfolio_df_dill: str):
    order_pairs, percentage_gains, index_performance, _,_ = \
        compute_all_statistics(path_to_live_portfolio_df_dill)
    axis.set_title("{}, {} \n  {}".format(title, percentage_gains, index_performance))


def main(path_to_live_portfolio_df_dill: str = None,
         path_to_backtest_portfolio_df_dill: str = None,
         path_to_offline_portfolio_df_dill: str = None):
    fig, ax = plt.subplots(nrows=3, ncols=1, sharex="all", sharey="all")

    ls, bs, ms = [], [], []

    if path_to_live_portfolio_df_dill is not None:
        live_portfolio_df = Portfolio.load_from_disk(path_to_live_portfolio_df_dill)
        live_signals = live_portfolio_df.signals
        plot_trading_signals(ax=ax[0], trading_signals=live_signals, color='k', label="live")
        plot_close_price(ax=ax[0], candles=convert_signals_to_backtest_candles(live_signals), color="k")
        ls = [signal.price_point.date_time for signal in live_signals]
        display_statistics("Live Run", ax[0], path_to_live_portfolio_df_dill)

    if path_to_backtest_portfolio_df_dill is not None:
        backtest_portfolio_df = Portfolio.load_from_disk(path_to_backtest_portfolio_df_dill)
        backtest_signals = backtest_portfolio_df.signals
        plot_trading_signals(ax=ax[1], trading_signals=backtest_signals, color='r', label="backtest")
        ms = [signal.price_point.date_time for signal in backtest_signals]
        display_statistics("backtest Run", ax[1], path_to_backtest_portfolio_df_dill)

    if path_to_offline_portfolio_df_dill is not None:
        offline_portfolio_df = Portfolio.load_from_disk(path_to_offline_portfolio_df_dill)
        offline_signals = offline_portfolio_df.signals
        plot_trading_signals(ax=ax[0], trading_signals=offline_signals, color='b', label="offline")
        bs = [signal.price_point.date_time for signal in offline_signals]
        display_statistics("offline Run", ax[2], path_to_offline_portfolio_df_dill)

    dt = np.concatenate([ls, ms, bs])
    ax[0].set_xlim(xmin=np.min(dt), xmax=np.max(dt))

    plt.show()


if __name__ == '__main__':
    parser = ArgumentParser(description="Convert metadata dill into csv")
    parser.add_argument("-live", dest="path_to_live_portfolio_df_dill", required=False,
                        help="live_portfolio_df.dill", action=FullPaths)
    parser.add_argument("-backtest", dest="path_to_backtest_portfolio_df_dill", required=False,
                        help="backtest_portfolio_df.dill", action=FullPaths)
    parser.add_argument("-offline", dest="path_to_offline_portfolio_df_dill", required=False,
                        help="offline_portfolio_df.dill", action=FullPaths)
    args = parser.parse_args()
    main(args.path_to_live_portfolio_df_dill,
         args.path_to_backtest_portfolio_df_dill,
         args.path_to_offline_portfolio_df_dill)
