import logging as logger
from typing import Union, Optional, List

from datetime import datetime

import tenacity

from src.containers.signal import SignalBuy, SignalSell, SignalHold
from src.containers.data_point import PricePoint
from src.containers.order import Order, Side, OrderState, OrderID
from src.containers.trading import CobinhoodTrading
from src.market_maker.actions import _act_if_buy_signal_and_open_bid_order, _act_if_sell_signal_and_open_ask_order, \
    _act_if_sell_signal_and_open_bid_order, _act_if_buy_signal_and_open_ask_order, \
    _act_if_buy_signal_and_filled_bid_order, _act_if_sell_signal_and_filled_ask_order, \
    _act_if_buy_signal_and_filled_ask_order, _act_if_sell_signal_and_filled_bid_order, \
    _noop_act_if_sell_signal_and_open_ask_order, _noop_act_if_buy_signal_and_open_bid_order
from src.market_maker.mock_trading import MockTrading
from src.market_maker.mock_trading_helpers import print_context
from src.type_aliases import BinanceClient
from src.containers.trading_pair import TradingPair


class MarketMakerError(RuntimeError):
    pass


def _instantiate_order() -> Order:
    raise NotImplementedError


def _init_signal() -> SignalBuy:
    return SignalBuy(-1, PricePoint(value=None, date_time=datetime.now()))


@tenacity.retry(wait=tenacity.wait_fixed(1))
def _get_last_filled_order(trading_pair: TradingPair, trader: Union[CobinhoodTrading, MockTrading]):
    last_order = trader.get_last_n_orders(trading_pair, 1)[0]
    i = 1
    while last_order.state is not OrderState.filled:
        last_order = trader.get_last_n_orders(trading_pair, i)[-1]
        i += 1
    return last_order


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
        self._filled_orders = []
        self._current_signal = None
        self._previous_signal = _init_signal()
        self._last_filled_order = _get_last_filled_order(trading_pair=self._trading_pair, trader=self._trader)
        self._last_placed_order = self._trader.get_last_n_orders(trading_pair=self._trading_pair, n=1)[0]

    @property
    def trader(self) -> Union[CobinhoodTrading, MockTrading]:
        return self._trader

    @property
    def filled_orders(self) -> List[Order]:
        return self._filled_orders

    @print_context
    def insert_signal(self, signal: Union[SignalBuy, SignalSell, SignalHold]):
        self._current_signal = signal
        # if self._current_signal != self._previous_signal:  # if new incoming signal
        self._update()
        self._previous_signal = self._current_signal

    @print_context
    def _perform_order_limit_check(self):
        if len(self._open_orders) > 1:
            raise MarketMakerError("There should only be one open order at a time.")

    @print_context
    def _check_for_open_orders(self) -> Optional[Order]:
        self._open_orders = self._trader.get_open_orders()
        self._perform_order_limit_check()
        if len(self._open_orders) == 1:
            return self._open_orders[0]

    @print_context
    def _is_order_filled(self, order_id: OrderID) -> bool:
        if self._trader.get_open_orders(order_id=order_id):
            return False
        else:
            return True

    def _update_orders_status(self):
        self._open_order = self._check_for_open_orders()
        self._last_filled_order = _get_last_filled_order(self._trading_pair, self._trader)
        self._last_placed_order = self._trader.get_last_n_orders(trading_pair=self._trading_pair, n=1)[0]

    @print_context
    def _update(self) -> Optional[Order]:
        self._update_orders_status()

        logger.info("Previous signal was {}...".format(type(self._previous_signal).__name__))
        logger.info("Current signal is {}...".format(type(self._current_signal).__name__))
        logger.info("Last filled order is {}...".format(type(self._last_filled_order).__name__))
        logger.info("Open order is {}...".format(type(self._open_order).__name__))

        if self._open_order:

            if isinstance(self._current_signal, SignalBuy):
                if self._open_order.side is Side.bid:
                    _ = _noop_act_if_buy_signal_and_open_bid_order(trader=self._trader, signal=self._current_signal,
                                                                   order=self._open_order)
                elif self._open_order.side is Side.ask:
                    _ = _act_if_buy_signal_and_open_ask_order(trader=self._trader, signal=self._current_signal,
                                                              order=self._open_order)
            elif isinstance(self._current_signal, SignalSell):
                if self._open_order.side is Side.bid:
                    _ = _act_if_sell_signal_and_open_bid_order(trader=self._trader, signal=self._current_signal,
                                                               order=self._open_order)
                elif self._open_order.side is Side.ask:
                    _ = _noop_act_if_sell_signal_and_open_ask_order(trader=self._trader, signal=self._current_signal,
                                                                    order=self._open_order)

        else:

            self._last_filled_order = _get_last_filled_order(trading_pair=self._trading_pair, trader=self._trader)

            if self._last_filled_order not in self._filled_orders:
                self._filled_orders.append(self._last_filled_order)

            if isinstance(self._current_signal, SignalBuy):
                if self._last_filled_order.side is Side.bid:
                    _ = _act_if_buy_signal_and_filled_bid_order(trader=self._trader, signal=self._current_signal,
                                                                order=self._last_filled_order)
                elif self._last_filled_order.side is Side.ask and self._is_order_filled(
                        order_id=self._last_placed_order.id):
                    last_placed_order = _act_if_buy_signal_and_filled_ask_order(trader=self._trader,
                                                                                signal=self._current_signal,
                                                                                order=self._last_filled_order)
                    if last_placed_order:
                        self._last_placed_order = last_placed_order
            elif isinstance(self._current_signal, SignalSell):
                if self._last_filled_order.side is Side.bid and self._is_order_filled(
                        order_id=self._last_placed_order.id):
                    last_placed_order = _act_if_sell_signal_and_filled_bid_order(trader=self._trader,
                                                                                 signal=self._current_signal,
                                                                                 order=self._last_filled_order)
                    if last_placed_order:
                        self._last_placed_order = last_placed_order
                elif self._last_filled_order.side is Side.ask:
                    _ = _act_if_sell_signal_and_filled_ask_order(trader=self._trader, signal=self._current_signal,
                                                                 order=self._last_filled_order)
        for _ in range(0, 2):
            self._update_orders_status()

        return self._last_filled_order


if __name__ == '__main__':
    client = BinanceClient("VWwsv93z4UHRoJEOkye1oZeqRtYPiaEXqzeG9fem2guMNKKU1tUDTTta9Nm4JZ3x",
                           "L8C3ws3xkxX2AUravH41kfDezrHin2LarC1K8MDnmGM51dRBZwqDpvTOVZ1Qztap")
    mm = ExperimentalMarketMaker(client, TradingPair("NEO", "BTC"), 500)
    order = mm.update()
    print(client.get_all_orders(symbol=str(TradingPair("NEO", "BTC"))))
    print(client.get_orderbook_ticker(symbol=str(TradingPair("NEO", "BTC"))))
