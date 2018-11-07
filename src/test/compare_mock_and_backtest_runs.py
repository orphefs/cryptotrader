import logging
import os
from typing import Tuple, List

from src import definitions
from src.classification.train_classifier import run_trained_classifier
from src.containers.portfolio import Portfolio
from src.definitions import DATA_DIR
from src.resource_manager import runner
from src.run_backtest import run_backtest


def run():
    path_to_training_portfolio_df = run_backtest(trading_pair="NEOBTC",
                                                 trade_amount=100,
                                                 path_to_stock_data=os.path.join(DATA_DIR,"test", "test_data"))
    path_to_backtest_portfolio_df = run_backtest(trading_pair="NEOBTC",
                                                 trade_amount=100,
                                                 path_to_stock_data=os.path.join(DATA_DIR,"test", "test_data"))

    return path_to_training_portfolio_df, path_to_backtest_portfolio_df


def load_portfolio(path_to_training_portfolio_df: str, path_to_backtest_portfolio_df: str) -> Tuple[
    Portfolio, Portfolio]:
    training_portfolio = Portfolio.load_from_disk(path_to_training_portfolio_df)
    backtest_portfolio = Portfolio.load_from_disk(path_to_backtest_portfolio_df)

    return training_portfolio, backtest_portfolio


def compare_lists(a: List, b: List):
    if not len(a) == len(b):
        return False
    return len(a) == sum([1 for i, j in zip(a, b) if i == j])


def compare(training_portfolio: Portfolio, backtest_portfolio: Portfolio):
    training_signals = training_portfolio.signals
    backtest_signals = backtest_portfolio.signals
    assert compare_lists(training_signals, backtest_signals)


def main():
    path_to_training_portfolio_df, path_to_backtest_portfolio_df = run()
    training_portfolio, backtest_portfolio = load_portfolio(
        path_to_training_portfolio_df, path_to_backtest_portfolio_df)
    compare(training_portfolio, backtest_portfolio)


if __name__ == '__main__':
    main()
