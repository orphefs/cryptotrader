from argparse import ArgumentParser
from typing import List

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes

from src.backtesting_logic.logic import _TradingSignal
from src.containers.candle import Candle, Price
from src.containers.time import Time, MilliSeconds
from src.live_logic.portfolio import Portfolio
from src.plotting.plot_candles import plot_trading_signals, plot_close_price
from src.tools.generate_run_statistics import compute_all_statistics
from src.tools.run_metadata import FullPaths


def convert_signals_to_mock_candles(signals: List[_TradingSignal]) -> List[Candle]:
    return [Candle(price=Price(
        open_price=None,
        high_price=None,
        low_price=None,
        close_price=signal.price_point.value),
        volume=None,
        time=Time(open_time=None, close_time=MilliSeconds(
            signal.price_point.date_time.timestamp()))) for signal in signals]


def display_statistics(title: str, axis: Axes, path_to_live_portfolio_df_dill: str):
    order_pairs, percentage_gains, index_performance = \
        compute_all_statistics(path_to_live_portfolio_df_dill)
    axis.set_title("{}, {} \n  {}".format(title, percentage_gains, index_performance))


def main(path_to_live_portfolio_df_dill: str = None,
         path_to_mock_portfolio_df_dill: str = None,
         path_to_backtest_portfolio_df_dill: str = None):
    fig, ax = plt.subplots(nrows=3, ncols=1, sharex="all", sharey="all")

    live_signals = []
    mock_signals = []
    backtest_signals = []

    if path_to_live_portfolio_df_dill is not None:
        live_portfolio_df = Portfolio.load_from_disk(path_to_live_portfolio_df_dill)
        live_signals = live_portfolio_df.signals[1:]
        plot_trading_signals(ax=ax[0], trading_signals=live_signals, color='k', label="live")
        plot_close_price(ax=ax[0], candles=convert_signals_to_mock_candles(live_signals), color="k")
        live_signals = [signal.price_point.date_time for signal in live_signals]
        display_statistics("Live Run", ax[0], path_to_live_portfolio_df_dill)

    if path_to_mock_portfolio_df_dill is not None:
        mock_portfolio_df = Portfolio.load_from_disk(path_to_mock_portfolio_df_dill)
        mock_signals = mock_portfolio_df.signals[1:]
        plot_trading_signals(ax=ax[1], trading_signals=mock_signals, color='r', label="mock")
        mock_signals = [signal.price_point.date_time for signal in mock_signals]
        display_statistics("Mock Run", ax[1], path_to_mock_portfolio_df_dill)

    if path_to_backtest_portfolio_df_dill is not None:
        backtest_portfolio_df = Portfolio.load_from_disk(path_to_backtest_portfolio_df_dill)
        backtest_signals = backtest_portfolio_df.signals[1:]
        plot_trading_signals(ax=ax[2], trading_signals=backtest_signals, color='b', label="backtest")
        backtest_signals = [signal.price_point.date_time for signal in backtest_signals]
        display_statistics("Backtest Run", ax[2], path_to_backtest_portfolio_df_dill)

    dt = np.concatenate([live_signals, mock_signals, backtest_signals])
    ax[0].set_xlim(xmin=np.min(dt), xmax=np.max(dt))

    plt.show()


if __name__ == '__main__':
    parser = ArgumentParser(description="Convert metadata dill into csv")
    parser.add_argument("-live", dest="path_to_live_portfolio_df_dill", required=False,
                        help="live_portfolio_df.dill", action=FullPaths)
    parser.add_argument("-mock", dest="path_to_mock_portfolio_df_dill", required=False,
                        help="mock_portfolio_df.dill", action=FullPaths)
    parser.add_argument("-backtest", dest="path_to_backtest_portfolio_df_dill", required=False,
                        help="backtest_portfolio_df.dill", action=FullPaths)
    args = parser.parse_args()
    main(args.path_to_live_portfolio_df_dill,
         args.path_to_mock_portfolio_df_dill,
         args.path_to_backtest_portfolio_df_dill)
