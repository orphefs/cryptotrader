import logging
from typing import Union, Optional, Type

from datetime import datetime

from src.backtesting_logic.logic import Buy, Sell, Hold
from src.containers.order import Order, OrderType, Size, Side, Price
from src.containers.time import MilliSeconds
from src.containers.trading import CobinhoodTrading, CobinhoodError, Trading
from src.test.mock_client import MockClient
from src.test.mock_trading import MockTrading
from src.type_aliases import CobinhoodClient, BinanceClient
from src.containers.trading_pair import TradingPair

logger = logging.getLogger('cryptotrader_api')


class MarketMakerError(RuntimeError):
    pass


def _act_if_buy_signal_and_bid_order(trader: CobinhoodTrading, signal: Buy, order: Order, ) -> Order:
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


def _act_if_sell_signal_and_ask_order(trader: CobinhoodTrading, signal: Sell, order: Order, ) -> Order:
    return _act_if_buy_signal_and_bid_order(trader=trader, signal=signal, order=order)


def _act_if_sell_signal_and_bid_order(trader: CobinhoodTrading, signal: Sell, order: Order) -> Order:
    try:
        success = trader.cancel_order(order_id="{}".format(order.id))
        if success:
            return order
    except CobinhoodError as error:
        logger.debug(error)
        print(error)


def _act_if_buy_signal_and_ask_order(trader: CobinhoodTrading, signal: Buy, order: Order, ) -> Order:
    return _act_if_sell_signal_and_bid_order(trader=trader, signal=signal, order=order)


def _act_if_buy_signal_and_filled_bid_order(trader: CobinhoodTrading, signal: Buy, order: Order) -> Order:
    pass


def _act_if_sell_signal_and_filled_ask_order(trader: CobinhoodTrading, signal: Sell, order: Order) -> Order:
    pass


def _instantiate_order() -> Order:
    raise NotImplementedError


def _act_if_buy_signal_and_filled_ask_order(trader: CobinhoodTrading, signal: Buy, order: Order) -> Order:
    try:
        return trader.place_order(Order(
            trading_pair_id=order.trading_pair_id,
            price=Price(signal.price_point.value),
            type=OrderType("limit"),
            side=Side("bid"),
            size=Size(order.size),
            timestamp=MilliSeconds(round(datetime.now().timestamp()*1000)),
        ))
    except CobinhoodError as error:
        logger.debug(error)
        print(error)


def _act_if_sell_signal_and_filled_bid_order(trader: CobinhoodTrading, signal: Sell, order: Order) -> Order:
    try:
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


class ExperimentalMarketMaker:
    def __init__(self,
                 trader: Union[CobinhoodTrading, MockTrading],
                 trading_pair: TradingPair,
                 quantity: float
                 ):
        self._trader = trader
        self._trading_pair = trading_pair
        self._quantity = quantity

    @property
    def trader(self):
        return self._trader

    def update(self, signal: Union[Buy, Sell, Hold]) -> Optional[Order]:
        order = None
        orders = self._trader.get_open_orders()
        if len(orders) > 1:
            raise MarketMakerError("There should only be one open order at a time.")
        if len(orders) == 1:  # order is not filled yet, still open
            print("\n--------------Order was filled--------------\n")
            order = orders[0]
            if isinstance(signal, Buy):
                if order.side.bid:  # buy order
                    order = _act_if_buy_signal_and_bid_order(trader=self._trader, signal=signal, order=order)
                elif order.side.ask:  # sell order
                    order = _act_if_buy_signal_and_ask_order(trader=self._trader, signal=signal, order=order)
            elif isinstance(signal, Sell):
                if order.side.bid:  # buy order
                    order = _act_if_sell_signal_and_bid_order(trader=self._trader, signal=signal, order=order)
                elif order.side.ask:  # sell order
                    order = _act_if_sell_signal_and_ask_order(trader=self._trader, signal=signal, order=order)

        elif len(orders) == 0:  # all orders filled, no open orders
            print("\n--------------Order is still open --------------\n")
            order = self._trader.get_last_filled_order(trading_pair=self._trading_pair)
            if isinstance(signal, Buy):
                if order.side.bid:
                    order = _act_if_buy_signal_and_filled_bid_order(trader=self._trader, signal=signal, order=order)
                elif order.side.ask:
                    order = _act_if_buy_signal_and_filled_ask_order(trader=self._trader, signal=signal, order=order)
            elif isinstance(signal, Sell):
                if order.side.bid:
                    order = _act_if_sell_signal_and_filled_bid_order(trader=self._trader, signal=signal, order=order)
                elif order.side.ask:
                    order = _act_if_sell_signal_and_filled_ask_order(trader=self._trader, signal=signal, order=order)
        return order


if __name__ == '__main__':
    client = BinanceClient("VWwsv93z4UHRoJEOkye1oZeqRtYPiaEXqzeG9fem2guMNKKU1tUDTTta9Nm4JZ3x",
                           "L8C3ws3xkxX2AUravH41kfDezrHin2LarC1K8MDnmGM51dRBZwqDpvTOVZ1Qztap")
    mm = ExperimentalMarketMaker(client, TradingPair("NEO", "BTC"), 500)
    order = mm.update()
    print(client.get_all_orders(symbol=str(TradingPair("NEO", "BTC"))))
    print(client.get_orderbook_ticker(symbol=str(TradingPair("NEO", "BTC"))))
