import logging
from typing import Union, Optional

from datetime import datetime

from src.containers.signal import SignalBuy, SignalSell, SignalHold
from src.type_aliases import BinanceOrder, CobinhoodClient, BinanceClient
from src.containers.trading_pair import TradingPair

logger = logging.getLogger('cryptotrader_api')


class NoopMarketMaker:
    def __init__(self, client: Union[BinanceClient, CobinhoodClient], trading_pair: TradingPair, quantity: float):
        self._client = client
        self._trading_pair = trading_pair
        self._quantity = quantity

    def place_order(self, signal: Union[SignalBuy, SignalSell, SignalHold]) -> Optional[BinanceOrder]:
        if isinstance(signal, SignalBuy):
            return self.place_buy_order()
        elif isinstance(signal, SignalSell):
            return self.place_sell_order()
        else:
            pass

    def place_buy_order(self):
        pass

    def place_sell_order(self):
        pass


class TestMarketMaker:
    def __init__(self, client: Union[BinanceClient, CobinhoodClient], trading_pair: TradingPair, quantity: float):
        self._client = client
        self._trading_pair = trading_pair
        self._quantity = quantity

    def place_order(self, signal: Union[SignalBuy, SignalSell, SignalHold]) -> Optional[BinanceOrder]:
        if isinstance(signal, SignalBuy):
            return self.place_buy_order()
        elif isinstance(signal, SignalSell):
            return self.place_sell_order()
        else:
            pass

    def place_buy_order(self):
        logger.info(
            "Placing Buy market order on {} for {} {}".format(datetime.now(), self._trading_pair, self._quantity))
        if isinstance(self._client, BinanceClient):
            order = self._client.create_test_order(
                symbol=self._trading_pair,
                side=BinanceClient.SIDE_BUY,
                type=BinanceClient.ORDER_TYPE_MARKET,
                quantity=self._quantity)
            return order
        elif isinstance(self._client, CobinhoodClient):
            print("Cobinhood Test Buy Order...")

    def place_sell_order(self):
        logger.info(
            "Placing Sell market order on {} for {} {}".format(datetime.now(), self._trading_pair, self._quantity))
        if isinstance(self._client, BinanceClient):
            order = self._client.create_test_order(
                symbol=self._trading_pair,
                side=BinanceClient.SIDE_SELL,
                type=BinanceClient.ORDER_TYPE_MARKET,
                quantity=self._quantity)
            return order
        elif isinstance(self._client, CobinhoodClient):
            print("Cobinhood Test Sell Order...")


def _create_cobinhood_order_dict(trading_pair: TradingPair, order_type: str, quantity: float) -> dict:
    return {
        "trading_pair_id": "{}".format(trading_pair.as_string_for_cobinhood()),
        "side": "{}".format(order_type),
        "type": "market",
        # "price": "0",
        "size": "{}".format(quantity)
    }


class OrderError(RuntimeError):
    pass


def raise_order_exception_if_error(order: dict):
    if "error" in order:
        raise OrderError("{}".format(order["error"]["error_code"]))
    else:
        pass


class MarketMaker:
    def __init__(self, client: Union[BinanceClient, CobinhoodClient], trading_pair: TradingPair, quantity: float):
        self._client = client
        self._trading_pair = trading_pair
        self._quantity = quantity

    def place_order(self, signal: Union[SignalBuy, SignalSell, SignalHold]) -> Optional[BinanceOrder]:
        if isinstance(signal, SignalBuy):
            return self.place_buy_order()
        elif isinstance(signal, SignalSell):
            return self.place_sell_order()
        else:
            pass

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
            order = self._client.trading.post_orders(
                _create_cobinhood_order_dict(trading_pair=self._trading_pair,
                                             order_type="bid",
                                             quantity=self._quantity)
            )
            raise_order_exception_if_error(order)
            return order

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
            order = self._client.trading.post_orders(
                _create_cobinhood_order_dict(trading_pair=self._trading_pair,
                                             order_type="ask",
                                             quantity=self._quantity)
            )
            raise_order_exception_if_error(order)
            return order


if __name__ == '__main__':
    client = BinanceClient("VWwsv93z4UHRoJEOkye1oZeqRtYPiaEXqzeG9fem2guMNKKU1tUDTTta9Nm4JZ3x",
                           "L8C3ws3xkxX2AUravH41kfDezrHin2LarC1K8MDnmGM51dRBZwqDpvTOVZ1Qztap")
    mm = MarketMaker(client, TradingPair("NEO", "BTC"), 500)
    order = mm.place_buy_order()
    print(client.get_all_orders(symbol=str(TradingPair("NEO", "BTC"))))
    print(client.get_orderbook_ticker(symbol=str(TradingPair("NEO", "BTC"))))
