from time import sleep
from typing import Optional, List

from src.classification.classifier_helpers import generate_signals_iteratively, generate_signals_from_classifier
from src.classification.train_classifier import run_trained_classifier
from src.connection.load_stock_data import load_stock_data
from src.containers.order import Order, OrderID, Price, Size
from src.containers.portfolio import Portfolio
from src.containers.stock_data import load_from_disk
from src.containers.trading import Trading, Trade
from src.containers.trading_pair import TradingPair
from src.definitions import TEST_DATA_DIR
from src.live_logic.ExperimentalMarketMaker import ExperimentalMarketMaker
from src.test.mock_client import MockClient
from src.test.mock_trading import MockTrading
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
    path_to_portfolio = os.path.join(TEST_DATA_DIR, "portfolio_for_mock_market_maker.dill")
    stock_data = os.path.join(TEST_DATA_DIR, "test_data_3.dill")
    classifier = os.path.join(TEST_DATA_DIR, "classifier_for_test_data_3.dill")
    run_trained_classifier(trading_pair=trading_pair,
                           client=CobinhoodClient(),
                           trade_amount=0.02,
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
        print("\n\n+++++++++++++++++++++++++++++++++++++\n"
              "++++++++++++NEW SIGNAL+++++++++++++++++"
              "+++++++++++++++++++++++++++++++++++++")
        print(signal)
        print("\n\n+++++++++++++++++++++++++++++++++++++\n"
              "+++++++++++++++++++++++++++++++++++++++"
              "+++++++++++++++++++++++++++++++++++++")
        for i in range(0,5):
            sleep(0.005)
            _ = mm.insert_signal(signal)

        count += 1
        if count > 200:
            break

    test_if_alternate_bid_ask_orders(mm.trader.filled_orders)


if __name__ == '__main__':
    main()
