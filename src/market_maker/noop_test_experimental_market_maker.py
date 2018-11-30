from time import sleep
from typing import List

from src.classification.classifier_helpers import generate_signals_from_classifier
from src.classification.trading_classifier import TradingClassifier
from src.classification.train_classifier import run_trained_classifier
from src.containers.order import Order
from src.containers.portfolio import Portfolio
from src.containers.trading_pair import TradingPair
from src.definitions import TEST_DATA_DIR
from src.market_maker.ExperimentalMarketMaker import ExperimentalMarketMaker
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
    count = 0
    for signal in signals:
        # print_signal(signal)
        for i in range(0, 5):
            sleep(0.005)
            _ = mm.insert_signal(signal)

        count += 1
        if count > 400:
            break

    portfolio = Portfolio(initial_capital=1, trade_amount=trade_amount,
                          classifier=TradingClassifier.load_from_disk(classifier))
    for order in mm.trader.filled_orders:
        portfolio.update(order)


    print(count)
    test_if_alternate_bid_ask_orders(mm.trader.filled_orders)


if __name__ == '__main__':
    main()
