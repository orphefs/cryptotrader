import os
from typing import Tuple, List

import matplotlib.pyplot as plt
import numpy as np

from src.backtesting_logic.logic import Sell, Buy
from src.definitions import DATA_DIR
from src.live_logic.portfolio import Portfolio


def load_portfolio() -> Portfolio:
    portfolio = Portfolio.load_from_disk(os.path.join(DATA_DIR, "portfolio_df.dill"))
    portfolio.compute_performance()
    return portfolio


def generate_order_pairs(portfolio: Portfolio) -> List[Tuple[Buy, Sell]]:
    order_pairs = list(zip(portfolio.signals[1::2], portfolio.signals[0::2]))
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


if __name__ == '__main__':
    portfolio = load_portfolio()
    order_pairs = generate_order_pairs(portfolio)
    net = compute_profits_and_losses(order_pairs)
    plot_histograms(net)
