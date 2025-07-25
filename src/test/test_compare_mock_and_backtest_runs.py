import os
from importlib import reload
from typing import Tuple, List
import logging
import pytest

from src.analysis_tools.generate_run_statistics import cleanup_signals
from src.containers.portfolio import Portfolio
from src.definitions import DATA_DIR, TEST_DATA_DIR
from src.run_backtest import run_backtest
from src.run_offline import run_offline
from src.containers.trading_pair import TradingPair


def run():
    path_to_offline_portfolio, _ = run_offline(trading_pair=TradingPair("NEO", "BTC"),
                                               trade_amount=100,
                                               path_to_stock_data=os.path.join(
                                                   TEST_DATA_DIR, "test_data_long.dill"),
                                               path_to_classifier=os.path.join(
                                                   TEST_DATA_DIR, "classifier.dill"),
                                               path_to_log=os.path.join(TEST_DATA_DIR, "offline_run.log")
                                               )

    logging.shutdown()  # temporary workaround to reinit logging for next run's log
    reload(logging)

    path_to_backtest_portfolio, _ = run_backtest(trading_pair=TradingPair("NEO", "BTC"),
                                                 trade_amount=100,
                                                 path_to_stock_data=os.path.join(
                                                     TEST_DATA_DIR, "test_data_long.dill"),
                                                 path_to_classifier= os.path.join(TEST_DATA_DIR, "classifier.dill"))

    return path_to_offline_portfolio, path_to_backtest_portfolio


def load_portfolio(path_to_offline_portfolio_df: str,
                   path_to_backtest_portfolio_df: str) -> Tuple[Portfolio, Portfolio]:
    offline_portfolio = Portfolio.load_from_disk(path_to_offline_portfolio_df)
    backtest_portfolio = Portfolio.load_from_disk(path_to_backtest_portfolio_df)

    return offline_portfolio, backtest_portfolio


def compare_lists(a: List, b: List):
    if not len(a) == len(b):
        return False
    return len(a) == len([i for i, j in zip(a, b) if i == j])


def compare(offline_portfolio: Portfolio, backtest_portfolio: Portfolio):
    for signal in offline_portfolio.signals:
        print(signal)

    offline_signals = cleanup_signals(offline_portfolio.signals)
    backtest_signals = cleanup_signals(backtest_portfolio.signals)

    for t, b in zip(offline_signals, backtest_signals):
        print("offline run: {}".format(t))
        print("backtest_run: {}".format(b))
        print("\n")

    assert compare_lists(offline_signals, backtest_signals)


def test_compare_runs():
    path_to_offline_portfolio_df, path_to_backtest_portfolio_df = run()
    offline_portfolio, backtest_portfolio = load_portfolio(
        path_to_offline_portfolio_df, path_to_backtest_portfolio_df)
    compare(offline_portfolio, backtest_portfolio)

if __name__ == '__main__':
    test_compare_runs()