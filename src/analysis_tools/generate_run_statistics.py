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


class TradingGains(_Gains):
    def __str__(self):
        return "Gained {} percent from trading within timeframe of {}.".format(self.gains * 100, self.elapsed_time)


class IndexGains(_Gains):
    def __str__(self):
        return "The asset price changed by {} percent within timeframe of {}.".format(self.gains * 100,
                                                                                      self.elapsed_time)


class NetGains(_Gains):
    def __str__(self):
        return "The net gains are {} percent within timeframe of {}.".format(self.gains * 100,
                                                                             self.elapsed_time)

    @staticmethod
    def from_index_and_trading_gains(index_gains, trading_gains):
        if index_gains.elapsed_time == trading_gains.elapsed_time:
            return NetGains(gains=trading_gains.gains - index_gains.gains,
                            elapsed_time=index_gains.elapsed_time)
        else:
            raise RuntimeError("Elapsed times must be identical "
                               "in order to compute net gains.")


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


def display_start_and_finish_prices(order_pairs: List[Tuple[Buy, Sell]]) -> str:
    return "Trading pair start price: {}, Trading pair finish price: {}".format(order_pairs[0][1].price_point.value,
                                                                                order_pairs[-1][1].price_point.value)


def display_total_number_of_orders(order_pairs: List[Tuple[Buy, Sell]]):
    return "Total number of buy/sell orders: {}".format(len(order_pairs) * 2)


def compute_testing_window(order_pairs: List[Tuple[Buy, Sell]]) -> TimeWindow:
    return TimeWindow(order_pairs[0][1].price_point.date_time, order_pairs[-1][1].price_point.date_time)


def calculate_trading_fees(fees: float):
    pass


class RunStatistics:
    def __init__(self, order_pairs: List[Tuple[Buy, Sell]],
                 trading_gains: TradingGains,
                 index_gains: IndexGains,
                 net_gains: NetGains,
                 classifier_time_window: TimeWindow,
                 testing_time_window: TimeWindow):
        self.order_pairs = order_pairs
        self.trading_gains = trading_gains
        self.index_gains = index_gains
        self.net_gains = net_gains
        self.classifier_time_window = classifier_time_window
        self.testing_time_window = testing_time_window
        self.number_of_orders = len(self.order_pairs) * 2
        self.profit_per_order_pair = (self.net_gains.gains / self.number_of_orders) *100


def calculate_percentage_gains(trade_amount: float, order_pairs: List[Tuple[Buy, Sell]]) -> TradingGains:
    net = compute_profits_and_losses(order_pairs)
    total_profit = np.sum(net)
    initial_investment = order_pairs[0][1].price_point.value * trade_amount
    gains = (total_profit * trade_amount) / initial_investment
    return TradingGains(gains=gains, elapsed_time=order_pairs[-1][1].price_point.date_time -
                                                  order_pairs[0][1].price_point.date_time)


def calculate_index_performance(order_pairs: List[Tuple[Buy, Sell]]) -> IndexGains:
    index_gains = (order_pairs[-1][1].price_point.value - order_pairs[0][1].price_point.value) / order_pairs[0][
        1].price_point.value
    return IndexGains(gains=index_gains, elapsed_time=order_pairs[-1][1].price_point.date_time -
                                                      order_pairs[0][1].price_point.date_time)


def compute_all_statistics(path_to_portfolio_df_dill: str):
    portfolio = load_portfolio(path_to_portfolio_df_dill)
    signals = extract_signals_from_portfolio(portfolio)
    signals = cleanup_signals(signals)
    order_pairs = generate_order_pairs(signals)
    trading_gains = calculate_percentage_gains(portfolio.trade_amount, order_pairs)
    index_gains = calculate_index_performance(order_pairs)
    net_gains = NetGains.from_index_and_trading_gains(index_gains, trading_gains)
    try:
        classifier_time_window = portfolio.classifier.training_time_window
    except AttributeError:
        classifier_time_window = None
    testing_time_window = compute_testing_window(order_pairs)

    return RunStatistics(
        order_pairs=order_pairs,
        trading_gains=trading_gains,
        index_gains=index_gains,
        net_gains=net_gains,
        classifier_time_window=classifier_time_window,
        testing_time_window=testing_time_window,
    )


def display(run_statistics: RunStatistics):
    print("Classifier training period: {}".format(run_statistics.classifier_time_window))
    print(display_timeframe(run_statistics.order_pairs))
    print(display_start_and_finish_prices(run_statistics.order_pairs))
    print(display_total_number_of_orders(run_statistics.order_pairs))
    print(run_statistics.trading_gains)
    print(run_statistics.index_gains)
    print(run_statistics.net_gains)
    print("Profit per order pair: {}".format(run_statistics.profit_per_order_pair))


def plot(run_statistics: RunStatistics):
    plot_histograms(compute_profits_and_losses(run_statistics.order_pairs))


if __name__ == '__main__':
    parser = ArgumentParser(description="Convert metadata dill into csv")
    parser.add_argument("-i", dest="input_filename", required=False,
                        help="input .dill", action=FullPaths)
    args = parser.parse_args()
    print("Input from {}".format(args.input_filename))
    run_statistics = compute_all_statistics(args.input_filename)
    display(run_statistics)
    plot(run_statistics)
