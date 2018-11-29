import random
from datetime import datetime
from queue import Queue
from typing import Optional, List, Any, Callable

from src.containers.order import Order, OrderID, Price, Size
from src.containers.time import MilliSeconds
from src.containers.trading import Trading, Trade
from src.containers.trading_pair import TradingPair
from src.helpers import generate_hash
from src.test.mock_client import MockClient


def _find_order_by_id(orders: List[Order], order_id: OrderID) -> Optional[Order]:
    order = list(filter(lambda x: x.id == order_id, orders))
    if len(order) > 0:
        return order[0]


def _find_latest_order(orders: List[Order]) -> Optional[Order]:
    if len(orders) > 0:
        return max(orders, key=lambda x: x.timestamp)


def _find_oldest_order(orders: List[Order]) -> Optional[Order]:
    if len(orders) > 0:
        return min(orders, key=lambda x: x.timestamp)


def _print_list(lst: List[Any]):
    for element in sorted(lst, key=lambda x: x.timestamp):
        print(element)


def on_call(func: Callable):
    def func_wrapper(*args, **kwargs):
        list_of_funcs = ["place_order", "modify_order", "cancel_order", ]

        if func.__name__ in list_of_funcs:
            print("\n==============BEFORE==================\n")
            print("Running function {}\n".format(func.__name__))
            print("Contents of filled orders: \n ")
            _print_list(args[0]._filled_orders)
            print("\n")
            print("Contents of open orders: \n")
            _print_list(args[0]._open_orders)
            print("\n")
            print("\n=======================================\n")

        if random.choice([True, False]):
            args[0]._fill_orders()
        result = func(*args, **kwargs)

        if func.__name__ in list_of_funcs:
            print("\n===============AFTER==================\n")
            print("Contents of filled orders: \n ")
            _print_list(args[0]._filled_orders)
            print("\n")
            print("Contents of open orders: \n")
            _print_list(args[0]._open_orders)
            print("\n")
            print("\n==========================================\n")

        return result

    return func_wrapper


sample_order = {
    "id": "8850805e-d783-46ec-9af5-30712035e760",
    "trading_pair_id": "COB-ETH",
    "side": "bid",
    "type": "limit",
    "price": "0.0001195",
    "size": "0.02",
    "filled": "0.02",
    "state": "filled",
    "timestamp": 1543508274848,
    "eq_price": "0.0001194999996323",
    "completed_at": "2018-05-11T06:09:38.946678Z",
    "source": "exchange"}


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
                oldest_order.completed_at = MilliSeconds(round(datetime.now().timestamp() * 1000))
                oldest_order.filled = oldest_order.size
            self._filled_orders += [oldest_order]

    def _initialize_filled_orders(self):
        self._filled_orders = [Order.from_cobinhood_response(sample_order)]

    @on_call
    def place_order(self, order: Order, ) -> Order:
        order.id = generate_hash(order.timestamp, order.size, order.price, order.side)
        print("Place order {}".format(order))
        self._open_orders += [order]
        return order

    @on_call
    def modify_order(self, order_id: OrderID, price: Price, size: Size) -> bool:
        order = _find_order_by_id(self._open_orders, order_id)
        if order is not None:
            order.price = price
            order.size = size
            print("Modify order {} \n to \n {}".format(order, order))
        else:
            print("Order {} was already filled, so could not modify.".format(order_id))
        return True

    @on_call
    def get_open_orders(self, order_id: Optional[OrderID] = None) -> List[Optional[Order]]:
        # print("Current open orders: \n")
        # _print_list(self._open_orders)
        return self._open_orders

    @on_call
    def cancel_order(self, order_id: OrderID) -> bool:
        print("Cancelling order with order id {} \n".format(order_id))
        order = _find_order_by_id(self._open_orders, order_id)
        if order in self._open_orders:
            self._open_orders.remove(order)

        if order is not None:
            print("Cancel order {} \n".format(order.id))
        else:
            order = _find_order_by_id(self._filled_orders, order_id)
            if order is not None:
                print("Order {} was already filled, so could not cancel.".format(order.id))
        return True

    @on_call
    def get_last_filled_order(self, trading_pair: TradingPair) -> Order:
        order = _find_latest_order(self._filled_orders)
        # print("Last filled order: {} \n".format(order))
        return order

    @on_call
    def get_order_history(self, trading_pair: TradingPair) -> List[Order]:
        # print("Order history: \n")
        # _print_list(self._filled_orders)
        return self._filled_orders

    def get_orders_trades(self, order_id: OrderID):
        raise NotImplementedError

    def get_trades(self) -> List[Trade]:
        raise NotImplementedError
