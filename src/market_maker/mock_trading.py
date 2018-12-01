import random
from copy import copy
from datetime import datetime
from typing import Optional, List

import wrapt

from src.containers.order import Order, OrderID, Price, Size
from src.containers.time import MilliSeconds
from src.containers.trading import Trading, Trade
from src.containers.trading_pair import TradingPair
from src.helpers import generate_hash
from src.market_maker.config import PRINT_TO_SDTOUT
from src.market_maker.mock_client import MockClient
from src.market_maker.mock_trading_helpers import print_function_name, print_contents_of_order_lists, _find_order_by_id, \
    _find_latest_order, _find_oldest_order

starting_order = {
    "id": "8850805e-d783-46ec-9af5-30712035e760",
    "trading_pair_id": "COB-ETH",
    "side": "bid",
    "type": "limit",
    "price": "0.031469",
    "size": "0.02",
    "filled": "0.02",
    "state": "filled",
    "timestamp": round(datetime.now().timestamp() * 1e3),
    "eq_price": "0.031469",
    "completed_at": "2018-05-11T06:09:38.946678Z",
    "source": "exchange"}


@wrapt.decorator
def randomly_fill_orders(wrapped_func, instance, args, kwargs):
    if random.choice([True] + [False] * 100):
        instance._fill_orders()
    result = wrapped_func(*args, **kwargs)
    return result


class MockTrading(Trading):
    def __init__(self, client: MockClient):
        super().__init__(client=client)
        self._filled_orders = []
        self._initialize_filled_orders()
        self._open_orders = []
        self._last_filled_order = None

    @property
    def filled_orders(self):
        return self._filled_orders

    def _fill_orders(self):
        if len(self._open_orders) > 0:
            oldest_order = _find_oldest_order(self._open_orders)
            if oldest_order in self._open_orders:
                self._open_orders.remove(oldest_order)
                now = round(datetime.now().timestamp() * 1000)
                oldest_order.completed_at = MilliSeconds(now)
                oldest_order.timestamp = MilliSeconds(now)
                oldest_order.filled = oldest_order.size
            self._filled_orders += [oldest_order]

    def _initialize_filled_orders(self):
        order = Order.from_cobinhood_response(starting_order)
        order.completed_at = MilliSeconds(round(datetime.now().timestamp() * 1000))
        self._filled_orders = [order]

    @print_contents_of_order_lists
    @randomly_fill_orders
    @print_function_name
    def place_order(self, order: Order, ) -> Order:
        order.id = generate_hash(order.timestamp, order.size, order.price, order.side)
        if PRINT_TO_SDTOUT:
            print("Place order {}".format(order))
        self._open_orders += [order]
        return order

    @print_contents_of_order_lists
    @randomly_fill_orders
    @print_function_name
    def modify_order(self, order: Order, price: Price, size: Size) -> bool:
        order_id = order.id
        order = _find_order_by_id(self._open_orders, order_id)
        original_order = copy(order)
        if original_order is not None:
            order.price = price
            order.size = size
            order.timestamp = MilliSeconds(round(datetime.now().timestamp() * 1000))
            if PRINT_TO_SDTOUT:
                print("Modify order {} \n to \n {}".format(original_order, order))
        else:
            if PRINT_TO_SDTOUT:
                print("Order {} was already filled, so could not modify.".format(order_id))
        return True

    @print_contents_of_order_lists
    @randomly_fill_orders
    def get_open_orders(self, order_id: Optional[OrderID] = None) -> List[Optional[Order]]:
        # print("Current open orders: \n")
        # _print_list(self._open_orders)
        return self._open_orders

    @print_contents_of_order_lists
    @randomly_fill_orders
    @print_function_name
    def cancel_order(self, order_id: OrderID) -> bool:
        print("Cancelling order with order id {} \n".format(order_id))
        order = _find_order_by_id(self._open_orders, order_id)
        if order in self._open_orders:
            self._open_orders.remove(order)

        if order is not None:
            if PRINT_TO_SDTOUT:
                print("Cancel order {} \n".format(order.id))
        else:
            order = _find_order_by_id(self._filled_orders, order_id)
            if order is not None:
                if PRINT_TO_SDTOUT:
                    print("Order {} was already filled, so could not cancel.".format(order.id))
        return True

    @print_contents_of_order_lists
    @randomly_fill_orders
    def get_last_filled_order(self, trading_pair: TradingPair) -> Order:
        order = _find_latest_order(self._filled_orders)
        # print("Last filled order: {} \n".format(order))
        return order

    @print_contents_of_order_lists
    @randomly_fill_orders
    def get_order_history(self, trading_pair: TradingPair) -> List[Order]:
        # print("Order history: \n")
        # _print_list(self._filled_orders)
        return self._filled_orders

    def get_orders_trades(self, order_id: OrderID):
        raise NotImplementedError

    def get_trades(self) -> List[Trade]:
        raise NotImplementedError
