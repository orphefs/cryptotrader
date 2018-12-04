import datetime
from time import sleep
from typing import List, Union

from src.analysis_tools.generate_run_statistics import compute_all_statistics, display
from src.containers.signal import SignalBuy, SignalSell
from src.classification.classifier_helpers import generate_signals_from_classifier
from src.classification.trading_classifier import TradingClassifier
from src.classification.train_classifier import run_trained_classifier
from src.containers.data_point import PricePoint, Price
from src.containers.order import Order, Side
from src.containers.portfolio import Portfolio
from src.containers.trading_pair import TradingPair
from src.definitions import TEST_DATA_DIR, DATA_DIR
from src.market_maker.ExperimentalMarketMaker import ExperimentalMarketMaker
from src.market_maker.config import PRINT_TO_SDTOUT
from src.market_maker.mock_client import MockClient
from src.market_maker.mock_trading import MockTrading
from src.market_maker.mock_trading_helpers import print_signal
from src.type_aliases import CobinhoodClient
import os


def test_if_alternate_bid_ask_orders(orders: List[Order]):
    orders = sorted(orders, key=lambda x: x.timestamp)
    for previous_order, next_order in zip(orders[0:], orders[1:]):
        if previous_order.side == next_order.side:
            result = False
            break
        else:
            result = True
            continue
    assert result


def convert_order_to_signal(order: Order) -> Union[SignalBuy, SignalSell]:
    if order.side is Side.bid:
        cls = SignalBuy
        signal = -1
    elif order.side is Side.ask:
        cls = SignalSell
        signal = 1
    else:
        raise RuntimeError("Input should be of type Order.")
    return cls(signal=signal, price_point=PricePoint(value=Price(order.price),
                                                     date_time=order.completed_at.as_datetime()))


def main():
    trading_pair = TradingPair("ETH", "BTC")
    trade_amount = 0.02
    path_to_portfolio = os.path.join(TEST_DATA_DIR, "portfolio_for_mock_market_maker.dill")
    stock_data = os.path.join(TEST_DATA_DIR, "test_data_3.dill")
    classifier = os.path.join(TEST_DATA_DIR, "classifier_for_test_data_3.dill")
    run_trained_classifier(trading_pair=trading_pair,
                           client=CobinhoodClient(),
                           trade_amount=trade_amount,
                           testing_data=stock_data,
                           classifier=classifier,
                           path_to_portfolio=path_to_portfolio,
                           )

    client = MockClient()
    trader = MockTrading(client)
    mm = ExperimentalMarketMaker(trader, trading_pair, 0.02)

    signals = generate_signals_from_classifier(stock_data, classifier)
    signal_count = 0
    for signal in signals:
        signal.price_point.date_time = datetime.datetime.now()
        if PRINT_TO_SDTOUT:
            print_signal(signal)
        for i in range(0, 5):
            sleep(0.005)
            _ = mm.insert_signal(signal)

        signal_count += 1
        if signal_count > 400:
            break

    portfolio = Portfolio(initial_capital=1, trade_amount=trade_amount,
                          classifier=TradingClassifier.load_from_disk(classifier))
    for order in mm.trader.filled_orders:
        signal = convert_order_to_signal(order)
        portfolio.update(Order.from_signal(signal))

    test_if_alternate_bid_ask_orders(mm.trader.filled_orders)

    portfolio.compute_performance()
    path_to_portfolio = os.path.join(DATA_DIR, "sample_portfolio.dill")
    portfolio.save_to_disk(path_to_portfolio)
    run_statistics = compute_all_statistics(path_to_portfolio)
    print("Number of signals: {}".format(signal_count))
    print("Signal/Order ratio: {}".format(signal_count / run_statistics.number_of_orders))



    display(run_statistics)


if __name__ == '__main__':
    main()
