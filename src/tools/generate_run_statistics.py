import os
from argparse import ArgumentParser
from typing import Tuple, List, Union

import matplotlib.pyplot as plt
import numpy as np

from src.backtesting_logic.logic import Sell, Buy, Hold
from src.definitions import DATA_DIR
from src.live_logic.portfolio import Portfolio
from src.tools.run_metadata import FullPaths


def load_portfolio(path_to_portfolio_df_dill: str) -> Portfolio:
    if path_to_portfolio_df_dill is None:
        path_to_portfolio_df_dill = os.path.join(DATA_DIR, "portfolio_df.dill")
    portfolio = Portfolio.load_from_disk(path_to_portfolio_df_dill)
    portfolio.compute_performance()
    return portfolio


def extract_signals_from_portfolio(portfolio: Portfolio) -> List[Union[Buy, Sell, Hold]]:
    return portfolio.signals


def cleanup_signals(signals: List[Union[Buy, Sell, Hold]]) -> List[Union[Buy, Sell]]:
    return [signal for signal in signals if isinstance(signal, Buy) or isinstance(signal, Sell)]


def generate_order_pairs(signals: List[Union[Buy, Sell]]) -> List[Tuple[Buy, Sell]]:
    if isinstance(signals[0], Buy):
        print("First order is a Buy order...")
        order_pairs = list(zip(signals[1::2], signals[0::2]))
    else:
        print("First order is a Sell order...")
        order_pairs = list(zip(signals[2::2], signals[1::2]))
    return order_pairs


def compute_profits_and_losses(order_pairs: List[Tuple[Buy, Sell]]) -> np.array:
    net = np.array([sell.price_point.value - buy.price_point.value for sell, buy in order_pairs])
    return net


def compute_ratio_of_profit_to_loss(net: np.array) -> float:
    ratio_of_profit_to_loss = np.abs(np.sum(net[net > 0]) / np.sum(net[net < 0]))
    print("Profit to Loss ratio: {}".format(ratio_of_profit_to_loss))
    return ratio_of_profit_to_loss


def plot_histograms(net: np.array):
    plt.hist(net[net > 0])
    plt.hist(net[net < 0])
    plt.xlabel("Net Profit")
    plt.ylabel("Count")
    plt.title("Profits vs. Losses (Ratio of profit to loss: {})".format(
        compute_ratio_of_profit_to_loss(net)))
    plt.show()


def main(path_to_portfolio_df_dill: str):
    portfolio = load_portfolio(path_to_portfolio_df_dill)
    signals = extract_signals_from_portfolio(portfolio)
    signals = cleanup_signals(signals)
    order_pairs = generate_order_pairs(signals)
    net = compute_profits_and_losses(order_pairs)
    plot_histograms(net)


if __name__ == '__main__':
    parser = ArgumentParser(description="Convert metadata dill into csv")
    parser.add_argument("-i", dest="input_filename", required=False,
                        help="input .dill", action=FullPaths)
    args = parser.parse_args()
    print("Input from {}".format(args.input_filename))
    main(args.input_filename)
