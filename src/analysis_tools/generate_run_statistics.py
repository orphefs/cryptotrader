import os
from argparse import ArgumentParser
from datetime import timedelta
from typing import Tuple, List, Union

import matplotlib.pyplot as plt
import numpy as np

from src.backtesting_logic.logic import Sell, Buy, Hold
from src.containers.portfolio import Portfolio
from src.containers.time_windows import TimeWindow
from src.definitions import DATA_DIR
from src.analysis_tools.run_metadata import FullPaths


class _Gains:
    def __init__(self, gains: float, elapsed_time: timedelta):
        self.gains = gains
        self.elapsed_time = elapsed_time


class PercentageGains(_Gains):
    def __str__(self):
        return "Gained {} percent within timeframe of {}.".format(self.gains * 100, self.elapsed_time)


class IndexPerformance(_Gains):
    def __str__(self):
        return "The asset price changed by {} percent within timeframe of {}.".format(self.gains * 100,
                                                                                      self.elapsed_time)


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


def display_timeframe(order_pairs: List[Tuple[Buy, Sell]]) -> str:
    return "Run started on {} and ended on {}".format(order_pairs[0][1].price_point.date_time,
                                                      order_pairs[-1][1].price_point.date_time)


def compute_testing_window(order_pairs: List[Tuple[Buy, Sell]]) -> TimeWindow:
    return TimeWindow(order_pairs[0][1].price_point.date_time, order_pairs[-1][1].price_point.date_time)


def calculate_percentage_gains(portfolio: Portfolio, order_pairs: List[Tuple[Buy, Sell]]) -> PercentageGains:
    net = compute_profits_and_losses(order_pairs)
    total_profit = np.sum(net)
    initial_investment = order_pairs[0][1].price_point.value * portfolio._trade_amount
    gains = (total_profit * portfolio._trade_amount) / initial_investment
    return PercentageGains(gains=gains, elapsed_time=order_pairs[-1][1].price_point.date_time -
                                                     order_pairs[0][1].price_point.date_time)


def calculate_index_performance(order_pairs: List[Tuple[Buy, Sell]]) -> IndexPerformance:
    index_gains = (order_pairs[-1][1].price_point.value - order_pairs[0][1].price_point.value) / order_pairs[0][
        1].price_point.value
    return IndexPerformance(gains=index_gains, elapsed_time=order_pairs[-1][1].price_point.date_time -
                                                            order_pairs[0][1].price_point.date_time)


def compute_all_statistics(path_to_portfolio_df_dill: str):
    portfolio = load_portfolio(path_to_portfolio_df_dill)
    signals = extract_signals_from_portfolio(portfolio)
    signals = cleanup_signals(signals)
    order_pairs = generate_order_pairs(signals)
    percentage_gains = calculate_percentage_gains(portfolio, order_pairs)
    index_performance = calculate_index_performance(order_pairs)
    net = compute_profits_and_losses(order_pairs)
    classifier_time_window = portfolio.classifier.training_time_window
    testing_time_window = compute_testing_window(order_pairs)
    return order_pairs, percentage_gains, index_performance, classifier_time_window, testing_time_window


def display_and_plot(order_pairs: List[Tuple[Union[Buy, Sell]]],
                     percentage_gains: PercentageGains,
                     index_performance: IndexPerformance,
                     classifier_time_window: TimeWindow,
                     ):
    print("Classifier training period: {}".format(classifier_time_window))
    print(display_timeframe(order_pairs))
    print(percentage_gains)
    print(index_performance)

    plot_histograms(compute_profits_and_losses(order_pairs))


if __name__ == '__main__':
    parser = ArgumentParser(description="Convert metadata dill into csv")
    parser.add_argument("-i", dest="input_filename", required=False,
                        help="input .dill", action=FullPaths)
    args = parser.parse_args()
    print("Input from {}".format(args.input_filename))
    order_pairs, percentage_gains, index_performance, \
    classifier_time_window, testing_time_window = compute_all_statistics(args.input_filename)
    display_and_plot(order_pairs, percentage_gains, index_performance, classifier_time_window)
