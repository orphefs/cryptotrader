import random
from queue import Queue
from typing import Optional, List, Any

from src.containers.order import Order, OrderID, Price, Size
from src.containers.trading import Trading, Trade
from src.containers.trading_pair import TradingPair
from src.test.mock_client import MockClient
from apscheduler.scheduler import Scheduler


def _find_order_by_id(orders: List[Order], order_id: OrderID) -> Order:
    return list(filter(lambda x: x.id == order_id, orders))[0]


def _find_latest_order(orders: List[Order]) -> Order:
    return max(orders, key=lambda x: x.timestamp)


def _find_oldest_order(orders: List[Order]) -> Order:
    return min(orders, key=lambda x: x.timestamp)


def _print_list(lst: List[Any]):
    for element in lst:
        print(element)
    print("\n")


def on_call(func):
    def func_wrapper(self):
        if random.choice([True, False]):
            self._fill_orders()
        func(self)
        return func
    return func_wrapper


class MockTrading(Trading):
    def __init__(self, client: MockClient):
        super().__init__(client=client)
        self._filled_orders = []
        self._open_orders = []
        self._last_filled_order = None
        self._scheduler = Scheduler()

    def _fill_orders(self):
        if len(self._open_orders) > 0:
            self._filled_orders += self._open_orders.pop(self._open_orders.index(
                _find_oldest_order(self._open_orders)))

    @on_call
    def place_order(self, order: Order, ) -> Order:
        print("Place order {}".format(order))
        self._open_orders += order
        return order

    @on_call
    def modify_order(self, order_id: OrderID, price: Price, size: Size) -> bool:
        found_order = _find_order_by_id(self._open_orders, order_id)
        order = _find_order_by_id(self._open_orders, order_id)
        found_order.price = price
        found_order.size = size
        print("Modify order {} \n to \n {}".format(order, found_order))
        return True

    @on_call
    def get_open_orders(self, order_id: Optional[OrderID]) -> List[Optional[Order]]:
        print("Current open orders: \n")
        _print_list(self._open_orders)
        return self._open_orders

    @on_call
    def cancel_order(self, order_id: OrderID) -> bool:
        order = _find_order_by_id(self._open_orders, order_id)
        self._open_orders.pop(self._open_orders.index(order))
        print("Cancel order {}".format(order))
        return True

    @on_call
    def get_last_filled_order(self, trading_pair: TradingPair) -> Order:
        order = _find_latest_order(self._filled_orders)
        print("Last filled order: {}".format(order))
        return order

    @on_call
    def get_order_history(self, trading_pair: TradingPair) -> List[Order]:
        print("Order history: \n")
        _print_list(self._filled_orders)
        return self._filled_orders

    def get_orders_trades(self, order_id: OrderID):
        raise NotImplementedError

    def get_trades(self) -> List[Trade]:
        raise NotImplementedError

