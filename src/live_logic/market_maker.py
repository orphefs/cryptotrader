from typing import Union

from binance.client import Client

from backtesting_logic.logic import Buy, Sell, Hold


class MarketMaker:
    def __init__(self, client):
        self._client = client

    def place_order(self, signal: Union[Buy, Sell, Hold]):
        if isinstance(signal, Buy):
            self.place_buy_order()
        elif isinstance(signal, Sell):
            self.place_sell_order()
        else:
            pass

    def place_buy_order(self):
        order = self._client.create_test_order(
            symbol='BNBBTC',
            side=Client.SIDE_BUY,
            type=Client.ORDER_TYPE_MARKET,
            quantity=100)
        return order

    def place_sell_order(self):
        order = self._client.create_test_order(
            symbol='BNBBTC',
            side=Client.SIDE_SELL,
            type=Client.ORDER_TYPE_MARKET,
            quantity=100)
        return order






