import logging
from typing import Union, Optional

from datetime import datetime

from src.backtesting_logic.logic import Buy, Sell, Hold
from src.containers.data_point import PricePoint
from src.containers.order import Order, OrderType, Size, Side, Price
from src.containers.time import MilliSeconds
from src.containers.trading import CobinhoodTrading, CobinhoodError
from src.market_maker.config import PRINT_TO_SDTOUT
from src.market_maker.mock_trading import MockTrading
from src.market_maker.mock_trading_helpers import print_function_name
from src.type_aliases import BinanceClient
from src.containers.trading_pair import TradingPair

logger = logging.getLogger('cryptotrader_api')


class MarketMakerError(RuntimeError):
    pass


def _instantiate_order() -> Order:
    raise NotImplementedError


@print_function_name
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


@print_function_name
def _act_if_sell_signal_and_ask_order(trader: CobinhoodTrading, signal: Sell, order: Order, ) -> Order:
    return _act_if_buy_signal_and_bid_order(trader=trader, signal=signal, order=order)


@print_function_name
def _act_if_sell_signal_and_bid_order(trader: CobinhoodTrading, signal: Sell, order: Order) -> Order:
    try:
        success = trader.cancel_order(order_id="{}".format(order.id))
        if success:
            return order
    except CobinhoodError as error:
        logger.debug(error)
        print(error)


@print_function_name
def _act_if_buy_signal_and_ask_order(trader: CobinhoodTrading, signal: Buy, order: Order, ) -> Order:
    return _act_if_sell_signal_and_bid_order(trader=trader, signal=signal, order=order)


@print_function_name
def _act_if_buy_signal_and_filled_bid_order(trader: CobinhoodTrading, signal: Buy, order: Order) -> Order:
    pass


@print_function_name
def _act_if_sell_signal_and_filled_ask_order(trader: CobinhoodTrading, signal: Sell, order: Order) -> Order:
    pass


@print_function_name
def _act_if_buy_signal_and_filled_ask_order(trader: CobinhoodTrading, signal: Buy, order: Order) -> Order:
    try:
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


# @print_function_name
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


def _init_signal() -> Buy:
    return Buy(-1, PricePoint(value=None, date_time=datetime.now()))


class ExperimentalMarketMaker:
    def __init__(self,
                 trader: Union[CobinhoodTrading, MockTrading],
                 trading_pair: TradingPair,
                 quantity: float
                 ):
        self._trader = trader
        self._trading_pair = trading_pair
        self._quantity = quantity
        self._open_orders = []
        self._current_signal = None
        self._previous_signal = _init_signal()

    @property
    def trader(self):
        return self._trader

    def insert_signal(self, signal: Union[Buy, Sell, Hold]):
        self._current_signal = signal
        # if self._current_signal != self._previous_signal:  # if new incoming signal
        self._update()
        self._previous_signal = self._current_signal

    def _perform_order_limit_check(self):
        if len(self._open_orders) > 1:
            raise MarketMakerError("There should only be one open order at a time.")

    def _check_for_open_orders(self):
        self._open_orders = self._trader.get_open_orders()
        self._perform_order_limit_check()
        if len(self._open_orders) == 1:
            self._open_order = self._open_orders[0]
        else:
            self._open_order = None

    def _update(self) -> Optional[Order]:
        self._check_for_open_orders()

        if self._open_order:

            if isinstance(self._current_signal, Buy):
                if self._open_order.side is Side.bid:
                    order = _act_if_buy_signal_and_bid_order(trader=self._trader, signal=self._current_signal,
                                                             order=self._open_order)
                elif self._open_order.side is Side.ask:
                    order = _act_if_buy_signal_and_ask_order(trader=self._trader, signal=self._current_signal,
                                                             order=self._open_order)
            elif isinstance(self._current_signal, Sell):
                if self._open_order.side is Side.bid:
                    order = _act_if_sell_signal_and_bid_order(trader=self._trader, signal=self._current_signal,
                                                              order=self._open_order)
                elif self._open_order.side is Side.ask:
                    order = _act_if_sell_signal_and_ask_order(trader=self._trader, signal=self._current_signal,
                                                              order=self._open_order)

        else:
            last_filled_order = self._trader.get_last_filled_order(trading_pair=self._trading_pair)
            if isinstance(self._current_signal, Buy):
                if last_filled_order.side is Side.bid:
                    order = _act_if_buy_signal_and_filled_bid_order(trader=self._trader, signal=self._current_signal,
                                                                    order=last_filled_order)
                elif last_filled_order.side is Side.ask:
                    order = _act_if_buy_signal_and_filled_ask_order(trader=self._trader, signal=self._current_signal,
                                                                    order=last_filled_order)
            elif isinstance(self._current_signal, Sell):
                if last_filled_order.side is Side.bid:
                    order = _act_if_sell_signal_and_filled_bid_order(trader=self._trader, signal=self._current_signal,
                                                                     order=last_filled_order)
                elif last_filled_order.side is Side.ask:
                    order = _act_if_sell_signal_and_filled_ask_order(trader=self._trader, signal=self._current_signal,
                                                                     order=last_filled_order)
        return None


if __name__ == '__main__':
    client = BinanceClient("VWwsv93z4UHRoJEOkye1oZeqRtYPiaEXqzeG9fem2guMNKKU1tUDTTta9Nm4JZ3x",
                           "L8C3ws3xkxX2AUravH41kfDezrHin2LarC1K8MDnmGM51dRBZwqDpvTOVZ1Qztap")
    mm = ExperimentalMarketMaker(client, TradingPair("NEO", "BTC"), 500)
    order = mm.update()
    print(client.get_all_orders(symbol=str(TradingPair("NEO", "BTC"))))
    print(client.get_orderbook_ticker(symbol=str(TradingPair("NEO", "BTC"))))
