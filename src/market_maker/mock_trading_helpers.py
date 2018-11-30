from typing import Callable, List, Optional, Any, Union

import wrapt

from src.backtesting_logic.logic import Buy, Sell
from src.containers.order import Order, OrderID
from src.market_maker.config import PRINT_FUNCTION_INFO


def print_signal(signal: Union[Buy, Sell]):
    print("\n\n+++++++++++++++++++++++++++++++++++++\n"
          "++++++++++++NEW SIGNAL+++++++++++++++++"
          "+++++++++++++++++++++++++++++++++++++")
    print(signal)
    print("\n\n+++++++++++++++++++++++++++++++++++++\n"
          "+++++++++++++++++++++++++++++++++++++++"
          "+++++++++++++++++++++++++++++++++++++")


@wrapt.decorator(enabled=PRINT_FUNCTION_INFO)
def print_function_name(wrapped, instance, args, kwargs):
    print("Running function {}\n".format(wrapped.__name__))
    return wrapped(*args, **kwargs)


@wrapt.decorator(enabled=PRINT_FUNCTION_INFO)
def print_contents_of_order_lists(wrapped, instance, args, kwargs):
    # list_of_funcs = ["place_order", "modify_order", "cancel_order", "randomly_fill_orders"]
    # if func.__name__ in list_of_funcs:
    print("\n==============BEFORE==================\n")
    print("Contents of filled orders: \n ")
    _print_list(instance._filled_orders)
    print("\n")
    print("Contents of open orders: \n")
    _print_list(instance._open_orders)
    print("\n")
    print("\n=======================================\n")

    result = wrapped(*args, **kwargs)

    # if func.__name__ in list_of_funcs:
    print("\n===============AFTER==================\n")
    print("Contents of filled orders: \n ")
    _print_list(instance._filled_orders)
    print("\n")
    print("Contents of open orders: \n")
    _print_list(instance._open_orders)
    print("\n")
    print("\n==========================================\n")
    return result


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
