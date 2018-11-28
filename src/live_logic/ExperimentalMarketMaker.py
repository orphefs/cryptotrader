import logging
from typing import Union, Optional

from datetime import datetime

from src.backtesting_logic.logic import Buy, Sell, Hold
from src.containers.order import Order
from src.containers.trading import CobinhoodTrading
from src.type_aliases import BinanceOrder, CobinhoodClient, BinanceClient
from src.containers.trading_pair import TradingPair

logger = logging.getLogger('cryptotrader_api')


class MarketMakerError(RuntimeError):
    pass


def _act_if_buy_signal_and_bid_order(signal: Buy, order: Order, ) -> Order:
    if signal.price_point.value < order.price:
        raise NotImplementedError

    elif signal.price_point.value > order.price:
        raise NotImplementedError

    else:
        raise NotImplementedError


def _act_if_sell_signal_and_bid_order(signal: Sell, order: Order, ) -> Order:
    if signal.price_point.value < order.price:
        raise NotImplementedError

    elif signal.price_point.value > order.price:
        raise NotImplementedError

    else:
        raise NotImplementedError


def _act_if_buy_signal_and_ask_order(signal: Buy, order: Order, ) -> Order:
    if signal.price_point.value < order.price:
        raise NotImplementedError

    elif signal.price_point.value > order.price:
        raise NotImplementedError

    else:
        raise NotImplementedError


def _act_if_sell_signal_and_ask_order(signal: Sell, order: Order, ) -> Order:
    if signal.price_point.value < order.price:
        raise NotImplementedError

    elif signal.price_point.value > order.price:
        raise NotImplementedError

    else:
        raise NotImplementedError


def _act_if_buy_signal_and_no_order(signal: Buy) -> Order:
    if signal.price_point.value < order.price:
        raise NotImplementedError

    elif signal.price_point.value > order.price:
        raise NotImplementedError

    else:
        raise NotImplementedError


def _act_if_sell_signal_and_no_order(signal: Sell) -> Order:
    if signal.price_point.value < order.price:
        raise NotImplementedError

    elif signal.price_point.value > order.price:
        raise NotImplementedError

    else:
        raise NotImplementedError


class ExperimentalMarketMaker:
    def __init__(self, client: Union[BinanceClient, CobinhoodClient], trading_pair: TradingPair, quantity: float):
        self._client = client
        self._trader = CobinhoodTrading(client)
        self._trading_pair = trading_pair
        self._quantity = quantity

    def update(self, signal: Union[Buy, Sell, Hold]) -> Order:
        orders = self._trader.get_open_orders()
        if len(orders) > 1:
            raise MarketMakerError("There should only be one open order at a time.")
        if len(orders) == 1:  # order is not filled yet, still open
            order = orders[0]
            if isinstance(signal, Buy):
                if order.side.bid:  # buy order
                    order = _act_if_buy_signal_and_bid_order(signal=signal, order=order)
                elif order.side.ask:  # sell order
                    order = _act_if_buy_signal_and_ask_order(signal=signal, order=order)
            elif isinstance(signal, Sell):
                if order.side.bid:  # buy order
                    order = _act_if_sell_signal_and_bid_order(signal=signal, order=order)
                elif order.side.ask:  # sell order
                    order = _act_if_sell_signal_and_ask_order(signal=signal, order=order)

        elif len(orders) == 0:  # all orders filled, no open orders
            if isinstance(signal, Buy):
                order = _act_if_buy_signal_and_ask_order(signal=signal)
            elif isinstance(signal, Sell):
                order = _act_if_sell_signal_and_bid_order(signal=signal)
        return order

    def place_buy_order(self):
        logger.info(
            "Placing Buy market order on {} for {} {}".format(datetime.now(), self._trading_pair, self._quantity))
        if isinstance(self._client, BinanceClient):
            order = self._client.order_market_buy(
                symbol=self._trading_pair,
                side=BinanceClient.SIDE_BUY,
                type=BinanceClient.ORDER_TYPE_MARKET,
                quantity=self._quantity)
            return order
        elif isinstance(self._client, CobinhoodClient):
            raise NotImplementedError

    def place_sell_order(self):
        logger.info(
            "Placing Sell market order on {} for {} {}".format(datetime.now(), self._trading_pair, self._quantity))
        if isinstance(self._client, BinanceClient):
            order = self._client.order_market_sell(
                symbol=self._trading_pair,
                side=BinanceClient.SIDE_SELL,
                type=BinanceClient.ORDER_TYPE_MARKET,
                quantity=self._quantity)
            return order
        elif isinstance(self._client, CobinhoodClient):
            raise NotImplementedError


if __name__ == '__main__':
    client = BinanceClient("VWwsv93z4UHRoJEOkye1oZeqRtYPiaEXqzeG9fem2guMNKKU1tUDTTta9Nm4JZ3x",
                           "L8C3ws3xkxX2AUravH41kfDezrHin2LarC1K8MDnmGM51dRBZwqDpvTOVZ1Qztap")
    mm = ExperimentalMarketMaker(client, TradingPair("NEO", "BTC"), 500)
    order = mm.update()
    print(order)
    print(client.get_all_orders(symbol=str(TradingPair("NEO", "BTC"))))
    print(client.get_orderbook_ticker(symbol=str(TradingPair("NEO", "BTC"))))
