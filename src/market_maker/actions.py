import logging as logger
from datetime import datetime
from typing import Optional

from src.containers.order import Order, Price, OrderType, Side, Size
from src.containers.order_book import Ask, Bid
from src.containers.signal import SignalBuy, SignalSell
from src.containers.time import MilliSeconds
from src.containers.trading import CobinhoodTrading, CobinhoodError
from src.logging_tools.tools import print_function_context
from src.market_maker.utils import get_last_filled_order


@print_function_context
def _act_if_buy_signal_and_open_bid_order(trader: CobinhoodTrading, signal: SignalBuy, order: Order, ) -> Order:
    logger.info(
        "Current signal is SignalBuy and open order is OrderBuy, OR Current signal is SignalSell and open order is OrderSell...")
    logger.info("Going to modify open order...")
    try:
        if signal.price_point.value < order.price:
            success = trader.modify_order(order, price=signal.price_point.value, size=order.size)
        elif signal.price_point.value > order.price:
            success = trader.modify_order(order, price=signal.price_point.value, size=order.size)
        else:
            success = trader.modify_order(order, price=signal.price_point.value, size=order.size)
        if success:
            order = trader.get_open_orders(order_id="{}".format(order.id))  # TODO: return new order (using order id)
            return order
    except CobinhoodError as error:
        logger.debug(error)
        print(error)


@print_function_context
def _act_if_sell_signal_and_open_ask_order(trader: CobinhoodTrading, signal: SignalSell, order: Order, ) -> Order:
    return _act_if_buy_signal_and_open_bid_order(trader=trader, signal=signal, order=order)


@print_function_context
def _noop_act_if_buy_signal_and_open_bid_order(trader: CobinhoodTrading, signal: SignalBuy, order: Order, ) -> Order:
    logger.info(
        "Current signal is SignalBuy and open order is OrderBuy, OR Current signal is SignalSell and open order is OrderSell...")
    logger.info("Not going to modify open order...")
    pass


@print_function_context
def _noop_act_if_sell_signal_and_open_ask_order(trader: CobinhoodTrading, signal: SignalSell, order: Order, ) -> Order:
    return _noop_act_if_buy_signal_and_open_bid_order(trader=trader, signal=signal, order=order)


@print_function_context
def _act_if_sell_signal_and_open_bid_order(trader: CobinhoodTrading, signal: SignalSell, order: Order) -> Order:
    logger.info(
        "Current signal is SignalSell and open order is OrderBuy, OR Current signal is SignalBuy and open order is OrderSell...")
    logger.info("Going to cancel open order...")
    try:
        success = trader.cancel_order(order_id="{}".format(order.id))
        if success:
            return order
    except CobinhoodError as error:
        logger.debug(error)
        print(error)


@print_function_context
def _act_if_buy_signal_and_open_ask_order(trader: CobinhoodTrading, signal: SignalBuy, order: Order, ) -> Order:
    return _act_if_sell_signal_and_open_bid_order(trader=trader, signal=signal, order=order)


@print_function_context
def _act_if_buy_signal_and_filled_bid_order(trader: CobinhoodTrading, signal: SignalBuy, order: Order) -> Order:
    logger.info("Current signal is SignalBuy and last filled order is OrderBuy...Doing nothing...")
    pass


@print_function_context
def _act_if_sell_signal_and_filled_ask_order(trader: CobinhoodTrading, signal: SignalSell, order: Order) -> Order:
    logger.info("Current signal is SignalSell and last filled order is OrderSell...Doing nothing...")
    pass


@print_function_context
def _act_if_buy_signal_and_filled_ask_order(trader: CobinhoodTrading, signal: SignalBuy, order: Order) -> Optional[
    Order]:
    if trader.get_open_orders():
        return None
    logger.info("Current signal is SignalBuy and last filled order is OrderSell...Placing OrderBuy...")
    try:
        # lowest_available_ask_order = get_optimal_bid_price_from_orderbook(trader, signal, order)
        return trader.place_order(Order(
            trading_pair_id=order.trading_pair_id,
            price=Price(signal.price_point.value),
            type=OrderType("limit"),
            side=Side("bid"),
            size=Size(order.size),
            timestamp=MilliSeconds(round(datetime.now().timestamp() * 1000)),
        ))
    except CobinhoodError as error:
        logger.debug(error)
        print(error)


@print_function_context
def _act_if_sell_signal_and_filled_bid_order(trader: CobinhoodTrading, signal: SignalSell, order: Order) -> Optional[
    Order]:
    if trader.get_open_orders():
        return None
    logger.info("Current signal is SignalSell and last filled order is OrderBuy...Placing OrderSell...")
    try:
        # highest_available_bid_order = get_optimal_ask_price_from_orderbook(trader, signal, order)
        return trader.place_order(Order(
            trading_pair_id=order.trading_pair_id,
            price=Price(signal.price_point.value),
            type=OrderType("limit"),
            side=Side("ask"),
            size=Size(order.size),
            timestamp=MilliSeconds(round(datetime.now().timestamp() * 1000)),

        ))

    except CobinhoodError as error:
        logger.debug(error)
        print(error)


def get_optimal_bid_price_from_orderbook(trader: CobinhoodTrading, signal: SignalBuy,
                                         previously_filled_ask_order: Order) -> Ask:
    orderbook = trader.get_orderbook(trading_pair=previously_filled_ask_order.trading_pair_id)
    return min([ask for ask in orderbook.asks if ask.size >= previously_filled_ask_order.size],
               key=lambda x: x.price)


def get_optimal_ask_price_from_orderbook(trader: CobinhoodTrading, signal: SignalSell,
                                         previously_filled_bid_order: Order) -> Bid:
    orderbook = trader.get_orderbook(trading_pair=previously_filled_bid_order.trading_pair_id)
    return max([bid for bid in orderbook.bids if bid.size >= previously_filled_bid_order.size],
               key=lambda x: x.price)
