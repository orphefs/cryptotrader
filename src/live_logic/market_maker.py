import logging
from typing import Union, Optional

import binance
from binance.client import Client
from datetime import datetime

from src.backtesting_logic.logic import Buy, Sell, Hold
from src.type_aliases import BinanceOrder

logger = logging.getLogger('cryptotrader_api')


class TestMarketMaker:
    def __init__(self, client: binance.client.Client, trading_pair: str, quantity: float):
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
        logger.info(
            "Placing Buy market order on {} for {} {}".format(datetime.now(), self._trading_pair, self._quantity))
        order = self._client.create_test_order(
            symbol=self._trading_pair,
            side=Client.SIDE_BUY,
            type=Client.ORDER_TYPE_MARKET,
            quantity=self._quantity)
        return order

    def place_sell_order(self):
        logger.info(
            "Placing Sell market order on {} for {} {}".format(datetime.now(), self._trading_pair, self._quantity))
        order = self._client.create_test_order(
            symbol=self._trading_pair,
            side=Client.SIDE_SELL,
            type=Client.ORDER_TYPE_MARKET,
            quantity=self._quantity)
        return order


class MarketMaker:
    def __init__(self, client: binance.client.Client, trading_pair: str, quantity: float):
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
        logger.info(
            "Placing Buy market order on {} for {} {}".format(datetime.now(), self._trading_pair, self._quantity))
        order = self._client.order_market_buy(
            symbol=self._trading_pair,
            side=Client.SIDE_BUY,
            type=Client.ORDER_TYPE_MARKET,
            quantity=self._quantity)
        return order

    def place_sell_order(self):
        logger.info(
            "Placing Sell market order on {} for {} {}".format(datetime.now(), self._trading_pair, self._quantity))
        order = self._client.order_market_sell(
            symbol=self._trading_pair,
            side=Client.SIDE_SELL,
            type=Client.ORDER_TYPE_MARKET,
            quantity=self._quantity)
        return order


if __name__ == '__main__':
    client = Client("VWwsv93z4UHRoJEOkye1oZeqRtYPiaEXqzeG9fem2guMNKKU1tUDTTta9Nm4JZ3x",
                    "L8C3ws3xkxX2AUravH41kfDezrHin2LarC1K8MDnmGM51dRBZwqDpvTOVZ1Qztap")
    mm = MarketMaker(client, "TRXBNB", 500)
    order = mm.place_buy_order()
    print(order)
    print(client.get_all_orders(symbol="TRXBNB"))
    print(client.get_orderbook_ticker(symbol="TRXBNB"))
