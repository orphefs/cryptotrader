import logging
from typing import Union, Optional

from datetime import datetime

from src.backtesting_logic.logic import Buy, Sell, Hold
from src.type_aliases import BinanceOrder, CobinhoodClient, BinanceClient
from src.containers.trading_pair import TradingPair

logger = logging.getLogger('cryptotrader_api')


class NoopMarketMaker:
    def __init__(self, client: Union[BinanceClient, CobinhoodClient], trading_pair: TradingPair, quantity: float):
        self._client = client
        self._trading_pair = trading_pair
        self._quantity = quantity

    def place_order(self, signal: Union[Buy, Sell, Hold]) -> Optional[BinanceOrder]:
        if isinstance(signal, Buy):
            return self.place_buy_order()
        elif isinstance(signal, Sell):
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

    def place_order(self, signal: Union[Buy, Sell, Hold]) -> Optional[BinanceOrder]:
        if isinstance(signal, Buy):
            return self.place_buy_order()
        elif isinstance(signal, Sell):
            return self.place_sell_order()
        else:
            pass

    def place_buy_order(self):
        if isinstance(self._client, BinanceClient):
            logger.info(
                "Placing Buy market order on {} for {} {}".format(datetime.now(), self._trading_pair, self._quantity))
            order = self._client.create_test_order(
                symbol=self._trading_pair,
                side=BinanceClient.SIDE_BUY,
                type=BinanceClient.ORDER_TYPE_MARKET,
                quantity=self._quantity)
            return order
        elif isinstance(self._client, CobinhoodClient):
            raise NotImplementedError

    def place_sell_order(self):
        if isinstance(self._client, BinanceClient):
            logger.info(
                "Placing Sell market order on {} for {} {}".format(datetime.now(), self._trading_pair, self._quantity))
            order = self._client.create_test_order(
                symbol=self._trading_pair,
                side=BinanceClient.SIDE_SELL,
                type=BinanceClient.ORDER_TYPE_MARKET,
                quantity=self._quantity)
            return order
        elif isinstance(self._client, CobinhoodClient):
            raise NotImplementedError


class MarketMaker:
    def __init__(self, client: Union[BinanceClient, CobinhoodClient], trading_pair: TradingPair, quantity: float):
        self._client = client
        self._trading_pair = trading_pair
        self._quantity = quantity

    def place_order(self, signal: Union[Buy, Sell, Hold]) -> Optional[BinanceOrder]:
        if isinstance(signal, Buy):
            return self.place_buy_order()
        elif isinstance(signal, Sell):
            return self.place_sell_order()
        else:
            pass

    def place_buy_order(self):
        if isinstance(self._client, BinanceClient):
            logger.info(
                "Placing Buy market order on {} for {} {}".format(datetime.now(), self._trading_pair, self._quantity))
            order = self._client.order_market_buy(
                symbol=self._trading_pair,
                side=BinanceClient.SIDE_BUY,
                type=BinanceClient.ORDER_TYPE_MARKET,
                quantity=self._quantity)
            return order
        elif isinstance(self._client, CobinhoodClient):
            raise NotImplementedError

    def place_sell_order(self):
        if isinstance(self._client, BinanceClient):
            logger.info(
                "Placing Sell market order on {} for {} {}".format(datetime.now(), self._trading_pair, self._quantity))
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
    mm = MarketMaker(client, TradingPair("NEO", "BTC"), 500)
    order = mm.place_buy_order()
    print(order)
    print(client.get_all_orders(symbol=str(TradingPair("NEO", "BTC"))))
    print(client.get_orderbook_ticker(symbol=str(TradingPair("NEO", "BTC"))))
