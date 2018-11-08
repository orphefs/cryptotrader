import os
from importlib import reload
from typing import Tuple, List
import logging

from src.containers.portfolio import Portfolio
from src.definitions import DATA_DIR
from src.run_backtest import run_backtest
from src.run_offline import run_offline


def run():
    path_to_offline_portfolio, _ = run_offline(trading_pair="NEOBTC",
                                               trade_amount=100,
                                               path_to_stock_data=os.path.join(
                                                   DATA_DIR, "test", "test_data.dill"),
                                               path_to_log=os.path.join(DATA_DIR, "offline_run.log")
                                               )

    logging.shutdown()  # temporary workaround to reinit logging for next run's log
    reload(logging)

    path_to_backtest_portfolio, _ = run_backtest(trading_pair="NEOBTC",
                                                 trade_amount=100,
                                                 path_to_stock_data=os.path.join(
                                                     DATA_DIR, "test", "test_data.dill"))

    return path_to_offline_portfolio, path_to_backtest_portfolio


def load_portfolio(path_to_offline_portfolio_df: str,
                   path_to_backtest_portfolio_df: str) -> Tuple[Portfolio, Portfolio]:
    offline_portfolio = Portfolio.load_from_disk(path_to_offline_portfolio_df)
    backtest_portfolio = Portfolio.load_from_disk(path_to_backtest_portfolio_df)

    return offline_portfolio, backtest_portfolio


def compare_lists(a: List, b: List):
    if not len(a) == len(b):
        return False
    return len(a) == sum([1 for i, j in zip(a, b) if i == j])


def compare(offline_portfolio: Portfolio, backtest_portfolio: Portfolio):
    offline_signals = offline_portfolio.signals
    backtest_signals = backtest_portfolio.signals

    for t, b in zip(offline_signals, backtest_signals):
        print("offline run: {}".format(t))
        print("backtest_run: {}".format(b))
        print("\n")

    assert compare_lists(offline_signals, backtest_signals)


def main():
    path_to_offline_portfolio_df, path_to_backtest_portfolio_df = run()
    offline_portfolio, backtest_portfolio = load_portfolio(
        path_to_offline_portfolio_df, path_to_backtest_portfolio_df)
    compare(offline_portfolio, backtest_portfolio)


if __name__ == '__main__':
    main()
