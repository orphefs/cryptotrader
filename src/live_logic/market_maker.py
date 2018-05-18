import logging
from typing import Union

import binance
from binance.client import Client


from backtesting_logic.logic import Buy, Sell, Hold


class MarketMaker:
    def __init__(self, client:binance.client.Client, trading_pair:str, quantity: float):
        self._client = client
        self._trading_pair = trading_pair
        self._quantity = quantity

    def place_order(self, signal: Union[Buy, Sell, Hold]):

        if isinstance(signal, Buy):
            self.place_buy_order()
        elif isinstance(signal, Sell):
            self.place_sell_order()
        else:
            pass

    def place_buy_order(self):
        logging.info("Placing Buy market order on {} for {}".format(self._trading_pair, self._quantity))
        order = self._client.create_test_order(
            symbol=self._trading_pair,
            side=Client.SIDE_BUY,
            type=Client.ORDER_TYPE_MARKET,
            quantity=self._quantity)
        return order

    def place_sell_order(self):
        logging.info("Placing Sell market order on {} for {}".format(self._trading_pair, self._quantity))
        order = self._client.create_test_order(
            symbol=self._trading_pair,
            side=Client.SIDE_SELL,
            type=Client.ORDER_TYPE_MARKET,
            quantity=self._quantity)
        return order






